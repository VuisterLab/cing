#!/usr/bin/env python
"""
This script will use NRG files to generate the CING reports as well as the
indices that live on top of them. For weekly and for more mass updates.

Execute like:

$CINGROOT/python/cing/NRG/nrgCing.py [entry_code]
     prepare runCing storeCING2db 
     createToposTokens getEntryInfo searchPdbEntries createToposTokens
     updateWeekly updateFrontPages updateCsvDumps
     forEachStoredEntry forEachStoredEntryRunScript runWeekly

$CINGROOT/python/cing/NRG/nrgCing.py 1brv prepare
$CINGROOT/python/cing/NRG/nrgCing.py 1brv runCing

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

from cing import * #@UnusedWildImport # pylint: disable=W0622
from cing.Libs import disk
from cing.Libs.NTgenUtils import * #@UnusedWildImport
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.disk import rmdir
from cing.Libs.html import GOOGLE_ANALYTICS_TEMPLATE
from cing.Libs.html import GOOGLE_PLUS_ONE_TEMPLATE
from cing.Libs.html import copyCingHtmlJsAndCssToDirectory
from cing.Libs.html import getStandardCingRevisionHtml
from cing.NRG import ARCHIVE_NMR_REDO_ID
from cing.NRG import ARCHIVE_NRG_ID
from cing.NRG import ARCHIVE_RECOORD_ID
from cing.NRG import mapArchive2Base
from cing.NRG import mapArchive2Schema
from cing.NRG.PDBEntryLists import getBmrbLinks
from cing.NRG.PDBEntryLists import getBmrbNmrGridEntries
from cing.NRG.PDBEntryLists import getBmrbNmrGridEntriesDOCRDone
from cing.NRG.PDBEntryLists import getEntryListFromCsvFile
from cing.NRG.PDBEntryLists import getPdbEntries
from cing.NRG.PDBEntryLists import writeEntryListToFile
from cing.NRG.WhyNot import FAILED_TO_BE_CONVERTED_NRG
from cing.NRG.WhyNot import FAILED_TO_BE_VALIDATED_CING
from cing.NRG.WhyNot import NOT_NMR_ENTRY
from cing.NRG.WhyNot import NO_EXPERIMENTAL_DATA
from cing.NRG.WhyNot import PROJECT_ID_BMRB
from cing.NRG.WhyNot import PROJECT_ID_CCPN
from cing.NRG.WhyNot import PROJECT_ID_CING
from cing.NRG.WhyNot import PROJECT_ID_NRG
from cing.NRG.WhyNot import PROJECT_ID_PDB
from cing.NRG.WhyNot import PROJECT_ID_WATTOS
from cing.NRG.WhyNot import PROJECT_ISSUE_URL_BMRB
from cing.NRG.WhyNot import PROJECT_ISSUE_URL_CCPN
from cing.NRG.WhyNot import PROJECT_ISSUE_URL_CING
from cing.NRG.WhyNot import PROJECT_ISSUE_URL_NRG
from cing.NRG.WhyNot import PROJECT_ISSUE_URL_PDB
from cing.NRG.WhyNot import PROJECT_ISSUE_URL_WATTOS
from cing.NRG.WhyNot import TO_BE_VALIDATED_BY_CING
from cing.NRG.WhyNot import WhyNot
from cing.NRG.WhyNot import WhyNotEntry
from cing.NRG.nrgCingRdb import NrgCingRdb
from cing.NRG.nrgCingRdb import getPdbIdList
from cing.NRG.runSqlForSchema import runSqlForSchema
from cing.NRG.settings import * #@UnusedWildImport
from cing.Scripts.FC.utils import getBmrbCsCountsFromFile
from cing.Scripts.doScriptOnEntryList import doFunctionOnEntryList
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList
from cing.Scripts.vCing.vCing import TEST_CING_STR
from cing.Scripts.vCing.vCing import VALIDATE_ENTRY_NRG_STR
from cing.Scripts.vCing.vCing import Vcing
from cing.Scripts.validateEntry import ARCHIVE_TYPE_BY_CH23
from cing.Scripts.validateEntry import ARCHIVE_TYPE_BY_CH23_BY_ENTRY
from cing.Scripts.validateEntry import PROJECT_TYPE_CCPN
from cing.Scripts.validateEntry import PROJECT_TYPE_CING
from glob import glob
from shutil import * #@UnusedWildImport
import commands
import shutil
import string

PHASE_C = 'C'   # coordinates
PHASE_R = 'R'   # restraints
PHASE_S = 'S'   # Chemical shifts
PHASE_F = 'F'   # SSA swap/deassign

phaseIdList = [PHASE_C, PHASE_R, PHASE_S, PHASE_F ]
#        self.phaseDataList = [
#                     [ 'Coordinate',    PHASE_C],
#                     [ 'Restraint',     PHASE_R],
#                     [ 'Shift',         PHASE_S],
#                     [ 'Filter',        PHASE_F],
#                      ]

LOG_NRG_CING = 'log_nrgCing'
LOG_STORE_CING2DB = 'log_storeCING2db'
LOG_REFINE_ENTRY = 'log_refineEntry'
LOG_REPLACE_COOR = 'log_replaceCoordinates'
#DATA_STR = 'log_nrgCing'
mapArchive2LogDir = {ARCHIVE_NRG_ID:        LOG_NRG_CING, 
                     ARCHIVE_NMR_REDO_ID:   LOG_REFINE_ENTRY,
                     ARCHIVE_RECOORD_ID:    LOG_REPLACE_COOR,
                     }

FAILURE_PREP_STR    = "Failed to prepareEntry"
recoordSyncDir      = 'recoordSync'


# pylint: disable=R0902
class NrgCing(Lister):
    """Main class for preparing and running CING reports on NRG and maintaining the statistics."""    
    #: 2hym has 1726 and 2bgf is the only entry over 5,000 Just used for reporting. 
    #: The entry is still included and considered 'done'.
    MAX_ERROR_COUNT_CING_LOG = 2000
    # 104d had 16. 108d had 460 
    MAX_ERROR_COUNT_FC_LOG = 99999 
    FRACTION_CS_CONVERSION_REQUIRED = 0.05 # DEFAULT: 0.05
    
    def __init__(self,
                 useTopos=False,
                 getTodoList=True,
                 max_entries_todo=1,
                 max_time_to_wait=86400, 
                 processes_max=None
#                 isProduction=True # Now imported from settings/localSettings.py
                ):
        Lister.__init__(self)
        self.assumeAllAreDone = assumeAllAreDone
        # Can be as many as fail every time.
        self.entry_to_delete_count_max = 10 # DEFAULT: 10
#        Allows debugging the prep stages. 
#        Also requires entry_to_delete_count_max>0
        self.delete_entry_with_badorno_prep = False # DEFAULT: False; set to True to clean up. 
        self.isProduction = isProduction        
        #: Only during production we do a write to WHY_NOT"
        self.ignoreUpdatesTemporarily = True # DEFAULT: False
        # Dir as base in which all info and scripts like this one resides
        self.base_dir = os.path.join(cingPythonCingDir, "NRG")

        self.results_base = results_base                
        self.D = dDir # pylint: disable=C0103
        self.cgi_dir = cgiDir
        
        self.results_dir = None
        self.data_dir = None
        self.htmlFooter = None
        self.max_entries_todo = max_entries_todo
        #: one day. 2p80 took the longest: 5.2 hours. But <Molecule "2ku1" (C:7,R:1659,A:36876,M:30)> is taking longer. 
        # 2ku2 is taking over 12 hrs now.                
        self.max_time_to_wait = max_time_to_wait
        self.processes_max = detectCPUs()
        if processes_max:
            self.processes_max = processes_max
#        self.processes_max = 2 # DEFAULT: commented out.
        
        ## Total number of child processes to be done if all scheduled to be done
        ## are indeed to be done. This is set later on and perhaps adjusted
        ## when the user interrupts the process by ctrl-c.
#        self.url_csv_file_link_base = 'http://www.bmrb.wisc.edu/servlet_data/viavia/bmrb_pdb_match'
        ## Dictionary with matches bmrb to pdb
        self.matches_one2many = {}
        ## Dictionary with matches bmrb to pdb
        self.matches_one2many_inv = {}

        ## Dictionary with matches pdb to bmrb
        # will be overwritten except when testing
#        self.matches_many2one = {
#'1b4y': 4400 ,
#'1brv': 4020 ,
# }
        # Retrieve the linkages between BMRB and PDB entries.
        self.matches_many2one = getBmrbLinks()
        if not self.matches_many2one:
            nTerror("Failed to get BMRB-PDB links")
        # end if
        self.useTopos = useTopos
        self.getTodoList = getTodoList
        self.entry_list_pdb = NTlist()
        self.entry_list_nmr = NTlist()
        self.entry_list_nmr_exp = NTlist()
        self.entry_list_nrg = NTlist()          # should be the same as self.entry_list_nmr_exp
        self.entry_list_nrg_docr = NTlist()
        self.entry_list_nrgcing = NTlist()
        self.entry_list_nmr_redo = NTlist()

        # Stages are cumulative in that e.g. R always includes all from C. This simplifies this setup hopefully.
        # id #name         #code

        # NMR entries prepared from mmCIF coordinates (NRG-DOCR entries will overrule these any time).
#        self.entry_list_prep_stage_C = NTlist()   
        # Should include entry_list_nrg_docr if all came over from NRG-DOCR.
#        self.entry_list_prep_stage_R = NTlist()   
#        self.entry_list_prep_stage_S = NTlist()   # Adds chemical shifts if available.
#        self.entry_list_prep_stage_F = NTlist()   # Might be filtered otherwise simply stage S.
#        self.phaseList = [self.entry_list_prep_stage_C, self.entry_list_prep_stage_R, 
#            self.entry_list_prep_stage_S, self.entry_list_prep_stage_F]

        # From disk.
        self.entry_list_prep_tried = NTlist()
        self.entry_list_prep_crashed = NTlist()
        self.entry_list_prep_failed = NTlist()
        self.entry_list_prep_done = NTlist()

        self.entry_list_store_tried = NTlist()
        self.entry_list_store_crashed = NTlist()
        self.entry_list_store_failed = NTlist()
        self.entry_list_store_in_db = NTlist()
        self.entry_list_store_not_in_db = NTlist()
        self.entry_list_store_done = NTlist()

        self.entry_list_tried = NTlist()      # .cing directory and .log file present so it was tried to start but might not have finished
        self.entry_list_untried = NTlist()      # all NMR entries except those in the tried list
        self.entry_list_crashed = NTlist()    # has a stack trace
        self.entry_list_stopped = NTlist()    # was stopped by time out or by user or by system (any other type of stop but stack trace)
        self.entry_list_done = NTlist()       # finished to completion of the cing run.
        self.entry_list_todo = NTlist()
        self.entry_list_updated = NTlist()    # Entries whos SOURCE has been updated and consequently need updting in derived data here. 
        self.inputModifiedDict = NTdict()     # This is the most recent of mmCIF, NRG, BMRB CS.
        self.entry_list_obsolete = NTlist()
        self.entry_list_obsolete_bad = NTlist()
        self.entry_list_missing_prep = NTlist()

        self.reportCsConversion = 0
        self.archive_id = ARCHIVE_NRG_ID
        self.schema_id  = None
        self.log_dir    = None
        self.usePreviousPdbEntries      = False # DEFAULT: False Can be set to True for faster debug run.
        self.validateEntryExternalDone  = True  # DEFAULT: True For NMR_REDO it is not from the start.
        self.entry_list_possible        = None # Set in setPossibleEntryList

        #: List of entries that might be in NRG but are invalid. NRG-CING will start from coordinates only.
        self.entry_list_bad_nrg_docr = NTlist() 
        self.entry_list_bad_overall = NTlist() # List of entries that NRG-CING should not even attempt.

        self.map_issue_to_bad_entry_list = NTdict()
        # NRG issue. Bad ccpn docr project
        self.map_issue_to_bad_entry_list[(PROJECT_ID_NRG, 272)] = '1lcc 1lcd 2l2z 2neo'.split()        
        # FC created a CCPN project that fails to read in again.
        self.map_issue_to_bad_entry_list[(PROJECT_ID_CING, 266)] = '134d 177d 1gnc 1lcc 1lcd 1qch 1sae 1sah 1saj 1sak 1sal 3sak'.split() 
        # Queeny runs out of 2Gb memory for 2rqf 
        self.map_issue_to_bad_entry_list[(PROJECT_ID_CING, 310)] = '2rqf'.split() 
        # CCPN issue. FC created a CCPN project that fails.
        self.map_issue_to_bad_entry_list[(PROJECT_ID_CCPN, 3446961)] = '4a1m 2l4e 2l4f 2l60 2lgk 2lja 2ljd 2lje 2ljf'.split()
        # Issue 312:   FC doing a bad calculation in swapping for SSA.        
        self.map_issue_to_bad_entry_list[(PROJECT_ID_CING, 312)] =\
            '1aj3 1d0w 1e0a 1f8h 1kft 1mek 1rkl 1w9r 1yyj 2ca7 2exg 2h2m 2j15 2jnc 2jxh 2kcc 2l4g 2xfm'.split()
        for key in self.map_issue_to_bad_entry_list:
            self.entry_list_bad_overall.addList( self.map_issue_to_bad_entry_list[key] )
        # end for
        self.entry_list_bad_overall.removeDuplicates() 
        self.entry_list_bad_overall.sort() # Sort in place. 
        
        self.updateDerivedResourceSettings() # The paths previously initialized with None.

        
        if 0:
            self.entry_list_todo = NTlist() 
            self.entry_list_todo += "1brv 1dum".split()
        # end if
        if 0: # DEFAULT: 0
            nTmessage("Going to use specific entry_list_todo in prepare")
#            self.entry_list_todo = "1brv".split()
#            self.entry_list_todo = readLinesFromFile('/Users/jd/NRG/lists/bmrbPdbEntryList.csv')
#            self.entry_list_todo = NTlist( *self.entry_list_todo )
#            self.entry_list_todo = readLinesFromFile(os.path.join(self.results_dir, 'entry_list_nmr_random_1-500.csv'))
#            self.entry_list_todo = readLinesFromFile(os.path.join(self.results_dir, 'entry_list_prep_todo.csv'))
#            self.entry_list_nmr = deepcopy(self.entry_list_todo)
#            self.entry_list_nrg_docr = deepcopy(self.entry_list_todo)
        # end if
        if 0: # DEFAULT: False
            self.searchPdbEntries()
            self.entry_list_todo = readLinesFromFile(os.path.join(self.results_dir, 'entry_list_prep_todo.csv'))
            self.entry_list_todo = NTlist( *self.entry_list_todo )
        # end if
    # end def
        
    def setPossibleEntryList(self, redo = True):        
        """
        Defines which entries should be possible to prepare and run. 
        Return True on error.
        """
        self.entry_list_possible = NTlist()
        if False: # DEFAULT: False
            self.entry_list_possible += '1brv 1dum'.split()
            return
        # end if

        if not self.entry_list_nmr:
            if self.usePreviousPdbEntries and not redo:
                nTmessage("Using previously found entries from the PDB and NRG databases.")
                self.entry_list_nmr         = getEntryListFromCsvFile('entry_list_nmr.csv')
            else:
                ## following statement is equivalent to a unix command like:
                nTmessage("Looking for entries from the PDB database.")
                self.entry_list_nmr = NTlist()
                self.entry_list_nmr.addList(getPdbEntries(onlyNmr=True))
                if not self.entry_list_nmr:
                    nTerror("No NMR entries found")
                    return True
                # end if
            # end if
        # end if
        nTmessage("Found %5d NMR entries." % len(self.entry_list_nmr) )
        nTmessage("Subtracting %d NMR entries that are known to fail because of issue(s)." % len(self.entry_list_bad_overall))
        subtractListStr = str(self.entry_list_bad_overall)
        nTmessage("Subtracting: %s ..." % subtractListStr[:80])
        
        # List of entries that might be in NRG but are invalid. NRG-CING will start from coordinates only.
        #        self.entry_list_bad_nrg_docr = NTlist() 
        self.entry_list_possible = self.entry_list_nmr.difference( self.entry_list_bad_overall )
        nTmessage("Keeping %d NMR entries that should be possible." % len(self.entry_list_possible))
        self.entry_list_obsolete_bad = self.entry_list_bad_overall.difference( self.entry_list_nmr )
        if self.entry_list_obsolete_bad:
            nTmessage("Consider removing from code the list of bad entries which are no longer in PDB: %s" % str(
                self.entry_list_obsolete_bad))
#        else:
#            nTmessage("No bad entries in code that are: %s" % str(self.entry_list_obsolete_bad))
#            pass
        # end if        
    # end def    
        
    def updateDerivedResourceSettings(self):
        '''
        Derived from self.D, results_base
        NB This routine will also change:
            - the cwd to the results_dir
            - the archive_id dependent settings.
        '''
        self.results_dir = os.path.join(self.D, self.results_base)
        self.data_dir = os.path.join(self.results_dir, DATA_STR)                
        self.schema_id = mapArchive2Schema[ self.archive_id ]
        self.log_dir = mapArchive2LogDir[ self.archive_id ]
        if 1:
            cingRevisionUrlStr = getStandardCingRevisionHtml()
            baseName = mapArchive2Base[ self.archive_id ]
            urlText = archive_link_template.replace('%a', baseName)
            startText = "<a href='%(urlText)s'>%(baseName)s</A>" % dict( urlText=urlText, baseName=baseName )
        # endif
        self.htmlFooter = startText + ' resource last updated on %s by CING (%s)' % ( time.asctime(), cingRevisionUrlStr )             

        os.chdir(self.results_dir)                 
        if False: # DEFAULT: False
            nTdebug("In updateDerivedResourceSettings (re-)setting:")        
            nTdebug("results_dir:             %s" % self.results_dir)        
            nTdebug("data_dir:                %s" % self.data_dir)        
            nTdebug("schema_id:               %s" % self.schema_id)        
            nTdebug("log_dir:                 %s" % self.log_dir)
        # end if        
    # end def
    
    def setup(self):
        """
        Bundled setups that require significant resources.
        """  
        pass
    # end def

    def runWeekly(self):
        'Called by updateWeekly doing actual CING validation runs.'
        #: If and only if new_hits_entry_list is empty and getTodoList is False; no entries will be attempted.
        self.getTodoList = True     # DEFAULT: True.
        # The variable below is local and can be used to update a specific batch.
        new_hits_entry_list = [] # DEFAULT: [].define empty for checking new ones.
#        new_hits_entry_list = string.split("")
        if 0: # DEFAULT False; use for processing a specific batch.
            entryListFileName = os.path.join(self.results_dir, 'entry_list_nmr_random_1-500.csv')
            new_hits_entry_list = readLinesFromFile(entryListFileName)
#            new_hits_entry_list = new_hits_entry_list[100:110]
        # end if        

        nTmessage("In runWeekly now")
        
        if self.isProduction:
            nTmessage("Updating matches between BMRB and PDB")
            try:
                cmd = "%s/python/cing/NRG/matchBmrbPdb.py" % cingRoot
                redirectOutputToFile = "matchBmrbPdb.log"
                matchBmrbPdbProgram = ExecuteProgram(cmd, redirectOutputToFile=redirectOutputToFile)
                exitCode = matchBmrbPdbProgram()
                if exitCode:
                    nTerrorT("Failed to %s" % cmd)
                else:
                    self.matches_many2one = getBmrbLinks()
                # end if        
            except:
                nTtracebackError()
                nTerror("Failed to update matches between BMRB and PDB from " + getCallerName())
                return True
            # end try
            nTmessage("Using %s BMRB-PDB matches" % len(self.matches_many2one.keys()))
        else:
            nTmessage("Using previously found %s BMRB-PDB matches" % len(self.matches_many2one.keys()))            
        # end if
        if not self.matches_many2one:
            nTerror("Failed to get BMRB-PDB links")
            return True
        # end if

        # Get the PDB info to see which entries can/should be done.
        if self.searchPdbEntries():
            nTerror("Failed to searchPdbEntries")
            return True
        # end if        
        if not self.entry_list_possible:
            if self.setPossibleEntryList():
                nTerror("Failed to setPossibleEntryList in %s" % getCallerName())
                return True
            # end if        
        # end if        
#        self.entry_list_possible = NTlist(*self.entry_list_nmr)
        nTmessage("Using %d NMR entries as possible entries." % len(self.entry_list_possible))

        if new_hits_entry_list:
            nTmessage("Using new_hits_entry_list with %d entries." % len(new_hits_entry_list))
            self.entry_list_todo = NTlist(*new_hits_entry_list)
        elif self.getTodoList:
            # Get todo list and some others.
            if self.getEntryInfo():
                nTerror("Failed to getEntryInfo (first time).")
                return True
            # end if
        # end if
        if self.entry_list_todo and self.max_entries_todo:
            nTdebug("Now in updateWeekly starting to prepare")
            if self.prepare():
                nTerror("Failed to prepare")
                return True
            # end if
            if self.getEntryInfo(): # need to see which preps failed; they are then excluded from todo list.
                nTerror("Failed to getEntryInfo (second time in updateWeekly).")
                return True
            # end if
            # WARNING: the above command wipes out the self.entry_list_todo
            if new_hits_entry_list:
                nTwarning("Using new_hits_entry_list with %d entries. (B)" % len(new_hits_entry_list))
                self.entry_list_todo = NTlist(*new_hits_entry_list)
            # end if
            nTdebug("Doing runCing only on entries for which prep is considered done.")
            self.entry_list_todo = self.entry_list_todo.intersection( self.entry_list_prep_done )
            if self.runCing():
                nTerror("Failed to runCing")
                return True
            # end if        
            # Do or redo the retrieval of the info from the filesystem on the state of NRG-CING.
            if self.getEntryInfo():
                nTerror("Failed to getEntryInfo")
                return True
            # end if       
        # end if
    # end def
            
    def updateWeekly(self):
        'Look for updates and update.'
        nTmessage("In updateWeekly starting with:\n%r" % self)
        doUpdateFrontPages        = True # DEFAULT: True. 
        doUpdateFrontPagePlots    = True # DEFAULT: True. 
        doUpdateCsvDumps          = True # DEFAULT: True. 
        doRunWeekly               = True # DEFAULT: True. 
        doWriteEntryListOfList    = True # DEFAULT: True. 
        doWriteWhyNotEntries      = True # DEFAULT: True. 
        # Since this is live, it can be done first which is nice to see succeeding.
        if doUpdateFrontPages:
            nTmessage("-1- Updating the front pages")
            if self.updateFrontPages():
                nTerror("In updateWeekly failed updateFrontPages")
                return True
            # end if
        # end if        
        if doRunWeekly:
            nTmessage("-2- Running weekly runs.")
            if self.runWeekly(): # actual work.
                nTerror("Failed to runWeekly")
                return True
            # end if        
        # end if
        if doWriteEntryListOfList:
            nTmessage("-3- Writing CSV files with entry lists.")
            if self.writeEntryListOfList():
                nTerror("Failed to writeEntryListOfList")
                return True
            # end if        
        # end if
        if doWriteWhyNotEntries:
            nTmessage("-4- Writing WHY_NOT entries.")
            if self.writeWhyNotEntries():
                nTerror("Failed to writeWhyNotEntries")
                return True
            # end if
        # end if
        if doUpdateFrontPagePlots:
            nTmessage("-5- Updating the front page plots")
            if self.updateFrontPagePlots():
                nTerror("In updateWeekly failed updateFrontPagePlots")
                return True
            # end if
        # end if        
        if doUpdateCsvDumps:
            nTmessage("-6- Updating the CSV dumps from the RDB.")
            if self.updateCsvDumps():
                nTerror("In updateWeekly failed updateCsvDumps")
                return True
            # end if
        # end if                        
    # end def

    def reportHeadAndTailEntries(self, timeTakenDict): # pylint: disable=R0201
        'Report the head and tail of all entries.'
        timeTakenList = NTlist(*timeTakenDict.values())
        if len(timeTakenList) < 1:
            nTmessage("No entries in reportHeadAndTailEntries")
            return
        # end if        
        n = 10 # Number of entries to list
        m = n/2 # on either side
        if len(timeTakenList) < n:
#            nTdebug("All entries in random order: %s" % str(timeTakenDict.keys())) # useless
            return
        # end if        
        entryLoL = []
        timeTakenList.sort()
        timeTakenDictInv = timeTakenDict.invert()
        for i in range(2):
            entryList = []
            entryLoL.append(entryList)
            if i == 0:
                timeTakenListSlice = timeTakenList[:m]
            else:
                timeTakenListSlice = timeTakenList[-m:]
            for timeTaken in timeTakenListSlice:
                entryList.append(timeTakenDictInv[timeTaken])
            # end for
        # end for
        nTmessage("%s fastest %s and slowest %s" % (m, str(entryLoL[0]), str(entryLoL[1])))
    # end def


    def addModTimesFromMmCif(self):
        "Looking at mmCIF input file modification times."
        nTmessage(self.addModTimesFromMmCif.__doc__)
        for entry_code in self.entry_list_nmr:
            entryCodeChar2and3 = entry_code[1:3]
            fileName = os.path.join(CIFZ2, entryCodeChar2and3, '%s.cif.gz' % entry_code)
#            nTdebug("Looking at: " + fileName)
            if not os.path.exists(fileName):
                if self.isProduction:
                    nTmessage("Failed to find: " + fileName)
                continue
            # end if        
            self.inputModifiedDict[ entry_code ] = os.path.getmtime(fileName)
        # end for
    # end def

    def addModTimesFromNrg(self):
        "Looking at NRG input file modification times."
        nTmessage(self.addModTimesFromNrg.__doc__)
        for entry_code in self.entry_list_nrg_docr:
            fileName = os.path.join(self.results_dir, recoordSyncDir, entry_code, '%s.tgz' % entry_code)
            if not os.path.exists(fileName):
                if self.isProduction:
                    nTdebug("Failed to find: " + fileName)
                continue
            # end if        
            nrgMod = os.path.getmtime(fileName)
#            nTdebug("For %s found: %s" % ( fileName, nrgMod))
            prevMod = getDeepByKeysOrAttributes(self.inputModifiedDict, entry_code)

            if prevMod:
                if nrgMod > prevMod:
                    self.inputModifiedDict[ entry_code ] = nrgMod # nrg more recent
                # end if        
            else:
                self.inputModifiedDict[ entry_code ] = nrgMod # nrg more recent
                if self.isProduction:
                    nTwarning("Found no mmCIF file for %s" % entry_code)
            # end else
        # end for
    # end def

    def getInputModificationTimes(self):
        'Getting the input modification times.'
        nTmessage(self.getInputModificationTimes.__doc__)
        if self.addModTimesFromMmCif():
            nTerror("Failed to addModTimesFromMmCif aborting")
            return True
        # end if        
        if self.addModTimesFromNrg():
            nTerror("Failed to addModTimesFromNrg aborting")
            return True
#        self.addInputModificationTimesFromBmrb() # TODO:
        # end if        
    # end def

    def getEntryInfo(self):
        """Returns True for error.

        This routine sets self.entry_list_todo

        Will remove entry directories if they do not occur in NRG up to a maximum number as not to whip out
        every one in a single blow by accident.

        If an entry has restraint data but is not in DOCR, it will be done from mmCIF until it does occur in DOCR.
        
        In NMR_REDO a prep stage is everything but validation.                    
        """
        
        showTimings = False # DEFAULT: False Enable for reporting.
        
        nTmessage("Get the entries tried, todo, crashed, and stopped in %s from file system." % self.results_base)

        crdb = NrgCingRdb(schema=self.schema_id) # Make sure to close it.
        if not crdb:
            nTerror("In %s RDB connection was not opened" % getCallerName())
            return True
        # end if

        if not self.entry_list_possible: # DEFAULT 0 this is done by updateWeekly already.            
            if self.setPossibleEntryList():
                nTerror("Failed to setPossibleEntryList in %s" % getCallerName())
                return True
            # end if
        # end if
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
        self.entry_list_missing_prep = NTlist()
        self.entry_list_tried = NTlist()
        self.entry_list_untried = NTlist()
        self.entry_list_crashed = NTlist()
        self.entry_list_stopped = NTlist() # mutely exclusive from entry_list_crashed
        self.entry_list_done = NTlist()
        self.entry_list_todo = NTlist()
        self.entry_list_updated = NTlist()

        if self.getInputModificationTimes():
            nTerror("Failed to getInputModificationTimes aborting")
            return True
        # end if        
        nTmessage("Scanning the prepare logs.")
        timeTakenDict = NTdict()
        for entry_code in self.entry_list_possible: # to be expanded to include all NMR entries.        
            entryCodeChar2and3 = entry_code[1:3]
            logDir = os.path.join(self.results_dir, DATA_STR, entryCodeChar2and3, entry_code, self.log_dir )
#            nTdebug("Looking in log dir: %s" % logDir)
            logLastFile = globLast(logDir + '/*.log')
#            nTdebug("logLastFile: %s" % logLastFile)
            if not logLastFile:
                if self.isProduction and self.assumeAllAreDone:
                    nTmessage("Failed to find any prep log file in directory: %s" % logDir)
                # end if                            
                continue
            # end if            
            self.entry_list_prep_tried.append(entry_code)
            analysisResultTuple = analyzeCingLog(logLastFile)
            if not analysisResultTuple:
                nTmessage("Failed to analyze log file: %s" % logLastFile)
                self.entry_list_prep_crashed.append(entry_code)
                continue
            # end if                    
            timeTaken, entryCrashed, nr_error, nr_warning, nr_message, nr_debug = analysisResultTuple
            if entryCrashed:
                nTmessage("Detected a crash: %s in %s" % (entry_code, logLastFile))
                self.entry_list_prep_crashed.append(entry_code)
                continue # don't mark it as stopped anymore.
            # end if
            if not timeTaken:
                nTmessage("Unexpected [%s] for time taken in CING prep log file: %s assumed crashed." % (timeTaken, logLastFile))
                self.entry_list_prep_crashed.append(entry_code)
                continue # don't mark it as stopped anymore.
            # end if
            statusFailurePrep = grep(logLastFile, FAILURE_PREP_STR, doQuiet=True) # returns 1 if found
            if (not statusFailurePrep) or (nr_error > self.MAX_ERROR_COUNT_CING_LOG):
                self.entry_list_prep_failed.append(entry_code)
                nTmessageNoEOL("For %s found %s/%s timeTaken/entryCrashed and %d/%d/%d/%d error,warning,message, and debug lines." % (
                    entry_code, timeTaken, entryCrashed, nr_error, nr_warning, nr_message, nr_debug))
                nTmessage("Please check: " + logLastFile)
#                nTmessage("%s Found %s errors in prep phase X please check: %s" % (entry_code, nr_error, logLastFile))
                continue
            # end if
            if self.reportCsConversion:
                resultList = NTlist()
                grep(logLastFile, 'Found fraction', resultList)
                if not resultList:
                    self.entry_list_prep_failed.append(entry_code)
                    nTerror("%s Failed to get fraction" % entry_code)
                    continue
                # end if                        
                nTmessage("%s %s" % (entry_code, resultList[0]))
            # end if                        
            if timeTaken:
                timeTakenDict[entry_code] = timeTaken
            # end if        
            # Check resulting file.
            ccpnInputFilePath = os.path.join(self.results_dir, INPUT_STR, entryCodeChar2and3, "%s.tgz" % entry_code)
            if not os.path.exists(ccpnInputFilePath):
                self.entry_list_prep_failed.append(entry_code)
                nTerror("%s Failed to find ccpn input file: %s" % (entry_code,ccpnInputFilePath))
                continue
            # end if
            self.entry_list_prep_done.append(entry_code)
        # end for
        timeTakenList = NTlist(*timeTakenDict.values())
        if showTimings:
            nTmessage("Time taken by prepare statistics\n%s" % timeTakenList.statsFloat())
            self.reportHeadAndTailEntries(timeTakenDict)
        # end if
        
# SCAN CING
        
        nTmessage("\nStarting to scan CING report/log (in order of hash by ch23).")
        timeTakenDict = NTdict()
        subDirList = os.listdir(DATA_STR)
        for subDir in subDirList:
            if len(subDir) != 2:
                if subDir != DS_STORE_STR:
                    nTdebug('Skipping subdir with other than 2 chars: [' + subDir + ']')
                # end if
                continue
            # end if            
            entryList = os.listdir(os.path.join(DATA_STR, subDir))
            for entryDir in entryList:
                entry_code = entryDir
                if not is_pdb_code(entry_code):
                    if entry_code != DS_STORE_STR:
                        nTerror("String doesn't look like a pdb code: " + entry_code)
                    # end if
                    continue
                if entry_code in self.entry_list_bad_overall:
#                    nTdebug("Skipping bad pdb code: " + entry_code)
                    continue
                # end if                
#                nTdebug("Working on: " + entry_code)

                entrySubDir = os.path.join(DATA_STR, subDir, entry_code)
                if not entry_code in self.entry_list_nmr:
                    msg = "Found entry %s in %s but not in PDB-NMR." % (entry_code, self.results_base)
                    if len(self.entry_list_obsolete) < self.entry_to_delete_count_max:
                        msg += " Will be removed from disk as well."
                        rmdir(entrySubDir)
                        self.entry_list_obsolete.append(entry_code)
                    else:
                        msg += " Will not be removed from disk because there were already removed: %s entries." % (
                            self.entry_to_delete_count_max)
                    nTwarning(msg)
                    # end if
                # end if
#                 Can't remove prep because that gives us no chance to inspect the failure.                
                if not entry_code in self.entry_list_prep_done:
                    msg = "Found entry %s in %s file system but no good prep done." % (entry_code, self.results_base )
                    if len(self.entry_list_missing_prep) < self.entry_to_delete_count_max:
                        if self.delete_entry_with_badorno_prep:
                            msg += " Will be removed from disk as well."
                            rmdir(entrySubDir)
                        else:
                            msg += " Will not be removed from disk because of setting: delete_entry_with_badorno_prep"
                        # end if
                        self.entry_list_missing_prep.append(entry_code)
                    else:
                        msg += " Will not be removed from disk since there were already removed: %s entries." % (
                            self.entry_to_delete_count_max)
                    # end if
                    nTwarning(msg)
                # end if
                
                # Look for last log file. Tricky because validation may have been done otherwise. But need to be able to scan it.
                logLastFile = globLast(entrySubDir + '/log_validateEntry/*.log')
                if not logLastFile:
                    nTmessage("Failed to find any log file in directory: %s" % entrySubDir)
                    continue
                # end if
                # .cing directory and .log file present so it was tried to start but might not have finished
                self.entry_list_tried.append(entry_code)
                entryCrashed = False
                timeTaken, entryCrashed, nr_error, nr_warning, nr_message, nr_debug = analyzeCingLog(logLastFile)
                msg = "For %s found %s/%s timeTaken/entryCrashed and %d/%d/%d/%d error,warning,message, and debug lines." % (
                        entry_code, timeTaken, entryCrashed, nr_error, nr_warning, nr_message, nr_debug)
                if entryCrashed:
                    nTmessage(msg + " Crashed.")
                    self.entry_list_crashed.append(entry_code)
                    continue # don't mark it as stopped anymore.
                # end if
                if nr_error > self.MAX_ERROR_COUNT_CING_LOG:
                    nTmessage(msg + " Could still be ok." )
#                    nTmessage("Found %s which is over %s please check: %s" % (nr_error, self.MAX_ERROR_COUNT_CING_LOG, entry_code))
                # end if
                if timeTaken:
                    timeTakenDict[entry_code] = timeTaken
#                else:
#                    nTmessage("Unexpected [%s] for time taken in CING log for file: %s" % (timeTaken, logLastFile))
                # end if
                timeStampLastValidation = getTimeStampFromFileName(logLastFile)
                if not timeStampLastValidation:
                    nTdebug("Failed to retrieve timeStampLastValidation from %s" % logLastFile)
                # end if
                timeStampLastInputMod = getDeepByKeysOrAttributes(self.inputModifiedDict, entry_code)
                # If the input has been updated then the entry should be redone so don't add it to the done list.
                if timeStampLastValidation and timeStampLastInputMod:
#                    nTdebug("Comparing input to validation time stamps: %s to %s" % (timeStampLastInputMod, timeStampLastValidation))
                    if timeStampLastValidation < timeStampLastInputMod:
                        if self.ignoreUpdatesTemporarily:
                            pass
#                                nTdebug('Ignoring temporarily update available for entry: %s' % entry_code)
                        else:
                            self.entry_list_updated.append(entry_code)
                            continue
                        # end if
                    # end if
                else:
                    nTdebug("Dates for last validation of last input modification not both retrieved for %s." % entry_code)
                # end if    
                if not timeTakenDict.has_key(entry_code):
                    # was stopped by time out or by user or by system (any other type of stop but stack trace)
                    nTmessage("%s Since CING end message was not found in %s assumed to have stopped" % (entry_code, logLastFile))
                    self.entry_list_stopped.append(entry_code)
                    continue
                # end if
                
                cingDirEntry = os.path.join(entrySubDir, entry_code + ".cing")
                if not os.path.exists(cingDirEntry):
                    nTmessage("%s Entry stopped because no(t yet a) directory: %s" % (entry_code, cingDirEntry))
                    self.entry_list_stopped.append(entry_code)
                    continue
                # end if
                # Look for end statement from CING which shows it wasn't killed before it finished.
                indexFileEntry = os.path.join(cingDirEntry, "index.html")
                if not os.path.exists(indexFileEntry):
                    nTmessage("%s Since index file %s was not found assumed to have stopped" % (entry_code, indexFileEntry))
                    self.entry_list_stopped.append(entry_code)
                    continue
                # end if
                projectHtmlFile = os.path.join(cingDirEntry, entry_code, "HTML/index.html")
                if not os.path.exists(projectHtmlFile):
                    nTmessage("%s Since project html file %s was not found assumed to have stopped" % (entry_code, projectHtmlFile))
                    self.entry_list_stopped.append(entry_code)
                    continue
                # end if
                if self.isProduction: # Disable for testing.
                    molGifFile = os.path.join(cingDirEntry, entry_code, "HTML/mol.gif")
                    if not os.path.exists(molGifFile):
                        nTmessage("%s Since mol.gif file %s was not found assumed to have stopped" % (entry_code, projectHtmlFile))
                        self.entry_list_stopped.append(entry_code)
                        continue
                    # end if
                # end if
                self.entry_list_done.append(entry_code)
            # end for entryDir
        # end for subDir
        timeTakenList = NTlist(*timeTakenDict.values())
        if showTimings:
            nTmessage("Time taken by validation statistics\n%s" % timeTakenList.statsFloat())
            self.reportHeadAndTailEntries(timeTakenDict)
        # end if
        self.entry_list_store_in_db = crdb.getPdbIdList(fromCing=True)
        if not self.entry_list_store_in_db:
            nTerror("Failed to get any entry from schema %s RDB" % self.schema_id)
            self.entry_list_store_in_db = NTlist()
        # end if
        nTmessage("Found %s entries in schema %s RDB" % (len(self.entry_list_store_in_db), self.schema_id))

        writeTextToFile("entry_list_nmr_redo.csv",      toCsv(self.entry_list_nmr_redo))

        entry_dict_store_in_db = list2dict(self.entry_list_store_in_db)

        # Remove a few entries in RDB that are not done.
        entry_list_in_db_not_done =  self.entry_list_store_in_db.difference(self.entry_list_done)
        if entry_list_in_db_not_done:
            txt = str(entry_list_in_db_not_done)
            txt = txt[:80]
            nTmessage("There are %s entries in RDB that are not currently done: %s" % ( len(entry_list_in_db_not_done), txt) )
        else:
            nTmessage("All entries in RDB are also done")
        # end if
        entry_list_in_db_to_remove = NTlist( *entry_list_in_db_not_done )
        if len(entry_list_in_db_not_done) > self.entry_to_delete_count_max:
            entry_list_in_db_to_remove = entry_list_in_db_not_done[:self.entry_to_delete_count_max] # doesn't make it into a NTlist.
            entry_list_in_db_to_remove = NTlist( *entry_list_in_db_to_remove )
        if entry_list_in_db_to_remove:
            nTmessage("There are %s entries in RDB that will be removed: %s" % (
                    len(entry_list_in_db_to_remove), str(entry_list_in_db_to_remove)))
        else:
            nTmessage("No entries in RDB need to be removed.")
        # end if
        for entry_code in entry_list_in_db_to_remove:
            if crdb.removeEntry( entry_code ):
                nTerror("Failed to remove %s from RDB" % entry_code )
            # end if
        # end for
        crdb.close()
        del crdb

        nTmessage("Scanning the store logs of entries done.")
        timeTakenDict = NTdict()
        for entry_code in self.entry_list_done:
            entryCodeChar2and3 = entry_code[1:3]
            logDir = os.path.join(self.results_dir, DATA_STR, entryCodeChar2and3, entry_code, LOG_STORE_CING2DB )
            logLastFile = globLast(logDir + '/*.log')#            nTdebug("logLastFile: %s" % logLastFile)
            if not logLastFile:
                # DEFAULT: 0 or 1 when assumed all are done by store instead of validate. This is not always the case!
#                if self.isProduction and self.assumeAllAreDone:
#                    nTdebug("Failed to find any store log file in directory: %s" % logDir)
#                # end if
                continue
            # end if
            self.entry_list_store_tried.append(entry_code)
            analysisResultTuple = analyzeCingLog(logLastFile)
            if not analysisResultTuple:
                nTmessage("Failed to analyze log file: %s" % logLastFile)
                self.entry_list_store_crashed.append(entry_code)
                continue
            # end if
            timeTaken, entryCrashed, nr_error, nr_warning, nr_message, nr_debug = analysisResultTuple
            if entryCrashed:
                nTmessage("For CING store log file: %s assumed crashed on basis of analyzeCingLog." % logLastFile)
                self.entry_list_store_crashed.append(entry_code)
                continue # don't mark it as stopped anymore.
            # end if
            if not entry_dict_store_in_db.has_key(entry_code):
#                nTmessage("%s not in db." % entry_code)
                self.entry_list_store_not_in_db.append(entry_code)
                continue # don't mark it as stopped anymore.
            # end if
            if nr_error > self.MAX_ERROR_COUNT_CING_LOG:
                self.entry_list_store_failed.append(entry_code)
                nTmessage("For %s found %s/%s timeTaken/entryCrashed and %d/%d/%d/%d error,warning,message, and debug lines. Please check: %s" % ( # pylint: disable=C0301
                    entry_code, timeTaken, entryCrashed, nr_error, nr_warning, nr_message, nr_debug, logLastFile) )
#                nTmessage("%s Found %s errors in storing please check: %s" % (entry_code, nr_error, logLastFile))
                continue
            # end if
            if timeTaken:
                timeTakenDict[entry_code] = timeTaken
#            else:
#                nTmessage("Unexpected [%s] for time taken in CING log for file: %s" % (timeTaken, logLastFile))
            self.entry_list_store_done.append(entry_code)
        # end for

        # Consider the entries updated as not done.
        self.entry_list_done = self.entry_list_done.difference(self.entry_list_updated)
        # Consider the entries updated as not done.
        if self.archive_id == ARCHIVE_NRG_ID:
            self.entry_list_nrgcing = self.entry_list_done
        elif self.archive_id == ARCHIVE_NMR_REDO_ID:
            self.entry_list_nmr_redo = self.entry_list_done
        else:
            nTerror("No list to set for archive id %s for entry_list_done" % self.archive_id)
        # end if

        timeTakenList = NTlist(*timeTakenDict.values())
        if showTimings:
            nTmessage("Time taken by storeCING2db statistics\n%s" % timeTakenList.statsFloat())
            self.reportHeadAndTailEntries(timeTakenDict)
        # end if
        if not self.entry_list_tried:
            nTerror("Failed to find entries that CING tried.")
        # end if
        self.entry_list_todo = NTlist(*self.entry_list_nmr)
        self.entry_list_todo = self.entry_list_todo.difference(self.entry_list_done)
        self.entry_list_todo = self.entry_list_todo.difference(self.entry_list_bad_overall)        

        self.entry_list_untried = NTlist(*self.entry_list_nmr)
        self.entry_list_untried = self.entry_list_untried.difference(self.entry_list_tried)
        self.entry_list_untried = self.entry_list_untried.difference(self.entry_list_bad_overall)
        
        # Prioritize the entries not done yet so we have at least a first version of them.
        if self.max_entries_todo < len(self.entry_list_todo):
            prioritizedTodoList = self.prioritizeTodoList()
            if prioritizedTodoList == None:
                nTerror("Failed to prioritizeTodoList. Keeping current entry_list_todo")
            else:                
                self.entry_list_todo = prioritizedTodoList
            # end if
        # end if

        nTmessage("Found %4d entries by NMR (A)." % len(self.entry_list_nmr))

        nTmessage("Found %4d entries that CING prep tried." % len(self.entry_list_prep_tried))
        nTmessage("Found %4d entries that CING prep crashed." % len(self.entry_list_prep_crashed))
        nTmessage("Found %4d entries that CING prep failed." % len(self.entry_list_prep_failed))
        nTmessage("Found %4d entries that CING prep done." % len(self.entry_list_prep_done))

        nTmessage("Found %4d entries that CING tried (T)." % len(self.entry_list_tried))
        nTmessage("Found %4d entries that CING did not try (A-T)." % len(self.entry_list_untried))
        nTmessage("Found %4d entries that CING crashed (C)." % len(self.entry_list_crashed))
        nTmessage("Found %4d entries that CING stopped (S)." % len(self.entry_list_stopped))
        nTmessage("Found %4d entries that CING should update (U)." % len(self.entry_list_updated))
        nTmessage("Found %4d entries that CING did (B=A-C-S-U)." % len(self.entry_list_done))
        nTmessage("Found %4d entries todo (A-B, to a max of %d)." % (len(self.entry_list_todo), self.max_entries_todo))
        nTmessage("Found %4d entries in %s made obsolete." % (len(self.entry_list_obsolete), self.results_base))
        nTmessage("Found %4d entries in %s without prep." % (len(self.entry_list_missing_prep), self.results_base))
        nTmessage("Found %4d entries in RDB %s." % (len(self.entry_list_store_in_db), self.results_base))

        nTmessage("Found %4d entries that CING store tried." % len(self.entry_list_store_tried))
        nTmessage("Found %4d entries that CING store crashed." % len(self.entry_list_store_crashed))
        nTmessage("Found %4d entries that CING store failed." % len(self.entry_list_store_failed))
        nTmessage("Found %4d entries that CING store not in db." % len(self.entry_list_store_not_in_db))
        nTmessage("Found %4d entries that CING store done." % len(self.entry_list_store_done))

        nTmessage("Found %4d entries in NRG-CING." % len(self.entry_list_nrgcing))
        nTmessage("Found %4d entries in NMR_REDO." % len(self.entry_list_nmr_redo))


        if not self.entry_list_done:
            nTwarning("Failed to find entries that CING did.")
        # end if
#        nTmessage("Writing the entry lists already; will likely be overwritten next.")
        self.writeEntryListOfList()
    # end def

    def prioritizeTodoList(self):
        '''
        Prioritize the entries not done yet so we have at least a first version of them.
        Input from self is 
        max_entries_todo
        entry_list_todo
        entry_list_untried
        Return is an (empty) NTlist or None (default return value) on error. 
        '''
        result = NTlist()
        if not self.max_entries_todo:
            nTdebug("Returning empty todo list because max_entries_todo is null." )
            return result
        # end if            
        if self.max_entries_todo >= len(self.entry_list_todo):
            nTmessage('No need to prioritizeTodoList because all entries can be done (tried at least)')
            return self.entry_list_todo
        # Undone entries have highest priority.
        n = 0 
        if self.entry_list_untried:
            n = min( len(self.entry_list_untried), self.max_entries_todo)
            result = self.entry_list_untried[:n]
            nTdebug("Added %d entries to new todo list." % len(result))
            if n == self.max_entries_todo:
                nTdebug("Returning new todo list with only %d untried entries." % (len(result)))
                return result
            # end if
        else:
            nTdebug("All entries have been tried.")
        # end if
        entry_list_todo_minus_untried = self.entry_list_todo.difference(self.entry_list_untried)
        count_todo_minus_untried = len(entry_list_todo_minus_untried)
        nTdebug("entry_list_todo_minus_untried with %d entries." % count_todo_minus_untried )
        if not count_todo_minus_untried:
            nTmessage("No todo entries to additionally add. Returning new todo list with %d entries." % (len(result)))
            return result
        # end if
        # m is the number of entries to still add
        m = self.max_entries_todo - n
        # p is the number of entries that can be added.
        p = min( m, count_todo_minus_untried )
        nTdebug("%d entries to still add and %d entries that can be added." % ( m, p))
        result = result.union(entry_list_todo_minus_untried[:p])
        nTdebug("result with %d entries." % len(result) )
        
        duplicateList = result.removeDuplicates()
        if duplicateList:
            nTcodeerror("Found unexpected duplicates: %s" % str(duplicateList))
            nTcodeerror("Removed and continuing with %d entries" % len(result))
            return
        # end if
        result = result.sort()    
        return result 
    # end def

    def searchPdbEntries(self, redo = False):
        """
        Set the list of matched entries and the dictionary holding the
        number of matches. They need to be defined as globals to this module.
        Return True on error.
        Also searches the PDB and BMRB databases itself.
        """
#        modification_time = os.path.getmtime("/Users/jd/.cshrc")
#        self.match.d[ "1brv" ] = EntryInfo(time=modification_time)

#        nTmessage("Looking for entries in the different preparation stages.")
#        for i, phaseData in enumerate(self.phaseDataList):
#            entryList = self.phaseList[i]
#            phaseName, _phaseId = phaseData
#            l = len(entryList)
#            nTmessage("Found %d entries in prep stage %s" % (l, phaseName))
        if self.usePreviousPdbEntries and not redo:
            nTmessage("Using previously found entries from the PDB and NRG databases.")
            self.entry_list_pdb         = getEntryListFromCsvFile('entry_list_pdb.csv')
            self.entry_list_nmr         = getEntryListFromCsvFile('entry_list_nmr.csv')
            self.entry_list_nmr_exp     = getEntryListFromCsvFile('entry_list_nmr_exp.csv')
            self.entry_list_nrg         = getEntryListFromCsvFile('entry_list_nrg.csv')
            self.entry_list_nrg_docr    = getEntryListFromCsvFile('entry_list_nrg_docr.csv')
        else:
            ## following statement is equivalent to a unix command like:
            nTmessage("Looking for entries from the PDB and NRG databases.")
            self.entry_list_pdb = NTlist()
            self.entry_list_pdb.addList(getPdbEntries())
            if not self.entry_list_pdb:
                nTerror("No PDB entries found")
                return True
            # end if
            self.entry_list_nmr = NTlist()
            self.entry_list_nmr.addList(getPdbEntries(onlyNmr=True))
            if not self.entry_list_nmr:
                nTerror("No NMR entries found")
                return True
            # end if
            self.entry_list_nmr_exp = NTlist()
            self.entry_list_nmr_exp.addList(getPdbEntries(onlyNmr=True, mustHaveExperimentalNmrData=True))
            if not self.entry_list_nmr_exp:
                nTerror("No NMR with experimental data entries found")
                return True
            # end if
            self.entry_list_nrg = NTlist()
            self.entry_list_nrg.addList(getBmrbNmrGridEntries())
            if not self.entry_list_nrg:
                nTerror("No NRG entries found")
                return True
            # end if
            ## The list of all entry_codes for which tgz files have been found
            self.entry_list_nrg_docr = NTlist()
            self.entry_list_nrg_docr.addList(getBmrbNmrGridEntriesDOCRDone())
            if not self.entry_list_nrg_docr:
                nTerror("No NRG DOCR entries found")
                return True
            # end if
            if len(self.entry_list_nrg_docr) < 3000:
                nTerror("watch out less than 3000 entries found [%s] which is suspect; quitting" % len(self.entry_list_nrg_docr))
                return True
            # end if
        # end if        
        nTmessage("Found %5d PDB entries." % len(self.entry_list_pdb))
        nTmessage("Found %5d NMR entries." % len(self.entry_list_nmr))        
        nTmessage("Found %5d NMR with experimental data entries." % len(self.entry_list_nmr_exp))
        nTmessage("Found %5d PDB entries in NRG." % len(self.entry_list_nrg))
        nTmessage("Found %5d NRG DOCR entries. (A)" % len(self.entry_list_nrg_docr))
    # end def


    def writeEntryListOfList(self):
        'Write all entry lists to csv files.'
#        nTmessage("Writing the entry list of each list to file")

        writeTextToFile("entry_list_possible.csv",      toCsv(self.entry_list_possible))
        writeTextToFile("entry_list_pdb.csv",           toCsv(self.entry_list_pdb))
        writeTextToFile("entry_list_nmr.csv",           toCsv(self.entry_list_nmr))
        writeTextToFile("entry_list_nmr_exp.csv",       toCsv(self.entry_list_nmr_exp))
        writeTextToFile("entry_list_nrg.csv",           toCsv(self.entry_list_nrg))
        writeTextToFile("entry_list_nrg_docr.csv",      toCsv(self.entry_list_nrg_docr))
        writeTextToFile("entry_list_nrgcing.csv",       toCsv(self.entry_list_nrgcing))
        writeTextToFile("entry_list_nmr_redo.csv",      toCsv(self.entry_list_nmr_redo))


        writeTextToFile("entry_list_prep_tried.csv",    toCsv(self.entry_list_prep_tried))
        writeTextToFile("entry_list_prep_crashed.csv",  toCsv(self.entry_list_prep_crashed))
        writeTextToFile("entry_list_prep_failed.csv",   toCsv(self.entry_list_prep_failed))
        writeTextToFile("entry_list_prep_done.csv",     toCsv(self.entry_list_prep_done))

        writeTextToFile("entry_list_tried.csv",         toCsv(self.entry_list_tried))
        writeTextToFile("entry_list_untried.csv",       toCsv(self.entry_list_untried))
        writeTextToFile("entry_list_done.csv",          toCsv(self.entry_list_done))
        writeTextToFile("entry_list_todo.csv",          toCsv(self.entry_list_todo))
        writeTextToFile("entry_list_crashed.csv",       toCsv(self.entry_list_crashed))
        writeTextToFile("entry_list_stopped.csv",       toCsv(self.entry_list_stopped))
#        writeTextToFile("entry_list_timing.csv",        toCsv(timeTakenDict))
        writeTextToFile("entry_list_updated.csv",       toCsv(self.entry_list_updated))
        writeTextToFile("entry_list_obsolete.csv",      toCsv(self.entry_list_obsolete))
        writeTextToFile("entry_list_missing_prep.csv",  toCsv(self.entry_list_missing_prep))

        writeTextToFile("entry_list_store_tried.csv",   toCsv(self.entry_list_store_tried))
        writeTextToFile("entry_list_store_crashed.csv", toCsv(self.entry_list_store_crashed))
        writeTextToFile("entry_list_store_failed.csv",  toCsv(self.entry_list_store_failed))
        writeTextToFile("entry_list_store_not_in_db.csv", toCsv(self.entry_list_store_not_in_db))
        writeTextToFile("entry_list_store_done.csv",    toCsv(self.entry_list_store_done))

#        for i, phaseData in enumerate(self.phaseDataList):
#            entryList = self.phaseList[i]
#            _phaseName, phaseId = phaseData
#            fn = 'entry_list_prep_stage_%s.csv' % phaseId
#            writeTextToFile(fn, toCsv(entryList))
    # end def


    def writeWhyNotEntries(self):
        "Write the WHYNOT files"

        writeTheManyFiles = False
        why_not_db_comments_file = '%s.txt_done' % self.results_base
        why_not2_db_comments_file = '%s.txt_comments' % self.results_base
        why_not_db_comments_dir = os.path.join(self.results_dir, "cmbi8", "comments")
        why_not_db_raw_dir = os.path.join(self.results_dir, "cmbi8", "raw")

        nTmessage("Create WHY_NOT lists")
        nTdebug("why_not_db_comments_dir: %s" % why_not_db_comments_dir)        
        nTdebug("why_not_db_raw_dir:      %s" % why_not_db_raw_dir)        


        nTmessage("New why_not2 style annotations")
#        self.map_issue_to_bad_entry_list[(PROJECT_ID_CING, 266)] = '134d 177d 1gnc 1lcc 1lcd 1qch 1sae 1sah 1saj 1sak 1sal 3sak'.split()
        msg = ''
        entryCount = 0
        for keyTuple in self.map_issue_to_bad_entry_list.keys():
            projectId, issueId = keyTuple
            if projectId == PROJECT_ID_BMRB  :
                issueUrl = PROJECT_ISSUE_URL_BMRB   + str(issueId) 
            elif projectId == PROJECT_ID_CCPN  :
                issueUrl = PROJECT_ISSUE_URL_CCPN   + str(issueId) 
            elif projectId == PROJECT_ID_CING  :
                issueUrl = PROJECT_ISSUE_URL_CING   + str(issueId) 
            elif projectId == PROJECT_ID_NRG   :
                issueUrl = PROJECT_ISSUE_URL_NRG    + str(issueId) 
            elif projectId == PROJECT_ID_PDB   :
                issueUrl = PROJECT_ISSUE_URL_PDB    + str(issueId) 
            elif projectId == PROJECT_ID_WATTOS:
                issueUrl = PROJECT_ISSUE_URL_WATTOS + str(issueId) 
            else:
                nTerror('Failed to find valid projectId got %s' % projectId)
                continue
            # end if
            msg += 'COMMENT: Failed to process because of <a href="%s">issue %s</a> in the %s project.\n' % ( issueUrl, issueId, projectId )
            for entry_code in self.map_issue_to_bad_entry_list[keyTuple]:
                entryCount += 1
                msg += '%s,%s\n' % (self.results_base, entry_code )
            # end for
        # end for
        why_not2_db_comments_file = os.path.join(why_not_db_comments_dir, why_not2_db_comments_file)
        writeTextToFile(why_not2_db_comments_file, msg)
        nTmessage("Written %s why_not2 style entry comments for %s issues to file: %s" % (
            len(self.map_issue_to_bad_entry_list.keys()), entryCount, why_not2_db_comments_file))
        
        nTmessage("New why_not2 style annotations")
        whyNot = WhyNot() # stupid why this needs to be fully specified.
        # Loop for speeding up the checks. Most are not nmr.
        for entry_code in self.entry_list_nmr:
            whyNotEntry = WhyNotEntry(entry_code)
            whyNot[entry_code] = whyNotEntry
            whyNotEntry.comment = NOT_NMR_ENTRY
            whyNotEntry.exists = False
        # end for
        for entry_code in self.entry_list_nmr:
            whyNotEntry = getDeepByKeysOrAttributes(whyNot, entry_code)
            if not whyNotEntry:                
                continue
            # end if
            whyNotEntry.exists = True
            if entry_code not in self.entry_list_nrg:
                whyNotEntry.comment = NO_EXPERIMENTAL_DATA
                whyNotEntry.exists = False
                continue
            # end if
            if entry_code not in self.entry_list_nrg_docr:
                whyNotEntry.comment = FAILED_TO_BE_CONVERTED_NRG
                whyNotEntry.exists = False
                continue
            # end if
            if entry_code not in self.entry_list_tried:
                whyNotEntry.comment = TO_BE_VALIDATED_BY_CING
                whyNotEntry.exists = False
                continue
            # end if
            if entry_code not in self.entry_list_done:
                whyNotEntry.comment = FAILED_TO_BE_VALIDATED_CING
                whyNotEntry.exists = False
                continue
            # end if
#            whyNotEntry.comment = PRESENT_IN_CING
            # Entries that are present in the database do not need a comment
            del(whyNot[entry_code])
        # end loop over entries
        whyNotStr = '%s' % whyNot
#        nTdebug("whyNotStr truncated to 1000 chars: [" + whyNotStr[0:1000] + "]")
        whyNotFn = "%s.txt" % self.results_base
        writeTextToFile(whyNotFn, whyNotStr)

        why_not_db_comments_file = os.path.join(why_not_db_comments_dir, why_not_db_comments_file)
#        nTdebug("Copying to: " + why_not_db_comments_file)
        shutil.copy(whyNotFn, why_not_db_comments_file)
        if writeTheManyFiles:
            for entry_code in self.entry_list_done:
                # For many files like: /usr/data/raw/nmr-cing/           d3/1d3z/1d3z.exist
                char23 = entry_code[1:3]
                subDir = os.path.join(why_not_db_raw_dir, char23, entry_code)
                if not os.path.exists(subDir):
                    os.makedirs(subDir)
                fileName = os.path.join(subDir, entry_code + ".exist")
                if not os.path.exists(fileName):
    #                nTdebug("Creating: " + fileName)
                    fp = open(fileName, 'w')
        #            fprintf(fp, ' ')
                    fp.close()
                # end if
            # end for
        # end if
    # end def
            
    def _format_html(self, file_content):
        """
        Reformat the input HTML file content and return it.
        """
        old_string = r"<!-- INSERT JUMP BOX HERE -->"
        new_string = self._getJumpBoxHtml()
        file_content = string.replace(file_content, old_string, new_string)        

        additional_head_string = '''        
<link media="screen" href="dataTableMedia/css/demo_table.css"         type="text/css" rel="stylesheet"/>
<link media="screen" href="dataTableMedia/css/TableTools.css"         type="text/css" rel="stylesheet"/>
<script src="util.js"                                                 type="text/javascript"></script>
<script src="jquery.js"                                               type="text/javascript"></script>
<script src="customTables.js"                                         type="text/javascript"></script>
<script src="dataTableMedia/js/jquery.dataTables.js"                  type="text/javascript"></script>
<script src="dataTableMedia/js/TableTools.js"                     type="text/javascript"></script>
<script src="dataTableMedia/js/jquery.dataTables.select.filtering.js" type="text/javascript" ></script>
        '''
        old_string = r"<!-- INSERT ADDITIONAL HEAD STRING HERE -->"        
        file_content = string.replace(file_content, old_string, additional_head_string)        
        new_string = '''
            <table id="dataTables-summaryArchive" class="display" cellspacing="0" cellpadding="0" border="0"> 
            <thead>
            <tr> 
        '''
        #Write headers: 'name', 'rog', 'distance_count', 'cs_count', 'chothia_class', 'chain_count', 'res_count'
        for i,_header in enumerate(summaryHeaderList):
            new_string += '\t<th title="{help}">{header}</th>\n'.format(header = summaryHeader2List[i],
                                                                          help = summaryHeaderTitleList[i])
        # end for        
        new_string += '''
            </tr> 
            </thead>
            </table>
        '''
        old_string = r"<!-- INSERT NEW RESULT STRING HERE -->"        
        file_content = string.replace(file_content, old_string, new_string)
        return file_content
    # end def

    def updateFrontPagePlots(self):
        """
        Update the plots on the front page except the pretty plot webpages.
        Return True on error.
        """
        crdb = NrgCingRdb(schema=self.schema_id) # Make sure to close it.
        if not crdb:
            nTerror("In %s RDB connection was not opened" % getCallerName())
            return True
        # end if        
        for trending in [ 1, 0 ]: # DEFAULT: 1,0
#        for trending in [ 0 ]:
            if crdb.createPlots(doTrending = trending, results_dir = self.results_dir):
                nTerror("Failed to createPlots.")
                return True
            # end if
        # end for
        del crdb # Not needed but speed up GC.
        if self.updateFrontPagePrettyPlots():
            nTerror("Failed to updateFrontPagePrettyPlots.")
            return True
        # end if
    # end def
    
    def updateFrontPagePrettyPlots(self):
        """
        Create an indexing page with all images linked.
        Return True on error.
        """
        for trending in [ 1, 0 ]: # DEFAULT: 1,0
#        for trending in [ 0 ]:
            inputDir = os.path.join(self.results_dir, PLOT_STR )
            outputDir = os.path.join(self.results_dir, PPLOT_STR )
            if trending:
                inputDir = os.path.join(self.results_dir, PLOT_TREND_STR )
                outputDir = os.path.join(self.results_dir, PPLOT_TREND_STR )
            # end if            
            if self.createPrettyPlots(inputDir, outputDir):
                nTerror("Failed to createPrettyPlots.")
                return True
            # end if
        # end for
    # end def    
    def createPrettyPlots(self, inputDir, outputDir, fnExtension = 'png'):
        """
        Create an indexing page with all images linked.
        It is assumed here that the two directories are located in a shared parent directory
        so that relative URL can be used like: ./plot/xxx.png
        results_dir -> HTML
                    -> plot (inputDir)
                    -> pplot (outputDir)
        
        Extra copies of css will be copied to the outputDir
        """
        number_of_entries_per_row = 4
        number_of_files_per_column = 2
        imageWidth = 200    # 1600 org is four times as large
        imageHeight = 150   # 1200
        nTmessage("Updating index files for input directory: %s" % inputDir)
        if os.path.exists(outputDir):
#            nTmessage("Removing output directory: %s" % outputDir)
            shutil.rmtree(outputDir)
        # end if
#        nTmessage("Creating output directory: %s" % outputDir)
        os.mkdir(outputDir)
#        nTdebug("Doing copyCingHtmlJsAndCssToDirectory")
        copyCingHtmlJsAndCssToDirectory(outputDir)        
#        htmlDir = os.path.join(cingRoot, "HTML")
        fnMatchPattern = '*.' + fnExtension
        image_fn_list = glob(os.path.join(inputDir,fnMatchPattern))        
        inputDirBase = os.path.basename(inputDir)
#        nTdebug("Got relative part of inputDir: %s" % inputDirBase) # e.g. plotTrend
        image_code_list = []
        for image_fn in image_fn_list:
            _root, image_code, _ext = nTpath(image_fn)
            image_code_list.append(image_code)
        # end for        
        ## Get the number of files required for building an index
        number_of_images_all_present = len(image_code_list)
        number_of_images_per_file = number_of_entries_per_row * number_of_files_per_column
        ## Number of files with indexes in google style
        number_of_files = int(number_of_images_all_present / number_of_images_per_file)
        if number_of_images_all_present % number_of_images_per_file:
            number_of_files += 1
        # end if
        nTmessage("Creating %s pages for %s image codes" % (number_of_files, number_of_images_all_present))
#        nTmessage("Generating %s index html files" % (number_of_files))

        file_name = os.path.join (self.base_dir, "data", self.results_base, "indexPplot.html")
        file_content = open(file_name, 'r').read()
        old_string = r"<!-- INSERT NEW TITLE HERE -->"
        new_string = capitalizeFirst( inputDirBase )
        file_content = string.replace(file_content, old_string, new_string)
        old_string = r"<!-- INSERT NEW FOOTER HERE -->"
        file_content = string.replace(file_content, old_string, self.htmlFooter)
        old_string = r"<!-- INSERT GOOGLE ANALYTICS TEMPLATE HERE -->"
        file_content = string.replace(file_content, old_string, GOOGLE_ANALYTICS_TEMPLATE)
        old_string = r"<!-- INSERT GOOGLE PLUS ONE TEMPLATE HERE -->"
        file_content = string.replace(file_content, old_string, GOOGLE_PLUS_ONE_TEMPLATE)
        ## Count will track the number of entries done per index file
        images_done_per_file = 0
        ## Following variable will track all done sofar
        images_done_all = 0
        ## Tracking the number in the current row. Set for the rare case that there
        ## are no entries at all. Otherwise it will be initialize on first pass.
        num_in_row = 0
        ## Tracking the index file number
        file_id = 1
        ## Text per row in an index file to insert
        insert_text = ''
        ## Repeat for all entries plus a dummy pass for writing the last index file
        for image_code in image_code_list + [ None ]:
            ## Finish this index file
            ## The last index file will only be written once...
            if images_done_per_file == number_of_images_per_file or images_done_all == number_of_images_all_present:
                begin_image_count = number_of_images_per_file * (file_id - 1) + 1
                end_image_count = min(number_of_images_per_file * file_id,
                                           number_of_images_all_present)
#                nTdebug("begin_image_count, end_image_count, number_of_images_all_present: %5d %5d %5d" % (
#                    begin_image_count, end_image_count, number_of_images_all_present))
                # image_code is just the base name of the file name.
                new_string = "Images: %s-%s of %s." % (
                        begin_image_count,
                        end_image_count,
                        number_of_images_all_present
                        )
                old_string = r"<!-- INSERT NEW RESULT STRING HERE -->"                
                new_file_content = string.replace(file_content, old_string, new_string)
                # Always end the row by adding dummy columns
                if num_in_row != number_of_entries_per_row:
                    insert_text += (number_of_entries_per_row - num_in_row) * 2 * r"<td>&nbsp;</td>" + r"</tr>"
                # end if
                ## Create the new index file from the example one by replacing a string
                ## with the new content.
                old_string = r"<!-- INSERT NEW ROWS HERE -->"
                new_file_content = string.replace(new_file_content, old_string, insert_text)

                first_string = '<a href="index_%s.html">First &lt; &lt;</a>' % 1
                final_string  = '<a href="index_%s.html">Last &gt; &gt;</a>' % number_of_files
                prev_string = ''
                if file_id > 1:
                    prev_string = '<a href="index_%s.html">Previous &lt;</a>' % ( file_id - 1)
                # end if
                next_string = ''
                if file_id < number_of_files:
                    next_string = '<a href="index_%s.html">> Next</a>' % ( file_id + 1)
                # end if
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
                    # end if
                # end for
                old_string = r"<!-- INSERT NEW LINKS HERE -->"
                new_string = 'Result pages: ' + ' '.join([first_string, prev_string, links_string, next_string, final_string])
                new_file_content = string.replace(new_file_content, old_string, new_string)
                ## Make the first index file name still index.html
                new_file_name = os.path.join( outputDir, 'index_%s.html' % file_id)
                if not file_id:
                    new_file_name = os.path.join( outputDir, '/index.html' )
                # end if 
                writeTextToFile(new_file_name, new_file_content)   
                images_done_per_file = 0
                num_in_row = 0
                insert_text = ""
                file_id += 1
            # end for
            ## Build on current index file
            ## The last iteration will not execute this block because of this clause
            if images_done_all < number_of_images_all_present:
                images_done_all += 1
                images_done_per_file += 1
                ## Get the html code right by abusing the formatting chars.
                ## as in sprintf etc.
                imageRelUrl = os.path.join( '..', inputDirBase, image_code + '.' + fnExtension)
                tmp_string = """
