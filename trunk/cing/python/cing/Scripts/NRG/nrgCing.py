"""
This script will use NRG files to generate CING reports

If the pickle is polluted do the following steps:
  -0- remove pickle.
  -1- set skip_newer_entries_if_images_exist = 1
      set regenerating_pickle = 1
      set the number of entries high and use 100 processors
  -2- run (takes less than an hour)
  -3- reset all the default options again and run again

When the modification times of the NRG files were reset
set doUpdateAfterFileSystemReset = 1

When you need to stop a batch processing, send a signal
to it for interuption. E.g. when 22059 is the PID of "python nrgCing.py 1"
do "kill -15 22059". Let it finish for a while when you see:
WARNING: Caught interrupt in parent.
WARNING: Trying to finish up by waiting for subprocesses
WARNING: only 965 out of 1000 jobs were started (not all successfully finished perhaps)
or similar. The minus of -15 is necessary because it needs to signal it's children.
"""
from cing import cingPythonCingDir
from cing.Libs import forkoff
from cing.Libs.NTutils import Lister
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import is_pdb_code
from cing.Libs.NTutils import symlink
from cing.Libs.find import find
import csv 
import os
import shelve
import shutil
import string
import time
import urllib

__author__ = "$Author: jurgen $"
__revision__ = "$Revision: 1.4 $"
__date__ = "$Date: 2006/10/19 17:35:50 $"



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
                 max_time_to_wait=20
                ):

        # Dir as base in which all info and scripts like this one resides
#        self.base_dir           = '/share/jurgen/BMRB/Molgrap'
        self.base_dir = os.path.join(cingPythonCingDir, "Scripts", "NRG")
        self.run_id = 'NRG'
        self.backcolor = 'cing_blue'

        self.results_base = 'cing_reports'
        self.results_base_dir = os.path.join('/Library/WebServer/Documents', self.results_base)
        self.results_dir = os.path.join(self.results_base_dir, self.run_id) 

#        self.coordinates_dir    = '/dumpzone/pdb/nozip/data/structures/all/pdb'        
        self.coordinates_dir = os.path.join(self.results_base_dir + 'projects')        
#        self.results_dir        = '/big/jurgen/molgrap/'        + run_id
        self.tmp_dir = self.results_dir + '/_tmp_'
#        self.results_url        = 'http://www.bmrb.wisc.edu/servlet_data/' + run_id
        self.results_url = 'http://localhost/' + self.results_base + '/' + self.run_id
        
        # The database file name:
        self.dbase_file_name = self.results_dir + os.sep + "pickle"
        # The csv file name for indexing bmrb
        self.index_bmrb_file_name = self.results_dir + "/index/index_bmrb.csv"
        # The csv file name for indexing pdb
        self.index_pdb_file_name = self.results_dir + "/index/index_pdb.csv"

        ## Which files shall be selected.
        ## Give a Unix style file pattern, not a regular expression
        self.file_match_pattern = r'*.tgz'                                        
        ## Maximum number of pictures to create before ending
        ## and writting the pickle and web page overview again.
        ## Restart the process to do any remaining entries.
        ## Don't overlap processes!!!
        self.max_entries_todo = max_entries_todo
        ## Levels of verbosity (inhereted by some other modules called)
                  # 0 Only errors
                  # 1 and warnings
                  # 2 and other stuff, this is the normal output level!
                  # 3 don't stop there
                  # 9 all that and debug info
        self.max_time_to_wait = max_time_to_wait 
        ## Set this variable to 0 for usual operations. Set to 1 for
        ## not generating new images if all are present all ready
        ## without regard to the up to dateness of the pdb file.
        self.skip_newer_entries_if_images_exist = 0

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
        self.pdb_entries_White = {}
        self.processes_todo = None
        ## Dictionary with pid:entry_code info on running children
        self.child_d = {}

        ##No changes required below this line
        ###############################################################################        

        if self.verbose > 1:
            NTmessage("Publish results at directory    :" + self.results_dir)
            NTmessage("Do maximum number of entries    :" + `self.max_entries_todo`)
        
        os.chdir(self.coordinates_dir)

        ## List of 'new' entries for which hits were found
        self.new_hits_entry_list = []
        self.done_entry_list = []
        self.pickle_changed = 0
        self.molgrap = {}

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
                NTerror(": couldn't open url for reader: " + url_links)
                return 0

            try:
                header_read = reader.next()
                if self.verbose > 2:        
                    NTdebug("read header: " + header_read)
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

        
    def pickle_read(self):

        ## Check out the latest copy of the information on the dipolar matches
        ## from the shelve.
        # First check existence
        if os.path.isfile(self.dbase_file_name):
            NTmessage("Loading old information from file: %s" % self.dbase_file_name)
            dbase = shelve.open(self.dbase_file_name)
            self.match = dbase[ 'molgrap_dict' ]
            # Close will NOT BE AUTOMATIC on close of program
            dbase.close()
        else:
            NTwarning("No old information available")
            NTwarning("Check if all entries will be scanned again")
            self.match = MyDict()

        NTmessage("Used dictionary: %s entries" % len(self.match.d))
