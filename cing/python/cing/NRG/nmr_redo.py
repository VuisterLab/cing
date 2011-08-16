#!/usr/bin/env python

"""
This script will use NRG-CING files to generate new structures for existing NMR PDB entries.

Execute like NrgCing, e.g.

$CINGROOT/python/cing/NRG/nmr_redo.py refine
$CINGROOT/python/cing/NRG/nmr_redo.py getEntryInfo
$CINGROOT/python/cing/NRG/nmr_redo.py 1brv storeCING2db
"""

from cing import cingDirScripts
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.helper import * #@UnusedWildImport
from cing.NRG import ARCHIVE_NMR_REDO_ID
from cing.NRG.nrgCing import NrgCing
from cing.NRG.nrgCing import runNrgCing
from cing.NRG.settings import * #@UnusedWildImport
from cing.NRG.validateEntryForCasp import ARCHIVE_TYPE_BY_CH23_BY_ENTRY
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList
from cing.Scripts.validateEntry import PROJECT_TYPE_CING

class NmrRedo(NrgCing):
    """Main class for preparing and running NMR recalculations."""
    def __init__(self,
                 useTopos=False,
                 getTodoList=True,
                 max_entries_todo=1,
                 max_time_to_wait=86400, 
                 # one day. 2p80 took the longest: 5.2 hours. 
#                 But <Molecule "2ku1" (C:7,R:1659,A:36876,M:30)> is taking longer. 2ku2 is taking over 12 hrs now.
                 processes_max=None,
                 prepareInput=False,
                 writeWhyNot=True,
                 writeTheManyFiles=False,
                 updateIndices=True,
#                 isProduction=True
                ):
        kwds = NTdict( 
                 useTopos=useTopos, # There must be an introspection possible for this.
                 getTodoList=getTodoList,
                 max_entries_todo=max_entries_todo,
                 max_time_to_wait=max_time_to_wait, # one day. 2p80 took the longest: 5.2 hours. 
#                 But <Molecule "2ku1" (C:7,R:1659,A:36876,M:30)> is taking longer. 2ku2 is taking over 12 hrs now.
                 processes_max=processes_max,
                 prepareInput=prepareInput,
                 writeWhyNot=writeWhyNot,
                 writeTheManyFiles=writeTheManyFiles,
                 updateIndices=updateIndices,
#                 isProduction=isProduction,
)
        kwds = kwds.toDict()
        NrgCing.__init__( self, **kwds ) # Steal most from super class. 
        self.results_base = results_base_redo


        self.entry_to_delete_count_max = 0 # can be as many as fail every time.
        self.usedCcpnInput = 0  # For NMR_REDO it is not from the start.
        self.validateEntryExternalDone = 0
        self.nrgCing = NrgCing() # Use as little as possible thru this inconvenience variable.
                
        self.archive_id = ARCHIVE_NMR_REDO_ID        
        self.validateEntryExternalDone = False # DEFAULT: True 
#        in the future and then it won't change but for NrgCing it is True from the start.
        self.updateDerivedResourceSettings() # The paths previously initialized in NrgCing. Will also chdir.
        
        if 1:
            self.entry_list_todo = NTlist() 
#            self.entry_list_todo += "1brv 1dum".split()
            self.entry_list_todo += "1brv".split()
        if 0: # DEFAULT: 0
            nTmessage("Going to use specific entry_list_todo in prepare")
#            self.entry_list_todo = "1brv".split()
#            self.entry_list_todo = readLinesFromFile('/Users/jd/NRG/lists/bmrbPdbEntryList.csv')
#            self.entry_list_todo = NTlist( *self.entry_list_todo )
#            self.entry_list_todo = readLinesFromFile(os.path.join(self.results_dir, 'entry_list_nmr_random_1-500.csv'))
#            self.entry_list_todo = readLinesFromFile(os.path.join(self.results_dir, 'entry_list_prep_todo.csv'))
#            self.entry_list_nmr = deepcopy(self.entry_list_todo)
#            self.entry_list_nrg_docr = deepcopy(self.entry_list_todo)
        if 0: # DEFAULT: False
            self.searchPdbEntries()
            self.entry_list_todo = readLinesFromFile(os.path.join(self.results_dir, 'entry_list_prep_todo.csv'))
            self.entry_list_todo = NTlist( *self.entry_list_todo )
    # end def  
        
    
    def refine(self):
        """On self.entry_list_todo.
        Return True on error.
        """
        entryListFileName = "entry_list_todo.csv"
        writeTextToFile(entryListFileName, toCsv(self.entry_list_todo))

        pythonScriptFileName = os.path.join(cingDirScripts, 'refineEntry.py')
#        inputDir = 'file://' + self.nrgCing.results_dir + '/' + self.inputDir # NB input is from NrgCing.
        inputDir = 'file://' + self.nrgCing.results_dir + '/' + DATA_STR
        outputDir = self.results_dir
        storeCING2db = "1" # DEFAULT: '1' All arguments need to be strings.
        filterTopViolations = '0' # DEFAULT: '1'
        filterVasco = '0'
        singleCoreOperation = '1'
        # Tune this to:
#            verbosity         inputDir             outputDir
#            pdbConvention     restraintsConvention archiveType         projectType
#            storeCING2db      ranges               filterTopViolations filterVasco
#            singleCoreOperation

        extraArgList = ( str(cing.verbosity), inputDir, outputDir,
                         '.', '.', ARCHIVE_TYPE_BY_CH23_BY_ENTRY, PROJECT_TYPE_CING,
                         storeCING2db, CV_RANGES_STR, filterTopViolations, filterVasco, singleCoreOperation)

        if doScriptOnEntryList(pythonScriptFileName,
                            entryListFileName,
                            self.results_dir,
                            processes_max = self.processes_max,
                            delay_between_submitting_jobs = 5, # why is this so long? because of time outs at tang?
                            max_time_to_wait = self.max_time_to_wait,
                            start_entry_id = 0,
                            max_entries_todo = self.max_entries_todo,                            
                            extraArgList=extraArgList):
            nTerror("Failed to doScriptOnEntryList")
            return True
        # end if
    # end def        
# end class.

if __name__ == '__main__':
    max_entries_todo = 1
    runNrgCing( useClass = NmrRedo, max_entries_todo = max_entries_todo )
