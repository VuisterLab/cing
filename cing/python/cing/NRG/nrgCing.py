"""
This script will use NRG files to generate the CING reports as well as the
indices that live on top of them.

Execute like:

python -u $CINGROOT/python/cing/NRG/nrgCing.py

As a cron job this will:
    - create a todo list
    - run entries todo
    - create new lists and write them to file.
"""

from cing import cingDirScripts
from cing import cingPythonCingDir
from cing import cingRoot
from cing.Libs.AwkLike import AwkLike
from cing.Libs.NTutils import Lister
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import is_pdb_code
from cing.Libs.NTutils import symlink
from cing.Libs.NTutils import toCsv
from cing.Libs.NTutils import writeTextToFile
from cing.Libs.disk import rmdir
from cing.Libs.html import GOOGLE_ANALYTICS_TEMPLATE
from cing.NRG.PDBEntryLists import getBmrbNmrGridEntries
from cing.NRG.PDBEntryLists import getBmrbNmrGridEntriesDOCRDone
from cing.NRG.PDBEntryLists import getPdbEntries
from cing.NRG.WhyNot import FAILED_TO_BE_CONVERTED_NRG
from cing.NRG.WhyNot import FAILED_TO_BE_VALIDATED_CING
from cing.NRG.WhyNot import NOT_NMR_ENTRY
from cing.NRG.WhyNot import NO_EXPERIMENTAL_DATA
from cing.NRG.WhyNot import TO_BE_VALIDATED_BY_CING
from cing.NRG.WhyNot import WhyNot
from cing.NRG.WhyNot import WhyNotEntry
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList
from cing.Scripts.validateEntry import ARCHIVE_TYPE_BY_ENTRY
from cing.Scripts.validateEntry import PROJECT_TYPE_CCPN
from glob import glob
import cing
import csv
import os
import shutil
import string
import time
import urllib


def run():
    """Return True on error"""
    max_entries_todo = 2    # was 500 (could be as many as u like)
    max_time_to_wait = 60 * 60 * 6 # 2p80 took the longest: 5.2 hours.
    processes_max = 8    # was 1 may be set to a 100 when just running through to regenerate pickle
    writeWhyNot = True
    updateIndices = True
    isProduction = True
    getTodoList = False # If and only if new_hits_entry_list is empty and getTodoList is False; no entries will be attempted.
    new_hits_entry_list = ['1bus'] # define empty for checking new ones.
#    new_hits_entry_list = ['1d3z']
#    new_hits_entry_list         = string.split("2jqv 2jnb 2jnv 2jvo 2jvr 2jy7 2jy8 2oq9 2osq 2osr 2otr 2rn9 2rnb")

    ## Initialize the project
    m = nrgCing(max_entries_todo = max_entries_todo, max_time_to_wait = max_time_to_wait, writeWhyNot = writeWhyNot,
                updateIndices = updateIndices, isProduction = isProduction, processes_max = processes_max)

    NTdebug("Publish results at directory    : " + m.results_dir)
    NTdebug("Do maximum number of entries    : " + `m.max_entries_todo`)

    # Get the PDB info to see which entries can/should be done.
    if m.searchPdbEntries():
        NTerror("Failed to searchPdbEntries")
        return True

    if new_hits_entry_list:
        m.entry_list_todo.addList(new_hits_entry_list)
    elif getTodoList:
        # Get todo list and some others.
        if m.getCingEntryInfo():
            NTerror("Failed to getCingEntryInfo (first time).")
            return True

    if m.entry_list_todo:
        if m.runCing():
            NTerror("Failed to runCing")
            return True

    # Do or redo the retrieval of the info from the filesystem on the doneness of NRG-CING.
    if m.getCingEntryInfo():
        NTerror("Failed to getCingEntryInfo")
        return True

    # Retrieve the linkages between BMRB and PDB entries.
    if m.getBmrbLinks():
        NTerror("Failed to get BMRB-PDB links")
        return True

    if m.updateIndexFiles():
        NTerror("Failed to update index files.")
        return True
