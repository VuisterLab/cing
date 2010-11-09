"""
Execute like
python $CINGROOT/python/cing/Scripts/validateForExercises.py

The data is included for testing in the CING distribution now.
NB this script differs from validateForProteinsDotDynDnsDotOrg.py in that this one starts from CING.
    LAST TIME 2010-05-27 the other script was used.
    DO NOT UES!
"""
from cing import cingDirScripts
from cing import cingDirTestsData
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList
from cing.Scripts.validateEntry import ARCHIVE_TYPE_FLAT
from cing.Scripts.validateEntry import PROJECT_TYPE_CING
from cing.core.constants import DATA_STR
import cing
import os

cing.verbosity = cing.verbosityDebug

startDir = '/Library/WebServer/Documents/ValidationExercises'
pythonScriptFileName  = os.path.join(cingDirScripts, 'validateEntry.py')
#entryListFileName     = os.path.join('/Users/jd', 'entryCodeList.csv')
entryListFileName     = os.path.join(cingDirScripts, DATA_STR, 'entryCodeListProteinsSite1')

# parameters for validateEntry
#inputDir              = '/Volumes/proteins/var/www/html/Education/Validation/HTML/Exercise_1/Data/'
#inputDir              = '/Users/jd/Sites/cing/in/Tests/data/cyana'
inputDir              = os.path.join(cingDirTestsData, "cing" )
outputDir             = startDir
pdbConvention         = '.'
restraintsConvention  = '.'

extraArgList = ( inputDir,
                 outputDir,
                 pdbConvention,
                 restraintsConvention,
                 `ARCHIVE_TYPE_FLAT`,
                 `PROJECT_TYPE_CING`
                  )

doScriptOnEntryList(pythonScriptFileName,
                    entryListFileName,
                    startDir,
                    processes_max = 2,
                    max_time_to_wait = 12000, # 1y4o took more than 600. This is one of the optional arguments.
                    START_ENTRY_ID                 = 0,
                    MAX_ENTRIES_TODO               = 10,
                    extraArgList=extraArgList)