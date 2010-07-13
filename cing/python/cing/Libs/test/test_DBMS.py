"""
Unit test execute as:
python $CINGROOT/python/cing/Libs/test/test_DBMS.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDebug
from cing.Libs.DBMS import DBMS
from cing.Libs.DBMS import Relation
from glob import glob
from unittest import TestCase
import cing
import os
import unittest

class AllChecks(TestCase):

    os.chdir(cingDirTmp)

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

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()