# end def run


class nrgCing(Lister):
    """Main class for running CING reports on NRG and maintaining the statistics."""
    def __init__(self,
                 max_entries_todo = 1,
                 max_time_to_wait = 20,
                 processes_max = 2,
                 writeWhyNot = False,
                 writeTheManyFiles = False,
                 updateIndices = False,
                 isProduction = False
                ):

        self.writeWhyNot = writeWhyNot
        "Write the info for the WhyNot database"
        self.writeTheManyFiles = writeTheManyFiles
        "Write the info for the WhyNot database in files per entry; too verbose and not used anymore?"
        self.updateIndices = updateIndices
        self.isProduction = isProduction
        "Only during production we do a write to WHY_NOT"

        # Dir as base in which all info and scripts like this one resides
        self.base_dir = os.path.join(cingPythonCingDir, "NRG")

        self.results_base = 'NRG-CING'
        self.results_dir = os.path.join('/Library/WebServer/Documents', self.results_base)
        self.data_dir = os.path.join(self.results_dir, 'data')
        self.results_host = 'localhost'
        if self.isProduction:
            # Needed for php script.
            self.results_host = 'nmr.cmbi.ru.nl'
        self.results_url = 'http://' + self.results_host + '/' + self.results_base # NEW without trailing slash.

        # The csv file name for indexing pdb
        self.index_pdb_file_name = self.results_dir + "/index/index_pdb.csv"
        self.why_not_db_comments_dir = os.path.join(self.results_dir, "cmbi8", "comments")
        self.why_not_db_raw_dir = os.path.join(self.results_dir, "cmbi8", "raw")
        self.why_not_db_comments_file = 'NRG-CING.txt_done'

        self.max_entries_todo = max_entries_todo
        self.max_time_to_wait = max_time_to_wait
        self.processes_max = processes_max

        ## How long to wait between submitting individual jobs when on the cluster.
        ##self.delay_between_submitting_jobs = 5
        self.delay_between_submitting_jobs = 15
        ## Total number of child processes to be done if all scheduled to be done
        ## are indeed to be done. This is set later on and perhaps adjusted
        ## when the user interrupts the process by ctrl-c.
        self.url_redirecter = self.results_url + '/redirect.php'
        self.url_csv_file_link_base = 'http://www.bmrb.wisc.edu/servlet_data/viavia/bmrb_pdb_match'
        ## Dictionary with matches pdb to bmrb
        self.matches_many2one = {}
        ## Dictionary with matches bmrb to pdb
        self.matches_one2many = {}
        ## Dictionary with matches bmrb to pdb
        self.matches_one2many_inv = {}
        ## Replace %b in the below for the real link.
        self.bmrb_link_template = 'http://www.bmrb.wisc.edu/cgi-bin/explore.cgi?bmrbId=%b'
        self.pdb_link_template = 'http://www.rcsb.org/pdb/explore/explore.do?structureId=%s'
        self.cing_link_template = self.results_url + '/data/%t/%s/%s.cing/%s/HTML/index.html'

        ##No changes required below this line
        ###############################################################################

        os.chdir(self.results_dir)

        ## List of 'new' entries for which hits were found
        self.new_hits_entry_list = NTlist()
        self.entry_list_pdb = NTlist()
        self.entry_list_nmr = NTlist()
        self.entry_list_nmr_exp = NTlist()
        self.entry_list_nrg = NTlist()          # should be the same as self.entry_list_nmr_exp
        self.entry_list_nrg_docr = NTlist()

        # From disk.
        self.entry_list_tried = NTlist()      # .cing directory and .log file present so it was tried to start but might not have finished
        self.entry_list_crashed = NTlist()    # has a stack trace
        self.entry_list_stopped = NTlist()    # was stopped by time out or by user or by system (any other type of stop but stack trace)
        self.entry_list_done = NTlist()       # finished to completion of the cing run.
        self.entry_list_todo = NTlist()
        self.timeTakenDict = NTdict()
        self.entry_list_obsolete = NTlist()
        self.ENTRY_DELETED_COUNT_MAX = 2


    def getBmrbLinks(self):
        """ Returns True for failure"""
        url_many2one = self.url_csv_file_link_base + "/score_many2one.csv"
        url_one2many = self.url_csv_file_link_base + "/score_one2many.csv"

        for url_links in (url_many2one, url_one2many):
            try:
                resource = urllib.urlopen(url_links)
                reader = csv.reader(resource)
            except IOError:
                NTerror("couldn't open url for reader: " + url_links)
                return True

            try:
                _header_read = reader.next()