##        NTmessage("Dictionary keys:"+ self.match.d.keys()


    def pickle_write(self):
        ## Save the pickle
        NTmessage("Write dictionary: %s entries" % len(self.match.d))
##        NTmessage("Dictionary keys:"+ self.match.d.keys()

        dbase = shelve.open(self.dbase_file_name)
        dbase[ 'molgrap_dict' ] = self.match
        dbase.close()


    """
    Check the resource dir for existance of all needed items.
    this is quit i/o intensive but the only way to garantee it
    as the pickle might get out of sync with reality
    Returns one for complete resource.
    """
    def is_complete_resource(self, entry_code):
        if self.verbose > 2:
            NTdebug("checking is_complete_resource for entry: " + entry_code)
        sub_dir = entry_code[1:3]
        new_dir = os.path.join (self.results_dir + '/pic', sub_dir)
        if not os.path.isdir(new_dir):
            return 0 ## INcomplete
        ## Check to see if all giffie files were actually made
        allPresent = 1
        gif_list = [ '', '_xl', '_big', '_pin' ]
        for giffie in gif_list:
            giffie_file_name = new_dir + '/' + entry_code + giffie + '.gif'
            if not os.path.isfile(giffie_file_name):
                allPresent = 0
                if self.verbose > 2:
                    NTdebug("no giffie found for file:" + giffie_file_name)
        if allPresent:
            return 1 ## complete
        return 0
    
        
    """
    Removes all giffies for a particular entry. Returns 0 in case of error.
    """
    def remove_resource(self, entry_code):
        if self.verbose > 2:
            NTdebug("remove resource for entry: " + entry_code)
        sub_dir = entry_code[1:3]
        new_dir = os.path.join (self.results_dir + '/pic', sub_dir)
        if not os.path.isdir(new_dir):
            if self.verbose > 2:
                NTdebug("resource dir is already not present: " + new_dir)
            return 1 ## already removed
        ## Try per giffie file
        gif_list = [ '', '_xl', '_big', '_pin' ]
        for giffie in gif_list:
            giffie_file_name = new_dir + '/' + entry_code + giffie + '.gif'
            if os.path.isfile(giffie_file_name):
                NTdebug("removing giffie: " + giffie_file_name)
                if os.unlink(giffie_file_name):
                    NTerror(": failed removing giffie: " + giffie_file_name)
                    return 0
        if os.path.isdir(new_dir):
            anyRemaining = os.listdir(new_dir) ## Get a listing.
            if not anyRemaining: ## an empty object is false. so remove the dir if nothing left.
                NTmessage("Removing sub dir: " + new_dir)
                if os.rmdir(new_dir):
                    NTerror(": failed removing dir: " + new_dir)
                    return 0
        return 1


    """
    The entries that were not (completely) done should not be included
    """
    def pickle_update_times_only(self):

        NTmessage("Updating all the modification times to today.")
            
        keys = self.match.d.keys()
        modification_time = time.time()
        NTmessage("To now time: " + time.ctime(modification_time))
        
        for entry_code in keys:
            self.match.d[ entry_code ] = EntryInfo(time=modification_time)


    """
    The entries that were not (completely) done should not be included
    """
    def pickle_cleanup(self):

        NTmessage("Cleaning up any mess")
            
        ## This is a bit stupid method because they are still sorted
        index = 0
        for entry_code in self.new_hits_entry_list:
            if not index in self.done_entry_list:
                del self.match.d[ entry_code ]        
                if self.verbose > 2:
                    NTmessage("Deleting entry from pickle because not done: " + entry_code)
            index += 1

    """
    Set the list of matched entries and the dictionary holding the 
    number of matches. They need to be defined as globals to this module.
    Return zero on error.
    """
    def search_matching_entries(self):
        ## The list of all entry_codes for which pdb file have been found
        entry_list_all = []

        ## following statement is equivalent to a unix command like:
        NTmessage("Looking for all pdb files in cwd: " + os.path.abspath(os.curdir))
            
        file_list_all = find.find(self.file_match_pattern)
        # Use the below for testing as it takes a few minutes to find all from the above.
        #file_list_all = [ './pdb1brv.pdb', './pdb2a33.pdb' ]
        #print file_list_all
        NTmessage("Found %s entries on file" % len(file_list_all))
        
        ## Strip the leading part from e.g.: ./pdb1brv.pdb
        for file_name in file_list_all:
            file_name = os.path.basename(file_name)
            entry_code = file_name[3:7]
            ## Check whether that's reasonable by matching against reg.exp.
            if not is_pdb_code(entry_code):
                tmpStr = "String doesn't look like a pdb code: ", entry_code
                raise RuntimeError, tmpStr
            entry_list_all.append(entry_code)            
            
        if not entry_list_all:
            NTerror("watch out no entries found; disable this check if really correct")
            return 0
        ## Look in dictionary for entries that are no longer on file and
        ## remove them from the dictionary and
        ## if present remove the files from the result directory
        NTmessage("Checking if any entries in the pickle are no longer in the pdb")
        for entry_code in self.match.d.keys():
            if not entry_code in entry_list_all:
                NTwarning(": removing old entry no longer on file: " + entry_code)
                NTmessage("Sleeping a second as to give a user a chance to interrupt these removes")
                time.sleep(1)
                del self.match.d[ entry_code ]
                self.pickle_changed += 1
                ## Delete old data if it is there.                
                if not self.remove_resource(entry_code):
                    NTerror(": failed to remove giffies for entry: " + entry_code)
                    return 0

        ## Look on file system for dictionary entries that are no longer current
        ## remove it from the dictionary and
        ## if present remove it from the directory
        NTmessage("Checking if any entries in the pickle are no longer (completely) in the image archive.")
            
        for entry_code in self.match.d.keys():
            if not self.is_complete_resource(entry_code):
                if self.verbose > 1:
                    NTwarning(": entry in pickle and PDB is no longer complete as a resource on file: " + entry_code)
                    NTwarning(": entry will be deleted from pickle until it's present again.")
                del self.match.d[ entry_code ]
                self.pickle_changed += 1
                ## Delete old data if it is there.                
                if not self.remove_resource(entry_code):
                    NTerror(": failed to remove giffies for entry: " + entry_code)
                    return 0

        if self.verbose > 1:
            NTmessage("Compiling a list of new entries todo")
            NTmessage("and checking old entries' time stamps too")
        ## Entry_list will contain entries that will be searched
        entry_list = []
        keys_org = self.match.d.keys()
        for entry_code in entry_list_all:
            ## Check if we're not overworking
            if len(entry_list) >= self.max_entries_todo:
                NTwarning(": Using truncated list of entries todo;            length                  : " + `self.max_entries_todo`)
                NTwarning(": Actual length of list of entries that should be done COULD be as large as: " + `len(entry_list_all)`)
                break
            
            chars2and3 = entry_code[1:3]
            file_name = self.coordinates_dir + os.sep + chars2and3 + os.sep + "pdb" + entry_code + ".ent.gz"            
            if os.path.isfile(file_name):
                modification_time = os.path.getmtime(file_name)
            else:
                NTerror(": file doesn't exist: " + file_name)
                NTerror(": assuming modification time is current time")
                modification_time = time.time()
            
            ## Entry completely new?            
            if not entry_code in keys_org:
                NTmessage("New entry in pdb with code: %s" % entry_code)
                entry_list.append(entry_code)
                self.match.d[ entry_code ] = EntryInfo(time=modification_time)
                self.pickle_changed += 1
            else:
                ## Include files that have been modified
                if modification_time > self.match.d[ entry_code ].time:
                    NTmessage("Found entry %s with newer modification times:\n\t%s and\n\t%s" % (
                          entry_code,
                            time.ctime(modification_time),
                            time.ctime(self.match.d[ entry_code ].time)
                          ))
                    self.match.d[ entry_code ] = EntryInfo(time=modification_time)
                    self.pickle_changed += 1
                    if self.skip_updated_pdb_files:
                        NTwarning("Skipping regeneration of PDB file because option set for skip_updated_pdb_files")
                        NTmessage("Modification time for this entry updated though.")
                    else:
                        entry_list.append(entry_code)
                    
                    
        if len(entry_list):
            NTmessage("Scanning %s 'new' entries: %s" % \
                  (len(entry_list), entry_list))
        else:
            NTmessage("No new entries to be scanned")
            return 1 # Success


        for entry_code in entry_list:
            ## Add info to dictionary
            self.new_hits_entry_list.append(entry_code)

        NTmessage("Total of %d new entries" % len(self.new_hits_entry_list))
        return 1 # Success


    """
    Just making the one page specific for an entry
    Returns 0 for success.
    """
    def make_individual_pages(self, entry_code):
        NTmessage("Making page for entry" + entry_code)
        if self.regenerating_pickle:
            return 0
        ## Check to see if there was all giffie files were actually made
        ## If not then still exit with an error
        if not self.is_complete_resource(entry_code):
            NTerror(": despite checks no giffie found for entry:" + entry_code)
            return 1

    """
    Just making the one page specific for an entry.
    Returns None for success.
    """
    def do_analyses_loop(self, processes_max):
        ## Setup a job list

        job_list = []
        
        for entry_code in self.new_hits_entry_list:
            job = (self.make_individual_pages, (entry_code,))
            job_list.append(job)

        f = forkoff.ForkOff(
                processes_max=processes_max,
                max_time_to_wait=self.max_time_to_wait,
                verbosity=self.verbose
                )
        self.done_entry_list = f.forkoff_start(job_list, self.delay_between_submitting_jobs)
        NTmessage("Finished following list:" + self.done_entry_list)

    """
    Remove original index files
    """
    def delete_index_files (self):
        for doBMRB2PDB in (0, 1): 
            count = 0
            while 1:
                count += 1
                bmrb_insert = "_pdb"
                if (doBMRB2PDB):
                    bmrb_insert = "_bmrb"
                file_name = self.results_dir + '/index/' + 'index%s_%d.html' % (bmrb_insert, count)
                if os.path.isfile(file_name):
                    NTdebug("Deleting index file: " + file_name)
                    os.unlink(file_name)
                else:
                    NTdebug("Removed last index file before not finding: " + file_name)
                    break
                
            file_name = self.results_dir + '/index/' + 'index%s.html' % bmrb_insert
            if os.path.islink(file_name) or os.path.isfile(file_name):
                NTdebug("Deleting index file" + file_name)
                os.unlink(file_name)
            else:
                NTwarning("Not finding overall index file:" + file_name)
            
        file_name = self.results_dir + '/index/' + 'index.html'
        if os.path.islink(file_name) or os.path.isfile(file_name):
            NTdebug("Deleting index file: " + file_name)
            os.unlink(file_name)
        else:
            NTwarning("Not finding overall overall index file: " + file_name)
                

    """
    Updating the index files disclosing the results for both ways:
    PDB to BMRB and BMRB to PDB.
    """
    def update_index_files(self):

        number_of_entries_per_row_pdb = 10
        number_of_files_per_column_pdb = 10
        number_of_entries_per_row_bmrb = 4
        number_of_files_per_column_bmrb = 4
        number_of_entries_per_row_White = number_of_entries_per_row_pdb
        number_of_files_per_column_White = number_of_files_per_column_pdb
        logo_text_bmrb = """
<A HREF="http://www.bmrb.wisc.edu"><img SRC="http://www.bmrb.wisc.edu/WebModule/wattos/MRGridServlet/images/bmrb_logo_brown_fg_cream_bg.gif" TITLE="BMRB home" border="0"></A>
"""
        logo_text_White = logo_text_bmrb
