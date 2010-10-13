# python -u $CINGROOT/python/cing/NRG/doAnnotateCaspNmrLoop.py

from cing import cingPythonDir
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG.CaspNmrMassageCcpnProject import baseDir
from cing.NRG.PDBEntryLists import writeEntryListToFile
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList

cing.verbosity = cing.verbosityDebug

cingDirNRG = os.path.join(cingPythonDir, 'cing', 'NRG' )
pythonScriptFileName = os.path.join(cingDirNRG, 'doAnnotateCaspNmr.py')
if False:
    entryListFileName = os.path.join(baseDir, 'list', 'entry_list_all.csv')
#    entryListFileName = os.path.join(startDir, 'list', 'entry_list_redo.csv')
else:
    entryListFileName = os.path.join(baseDir, 'list', 'entry_list_single.csv')
#    entryList = 'T0538Org T0538TS001 T0538TS039'.split()
#    entryList = 'T0538Org'.split()
#    entryList = 'T0538TS001 T0538TS002 T0538TS257'.split()
    entryList = 'T0538TS328'.split()
    writeEntryListToFile(entryListFileName, entryList)
extraArgList = ()

doScriptOnEntryList(pythonScriptFileName,
                    entryListFileName,
                    baseDir,
                    processes_max = 2,
                    delay_between_submitting_jobs = 2,
                    max_time_to_wait = 6000,
                    START_ENTRY_ID = 0,
                    MAX_ENTRIES_TODO = 100,
                    expectPdbEntryList = False,
                    extraArgList = extraArgList)
