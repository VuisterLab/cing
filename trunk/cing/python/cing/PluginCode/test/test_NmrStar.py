"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_NmrStar.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.Ccpn import Ccpn #@UnusedImport needed to throw a ImportWarning so that the test is handled properly.
from cing.PluginCode.NmrStar import NmrStar
from cing.core.classes import Project
from unittest import TestCase
import shutil
import unittest

#print sys.path

class AllChecks(TestCase):

    def _testNmrStar(self):
        "Testing conversion from CCPN to NMR-STAR using Wim Vranken's FC. Disabled test because only JFD uses it."
        # failing entries: 1ai0, 1kr8 (same for 2hgh)
        entryList = "1a4d".split()
#        entryList = "1a4d 1a24 1afp 1ai0 1brv 1bus 1cjg 1hue 1ieh 1iv6 1kr8 2hgh 2k0e SRYBDNA Parvulustat".split()
#1iv6 needs better ccpn file from FC
#        if you have a local copy you can use it; make sure to adjust the path setting below.
        useNrgArchive = False # Default is False


        cingDirTmpTest = os.path.join( cingDirTmp, getCallerName() )
        mkdirs( cingDirTmpTest )
        self.failIf(os.chdir(cingDirTmpTest), msg =
            "Failed to change to test directory for files: " + cingDirTmpTest)

        for entryId in entryList:
            project = Project.open(entryId, status = 'new')
            self.assertTrue(project, 'Failed opening project: ' + entryId)

            if useNrgArchive: # default is False
                inputArchiveDir = os.path.join('/Library/WebServer/Documents/NRG-CING/recoordSync', entryId)
            else:
                inputArchiveDir = os.path.join(cingDirTestsData, "ccpn")

            ccpnFile = os.path.join(inputArchiveDir, entryId + ".tgz")
            self.assertTrue(project.initCcpn(ccpnFolder = ccpnFile))
            self.assertTrue(project.save())
            fileName = os.path.join( cingDirTmp, entryId + ".str")
            nmrStar = NmrStar(project)
            self.assertTrue( nmrStar )
            self.assertTrue( nmrStar.toNmrStarFile( fileName ))
            # Do not leave the old CCPN directory laying around since it might get added to by another test.
            if os.path.exists(entryId):
                self.assertFalse(shutil.rmtree(entryId))

if __name__ == "__main__":
    cing.verbosity = verbosityDetail
    cing.verbosity = verbosityOutput
    cing.verbosity = verbosityNothing
    cing.verbosity = verbosityDebug
    unittest.main()
