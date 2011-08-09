"""
Execute like: python -u $CINGROOT/python/cing/NRG/CasdNmrCing.py

This script will use CASD-NMR files to generate CING reports, see
Scripts/validateforCASD_NMR.py

If the pickle is polluted do the following steps:
  -0- remove pickle.
  -1- set skip_newer_entries_if_images_exist = 1
      set regenerating_pickle = 1
      set the number of entries high and use 100 processors
  -2- run (takes less than an hour)
  -3- reset all the default options again and run again


When you need to stop a batch processing, send a signal
to it for interuption. E.g. when 22059 is the PID of "python CasdNmrCing.py 1"
do "kill -15 22059". Let it finish for a while when you see:
WARNING: Caught interrupt in parent.
WARNING: Trying to finish up by waiting for subprocesses
WARNING: only 965 out of 1000 jobs were started (not all successfully finished perhaps)
or similar. The minus of -15 is necessary because it needs to signal it's children.
"""

from cing import cingPythonCingDir
from cing import cingRoot
from cing.Libs import forkoff
from cing.Libs.AwkLike import AwkLike
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.forkoff import get_cmd_output
from cing.Libs.html import GOOGLE_ANALYTICS_TEMPLATE
from cing.NRG import CASD_NMR_BASE_NAME
from cing.NRG.CasdNmrMassageCcpnProject import baseDir
from cing.NRG.CasdNmrMassageCcpnProject import entryList
from glob import glob
import csv
import shutil
import string


class MyDict(Lister):
    """just a simple dictionary"""
    def __init__(self):
        self.d = {}

class EntryInfo(Lister):
    def __init__(self, time=None):
        self.time = time


class casdNmrCing(Lister):

    def __init__(self,
                 max_entries_todo=1,
                 max_time_to_wait=20,
                 writeWhyNot=False,
                 updateIndices=False,
                 isProduction=False
                ):

        self.writeWhyNot = writeWhyNot
        self.updateIndices = updateIndices
        "Only during production we do a write to WHY_NOT"
        self.isProduction = isProduction

        # Dir as base in which all info and scripts like this one resides
        self.base_dir = os.path.join(cingPythonCingDir, "NRG")
        self.backcolor = 'cing_blue'
        self.data_dir_local = "dataCASD-NMR"

#        self.results_base = 'eNMRworkshop2'
        self.results_base = CASD_NMR_BASE_NAME
        self.results_base_dir = os.path.join('/Library/WebServer/Documents', self.results_base)
        self.results_dir = self.results_base_dir

        self.data_dir = os.path.join(self.results_base_dir, DATA_STR)
#        self.results_dir        = '/big/jurgen/molgrap/'        + run_id
        self.tmp_dir = self.results_dir + '/_tmp_'
        # all relative now.
#        self.results_host = 'localhost'
#        if self.isProduction:
#            # Needed for php script.
#            self.results_host = 'nmr.cmbi.ru.nl'
#        self.results_url = 'http://' + self.results_host + '/' + self.results_base + '/'

        # The csv file name for indexing pdb
        self.index_pdb_file_name = self.results_dir + "/index/index_pdb.csv"

        ## Maximum number of pictures to create before ending
        ## and writting the pickle and web page overview again.
        ## Restart the process to do any remaining entries.
        ## Don't overlap processes!!!
        self.max_entries_todo = max_entries_todo
        self.max_time_to_wait = max_time_to_wait

        ## When set to non-zero the algorithm will update the modification
        ## time for an updated pdb file in the pickle but will not
        ## regenerate the images provided that they are present already
        ## Default is 0
        self.skip_updated_pdb_files = 0

        ## Will never actually try to create an image when set to 1
        ## Default is 0
        self.regenerating_pickle = 0

        ## How long to wait between submitting individual jobs when on the cluster.
        ##self.delay_between_submitting_jobs = 5
        self.delay_between_submitting_jobs = 0
        ## Total number of child processes to be done if all scheduled to be done
        ## are indeed to be done. This is set later on and perhaps adjusted
        ## when the user interrupts the process by ctrl-c.

