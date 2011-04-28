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

    def _test_NrgCingRdb(self):

        cingDirTmpTest = os.path.join( cingDirTmp, getCallerName() )
        mkdirs( cingDirTmpTest )
        self.failIf(os.chdir(cingDirTmpTest), msg =
            "Failed to change to test directory for files: " + cingDirTmpTest)

        m = nrgCingRdb(host='localhost')
        l = m.getPdbIdList()
        NTdebug("pdbIdList length: %d %s" % (len(l), l))
        self.assertTrue(l)
        if 1 and l:
            entry_code = l[0]
            self.assertFalse( m.removeEntry(entry_code))
        # end if


if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()