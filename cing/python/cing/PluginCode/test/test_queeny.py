"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_queeny.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG import * #@UnusedWildImport
from cing.NRG.storeCING2db import doStoreCING2db
from cing.PluginCode.Ccpn import Ccpn #@UnusedImport needed to throw a ImportWarning so that the test is handled properly.
from cing.PluginCode.required.reqQueeny import * #@UnusedWildImport
from cing.core.classes import Project
from unittest import TestCase
import unittest

class AllChecks(TestCase):
    def testQueeny(self):

        runQueeny = 1  # DEFAULT: 1
        doStoreCheck = 0 # DEFAULT: 0 Requires sqlAlchemy
        doValueCheck = 1 # DEFAULT: 1 Requires 1brv
        entryList = "1brv_cs_pk_2mdl".split() # DEFAULT because it contains many data types and is small/fast to run.
#        entryList = "1a24 1a4d 1afp 1ai0 1b4y 1brv 1brv 1bus 1cjg 1hue 1ieh 1iv6 1kr8 2cka 2hgh 2jzn 2k0e 8psh".split()

        expectedInfoList = [
(158, 0.0     ),
(159, 0.0     ),
(160, 0.0     ),
(161, 0.0     ),
(162, 0.0     ),
(163, 0.0     ),
(164, 0.0     ),
(165, 0.000141),
(166, 0.006669),
(167, 0.047112),
(168, 0.159379),
(169, 0.309577),
(170, 0.578983),
(171, 0.838257), # First residue with restraints. Previously none zero elements are due to window averaging JFD assumes.
(172, 1.029047),
(173, 1.063531),
(174, 0.969195),
(175, 1.027744),
(176, 0.954469),
(177, 0.794625),
(178, 0.822723),
(179, 0.845598),
(180, 0.828139),
(181, 0.971881),
(182, 1.141096),
(183, 1.063613),
(184, 0.974891),
(185, 1.116405),
(186, 1.113886),
(187, 0.945552),
(188, 0.731124),
(189, 0.411986),
        ]
        self.failIf(os.chdir(cingDirTmp), msg =
            "Failed to change to directory for temporary test files: " + cingDirTmp)
        for entryId in entryList:
            project = Project.open(entryId, status = 'new')
            self.assertTrue(project, 'Failed opening project: ' + entryId)

            inputArchiveDir = os.path.join(cingDirTestsData, "ccpn")

            ccpnFile = os.path.join(inputArchiveDir, entryId + ".tgz")
            if not os.path.exists(ccpnFile):
                ccpnFile = os.path.join(inputArchiveDir, entryId + ".tar.gz")
                if not os.path.exists(ccpnFile):
                    self.fail("Neither %s or the .tgz exist" % ccpnFile)
            self.assertTrue(project.initCcpn(ccpnFolder = ccpnFile, modelCount=1))
            if runQueeny:
                self.assertFalse(project.runQueeny())
                if doValueCheck:
                    for i,res in enumerate( project.molecule.allResidues()):
                        expected = expectedInfoList[i][1]
                        calculated = getDeepByKeysOrAttributes(res, QUEENY_INFORMATION_STR )
                        NTdebug("Comparing expected versus calculated for %20s with %8.3f %8.3f" % (res, expected, calculated))
                        self.assertAlmostEqual(expected,calculated,3)
            if doStoreCheck:
#                # Does require:
                from cing.PluginCode.sqlAlchemy import csqlAlchemy #@UnusedImport
                pdbEntryId = entryId[0:4]
                if doStoreCING2db( pdbEntryId, ARCHIVE_DEV_NRG_ID, project=project):
                    NTerror("Failed to store CING project's data to DB but continuing.")
        # end for
    # end def test

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
