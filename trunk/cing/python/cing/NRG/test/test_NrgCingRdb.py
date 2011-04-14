"""
Unit test execute as:
python $CINGROOT/python/cing/NRG/test/test_NrgCingRdb.py
"""
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG.nrgCingRdb import nrgCingRdb
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def test_NrgCingRdb(self):

        cingDirTmpTest = os.path.join( cingDirTmp, getCallerName() )
        mkdirs( cingDirTmpTest )
        self.failIf(os.chdir(cingDirTmpTest), msg =
            "Failed to change to test directory for files: " + cingDirTmpTest)

        m = nrgCingRdb(host='localhost')
        l = m.getPdbIdList()
        NTdebug("pdbIdList length: %d %s" % (len(l), l))
        self.assertTrue(l)


if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()