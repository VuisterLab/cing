"""
Unit test execute as:
python $CINGROOT/python/cing/NRG/test/test_PDBEntryLists.py
"""
from cing import cingDirTestsData #@UnusedImport
from cing import cingDirTmp
from cing import verbosityDebug
from cing.Libs.NTutils import NTdebug
from cing.NRG.PDBEntryLists import getPdbEntries
from unittest import TestCase
import cing
import os
import unittest

class AllChecks(TestCase):

    def test_PDBEntryLists(self):
        self.failIf(os.chdir(cingDirTmp), msg = 
            "Failed to change to directory for temporary test files: " + cingDirTmp)
        
        if False:
            nmrList = getPdbEntries(onlyNmr = True)
            NTdebug("getPdbEntries NMR: %d %s" % (len(nmrList), nmrList))
            self.assertTrue( nmrList )

        pdbList = getPdbEntries(onlyNmr = False)
        NTdebug("getPdbEntries ALL: %d %s" % (len(pdbList), pdbList))
        self.assertTrue( pdbList )

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
