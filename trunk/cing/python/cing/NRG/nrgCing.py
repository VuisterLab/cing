"""
This script will use NRG files to generate the CING reports as well as the
indices that live on top of them. For weekly and for more mass updates.

Execute like:

python -u $CINGROOT/python/cing/NRG/nrgCing.py [entry_code] [updateWeekly prepare prepareEntry runCingEntry storeCING2db createToposTokens ]

As a cron job this will:
    - create a todo list
    - prepare/run entries todo
    - create new lists and write them to file.

Time taken by CING by statistics
Count                  5644
Average             880.767
Standard deviation  727.007
Minimum              28.148
Maximum            18593.635
Sum                4971048.908
"""

from cing import cingDirScripts
from cing import cingPythonCingDir
from cing import header
from cing.Libs.NTgenUtils import analyzeCingLog
from cing.Libs.NTgenUtils import analyzeFcLog
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.disk import globLast
from cing.Libs.disk import mkdirs
from cing.Libs.disk import rmdir
from cing.Libs.helper import detectCPUs
from cing.Libs.html import GOOGLE_ANALYTICS_TEMPLATE
from cing.NRG import ARCHIVE_NRG_ID
from cing.NRG.PDBEntryLists import * #@UnusedWildImport
from cing.NRG.WhyNot import * #@UnusedWildImport
from cing.NRG.nrgCingRdb import nrgCingRdb
from cing.NRG.settings import * #@UnusedWildImport
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList
from cing.Scripts.vCing.vCing import VALIDATE_ENTRY_NRG_STR
from cing.Scripts.vCing.vCing import vCing
from cing.Scripts.validateEntry import ARCHIVE_TYPE_BY_CH23
from cing.Scripts.validateEntry import PROJECT_TYPE_CCPN
from cing.main import getStartMessage
from cing.main import getStopMessage
from shutil import copyfile
from shutil import rmtree
import commands
import csv
import shutil
import string

PHASE_C = 'C'
PHASE_R = 'R'
PHASE_S = 'S'
PHASE_F = 'F'

LOG_NRG_CING = 'log_nrgCing'
LOG_STORE_CING2DB = 'log_storeCING2db'
#DATA_STR = 'log_nrgCing'

