from cing import cingDirScripts
from cing import cingDirTmp
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList
from cing.core.constants import CYANA
from cing.core.constants import PDB
import cing
import os

cing.verbosity = cing.verbosityDebug

# parameters for doScriptOnEntryList
#startDir              = '/Users/jd/tmp/cing/dyndns/'
startDir              = '/Users/jd/Sites/cing/out'
pythonScriptFileName  = os.path.join(cingDirScripts, 'validateEntry.py')
entryListFileName     = os.path.join(cingDirTmp, 'entryCodeList.csv')

# parameters for validateEntry
#inputDir              = '/Volumes/proteins/var/www/html/Education/Validation/HTML/Exercise_1/Data/'
inputDir              = '/Users/jd/Sites/cing/in/Tests/data/cyana'
outputDir             = startDir
pdbConvention         = PDB
restraintsConvention  = CYANA

extraArgList = ( inputDir,
                 outputDir,
                 pdbConvention,
                 restraintsConvention )

doScriptOnEntryList(pythonScriptFileName, entryListFileName, startDir,
                    max_time_to_wait = 12000, # 1y4o took more than 600. This is one of the optional arguments.
                    extraArgList=extraArgList)

