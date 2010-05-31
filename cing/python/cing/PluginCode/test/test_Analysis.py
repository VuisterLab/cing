"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_Analysis.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDebug
from cing.PluginCode.Analysis import Analysis #@UnusedImport needed to throw a ImportWarning so that the test is handled properly.
from cing.PluginCode.Ccpn import Ccpn #@UnusedImport needed to throw a ImportWarning so that the test is handled properly.
from cing.Scripts.Analysis.PyRPF import DEFAULT_DIAGONAL_EXCLUSION_SHIFT
from cing.Scripts.Analysis.PyRPF import DEFAULT_DISTANCE_THRESHOLD
from cing.Scripts.Analysis.PyRPF import DEFAULT_PROCHIRAL_EXCLUSION_SHIFT
from cing.core.classes import Project
from unittest import TestCase
import cing
import os
import unittest

class AllChecks(TestCase):

    entryList = "1brv_cs_pk_2mdl".split()

    def testAnalysisRpf(self):

#        if you have a local copy you can use it; make sure to adjust the path setting below.
        fastestTest = True

        modelCount=99
        if fastestTest:
            modelCount=2

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

            self.assertTrue(project.initCcpn(ccpnFolder = ccpnFile, modelCount=modelCount))

            analysis = Analysis(project)
            self.assertTrue(analysis.runRpf(doAlised=False,
                distThreshold=DEFAULT_DISTANCE_THRESHOLD,
                prochiralExclusion=DEFAULT_PROCHIRAL_EXCLUSION_SHIFT,
                diagonalExclusion=DEFAULT_DIAGONAL_EXCLUSION_SHIFT))

            self.assertTrue(project.save())

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
