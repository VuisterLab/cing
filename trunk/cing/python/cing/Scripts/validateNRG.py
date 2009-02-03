# python -u $CINGROOT/python/cing/Scripts/validateNRG.py
from cing import cingDirScripts
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList
import cing
import os

cing.verbosity = cing.verbosityDebug
#cing.verbosity = cing.verbosityDefault

# parameters for doScriptOnEntryList
startDir = '/Library/WebServer/Documents/NRG-CING'
pythonScriptFileName = os.path.join(cingDirScripts, 'validateEntry.py')
entryListFileName = os.path.join(startDir, 'entry_list_1a3p.csv')
#entryListFileName = os.path.join(startDir, 'entry_list_nrg_docr.csv')
#entryListFileName = os.path.join('/Users/jd', 'entryCodeList.csv')
#entryListFileName = os.path.join('/Users/jd', 'entryCodeList-Oceans14.csv')

# parameters for validateEntry
#inputDir              = '/Users/jd/wattosTestingPlatform/nozip/data/structures/all/pdb'
inputDir = 'http://restraintsgrid.bmrb.wisc.edu/servlet_data/NRG_ccpn_tmp'
outputDir = startDir

extraArgList = (inputDir, outputDir, '.', '.')
    
doScriptOnEntryList(pythonScriptFileName,
                    entryListFileName,
                    startDir,
                    processes_max=2,
                    delay_between_submitting_jobs=15, # why is this so long? because of time outs at tang?
                    max_time_to_wait=1200, # 1y4o took more than 600. This is one of the optional arguments.
                    START_ENTRY_ID=0,
                    MAX_ENTRIES_TODO=1,
                    extraArgList=extraArgList)
