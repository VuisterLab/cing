"""
Execute like
python $CINGROOT/python/cing/Scripts/validateForProteinsDotDynDnsDotOrg.py

NB this script differs from validateForExercises.py in that this one starts from CYANA.

After execution copy the data over to the right spot.
\cp -rvf $D/tmp/proteinsDotDynDnsDotOrg/data/* $D/ValidationExercises/data
No need to update the indices unless changing the entries.
"""

from cing import cingDirScripts
from cing import cingDirTestsData
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList
from cing.Scripts.validateEntry import ARCHIVE_TYPE_BY_ENTRY
from cing.Scripts.validateEntry import PROJECT_TYPE_CYANA
from cing.core.constants import * #@UnusedWildImport

cing.verbosity = cing.verbosityDebug

# parameters for doScriptOnEntryList
#startDir              = '/Users/jd/tmp/cing/dyndns/'
#startDir              = '/Users/jd/Sites/cing/out'
startDir              = '/Library/WebServer/Documents/tmp/proteinsDotDynDnsDotOrg'

pythonScriptFileName  = os.path.join(cingDirScripts, 'validateEntry.py')
#entryListFileName     = os.path.join('/Users/jd', 'entryCodeList.csv')
entryListFileName     = os.path.join(cingDirScripts, 'data', 'entryCodeListProteinsSite1')

# parameters for validateEntry
#inputDir              = '/Volumes/proteins/var/www/html/Education/Validation/HTML/Exercise_1/Data/'
#inputDir              = '/Users/jd/Sites/cing/in/Tests/data/cyana'
inputDir              = os.path.join(cingDirTestsData, "cyana" )
outputDir             = startDir
#pdbConvention         = PDB before using Yasara to update.
pdbConvention         = IUPAC
restraintsConvention  = CYANA

extraArgList = ( inputDir,
                 outputDir,
                 pdbConvention,
                 restraintsConvention,
                 `ARCHIVE_TYPE_BY_ENTRY`,
                 `PROJECT_TYPE_CYANA`
                  )

doScriptOnEntryList(pythonScriptFileName,
                    entryListFileName,
                    startDir,
                    processes_max = 2,
                    max_time_to_wait = 12000, # 1y4o took more than 600. This is one of the optional arguments.
                    START_ENTRY_ID                 = 0,
                    MAX_ENTRIES_TODO               = 10,
                    extraArgList=extraArgList)

