# python -u $CINGROOT/python/cing/NRG/checkValidationCriteria.py
# NB this script fails if the MySql backend is not installed.
from cing import cingPythonDir
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList
import cing
import os
#from cing.NRG.PDBEntryLists import writeEntryListToFile

cing.verbosity = cing.verbosityDebug
#cing.verbosity = cing.verbosityDefault

# parameters for doScriptOnEntryList
startDir = '/Library/WebServer/Documents/NRG-CING'
cingDirNRG = os.path.join(cingPythonDir, 'cing', 'NRG' )
pythonScriptFileName = os.path.join(cingDirNRG, 'storeNRGCING2db.py')
entryListFileName = os.path.join(startDir, 'entry_list_done.csv')

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
                    START_ENTRY_ID = 21,
                    MAX_ENTRIES_TODO = 1,
                    extraArgList = extraArgList)