#"""<A HREF="http://www.uwstructuralgenomics.org/"><img SRC="http://www.uwstructuralgenomics.org/images/Whiteheader.jpg" TITLE="White home" border="0"></A>
#<BR>"""
        color_scheme_text_bmrb = """text="#660000" bgcolor="#FFFFCC" link="#666633" vlink="#999966" alink="#999966\""""
        color_scheme_text_White = ""
## No settings required  after this line for this method
########################################################################################        


        self.delete_index_files()            
        for doBMRB2PDB in (0, 1):            
            keys = self.match.d.keys()
            bmrb_insert = "_pdb"
            color_scheme_text = color_scheme_text_bmrb
            logo_text = logo_text_bmrb
            if self.doWhiteArchive:
                if doBMRB2PDB:
                    continue
                header_text = "Molecular images of all entries in the PDB"
                footer_text = """
                       The PDB entry link is to the RCSB PDB site. Below that, a link
                       to the BMRB entry is given for those PDB entries originating from NMR studies that 
                       have NMR experimental data deposited with BMRB.
                       A version with yellow background exists <a href=../../molgrap/index.html>here</a>."""
                number_of_entries_per_row = number_of_entries_per_row_White
                number_of_files_per_column = number_of_files_per_column_White
                color_scheme_text = color_scheme_text_White
                logo_text = logo_text_White
            else:
                header_text = "Molecular images of all PDB entries"
                footer_text = """
                       The PDB entry link is to the RCSB PDB site. Below that, a link
                       to the BMRB entry is given for those PDB entries originating from NMR studies that 
                       have NMR experimental data deposited with BMRB.
                       The reverse index can be found <a href=index_bmrb.html>here</a>.
                       A version with white background exists <a href=../../molgrapWhite/index.html>here</a>."""
                number_of_entries_per_row = number_of_entries_per_row_pdb
                number_of_files_per_column = number_of_files_per_column_pdb
            if doBMRB2PDB:
                number_of_entries_per_row = number_of_entries_per_row_bmrb
                number_of_files_per_column = number_of_files_per_column_bmrb                
                header_text = "Molecular images for BMRB entries from a related PDB entry"
                footer_text = \
                    """The BMRB entry link is to the 
                       NMR experimental data deposited with BMRB. Below that, a link
                       is provided to the PDB entry used to generate the images.
                       The reverse index can be found <a href=index_pdb.html>here</a>.
                    """
                bmrb_insert = "_bmrb"
                keys_bmrb = self.matches_one2many.keys()
                keys = []
                for bmrb_entry_code in keys_bmrb:
                    pdb_entry_code = self.matches_one2many[ bmrb_entry_code ]
                    if (self.match.d.has_key(pdb_entry_code)):                        
                        keys.append(string.atoi(bmrb_entry_code))
                    else:
                        NTmessage("DEBUG WARNING: skipping bmrb code      : " + bmrb_entry_code)
                        NTmessage("DEBUG WARNING: because missing pdb code: " + pdb_entry_code)
                csvwriter = csv.writer(file(self.index_bmrb_file_name, "w"))
            else:
                csvwriter = csv.writer(file(self.index_pdb_file_name, "w"))
                
            if not keys:
                if doBMRB2PDB:
                    NTerror(": no entries in BMRB to PDB, skipping creation of indexes")
                    return 0
                else:
                    NTwarning("no entries in pickle, skipping creation of indexes")
                    return 1
                    
            keys.sort()
            # Now convert the BMRB ids back to strings.
            if doBMRB2PDB:
                keys_tmp = []
                for bmrb_entry_code in keys:
                    keys_tmp.append(`bmrb_entry_code`)
                keys = keys_tmp
                keys.reverse()
            
            number_of_entries_per_file = number_of_entries_per_row * number_of_files_per_column            
            ## Get the number of files required for building an index
            number_of_entries_all_present = len(keys)
            ## Number of files with indexes in google style
            number_of_files = int(number_of_entries_all_present / number_of_entries_per_file)
            if (number_of_entries_all_present % number_of_entries_per_file):
                number_of_files += 1
            NTmessage("Generating %s %s index html files" % (number_of_files, bmrb_insert))
                    
            ## Initialize a string object for holding the html code to be inserted
            ## in the example file. Abuse the formatting chars to insert specific
            ## strings later on.
