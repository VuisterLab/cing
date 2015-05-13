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
from cing.core.constants import CV_RANGES_STR
from cing.core.constants import DATA_STR
import cing
import os

cing.verbosity = cing.verbosityDebug

startDir = '/Library/WebServer/Documents/Education/Validation/CINGreports_r987'
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

storeCING2db = "0"
filterTopViolations = '0' 
filterVasco = '0'

extraArgList = ( str(cing.verbosity),
                 inputDir,
                 outputDir,
                 pdbConvention,
                 restraintsConvention,
                 repr(ARCHIVE_TYPE_FLAT),
                 repr(PROJECT_TYPE_CING),
                 storeCING2db,      CV_RANGES_STR,               filterTopViolations, filterVasco
                  )

doScriptOnEntryList(pythonScriptFileName,
                    entryListFileName,
                    startDir,
                    processes_max = 8,
                    max_time_to_wait = 12000, # 1y4o took more than 600. This is one of the optional arguments.
                    start_entry_id                 = 0,
                    max_entries_todo               = 10,
                    extraArgList=extraArgList)