#                NTdebug("read header: %s" % header_read)
                for row in reader:
                    bmrb_code = row[0]
                    pdb_code = row[1]
                    if (url_links == url_many2one):
                        self.matches_many2one[ pdb_code ] = bmrb_code
                    else:
                        self.matches_one2many[     bmrb_code ] = pdb_code
                        self.matches_one2many_inv[ pdb_code  ] = bmrb_code
            # Never know when the connection is finally empty.
            except IOError:
                pass

            if url_links == url_many2one:
                NTmessage("Found %s matches from PDB to BMRB" % len(self.matches_many2one))
            else:
                NTmessage("Found %s matches from BMRB to PDB" % len(self.matches_one2many))


    def getCingEntryInfo(self):
        """Returns True for error
        Will remove entry directories if they do not occur in NRG up to a maximum number as not to whipe out
        every one in a single blow by accident.
        """

        NTmessage("Get the entries tried, todo, crashed, and stopped in NRG-CING from file system.")

        self.entry_list_obsolete = NTlist()
        self.entry_list_tried = NTlist()
        self.entry_list_crashed = NTlist()
        self.entry_list_stopped = NTlist()
        self.entry_list_done = NTlist()
        self.entry_list_todo = NTlist()


        subDirList = os.listdir('data')
        for subDir in subDirList:
            if len(subDir) != 2:
                if subDir != ".DS_Store":
                    NTdebug('Skipping subdir with other than 2 chars: [' + subDir + ']')
                continue
            entryList = os.listdir(os.path.join('data', subDir))
            for entryDir in entryList:
                entry_code = entryDir
                if not is_pdb_code(entry_code):
                    if entry_code != ".DS_Store":
                        NTerror("String doesn't look like a pdb code: " + entry_code)
                    continue
#                NTdebug("Working on: " + entry_code)

                entrySubDir = os.path.join('data', subDir, entry_code)
                if not entry_code in self.entry_list_nrg_docr:
                    NTwarning("Found entry %s in NRG-CING but not in NRG. Will be obsoleted in NRG-CING too" % entry_code)
                    if len(self.entry_list_obsolete) < self.ENTRY_DELETED_COUNT_MAX:
                        rmdir(entrySubDir)
                        self.entry_list_obsolete.append(entry_code)
                    else:
                        NTerror("Entry %s in NRG-CING not obsoleted since there were already removed: %s" % (
                            entry_code, self.ENTRY_DELETED_COUNT_MAX))
                # end if

                cingDirEntry = os.path.join(entrySubDir, entry_code + ".cing")
                if not os.path.exists(cingDirEntry):
                    NTmessage("Failed to find directory: %s" % cingDirEntry)
                    continue

                # Look for last log file
                logList = glob(entrySubDir + '/log_validateEntry/*.log')
                if not logList:
                    NTmessage("Failed to find any log file in directory: %s" % entrySubDir)
                    continue
                # .cing directory and .log file present so it was tried to start but might not have finished
                self.entry_list_tried.append(entry_code)

                logLastFile = logList[-1]
