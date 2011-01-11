from cing import cingPythonDir
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG.PDBEntryLists import writeEntryListToFile
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList

cing.verbosity = cing.verbosityDebug

# parameters for doScriptOnEntryList
startDir = '/Library/WebServer/Documents/CASD-NMR-CING'

cingDirNRG = os.path.join(cingPythonDir, 'cing', 'NRG' )
pythonScriptFileName = os.path.join(cingDirNRG, 'runQueenyEntry.py')
entryListFileName = os.path.join(startDir, 'list', 'entry_list_todo.csv')
#    entryList = 'VpR247Cheshire'.split()
entryList = [
'AR3436APiscataway2',
'AtT13Piscataway',
'CGR26APiscataway',
'CtR69APiscataway',
'ET109AoxPiscataway2',
'ET109AredPiscataway2',
'HR5537APiscataway2',
'NeR103APiscataway',
'PGR122APiscataway',
'VpR247Piscataway2'
]
writeEntryListToFile(entryListFileName, entryList)
extraArgList = ()

doScriptOnEntryList(pythonScriptFileName,
                    entryListFileName,
                    startDir,
                    processes_max = 8,
                    delay_between_submitting_jobs = 2,
                    max_time_to_wait = 6000,
                    START_ENTRY_ID = 0,
                    MAX_ENTRIES_TODO = 1,
                    expectPdbEntryList = False,
                    extraArgList = extraArgList)
