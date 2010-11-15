"""
Unit test execute as:
python -u $CINGROOT/python/cing/Scripts/test/testlinkdataNRGforGeerten.py
"""
from cing import cingDirTmp, cingDirTestsData #@UnusedImport
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Scripts.linkdataNRGforGeerten import * #@UnusedWildImport
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def tttestLinkdata(self):
        self.failIf(os.chdir(cingDirTmp), msg =
            "Failed to change to directory for temporary test files: " + cingDirTmp)
        if os.path.exists(outputFnLinkData):
            os.remove(outputFnLinkData)
        self.assertFalse(linkdataNRG())
        self.assertTrue(os.path.exists(outputFnLinkData))

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