#                NTdebug("Found logLastFile %s" % logLastFile)
#                set timeTaken = (` grep 'CING took       :' $logFile | gawk '{print $(NF-1)}' `)
#                text = readTextFromFile(logLastFile)
                for r in AwkLike(logLastFile):
                    line = r.dollar[0]
                    if line.startswith('CING took       :'):
#                        NTdebug("Matched line: %s" % line)
                        timeTakenStr = r.dollar[r.NF - 1]
                        self.timeTakenDict[entry_code] = float(timeTakenStr)
#                        NTdebug("Found time: %s" % self.timeTakenDict[entry_code])
                    if line.startswith('Traceback (most recent call last)'):
#                        NTdebug("Matched line: %s" % line)
                        if entry_code in self.entry_list_crashed:
                            NTwarning("%s was already found before; not adding again." % entry_code)
                        else:
                            self.entry_list_crashed.append(entry_code)
                # end for AwkLike
                if not self.timeTakenDict.has_key(entry_code):
                    # was stopped by time out or by user or by system (any other type of stop but stack trace)
                    NTmessage("%s Since CING end message was not found assumed to have stopped" % entry_code)
                    self.entry_list_stopped.append(entry_code)
                    continue

                # Look for end statement from CING which shows it wasn't killed before it finished.
                indexFileEntry = os.path.join(cingDirEntry, "index.html")
                if not os.path.exists(indexFileEntry):
                    NTmessage("%s Since index file %s was not found assumed to have stopped" % (entry_code, indexFileEntry))
                    self.entry_list_stopped.append(entry_code)
                    continue

                projectHtmlFile = os.path.join(cingDirEntry, entry_code, "HTML/index.html")
                if not os.path.exists(projectHtmlFile):
                    NTmessage("%s Since project html file %s was not found assumed to have stopped" % (entry_code, projectHtmlFile))
                    self.entry_list_stopped.append(entry_code)
                    continue
                self.entry_list_done.append(entry_code)
            # end for entryDir
        # end for subDir
        timeTakenList = NTlist() # local variable.
        timeTakenList.addList(self.timeTakenDict.values())
        NTmessage("Time taken by CING by statistics\n%s" % timeTakenList.statsFloat())

        if not self.entry_list_tried:
            NTerror("Failed to find entries that CING tried.")

        self.entry_list_todo.addList(self.entry_list_nrg_docr)
        self.entry_list_todo = self.entry_list_todo.difference(self.entry_list_done)

        NTmessage("Found %s entries that CING tried (T)." % len(self.entry_list_tried))
        NTmessage("Found %s entries that CING crashed (C)." % len(self.entry_list_crashed))
        NTmessage("Found %s entries that CING stopped (S)." % len(self.entry_list_stopped))
        if not self.entry_list_done:
            NTerror("Failed to find entries that CING did.")
        NTmessage("Found %s entries that CING did (B=A-C-S)." % len(self.entry_list_done))
        NTmessage("Found %s entries todo (A-B)." % len(self.entry_list_todo))
        NTmessage("Found %s entries in NRG-CING made obsolete." % len(self.entry_list_obsolete))
    # end def

    def searchPdbEntries(self):
        """
        Set the list of matched entries and the dictionary holding the
        number of matches. They need to be defined as globals to this module.
        Return True on error.
        Also searches the PDB and BMRB databases itself.
        """
