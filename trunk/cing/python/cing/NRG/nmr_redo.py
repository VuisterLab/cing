#!/usr/bin/env python

"""
This script will use NRG-CING files to generate new structures for existing PDB entries.

Execute like nrgCing, e.g.

$CINGROOT/python/cing/NRG/nmr_redo.py refine
$CINGROOT/python/cing/NRG/nmr_redo.py getEntryInfo
$CINGROOT/python/cing/NRG/nmr_redo.py 1brv storeCING2db
"""

from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.helper import * #@UnusedWildImport
from cing.NRG.nrgCing import * #@UnusedWildImport
from cing.NRG.settings import * #@UnusedWildImport
from cing.Scripts.validateEntry import * #@UnusedWildImport

class NmrRedo(nrgCing):
    """Main class for preparing and running NMR recalculations."""
    def __init__(self,
                 useTopos=False,
                 getTodoList=True,
                 max_entries_todo=1,
                 max_time_to_wait=86400, # one day. 2p80 took the longest: 5.2 hours. But <Molecule "2ku1" (C:7,R:1659,A:36876,M:30)> is taking longer. 2ku2 is taking over 12 hrs now.
                 processes_max=None,
                 prepareInput=False,
                 writeWhyNot=True,
                 writeTheManyFiles=False,
                 updateIndices=True,
                 isProduction=True
                ):
        kwds = NTdict( useTopos=useTopos, # There must be an introspection possible for this.
                 getTodoList=getTodoList,
                 max_entries_todo=max_entries_todo,
                 max_time_to_wait=max_time_to_wait, # one day. 2p80 took the longest: 5.2 hours. But <Molecule "2ku1" (C:7,R:1659,A:36876,M:30)> is taking longer. 2ku2 is taking over 12 hrs now.
                 processes_max=processes_max,
                 prepareInput=prepareInput,
                 writeWhyNot=writeWhyNot,
                 writeTheManyFiles=writeTheManyFiles,
                 updateIndices=updateIndices,
                 isProduction=isProduction,
)
        kwds = kwds.toDict()
        nrgCing.__init__( self, **kwds ) # Steal most from super class. @UndefinedVariable for init??? JFD; doesn't understand.
        self.results_base = results_base_redo


        self.ENTRY_TO_DELETE_COUNT_MAX = 0 # can be as many as fail every time.
        self.usedCcpnInput = 0  # For NMR_REDO it is not from the start.
        self.validateEntryExternalDone = 0
        self.nrgCing = nrgCing() # Use as little as possible thru this convenience variable.
                
        self.archive_id = ARCHIVE_NMR_REDO_ID        
        self.validateEntryExternalDone = False # DEFAULT: True in the future and then it won't chainge but for nrgCing it is True from the start.
        self.entry_list_possible = self.getPossibleEntryList()

        self.updateDerivedResourceSettings() # The paths previously initialized in nrgCing. Will also chdir.
        
        if 0:
            self.entry_list_todo = NTlist() 
            self.entry_list_todo += "1brv 1dum".split()
        if 0: # DEFAULT: 0
            NTmessage("Going to use specific entry_list_todo in prepare")
#            self.entry_list_todo = "1a24 1a4d 1afp 1ai0 1b4y 1brv 1bus 1c2n 1cjg 1d3z 1hue 1ieh 1iv6 1jwe 1kr8 2cka 2fws 2hgh 2jmx 2k0e 2kib 2knr 2kz0 2rop".split()
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
        
    def getPossibleEntryList(self):
        self.entry_list_possible = NTlist() # NEW: monomeric, and beyond.
        self.entry_list_possible += '1brv 1dum'.split()
        return self.entry_list_possible
    # end def   
    
    def refine(self):
        """On self.entry_list_todo.
        Return True on error.
        """
        entryListFileName = "entry_list_todo.csv"
        writeTextToFile(entryListFileName, toCsv(self.entry_list_todo))

        pythonScriptFileName = os.path.join(cingDirScripts, 'refineEntry.py')
#        inputDir = 'file://' + self.nrgCing.results_dir + '/' + self.inputDir # NB input is from nrgCing.
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
                            processes_max=self.processes_max,
                            delay_between_submitting_jobs=5, # why is this so long? because of time outs at tang?
                            max_time_to_wait=self.max_time_to_wait,
                            MAX_ENTRIES_TODO=self.max_entries_todo,
                            extraArgList=extraArgList):
            NTerror("Failed to doScriptOnEntryList")
            return True
        # end if
    # end def        
# end class.

if __name__ == '__main__':
    runNrgCing( useClass = NmrRedo )
