"""
This script will use NRG files to generate CING reports

If the pickle is polluted do the following steps:
  -0- remove pickle.
  -1- set skip_newer_entries_if_images_exist = 1
      set regenerating_pickle = 1
      set the number of entries high and use 100 processors
  -2- run (takes less than an hour)
  -3- reset all the default options again and run again


When you need to stop a batch processing, send a signal
to it for interuption. E.g. when 22059 is the PID of "python nrgCing.py 1"
do "kill -15 22059". Let it finish for a while when you see:
WARNING: Caught interrupt in parent.
WARNING: Trying to finish up by waiting for subprocesses
WARNING: only 965 out of 1000 jobs were started (not all successfully finished perhaps)
or similar. The minus of -15 is necessary because it needs to signal it's children.

Execute like:

python -u $CINGROOT/python/cing/NRG/nrgCing.py

"""
from cing import cingPythonCingDir
from cing import cingRoot
from cing.Libs import forkoff
from cing.Libs.NTutils import Lister
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import is_pdb_code
from cing.Libs.NTutils import symlink
from cing.Libs.NTutils import toCsv
from cing.Libs.NTutils import writeTextToFile
from cing.NRG.PDBEntryLists import getBmrbNmrGridEntries
from cing.NRG.PDBEntryLists import getBmrbNmrGridEntriesDOCRfREDDone
from cing.NRG.PDBEntryLists import getPdbEntries
from cing.NRG.WhyNot import FAILED_TO_BE_CONVERTED_NRG
from cing.NRG.WhyNot import FAILED_TO_BE_VALIDATED_CING
from cing.NRG.WhyNot import NOT_NMR_ENTRY
from cing.NRG.WhyNot import NO_EXPERIMENTAL_DATA
from cing.NRG.WhyNot import TO_BE_VALIDATED_BY_CING
from cing.NRG.WhyNot import WhyNot
from cing.NRG.WhyNot import WhyNotEntry
import cing
import csv 
import os
import shutil
import string
import time
import urllib

class MyDict(Lister):
    """just a simple dictionary"""
    def __init__(self):
        self.d = {}

class EntryInfo(Lister):
    def __init__(self, time=None):
        self.time = time


class nrgCing(Lister):

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

        self.results_base = 'NRG-CING'
        self.results_base_dir = os.path.join('/Library/WebServer/Documents', self.results_base)
        self.results_dir = self.results_base_dir 

        self.data_dir = os.path.join(self.results_base_dir, 'data')        
