from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityError
from cing.Libs.NTutils import NTdebug
from cing.STAR import Utils
from unittest import TestCase
import cing
import os
import unittest



class AllChecks(TestCase):
        
    os.chdir(cingDirTmp)

    def testTranspose(self):
        m1 = [ [1,2], [3,4] ]
        m2 = [ (1,3), (2,4) ]        
        m1t= Utils.transpose(m1)
        self.assertTrue(m1t==m2)
    def testLister(self):
        self.dummy = "dumb"
        NTdebug( "%r", self )
        
if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    cing.verbosity = verbosityError
    unittest.main() 
