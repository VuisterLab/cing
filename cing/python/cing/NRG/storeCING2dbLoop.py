# python -u $CINGROOT/python/cing/NRG/storeCING2dbLoop.py
# NB this script fails if the MySql backend is not installed.
from cing import cingPythonDir
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG import * #@UnusedWildImport
from cing.NRG.PDBEntryLists import writeEntryListToFile
from cing.NRG.settings import dDir
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList


def storeCING2dbLoop(archive_id, entryList=None, expectPdbEntryList = True):

    if archive_id == ARCHIVE_CASD_ID:
        startDir = os.path.join(dDir,'CASD-NMR-CING')
        expectPdbEntryList = False
    elif archive_id == ARCHIVE_CASP_ID:
        startDir = os.path.join(dDir,'CASP-NMR-CING')
        expectPdbEntryList = False
    elif archive_id == ARCHIVE_NRG_ID:
        startDir = os.path.join(dDir,'NRG-CING')
    elif archive_id == ARCHIVE_PDB_ID:
        startDir = os.path.join(dDir,'PDB-CING')
    else:
        NTerror("Expected valid archive_id argument but got: %s" % archive_id)
        return True


    # parameters for doScriptOnEntryList
    cingDirNRG = os.path.join(cingPythonDir, 'cing', 'NRG' )
    pythonScriptFileName = os.path.join(cingDirNRG, 'storeCING2db.py')

    if entryList:
        entryListFileName = os.path.join(startDir, 'list', 'entry_list_single.csv')
        writeEntryListToFile(entryListFileName, entryList)
    else:
        entryListFileName = os.path.join(startDir, 'list', 'entry_list_all.csv')
    #    entryListFileName = os.path.join(startDir, 'list', 'entry_list_all_org.csv')
    #    entryListFileName = os.path.join(startDir, 'list', 'entry_list_redo.csv')

#    inputDir = '.'
#    extraArgList = (archive_id, inputDir)
    extraArgList = (archive_id,) # note that for length one tuples the comma is required.

    doScriptOnEntryList(pythonScriptFileName,
                        entryListFileName,
                        startDir,
                        processes_max = 2,
                        delay_between_submitting_jobs = 1,
                        max_time_to_wait = 60 * 6,
                        START_ENTRY_ID = 0,
                        MAX_ENTRIES_TODO = 1,
                        expectPdbEntryList = expectPdbEntryList,
                        extraArgList = extraArgList)

if __name__ == '__main__':
    cing.verbosity = cing.verbosityDebug
    #cing.verbosity = cing.verbosityDefault
#    archive_id = ARCHIVE_NRG_ID
#    entryList = '1brv'.split()
#    entryList = '1a4d 1a24 1afp 1ai0 1b4y 1brv 1bus 1cjg 1d3z 1hkt 1hue 1ieh 1iv6 1jwe 1kr8 2hgh 2k0e'.split()
#    entryList = []

#    archive_id = ARCHIVE_CASP_ID
#    entryList = 'T0538TS001 T0538Org'.split()

    archive_id = ARCHIVE_CASD_ID
#        entryList = None # will use all entries in startDir, 'list', 'entry_list_all.csv'
    entryList = 'NeR103ALyon2'.split()
#        entryList = 'AR3436APiscataway2 AtT13Piscataway CGR26APiscataway CtR69APiscataway ET109AoxPiscataway2 ET109AredPiscataway2 HR5537APiscataway2 NeR103APiscataway PGR122APiscataway VpR247Piscataway2'.split()

#    archive_id = ARCHIVE_PDB_ID
##        entryList = '1brv'.split()
#    entryList = "3kff 3a4r 3a34 3i40 2xdy 3mcd 3ild 1brv 1hkt".split()

    storeCING2dbLoop(archive_id, entryList=entryList)