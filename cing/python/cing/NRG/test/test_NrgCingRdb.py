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

    def _testGetPdbIdList(self):

        self.failIf(os.chdir(cingDirTmp), msg =
            "Failed to change to directory for temporary test files: " + cingDirTmp)
        m = nrgCingRdb(host='localhost')
        l = m.getPdbIdList()
        NTdebug("pdbIdList length: %d %s" % (len(l), l))
        self.assertTrue(l)


if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()