#        modification_time = os.path.getmtime("/Users/jd/.cshrc")
#        self.match.d[ "1brv" ] = EntryInfo(time=modification_time)

        ## following statement is equivalent to a unix command like:
        NTdebug("Looking for entries from the PDB and BMRB databases.")

        self.entry_list_pdb.addList(getPdbEntries())
        if not self.entry_list_pdb:
            NTerror("No PDB entries found")
            return True
        NTmessage("Found %s PDB entries." % len(self.entry_list_pdb))

        self.entry_list_nmr.addList(getPdbEntries(onlyNmr = True))
        if not self.entry_list_nmr:
            NTerror("No NMR entries found")
            return True
        NTmessage("Found %s NMR entries." % len(self.entry_list_nmr))

        self.entry_list_nmr_exp.addList(getPdbEntries(onlyNmr = True, mustHaveExperimentalNmrData = True))
        if not self.entry_list_nmr_exp:
            NTerror("No NMR with experimental data entries found")
            return True
        NTmessage("Found %s NMR with experimental data entries." % len(self.entry_list_nmr_exp))

        self.entry_list_nrg.addList(getBmrbNmrGridEntries())
        if not self.entry_list_nrg:
            NTerror("No NRG entries found")
            return True
        NTmessage("Found %s PDB entries in NRG." % len(self.entry_list_nrg))

        ## The list of all entry_codes for which tgz files have been found
        self.entry_list_nrg_docr.addList(getBmrbNmrGridEntriesDOCRDone())
        if not self.entry_list_nrg_docr:
            NTerror("No NRG DOCR entries found")
            return True
        NTmessage("Found %s NRG DOCR entries. (A)" % len(self.entry_list_nrg_docr))
        if len(self.entry_list_nrg_docr) < 3000:
            NTerror("watch out less than 3000 entries found [%s] which is suspect; quitting" % len(self.entry_list_nrg_docr))
            return True



    def doWriteEntryLoL(self):
        """Write the entry list of each list to file"""
        writeTextToFile("entry_list_pdb.csv", toCsv(self.entry_list_pdb))
        writeTextToFile("entry_list_nmr.csv", toCsv(self.entry_list_nmr))
        writeTextToFile("entry_list_nmr_exp.csv", toCsv(self.entry_list_nmr_exp))
        writeTextToFile("entry_list_nrg.csv", toCsv(self.entry_list_nrg))
        writeTextToFile("entry_list_nrg_docr.csv", toCsv(self.entry_list_nrg_docr))
        writeTextToFile("entry_list_tried.csv", toCsv(self.entry_list_tried))
        writeTextToFile("entry_list_done.csv", toCsv(self.entry_list_done))
        writeTextToFile("entry_list_todo.csv", toCsv(self.entry_list_todo))
        writeTextToFile("entry_list_crashed.csv", toCsv(self.entry_list_crashed))
        writeTextToFile("entry_list_stopped.csv", toCsv(self.entry_list_stopped))
        writeTextToFile("entry_list_timing.csv", toCsv(self.timeTakenDict))


    def doWriteWhyNot(self):
        "Write the WHYNOT files"
        NTdebug("Create WHY_NOT list")
        whyNot = WhyNot()
        # Loop for speeding up the checks. Most are not nmr.
        for entryId in self.entry_list_pdb:
            whyNotEntry = WhyNotEntry(entryId)
            whyNot[entryId] = whyNotEntry
            whyNotEntry.comment = NOT_NMR_ENTRY
            whyNotEntry.exists = False

        for entryId in self.entry_list_nmr:
            whyNotEntry = whyNot[entryId]
            whyNotEntry.exists = True
            if entryId not in self.entry_list_nrg:
                whyNotEntry.comment = NO_EXPERIMENTAL_DATA
                whyNotEntry.exists = False
                continue
            if entryId not in self.entry_list_nrg_docr:
                whyNotEntry.comment = FAILED_TO_BE_CONVERTED_NRG
                whyNotEntry.exists = False
                continue
            if entryId not in self.entry_list_tried:
                whyNotEntry.comment = TO_BE_VALIDATED_BY_CING
                whyNotEntry.exists = False
                continue
            if entryId not in self.entry_list_done:
                whyNotEntry.comment = FAILED_TO_BE_VALIDATED_CING
                whyNotEntry.exists = False
                continue

#            whyNotEntry.comment = PRESENT_IN_CING
            # Entries that are present in the database do not need a comment
            del(whyNot[entryId])
        # end loop over entries
        whyNotStr = '%s' % whyNot
