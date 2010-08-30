"""
Unit test
python -u $CINGROOT/python/cing/PluginCode/test/test_Wattos.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.Ccpn import Ccpn #@UnusedImport needed to throw a ImportWarning so that the test is handled properly.
from cing.PluginCode.Wattos import runWattos
from cing.core.classes import Project
from unittest import TestCase
import shutil
import unittest

class AllChecks(TestCase):

    "Enable again when issue 193 with NMR-STAR format has been alleviated; "
    def tttestWattos(self):
        "Testing wattos reading and working on a star file that first gets created by Wim's FC."

        # failing entries: 1ai0, 1kr8 (same for 2hgh)
#        entryList = "1kr8".split()
        entryList = "1brv".split()
#        entryList = "basp2".split()
#        entryList = "taf3".split()
#        entryList = "1a4d".split()
#        entryList = "2k0e_all".split()
#        entryList = "1a4d 1a24 1afp 1ai0 1brv 1bus 1cjg 1hue 1ieh 1iv6 1kr8 2hgh 2k0e SRYBDNA Parvulustat".split()
#        entryList = "1afp 1ai0 1brv 1bus 1cjg 1hue 1ieh 1iv6 1kr8 2hgh 2k0e".split()
#1iv6 needs better ccpn file from FC
#        entryList = ["Parvulustat"]
#        entryList = ["SRYBDNA"]

#        if you have a local copy you can use it; make sure to adjust the path setting below.
        useNrgArchive = False # Default is False


        self.failIf(os.chdir(cingDirTmp), msg =
            "Failed to change to directory for temporary test files: " + cingDirTmp)
        for entryId in entryList:
            project = Project.open(entryId, status = 'new')
            self.assertTrue(project, 'Failed opening project: ' + entryId)

            if useNrgArchive: # default is False
                inputArchiveDir = os.path.join('/Library/WebServer/Documents/NRG-CING/recoordSync', entryId)
            else:
                inputArchiveDir = os.path.join(cingDirTestsData, "ccpn")

            ccpnFile = os.path.join(inputArchiveDir, entryId + ".tgz")
            self.assertTrue(project.initCcpn(ccpnFolder = ccpnFile))
#            self.assertTrue(project.save())
            self.assertTrue(runWattos(project))
            # Do not leave the old CCPN directory laying around since it might get added to by another test.
            if os.path.exists(entryId):
                self.assertFalse(shutil.rmtree(entryId))

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()


