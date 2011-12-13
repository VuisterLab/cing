"""
Unit test execute as:
python -u $CINGROOT/python/cing/Scripts/test/test_RotateLeucines.py
"""
from cing import cingDirTestsData #@UnusedImport
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.required.reqYasara import YASARA_STR
from cing.Scripts.rotateLeucines import * #@UnusedWildImport
from nose.plugins.skip import SkipTest
from unittest import TestCase
import unittest

# Import using optional plugins.
try:
    from cing.PluginCode.yasaraPlugin import yasaraShell #@UnusedImport needed to throw a ImportWarning so that test is handled properly.
except ImportWarning, extraInfo: # Disable after done debugging; can't use nTdebug yet.
    print "Got ImportWarning %-10s Skipping unit check %s." % ( YASARA_STR, getCallerFileName() )
    raise SkipTest(YASARA_STR)
# end try

class AllChecks(TestCase):

    def _test_rotateLeucinesInYasara(self):
        cingDirTmpTest = os.path.join( cingDirTmp, getCallerName() )
        mkdirs( cingDirTmpTest )
        self.failIf(os.chdir(cingDirTmpTest), msg =
            "Failed to change to test directory for files: " + cingDirTmpTest)

        entryId = '1brv'
        if False: # DEFAULT False
            entryId='H2_2Ca_64_100'

        inputArchiveDir = os.path.join(cingDirTestsData, "cing")
        self.assertFalse( runRotateLeucines(cingDirTmpTest, inputArchiveDir, entryId))
    # end def
# end class
        
if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
# end if