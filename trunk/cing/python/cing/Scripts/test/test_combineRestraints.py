"""
Unit test execute as:
python -u $CINGROOT/python/cing/Scripts/test/test_combineRestraints.py
"""
from cing import cingDirTestsData #@UnusedImport
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.required.reqYasara import YASARA_STR
from cing.Scripts.CombineRestraints import alterRestraintsForLeus
from nose.plugins.skip import SkipTest
from unittest import TestCase
import unittest

# Import using optional plugins.
try:
    from cing.PluginCode.yasaraPlugin import yasaraShell #@UnusedImport needed to throw a ImportWarning so that test is handled properly.
    # A bit redundant with above line.
    from cing.Scripts.rotateLeucines import * #@UnusedWildImport Relies on Yasara as well.
except ImportWarning, extraInfo: # Disable after done debugging; can't use nTdebug yet.
    print "Got ImportWarning %-10s Skipping unit check %s." % ( YASARA_STR, getCallerFileName() )
    raise SkipTest(YASARA_STR)
# end try

class AllChecks(TestCase):
    def _test_CombineRestraints(self):
        cingDirTmpTest = os.path.join( cingDirTmp, getCallerName() )
        mkdirs( cingDirTmpTest )
        self.failIf(os.chdir(cingDirTmpTest), msg =
            "Failed to change to test directory for files: " + cingDirTmpTest)

        # Original project
        proj_name='H2_2Ca_64_100'
        # project with rotated leucines (created with RotateLeucines).
        proj2_name='H2_2Ca_64_100_3_rotleucines'
        # NO CHANGES NEEDED BELOW THIS LINE.
        inputArchiveDir = os.path.join(cingDirTestsData, "cing")
        file_name = '%s/%s.tgz'%(inputArchiveDir,proj_name)
        proj1 = Project.open(file_name,status = 'old')
        proj2 = Project.open(proj2_name,status = 'old')
        leuNumberList=[2,3,4]
        treshold=0 #minimal violation, necessary to classify the restraints.
        deasHB=True #first deassign all HBs in the specified leucines
        dihrCHI2=True #add a dihedral restraint on the leucines.
        status=alterRestraintsForLeus(leuNumberList,proj1,proj2,treshold,deasHB,dihrCHI2)
        self.assertTrue( status )
        proj1.save()
    # end def
# end class

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
