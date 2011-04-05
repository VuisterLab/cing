"""
Unit test
python -u $CINGROOT/python/cing/PluginCode/test/test_Wattos.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.Ccpn import Ccpn #@UnusedImport needed to throw a ImportWarning so that the test is handled properly.
from cing.PluginCode.Wattos import runWattos
from cing.PluginCode.required.reqWattos import * #@UnusedWildImport
from cing.core.classes import Project
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def test_Wattos(self):
        "Testing wattos reading and working on a star file that first gets created by Wim's FC."

        # failing entries: 1ai0, 1kr8 (same for 2hgh)
#        entryList = "1kr8".split()
        entryList = "1brv".split()
#        entryList = "basp2".split()
#        entryList = "1bus".split()
#        entryList = "1a4d".split()
#        entryList = "2k0e_all".split()
#        entryList = "1a4d 1a24 1afp 1ai0 1brv 1bus 1cjg 1hue 1ieh 1iv6 1kr8 2hgh 2k0e SRYBDNA Parvulustat".split()
#        entryList = "1afp 1ai0 1brv 1bus 1cjg 1hue 1ieh 1iv6 1kr8 2hgh 2k0e".split()
#1iv6 needs better ccpn file from FC
#        entryList = ["Parvulustat"]
#        entryList = ["SRYBDNA"]

#        if you have a local copy you can use it; make sure to adjust the path setting below.
        useNrgArchive = False # Default is False
        ranges='cv'
#        ranges='16-29'


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
#            self.assertTrue(project.save())
            self.assertFalse(project.molecule.setRanges(ranges))
            self.assertTrue(runWattos(project))
            mol = project.molecule
            completenessMol = mol.getDeepByKeys( WATTOS_STR, COMPLCHK_STR, VALUE_LIST_STR)
            NTdebug("completenessMol: %s" % completenessMol)
            for res in mol.allResidues():
                completenessRes = res.getDeepByKeys( WATTOS_STR, COMPLCHK_STR, VALUE_LIST_STR)
                NTdebug("%s: %s" % (res, completenessRes))
            # end for

            self.assertTrue(completenessMol)
if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()


