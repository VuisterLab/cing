# python -u $CINGROOT/python/cing/NRG/storeCASDCING2dbLoop.py
# NB this script fails if the MySql backend is not installed.
from cing import cingPythonDir
from cing.NRG.PDBEntryLists import writeEntryListToFile
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList
import cing
import os
#from cing.NRG.PDBEntryLists import writeEntryListToFile

cing.verbosity = cing.verbosityDebug
#cing.verbosity = cing.verbosityDefault

# parameters for doScriptOnEntryList
startDir = '/Library/WebServer/Documents/CASD-NMR-CING'
cingDirNRG = os.path.join(cingPythonDir, 'cing', 'NRG' )
pythonScriptFileName = os.path.join(cingDirNRG, 'storeCASDCING2db.py')

if False:
    entryListFileName = os.path.join(startDir, 'list', 'entry_list_all.csv')
#    entryListFileName = os.path.join(startDir, 'list', 'entry_list_all_org.csv')
#    entryListFileName = os.path.join(startDir, 'list', 'entry_list_redo.csv')
else:
    entryListFileName = os.path.join(startDir, 'list', 'entry_list_single.csv')
    entryList = 'AR3436AOrg'.split()
    writeEntryListToFile(entryListFileName, entryList)

inputDir = '.'
#outputDir = '/Library/WebServer/Documents/NRG-CING-RDB'
extraArgList = (inputDir)

# enable next line for test run.
#writeEntryListToFile(entryListFileName, ['1brv'])

doScriptOnEntryList(pythonScriptFileName,
                    entryListFileName,
                    startDir,
                    processes_max = 2,
                    delay_between_submitting_jobs = 1,
                    max_time_to_wait = 60 * 6,
                    START_ENTRY_ID = 0,
                    MAX_ENTRIES_TODO = 1,
                    expectPdbEntryList = False,
                    extraArgList = extraArgList)