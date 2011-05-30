'''
Unit test execute as:
python -u $CINGROOT/python/cing/Libs/test/test_NoeCompleteness.py

Created on May 30, 2011

@author: jd
'''
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.NoeCompleteness import * #@UnusedWildImport
from unittest import TestCase
import unittest


class AllChecks(TestCase):
    cingDirTmpTest = os.path.join( cingDirTmp, 'test_NoeCompleteness' )
    mkdirs( cingDirTmpTest )
    os.chdir(cingDirTmpTest)

    def test_NoeCompleteness(self):
        cing.verbosity = cing.verbosityDebug
        c = CompletenessLib()
        self.assertTrue(c)
        
if __name__ == "__main__":
    unittest.main()