#        self.results_dir        = '/big/jurgen/molgrap/'        + run_id
        self.tmp_dir = self.results_dir + '/_tmp_'
        self.results_host = 'localhost' 
        if self.isProduction: 
            # Needed for php script. 
            self.results_host = 'nmr.cmbi.ru.nl'
        self.results_url = 'http://' + self.results_host + '/' + self.results_base + '/'
        
        # The csv file name for indexing pdb
        self.index_pdb_file_name = self.results_dir + "/index/index_pdb.csv"

        if self.isProduction: 
            # For file: /usr/scratch/whynot/comments/20090106_NRG-CING.txt_done        
            self.why_not_db_comments_dir = "/Volumes/cmbi8/usr/scratch/whynot/comments"
            # For many files like: /usr/data/raw/nmr-cing/d3/1d3z/1d3z.exist
            self.why_not_db_raw_dir = "/Volumes/cmbi8/usr/data/data/raw/nrg-cing"
        else:
            self.why_not_db_comments_dir = os.path.join(self.results_base_dir,"cmbi8","comments")
            self.why_not_db_raw_dir = os.path.join(self.results_base_dir,"cmbi8","raw")

        self.why_not_db_comments_file = 'NRG-CING.txt_done'
        
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
        self.pdb_entries_White = {}
        self.processes_todo = None
        ## Dictionary with pid:entry_code info on running children
        self.child_d = {}

        ##No changes required below this line
        ###############################################################################        

        NTmessage("Publish results at directory    : " + self.results_dir)
        NTmessage("Do maximum number of entries    : " + `self.max_entries_todo`)
        
        os.chdir(self.results_dir)

        ## List of 'new' entries for which hits were found
        self.new_hits_entry_list = []
        self.done_entry_list = []

    """ Returns zero for failure
    """
    def get_bmrb_links(self):
        url_many2one = self.url_csv_file_link_base + "/score_many2one.csv"
        url_one2many = self.url_csv_file_link_base + "/score_one2many.csv"

        for url_links in (url_many2one, url_one2many):     
            try:
                resource = urllib.urlopen(url_links)
                reader = csv.reader(resource)
            except IOError:
                NTerror("couldn't open url for reader: " + url_links)
                return 0

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
                NTmessage("Found number of matches from PDB to BMRB entries: %d" % len(self.matches_many2one))
            else:
                NTmessage("Found number of matches from BMRB to PDB entries: %d" % len(self.matches_one2many))            
        return 1

        
    """
    Check the resource dir for existence of all needed items.
    this is quit i/o intensive but the only way to guarantee it
    as the pickle might get out of sync with reality
    Returns one for complete resource.
    """
    def is_complete_resource(self, entry_code):
        NTdebug("checking is_complete_resource for entry: " + entry_code)
        sub_dir = entry_code[1:3]
        indexFileName = os.path.join (self.results_dir, 'data', sub_dir, entry_code, entry_code + ".cing", 'index.html')
        return os.path.isfile(indexFileName)
 
 
    def getCingEntriesTriedAndDone(self):
        "Returns list or None for error"
        NTdebug("From disk get the entries done in NRG-CING")
        
        entry_list_tried = []
        entry_list_done = []
        
        
        subDirList = os.listdir('data')
        for subDir in subDirList:
            if len(subDir) != 2:
                if subDir != ".DS_Store":
                    NTdebug('Skipping subdir with other than 2 chars: [' + subDir + ']')
                continue 
            entryList = os.listdir(os.path.join('data',subDir))
            for entryDir in entryList:
                entry_code = entryDir
                if not is_pdb_code(entry_code):
                    if entry_code != ".DS_Store":
                        NTerror("String doesn't look like a pdb code: " + entry_code)
                    continue

                cingDirEntry = os.path.join('data',subDir, entry_code, entry_code + ".cing")
                if not os.path.exists(cingDirEntry):
                    continue
                
                entry_list_tried.append(entry_code)
                indexFileEntry = os.path.join(cingDirEntry, "index.html")
                if os.path.exists(indexFileEntry):
                    entry_list_done.append(entry_code)
                     
        
        return (entry_list_tried, entry_list_done)


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
        NTdebug("Looking for PDB entries from different databases.")

        if self.writeWhyNot:
            self.entry_list_pdb = getPdbEntries()
            if not self.entry_list_pdb:
                NTerror("No PDB entries found")
                return 0
            NTmessage("Found %s PDB entries." % len(self.entry_list_pdb))
    
            self.entry_list_nmr = getPdbEntries(onlyNmr=True)
            if not self.entry_list_nmr:
                NTerror("No NMR entries found")
                return 0
            NTmessage("Found %s NMR entries." % len(self.entry_list_nmr))
    
            
            self.entry_list_nrg = getBmrbNmrGridEntries()
            if not self.entry_list_nrg:
                NTerror("No NRG entries found")
                return 0
            NTmessage("Found %s PDB entries in NRG." % len(self.entry_list_nrg))
            
            ## The list of all entry_codes for which tgz files have been found
            self.entry_list_nrg_docr = getBmrbNmrGridEntriesDOCRfREDDone()
            if not self.entry_list_nrg_docr:
                NTerror("No NRG DOCR entries found")
                return 0
            NTmessage("Found %s NRG DOCR entries." % len(self.entry_list_nrg_docr))                    
            if len(self.entry_list_nrg_docr) < 3000:
                NTerror("watch out less than 3000 entries found [%s] which is suspect; quitting" % len(self.entry_list_nrg_docr))
                return 0
    
            (self.entry_list_tried, self.entry_list_done) = self.getCingEntriesTriedAndDone()
            if not self.entry_list_tried:
                NTerror("Failed to find entries that CING tried.")
                return 0
            NTmessage("Found %s entries that CING tried." % len(self.entry_list_tried))

        if not self.entry_list_done:
            NTerror("Failed to find entries that CING did.")
            return 0
        NTmessage("Found %s entries that CING did." % len(self.entry_list_done))
        
        if self.writeWhyNot:
            self.doWriteWhyNot()
        
        if self.updateIndices:
            self.update_index_files()
            
        # premature return until coded completely... TODO:
        return 0
    
        
