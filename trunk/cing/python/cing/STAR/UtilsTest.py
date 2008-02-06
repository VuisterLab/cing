from cing.STAR.Utils import Lister
from unittest import TestCase
import Utils
import unittest



class AllChecks(TestCase, Lister):
        
    def testTranspose(self):
        m1 = [ [1,2], [3,4] ]
        m2 = [ (1,3), (2,4) ]        
        m1t= Utils.transpose(m1)
        self.assertTrue(m1t==m2)
    def testLister(self):
        self.dummy = "dumb"
        print self
        
if __name__ == "__main__":
    unittest.main() 
#    a = AllChecks()
#    a.testLister()