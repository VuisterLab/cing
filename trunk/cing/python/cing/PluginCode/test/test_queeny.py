"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_queeny.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.Ccpn import Ccpn #@UnusedImport needed to throw a ImportWarning so that the test is handled properly.
from cing.PluginCode.required.reqWattos import * #@UnusedWildImport
from cing.core.classes import Project
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    entryList = "1brv_cs_pk_2mdl".split() # DEFAULT because it contains many data types and is small/fast to run.

    def testQueeny(self):

        self.failIf(os.chdir(cingDirTmp), msg =
            "Failed to change to directory for temporary test files: " + cingDirTmp)
        for entryId in AllChecks.entryList:
            project = Project.open(entryId, status = 'new')
            self.assertTrue(project, 'Failed opening project: ' + entryId)

            inputArchiveDir = os.path.join(cingDirTestsData, "ccpn")

            ccpnFile = os.path.join(inputArchiveDir, entryId + ".tgz")
            if not os.path.exists(ccpnFile):
                ccpnFile = os.path.join(inputArchiveDir, entryId + ".tar.gz")
                if not os.path.exists(ccpnFile):
                    self.fail("Neither %s or the .tgz exist" % ccpnFile)
            self.assertTrue(project.initCcpn(ccpnFolder = ccpnFile, modelCount=1))
            self.assertFalse(project.runQueeny())
        # end for
    # end def test

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
