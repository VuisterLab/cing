"""
Unit test execute as:
python -u $CINGROOT/python/cing/STAR/test/test_Utils.py
"""
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from unittest import TestCase
import unittest



class AllChecks(TestCase, Lister):

    cingDirTmpTest = os.path.join( cingDirTmp, 'test_Utils' )
    mkdirs( cingDirTmpTest )
    os.chdir(cingDirTmpTest)


    def test_Transpose(self):
        m1 = [ [1,2], [3,4] ]
        m2 = [ [1,3], [2,4] ]
        m1t= transpose(m1)
        self.assertTrue(m1t==m2)
        
    def test_Lister(self):
        self.dummy = "dumb"
        nTdebug( "Self is: %r", self )

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
#    cing.verbosity = verbosityError
    unittest.main()
