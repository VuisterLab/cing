from cing import cingDirScripts
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList
import cing
import os

cing.verbosity = cing.verbosityDebug

# parameters for doScriptOnEntryList
startDir = '/Library/WebServer/Documents/NRG-CING'
pythonScriptFileName = os.path.join(cingDirScripts, 'validateEntry.py')
entryListFileName = os.path.join('/Users/jd', 'entryCodeList.csv')

# parameters for validateEntry
#inputDir              = '/Users/jd/wattosTestingPlatform/nozip/data/structures/all/pdb'
inputDir = 'http://restraintsgrid.bmrb.wisc.edu/servlet_data/NRG_ccpn_tmp'
outputDir = startDir

extraArgList = (inputDir, outputDir, '.', '.')
    
doScriptOnEntryList(pythonScriptFileName,
                    entryListFileName,
                    startDir,
                    processes_max=2,
                    max_time_to_wait=12000, # 1y4o took more than 600. This is one of the optional arguments.
                    extraArgList=extraArgList)
