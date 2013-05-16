# python -u $CINGROOT/python/cing/NRG/validateForCASD_NMR.py
from cing import cingPythonDir
from cing.NRG import CASD_NMR_BASE_NAME
from cing.NRG.PDBEntryLists import writeEntryListToFile
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList
from cing.Scripts.validateEntry import ARCHIVE_TYPE_BY_CH23_BY_ENTRY
from cing.Scripts.validateEntry import PROJECT_TYPE_CCPN
from cing.core import constants as cingConstants
from cing.NRG import CasdScripts
import cing
import os

cing.verbosity = cing.verbosityDebug
#cing.verbosity = cing.verbosityDefault

# parameters for doScriptOnEntryList
cingDataDir = os.environ.get('CINGDATAROOT')
startDir = os.path.join(cingDataDir, CASD_NMR_BASE_NAME)
inputDirCASD_NMR = os.path.join(startDir, cingConstants.DATA_STR)
#inputDirCASD_NMR = 'file:///Users/jd/%s/data' % CASD_NMR_BASE_NAME
#cingDirNRG = os.path.join(cingPythonDir, 'cing', 'NRG' )
pythonScriptFileName = os.path.join(cingDirNRG,  'cing', 'NRG', 'validateEntryForCasd.py')
#pythonScriptFileName = os.path.join(cingDirNRG, 'storeCASDCING2db.py')

#if 1:
#    entryListFileName = os.path.join(startDir, 'list', 'entry_list_all.csv')
#    entryListFileName = os.path.join(startDir, 'list', 'entry_list_all_org.csv')
#    entryListFileName = os.path.join(startDir, 'list', 'entry_list_redo.csv')
#else:
#    entryListFileName = os.path.join(startDir, 'list', 'entry_list_single.csv')
#    entryList = 'NeR103ALyon2'.split()
#    writeEntryListToFile(entryListFileName, entryList)


# get mster results file
resultFile = os.path.join(inputDirCASD_NMR, 'resultData.json')
resultData = json.load(open(resultFile))

# Get all entries for CASD 2013
#entryList = [CasdScripts.getEntryName(dd) for dd in resultData if dd['EntryID'] > 120]
entryList = ['2m2e_Lyon_263',]

outputDir = startDir

extraArgList = (inputDirCASD_NMR, outputDir, '.', '.', ARCHIVE_TYPE_BY_CH23_BY_ENTRY, PROJECT_TYPE_CCPN)

max_time_to_wait = 60 * 60 * 6 # 2p80 took the longest: 5.2 hours.

doScriptOnEntryList(pythonScriptFileName,
                    None,
                    startDir,
                    processes_max = 4,
                    delay_between_submitting_jobs = 5, # why is this so long? because of time outs at tang?
                    max_time_to_wait = max_time_to_wait, # 1y4o took more than 600. This is one of the optional arguments.
                    # 1ai0 took over 20 min; let's set this to 1 hour
                    start_entry_id = 0,
                    max_entries_todo = 4,
                    expectPdbEntryList = False,
                    entryList = entryList,
                    extraArgList = extraArgList)
