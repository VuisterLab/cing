"""
Unit test execute as:
python $CINGROOT/python/cing/Database/Scripts/test/test_createStarUserLib.py
"""
from cing import cingDirTmp
from cing.Database.Scripts.createStarUserLib import createStarUserLib
from cing.Libs.NTutils import * #@UnusedWildImport
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    cingDirTmpTest = os.path.join( cingDirTmp, 'test_createStarUserLib' )
    mkdirs( cingDirTmpTest )
    os.chdir(cingDirTmpTest)

    def _test_createSimpleFastProject(self):
        createStarUserLib()
    # end def
# end class

if __name__ == "__main__":
    cing.verbosity = cing.verbosityDebug
    unittest.main()