#        ## Look in dictionary for entries that are no longer on file and
#        ## remove them from the dictionary and
#        ## if present remove the files from the result directory
#        NTmessage("Checking if any entries in NRG-CING are no longer in the NRG")
#        for entry_code in self.match.d.keys():
#            if not entry_code in entry_list_all:
#                NTwarning("removing old entry no longer on file: " + entry_code)
#                NTmessage("Sleeping a second as to give a user a chance to interrupt these removes")
#                time.sleep(1)
#                del self.match.d[ entry_code ]
#                ## Delete old data if it is there.                
#                if not self.remove_resource(entry_code):
#                    NTerror("failed to remove resource for entry: " + entry_code)
#                    return 0
#
#
#        ## Look on file system for dictionary entries that are no longer current
#        ## remove it from the dictionary and
#        ## if present remove it from the directory
#        NTmessage("Checking if any entries in the pickle are no longer (completely) in the image archive.")
#            
#        for entry_code in self.match.d.keys():
#            if not self.is_complete_resource(entry_code):
#                NTwarning("entry in pickle and PDB is no longer complete as a resource on file: " + entry_code)
#                NTwarning("entry will be deleted from pickle until it's present again.")
#                del self.match.d[ entry_code ]
#                self.pickle_changed += 1
#                ## Delete old data if it is there.                
#                if not self.remove_resource(entry_code):
#                    NTerror("failed to remove giffies for entry: " + entry_code)
#                    return 0
#
#        NTmessage("Compiling a list of new entries todo")
#        ## Entry_list will contain entries that will be searched
#        entry_list = []
#        for entry_code in entry_list_all:
#            ## Check if we're not overworking
#            if len(entry_list) >= self.max_entries_todo:
#                NTwarning("Using truncated list of entries todo;            length                  : " + `self.max_entries_todo`)
#                NTwarning("Actual length of list of entries that should be done COULD be as large as: " + `len(entry_list_all)`)
#                break
#            
#            chars2and3 = entry_code[1:3]
#            file_name = self.data_dir + os.sep + chars2and3 + os.sep + "pdb" + entry_code + ".ent.gz"            
#            if os.path.isfile(file_name):
#                modification_time = os.path.getmtime(file_name)
#            else:
#                NTerror("file doesn't exist: " + file_name)
#                NTerror("assuming modification time is current time")
#                modification_time = time.time()
#            
#            ## Entry completely new?            
#            if not entry_code in keys_org:
#                NTmessage("New entry in pdb with code: %s" % entry_code)
#                entry_list.append(entry_code)
#                self.match.d[ entry_code ] = EntryInfo(time=modification_time)
#                self.pickle_changed += 1
#            else:
#                ## Include files that have been modified
#                if modification_time > self.match.d[ entry_code ].time:
#                    NTmessage("Found entry %s with newer modification times:\n\t%s and\n\t%s" % (
#                          entry_code,
#                            time.ctime(modification_time),
#                            time.ctime(self.match.d[ entry_code ].time)
#                          ))
#                    self.match.d[ entry_code ] = EntryInfo(time=modification_time)
#                    self.pickle_changed += 1
#                    if self.skip_updated_pdb_files:
#                        NTwarning("Skipping regeneration of PDB file because option set for skip_updated_pdb_files")
#                        NTmessage("Modification time for this entry updated though.")
#                    else:
#                        entry_list.append(entry_code)
#                    
#                    
#        if len(entry_list):
#            NTmessage("Scanning %s 'new' entries: %s" % \
#                  (len(entry_list), entry_list))
#        else:
#            NTmessage("No new entries to be scanned")
#            return 1 # Success
#
#
#        for entry_code in entry_list:
#            ## Add info to dictionary
#            self.new_hits_entry_list.append(entry_code)
#
#        NTmessage("Total of %d new entries" % len(self.new_hits_entry_list))
#        return 1 # Success


    def doWriteWhyNot(self):
        "Create WHY_NOT list"
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
            del( whyNot[entryId] )
        # end loop over entries
        whyNotStr = '%s' % whyNot
