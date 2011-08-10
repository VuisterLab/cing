# python -u $CINGROOT/python/cing/Scripts/interactive/mouseBuffer4.py
from cing import cingDirData
from cing import cingDirTmp
from cing import cingPythonCingDir
from cing.Libs.DBMS import DBMS
from cing.NRG.PDBEntryLists import readEntryListFromFile
from cing.NRG.PDBEntryLists import writeEntryListToFile
from cing.NRG.settings import pdbbase_dir
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList
import cing
import os


if False:
    os.chdir('/Library/WebServer/Documents/NRG-CING/pgsql')
    dbms = DBMS()
    relationName = 'nrgcing.cingentry'
    dbms.readCsvRelationList([relationName], '.')
    table = dbms.tables[relationName]
    table.setColumnToValue(65,0)
    file_name_new = relationName +"_new.csv"
    table.writeCsvFile(file_name_new)

if True:
    cing.verbosity = cing.verbosityDebug
    startDir = cingDirTmp
    entryListFileName = os.path.join(startDir, 'entry_list_batch.csv')
    if False:
        entryList = '1bha 1bus 1cey 1cld 1ego 1egr 1erc 1maj 1mak 1mdj 1pba 1pdc 1tfs 1tnn 1tur 1tus 2aas 4trx 9pcy'.split()
    else:
        entryList = readEntryListFromFile(cingDirData+'/Varia/entry_list_92.csv', headerCount = 1)
    writeEntryListToFile(entryListFileName, entryList)
    pdbDir = pdbbase_dir + '/data/structures/all/pdb'

    pythonScriptFileName = 'python %s/main.py -v 9 --initPDB %s/pdb$x.ent.gz --validateFastest --ranges cv -n' % (
        cingPythonCingDir, pdbDir)
    extraArgList = ()

    doScriptOnEntryList(pythonScriptFileName,
                        entryListFileName,
                        startDir,
                        processes_max = 2,
                        delay_between_submitting_jobs = 2,
                        max_time_to_wait = 6000,
                        start_entry_id = 0,
                        max_entries_todo = 299,
                        expectPdbEntryList = True,
                        extraArgList = extraArgList)