#        NTdebug("whyNotStr truncated to 1000 chars: [" + whyNotStr[0:1000] + "]")

        writeTextToFile("NRG-CING.txt", whyNotStr)

        why_not_db_comments_file = os.path.join(self.why_not_db_comments_dir, self.why_not_db_comments_file)
        NTdebug("Copying to: " + why_not_db_comments_file)
        shutil.copy("NRG-CING.txt", why_not_db_comments_file)
        if self.writeTheManyFiles:
            for entryId in self.entry_list_done:
                # For many files like: /usr/data/raw/nmr-cing/           d3/1d3z/1d3z.exist
                char23 = entryId[1:3]
                subDir = os.path.join(self.why_not_db_raw_dir, char23, entryId)
                if not os.path.exists(subDir):
                    os.makedirs(subDir)
                fileName = os.path.join(subDir, entryId + ".exist")
                if not os.path.exists(fileName):
    #                NTdebug("Creating: " + fileName)
                    fp = open(fileName, 'w')
        #            fprintf(fp, ' ')
                    fp.close()


    def updateIndexFiles(self):
        """Updating the index files.
        Return True on error."""

        if not self.updateIndices:
            return

        NTmessage("Updating index files")

        number_of_entries_per_row = 4
        number_of_files_per_column = 4

        indexDir = os.path.join(self.results_dir, "index")
        if os.path.exists(indexDir):
            shutil.rmtree(indexDir)
        os.mkdir(indexDir)
        htmlDir = os.path.join(cingRoot, "HTML")

        csvwriter = csv.writer(file(self.index_pdb_file_name, "w"))
        if not self.entry_list_done:
            NTwarning("No entries done, skipping creation of indexes")
            return

        self.entry_list_done.sort()

        number_of_entries_per_file = number_of_entries_per_row * number_of_files_per_column
        ## Get the number of files required for building an index
        number_of_entries_all_present = len(self.entry_list_done)
        ## Number of files with indexes in google style
        number_of_files = int(number_of_entries_all_present / number_of_entries_per_file)
        if number_of_entries_all_present % number_of_entries_per_file:
            number_of_files += 1
        NTmessage("Generating %s index html files" % (number_of_files))

        example_str_template = """ <td><a href=""" + self.pdb_link_template + \
        """>%S</a><BR><a href=""" + self.bmrb_link_template + ">%b</a>"

        cingImage = '../data/%t/%s/%s.cing/%s/HTML/mol.gif'
        example_str_template += '</td><td><a href="' + self.cing_link_template + '"><img SRC="' + cingImage + '" border=0 width="200" ></a></td>'
        file_name = os.path.join (self.base_dir, "data", "index.html")
        file_content = open(file_name, 'r').read()
        old_string = r"<!-- INSERT NEW DATE HERE -->"
        new_string = time.asctime()
        file_content = string.replace(file_content, old_string, new_string)

        old_string = r"<!-- INSERT FOOTER HERE -->"
        file_content = string.replace(file_content, old_string, GOOGLE_ANALYTICS_TEMPLATE)

        ## Count will track the number of entries done per index file
        entries_done_per_file = 0
        ## Following variable will track all done sofar
        entries_done_all = 0
        ## Tracking the number in the current row. Set for the rare case that there
        ## are no entries at all. Otherwise it will be initialize on first pass.
        num_in_row = 0
        ## Tracking the index file number
        file_id = 1
        ## Text per row in an index file to insert
        insert_text = ''

        ## Repeat for all entries plus a dummy pass for writing the last index file
        for x_entry_code in self.entry_list_done + [ None ]:
            if x_entry_code:
                pdb_entry_code = x_entry_code
                if self.matches_many2one.has_key(pdb_entry_code):
                    bmrb_entry_code = self.matches_many2one[pdb_entry_code]
                    bmrb_entry_code = bmrb_entry_code
                else:
                    bmrb_entry_code = ""

            ## Finish this index file
            ## The last index file will only be written once...
            if entries_done_per_file == number_of_entries_per_file or \
                    entries_done_all == number_of_entries_all_present:

                begin_entry_count = number_of_entries_per_file * (file_id - 1) + 1
                end_entry_count = min(number_of_entries_per_file * file_id,
                                           number_of_entries_all_present)
