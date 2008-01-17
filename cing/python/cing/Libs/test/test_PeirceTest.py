from cing.Libs import peirceTest
from unittest import TestCase
import unittest

class AllChecks(TestCase):
        
    def testPeirceTest1(self):        
        values = [101.2, 90.0, 99.0, 102.0, 103.0, 100.2, 89.0, 98.1, 101.5, 102.0]
        vOld,_oOld = peirceTest.peirceTestOld( values )
#        print 'v=',vOld
#        print vOld.av, vOld.sd
#        print 'o=',_oOld
#        
        v,_o = peirceTest.peirceTest( values )
#        print 'v=',v
#        print v.av, v.sd
#        print 'o=',o
    
        self.assertTrue( vOld == v )

    def testPeirceTest2(self):
        # A stable array just longer than the reference data used in the test.
        values = []        
        for i in range(0,1000):
            values.append(1)        
#        printDebug("n="+`len(values)`)
        for i in range(0,10):
            values[i] = 2        
        # Will only note first 9 outliers
        vOld,oOld = peirceTest.peirceTestOld( values )
#        print 'v=',vOld
#        print vOld.av, vOld.sd
#        print 'o=',oOld
#        
        v,o = peirceTest.peirceTest( values )
#        print 'v=',v
#        print v.av, v.sd
#        print 'o=',o
    
        self.assertFalse( vOld == v )
        self.assertFalse( oOld == o )
                
    def testPeirceTest3(self):
        #Note the difference between array sizes 17 and 18. 
        #No outliers identified at 18 but 7 outliers made the cutoff at size 17
        values = []    
        n = 200   # Default value 200. Tested up to 10,000 once before.
        m = 10    # Only tested with default value 10.
        for i in range(0,n):
            values.append(1)        
#        printDebug("n="+`len(values)`)
        for i in range(0,m):
            values[i] = 2
                
        while n > 3:
            values = values[:n]        
            _v,o = peirceTest.peirceTest( values )
#            print 'number of outliers at size: '+`n`+ ' =',len(o)
            self.assertTrue(len(o)<=m)
            n -= 1
                    
if __name__ == "__main__":
    unittest.main()