#            insert_text_template = \
#                            "<tr>" + \
#                                number_of_entries_per_row * \
#                                "<td>PDB entry code</td><td>Pin up</td>" + \
#                            "</tr>"
            
            if doBMRB2PDB:
                example_str_template = \
                """
                <td><a href=""" + self.bmrb_link_template + \
                """>%b</a><BR>
                    <a href=""" + self.pdb_link_template + \
                ">%S</a>"
                image_insert = ""
            else:
                example_str_template = \
                """
                <td><a href=""" + self.pdb_link_template + \
                """>%S</a><BR>
                    <a href=""" + self.bmrb_link_template + \
                ">%b</a>"                
                image_insert = "_pin"
##                if self.doWhiteArchive:
##                    image_insert = ""
                    
            example_str_template = example_str_template + \
                """</td>
                <td><a href="../pic/%t/%s_xl.gif"><img SRC="../pic/%t/%s""" + image_insert + """.gif" border=0 ></a></td>
                """
            file_name = os.path.join (self.base_dir, "index.html")
            file_content = open(file_name, 'r').read()
            old_string = r"<!-- INSERT NEW DATE HERE -->"
            new_string = time.asctime()
            file_content = string.replace(file_content, old_string, new_string)
            old_string = r"<!-- INSERT NEW HEADER HERE -->"
            file_content = string.replace(file_content, old_string, header_text)
            old_string = r"<!-- INSERT NEW FOOTER HERE -->"
            file_content = string.replace(file_content, old_string, footer_text)
            old_string = r"<!-- INSERT NEW LOGO HERE -->"
            file_content = string.replace(file_content, old_string, logo_text)
            old_string = r"<!-- INSERT NEW COLOR SCHEME HERE -->"
            file_content = string.replace(file_content, old_string, color_scheme_text)

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

            ## Repeat for all entries plus a dummy pass for writting the last index file    
            for x_entry_code in keys + [ None ]:
                if x_entry_code:
                    if doBMRB2PDB:
                        bmrb_entry_code = x_entry_code
                        if not self.matches_one2many.has_key(bmrb_entry_code):
                            NTerror("bmrb entry code as a key not found in key list (code bug): %s %s" % (
                             bmrb_entry_code,
                             keys))
                            return 0
                        pdb_entry_code = self.matches_one2many[bmrb_entry_code]                   
                    else:
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
                    NTdebug("%5d %5d %5d" % (
                            begin_entry_count, end_entry_count, number_of_entries_all_present))

                    old_string = r"<!-- INSERT NEW RESULT STRING HERE -->"
                    jump_form_start = '<FORM method="GET" action="%s">' % self.url_redirecter
                    result_string = jump_form_start + "PDB entries"
                    db_id = "PDB"
                    if doBMRB2PDB:
                        result_string = jump_form_start + "BMRB entries (most recent first)"
                        db_id = "BMRB"

                    jump_form = '<INPUT type="hidden" name="database" value="%s">' % string.lower(db_id)
                    jump_form = jump_form + \