#                NTdebug("%5d %5d %5d" % (begin_entry_count, end_entry_count, number_of_entries_all_present))

                old_string = r"<!-- INSERT NEW RESULT STRING HERE -->"
                jump_form_start = '<FORM method="GET" action="%s">' % self.url_redirecter
                result_string = jump_form_start + "PDB entries"
                db_id = "PDB"

                jump_form = '<INPUT type="hidden" name="database" value="%s">' % string.lower(db_id)
                jump_form = jump_form + \
"""<INPUT type="text" size="4" name="id" value="" >
<INPUT type="submit" name="button" value="go">"""
                jump_form_end = "</FORM>"

                begin_entry_code = string.upper(self.entry_list_done[ begin_entry_count - 1 ])
                end_entry_code = string.upper(self.entry_list_done[ end_entry_count - 1 ])
                new_row = [ file_id, begin_entry_code, end_entry_code ]
                csvwriter.writerow(new_row)

                new_string = '%s: <B>%s-%s</B> &nbsp;&nbsp; (%s-%s of %s). &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Jump to index with %s entry id &nbsp; %s\n%s\n' % (
                        result_string,
                        begin_entry_code,
                        end_entry_code,
                        begin_entry_count,
                        end_entry_count,
                        number_of_entries_all_present,
                        db_id,
                        jump_form,
                        jump_form_end
                        )
                new_file_content = string.replace(file_content, old_string, new_string)

                # Always end the row by adding dummy columns
                if num_in_row != number_of_entries_per_row:
                    insert_text += (number_of_entries_per_row -
                                     num_in_row) * 2 * r"<td>&nbsp;</td>" + r"</tr>"

                ## Create the new index file from the example one by replacing a string
                ## with the new content.
                old_string = r"<!-- INSERT NEW ROWS HERE -->"
                new_file_content = string.replace(new_file_content, old_string, insert_text)

                if file_id > 1:
                    prev_string = '<a href="index_%s.html">Previous &lt;</a>' % (
                        file_id - 1)
                else:
                    prev_string = ''
                if file_id < number_of_files:
                    next_string = '<a href="index_%s.html">> Next</a>' % (
                        file_id + 1)
                else:
                    next_string = ''

                first_link = max(1, file_id - number_of_files_per_column)
                last_link = min(number_of_files, file_id + number_of_files_per_column - 1)
                links_string = ''
                for link in range(first_link, last_link + 1):
                    ## List link but don't include a link out for the current file_id
                    if link == file_id:
                        links_string += ' <B>%s</B>' % link
                    else:
                        links_string += ' <a href="index_%s.html">%s</a>' % (
                             link, link)

                old_string = r"<!-- INSERT NEW LINKS HERE -->"
                new_string = 'Result page: %s %s %s' % (
                    prev_string, links_string, next_string)
                new_file_content = string.replace(new_file_content, old_string, new_string)


                ## Make the first index file name still index.html
                new_file_name = indexDir + '/index_' + `file_id` + '.html'
                if not file_id:
                    new_file_name = indexDir + '/index.html'
                open(new_file_name, 'w').write(new_file_content)

                entries_done_per_file = 0
                num_in_row = 0
                insert_text = ""
                file_id += 1
            ## Build on current index file
            ## The last iteration will not execute this block because of this clause
            if entries_done_all < number_of_entries_all_present:
                entries_done_all += 1
                entries_done_per_file += 1
                ## Get the html code right by abusing the formatting chars.
                ## as in sprintf etc.
                tmp_string = string.replace(example_str_template, r"%S", string.upper(pdb_entry_code))
                tmp_string = string.replace(tmp_string, r"%s", pdb_entry_code)
                tmp_string = string.replace(tmp_string, r"%t", pdb_entry_code[1:3])
                tmp_string = string.replace(tmp_string, r"%b", bmrb_entry_code)

                num_in_row = entries_done_per_file % number_of_entries_per_row
                if num_in_row == 0:
                    num_in_row = number_of_entries_per_row

                if num_in_row == 1:
                    # Start new row
                    tmp_string = r"<tr>" + tmp_string
                elif (num_in_row == number_of_entries_per_row):
                    # End this row
                    tmp_string = tmp_string + r"</tr>"

                insert_text += tmp_string

        ## Make a sym link from the index_pdb_1.html file to the index_pdb.html file
        index_file_first = 'index_1.html'
        index_file = os.path.join(indexDir, 'index.html')
        ## Assume that a link that is already present is valid and will do the job
