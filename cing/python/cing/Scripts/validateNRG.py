# python -u $CINGROOT/python/cing/Scripts/validateNRG.py
from cing import cingDirScripts
from cing.Libs.NTutils import NTerror
from cing.NRG.PDBEntryLists import getBmrbNmrGridEntriesDOCRfREDDone
from cing.NRG.PDBEntryLists import writeEntryListToFile
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList
from cing.Scripts.validateEntry import ARCHIVE_TYPE_BY_ENTRY
import cing
import os
import sys

cing.verbosity = cing.verbosityDebug
#cing.verbosity = cing.verbosityDefault

# parameters for doScriptOnEntryList
startDir = '/Library/WebServer/Documents/NRG-CING'
pythonScriptFileName = os.path.join(cingDirScripts, 'validateEntry.py')
#entryListFileName = os.path.join(startDir, 'entry_list_108d.csv')
entryListFileName = os.path.join(startDir, 'entry_list_nrg_docr.csv')
#entryListFileName = os.path.join('/Users/jd', 'entryCodeList.csv')
#entryListFileName = os.path.join('/Users/jd', 'entryCodeList-Oceans14.csv')

# parameters for validateEntry
#inputDir              = '/Users/jd/wattosTestingPlatform/nozip/data/structures/all/pdb'
inputDir = 'file://Library/WebServer/Documents/NRG-CING/recoordSync'
#inputDir = 'http://restraintsgrid.bmrb.wisc.edu/servlet_data/NRG_ccpn_tmp'
outputDir = startDir

extraArgList = (inputDir, outputDir, '.', '.', `ARCHIVE_TYPE_BY_ENTRY`)

retrieveEntryListFromNRG = True

if retrieveEntryListFromNRG:
    ## The list of all entry_codes for which tgz files have been found
    entry_list_nrg_docr = getBmrbNmrGridEntriesDOCRfREDDone()
    if not entry_list_nrg_docr:
        NTerror("No NRG DOCR entries found")
        sys.exit(1)
    if writeEntryListToFile(entryListFileName, entry_list_nrg_docr):
        NTerror("Failed to write entry list")
        sys.exit(1)

doScriptOnEntryList(pythonScriptFileName,
                    entryListFileName,
                    startDir,
                    processes_max = 2,
                    delay_between_submitting_jobs = 15, # why is this so long? because of time outs at tang?
                    max_time_to_wait = 3600, # 1y4o took more than 600. This is one of the optional arguments.
                    # 1ai0 took over 20 min; let's set this to 1 hour
                    START_ENTRY_ID = 0,
                    MAX_ENTRIES_TODO = 1,
                    extraArgList = extraArgList)
