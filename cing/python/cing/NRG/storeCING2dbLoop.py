"""
python -u $CINGROOT/python/cing/NRG/storeCING2dbLoop.py
# NB this script fails if the backend is not installed.
"""
from cing import cingPythonDir
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG import * #@UnusedWildImport
from cing.NRG.PDBEntryLists import writeEntryListToFile
from cing.NRG.settings import dDir
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList


def storeCING2dbLoop(archive_id, entryList=None, expectPdbEntryList = True):
    'simplest loop over all entries for a quicky.'
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
        nTerror("Expected valid archive_id argument but got: %s" % archive_id)
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
                        start_entry_id = 0,
                        max_entries_todo = 1,
                        expectPdbEntryList = expectPdbEntryList,
                        extraArgList = extraArgList)

if __name__ == '__main__':
    cing.verbosity = cing.verbosityDebug
    #cing.verbosity = cing.verbosityDefault
    
    if 1:
        arch_id = ARCHIVE_NRG_ID
        eList = '1brv'.split()
    #    eList = '1a4d 1a24 1afp 1ai0 1b4y 1brv 1bus 1cjg 1d3z 1hkt 1hue 1ieh 1iv6 1jwe 1kr8 2hgh 2k0e'.split()
    #    eList = []
    elif 0:
        arch_id = ARCHIVE_CASP_ID
        eList = 'T0538TS001 T0538Org'.split()
    elif 0:
        arch_id = ARCHIVE_CASD_ID
    #        eList = None # will use all entries in startDir, 'list', 'entry_list_all.csv'
        eList = 'NeR103ALyon2'.split()
    elif 0:
        arch_id = ARCHIVE_PDB_ID
    #        eList = '1brv'.split()
        eList = "3kff 3a4r 3a34 3i40 2xdy 3mcd 3ild 1brv 1hkt".split()

    storeCING2dbLoop(archive_id=arch_id, entryList=eList)