class nrgCing(Lister):
    """Main class for preparing and running CING reports on NRG and maintaining the statistics."""
    def __init__(self,
                 new_hits_entry_list=None,
                 useTopos=False,
                 getTodoList=True,
                 max_entries_todo=1,
                 max_time_to_wait=86400, # one day. 2p80 took the longest: 5.2 hours. But <Molecule "2ku1" (C:7,R:1659,A:36876,M:30)> is taking longer
                 processes_max=None,
                 prepareInput=False,
                 writeWhyNot=True,
                 writeTheManyFiles=False,
                 updateIndices=True,
                 isProduction=True
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
        self.D = '/Library/WebServer/Documents'
        self.results_dir = os.path.join(self.D, self.results_base)
        self.data_dir = os.path.join(self.results_dir, DATA_STR)
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
        self.processes_max = detectCPUs()
        if processes_max:
            self.processes_max = processes_max
#        self.processes_max = 2 # DEFAULT: commented out.

        ## How long to wait between submitting individual jobs when on the cluster.
        ##self.delay_between_submitting_jobs = 5
        self.delay_between_submitting_jobs = 5
        ## Total number of child processes to be done if all scheduled to be done
        ## are indeed to be done. This is set later on and perhaps adjusted
        ## when the user interrupts the process by ctrl-c.
        self.url_directer = self.results_url + '/direct.php'
        self.url_redirecter = self.results_url + '/redirect.php'
#        self.url_csv_file_link_base = 'http://www.bmrb.wisc.edu/servlet_data/viavia/bmrb_pdb_match'
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

        os.chdir(self.results_dir)

        ## List of 'new' entries for which hits were found
        self.new_hits_entry_list = NTlist()
        if new_hits_entry_list:
            self.new_hits_entry_list = new_hits_entry_list
        self.useTopos = useTopos
        self.getTodoList = getTodoList
        self.entry_list_pdb = NTlist()
        self.entry_list_nmr = NTlist()
        self.entry_list_nmr_exp = NTlist()
        self.entry_list_nrg = NTlist()          # should be the same as self.entry_list_nmr_exp
        self.entry_list_nrg_docr = NTlist()

        # Stages are cumulative in that e.g. R always includes all from C. This simplifies this setup hopefully.
                      # id #name         #code

        self.phaseIdList = [PHASE_C, PHASE_R, PHASE_S, PHASE_F]
        self.phaseDataList = [
                     [ 'Coordinate', 'C'],
                     [ 'Restraint', 'R'],
                     [ 'Shift', 'S'],
                     [ 'Filter', 'F'],
                      ]
        self.recoordSyncDir = 'recoordSync'
        self.inputDir = 'input'
#        self.entry_list_prep_stage_C = NTlist()   # NMR entries prepared from mmCIF coordinates (NRG-DOCR entries will overrule these any time).
#        self.entry_list_prep_stage_R = NTlist()   # Should include entry_list_nrg_docr if all came over from NRG-DOCR.
#        self.entry_list_prep_stage_S = NTlist()   # Adds chemical shifts if available.
#        self.entry_list_prep_stage_F = NTlist()   # Might be filtered otherwise simply stage S.
#        self.phaseList = [self.entry_list_prep_stage_C, self.entry_list_prep_stage_R, self.entry_list_prep_stage_S, self.entry_list_prep_stage_F]

        # From disk.
        self.entry_list_prep_tried = NTlist()
        self.entry_list_prep_crashed = NTlist()
        self.entry_list_prep_failed = NTlist()
        self.entry_list_prep_done = NTlist()

        self.entry_list_store_tried = NTlist()
        self.entry_list_store_crashed = NTlist()
        self.entry_list_store_failed = NTlist()
        self.entry_list_store_not_in_db = NTlist()
        self.entry_list_store_done = NTlist()

        self.entry_list_tried = NTlist()      # .cing directory and .log file present so it was tried to start but might not have finished
        self.entry_list_crashed = NTlist()    # has a stack trace
        self.entry_list_stopped = NTlist()    # was stopped by time out or by user or by system (any other type of stop but stack trace)
        self.entry_list_done = NTlist()       # finished to completion of the cing run.
        self.entry_list_todo = NTlist()
        self.entry_list_updated = NTlist()
        self.timeTakenDict = NTdict()
        self.inputModifiedDict = NTdict()     # This is the most recent of mmCIF, NRG, BMRB CS.
        self.entry_list_obsolete = NTlist()
        self.ENTRY_DELETED_COUNT_MAX = 2
        self.MAX_ERROR_COUNT_CING_LOG = 200
        self.MAX_ERROR_COUNT_FC_LOG = 99999 # 104d had 16. 108d had 460
        self.wattosVerbosity = cing.verbosity
        self.wattosMemory = '4g'
        if not self.isProduction:
            self.wattosMemory = '2g' # development machine Stella only has 4g total and this is only important for largest entries like 2ku2
        self.wattosProg = "java -Djava.awt.headless=true -Xmx%s Wattos.CloneWars.UserInterface -at -verbosity %s" % (self.wattosMemory, self.wattosVerbosity)
        self.tokenListFileName = os.path.join(self.results_dir, 'token_list_todo.txt')
        self.vc = None

    def initVc(self):
        NTmessage("Setting up vCing")
        self.vc = vCing(max_time_to_wait_per_job=self.max_time_to_wait)
        NTmessage("Starting with %r" % self.vc)

    def updateWeekly(self):
        self.writeWhyNot = True     # DEFAULT: True.
        self.updateIndices = True   # DEFAULT: True.
        self.getTodoList = True     # DEFAULT: True. If and only if new_hits_entry_list is empty and getTodoList is False; no entries will be attempted.

        self.new_hits_entry_list = [] # DEFAULT: [].define empty for checking new ones.
    #    self.new_hits_entry_list = ['1brv']
    #    self.new_hits_entry_list         = string.split("2jqv 2jnb 2jnv 2jvo 2jvr 2jy7 2jy8 2oq9 2osq 2osr 2otr 2rn9 2rnb")

        if False: # DEFAULT False; use for processing a specific batch.
            entryListFileName = os.path.join(self.results_dir, 'entry_list_todo_all.csv')
            self.new_hits_entry_list = readLinesFromFile(entryListFileName)
            self.new_hits_entry_list = self.new_hits_entry_list[100:110]

        NTmessage("In updateWeekly starting with:\n%r" % self)

        # Retrieve the linkages between BMRB and PDB entries.
        self.matches_many2one = getBmrbLinks()
        if not self.matches_many2one:
            NTerror("Failed to get BMRB-PDB links")
            return True

        # Get the PDB info to see which entries can/should be done.
        if self.searchPdbEntries():
            NTerror("Failed to searchPdbEntries")
            return True

        if self.new_hits_entry_list:
            self.entry_list_todo.addList(self.new_hits_entry_list)
        elif self.getTodoList:
            # Get todo list and some others.
            if self.getEntryInfo():
                NTerror("Failed to getEntryInfo (first time).")
                return True

        if self.entry_list_todo and self.max_entries_todo:
            if self.prepare():
                NTerror("Failed to prepare")
                return True
            if self.getEntryInfo(): # needed to see which preps failed; they are then excluded from todo list.
                NTerror("Failed to getEntryInfo (second time in updateWeekly).")
                return True
            self.entry_list_todo.difference( self.entry_list_prep_crashed )
            self.entry_list_todo.difference( self.entry_list_prep_failed )
            if self.runCing():
                NTerror("Failed to runCing")
                return True
            # Do or redo the retrieval of the info from the filesystem on the doneness of NRG-CING.
            if self.getEntryInfo():
                NTerror("Failed to getEntryInfo")
                return True

        if self.doWriteEntryLoL():
            NTerror("Failed to doWriteEntryLoL")
            return True

        if self.doWriteWhyNot():
            NTerror("Failed to doWriteWhyNot")
            return True

        if self.updateIndexFiles():
            NTerror("Failed to update index files.")
            return True
    # end def run

    def addInputModificationTimesFromMmCif(self):
        NTmessage("Looking at mmCIF input file modification times.")
        for entryId in self.entry_list_nmr:
            entryCodeChar2and3 = entryId[1:3]
            fileName = os.path.join(CIFZ2, entryCodeChar2and3, '%s.cif.gz' % entryId)
#            NTdebug("Looking at: " + fileName)
            if not os.path.exists(fileName):
                if self.isProduction:
                    NTmessage("Failed to find: " + fileName)
                continue
            self.inputModifiedDict[ entryId ] = os.path.getmtime(fileName)
        # end for
    # end def

    def addInputModificationTimesFromNrg(self):
        NTmessage("Looking at NRG input file modification times.")
        for entryId in self.entry_list_nrg_docr:
            inputDir = os.path.join(self.results_dir, self.recoordSyncDir)
            fileName = os.path.join(inputDir, entryId, '%s.tgz' % entryId)
            if not os.path.exists(fileName):
                if self.isProduction:
                    NTdebug("Failed to find: " + fileName)
                continue
            nrgMod = os.path.getmtime(fileName)
#            NTdebug("For %s found: %s" % ( fileName, nrgMod))
            prevMod = getDeepByKeysOrAttributes(self.inputModifiedDict, entryId)

            if prevMod:
               if nrgMod > prevMod:
                   self.inputModifiedDict[ entryId ] = nrgMod # nrg more recent
               else:
                   pass
            else:
               self.inputModifiedDict[ entryId ] = nrgMod # nrg more recent
               if self.isProduction:
                   NTwarning("Found no mmCIF file for %s" % entryId)
            # end else
        # end for
    # end def

    def getInputModificationTimes(self):
        if self.addInputModificationTimesFromMmCif():
            NTerror("Failed to addInputModificationTimesFromMmCif aborting")
            return True
        if self.addInputModificationTimesFromNrg():
            NTerror("Failed to addInputModificationTimesFromNrg aborting")
            return True
#        self.addInputModificationTimesFromBmrb() # TODO:


    def getEntryInfo(self):
        """Returns True for error.

        This routine sets self.entry_list_todo

        Will remove entry directories if they do not occur in NRG up to a maximum number as not to whip out
        every one in a single blow by accident.

        If an entry has restraint data but is not in DOCR, it will be done from mmCIF until it does occur in DOCR.
        """

        NTmessage("Get the entries tried, todo, crashed, and stopped in NRG-CING from file system.")


        self.entry_list_prep_tried = NTlist()
        self.entry_list_prep_crashed = NTlist()
        self.entry_list_prep_failed = NTlist()
        self.entry_list_prep_done = NTlist()

        self.entry_list_store_tried = NTlist()
        self.entry_list_store_crashed = NTlist()
        self.entry_list_store_failed = NTlist()
        self.entry_list_store_not_in_db = NTlist()
        self.entry_list_store_done = NTlist()

        self.entry_list_obsolete = NTlist()
        self.entry_list_tried = NTlist()
        self.entry_list_crashed = NTlist()
        self.entry_list_stopped = NTlist() # mutely exclusive from entry_list_crashed
        self.entry_list_done = NTlist()
        self.entry_list_todo = NTlist()
        self.entry_list_updated = NTlist()

        if self.getInputModificationTimes():
            NTerror("Failed to getInputModificationTimes aborting")
            return True

        # TODO: loop this over different prep stages.
        NTmessage("Scanning the prep logs.")
        for entry_code in self.entry_list_nmr:
            entryCodeChar2and3 = entry_code[1:3]
            logDir = os.path.join(self.results_dir, DATA_STR, entryCodeChar2and3, entry_code, LOG_NRG_CING )
#            NTdebug("Looking in log dir: %s" % logDir)
            logLastFile = globLast(logDir + '/*.log')
#            NTdebug("logLastFile: %s" % logLastFile)
            if not logLastFile:
                if self.isProduction and 0: # DEFAULT: 1 when assumed all are done.
                    NTmessage("Failed to find any prep log file in directory: %s" % logDir)
                continue
            self.entry_list_prep_tried.append(entry_code)
            analysisResultTuple = analyzeCingLog(logLastFile)
            if not analysisResultTuple:
                NTmessage("Failed to analyze log file: %s" % logLastFile)
                self.entry_list_prep_crashed.append(entry_code)
                continue
            timeTaken, entryCrashed, nr_error, nr_warning, nr_message, nr_debug = analysisResultTuple
            if entryCrashed:
                NTmessage("Detected a crash: %s" % entry_code, logLastFile)
                self.entry_list_prep_crashed.append(entry_code)
                continue # don't mark it as stopped anymore.
            # end if
            if not timeTaken:
                NTmessage("Unexpected [%s] for time taken in CING prep log file: %s assumed crashed." % (timeTaken, logLastFile))
                self.entry_list_prep_crashed.append(entry_code)
                continue # don't mark it as stopped anymore.
            # end if
            if nr_error > 0:
                self.entry_list_prep_failed.append(entry_code)
                NTmessage("Found %s/%s timeTaken/entryCrashed and %d/%d/%d/%d error,warning,message, and debug lines." % (timeTaken, entryCrashed, nr_error, nr_warning, nr_message, nr_debug) )
                NTmessage("%s Found %s errors in prep phase X please check: %s" % (entry_code, nr_error, logLastFile))
                continue
            # end if
            self.entry_list_prep_done.append(entry_code)
        # end for

        NTmessage("Starting to scan CING report/log.")
        subDirList = os.listdir(DATA_STR)
        for subDir in subDirList:
            if len(subDir) != 2:
                if subDir != DS_STORE_STR:
                    NTdebug('Skipping subdir with other than 2 chars: [' + subDir + ']')
                continue
            entryList = os.listdir(os.path.join(DATA_STR, subDir))
            for entryDir in entryList:
                entry_code = entryDir
                if not is_pdb_code(entry_code):
                    if entry_code != DS_STORE_STR:
                        NTerror("String doesn't look like a pdb code: " + entry_code)
                    continue
#                NTdebug("Working on: " + entry_code)

                entrySubDir = os.path.join(DATA_STR, subDir, entry_code)
                if not entry_code in self.entry_list_nmr:
                    NTwarning("Found entry %s in NRG-CING but not in PDB-NMR. Will be obsoleted in NRG-CING too" % entry_code)
                    if len(self.entry_list_obsolete) < self.ENTRY_DELETED_COUNT_MAX:
                        rmdir(entrySubDir)
                        self.entry_list_obsolete.append(entry_code)
                    else:
                        NTerror("Entry %s in NRG-CING not obsoleted since there were already removed: %s entries." % (
                            entry_code, self.ENTRY_DELETED_COUNT_MAX))
                # end if

                cingDirEntry = os.path.join(entrySubDir, entry_code + ".cing")
                if not os.path.exists(cingDirEntry):
#                    NTdebug("Skipping entry because no(t yet a) directory: %s" % cingDirEntry)
                    continue

                # Look for last log file
                logLastFile = globLast(entrySubDir + '/log_validateEntry/*.log')
                if not logLastFile:
                    NTmessage("Failed to find any log file in directory: %s" % entrySubDir)
                    continue
                # .cing directory and .log file present so it was tried to start but might not have finished
                self.entry_list_tried.append(entry_code)
                entryCrashed = False
                timeTaken, entryCrashed, nr_error, nr_warning, nr_message, nr_debug = analyzeCingLog(logLastFile)
                if entryCrashed:
                    self.entry_list_crashed.append(entry_code)
                    continue # don't mark it as stopped anymore.
                # end if
                if nr_error > self.MAX_ERROR_COUNT_CING_LOG:
                    NTmessage("Found %s/%s timeTaken/entryCrashed and %d/%d/%d/%d error,warning,message, and debug lines." % (timeTaken, entryCrashed, nr_error, nr_warning, nr_message, nr_debug) )
                    NTmessage("Found %s which is over %s please check: %s" % (nr_error, self.MAX_ERROR_COUNT_CING_LOG, entry_code))

                if timeTaken:
                    self.timeTakenDict[entry_code] = timeTaken
                else:
                    NTmessage("Unexpected [%s] for time taken in CING log for file: %s" % (timeTaken, logLastFile))

                timeStampLastValidation = getTimeStampFromFileName(logLastFile)
                if not timeStampLastValidation:
                    NTdebug("Failed to retrieve timeStampLastValidation from %s" % logLastFile)
                timeStampLastInputMod = getDeepByKeysOrAttributes(self.inputModifiedDict, entry_code)
                # If the input has been updated then the entry should be redone so don't add it to the done list.
                if timeStampLastValidation and timeStampLastInputMod:
#                    NTdebug("Comparing input to validation time stamps: %s to %s" % (timeStampLastInputMod, timeStampLastValidation))
                    if timeStampLastValidation < timeStampLastInputMod:
                        self.entry_list_updated.append(entry_code)
                        continue
                else:
                    NTdebug("Dates for last validation of last input modification not both retrieved for %s." % entry_code)
                # end if

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

                if isProduction: # DEFAULT: True but disabled for testing.
                    molGifFile = os.path.join(cingDirEntry, entry_code, "HTML/mol.gif")
                    if not os.path.exists(molGifFile):
                        NTmessage("%s Since mol.gif file %s was not found assumed to have stopped" % (entry_code, projectHtmlFile))
                        self.entry_list_stopped.append(entry_code)
                        continue

                self.entry_list_done.append(entry_code)
            # end for entryDir
        # end for subDir

        if self.isProduction:
            host = 'nmr'
        else:
            host = 'localhost'
        m = nrgCingRdb(host=host)
        self.entry_list_store_in_db = m.getPdbIdList()
        if not self.entry_list_store_in_db:
            NTerror("Failed to get any entry from NRG-CING RDB")
            self.entry_list_store_in_db = NTlist()
        entry_dict_store_in_db = list2dict(self.entry_list_store_in_db)

        NTmessage("Scanning the store logs of entries done.")
        for entry_code in self.entry_list_done:
            entryCodeChar2and3 = entry_code[1:3]
            logDir = os.path.join(self.results_dir, DATA_STR, entryCodeChar2and3, entry_code, LOG_STORE_CING2DB )
            logLastFile = globLast(logDir + '/*.log')#            NTdebug("logLastFile: %s" % logLastFile)
            if not logLastFile:
                if self.isProduction and 0: # DEFAULT: 1 when assumed all are done.
                    NTmessage("Failed to find any store log file in directory: %s" % logDir)
                continue
            self.entry_list_store_tried.append(entry_code)
            analysisResultTuple = analyzeCingLog(logLastFile)
            if not analysisResultTuple:
                NTmessage("Failed to analyze log file: %s" % logLastFile)
                self.entry_list_store_crashed.append(entry_code)
                continue
            timeTaken, entryCrashed, nr_error, nr_warning, nr_message, nr_debug = analysisResultTuple
            if entryCrashed:
                NTmessage("For CING store log file: %s assumed crashed." % (timeTaken, logLastFile))
                self.entry_list_store_crashed.append(entry_code)
                continue # don't mark it as stopped anymore.
            # end if
            if not entry_dict_store_in_db.has_key(entry_code):
                NTmessage("Failed to find [%s] in db." % entry_code)
                self.entry_list_store_not_in_db.append(entry_code)
                continue # don't mark it as stopped anymore.
            # end if
            if nr_error > self.MAX_ERROR_COUNT_CING_LOG:
                self.entry_list_store_failed.append(entry_code)
                NTmessage("Found %s/%s timeTaken/entryCrashed and %d/%d/%d/%d error,warning,message, and debug lines." % (timeTaken, entryCrashed, nr_error, nr_warning, nr_message, nr_debug) )
                NTmessage("%s Found %s errors in storing please check: %s" % (entry_code, nr_error, logLastFile))
                continue
            # end if
            self.entry_list_store_done.append(entry_code)
        # end for

        # Consider the entries updated as not done.
        self.entry_list_done.difference(self.entry_list_updated)
        # Consider the entries updated as not done.

        timeTakenList = NTlist() # local variable.
        timeTakenList.addList(self.timeTakenDict.values())
        NTmessage("Time taken by CING by statistics\n%s" % timeTakenList.statsFloat())

        if not self.entry_list_tried:
            NTerror("Failed to find entries that CING tried.")

        self.entry_list_todo.addList(self.entry_list_nmr)
        self.entry_list_todo = self.entry_list_todo.difference(self.entry_list_done)

        NTmessage("Found %4d entries by NMR (A)." % len(self.entry_list_nmr))

        NTmessage("Found %4d entries that CING prep tried." % len(self.entry_list_prep_tried))
        NTmessage("Found %4d entries that CING prep crashed." % len(self.entry_list_prep_crashed))
        NTmessage("Found %4d entries that CING prep failed." % len(self.entry_list_prep_failed))
        NTmessage("Found %4d entries that CING prep done." % len(self.entry_list_prep_done))

        NTmessage("Found %4d entries that CING tried (T)." % len(self.entry_list_tried))
        NTmessage("Found %4d entries that CING crashed (C)." % len(self.entry_list_crashed))
        NTmessage("Found %4d entries that CING stopped (S)." % len(self.entry_list_stopped))
        NTmessage("Found %4d entries that CING should update (U)." % len(self.entry_list_updated))
        NTmessage("Found %4d entries that CING did (B=A-C-S-U)." % len(self.entry_list_done))
        NTmessage("Found %4d entries todo (A-B)." % len(self.entry_list_todo))
        NTmessage("Found %4d entries in NRG-CING made obsolete." % len(self.entry_list_obsolete))

        NTmessage("Found %4d entries that CING store tried." % len(self.entry_list_store_tried))
        NTmessage("Found %4d entries that CING store crashed." % len(self.entry_list_store_crashed))
        NTmessage("Found %4d entries that CING store failed." % len(self.entry_list_store_failed))
        NTmessage("Found %4d entries that CING store not in db." % len(self.entry_list_store_not_in_db))
        NTmessage("Found %4d entries that CING store done." % len(self.entry_list_store_done))


        if not self.entry_list_done:
            NTwarning("Failed to find entries that CING did.")

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

#        NTmessage("Looking for entries in the different preparation stages.")
#        for i, phaseData in enumerate(self.phaseDataList):
#            entryList = self.phaseList[i]
#            phaseName, _phaseId = phaseData
#            l = len(entryList)
#            NTmessage("Found %d entries in prep stage %s" % (l, phaseName))

        ## following statement is equivalent to a unix command like:
        NTmessage("Looking for entries from the PDB and NRG databases.")
        if True: # DEFAULT ON Use switch to debug.
            self.entry_list_pdb.addList(getPdbEntries())
            if not self.entry_list_pdb:
                NTerror("No PDB entries found")
                return True
            self.entry_list_nmr.addList(getPdbEntries(onlyNmr=True))
            if not self.entry_list_nmr:
                NTerror("No NMR entries found")
                return True
        else:
            self.entry_list_pdb += '1crn 1bus 1brv 1a4d'.split()
            self.entry_list_nmr += '1bus 1brv'.split()
            self.entry_list_nrg_docr += '1brv'.split()


        NTmessage("Found %5d PDB entries." % len(self.entry_list_pdb))
        NTmessage("Found %5d NMR entries." % len(self.entry_list_nmr))

        self.entry_list_nmr_exp.addList(getPdbEntries(onlyNmr=True, mustHaveExperimentalNmrData=True))
        if not self.entry_list_nmr_exp:
            NTerror("No NMR with experimental data entries found")
            return True
        NTmessage("Found %5d NMR with experimental data entries." % len(self.entry_list_nmr_exp))

        self.entry_list_nrg.addList(getBmrbNmrGridEntries())
        if not self.entry_list_nrg:
            NTerror("No NRG entries found")
            return True
        NTmessage("Found %5d PDB entries in NRG." % len(self.entry_list_nrg))

        if 1: # DEFAULT 1
            ## The list of all entry_codes for which tgz files have been found
            self.entry_list_nrg_docr.addList(getBmrbNmrGridEntriesDOCRDone())
            if not self.entry_list_nrg_docr:
                NTerror("No NRG DOCR entries found")
                return True
            if len(self.entry_list_nrg_docr) < 3000:
                NTerror("watch out less than 3000 entries found [%s] which is suspect; quitting" % len(self.entry_list_nrg_docr))
                return True
        NTmessage("Found %5d NRG DOCR entries. (A)" % len(self.entry_list_nrg_docr))




    def doWriteEntryLoL(self):
        """Write the entry list of each list to file"""
        writeTextToFile("entry_list_pdb.csv", toCsv(self.entry_list_pdb))
        writeTextToFile("entry_list_nmr.csv", toCsv(self.entry_list_nmr))
        writeTextToFile("entry_list_nmr_exp.csv", toCsv(self.entry_list_nmr_exp))
        writeTextToFile("entry_list_nrg.csv", toCsv(self.entry_list_nrg))
        writeTextToFile("entry_list_nrg_docr.csv", toCsv(self.entry_list_nrg_docr))


        writeTextToFile("entry_list_prep_tried.csv", toCsv(self.entry_list_prep_tried))
        writeTextToFile("entry_list_prep_crashed.csv", toCsv(self.entry_list_prep_crashed))
        writeTextToFile("entry_list_prep_failed.csv", toCsv(self.entry_list_prep_failed))
        writeTextToFile("entry_list_prep_done.csv", toCsv(self.entry_list_prep_done))

        writeTextToFile("entry_list_tried.csv", toCsv(self.entry_list_tried))
        writeTextToFile("entry_list_done.csv", toCsv(self.entry_list_done))
        writeTextToFile("entry_list_todo.csv", toCsv(self.entry_list_todo))
        writeTextToFile("entry_list_crashed.csv", toCsv(self.entry_list_crashed))
        writeTextToFile("entry_list_stopped.csv", toCsv(self.entry_list_stopped))
        writeTextToFile("entry_list_timing.csv", toCsv(self.timeTakenDict))
        writeTextToFile("entry_list_updated.csv", toCsv(self.entry_list_updated))
        writeTextToFile("entry_list_obsolete.csv", toCsv(self.entry_list_obsolete))

        writeTextToFile("entry_list_store_tried.csv", toCsv(self.entry_list_store_tried))
        writeTextToFile("entry_list_store_crashed.csv", toCsv(self.entry_list_store_crashed))
        writeTextToFile("entry_list_store_failed.csv", toCsv(self.entry_list_store_failed))
        writeTextToFile("entry_list_store_not_in_db.csv", toCsv(self.entry_list_store_not_in_db))
        writeTextToFile("entry_list_store_done.csv", toCsv(self.entry_list_store_done))

#        for i, phaseData in enumerate(self.phaseDataList):
#            entryList = self.phaseList[i]
#            _phaseName, phaseId = phaseData
#            fn = 'entry_list_prep_stage_%s.csv' % phaseId
#            writeTextToFile(fn, toCsv(entryList))




    def doWriteWhyNot(self):
        "Write the WHYNOT files"
        if self.writeWhyNot:
            NTmessage("Create WHY_NOT list")
        else:
            NTmessage("Skipping create WHY_NOT list")
            return

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
#        NTdebug("Copying to: " + why_not_db_comments_file)
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
        """Updating the index files based on self.entry_list_done
        Run other steps first.
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
                bmrb_entry_code = ""
                if self.matches_many2one.has_key(pdb_entry_code):
                    bmrb_entry_code = self.matches_many2one[pdb_entry_code]
#                    bmrb_entry_code = bmrb_entry_code

            ## Finish this index file
            ## The last index file will only be written once...
            if entries_done_per_file == number_of_entries_per_file or \
                    entries_done_all == number_of_entries_all_present:

                begin_entry_count = number_of_entries_per_file * (file_id - 1) + 1
                end_entry_count = min(number_of_entries_per_file * file_id,
                                           number_of_entries_all_present)
#                NTdebug("%5d %5d %5d" % (begin_entry_count, end_entry_count, number_of_entries_all_present))

                old_string = r"<!-- INSERT NEW RESULT STRING HERE -->"
                jump_form_start = '<FORM method="GET" action="%s">' % self.url_directer
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

        fileListToCopy = [ 'direct.php', 'redirect.php', 'pdb.php']
        NTmessage("Copy the php scripts: %s" % fileListToCopy)
        for fileNameToCopy in fileListToCopy:
            org_file = os.path.join(self.base_dir, DATA_STR, fileNameToCopy)
            shutil.copy(org_file, self.results_dir)

        NTmessage("Copy the overall index")
        org_file = os.path.join(self.base_dir, DATA_STR, 'redirect.html')
        new_file = os.path.join(self.results_dir, 'index.html')
        shutil.copy(org_file, new_file)

        fileListToCopy = [ 'cing.css', 'header_bg.jpg', ]
        NTmessage("Copy the html files: %s" % fileListToCopy)
        for fileNameToCopy in fileListToCopy:
            org_file = os.path.join(htmlDir, fileNameToCopy)
            shutil.copy(org_file, indexDir)
    # end def

    def postProcessEntryAfterVc(self, entry_code):
        """
        Unzips the tgz.
        Copies the log
        Removes both tgz & log.

        Returns True on error.
        """
        NTmessage("Doing postProcessEntryAfterVc on  %s" % entry_code)

        doRemoves = 1 # DEFAULT 1 disable for testing.
        doLog = 1 # DEFAULT 1 disable for testing.
        doTgz = 1 # DEFAULT 1 disable for testing.

        entryCodeChar2and3 = entry_code[1:3]
        entryDir = os.path.join(self.data_dir , entryCodeChar2and3, entry_code)
        if not os.path.exists(entryDir):
            NTerror("Skipping %s because dir %s was not found." % (entry_code, entryDir))
            return True
        os.chdir(entryDir)

        if doLog:
            if not self.vc:
                self.initVc()
            master_target_log_dir = os.path.join(self.vc.MASTER_TARGET_DIR, self.vc.MASTER_TARGET_LOG)
            if not os.path.exists(master_target_log_dir):
                NTerror("Skipping %s because failed to find master_target_log_dir: %s" % (entry_code, master_target_log_dir))
                return True
            logScriptFileNameRoot = 'validateEntryNrg'
            logFilePattern = '/*%s_%s_*.log' % (logScriptFileNameRoot, entry_code)
            logLastFile = globLast(master_target_log_dir + logFilePattern)
            if not logLastFile:
                NTerror("Skipping %s because failed to find last log file in directory: %s by pattern %s" % (entry_code, master_target_log_dir, logFilePattern))
                return True

            date_stamp = getDateTimeStampForFileName(logLastFile)
            if not date_stamp:
                NTerror("Skipping %s because failed to find date for log file: %s" % (entry_code, logLastFile))
                return True

            logScriptFileNameRootNew = 'validateEntry' # stick them in next to the locally derived logs.
            newLogDir = 'log_' + logScriptFileNameRootNew
            if not os.path.exists(newLogDir):
                os.mkdir(newLogDir)
            logLastFileNew = '%s_%s.log' % (entry_code, date_stamp)
            logLastFileNewFull = os.path.join(newLogDir, logLastFileNew)
            NTdebug("Copy from %s to %s" % (logLastFile, logLastFileNewFull))
            copyfile(logLastFile, logLastFileNewFull)
            if doRemoves:
                os.remove(logLastFile)
        # end if doLog

        if doTgz:
            tgzFileNameCing = entry_code + ".cing.tgz"
            if not os.path.exists(tgzFileNameCing):
                NTerror("Skipping %s because tgz %s not found in: %s" % (entry_code, tgzFileNameCing, os.getcwd()))
                return True
            cmd = "tar -xzf %s" % tgzFileNameCing
            NTdebug("cmd: %s" % cmd)
            status, result = commands.getstatusoutput(cmd)
            if status:
                NTerror("Failed to untar status: %s with result %s" % (status, result))
                return True
            if doRemoves:
                os.remove(tgzFileNameCing)
            # end if
        # end if doTgz
    # end def

    def prepareEntry(self, entry_code,
                     doInteractive=0,
                     convertMmCifCoor=1,
                     convertMrRestraints=0,
                     convertStarCS=0,
                     filterCcpnAll=0):
        "Return True on error."

        entryCodeChar2and3 = entry_code[1:3]
        copyToInputDir = 1 # DEFAULT: 1
        finalPhaseId = None # id to use for final move to input dir.
        # Absolute paths with still be appending a entryCodeChar2and3
        inputDirByPhase = {
                           PHASE_C: os.path.join(dir_C, entryCodeChar2and3, entry_code),
                           PHASE_R: os.path.join(self.recoordSyncDir, entry_code)
                           }

        NTmessage("interactive            interactive run is fast use zero for production                              %s" % doInteractive)
        NTmessage("convertMmCifCoor       Converts PDB mmCIF to NMR-STAR with Wattos        -> C/XXXX_C_FC.xml         %s" % convertMmCifCoor)
        NTmessage("convertMrRestraints    Adds STAR restraints to Ccpn with XXXX            -> R/XXXX_R_FC.xml         %s" % convertMrRestraints)
        NTmessage("convertStarCS          Adds STAR CS to Ccpn with XXXX                    -> S/XXXX_S_FC.xml         %s" % convertStarCS)
        NTmessage("filterCcpnAll          Filter CS and restraints with XXXX                -> F/XXXX_F_FC.xml         %s" % filterCcpnAll)
        NTmessage("Doing                                                                                            %4s" % entry_code)
#        NTdebug("copyToInputDir          Copies the input to the collecting directory                                 %s" % copyToInputDir)


        if convertMmCifCoor == convertMrRestraints:
            NTerror("One and one only needs to be True of convertMmCifCoor == convertMrRestraints")
            return True

        if convertMmCifCoor:
            NTmessage("  mmCIF")
#            convertStarCoor = 0 # DEFAULT 1: TODO: code.

            C_sub_entry_dir = os.path.join(dir_C, entryCodeChar2and3)
            C_entry_dir = os.path.join(C_sub_entry_dir, entry_code)

            script_file = '%s/ReadMmCifWriteNmrStar.wcf' % wcf_dir
            inputMmCifFile = os.path.join(CIFZ2, entryCodeChar2and3, '%s.cif.gz' % entry_code)
            outputStarFile = "%s_C_Wattos.str" % entry_code
            script_file_new = "%s.wcf" % entry_code
            log_file = "%s.log" % entry_code

            if not os.path.exists(C_entry_dir):
                mkdirs(dir_C)
            if not os.path.exists(C_sub_entry_dir):
                mkdirs(C_sub_entry_dir)
            os.chdir(C_sub_entry_dir)
            if os.path.exists(entry_code):
                if 1: # DEFAULT: 1
                    rmtree(entry_code)
                # end if False
            # end if
            if not os.path.exists(entry_code):
                os.mkdir(entry_code)
            os.chdir(entry_code)

            if not os.path.exists(inputMmCifFile):
                NTerror("%s No input mmCIF file: %s" % (entry_code, inputMmCifFile))
                return True

            maxModels = '999'
            if doInteractive:
                maxModels = '1'

            script_str = readTextFromFile(script_file)
            script_str = script_str.replace('WATTOS_VERBOSITY', str(self.wattosVerbosity))
            script_str = script_str.replace('INPUT_MMCIF_FILE', inputMmCifFile)
            script_str = script_str.replace('MAX_MODELS', maxModels)
            script_str = script_str.replace('OUTPUT_STAR_FILE', outputStarFile)

            writeTextToFile(script_file_new, script_str)
            wattosProgram = ExecuteProgram(self.wattosProg, #rootPath = wattosDir,
                                     redirectOutputToFile=log_file,
                                     redirectInputFromFile=script_file_new)
            now = time.time()
            wattosExitCode = wattosProgram()
            difTime = time.time() - now
            NTmessage("Wattos reading the mmCIF took %8.1f seconds" % difTime)
            if wattosExitCode:
                NTerror("%s Failed wattos script %s with exit code: %s" % (entry_code, script_file_new, str(wattosExitCode)))
                return True

            resultList =[]
            status = grep(log_file, 'ERROR', resultList=resultList, doQuiet=True)
            if status == 0:
                NTerror("%s found %s errors in Wattos log file; aborting." % ( entry_code, len(resultList)))
                NTerror('\n' +'\n'.join(resultList))
                return True
            os.unlink(script_file_new)
            if not os.path.exists(outputStarFile):
                NTerror("%s found no output star file %s" % (entry_code, outputStarFile))
                return True
            # end if


            NTmessage("  star2Ccpn")
            log_file = "%s_star2Ccpn.log" % entry_code
            inputStarFile = "%s_C_wattos.str" % entry_code
            inputStarFileFull = os.path.join(C_entry_dir, inputStarFile)
            fcScript = os.path.join(cingDirScripts, 'FC', 'convertStar2Ccpn.py')

            if not os.path.exists(inputStarFileFull):
                NTerror("%s previous step produced no star file." % entry_code)
                return True

            # Will save a copy to disk as well.
            convertProgram = ExecuteProgram("python -u %s" % fcScript, redirectOutputToFile=log_file)
            NTmessage("==> Running Wim Vranken's FormatConverter from script %s" % fcScript)
            exitCode = convertProgram("%s %s %s" % (inputStarFile, entry_code, C_entry_dir))
            if exitCode:
                NTerror("Failed convertProgram with exit code: %s" % str(exitCode))
                return True
            analysisResultTuple = analyzeFcLog(log_file)
            if not analysisResultTuple:
                NTerror("Failed to analyze log file: %s" % log_file)
                return True
            timeTaken, entryCrashed, nr_error, nr_warning, nr_message, nr_debug = analysisResultTuple
            if entryCrashed or (nr_error > self.MAX_ERROR_COUNT_FC_LOG):
                NTmessage("Found %s/%s timeTaken/entryCrashed and %d/%d/%d/%d error,warning,message, and debug lines." % (timeTaken, entryCrashed, nr_error, nr_warning, nr_message, nr_debug) )
                NTmessage("Found %s errors in prep phase X please check: %s" % (nr_error, entry_code))
                resultList = []
                status = grep(log_file, 'ERROR', resultList=resultList, doQuiet=True, caseSensitive=False)
                if status == 0:
                    NTerror("%s found errors in log file; aborting." % entry_code)
                    NTmessage('\n'.join(resultList))
                    return True
            finalPhaseId = PHASE_C
        # end if convertMmCifCoor

        if convertMrRestraints:
                finalPhaseId = PHASE_R
                # Nothing else needed really.
        if copyToInputDir:
            if not finalPhaseId:
                NTerror("Failed to finish any prep stage.")
                return True
            if finalPhaseId not in self.phaseIdList:
                NTerror("Failed to finish valid prep stage: [%s]" % finalPhaseId)
                return True
            finalInputDir = getDeepByKeysOrAttributes(inputDirByPhase, finalPhaseId)
            if not finalInputDir:
                NTerror("Failed to get prep stage dir: [%s]" % finalInputDir)
                return True
            fn = "%s.tgz" % entry_code
            finalInputTgz = os.path.join(finalInputDir, fn)
            if not os.path.exists(finalInputTgz):
                NTerror("final input tgz missing: %s" % finalInputTgz)
                return True
            dst = os.path.join(self.results_dir, self.inputDir, entryCodeChar2and3)
            if not os.path.exists(dst):
                os.mkdir(dst)
            fullDst = os.path.join(dst, fn)
            if os.path.exists(fullDst):
                os.remove(fullDst)
            os.link(finalInputTgz, fullDst) # Will use less resources but will be expanded when copied between resources.
            NTmessage("Copied input %s to: %s" % (finalInputTgz, dst))
        else:
            NTwarning("Did not copy input %s" % finalInputTgz)
        # end else
        NTmessage("Done with %s" % entry_code)
    # end def


    def runCing(self):
        """On self.entry_list_todo.
        Return True on error.
        """

        NTmessage("Starting runCing")
#        return True

        NTmessage("Not using topos")
        entryListFileName = "entry_list_todo.csv"
        writeTextToFile(entryListFileName, toCsv(self.entry_list_todo))

        pythonScriptFileName = os.path.join(cingDirScripts, 'validateEntry.py')
#        inputDir = 'file://' + self.results_dir + '/' + self.recoordSyncDir
        inputDir = 'file://' + self.results_dir + '/' + self.inputDir
        outputDir = self.results_dir
        storeCING2db = "1" # DEFAULT: 1 All arguments need to be strings.
        extraArgList = (inputDir, outputDir, '.', '.', `ARCHIVE_TYPE_BY_CH23`, `PROJECT_TYPE_CCPN`, storeCING2db)

        if doScriptOnEntryList(pythonScriptFileName,
                            entryListFileName,
                            self.results_dir,
                            processes_max=self.processes_max,
                            delay_between_submitting_jobs=5, # why is this so long? because of time outs at tang?
                            max_time_to_wait=self.max_time_to_wait,
                            # <Molecule "2p80" (C:20,R:1162,A:24552,M:20)>
                            START_ENTRY_ID=0, # default.
                            MAX_ENTRIES_TODO=self.max_entries_todo,
                            extraArgList=extraArgList):
            NTerror("Failed to doScriptOnEntryList")
            return True
        # end if
    # end def runCing.

    def postProcessAfterVc(self):
        """Return True on error.
        TODO: embed.
        """

        NTmessage("Starting postProcessAfterVc")
        self.entry_list_nmr = readLinesFromFile(os.path.join(self.results_dir, 'entry_list_nmr.csv'))
        self.entry_list_done = readLinesFromFile(os.path.join(self.results_dir, 'entry_list_done.csv'))
        self.entry_list_todo = NTlist()
        self.entry_list_todo.addList(self.entry_list_nmr)
        self.entry_list_todo = self.entry_list_todo.difference(self.entry_list_done)

        NTmessage("Found entries in NMR          : %d" % len(self.entry_list_nmr))
        NTmessage("Found entries in NRG-CING done: %d" % len(self.entry_list_done))
        NTmessage("Found entries in NRG-CING todo: %d" % len(self.entry_list_todo))

        for entry_code in self.entry_list_todo:
            self.postProcessEntryAfterVc(entry_code)
        NTmessage("Done")
    # end def



    def createToposTokens(self):
        """Return True on error.
        TODO: embed.
        """
        extraArgListStr = "http://nmr.cmbi.umcn.nl/NRG-CING/prep/C jd@nmr.cmbi.umcn.nl:/Library/WebServer/Documents/NRG-CING . . BY_CH23_BY_ENTRY CCPN"

        NTmessage("Starting createToposTokens with extra params: [%s]" % extraArgListStr)
        self.entry_list_nmr = readLinesFromFile(os.path.join(self.results_dir, 'entry_list_nmr.csv'))
        self.entry_list_done = readLinesFromFile(os.path.join(self.results_dir, 'entry_list_done.csv'))
        self.entry_list_todo = NTlist()
        self.entry_list_todo.addList(self.entry_list_nmr)
        self.entry_list_todo = self.entry_list_todo.difference(self.entry_list_done)

        NTmessage("Found entries in NMR          : %d" % len(self.entry_list_nmr))
        NTmessage("Found entries in NRG-CING done: %d" % len(self.entry_list_done))
        NTmessage("Found entries in NRG-CING todo: %d" % len(self.entry_list_todo))

#        NTdebug("Quitting for now.")
#        return True

        tokenList = []
        for entry_code in self.entry_list_todo:
            tokenStr = ' '.join([VALIDATE_ENTRY_NRG_STR, entry_code, extraArgListStr])
            tokenList.append(tokenStr)
        tokenListStr = '\n'.join(tokenList)
        NTmessage("Writing tokens to: [%s]" % self.tokenListFileName)
        writeTextToFile(self.tokenListFileName, tokenListStr)
    # end def

    def prepare(self):
        "Return True on error."

        NTmessage("Starting prepare using self.entry_list_todo")

        if False: # DEFAULT: False
            entry_code = '1brv'
            if self.prepareEntry(entry_code, convertMmCifCoor=0, convertMrRestraints=1, convertStarCS=0):
                NTerror("In prepare failed prepareEntry")
                return True
        if False: # DEFAULT: False
#            self.entry_list_todo = "134d 135d 136d 177d 1crq 1crr 1ezc 1ezd 1gnc 1kld 1l0r 1lcc 1lcd 1msh 1qch 1r4e 1sah 1saj 1vve 2axx 2ezq 2ezr 2ezs 2i7z 2ku2 2neo 2ofg".split()
            self.entry_list_todo = "1crq 1crr 1ezc 1ezd 1kld 1sah 1saj 1vve 2axx 2ezq 2ezr 2ezs".split()
            self.entry_list_nmr = deepcopy(self.entry_list_todo)
            self.entry_list_nrg_docr = []

#            self.entry_list_todo = "1a4d 1brv 9bog".split()
#            self.entry_list_nmr = "1a4d 1a24 1brv 1afp ".split()
#            self.entry_list_nrg_docr = "1a4d 1a24 1afp".split()

#        self.entry_list_nmr = readLinesFromFile(os.path.join(self.results_dir, 'entry_list_nmr.csv'))
#        self.entry_list_done = readLinesFromFile(os.path.join(self.results_dir, 'entry_list_done.csv'))
#        self.entry_list_todo = NTlist()
#        self.entry_list_todo.addList(self.entry_list_nmr)
#        self.entry_list_todo = self.entry_list_todo.difference(self.entry_list_done)
##        self.entry_list_todo = "2znf".split()
        permutationArgumentList = NTdict() # per permutation hold the entry list.
        for entry_code in self.entry_list_todo:
            convertMmCifCoor = 0
            convertMrRestraints = 0
            convertStarCS = 0
            if entry_code in self.entry_list_nmr:
                convertMmCifCoor = 1
            if entry_code in self.entry_list_nrg_docr:
                convertMrRestraints = 1
            if convertMrRestraints:
                convertMmCifCoor = 0
            if not (convertMmCifCoor or convertMrRestraints):
                NTerror("not (convertMmCifCoor or convertMrRestraints) in prepare. Skipping entry: %s" % entry_code)
                continue
            argList = [convertMmCifCoor, convertMrRestraints, convertStarCS]
            argStringList = [ str(x) for x in argList ]
            permutationKey = ' '.join(argStringList) # strings
            if not getDeepByKeysOrAttributes(permutationArgumentList, permutationKey):
                permutationArgumentList[permutationKey] = NTlist()
            permutationArgumentList[permutationKey].append(entry_code)
#
#        NTmessage("Found entries in NMR          : %d" %  len(self.entry_list_nmr))
#        NTmessage("Found entries in NRG-CING done: %d" %  len(self.entry_list_done))
        NTmessage("Found entries in NRG-CING todo: %d" % len(self.entry_list_todo))
        for permutationKey in permutationArgumentList.keys(): # strings
#            permutationKeyForFileName = re.compile('[ ,\[\]]').sub('', permutationKey)
            permutationKeyForFileName = permutationKey.replace(' ', '')
            extraArgList = permutationKey.split()
            convertMmCifCoor, convertMrRestraints, convertStarCS = extraArgList
            NTmessage("Keys: %s split to: %s %s %s with number of entries %d" % (permutationKey, convertMmCifCoor, convertMrRestraints, convertStarCS, len(permutationArgumentList[permutationKey])))

#            NTdebug("Quitting for now.")
#            continue

            entryListFileName = "entry_list_todo_prep_perm_%s.csv" % permutationKeyForFileName
            writeTextToFile(entryListFileName, toCsv(permutationArgumentList[permutationKey]))
            pythonScriptFileName = __file__ # recursive call in fact.
            extraArgList = ['prepareEntry' ] + extraArgList
            if doScriptOnEntryList(pythonScriptFileName,
                                entryListFileName,
                                self.results_dir,
                                processes_max=self.processes_max,
                                max_time_to_wait=600,
                                extraArgList=extraArgList, # list of strings
                                START_ENTRY_ID=0, # DEFAULT: 0.
                                MAX_ENTRIES_TODO=self.max_entries_todo,
    #                            MAX_ENTRIES_TODO=self.max_entries_todo # DEFAULT
                                ):
                NTerror("In nrgCing#prepare Failed to doScriptOnEntryList")
                return True
            # end if
        # end for
        NTmessage("Done with prepare.")
    # end def

    def storeCING2db(self):
        "Return True on error."

        NTmessage("Starting storeCING2db using self.entry_list_done that will be derived here.")

#        self.searchPdbEntries()
#        self.getEntryInfo()

        if True: # DEFAULT: False
            self.entry_list_done = '2hyn 2kj3 2ku1'.split()

        if False: # DEFAULT: False
            self.entry_list_todo = "134d 135d 136d 177d 1crq 1crr 1ezc 1ezd 1gnc 1kld 1l0r 1lcc 1lcd 1msh 1qch 1r4e 1sah 1saj 1vve 2axx 2ezq 2ezr 2ezs 2i7z 2ku2 2neo 2ofg".split()
            self.entry_list_nmr = deepcopy(self.entry_list_todo)
            self.entry_list_nrg_docr = []

        NTmessage("Found entries in NRG-CING todo: %d" % len(self.entry_list_todo))

        # parameters for doScriptOnEntryList
        cingDirNRG = os.path.join(cingPythonDir, 'cing', 'NRG' )
        pythonScriptFileName = os.path.join(cingDirNRG, 'storeCING2db.py')
        entryListFileName = os.path.join( self.results_dir, 'entry_list_done.csv')
        writeEntryListToFile(entryListFileName, self.entry_list_done)
        extraArgList = (ARCHIVE_NRG_ID,) # note that for length one tuples the comma is required.

        doScriptOnEntryList(pythonScriptFileName,
                            entryListFileName,
                            self.results_dir,
                            processes_max = self.processes_max,
                            delay_between_submitting_jobs = 1,
                            max_time_to_wait = 60 * 60, # Largest entries take a bit longer than the initial 6 minutes; 2hyn etc.
                            START_ENTRY_ID = 0,
                            MAX_ENTRIES_TODO = self.max_entries_todo,
                            expectPdbEntryList = True,
                            extraArgList = extraArgList)
        NTmessage("Done with storeCING2db.")
    # end def
# end class.


if __name__ == '__main__':
    """
Additional modes I see:
        batchUpdate        Run validation checks to NRG-CING web site.
        prepare            Only moves the entries through prep stages.
    """
    cing.verbosity = verbosityDebug
    isProduction = 1       # DEFAULT: 1.
    max_entries_todo = 40  # DEFAULT: 40
    useTopos = 0           # DEFAULT: 0

    NTmessage(header)
    NTmessage(getStartMessage())
    ## Initialize the project
    m = nrgCing(isProduction=isProduction, max_entries_todo=max_entries_todo, useTopos=useTopos)

    destination = sys.argv[1]
    hasPdbId = False
    entry_code = '.'
    if is_pdb_code(destination): # needs to be first argument if this main is to be used by doScriptOnEntryList.
        entry_code = destination
        hasPdbId = True
        destination = sys.argv[2]
    # end if
    startArgListOther = 2
    if hasPdbId:
        startArgListOther = 3
    argListOther = []
    if len(sys.argv) > startArgListOther:
        argListOther = sys.argv[startArgListOther:]
    NTmessage('\nGoing to destination: %s with(out) on entry_code %s with extra arguments %s' % (destination, entry_code, str(argListOther)))

    try:
        if destination == 'updateWeekly':
            if m.updateWeekly():
                NTerror("Failed to updateWeekly")
        elif destination == 'prepare':
            if m.prepare():
                NTerror("Failed to prepare")
        elif destination == 'prepareEntry':
            convertMmCifCoor = 1
            convertMrRestraints = 0
            if len(argListOther) > 0:
                convertMmCifCoor = int(argListOther[0])
                if len(argListOther) > 1:
                    convertMrRestraints = int(argListOther[1])
            if m.prepareEntry(entry_code, convertMmCifCoor=convertMmCifCoor, convertMrRestraints=convertMrRestraints):
                NTerror("Failed to prepareEntry")
        elif destination == 'runCingEntry':
            m.entry_list_todo = [ entry_code ]
            if m.runCing():
                NTerror("Failed to runCingEntry")
        elif destination == 'postProcessAfterVc':
            if m.postProcessAfterVc():
                NTerror("Failed to postProcessAfterVc")
        elif destination == 'postProcessEntryAfterVc':
            if m.postProcessEntryAfterVc(entry_code):
                NTerror("Failed to postProcessEntryAfterVc")
        elif destination == 'createToposTokens':
            if m.createToposTokens():
                NTerror("Failed to createToposTokens")
        elif destination == 'storeCING2db':
            if m.storeCING2db():
                NTerror("Failed to storeCING2db")
        else:
            NTerror("Unknown destination: %s" % destination)
        # end if
    except:
        NTtracebackError()
    finally:
        NTmessage(getStopMessage())

