# python -u $CINGROOT/python/cing/Scripts/checkValidationCriteria.py

from cing import cingDirScripts
from cing.NRG.PDBEntryLists import writeEntryListToFile
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList
import cing
import os

cing.verbosity = cing.verbosityDebug
#cing.verbosity = cing.verbosityDefault

# parameters for doScriptOnEntryList
startDir = '/Library/WebServer/Documents/NRG-CING'
pythonScriptFileName = os.path.join(cingDirScripts, 'storeNRGCING2db.py')
entryListFileName = os.path.join(startDir, 'entry_list_single.csv')

inputDir = '.'
#outputDir = '/Library/WebServer/Documents/NRG-CING-RDB'
extraArgList = (inputDir)

# enable next line for test run.
writeEntryListToFile(entryListFileName, ['1brv'])

doScriptOnEntryList(pythonScriptFileName,
                    entryListFileName,
                    startDir,
                    processes_max = 2,
                    delay_between_submitting_jobs = 5,
                    max_time_to_wait = 60 * 6,
                    START_ENTRY_ID = 0,
                    MAX_ENTRIES_TODO = 2,
                    extraArgList = extraArgList)