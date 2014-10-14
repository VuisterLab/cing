"""python $CINGROOT/python/cing/PluginCode/test/test_shiftx.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.required.reqShiftx import SHIFTX_STR
from cing.core.classes import Project
from cing.constants import * #@UnusedWildImport
from nose.plugins.skip import SkipTest
from unittest import TestCase
import unittest

# Import using optional plugins.
try:
    from cing.PluginCode.shiftx import runShiftx #@UnusedImport needed to throw a ImportWarning so that the test is handled properly.
except ImportWarning, extraInfo: # Disable after done debugging; can't use nTdebug yet.
    print "Got ImportWarning %-10s Skipping unit check %s." % ( SHIFTX_STR, getCallerFileName() )
    raise SkipTest(SHIFTX_STR)
# end try

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