#        self.url_redirecter = self.results_url + '/redirect.php'

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
#        self.cing_link_template = self.results_url + '/data/%t/%s/%s.cing/index.html' # relative link below
        self.cing_link_template = '../data/%t/%s/%s.cing/index.html'
        self.pdb_entries_White = {}
        self.processes_todo = None
        ## Dictionary with pid:entry_code info on running children
        self.child_d = {}

        ##No changes required below this line
        ###############################################################################

        nTmessage("Publish results at directory    : " + self.results_dir)
        nTmessage("Do maximum number of entries    : " + repr(self.max_entries_todo))

        os.chdir(self.results_dir)

        ## List of 'new' entries for which hits were found
        self.new_hits_entry_list = []
        self.done_entry_list = []
        self.entry_list_all = NTlist()
        self.entry_list_todo = NTlist()
        self.entry_anno_list_all = []
        self.timeTakenDict = NTdict()


    """
    Check the resource dir for existence of all needed items.
    this is quit i/o intensive but the only way to guarantee it
    as the pickle might get out of sync with reality
    Returns one for complete resource.
    """
    def is_complete_resource(self, entry_code):
        nTdebug("checking is_complete_resource for entry: " + entry_code)
        sub_dir = entry_code[1:3]
        indexFileName = os.path.join (self.results_dir, DATA_STR, sub_dir, entry_code, entry_code + ".cing", 'index.html')
        return os.path.isfile(indexFileName)


    def getCingEntriesTriedAndDone(self):
        "Returns list or None for error"
        nTdebug("From disk get the entries done in CASD-NMR-CING")

        entry_list_tried = []
        entry_list_done = []
        entry_list_crashed = []

        nTdebug("Now in: " + os.getcwd())
        subDirList = os.listdir(DATA_STR)
        for subDir in subDirList:
            if len(subDir) != 2:
                if subDir != DS_STORE_STR:
                    nTdebug('Skipping subdir with other than 2 chars: [' + subDir + ']')
                continue
            entryList = os.listdir(os.path.join(DATA_STR,subDir))
            for entryDir in entryList:
                entry_code = entryDir
                if entry_code == DS_STORE_STR:
                    continue

                entrySubDir = os.path.join(DATA_STR, subDir, entry_code)

                cingDirEntry = os.path.join(entrySubDir, entry_code + ".cing")
                if not os.path.exists(cingDirEntry):
                    continue
                logFileValidate = 'log_validateEntryForCasd'
                for logFile in ( logFileValidate, 'log_storeCING2db' ):
                    # Look for last log file
                    logList = glob(entrySubDir + '/%s/*.log' % logFile)
                    if not logList:
                        nTmessage("Failed to find any log file in subdirectory of: %s" % entrySubDir)
                        continue
                    # .cing directory and .log file present so it was tried to start but might not have finished
    #                self.entry_anno_list_tried.append(entry_code)
                    if logFile == logFileValidate:
                        entry_list_tried.append(entry_code)
                    logLastFile = logList[-1]

                    entryCrashed = False
                    entryWithErrorMessage = False
                    for r in AwkLike(logLastFile):
                        line = r.dollar[0]
                        if line.startswith('CING took       :'):
    #                        nTdebug("Matched line: %s" % line)
                            timeTakenStr = r.dollar[r.NF - 1]
                            self.timeTakenDict[entry_code] = float(timeTakenStr)
    #                        nTdebug("Found time: %s" % self.timeTakenDict[entry_code])
                        if line.startswith('Traceback (most recent call last)'):
    #                        nTdebug("Matched line: %s" % line)
                            if entry_code in entry_list_crashed:
                                nTwarning("%s was already found before; not adding again." % entry_code)
                            else:
                                entry_list_crashed.append(entry_code)
                                entryCrashed = True
                        if line.count('ERROR:'):
                            nTerror("Matched line: %s" % line)
                            entryWithErrorMessage = True
                        if line.count('Aborting'):
                            nTdebug("Matched line: %s" % line)
                            entryCrashed = True
                            if entry_code in entry_list_crashed:
                                nTwarning("%s was already found before; not adding again." % entry_code)
                            else:
                                entry_list_crashed.append(entry_code)
                if entryWithErrorMessage:
                    nTerror("Above for entry: %s" % entry_code)
                if entryCrashed:
                    continue # don't mark it as stopped anymore.

                indexFileEntry = os.path.join(cingDirEntry, "index.html")
                if os.path.exists(indexFileEntry):
                    entry_list_done.append(entry_code)
        return (entry_list_tried, entry_list_done, entry_list_crashed)


    def getCingAnnoEntryInfo(self):
        """Returns True for error
        Checks the completeness and errors from annotation.
        """

        MAX_LINK_ERRORS = 20 # VpR247Cheshire had 16 terminii etc. problems that can be ignored.
        MAX_CHAIN_MAPPING_ERRORS = 1
        MAX_ANY_ERRORS = MAX_LINK_ERRORS + MAX_CHAIN_MAPPING_ERRORS

        nTmessage("Get the entries tried, todo, crashed, and stopped from file system.")

        self.entry_anno_list_obsolete = NTlist()
        self.entry_anno_list_tried = NTlist()
        self.entry_anno_list_crashed = NTlist()
        self.entry_anno_list_stopped = NTlist() # mutely exclusive from entry_list_crashed
        self.entry_anno_list_done = NTlist()
        self.entry_anno_list_todo = NTlist()

        cwdCache = os.getcwd()
        os.chdir(baseDir)
        subDirList = os.listdir(DATA_STR)
        subDirList.sort()
        for subDir in subDirList:
            if len(subDir) != 2:
                if subDir != DS_STORE_STR:
                    nTdebug('Skipping subdir with other than 2 chars: [' + subDir + ']')
                continue
            entryList = os.listdir(os.path.join(DATA_STR, subDir))
            for entryDir in entryList:
                entry_code = entryDir
                if entry_code.startswith( "."):
