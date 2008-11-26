# python -u $CINGROOT/python/cing/Scripts/getNRG_CCPNwrapper.py
from cing import cingDirScripts
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList
import cing
import os

cing.verbosity = cing.verbosityDebug
#cing.verbosity = cing.verbosityDefault

# parameters for doScriptOnEntryList
startDir = '/Library/WebServer/Documents/NRG-CING'
pythonScriptFileName = os.path.join(cingDirScripts, 'getNRG_CCPN.py')
#entryListFileName = os.path.join('/Users/jd', 'NMR_Restraints_Grid_entries_2008_11-21.txt')
#entryListFileName = os.path.join('/Users/jd', 'entryCodeList.csv')
entryListFileName = os.path.join('/Users/jd', 'entryCodeList-Oceans14.csv')

# parameters for validateEntry
#inputDir              = '/Users/jd/wattosTestingPlatform/nozip/data/structures/all/pdb'
inputDir = 'http://restraintsgrid.bmrb.wisc.edu/servlet_data/NRG_ccpn_tmp'
outputDir = startDir

extraArgList = (inputDir, outputDir )
    
doScriptOnEntryList(pythonScriptFileName,
                    entryListFileName,
                    startDir,
                    processes_max=1,
                    delay_between_submitting_jobs=1,
                    max_time_to_wait=12000, # 1y4o took more than 600. This is one of the optional arguments.
                    START_ENTRY_ID=0,
                    MAX_ENTRIES_TODO=999,
                    extraArgList=extraArgList)