#        NTmessage('Symlinking: %s %s' % (index_file_first, index_file))
        symlink(index_file_first, index_file)

#        ## Make a sym link from the index_bmrb.html file to the index.html file
#        index_file_first = 'index_pdb.html'
#        index_file_first = index_file_first
#        index_file = os.path.join(self.results_dir + "/index", 'index.html')
#        NTdebug('Symlinking (B): %s %s' % (index_file_first, index_file))
#        symlink(index_file_first, index_file)

        NTmessage("Copy the adjusted php script")
        org_file = os.path.join(self.base_dir, 'data', 'redirect.php')
        new_file = os.path.join(self.results_dir, 'redirect.php')
        file_content = open(org_file, 'r').read()
        old_string = 'URL_BASE'
        file_content = string.replace(file_content, old_string, self.results_url)
        open(new_file, 'w').write(file_content)

        NTmessage("Copy the adjusted html redirect")
        org_file = os.path.join(self.base_dir, 'data', 'redirect.html')
        new_file = os.path.join(self.results_dir, 'index.html')
#        file_content = open(org_file, 'r').read()
#        old_string = 'URL_BASE'
#        file_content = string.replace(file_content, old_string, self.results_url)
#        open(new_file, 'w').write(file_content)
        shutil.copy(org_file, new_file)

        cssFile = os.path.join(htmlDir, "cing.css")
        headerBgFile = os.path.join(htmlDir, "header_bg.jpg")
        shutil.copy(cssFile, indexDir)
        shutil.copy(headerBgFile, indexDir)


    def runCing(self):
        """On self.entry_list_todo.
        Return True on error.
        """
        entryListFileName = "entry_list_todo.csv"
        writeTextToFile(entryListFileName, toCsv(self.entry_list_todo))

        pythonScriptFileName = os.path.join(cingDirScripts, 'validateEntry.py')
        inputDir = 'file://' + self.results_dir + '/recoordSync'
        outputDir = self.results_dir
        extraArgList = (inputDir, outputDir, '.', '.', `ARCHIVE_TYPE_BY_ENTRY`, `PROJECT_TYPE_CCPN`)

        if doScriptOnEntryList(pythonScriptFileName,
                            entryListFileName,
                            self.results_dir,
                            processes_max = self.processes_max,
                            delay_between_submitting_jobs = 15, # why is this so long? because of time outs at tang?
                            max_time_to_wait = self.max_time_to_wait,
                            # <Molecule "2p80" (C:20,R:1162,A:24552,M:20)>
                            START_ENTRY_ID = 0, # default.
                            MAX_ENTRIES_TODO = self.max_entries_todo,
                            extraArgList = extraArgList):
            NTerror("Failed to doScriptOnEntryList")
            return True
    # end def runCing.


if __name__ == '__main__':
    cing.verbosity = cing.verbosityDebug
    run()
