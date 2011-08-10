# python -u $CINGROOT/python/cing/NRG/validateForCASP_NMR.py
from cing import cingPythonDir
from cing.NRG import CASP_NMR_BASE_NAME
from cing.NRG.PDBEntryLists import writeEntryListToFile
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList
from cing.Scripts.validateEntry import ARCHIVE_TYPE_BY_CH23_BY_ENTRY
from cing.Scripts.validateEntry import PROJECT_TYPE_CCPN
import cing
import os

cing.verbosity = cing.verbosityDebug
#cing.verbosity = cing.verbosityDefault

# parameters for doScriptOnEntryList
startDir = '/Library/WebServer/Documents/%s' % CASP_NMR_BASE_NAME
cingDirNRG = os.path.join(cingPythonDir, 'cing', 'NRG' )
pythonScriptFileName = os.path.join(cingDirNRG, 'validateEntryForCasp.py')
#pythonScriptFileName = os.path.join(cingDirNRG, 'storeCASDCING2db.py')

if True:
    entryListFileName = os.path.join(startDir, 'list', 'entry_list_all.csv')
#    entryListFileName = os.path.join(startDir, 'list', 'entry_list_all_org.csv')
#    entryListFileName = os.path.join(startDir, 'list', 'entry_list_redo.csv')
else:
    entryListFileName = os.path.join(startDir, 'list', 'entry_list_single.csv')
#    entryList = 'T0538Org T0538TS001 T0538TS039'.split()
    entryList = 'T0538Org T0538TS001'.split()
#    entryList = 'T0538Org'.split()
#    entryList = 'T0538TS001'.split()
#    entryList = 'T0538TS039'.split()
    writeEntryListToFile(entryListFileName, entryList)

inputDirCASD_NMR = 'file:///Users/jd/CASP-NMR-CING/data'
outputDir = startDir

extraArgList = (inputDirCASD_NMR, outputDir, '.', '.', ARCHIVE_TYPE_BY_CH23_BY_ENTRY, PROJECT_TYPE_CCPN, 'True')

max_time_to_wait = 60 * 60 * 6 # 2p80 took the longest: 5.2 hours.

doScriptOnEntryList(pythonScriptFileName,
                    entryListFileName,
                    startDir,
                    processes_max = 2,
                    delay_between_submitting_jobs = 5, # why is this so long? because of time outs at tang?
                    max_time_to_wait = max_time_to_wait, # 1y4o took more than 600. This is one of the optional arguments.
                    # 1ai0 took over 20 min; let's set this to 1 hour
                    start_entry_id = 0,
                    max_entries_todo = 10,
                    expectPdbEntryList = False,
                    extraArgList = extraArgList)