"""<INPUT type="text" size="4" name="id" value="" >            
<INPUT type="submit" name="button" value="go">"""                   
                    jump_form_end = "</FORM>"

                    begin_entry_code = string.upper(keys[ begin_entry_count - 1 ])
                    end_entry_code = string.upper(keys[ end_entry_count - 1 ])
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
                        prev_string = '<a href="index%s_%s.html">Previous &lt;</a>' % (
                            bmrb_insert, file_id - 1)
                    else:
                        prev_string = ''
                    if file_id < number_of_files:
                        next_string = '<a href="index%s_%s.html">> Next</a>' % (
                            bmrb_insert, file_id + 1)
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
                            links_string += ' <a href="index%s_%s.html">%s</a>' % (
                                bmrb_insert, link, link)
                            
                    old_string = r"<!-- INSERT NEW LINKS HERE -->"
                    new_string = 'Result page: %s %s %s' % (
                        prev_string, links_string, next_string)
                    new_file_content = string.replace(new_file_content, old_string, new_string)


                    ## Make the first index file name still index.html
                    
                    if file_id:
                        new_file_name = self.results_dir + '/index/index' + bmrb_insert + "_" + `file_id` + '.html'
                    else:
                        new_file_name = self.results_dir + '/index/index' + bmrb_insert + '.html'
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
            index_file_first = 'index%s_1.html' % bmrb_insert
            index_file = os.path.join(self.results_dir + "/index", 'index%s.html' % bmrb_insert)
            ## Assume that a link that is already present is valid and will do the job
            NTmessage('Symlinking (A): %s %s' % (index_file_first, index_file))
            symlink(index_file_first, index_file)
                 
        ## Make a sym link from the index_bmrb.html file to the index.html file
        #x = """
        if self.doWhiteArchive:
            index_file_first = 'index_pdb.html'
        else:
            index_file_first = 'index_bmrb.html'
        index_file_first = index_file_first
        index_file = os.path.join(self.results_dir + "/index", 'index.html')
        if self.verbose > 2:
            print 'Symlinking (B):', index_file_first, index_file
        symlink(index_file_first, index_file)
         
        NTmessage("Copy the adjusted php script")
        org_file = os.path.join(self.base_dir, 'redirect.php')
        new_file = os.path.join(self.results_dir, 'redirect.php')
        file_content = open(org_file, 'r').read()
        old_string = 'URL_BASE'
        file_content = string.replace(file_content, old_string, self.results_url)
        open(new_file, 'w').write(file_content)

        NTmessage("Copy the adjusted html redirect")
        org_file = os.path.join(self.base_dir, 'redirect.html')
        new_file = os.path.join(self.results_dir, 'index.html')
        file_content = open(org_file, 'r').read()
        old_string = 'URL_BASE'
        file_content = string.replace(file_content, old_string, self.results_url)
        open(new_file, 'w').write(file_content)

        NTmessage("Copy the molecule of the hour script")
        org_file = os.path.join(self.base_dir, 'moleculeOfTheHour.html')
        new_file = os.path.join(self.results_dir, 'moleculeOfTheHour.html')
        file_content = open(org_file, 'r').read()
        old_string = r"<!-- INSERT NEW COLOR SCHEME HERE -->"
        file_content = string.replace(file_content, old_string, color_scheme_text)
        old_string = r"<!-- INSERT NEW LOGO HERE -->"
        file_content = string.replace(file_content, old_string, logo_text)
        old_string = r"<!-- INSERT NEW DATE HERE -->"
        new_string = time.asctime()
        file_content = string.replace(file_content, old_string, new_string)        
        open(new_file, 'w').write(file_content)
        NTmessage("Copy the molecule of the hour html page")     
        org_file = os.path.join(self.base_dir, 'moleculeOfTheHour.py')
        new_file = os.path.join(self.results_dir, 'moleculeOfTheHour.py')
        shutil.copyfile(org_file, new_file)
        return 1
    
