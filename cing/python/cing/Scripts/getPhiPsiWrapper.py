from cing import cingDirScripts
from cing import cingDirTmp
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList
import cing
import os

cing.verbosity = cing.verbosityDebug

# parameters for doScriptOnEntryList
startDir              = os.path.join(cingDirTmp,     'phipsi_wi_db')
pythonScriptFileName  = os.path.join(cingDirScripts, 'getPhiPsi.py')
entryListFileName     = os.path.join(cingDirScripts, 'data', 'PDB_tmp.LIS')

START_ENTRY_ID                 =0 # default 0
MAX_ENTRIES_TODO               =999 # default a ridiculously large number like 999999

doScriptOnEntryList(pythonScriptFileName, entryListFileName, startDir,
                    max_time_to_wait = 240, # 1gkp  took over 120
                    START_ENTRY_ID                 = START_ENTRY_ID, # default 0
                    MAX_ENTRIES_TODO               = MAX_ENTRIES_TODO # default a ridiculously large number like 999999
                    )

