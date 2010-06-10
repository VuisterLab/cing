# python -u $CINGROOT/python/cing/NRG/doAnnotateCasdNmrLoop.py

from cing import cingPythonDir
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG.CasdNmrMassageCcpnProject import baseDir
from cing.NRG.CasdNmrMassageCcpnProject import programHoH
from cing.NRG.PDBEntryLists import writeEntryListToFile
from cing.NRG.doAnnotateCasdNmr import annotateEntry
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList

cing.verbosity = cing.verbosityDebug

# parameters for doScriptOnEntryList
startDir = baseDir

cingDirNRG = os.path.join(cingPythonDir, 'cing', 'NRG' )
pythonScriptFileName = os.path.join(cingDirNRG, 'doAnnotateCasdNmr.py')
if False:
    entryListFileName = os.path.join(startDir, 'list', 'entry_list_all.csv')
#    entryListFileName = os.path.join(startDir, 'list', 'entry_list_redo.csv')
else:
    entryListFileName = os.path.join(startDir, 'list', 'entry_list_single.csv')
    entryList = 'VpR247Cheshire'.split()
    writeEntryListToFile(entryListFileName, entryList)
extraArgList = ()

doScriptOnEntryList(pythonScriptFileName,
                    entryListFileName,
                    startDir,
                    processes_max = 2,
                    delay_between_submitting_jobs = 2,
                    max_time_to_wait = 6000,
                    START_ENTRY_ID = 0,
                    MAX_ENTRIES_TODO = 100,
                    expectPdbEntryList = False,
                    extraArgList = extraArgList)

"""
Alternatively to the strategy above use a simple loop that
does not put the log files nicely into separate directories etc.
NOT USED AFTER MOVED HERE.
"""
def annotateLoop():
    maxCities = 100
    maxEntries = 100
    entryList = ['CGR26A']
    #    cityList = [ 'Cheshire', 'Frankfurt', 'Lyon', 'Paris', 'Piscataway', 'Seattle', 'Utrecht' ]
    cityList = [ 'Cheshire']
    maxEntries = min(maxEntries, len(entryList))
    maxCities = min(maxCities, len(cityList))

    for entryCode in entryList[0:maxEntries]:
        for city in cityList[0:maxCities]:
            entryCodeNew = entryCode + city
            programId = getDeepByKeys(programHoH, entryCode, city)
            if not (city == 'Test' or programId):
#                NTdebug("Skipping %s" % entryCodeNew)
                continue
            else:
                NTdebug("Looking at %s" % entryCodeNew)
            entryCodePlusCity = entryCode + '_' + city # will be split on
            annotateEntry(entryCodePlusCity)
# end def