#                    nTdebug('Skipping hidden file: [' + entry_code + ']')
                    continue
                if entry_code.endswith( "Org") or entry_code.endswith( "Test"):
#                    nTdebug('Skipping original entry: [' + entry_code + ']')
                    continue
                entrySubDir = os.path.join(DATA_STR, subDir, entry_code)
#                if not entry_code in self.entry_list_nrg_docr:
#                    nTwarning("Found entry %s in NRG-CING but not in NRG. Will be obsoleted in NRG-CING too" % entry_code)
#                    if len(self.entry_list_obsolete) < self.ENTRY_DELETED_COUNT_MAX:
#                        rmdir(entrySubDir)
#                        self.entry_list_obsolete.append(entry_code)
#                    else:
#                        nTerror("Entry %s in NRG-CING not obsoleted since there were already removed: %s" % (
#                            entry_code, self.ENTRY_DELETED_COUNT_MAX))
                # end if

#                cingDirEntry = os.path.join(entrySubDir, entry_code + ".cing")
#                if not os.path.exists(cingDirEntry):
#                    nTmessage("Failed to find directory: %s" % cingDirEntry)
#                    continue

                # Look for last log file
                logList = glob(entrySubDir + '/log_doAnno*/*.log')
                if not logList:
                    nTmessage("Failed to find any log file in directory: %s" % entrySubDir)
                    continue
                # .cing directory and .log file present so it was tried to start but might not have finished
                self.entry_anno_list_tried.append(entry_code)

                logLastFile = logList[-1]
#                nTdebug("Found logLastFile %s" % logLastFile)
#                set timeTaken = (` grep 'CING took       :' $logFile | gawk '{print $(NF-1)}' `)
#                text = readTextFromFile(logLastFile)
                entryCrashed = False

                linkErrorList = []
                chainMappingErrorList = []
                anyErrorList = []
                for r in AwkLike(logLastFile):
                    line = r.dollar[0]
                    if line.startswith('CING took       :'):
#                        nTdebug("Matched line: %s" % line)
                        timeTakenStr = r.dollar[r.NF - 1]
                        self.timeTakenDict[entry_code] = float(timeTakenStr)
#                        nTdebug("Found time: %s" % self.timeTakenDict[entry_code])
                    if line.startswith('Traceback (most recent call last)'):