###############################################################################

## Always nice to have a main:

if __name__ == '__main__':
    # 13 seconds per entry.
    # 300 entries per hour.
    # 31,123 entries take almost 5 days.
    # WATCH OUT something makes molmol not always generate a pov file when multiple instances run
    # at the same time. It must be using a common temp file or so.
    verbosity = 9    # 0 gives no output and 9 is all; 2 is default
    max_entries_todo = 1    # was 500 (could be as many as u like)
    max_time_to_wait = 12000 # 1y4o took more than 600. This is one of the optional arguments.
    processors = 1    # was 1 may be set to a 100 when just running through to regenerate pickle                                       
    doUpdateAfterFileSystemReset = 0    # DEFAULT 0 use to update all the modification times to now in the pickle.
    new_hits_entry_list = [] # define empty for checking new ones.
    new_hits_entry_list = ['1brv']
#    new_hits_entry_list         = string.split("2jqv 2jnb 2jnv 2jvo 2jvr 2jy7 2jy8 2oq9 2osq 2osr 2otr 2rn9 2rnb")
    
    ## Initialize the project 
    m = nrgCing(verbose=verbosity,
                        max_entries_todo=max_entries_todo,
                        max_time_to_wait=max_time_to_wait
                    ) 

    if not m.get_bmrb_links():
        NTerror("can't get bmrb links")
        os._exit(1)
    
    ## Read old info if available
    m.pickle_read()

    ## START: FOR FAST RUN BLOCK THIS OUT
    ## Was the filesystem reset and all modification times off?
    if doUpdateAfterFileSystemReset:
        m.pickle_update_times_only()
        m.pickle_write()
        os._exit(0)
        
    ## Searches and matches
    if new_hits_entry_list:
        m.new_hits_entry_list = new_hits_entry_list
        NTmessage("Doing list of new entries: %s" % new_hits_entry_list)
    else:
        if not m.search_matching_entries():
            NTerror("can't search matching entries")
            os._exit(1)
    
        
    ## Make the individual and overall web pages including
    ## new versions of the scripts used.    
    m.do_analyses_loop(processes_max=processors)

    m.pickle_cleanup()
    ## END: FOR FAST RUN BLOCK THIS OUT

    if not m.update_index_files():
        NTerror(": can't update index files")

    ## Save changed pickle
    m.pickle_write()
