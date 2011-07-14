"""
Unit test execute as:
python $CINGROOT/python/cing/Libs/test/test_DBMS.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing import cingRoot
from cing.Libs.DBMS import DBMS
from cing.Libs.DBMS import Relation
from cing.Libs.DBMS import addColumnHeaderRowToCsvFile
from cing.Libs.DBMS import sortRelationByColumnListFromCsvFile
from cing.Libs.DBMS import sort_table
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG.PDBEntryLists import matchBmrbPdbDataDir
from glob import glob
from shutil import copyfile
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    cingDirTmpTest = os.path.join( cingDirTmp, 'test_DBMS' )
    mkdirs( cingDirTmpTest )
    os.chdir(cingDirTmpTest)

    def testDBMSread(self):
        csvFileDir = os.path.join(cingDirTestsData, "dbms", 'Overview')
        relationNames = glob("%s/*.csv" % csvFileDir)
        # Truncate the extensions
        relationNames = [ relationName[:-4] for relationName in relationNames]
        dbms = DBMS()
        self.assertFalse(dbms.readCsvRelationList(relationNames, csvFileDir))

    def testDBMShashing(self):
        dbms = DBMS()
        mTable = Relation('mTable', dbms, columnList=['pdb_id', 'bmrb_id'])
        pdbIdNewMany2OneList = mTable.getColumn('pdb_id')
        bmrbIdNewMany2OneList = mTable.getColumn('bmrb_id')
        pdbIdNewMany2OneList += '2kz0 2rop'.split()
        bmrbIdNewMany2OneList += [16995, 11041]
        mTableHash = mTable.getHash()
        rowList = mTableHash['2rop']
        self.assertEqual(11041,rowList[1])
        nTdebug('\n'+str(mTable))

    def testAddColumnHeaderRowToCsvFile(self):
        adit_fn = 'adit_nmr_matched_pdb_bmrb_entry_ids.csv' # already contains one header row but let's add another one.
        src = os.path.join(cingRoot, matchBmrbPdbDataDir, adit_fn)
        copyfile(src, adit_fn)
        columnOrder = 'bmrb_id pdb_id'.split()
        self.assertFalse( addColumnHeaderRowToCsvFile(adit_fn, columnOrder))

    def testSortTable(self):
        mytable = (
            ('Joe',     'Clark',    1989),
            ('Charlie', 'Babbitt',  1988),
            ('Frank',   'Abagnale', 2002),
            ('Bill',    'Clark',    2009),
            ('Alan',    'Clark',    1804),
            )
        for row in sort_table(mytable, (1,0)):
            nTmessage( str(row) )

    def testSortCsvFile(self):
        fn = 'adit_nmr_matched_pdb_bmrb_entry_ids.csv' # already contains one header row but let's add another one.
#        fn = 'test.csv' # already contains one header row but let's add another one.
        src = os.path.join(cingRoot, matchBmrbPdbDataDir, fn)
        copyfile(src, fn)
        self.assertFalse( sortRelationByColumnListFromCsvFile( fn, columnList=(1,0), containsHeaderRow=True))


if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()