#                        nTdebug("Matched line: %s" % line)
                        if entry_code in self.entry_anno_list_crashed:
                            nTwarning("%s was already found before; not adding again." % entry_code)
                        else:
                            self.entry_anno_list_crashed.append(entry_code)
                            entryCrashed = True
                    if line.count('ERROR:'):
                        nTerror("Matched line: %s" % line)

                    hasPseudoErrorListed = line.count(" .Q") # ignore the errors for pseudos e.g. in CGR26ALyon Hopefully this is unique enough; tested well.
                    if line.count("Error: Not linking atom"):
                        if not hasPseudoErrorListed:
                            linkErrorList.append(line)
                    if line.count("Error: no chain mapping"):
                        chainMappingErrorList.append(line)
                    lineLower = line.lower()

                    hasApiErrorListed =  line.count('ApiError: ccp.nmr.NmrConstraint.DistanceConstraintItem.__init__:')
                    if lineLower.count("error"):
                        if not (hasPseudoErrorListed or hasApiErrorListed):
                            anyErrorList.append(line)

                    if line.count('Aborting'):
                        nTdebug("Matched line: %s" % line)
                        entryCrashed = True
                        if entry_code in self.entry_anno_list_crashed:
                            nTwarning("%s was already found before; not adding again." % entry_code)
                        else:
                            self.entry_anno_list_crashed.append(entry_code)
                if entryCrashed:
                    continue # don't mark it as stopped anymore.

                linkErrorListCount = len(linkErrorList)
                if linkErrorListCount > MAX_LINK_ERRORS:
                    nTerror("%-25s has more than %s link errors;          %s" % (entry_code,MAX_LINK_ERRORS,linkErrorListCount))
                    entryCrashed = True
                chainMappingListCount = len(chainMappingErrorList)
                if chainMappingListCount > MAX_CHAIN_MAPPING_ERRORS:
                    nTerror("%-25s has more than %s chain mapping errors; %s" % (entry_code,MAX_CHAIN_MAPPING_ERRORS,chainMappingListCount))
                    entryCrashed = True
                anyErrorListCount = len(anyErrorList)
                if anyErrorListCount > MAX_ANY_ERRORS:
                    nTerror("%-25s has more than %s any errors;           %s" % (entry_code,MAX_ANY_ERRORS,anyErrorListCount))
                    entryCrashed = True

                if entryCrashed:
                    continue # don't mark it as stopped anymore.

                if not self.timeTakenDict.has_key(entry_code):
                    # was stopped by time out or by user or by system (any other type of stop but stack trace)
                    nTmessage("%s Since CING end message was not found assumed to have stopped" % entry_code)
                    self.entry_anno_list_stopped.append(entry_code)
                    continue

                # Look for end statement from CING which shows it wasn't killed before it finished.
                ccpnFileEntry = os.path.join(entrySubDir, "%s.tgz"%entry_code)
                if not os.path.exists(ccpnFileEntry):
                    nTmessage("%s Since ccpn file %s was not found assumed to have stopped" % (entry_code, ccpnFileEntry))
                    self.entry_anno_list_stopped.append(entry_code)
                    continue

                self.entry_anno_list_done.append(entry_code)
            # end for entryDir
        # end for subDir
        timeTakenList = NTlist() # local variable.
        timeTakenList.addList(self.timeTakenDict.values())
        nTmessage("Time taken by CING by statistics\n%s" % timeTakenList.statsFloat())

        if not self.entry_anno_list_tried:
            nTerror("Failed to find entries that CING tried.")

        self.entry_anno_list_todo.addList(self.entry_anno_list_all)
        self.entry_anno_list_todo = self.entry_anno_list_todo.difference(self.entry_anno_list_done)

        nTmessage("Found %s entries overall for annotation." % len(self.entry_anno_list_all))
        nTmessage("Found %s entries that CING tried (T)." % len(self.entry_anno_list_tried))
        nTmessage("Found %s entries that CING crashed/failed (C)." % len(self.entry_anno_list_crashed))
        nTmessage("Found %s entries that CING stopped (S)." % len(self.entry_anno_list_stopped))
        if not self.entry_anno_list_done:
            nTerror("Failed to find entries that CING did.")
        nTmessage("Found %s entries that CING did (B=A-C-S)." % len(self.entry_anno_list_done))
        nTmessage("Found %s entries todo (A-B)." % len(self.entry_anno_list_todo))
        nTmessage("Found %s entries obsolete (not removed yet)." % len(self.entry_anno_list_obsolete))
        nTmessage("Found entries todo:\n%s" % self.entry_anno_list_todo)
        os.chdir(cwdCache)
    # end def

    """
    Set the list of matched entries and the dictionary holding the
    number of matches. They need to be defined as globals to this module.
    Return zero on error.
    """
    def search_matching_entries(self):
        self.match = MyDict()
#        modification_time = os.path.getmtime("/Users/jd/.cshrc")
#        self.match.d[ "1brv" ] = EntryInfo(time=modification_time)

        ## following statement is equivalent to a unix command like:
        nTdebug("Looking for PDB entries from different databases.")

        resultList = self.getCingEntriesTriedAndDone()
        self.entry_list_tried, self.entry_list_done, self.entry_list_crashed = resultList
        if not self.entry_list_tried:
            nTwarning("Failed to find entries that CING tried.")
#            return 0
        nTmessage("Found %s entries that CING tried." % len(self.entry_list_tried))
        nTmessage("Found %s entries that crashed CING." % len(self.entry_list_crashed))

        if not self.entry_list_done:
            nTwarning("Failed to find entries that CING did.")
