from cing import cingDirScripts
from cing import cingDirTmp
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList
import cing
import os

doRamachandran = False

def main():
    """This is a potentially dangerous script. It took JFD an hour one time 
    to realize it was called inadvertently by not having it wrappen in a function. 
"""
    
    subdir = 'chi1chi2_wi_db'
    if doRamachandran:
        subdir = 'phipsi_wi_db'
    
    # parameters for doScriptOnEntryList
    startDir              = os.path.join(cingDirTmp,     subdir)
    pythonScriptFileName  = os.path.join(cingDirScripts, 'getPhiPsi.py')
    entryListFileName     = os.path.join(cingDirScripts, 'data', 'PDB.LIS')
    
    START_ENTRY_ID                 =0 # default 0
    MAX_ENTRIES_TODO               =1000 # default a ridiculously large number like 999999
    
    doScriptOnEntryList(pythonScriptFileName, entryListFileName, startDir,
                        max_time_to_wait = 240, # 1gkp  took over 120
                        START_ENTRY_ID                 = START_ENTRY_ID, # default 0
                        MAX_ENTRIES_TODO               = MAX_ENTRIES_TODO # default a ridiculously large number like 999999
                        )

if __name__ == '__main__':
    cing.verbosity = cing.verbosityDebug
    main()