<td> <a href="%(imageRelUrl)s"> <img SRC="%(imageRelUrl)s" border="0" width="%(imageWidth)s" height="%(imageHeight)s"> </a> </td>""" % dict(
                    imageRelUrl=imageRelUrl, imageWidth=imageWidth, imageHeight=imageHeight)
                num_in_row = images_done_per_file % number_of_entries_per_row
                if num_in_row == 0:
                    num_in_row = number_of_entries_per_row
                # end if
                if num_in_row == 1:
                    # Start new row
                    tmp_string = "\n<tr>" + tmp_string
                elif (num_in_row == number_of_entries_per_row):
                    # End this row
                    tmp_string = tmp_string + "\n</tr>"
                # end if
                insert_text += tmp_string
            # end if
        # end if
        index_file_first = 'index_1.html'
        index_file = os.path.join(outputDir, 'index.html')
        ## Assume that a link that is already present is valid and will do the job
#        nTdebug('Symlinking: %s %s' % (index_file_first, index_file))
        symlink(index_file_first, index_file)        
    # end def    
    
    def updateCsvDumps(self):
        """
        Dumps the relational database to about 1 Gb of CSV files.
        """
        csvDumpDir = os.path.join( self.results_dir, 'pgsql' )
        sqlFile = os.path.join( self.base_dir, 'sql', 'dumpNRG-CING.sql')
        if runSqlForSchema(sqlFile, schemaId = self.schema_id, rootPath=csvDumpDir):
            nTerror("Failed runSqlForSchema in updateCsvDumps")
            return True
    # end def
    
    def updateFrontPages(self):
        """
        Create a overall summary table that shows an overview of the tables.
        Created on Oct 13, 2011        
        @author: tbeek
        """
        nTmessage("Starting %s" % getCallerName())
        htmlDir = os.path.join(self.results_dir, "HTML")
        if os.path.isdir(htmlDir):
#            nTdebug("Removing original html directory for NRG-CING.")
            rmdir(htmlDir)
        # end if
        nTmessage("Creating HTML directory for %s." % self.results_base)
        mkdirs(htmlDir)
#        srcHtmlPath = os.path.join(cingRoot, cingPaths.html)        
        data_dir = os.path.join (self.base_dir, "data" )
        base_data_dir = os.path.join (data_dir, self.results_base )
        # Most crud can come in from the traditional method.
        copyCingHtmlJsAndCssToDirectory(htmlDir)
        
        nTmessage("Adding frontpage-specific html.")
        fnList = """
            about.html 
            contact.html 
            credits.html 
            help.html 
            helpCing.html 
            helpPlot.html 
            helpTutorials.html
            glossary.html 
            index.html
            download.html 
            plot.html 
            cing.png 
            icon_email.gif
            icon_reference.gif
            icon_website.png
            icon_youtube.jpeg
            icon_download.gif
            NRG-CING_circle.png
            """.split()
        for fn in fnList:
            srcFile = os.path.join(base_data_dir, fn)
            dstFile = os.path.join(htmlDir,       fn)
            if not fn.endswith('.html'):
                copyfile(srcFile, dstFile)
#                nTdebug("-1- Added extra file %s." % dstFile)
                continue
            # end if
            file_content = open(srcFile, 'r').read()                    
            old_string = r"<!-- INSERT NEW FOOTER HERE -->"
            file_content = string.replace(file_content, old_string, self.htmlFooter)
            old_string = r"<!-- INSERT GOOGLE ANALYTICS TEMPLATE HERE -->"
            file_content = string.replace(file_content, old_string, GOOGLE_ANALYTICS_TEMPLATE)                        
            old_string = r"<!-- INSERT GOOGLE PLUS ONE TEMPLATE HERE -->"
            file_content = string.replace(file_content, old_string, GOOGLE_PLUS_ONE_TEMPLATE)                        
            if fn != 'index.html':
                writeTextToFile(dstFile, file_content)
#                nTdebug("-2- Added extra file %s." % dstFile)
                continue
            # end if
            # Get framework input
            file_content = self._format_html(file_content)                            
            htmlfile = os.path.join(htmlDir, 'index.html')
            writeTextToFile(htmlfile, file_content)
#            nTdebug("-3- Written HTML index file: %s" % htmlfile)            
        # end for
        nTmessage("Copy the overall index")
        org_file = os.path.join(data_dir, 'redirect.html')
        new_file = os.path.join(self.results_dir, 'index.html')
        shutil.copy(org_file, new_file)
        
        nTmessage("Copy the python cgi server for TableTools\n")
        cgi_file_name = 'DataTablesServer.py'
        if not os.path.exists(self.cgi_dir):
            nTerror("Please first create the server directory as expected at: %s" % self.cgi_dir)
            return True
        # end if
        org_file = os.path.join(self.base_dir, 'server', cgi_file_name)
        new_file = os.path.join(self.cgi_dir, cgi_file_name)
        if os.path.exists(new_file): # remove because if it's a hard link the copy will fail.
            os.unlink(new_file)
        # end if
        shutil.copy(org_file, new_file)
    # end def

    def postProcessEntryAfterVc(self, entry_code):
        """
        Unzips the tgz.
        Copies the log
        Removes both tgz & log.

        Returns True on error.
        """
        nTmessage("Doing postProcessEntryAfterVc on  %s" % entry_code)

        doRemoves = 0 # DEFAULT 0 enable to clean up.
        doLog = 1 # DEFAULT 1 disable for testing.
        doTgz = 1 # DEFAULT 1 disable for testing.
        doCopyTgz = 1

#            'Initialize the Vcing class'
        nTmessage("Setting up Vcing")
        vc = Vcing(max_time_to_wait_per_job=self.max_time_to_wait)
        nTmessage("Starting with %r" % vc)

        entryCodeChar2and3 = entry_code[1:3]
        entryDir = os.path.join(self.data_dir , entryCodeChar2and3, entry_code)
        if not os.path.exists(entryDir):
            nTerror("Skipping %s because dir %s was not found." % (entry_code, entryDir))
            return True
        # end if
        os.chdir(entryDir)

        if doLog:
            master_target_log_dir = os.path.join(vc.master_target_dir, vc.MASTER_TARGET_LOG)
            if not os.path.exists(master_target_log_dir):
                nTerror("Skipping %s because failed to find master_target_log_dir: %s" % (entry_code, master_target_log_dir))
                return True
            # end if
            logScriptFileNameRoot = 'validateEntryNrg'
            logFilePattern = '/*%s_%s_*.log' % (logScriptFileNameRoot, entry_code)
            logLastFile = globLast(master_target_log_dir + logFilePattern)
            if not logLastFile:
                nTerror("Skipping %s because failed to find last log file in directory: %s by pattern %s" % (
                    entry_code, master_target_log_dir, logFilePattern))
                return True
            # end if
            date_stamp = getDateTimeStampForFileName(logLastFile)
            if not date_stamp:
                nTerror("Skipping %s because failed to find date for log file: %s" % (entry_code, logLastFile))
                return True
            # end if
            logScriptFileNameRootNew = 'validateEntry' # stick them in next to the locally derived logs.
            newLogDir = 'log_' + logScriptFileNameRootNew
            if not os.path.exists(newLogDir):
                os.mkdir(newLogDir)
            # end if
            logLastFileNew = '%s_%s.log' % (entry_code, date_stamp)
            logLastFileNewFull = os.path.join(newLogDir, logLastFileNew)
            nTdebug("Copy from %s to %s" % (logLastFile, logLastFileNewFull))
            copy2(logLastFile, logLastFileNewFull)
            if doRemoves:
                os.remove(logLastFile)
            # end if
        # end if doLog
        if doTgz:
            tgzFileNameCing = entry_code + ".cing.tgz"
            if os.path.exists(tgzFileNameCing):
                nTdebug("Removing local tgz %s" % (tgzFileNameCing))
                os.remove(tgzFileNameCing)
            # end if
            if doCopyTgz:
                tgzFileNameCingMaster = os.path.join(vc.master_d, self.results_base, 'data', entryCodeChar2and3, 
                                                     entry_code, tgzFileNameCing)
                if not os.path.exists(tgzFileNameCingMaster):
                    nTerror("Skipping %s because failed to find master's: %s" % (entry_code, tgzFileNameCingMaster))
                    return True
                # end if
                copy2(tgzFileNameCingMaster, '.')
            # end if
            if not os.path.exists(tgzFileNameCing):
                nTerror("Skipping %s because local tgz %s not found in: %s" % (entry_code, tgzFileNameCing, os.getcwd()))
                return True
            # end if
            fileNameCing = entry_code + ".cing"
            if os.path.exists(fileNameCing):
                nTdebug("Removing local .cing %s" % (fileNameCing))
                rmtree(fileNameCing)
            # end if
            cmd = "tar -xzf %s" % tgzFileNameCing
            nTdebug("cmd: %s" % cmd)
            status, result = commands.getstatusoutput(cmd)
            if status:
                nTerror("Failed to untar status: %s with result %s" % (status, result))
                return True
            # end if
            if doRemoves:
                os.remove(tgzFileNameCing)
            # end if
        # end if doTgz
    # end def

    def prepareEntry(self, entry_code,
                     doInteractive=0,
                     convertMmCifCoor=1,
                     convertMrRestraints=1,
                     convertStarCS=1,
                     filterCcpnAll=0
                     ):
        "Return True on error."

        entryCodeChar2and3 = entry_code[1:3]
        copyToInputDir = 1 # DEFAULT: 1
#        filterTopViolations = 1 # DEFAULT: 1
        finalPhaseId = None # id to use for final move to input dir.
        # Absolute paths with still be appending a entryCodeChar2and3
        inputDirByPhase = {
                           PHASE_C: os.path.join(dir_C, entryCodeChar2and3, entry_code),
                           PHASE_S: os.path.join(dir_S, entryCodeChar2and3, entry_code),
                           PHASE_R: os.path.join(self.results_dir, recoordSyncDir, entry_code),
                           PHASE_F: os.path.join(dir_F, entryCodeChar2and3, entry_code),
                           }

        nTmessage("interactive            interactive run is fast use zero for production   %s" % doInteractive)
        nTmessage("")
        nTmessage("convertMmCifCoor       Start from mmCIF                                  %s" % convertMmCifCoor)
        nTmessage("convertMrRestraints    Start from DOCR                                   %s" % convertMrRestraints)
        nTmessage("convertStarCS          Adds STAR CS to Ccpn with FC                      %s" % convertStarCS)
        nTmessage("filterCcpnAll          Filter CS and restraints with FC                  %s" % filterCcpnAll)
        nTmessage("Doing                                                                 %4s" % entry_code)
#        nTdebug("copyToInputDir          Copies the input to the collecting directory                                 %s" % copyToInputDir)


        if convertMmCifCoor == convertMrRestraints:
            nTerror("One and one only needs to be True of convertMmCifCoor == convertMrRestraints")
            return True
        # end if
        if convertMmCifCoor:
            nTmessage("  mmCIF")

            c_sub_entry_dir = os.path.join(dir_C, entryCodeChar2and3)
            c_entry_dir = os.path.join(c_sub_entry_dir, entry_code)

            script_file = '%s/ReadMmCifWriteNmrStar.wcf' % wcf_dir
            inputMmCifFile = os.path.join(CIFZ2, entryCodeChar2and3, '%s.cif.gz' % entry_code)
            outputStarFile = "%s_C_Wattos.str" % entry_code
            script_file_new = "%s.wcf" % entry_code
            log_file = "%s.log" % entry_code

            if not os.path.exists(c_entry_dir):
                mkdirs(dir_C)
            # end if
            if not os.path.exists(c_sub_entry_dir):
                mkdirs(c_sub_entry_dir)
            # end if
            os.chdir(c_sub_entry_dir)
            if os.path.exists(entry_code):
                if 1: # DEFAULT: 1
                    rmtree(entry_code)
                # end if False
            # end if
            if not os.path.exists(entry_code):
                os.mkdir(entry_code)
            # end if
            os.chdir(entry_code)

            if not os.path.exists(inputMmCifFile):
                nTerror("%s No input mmCIF f: %s" % (entry_code, inputMmCifFile))
                return True
            # end if
            maxModels = '999'
            if doInteractive:
                maxModels = '1'
            # end if
            script_str = readTextFromFile(script_file)
            script_str = script_str.replace('WATTOS_VERBOSITY', str(cing.verbosity))
            script_str = script_str.replace('INPUT_MMCIF_FILE', inputMmCifFile)
            script_str = script_str.replace('MAX_MODELS', maxModels)
            script_str = script_str.replace('OUTPUT_STAR_FILE', outputStarFile)

    #        self.wattosVerbosity = cing.verbosity
            #: development machine Stella only has 4g total
            #: This is only important for largest entries like 2ku2
    #        self.wattosMemory = '2g' # DEFAULT: 4g but reduced to 2 because -d32 was needed on OSX Lion currently.
    #        if not self.isProduction:
    #            self.wattosMemory = '2g'
            # For x86 (32 bit) os not all 2g are available. For Ubuntu it seems to be less than 1800, trying 1500.  
            wattosProg = "%s Wattos.CloneWars.UserInterface -at -verbosity %s" % ( JVM_CMD_STD, cing.verbosity )
            writeTextToFile(script_file_new, script_str)
            wattosProgram = ExecuteProgram(wattosProg, #rootPath = wattosDir,
                                     redirectOutputToFile=log_file,
                                     redirectInputFromFile=script_file_new)
#            now = time.time()
            wattosExitCode = wattosProgram()
#            difTime = time.time() - now #@UnusedVariable
#            nTdebug("Wattos reading the mmCIF took %8.1f seconds" % difTime)
            if wattosExitCode:
                nTerror("%s Failed wattos script %s with exit code: %s" % (entry_code, script_file_new, str(wattosExitCode)))
                return True
            # end if
            resultList =[]
            status = grep(log_file, 'ERROR', resultList=resultList, doQuiet=True)
            if status == 0:
                nTerror("%s found %s errors in Wattos log f; aborting." % ( entry_code, len(resultList)))
                nTerror('\n' +'\n'.join(resultList))
                return True
            # end if
            os.unlink(script_file_new)
            if not os.path.exists(outputStarFile):
                nTerror("%s found no output star file [%s]" % (entry_code, outputStarFile))
                return True
            # end if

            nTmessage("  star2Ccpn")
            log_file = "%s_star2Ccpn.log" % entry_code
#            inputStarFile = "%s_C_wattos.str" % entry_code
            inputStarFile = outputStarFile
            inputStarFileFull = os.path.join(c_entry_dir, inputStarFile)
            outputCcpnFile = "%s.tgz" % entry_code
            fcScript = os.path.join(cingDirScripts, 'FC', 'convertStar2Ccpn.py')

            if not os.path.exists(inputStarFileFull):
                nTerror("%s previous step produced no star file at %s." % (entry_code, inputStarFileFull))
                return True
            # end if

            # Will save a copy to disk as well.
            convertProgram = ExecuteProgram("python -u %s" % fcScript, redirectOutputToFile=log_file)
#            nTmessage("==> Running Wim Vranken's FormatConverter from script %s" % fcScript)
            exitCode = convertProgram("%s %s %s" % (inputStarFile, entry_code, c_entry_dir))
            if exitCode:
                nTerror("Failed convertProgram with exit code: %s" % str(exitCode))
                return True
            # end if
            analysisResultTuple = analyzeFcLog(log_file)
            if not analysisResultTuple:
                nTerror("Failed to analyze log f: %s" % log_file)
                return True
            # end if
            timeTaken, entryCrashed, nr_error, nr_warning, nr_message, nr_debug = analysisResultTuple
            if entryCrashed or (nr_error > self.MAX_ERROR_COUNT_FC_LOG):
                nTmessage("Found %s/%s timeTaken/entryCrashed and %d/%d/%d/%d error,warning,message, and debug lines." % (
                    timeTaken, entryCrashed, nr_error, nr_warning, nr_message, nr_debug) )
                nTmessage("Found %s errors in prep phase C please check: %s" % (nr_error, entry_code))
                resultList = []
                status = grep(log_file, 'ERROR', resultList=resultList, doQuiet=True, caseSensitive=False)
                if status == 0:
                    nTerror("%s found errors in log f; aborting." % entry_code)
                    nTmessage('\n'.join(resultList))
                    return True
                # end if
            # end if
            if not os.path.exists(outputCcpnFile):
                nTerror("%s found no output ccpn f %s" % (entry_code, outputCcpnFile))
                return True
            # end if
            finalPhaseId = PHASE_C
        # end if convertMmCifCoor
        if convertMrRestraints:
            nTmessage("  DOCR CCPN")
            finalPhaseId = PHASE_R
            # Nothing else needed really.
        # end if
        if convertStarCS:
            nTmessage("  star CS")
            s_sub_entry_dir = os.path.join(dir_S, entryCodeChar2and3)
            s_entry_dir = os.path.join(s_sub_entry_dir, entry_code)

            if not os.path.exists(s_entry_dir):
                mkdirs(dir_S)
            # end if                
            if not os.path.exists(s_sub_entry_dir):
                mkdirs(s_sub_entry_dir)
            # end if
            os.chdir(s_sub_entry_dir)
            if os.path.exists(entry_code):
                rmtree(entry_code)
            # end if
            if not os.path.exists(entry_code):
                os.mkdir(entry_code)
            # end if
            os.chdir(entry_code)

            inputDir = getDeepByKeysOrAttributes(inputDirByPhase, finalPhaseId)
            if not inputDir:
                nTerror("Failed to get prep stage dir for phase: [%s]" % finalPhaseId)
                return True
            # end if
            fn = "%s.tgz" % entry_code
            inputCcpnFile = os.path.join(inputDir, fn)
            outputCcpnFile = fn
            if not os.path.exists( inputCcpnFile):
                nTerror("Failed to find input: %s" % inputCcpnFile)
                return True
            # end if
            inputLocalCcpnFile = "%s_input.tgz" % entry_code
            shutil.copy( inputCcpnFile, inputLocalCcpnFile )


            log_file = "%s_starCS2Ccpn.log" % entry_code

            if not self.matches_many2one.has_key(entry_code):
                nTerror("No BMRB entry for PDB entry: %s" % entry_code)
                return True
            # end if
            bmrb_id = self.matches_many2one[entry_code]
            bmrb_code = 'bmr%s' % bmrb_id

#            digits12 ="%02d" % ( bmrb_id % 100 )
#            inputStarDir = os.path.join(bmrbDir, digits12)
            inputStarDir = os.path.join(bmrbDir, bmrb_code)
            if not os.path.exists(inputStarDir):
                nTerror("Input star dir not found: %s" % inputStarDir)
                return True
            # end if
            inputStarFile = os.path.join(inputStarDir, '%s_21.str'%bmrb_code)
            if not os.path.exists(inputStarFile):
                nTerror("inputStarFile not found: %s" % inputStarFile)
                return True
            # end if
            fcScript = os.path.join(cingDirScripts, 'FC', 'mergeNrgBmrbShifts.py')

            # Will save a copy to disk as well.
            convertProgram = ExecuteProgram("python -u %s" % fcScript, redirectOutputToFile=log_file)
#            nTmessage("==> Running Wim Vranken's FormatConverter from script %s" % fcScript)
            exitCode = convertProgram("%s -bmrbCodes %s -raise -force -noGui" % (entry_code, bmrb_code))
            if exitCode:
                nTerror("Failed convertProgram with exit code: %s" % str(exitCode))
                return True
            # end if
            analysisResultTuple = analyzeFcLog(log_file)
            if not analysisResultTuple:
                nTerror("Failed to analyze log f: %s" % log_file)
                return True
            # end if
            timeTaken, entryCrashed, nr_error, nr_warning, nr_message, nr_debug = analysisResultTuple
            if entryCrashed or (nr_error > self.MAX_ERROR_COUNT_FC_LOG):
                nTmessage("Found %s/%s timeTaken/entryCrashed and %d/%d/%d/%d error,warning,message, and debug lines." % (
                    timeTaken, entryCrashed, nr_error, nr_warning, nr_message, nr_debug) )
                nTmessage("Found %s errors in prep phase S please check: %s" % (nr_error, entry_code))
                resultList = []
                status = grep(log_file, 'ERROR', resultList=resultList, doQuiet=True, caseSensitive=False)
                if status == 0:
                    nTerror("%s found errors in log f; aborting." % entry_code)
                    nTmessage('\n'.join(resultList))
                # end if
                return True
            # end if
            if not os.path.exists(outputCcpnFile):
                nTerror("%s found no output ccpn f %s" % (entry_code, outputCcpnFile))
                return True
            # end if
            if True:
                nTmessage("Testing completeness of FC merge by comparing input STAR with output CING counts" )
                conversionCsSucces = True
                nucleiToCheckList = '1H 13C 15N 31P'.split()
#                bmrbCountMap = getBmrbCsCounts()
#                bmrbCsMap = getDeepByKeysOrAttributes( bmrbCountMap, bmrb_id )
                bmrbCsMap = getBmrbCsCountsFromFile(inputStarFile)
                nTmessage("BMRB %r" % bmrbCsMap)

                project = Project.open(entry_code, status = 'new')
                project.initCcpn(ccpnFolder = outputCcpnFile)
                assignmentCountMap = project.molecule.getAssignmentCountMap()
                star_count_total = 0
                cing_count_total = 0
                for nucleusId in nucleiToCheckList:
                    star_count = getDeepByKeysOrAttributes( bmrbCsMap, nucleusId )
                    cing_count = getDeepByKeysOrAttributes( assignmentCountMap, nucleusId )
#                    nTdebug("nucleus: %s input: %s project: %s" % ( nucleusId, star_count, cing_count ) )
                    if star_count == None or star_count == 0:
#                        nTmessage("No nucleus: %s in input" % nucleusId)
                        continue
                    # end if
                    if cing_count == None:
                        nTerror("No nucleus: %s in project" % nucleusId)
                        continue
                    # end if
                    star_count_total += star_count
                    cing_count_total += cing_count
                # end for
                if star_count_total == 0:
                    f = 0.0
                else:
                    f = (1. * cing_count_total) / star_count_total
                # end if
                resultTuple = (self.FRACTION_CS_CONVERSION_REQUIRED, f, star_count_total, cing_count_total )

                # Use same number of field to facilitate computer readability.
                if f < self.FRACTION_CS_CONVERSION_REQUIRED:
                    nTmessage("Found fraction less than the cutoff %.2f but %.2f overall (STAR/CING: %s/%s)" % resultTuple)
                    conversionCsSucces = False
                else:
                    nTmessage("Found fraction of at least   cutoff %.2f at %.2f  overall (STAR/CING: %s/%s)" % resultTuple)
                # end if
                del project
            # end CS count check.

            if 1: # DEFAULT 1 tmp files are removed when all is successful.
                cingDir = "%s.cing" % entry_code
                tmpFileList = [inputLocalCcpnFile, entry_code, cingDir]
                for f in tmpFileList:
                    if os.path.exists( f ):
                        if os.path.isdir(f):
                            shutil.rmtree(f)
                        else:
                            os.unlink(f)
                        # end if
                    # end if
                # end for
            # end if                
            if conversionCsSucces: # Only use CS if criteria on conversion were met.
                finalPhaseId = PHASE_S
            # end if
        # end if CS

        if filterCcpnAll and convertMrRestraints: # Makes no sense to do when there are no restraints at all.
            nTmessage("  filter")

            f_sub_entry_dir = os.path.join(dir_F, entryCodeChar2and3)
            f_entry_dir = os.path.join(f_sub_entry_dir, entry_code)

            if not os.path.exists(f_entry_dir):
                mkdirs(dir_F)
            # end if
            if not os.path.exists(f_sub_entry_dir):
                mkdirs(f_sub_entry_dir)
            # end if
            os.chdir(f_sub_entry_dir)
            if os.path.exists(entry_code):
                rmtree(entry_code)
            # end if
            if not os.path.exists(entry_code):
                os.mkdir(entry_code)
            # end if
            os.chdir(entry_code)

            inputDir = getDeepByKeysOrAttributes(inputDirByPhase, finalPhaseId)
            if not inputDir:
                nTerror("Failed to get prep stage dir for phase: [%s]" % finalPhaseId)
                return True
            # end if
            fn = "%s.tgz" % entry_code
            inputCcpnFile = os.path.join(inputDir, fn)
            if not os.path.exists( inputCcpnFile):
                nTerror("Failed to find input: %s" % inputCcpnFile)
                return True
            # end if
            nTmessage("         -1- assign")
            filterAssignSucces = 1
            log_file = "%s_FC_assign.log" % entry_code
            fcScript = os.path.join(cingDirScripts, 'FC', 'utils.py')
            outputCcpnFile = "%s_assign.tgz" % entry_code

            # Will save a copy to disk as well.
            convertProgram = ExecuteProgram("python -u %s" % fcScript, redirectOutputToFile=log_file)
#                nTmessage("==> Running Wim Vranken's FormatConverter from script %s" % fcScript)
            exitCode = convertProgram("%s fcProcessEntry %s %s swapCheck" % (entry_code, inputCcpnFile, outputCcpnFile))
            if exitCode:
                nTerror("Failed convertProgram with exit code: %s" % str(exitCode))
                return True
            # end if
            analysisResultTuple = analyzeCingLog(log_file)
            if not analysisResultTuple:
                nTerror("Failed to analyze log file: %s" % log_file)
                return True
            # end if
            timeTaken, entryCrashed, nr_error, nr_warning, nr_message, nr_debug = analysisResultTuple
            if entryCrashed or (nr_error > self.MAX_ERROR_COUNT_FC_LOG):
                nTmessage("Found %s/%s timeTaken/entryCrashed and %d/%d/%d/%d error,warning,message, and debug lines." % (
                    timeTaken, entryCrashed, nr_error, nr_warning, nr_message, nr_debug) )
                nTmessage("Found %s errors in prep phase F -1- assign please check: %s" % (nr_error, entry_code))
                resultList = []
                status = grep(log_file, 'ERROR', resultList=resultList, doQuiet=True, caseSensitive=False)
                if status == 0:
                    nTerror("%s found errors in log file; aborting." % entry_code)
                    nTmessage('\n'.join(resultList))
                # end if
                filterAssignSucces = 0
            # end if
            if not os.path.exists(outputCcpnFile):
                nTerror("%s found no output ccpn file %s" % (entry_code, outputCcpnFile))
                filterAssignSucces = 0
            # end if
            if filterAssignSucces: # Only use filtering if successful but do continue if failed just skip this.
                finalPhaseId = PHASE_F
            # end if
        # end filterCcpnAll
        nTmessage("Before copyToInputDir")
        if copyToInputDir:
            if not finalPhaseId:
                nTerror("Failed to finish any prep stage.")
                return True
            # end if
            if finalPhaseId not in phaseIdList:
                nTerror("Failed to finish valid prep stage: [%s]" % finalPhaseId)
                return True
            # end if
            finalInputDir = getDeepByKeysOrAttributes(inputDirByPhase, finalPhaseId)
            if not finalInputDir:
                nTerror("Failed to get prep stage dir: [%s]" % finalInputDir)
                return True
            # end if
            fn = "%s.tgz" % entry_code
            fnDst = fn
            if finalPhaseId == PHASE_F:
                fn = "%s_assign.tgz" % entry_code
            # end if
            finalInputTgz = os.path.join(finalInputDir, fn)
            if not os.path.exists(finalInputTgz):
                nTerror("final input tgz missing: %s" % finalInputTgz)
                return True
            # end if
            dst = os.path.join(self.results_dir, INPUT_STR, entryCodeChar2and3)
            if not os.path.exists(dst):
                os.mkdir(dst)
            # end if
            fullDst = os.path.join(dst, fnDst)
            if os.path.exists(fullDst):
                os.remove(fullDst)
            # end if
#            os.link(finalInputTgz, fullDst) # Will use less resources but will be expanded when copied between resources.
            disk.copy(finalInputTgz, fullDst)
            nTmessage("Copied input %s to: %s" % (finalInputTgz, fullDst)) # should be a debug statement.
        else:
            nTwarning("Did not copy input %s" % finalInputTgz)
        # end else
        if 0: # DEFAULT: 0
            self.entry_list_todo = [ entry_code ]
            self.runCing()
        # end if
        nTmessage("Done prepareEntry with %s" % entry_code)
    # end def


    def runCing(self):
        """
        On self.entry_list_todo.
        Return True on error.
        """
        nTmessage("Starting runCing")
        if 0: # DEFAULT 0
            nTmessage("Going to use non-default entry_list_todo in runCing")
#            self.entry_list_todo = readLinesFromFile('/Users/jd/NRG/lists/bmrbPdbEntryList.csv')
            self.entry_list_todo = "1brv 1hkt 1mo7 1mo8 1ozi 1p9j 1pd7 1qjt 1vj6 1y7n 2fws 2fwu 2jsx".split()
            self.entry_list_todo = NTlist( *self.entry_list_todo )
            if False:
                if self.searchPdbEntries():
                    nTerror("Failed to searchPdbEntries")
                    return True
                # end if
            # end if
        # end if
        if not self.entry_list_todo:
            nTmessage("Skipping runCing since no entries present in self.entry_list_todo")
            return
        # end if        
        entryListFileName = "entry_list_todo.csv"
        writeTextToFile(entryListFileName, toCsv(self.entry_list_todo))

        pythonScriptFileName = os.path.join(cingDirScripts, 'validateEntry.py')
        inputDir = 'file://' + self.results_dir + '/' + INPUT_STR
        outputDir = self.results_dir
        storeCING2db = "1"          # DEFAULT: '1' All arguments need to be strings.
        filterTopViolations = '1'   # DEFAULT: '1'
        filterVasco = '1'           # DEFAULT: '1'
        singleCoreOperation = '1'   # DEFAULT: '1'
        # Tune this to:
#            verbosity         inputDir             outputDir
#            pdbConvention     restraintsConvention archiveType         projectType
#            storeCING2db      ranges               filterTopViolations filterVasco
#            singleCoreOperation
        extraArgList = ( str(cing.verbosity), inputDir, outputDir,
                         '.', '.', ARCHIVE_TYPE_BY_CH23, PROJECT_TYPE_CCPN,
                         storeCING2db, CV_RANGES_STR, filterTopViolations, filterVasco, singleCoreOperation)

        if doScriptOnEntryList(pythonScriptFileName,
                            entryListFileName,
                            self.results_dir,
                            processes_max=self.processes_max,
                            max_time_to_wait=self.max_time_to_wait,
                            max_entries_todo=self.max_entries_todo,
                            extraArgList=extraArgList):
            nTerror("Failed to doScriptOnEntryList")
            return True
        # end if
    # end def runCing.

    def postProcessAfterVc(self):
        """Return True on error.
        TODO: embed.
        """

        nTmessage("Starting postProcessAfterVc")
        self.entry_list_nmr = readLinesFromFile(os.path.join(self.results_dir, 'entry_list_nmr.csv'))
        self.entry_list_done = readLinesFromFile(os.path.join(self.results_dir, 'entry_list_done.csv'))
        self.entry_list_todo = NTlist()
        self.entry_list_todo.addList(self.entry_list_nmr)
        self.entry_list_todo = self.entry_list_todo.difference(self.entry_list_done)
        if 1: # Default 1 for now.
            nTmessage("Going to use non-default entry_list_todo in postProcessAfterVc")
            self.entry_list_todo = readLinesFromFile(os.path.join(self.results_dir, 'entry_list_good_tgz_after_7.csv'))
#            self.entry_list_todo = '1brv 9pcy'.split()
            self.entry_list_todo = NTlist( *self.entry_list_todo )
        # end if
        nTmessage("Found entries in NMR          : %d" % len(self.entry_list_nmr))
        nTmessage("Found entries in %s done: %d" % (self.results_base, len(self.entry_list_done)))
        nTmessage("Found entries in %s todo: %d" % (self.results_base, len(self.entry_list_todo)))

        for entry_code in self.entry_list_todo:
            self.postProcessEntryAfterVc(entry_code)
        # end for
        nTmessage("Done")
    # end def



    def createToposTokens(self, jobId = TEST_CING_STR):
        """Return True on error.
        """
        tokenListFileName = os.path.join(self.results_dir, 'token_list_todo.txt')        
        # Sync below code with validateEntry#main
#        inputUrl = 'http://nmr.cmbi.ru.nl/NRG-CING/input' # NB cmbi.umcn.nl domain is not available inside cmbi weird.
        inputUrl = 'ssh://jurgenfd@gb-ui-kun.els.sara.nl:/home/jurgenfd/D/%s/input' % self.results_base
#        inputUrl = 'http://dodos.dyndns.org/NRG-CING/input' # NB cmbi.umcn.nl domain is not available inside cmbi weird.
#        outputUrl = 'jd@nmr.cmbi.umcn.nl:/Library/WebServer/Documents/NRG-CING'
#        outputUrl = 'jd@dodos.dyndns.org:/Library/WebServer/Documents/NRG-CING'
        outputUrl = 'ssh://jurgenfd@gb-ui-kun.els.sara.nl:/home/jurgenfd/D/' + self.results_base
#
        storeCING2db = 0
        ranges = CV_RANGES_STR
        filterTopViolations = 1
        filterVasco = 1

        extraArgListTxt = """
            %s %s %s
            . . %s %s
            %s %s %s %s
        """ % ( cing.verbosity,  inputUrl, outputUrl,
                ARCHIVE_TYPE_BY_CH23, PROJECT_TYPE_CCPN,
                storeCING2db, ranges, filterTopViolations, filterVasco )
        extraArgListStr = ' '.join( extraArgListTxt.split())


        nTdebug("tokenListFileName:       %s" % tokenListFileName)        

        nTmessage("Starting createToposTokens with extra params: [%s]" % extraArgListStr)
        self.entry_list_nmr = readLinesFromFile(os.path.join(self.results_dir, 'entry_list_nmr.csv'))
        self.entry_list_done = readLinesFromFile(os.path.join(self.results_dir, 'entry_list_done.csv'))
        self.entry_list_todo = NTlist()
        self.entry_list_todo.addList(self.entry_list_nmr)
        self.entry_list_todo = self.entry_list_todo.difference(self.entry_list_done)
        if True: # DEFAULT: True
            self.entry_list_todo = readLinesFromFile(os.path.join(self.results_dir, 'entry_list_nmr_random_8.csv'))
#            self.entry_list_todo = self.entry_list_todo[:19]
#            self.entry_list_todo = "1brv".split() # Or other 10 residue entries:  1n6t 1p9f 1idv 1kuw 1n9u 1hff  1r4h
            # invalids 1nxn 1gac 1t5n
            self.entry_list_todo = NTlist( *self.entry_list_todo )
        # end if

        nTmessage("Found entries in NMR          : %d" % len(self.entry_list_nmr))
        nTmessage("Found entries in %s done: %d" % (self.results_base, len(self.entry_list_done)))
        nTmessage("Found entries in %s todo: %d" % (self.results_base, len(self.entry_list_todo)))

#        nTdebug("Quitting for now.")
#        return True

        tokenList = []
        for entry_code in self.entry_list_todo:
            tokenStr = ' '.join([jobId, entry_code, extraArgListStr])
            tokenList.append(tokenStr)
        # end for
        tokenListStr = '\n'.join(tokenList)
        nTmessage("Writing tokens to: [%s]" % tokenListFileName)
        writeTextToFile(tokenListFileName, tokenListStr)
    # end def

    def prepare(self):
        "Return True on error."

        nTmessage("Starting prepare using self.entry_list_todo")
        permutationArgumentMap = NTdict() # per permutation hold the entry list.

        for entry_code in self.entry_list_todo:
            convertMmCifCoor = 0
            convertMrRestraints = 0
            convertStarCS = 0
            filterCcpnAll = 0
            if entry_code in self.entry_list_nmr:
                convertMmCifCoor = 1
            # end if
            if entry_code in self.entry_list_nrg_docr:
                convertMrRestraints = 1
            # end if
            if convertMrRestraints:
                convertMmCifCoor = 0
            # end if
            if self.matches_many2one.has_key(entry_code):
                convertStarCS = 1
            # end if
            if convertMrRestraints: # Filter when there are restraints
                filterCcpnAll = 1
            # end if
            if not (convertMmCifCoor or convertMrRestraints):
                nTerror("not (convertMmCifCoor or convertMrRestraints) in prepare. Skipping entry: %s" % entry_code)
                continue
            # end if
            argList = [convertMmCifCoor, convertMrRestraints, convertStarCS, filterCcpnAll]
            argStringList = [ str(x) for x in argList ]
            permutationKey = ' '.join(argStringList) # strings
            if not getDeepByKeysOrAttributes(permutationArgumentMap, permutationKey):
                permutationArgumentMap[permutationKey] = NTlist()
            # end if
            permutationArgumentMap[permutationKey].append(entry_code)
        # end for#
        nTdebug("Found entries in NMR          : %d (entry_list_nmr)"         %  len(self.entry_list_nmr))
        nTdebug("Found entries in NRG DOCR     : %d (entry_list_nrg_docr)"    %  len(self.entry_list_nrg_docr))
        nTdebug("Found entries in              : %d (matches_many2one)"       %  len(self.matches_many2one.keys()))
        nTdebug("Found entries todo            : %d" % len(self.entry_list_todo))

        nTdebug("Permutations:")
        for permutationKey in permutationArgumentMap.keys():
            nTdebug("Keys: %s split to: %s %s %s %s with number of entries %d" % (
                permutationKey, convertMmCifCoor, convertMrRestraints, convertStarCS, 
                filterCcpnAll, len(permutationArgumentMap[permutationKey])))
        # end for
        
        for permutationKey in permutationArgumentMap.keys(): # strings
#            permutationKeyForFileName = re.compile('[ ,\[\]]').sub('', permutationKey)
            permutationKeyForFileName = permutationKey.replace(' ', '')
            extraArgList = permutationKey.split()
            convertMmCifCoor, convertMrRestraints, convertStarCS, filterCcpnAll = extraArgList
            nTmessage("Keys: %s split to: %s %s %s %s with number of entries %d" % (
                    permutationKey, convertMmCifCoor, convertMrRestraints, convertStarCS, 
                    filterCcpnAll, len(permutationArgumentMap[permutationKey])))

#            nTdebug("Quitting for now.")
#            continue

            entryListFileName = "entry_list_todo_prep_perm_%s.csv" % permutationKeyForFileName
            writeTextToFile(entryListFileName, toCsv(permutationArgumentMap[permutationKey]))
            pythonScriptFileName = __file__ # recursive call in fact.
            extraArgList = ['prepare' ] + extraArgList
            if doScriptOnEntryList(pythonScriptFileName,
                                entryListFileName,
                                self.results_dir,
                                processes_max=self.processes_max,
                                max_time_to_wait=6000,
                                extraArgList=extraArgList, # list of strings
                                start_entry_id=0, # DEFAULT: 0.
                                max_entries_todo=self.max_entries_todo,
    #                            max_entries_todo=self.max_entries_todo # DEFAULT
                                ):
                nTerror("In NrgCing#prepare Failed to doScriptOnEntryList")
                return True
            # end if
        # end for
        nTmessage("Done with prepare.")
    # end def

    def storeCING2db(self):
        "Return True on error."

        nTmessage("Starting storeCING2db using self.entry_list_todo.")
#        self.searchPdbEntries()
#        self.getEntryInfo()
        if 0: # DEFAULT: False
            nTmessage("Going to use non-default entry_list_todo in storeCING2db")
#            self.entry_list_todo = '1jo4 1mag 1mic 1msh 1n2y 1ng8 1nt5 2kox'.split()
            self.entry_list_todo = readLinesFromFile('/Users/jd/entry_list_of_interest.csv')
#            self.entry_list_todo = readLinesFromFile(os.path.join(self.results_dir, 'list', 'entry_list_tostore.csv'))
#            self.entry_list_todo = readLinesFromFile(os.path.join('/Users/jd', 'entry_list_to_store.csv'))
            self.entry_list_todo = NTlist( *self.entry_list_todo )
        # end if
        nTmessage("Found entries in %s todo: %d" % (self.results_base, len(self.entry_list_todo)))

        # parameters for doScriptOnEntryList
        cingDirNRG = os.path.join(cingPythonDir, 'cing', 'NRG' )
        pythonScriptFileName = os.path.join(cingDirNRG, 'storeCING2db.py')
        entryListFileName = os.path.join( self.results_dir, 'entry_list_todo.csv')
        writeEntryListToFile(entryListFileName, self.entry_list_todo)
        
#        if not self.isProduction:
#            archive_id=ARCHIVE_DEV_NRG_ID
        extraArgList = (self.archive_id,) # note that for length one tuples the comma is required.

        doScriptOnEntryList(pythonScriptFileName,
                            entryListFileName,
                            self.results_dir,
                            processes_max           = self.processes_max,
                            max_time_to_wait        = 60 * 60, # Largest entries take a bit longer than the initial 6 minutes; 2hyn etc.
                            start_entry_id          = 0,
                            max_entries_todo        = self.max_entries_todo,
                            expectPdbEntryList      = True,
                            shuffleBeforeSelecting  = True,                            
                            extraArgList            = extraArgList)
        nTmessage("Done with storeCING2db.")
    # end def
    
    def forEachStoredEntry(self):
        "Do a manual action on every entry in RDB."
#        f = createPinUp
        f = checkCingLogForErrors
        log_dir = 'log_updateProjectHtml'
        requiresLogFilePresent = True
        maxErrors = 3
#        extraArgList = (self.results_base, )
        extraArgList = (self.results_dir, log_dir, requiresLogFilePresent, maxErrors )
        # NO CHANGES BELOW
        nTmessage("Starting forEachStoredEntry")        
        if 0: # DEFAULT: True
            self.entry_list_todo = getPdbIdList(fromCing=True)
            self.entry_list_todo = NTlist( *self.entry_list_todo )
            if not self.entry_list_todo:
                nTerror("Failed to get any entry from RDB")
                return True
        else:
            self.entry_list_todo = '1brv'.split()
#            self.entry_list_todo = '1brv 2duw'.split()
            entryListFileName = os.path.join(self.results_dir, 'entry_list_toUpdateHtml.csv')
            self.entry_list_todo = readLinesFromFile(entryListFileName)
        # end if            
        nTmessage("Found entries in %s todo: %d" % (self.results_base, len(self.entry_list_todo)))
        # parameters for doScriptOnEntryList
        entryListFileName = os.path.join( self.results_dir, 'entry_list_todo.csv')
        writeEntryListToFile(entryListFileName, self.entry_list_todo)
        doFunctionOnEntryList(f,
                            entryListFileName,
                            processes_max = self.processes_max,
                            max_time_to_wait = 60 * 60, # Largest entries take a bit longer than the initial 6 minutes; 2hyn etc.
                            start_entry_id = 0,
                            max_entries_todo = 9, # DEFAULT: 99999
                            extraArgList = extraArgList)
        nTmessage("Done with forEachStoredEntry.")
    # end def
        
    def forEachStoredEntryRunScript(self):
        "Do full script with output redirection on every entry in RDB."
        pythonScriptFileName = os.path.join(cingDirScripts, 'interactive', 'updateProjectHtml.py')
        extraArgList = ( str(cing.verbosity), )
        # NO CHANGES BELOW
        nTmessage("Starting forEachStoredEntry")        
        if 0: # DEFAULT: True
            self.entry_list_todo = getPdbIdList(fromCing=True)
            self.entry_list_todo = NTlist( *self.entry_list_todo )
            if not self.entry_list_todo:
                nTerror("Failed to get any entry from RDB")
                return True
        else:
#            self.entry_list_todo = '1ahd 1ahl 1akk 1akp 1aml 1apc 1aps 1aq5 1arq 1arr 1ato 1atx 1auu 1ax3 1axh 1ayg'.split()            
#            self.entry_list_todo = '1brv 2duw'.split()
            entryListFileName = os.path.join(self.results_dir, 'entry_list_toUpdateHtml.csv')
            self.entry_list_todo = readLinesFromFile(entryListFileName)
        # end if            
        nTmessage("Found entries in %s todo: %d" % (self.results_base, len(self.entry_list_todo)))
        # parameters for doScriptOnEntryList
        entryListFileName = os.path.join( self.results_dir, 'entry_list_todo.csv')
        writeEntryListToFile(entryListFileName, self.entry_list_todo)
        if doScriptOnEntryList(pythonScriptFileName,
                            entryListFileName,
                            self.results_dir,
                            processes_max = self.processes_max,
                            max_time_to_wait = self.max_time_to_wait,
                            start_entry_id = 0,
                            max_entries_todo = 9, # DEFAULT: 99999                            
                            extraArgList=extraArgList):
            nTerror("Failed to doScriptOnEntryList")
            return True
        # end if                
        nTmessage("Done with forEachStoredEntryRunScript.")
    # end def
        
    def replaceCoordinates(self):
        """
        On self.entry_list_todo.
        Return True on error.
        
        """
        self.entry_list_todo = readLinesFromFile(os.path.join(self.results_dir, 'list', 'entry_list_recoord_nrgcing_shuffled.csv'))
        self.entry_list_todo = self.entry_list_todo[:100]
        entryListFileName = "entry_list_recoord_todo.csv"
        writeTextToFile(entryListFileName, toCsv(self.entry_list_todo))

        pythonScriptFileName = os.path.join(cingDirScripts, 'replaceCoordinates.py')
        nC = getDeepByKeysOrAttributes(self, 'nrgCing' )
        if not nC:
            nC = self
            nTwarning("Check code for replaceCoordinates")        
        inputDir = 'file://' + nC.results_dir + '/' + DATA_STR
        outputDir = self.results_dir
        storeCING2db =          "1" # DEFAULT: '1' All arguments need to be strings.
        filterTopViolations =   '0' # DEFAULT: '1'
        filterVasco =           '0'
        singleCoreOperation =   '1'
        # RECOORD coordinates
        inPathTemplate          = "/Library/WebServer/Documents/recoord_cns_w/web/%s_cns_w.pdb"
        convention              = XPLOR
        
        extraArgList = ( str(cing.verbosity), inputDir, outputDir,
                         '.', '.', ARCHIVE_TYPE_BY_CH23_BY_ENTRY, PROJECT_TYPE_CING,
                         storeCING2db, CV_RANGES_STR, filterTopViolations, filterVasco, singleCoreOperation,
                         inPathTemplate, self.archive_id, convention )

        if doScriptOnEntryList(pythonScriptFileName,
                            entryListFileName,
                            self.results_dir,
                            processes_max = self.processes_max,
                            max_time_to_wait = self.max_time_to_wait,
                            start_entry_id = 0,
                            max_entries_todo = 90,                            
                            extraArgList=extraArgList):
            nTerror("Failed to doScriptOnEntryList")
            return True
        # end if
    # end def        
    
    def refine(self):  # pylint: disable=R0201
        """
        Needs to be overriden by e.g. nmr_redo.
        Return True on error.
        """
        return True
    # end def
    
    def findMissingEntries(self):
        'Return True if entries are missing in pdbj wrt rcsb-pdb.'
        # BAD
        badEntryNtList = self.entry_list_bad_overall
        NTmessage("Found %s bad entries count: %s (expected to be missing)." % (self.results_base, len(badEntryNtList)))
        # GOOD
        host = 'localhost'
        if False: # DEFAULT False
            host = 'nmr.cmbi.umcn.nl'
        # end if
        entryList = getPdbIdList(fromCing=True, host=host)
        if not entryList:
            nTerror("Failed to get any entry from NRG-CING RDB")
            return True
        # end if
        NTmessage("Found %s entries count: %s" % (self.results_base, len(entryList)))
        # PDB
        pdbRcsbEntryList = getPdbEntries(onlyNmr=True)
        NTmessage("Found RCSB PDB entries count: %s" % len(pdbRcsbEntryList))
        
        
        pdbRcsbEntryNtList = NTlist(*pdbRcsbEntryList)
        entryNtList = NTlist(*entryList)
        missingEntryNtList = pdbRcsbEntryNtList.difference(entryNtList)
        missingEntryNtList = missingEntryNtList.difference(badEntryNtList)
        NTmessage("Found %s missing entries count: %s %s" % (self.results_base, len(missingEntryNtList), missingEntryNtList))
        pdbRcsbMissingEntryNtList = entryNtList.difference(pdbRcsbEntryNtList)
        NTmessage("Found RCSB-PDB missing entries count: %s %s" % (len(pdbRcsbMissingEntryNtList), pdbRcsbMissingEntryNtList))
    # end def        
    def _getJumpBoxHtml(self):
        return '''
            <div style="width: 25em">
            <FORM method="GET" action="../../cgi-bin/cingRdbServer/DataTablesServer.py" class="display">
            Search by PDB ID (e.g. 9pcy):
            <INPUT type="hidden" name="database" value="pdb" align="left">
            <INPUT type="text" size="4" name="id" value="" title="Please provide the PDB identifier to obtain the validation report">
            <INPUT type="submit" name="button" value="Go">                        
            </FORM>
            </div>
        '''
    # end def                
# end class.

def runNrgCing( useClass = NrgCing,
            max_entries_todo = 40 # DEFAULT: 40 # for weekly update. Further customize for manual work in __init__
                 ):
    """
    Additional modes I see:
        batchUpdate        Run validation checks to web site.
        prepare            Only moves the entries through prep stages.
    """
    cing.verbosity = verbosityDebug
    useTopos = 0           # DEFAULT: 0
    processes_max = None # Default None to be determined by os.

    nTmessage(header)
    nTmessage(getStartMessage())
    ## Initialize the project
    uClass = useClass( max_entries_todo=max_entries_todo, useTopos=useTopos, processes_max = processes_max )
    uClass.setup()
    
    destination = sys.argv[1]
    hasPdbId = False
    entry_code = '.'
    if is_pdb_code(destination): # needs to be first argument if this main is to be used by doScriptOnEntryList.
        entry_code = destination
        hasPdbId = True
        destination = sys.argv[2]
        uClass.entry_list_todo = [ entry_code ]
    # end if        
    
    uClass.entry_list_todo = NTlist( *uClass.entry_list_todo )
        
    # end if
    startArgListOther = 2
    if hasPdbId:
        startArgListOther = 3
    # end if
    argListOther = []
    if len(sys.argv) > startArgListOther:
        argListOther = sys.argv[startArgListOther:]
    # end if
    nTmessage('\nGoing to destination: %s with(out) entry_code %s with extra arguments %s' % (destination, entry_code, str(argListOther)))

    try:
        if destination == 'prepare':
            convertMmCifCoor = 1 # always present so nicest fall back.
            convertMrRestraints = 0
            convertStarCS = 0
            filterCcpnAll = 0
            doInteractive=not isProduction
            if len(argListOther) > 0:
                convertMmCifCoor = int(argListOther[0])
                if len(argListOther) > 1:
                    convertMrRestraints = int(argListOther[1])
                    if len(argListOther) > 2:
                        convertStarCS = int(argListOther[2])
                        if len(argListOther) > 3:
                            filterCcpnAll = int(argListOther[3])
                        # end if
                    # end if
                # end if
            # end if
            if uClass.prepareEntry(entry_code, doInteractive=doInteractive, 
                                   convertMmCifCoor=convertMmCifCoor, convertMrRestraints=convertMrRestraints, 
                                   convertStarCS=convertStarCS, filterCcpnAll=filterCcpnAll):
                nTerror(FAILURE_PREP_STR)
            # end if
        elif destination == 'runCing':
            if uClass.runCing():
                nTerror("Failed to runCing")
            # end if
        elif destination == 'postProcessAfterVc':
            if uClass.postProcessAfterVc():
                nTerror("Failed to postProcessAfterVc")
            # end if
        elif destination == 'postProcessEntryAfterVc':
            if uClass.postProcessEntryAfterVc(entry_code):
                nTerror("Failed to postProcessEntryAfterVc")
            # end if
        elif destination == 'createToposTokens':
            if uClass.createToposTokens(jobId=VALIDATE_ENTRY_NRG_STR):
#            if uClass.createToposTokens():
                nTerror("Failed to createToposTokens")
            # end if
        elif destination == 'storeCING2db':
            if uClass.storeCING2db():
                nTerror("Failed to storeCING2db")
            # end if
        elif destination == 'getEntryInfo':
            if uClass.getEntryInfo():
                nTerror("Failed to getEntryInfo")                
            # end if
        elif destination == 'searchPdbEntries':
            if uClass.searchPdbEntries():
                nTerror("Failed to searchPdbEntries")                
            # end if
        # NMR_REDO specific
        elif destination == 'refine':
            if uClass.refine(): # in nmr_redo
                nTerror("Failed to refine")
            # end if
        elif destination == 'replaceCoordinates':
            if uClass.replaceCoordinates(): # in recoord
                nTerror("Failed to replaceCoordinates")
            # end if
        elif destination == 'findMissingEntries':
            if uClass.findMissingEntries(): # in nmr_redo
                nTerror("Failed to findMissingEntries")
            # end if
        elif destination == 'updateWeekly':
            if uClass.updateWeekly():
                nTerror("Failed to updateWeekly")
            # end if
        elif destination == 'runWeekly':
            if uClass.runWeekly():
                nTerror("Failed to runWeekly")
            # end if            
        elif destination == 'updateFrontPages':
            if uClass.updateFrontPages():
                nTerror("Failed to updateFrontPages")                
            # end if
        elif destination == 'updateCsvDumps':
            if uClass.updateCsvDumps(): 
                nTerror("Failed to updateCsvDumps")                
            # end if
        elif destination == 'updateFrontPagePlots':
            if uClass.updateFrontPagePlots(): 
                nTerror("Failed to updateFrontPagePlots")                
            # end if
        elif destination == 'updateFrontPagePrettyPlots':
            if uClass.updateFrontPagePrettyPlots(): 
                nTerror("Failed to updateFrontPagePrettyPlots")                
            # end if
        elif destination == 'forEachStoredEntry':
            if uClass.forEachStoredEntry():
                nTerror("Failed to forEachStoredEntry")                
            # end if
        elif destination == 'forEachStoredEntryRunScript':
            if uClass.forEachStoredEntryRunScript():
                nTerror("Failed to forEachStoredEntryRunScript")                
            # end if
        elif destination == 'writeWhyNotEntries':
            if uClass.writeWhyNotEntries():
                nTerror("Failed to writeWhyNotEntries")                
            # end if
        else:
            nTerror("Unknown destination: %s" % destination)
        # end if
    except:
        nTtracebackError()
    finally:
        nTmessage(getStopMessage(cing.starttime))
    # end try
# end def    


if __name__ == '__main__':
    runNrgCing( max_entries_todo = 40 ) # DEFAULT: 40