#            return 0
        nTmessage("Found %s entries that CING did." % len(self.entry_list_done))

        self.entry_list_all.addList( self.entry_anno_list_all )
        for entry in entryList:
            self.entry_list_all.append( entry + 'Org' )

        self.entry_list_todo.addList(self.entry_list_all)
        self.entry_list_todo = self.entry_list_todo.difference(self.entry_list_done)

        nTmessage("Found entries overall: %s" % len(self.entry_list_all))
        nTmessage("Found entries todo:    %s" % len(self.entry_list_todo))
        nTmessage("Found entries todo:    \n%s" % self.entry_list_todo)

        if self.updateIndices:
            self.update_index_files()

#        nTdebug("premature return until coded completely... TODO:")
        return True



    def make_individual_pages(self, entry_code):
        """
        Just making the one page specific for an entry
        Returns 0 for success.
        """
        nTmessage("Making page for entry: " + entry_code)
        if self.regenerating_pickle:
            return 0
        ## Check to see if there was all giffie files were actually made
        ## If not then still exit with an error
        if not self.is_complete_resource(entry_code):
            nTerror("despite checks no gif fie found for entry: " + entry_code)
            return 1

    def do_analyses_loop(self, processes_max):
        ## Setup a job list
        return
#        job_list = []
#
#        for entry_code in self.new_hits_entry_list:
#            job = (self.make_individual_pages, (entry_code,))
#            job_list.append(job)
#
#        f = forkoff.ForkOff(processes_max=processes_max, max_time_to_wait=self.max_time_to_wait)
#        self.done_entry_list = f.forkoff_start(job_list, self.delay_between_submitting_jobs)
#        nTmessage("Finished following list: %s" % self.done_entry_list)


    def update_index_files(self):
        "Updating the index files"

        number_of_entries_per_row = 5
        number_of_files_per_column = 5

        indexDir = os.path.join(self.results_dir, "index")
        if os.path.exists(indexDir):
            shutil.rmtree(indexDir)
        os.mkdir(indexDir)
        htmlDir = os.path.join(cingRoot, "HTML")

        csvwriter = csv.writer(file(self.index_pdb_file_name, "w"))
        if not self.entry_list_done:
            nTwarning("No entries done, skipping creation of indexes")
            return 1

        self.entry_list_done.sort()

        number_of_entries_per_file = number_of_entries_per_row * number_of_files_per_column
        ## Get the number of files required for building an index
        number_of_entries_all_present = len(self.entry_list_done)
        ## Number of files with indexes in google style
        number_of_files = int(number_of_entries_all_present / number_of_entries_per_file)
        if number_of_entries_all_present % number_of_entries_per_file:
            number_of_files += 1
        nTmessage("Generating %s index html files" % (number_of_files))

#        example_str_template = """ <td><a href=""" + self.pdb_link_template + \
#        """>%S</a><BR><a href=""" + self.bmrb_link_template + ">%b</a>"

        cingImage = '../data/%t/%s/%s.cing/%x/HTML/mol.gif'
        example_str_template = '<td><a href="' + self.cing_link_template + '"><img SRC="' + cingImage + '" border=0 width="200" ></a><BR>%s</td>'
        file_name = os.path.join (self.base_dir, self.data_dir_local, "index.html")
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
#                nTdebug("%5d %5d %5d" % (begin_entry_count, end_entry_count, number_of_entries_all_present))

                old_string = r"<!-- INSERT NEW RESULT STRING HERE -->"
                result_string = "CASD-NMR data sets"

