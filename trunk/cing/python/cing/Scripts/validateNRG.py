# python -u $CINGROOT/python/cing/Scripts/validateNRG.py
# create dirs below by hand:
# mkdir -p /Library/WebServer/Documents/NRG-CING/cmbi8/comments/
# Check which ones are running by setting screen to a large width (300 chars) then do something like:
# ps -le | head -1;ps -le | grep BY_ENTR | grep -v 'cd '
# E.g.
#   501 29210 29209    4000   0  18  0   386856 301464 -      R    187bfe90 ??        15:23.41
#/opt/local/Library/Frameworks/Python.framework/Versions/2.5/Resources/Python.app/Contents/MacOS/Python -u
#/Users/jd/workspace35/cingStable/python/cing/Scripts/validateEntry.py 1rf8
#file://Library/WebServer/Documents/NRG-CING/recoordSync /Library/WebServer/Documents/NRG-CING . . BY_ENTRY CCPN
# Tells you this entry has been running for 15 minutes 23 seconds.

from cing import cingDirScripts
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG.PDBEntryLists import getBmrbNmrGridEntriesDOCRfREDDone
from cing.NRG.PDBEntryLists import writeEntryListToFile
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList
from cing.Scripts.validateEntry import ARCHIVE_TYPE_BY_ENTRY # watch out for NRG-CING validateEntry.py needs to have a couple of lines commented out.
from cing.Scripts.validateEntry import PROJECT_TYPE_CCPN

cing.verbosity = cing.verbosityDebug
#cing.verbosity = cing.verbosityDefault

# parameters for doScriptOnEntryList
startDir = '/Library/WebServer/Documents/NRG-CING'
pythonScriptFileName = os.path.join(cingDirScripts, 'validateEntry.py')
#entryListFileName = os.path.join(startDir, 'entry_list_todo.csv')
entryListFileName = os.path.join(startDir, 'entry_list_single.csv')

# parameters for validateEntry
#inputDir              = '/Users/jd/wattosTestingPlatform/nozip/data/structures/all/pdb'
inputDir = 'file://Library/WebServer/Documents/NRG-CING/recoordSync'
#inputDir = 'http://restraintsgrid.bmrb.wisc.edu/servlet_data/NRG_ccpn_tmp'
outputDir = startDir

extraArgList = (inputDir, outputDir, '.', '.', `ARCHIVE_TYPE_BY_ENTRY`, `PROJECT_TYPE_CCPN`)

retrieveEntryListFromNRG = False
if retrieveEntryListFromNRG:
    ## The list of all entry_codes for which tgz files have been found
    entry_list_nrg_docr = getBmrbNmrGridEntriesDOCRfREDDone()
    if not entry_list_nrg_docr:
        NTerror("No NRG DOCR entries found")
        sys.exit(1)
    if writeEntryListToFile(entryListFileName, entry_list_nrg_docr):
        NTerror("Failed to write entry list")
        sys.exit(1)

# disable next line for regular run.
writeEntryListToFile(entryListFileName, ['1brv'])

doScriptOnEntryList(pythonScriptFileName,
                    entryListFileName,
                    startDir,
                    processes_max = 2,
                    delay_between_submitting_jobs = 15, # why is this so long? because of time outs at tang?
                    max_time_to_wait = 60 * 60 * 6, # 2p80 took the longest: 5.2 hours.
                    # <Molecule "2p80" (C:20,R:1162,A:24552,M:20)>
                    START_ENTRY_ID = 0,
                    MAX_ENTRIES_TODO = 2,
                    extraArgList = extraArgList)
