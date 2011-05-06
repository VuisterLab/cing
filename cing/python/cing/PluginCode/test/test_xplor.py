"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_xplor_nih.py

For testing execution of cing inside of Xplor-NIH python interpreter with the data living outside of it.
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.Ccpn import Ccpn #@UnusedImport needed to throw a ImportWarning so that the test is handled properly.
from cing.PluginCode.xplor import quoteAtomNameIfNeeded
from cing.core.classes import Project
from shutil import copyfile
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def _test_quoteAtomNameIfNeeded(self):
        inputList    = """ HA h2' h2'' hb*  ca+2  """.split()
        expectedList = """ HA h2' h2'' hb* "ca+2" """.split()
        for i, input in enumerate(inputList):
            self.assertEqual( expectedList[i], quoteAtomNameIfNeeded(input))

    def test_exportXplor(self):
        modelCount = 1
        entryList  = "1brv     2fws                      ".split()
        cingDirTmpTest = os.path.join(cingDirTmp, getCallerName())
        mkdirs(cingDirTmpTest)
        self.failIf(os.chdir(cingDirTmpTest), msg=
            "Failed to change to test directory for files: " + cingDirTmpTest)
        for i, entryId in enumerate(entryList):
            if i != 0: # Selection of the entries.
                continue
            inputArchiveDir = os.path.join(cingDirTestsData, "ccpn")
            ccpnFile = os.path.join(inputArchiveDir, entryId + ".tgz")
            if not os.path.exists(ccpnFile):
                self.fail("Neither %s or the .tgz exist" % ccpnFile)
            if not os.path.exists(entryId + ".tgz"):
                copyfile(ccpnFile, os.path.join('.', entryId + ".tgz"))

            project = Project.open(entryId, status = 'new')
            self.assertTrue(project.initCcpn(ccpnFolder = ccpnFile, modelCount=modelCount))
            molecule = project.molecule
            chain0 = molecule.allChains()[0]
            chain = molecule.removeChain(chain0)
            self.assertTrue( chain )
            if molecule.allChains():
                pdbFileName = entryId +"%03d.pdb"
                molecule.export2xplor( pdbFileName )
        # end for
if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
