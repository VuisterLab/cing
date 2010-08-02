"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_NmrStar.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityDetail
from cing import verbosityNothing
from cing import verbosityOutput
from cing.PluginCode.Ccpn import Ccpn #@UnusedImport needed to throw a ImportWarning so that the test is handled properly.
from cing.PluginCode.NmrStar import NmrStar
from cing.core.classes import Project
from unittest import TestCase
import cing
import os
import shutil
import unittest

class AllChecks(TestCase):

    def tttestNmrStar(self):
        "Disabled by JFD for now as I'm the only one checking this."
        # failing entries: 1ai0, 1kr8 (same for 2hgh)
#        entryList = "1kr8".split()
#        entryList = "1brv".split()
#        entryList = "basp2".split()
#        entryList = "taf3".split()
        entryList = "1a4d".split() # don't use the same entry code as for test_ccpn.py until issue 213 is resolved.
#        entryList = "2k0e_all".split()
#        entryList = "1a4d 1a24 1afp 1ai0 1brv 1bus 1cjg 1hue 1ieh 1iv6 1kr8 2hgh 2k0e SRYBDNA Parvulustat".split()
#        entryList = "1afp 1ai0 1brv 1bus 1cjg 1hue 1ieh 1iv6 1kr8 2hgh 2k0e".split()
#1iv6 needs better ccpn file from FC
#        entryList = ["Parvulustat"]
#        entryList = ["SRYBDNA"]

#        if you have a local copy you can use it; make sure to adjust the path setting below.
        useNrgArchive = False # Default is False


        self.failIf(os.chdir(cingDirTmp), msg =
            "Failed top change to directory for temporary test files: " + cingDirTmp)
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
