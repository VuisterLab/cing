#!/usr/bin/env python

"""
This script will use NRG-CING files to generate new structures for existing PDB entries.

Execute like:

$CINGROOT/python/cing/NMR_REDO/nmr_redo.py [entry_code] [refineEntry store2db]
"""

from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.helper import * #@UnusedWildImport
from cing.NRG.nrgCing import * #@UnusedWildImport
from cing.NRG.settings import * #@UnusedWildImport

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
        # Dir as base in which all info and scripts like this one resides
        self.base_dir = os.path.join(cingPythonCingDir, "NMR_REDO")
        self.results_base = results_base_redo
        self.results_dir = os.path.join(self.D, self.results_base)
        self.data_dir = os.path.join(self.results_dir, DATA_STR)

        # The csv file name for indexing pdb
        self.index_pdb_file_name = self.results_dir + "/index/index_pdb.csv"
        self.why_not_db_comments_dir = None
        self.why_not_db_raw_dir = None
        self.why_not_db_comments_file = None

        os.chdir(self.results_dir)
        self.ENTRY_TO_DELETE_COUNT_MAX = 33 # can be as many as fail every time.
        self.nrgCing = nrgCing()
        
    def refine(self):
        """On self.entry_list_todo.
        Return True on error.
        """
        NTdebug("Now in %s" % getCallerName())
        if 0: # DEFAULT 0
            NTmessage("Going to use non-default entry_list_todo in runCing")
#            self.entry_list_todo = readLinesFromFile('/Users/jd/NRG/lists/bmrbPdbEntryList.csv')
            self.entry_list_todo = "1brv 1hkt 1mo7 1mo8 1ozi 1p9j 1pd7 1qjt 1vj6 1y7n 2fws 2fwu 2jsx".split()
            self.entry_list_todo = NTlist( *self.entry_list_todo )

            if self.searchPdbEntries():
                NTerror("Failed to searchPdbEntries")
                return True

        entryListFileName = "entry_list_todo.csv"
        writeTextToFile(entryListFileName, toCsv(self.entry_list_todo))

        pythonScriptFileName = os.path.join(cingDirScripts, 'refineEntry.py')
        inputDir = 'file://' + self.nrgCing.results_dir + '/' + self.inputDir # NB input is from nrgCing.
        outputDir = self.results_dir
        storeCING2db = "1" # DEFAULT: '1' All arguments need to be strings.
        filterTopViolations = '1' # DEFAULT: '1'
        filterVasco = '1'
        # Tune this to:
#            verbosity         inputDir             outputDir
#            pdbConvention     restraintsConvention archiveType         projectType
#            storeCING2db      ranges               filterTopViolations filterVasco
        extraArgList = ( str(cing.verbosity), inputDir, outputDir,
                         '.', '.', ARCHIVE_TYPE_BY_CH23, PROJECT_TYPE_CCPN,
                         storeCING2db, CV_RANGES_STR, filterTopViolations, filterVasco)

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
    # end def runCing.
    
# end class.


def runNmrRedo():
    """
    Additional modes I see:
        batchUpdate        Run validation checks to NRG-CING web site.
        prepare            Only moves the entries through prep stages.
    """
    cing.verbosity = verbosityDebug
    max_entries_todo = 40  # DEFAULT: 40
    useTopos = 0           # DEFAULT: 0
    processes_max = None # Default None to be determined by os.

    NTmessage(header)
    NTmessage(getStartMessage())
    m = NmrRedo(isProduction=isProduction, max_entries_todo=max_entries_todo, useTopos=useTopos, processes_max = processes_max )

    destination = sys.argv[1]
    hasPdbId = False
    entry_code = '.'
    if is_pdb_code(destination): # needs to be first argument if this main is to be used by doScriptOnEntryList.
        entry_code = destination
        hasPdbId = True
        destination = sys.argv[2]
        m.entry_list_todo = [ entry_code ]
    # end if
    startArgListOther = 2
    if hasPdbId:
        startArgListOther = 3
    argListOther = []
    if len(sys.argv) > startArgListOther:
        argListOther = sys.argv[startArgListOther:]
    NTmessage('\nGoing to destination: %s with(out) on entry_code %s with extra arguments %s' % (destination, entry_code, str(argListOther)))

    try:
        if destination == 'refine':
            if m.refine(): # in nmr_redo
                NTerror("Failed to refine")
        else:
            NTerror("Unknown destination: %s" % destination)
        # end if        
    except:
        NTtracebackError()
    finally:
        NTmessage(getStopMessage(cing.starttime))
    # end try
# end def    


if __name__ == '__main__':
    runNmrRedo() # Customize in initializer for nmr_redo specific settings.
