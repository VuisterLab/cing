from cing import verbosityDebug
from cing import verbosityError
from cing.Libs.NTutils import printDebug
from unittest import TestCase
import Utils
import cing
import unittest



class AllChecks(TestCase):
        
    def testTranspose(self):
        m1 = [ [1,2], [3,4] ]
        m2 = [ (1,3), (2,4) ]        
        m1t= Utils.transpose(m1)
        self.assertTrue(m1t==m2)
    def testLister(self):
        self.dummy = "dumb"
        printDebug( self )
        
if __name__ == "__main__":
    cing.verbosity = verbosityError
    cing.verbosity = verbosityDebug
    unittest.main() 
#    a = AllChecks()
#    a.testLister()