#                begin_entry_code = string.upper(self.entry_list_done[ begin_entry_count - 1 ])
#                end_entry_code = string.upper(self.entry_list_done[ end_entry_count - 1 ])
                begin_entry_code = self.entry_list_done[ begin_entry_count - 1 ]
                end_entry_code = self.entry_list_done[ end_entry_count - 1 ]
                new_row = [ file_id, begin_entry_code, end_entry_code ]
                csvwriter.writerow(new_row)

                new_string = '%s: <B>%s-%s</B> &nbsp;&nbsp; (%s-%s of %s).\n' % (
                        result_string,
                        begin_entry_code,
                        end_entry_code,
                        begin_entry_count,
                        end_entry_count,
                        number_of_entries_all_present
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
                new_file_name = indexDir + '/index_' + repr(file_id) + '.html'
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

                t = pdb_entry_code[1:3]
                startDir = '%s/%s/%s/%s.cing' % ( self.data_dir, t, pdb_entry_code, pdb_entry_code )
                cmd = 'cd %s; find . -name "mol.gif"' % startDir
#                nTdebug("Attempting cmd: [%s]" % cmd)
                output = get_cmd_output( cmd )
                if output == None:
                    nTerror("Failed to find mol.gif")
                    x = 'Molecularsystem' # but not always.
                else:
                    try:
                        x = output.split('/')[1] # ./Molecularsystem/HTML/mol.gif
                    except:
#                        TODO: enable again for this is a valid check it just ruins my output on development.
                        nTwarning("Failed to find molecular system name for %s from output: [%s]" % (pdb_entry_code,output))
                        x = 'Molecularsystem' # but not always.
#                nTdebug("found molecular system name: %s" % x)

                tmp_string = string.replace(example_str_template, r"%S", string.upper(pdb_entry_code)) # does nothing because %S was omitted.
                tmp_string = string.replace(tmp_string, r"%s", pdb_entry_code)
                tmp_string = string.replace(tmp_string, r"%t", t)
                tmp_string = string.replace(tmp_string, r"%x", x)
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
#        nTmessage('Symlinking: %s %s' % (index_file_first, index_file))
        symlink(index_file_first, index_file)

#        ## Make a sym link from the index_bmrb.html file to the index.html file
#        index_file_first = 'index_pdb.html'
#        index_file_first = index_file_first
#        index_file = os.path.join(self.results_dir + "/index", 'index.html')
#        nTdebug('Symlinking (B): %s %s' % (index_file_first, index_file))
#        symlink(index_file_first, index_file)

#        nTmessage("Copy the adjusted php script")
#        org_file = os.path.join(self.base_dir, self.data_dir_local, 'redirect.php')
#        new_file = os.path.join(self.results_dir, 'redirect.php')
#        file_content = open(org_file, 'r').read()
#        old_string = 'URL_BASE'
#        file_content = string.replace(file_content, old_string, self.results_url)
#        open(new_file, 'w').write(file_content)

        nTmessage("Copy the adjusted html redirect")
        org_file = os.path.join(self.base_dir, self.data_dir_local, 'redirect.html')
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
        return 1

    def update(self, new_hits_entry_list=None,doCheckAnnotation=False):
        entryListFileName = os.path.join(baseDir, 'list', 'entry_list_all.csv')
        self.entry_anno_list_all = NTlist()
        self.entry_anno_list_all.addList( readLinesFromFile(entryListFileName, doStrip=True))

        if doCheckAnnotation:
            self.getCingAnnoEntryInfo()
        ## Searches and matches
        if new_hits_entry_list:
            m.new_hits_entry_list = new_hits_entry_list
            nTmessage("Doing list of new entries: %s" % new_hits_entry_list)
#        else:
        if not m.search_matching_entries():
            nTerror("can't search matching entries")
            os._exit(1)

        ## Make the individual and overall web pages including
        ## new versions of the scripts used.
        m.do_analyses_loop(processes_max=processors)

#        Disable for now TODO: enable again.
#        if not m.update_index_files():
#            nTerror("can't update index files")

if __name__ == '__main__':
    cing.verbosity = cing.verbosityDebug

    max_entries_todo = 0    # was 500 (could be as many as u like)
    max_time_to_wait = 12000 # 1y4o took more than 600. This is one of the optional arguments.
    processors = 2    # was 1 may be set to a 100 when just running through to regenerate pickle
    writeWhyNot = True
    updateIndices = True
    doCheckAnnotation = True # default is False
    isProduction = True
    new_hits_entry_list = [] # define empty for checking new ones.
    new_hits_entry_list = ['NeR103ALyon2']
#    new_hits_entry_list = ['atT13']
#    new_hits_entry_list         = string.split("2jqv 2jnb 2jnv 2jvo 2jvr 2jy7 2jy8 2oq9 2osq 2osr 2otr 2rn9 2rnb")

    ## Initialize the project
    m = casdNmrCing(max_entries_todo=max_entries_todo, max_time_to_wait=max_time_to_wait, writeWhyNot=writeWhyNot, updateIndices=updateIndices,
                isProduction=isProduction)
#    m.getCingEntriesTriedAndDone()
    m.update(new_hits_entry_list,doCheckAnnotation=doCheckAnnotation)
    nTmessage("Finished creating the CASD-NMR CING indices")