"""
Unit test execute as:
python $CINGROOT/python/cing/Libs/test/test_DBMS.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDebug
from cing.Libs.DBMS import DBMS
from unittest import TestCase
from glob import glob
from cing import verbosityOutput
import cing
import os
import unittest

class AllChecks(TestCase):


    def testDBMSread(self):
        os.chdir(cingDirTmp)
        csvFileDir = os.path.join(cingDirTestsData, "dbms", 'Overview')
        relationNames = glob("%s/*.csv" % csvFileDir)
        # Truncate the extensions
        relationNames = [ relationName[:-4] for relationName in relationNames]
        dbms = DBMS()
        self.assertFalse(dbms.readCsvRelationList(relationNames, csvFileDir))


if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    cing.verbosity = verbosityOutput
    unittest.main()