#        NTdebug("whyNotStr truncated to 1000 chars: [" + whyNotStr[0:1000] + "]")
        writeTextToFile("NRG-CING.txt", whyNotStr)
        writeTextToFile("entry_list_pdb.csv", toCsv(self.entry_list_pdb))
        writeTextToFile("entry_list_nmr.csv", toCsv(self.entry_list_nmr))
        writeTextToFile("entry_list_nrg.csv", toCsv(self.entry_list_nrg))
        writeTextToFile("entry_list_nrg_docr.csv", toCsv(self.entry_list_nrg_docr))
        writeTextToFile("entry_list_tried.csv", toCsv(self.entry_list_tried))
        writeTextToFile("entry_list_done.csv", toCsv(self.entry_list_done))
                     
        why_not_db_comments_file = os.path.join(self.why_not_db_comments_dir, self.why_not_db_comments_file)
        NTdebug("Copying to: " + why_not_db_comments_file)
        shutil.copy("NRG-CING.txt", why_not_db_comments_file)
        for entryId in self.entry_list_done:
            # For many files like: /usr/data/raw/nmr-cing/           d3/1d3z/1d3z.exist
            char23 = entryId[1:3]
            subDir = os.path.join(self.why_not_db_raw_dir, char23, entryId)
            if not os.path.exists(subDir):
                os.makedirs(subDir)
            fileName = os.path.join(subDir, entryId + ".exist")
            if not os.path.exists(fileName):
                NTdebug("Creating: " + fileName)
                fp = open(fileName, 'w')
    #            fprintf(fp, ' ')
                fp.close()
            
        

    def make_individual_pages(self, entry_code):
        """
        Just making the one page specific for an entry
        Returns 0 for success.
        """
        NTmessage("Making page for entry: " + entry_code)
        if self.regenerating_pickle:
            return 0
        ## Check to see if there was all giffie files were actually made
        ## If not then still exit with an error
        if not self.is_complete_resource(entry_code):
            NTerror("despite checks no gif fie found for entry: " + entry_code)
            return 1

    def do_analyses_loop(self, processes_max):
        ## Setup a job list
        return
        job_list = []
        
        for entry_code in self.new_hits_entry_list:
            job = (self.make_individual_pages, (entry_code,))
            job_list.append(job)

        f = forkoff.ForkOff(processes_max=processes_max, max_time_to_wait=self.max_time_to_wait)
        self.done_entry_list = f.forkoff_start(job_list, self.delay_between_submitting_jobs)
        NTmessage("Finished following list: %s" % self.done_entry_list) 

                
    def update_index_files(self):
        "Updating the index files"

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
            return 1

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
        return 1
    
    def update(self, new_hits_entry_list=None):
        if not m.get_bmrb_links():
            NTerror("can't get bmrb links")
            os._exit(1)
                
        ## Searches and matches
#        if new_hits_entry_list:
#            m.new_hits_entry_list = new_hits_entry_list
#            NTmessage("Doing list of new entries: %s" % new_hits_entry_list)
#        else:
        if not m.search_matching_entries():
            NTerror("can't search matching entries")
            os._exit(1)
                    
        ## Make the individual and overall web pages including
        ## new versions of the scripts used.    
        m.do_analyses_loop(processes_max=processors)
    
        if not m.update_index_files():
            NTerror("can't update index files")    
    
if __name__ == '__main__':
    cing.verbosity = cing.verbosityDebug

    max_entries_todo = 1    # was 500 (could be as many as u like)
    max_time_to_wait = 12000 # 1y4o took more than 600. This is one of the optional arguments.
    processors = 2    # was 1 may be set to a 100 when just running through to regenerate pickle                                       
    writeWhyNot = True
    updateIndices = True
    isProduction = False
    new_hits_entry_list = [] # define empty for checking new ones.
    new_hits_entry_list = ['1d3z']
#    new_hits_entry_list         = string.split("2jqv 2jnb 2jnv 2jvo 2jvr 2jy7 2jy8 2oq9 2osq 2osr 2otr 2rn9 2rnb")
    
    ## Initialize the project 
    m = nrgCing(max_entries_todo=max_entries_todo, max_time_to_wait=max_time_to_wait, writeWhyNot=writeWhyNot, updateIndices=updateIndices,
                isProduction=isProduction)
#    m.getCingEntriesTriedAndDone() 
    m.update(new_hits_entry_list)