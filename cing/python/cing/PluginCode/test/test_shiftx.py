"""python $CINGROOT/python/cing/PluginCode/test/test_shiftx.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.shiftx import runShiftx #@UnusedImport needed to throw a ImportWarning so that the test is handled properly.
from cing.core.classes import Project
from cing.core.constants import * #@UnusedWildImport
from unittest import TestCase
import unittest

class AllChecks(TestCase):
    def test_shiftx(self):
#        entryId = "1brv" # Small much studied PDB NMR entry
#        entryId = "2hgh_1model"  RNA-protein complex.
        entryId = "1brv"
#        entryId = "1tgq_1model" # withdrawn entry
        cingDirTmpTest = os.path.join( cingDirTmp, getCallerName() )
        mkdirs( cingDirTmpTest )
        self.failIf(os.chdir(cingDirTmpTest), msg =
            "Failed to change to test directory for files: " + cingDirTmpTest)

        project = Project( entryId )
        self.failIf( project.removeFromDisk())
        project = Project.open( entryId, status='new' )
        cyanaFile = os.path.join(cingDirTestsData, "cyana", entryId + ".cyana.tgz")
        self.assertTrue(project.initCyana(cyanaFolder = cyanaFile))
        project.runShiftx()

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
