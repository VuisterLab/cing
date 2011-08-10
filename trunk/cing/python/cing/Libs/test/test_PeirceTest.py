from cing.Libs import peirceTest
from unittest import TestCase
from cing import verbosityError
from cing import verbosityDebug
import cing
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
#        print 'o=',_o
    
        self.assertTrue( vOld == v )

    def testPeirceTest2(self):
        # A stable array just longer than the reference data used in the test.
        values = []        
        for i in range(0,1000):
            values.append(1)        
#        nTdebug("n=",len(values))
        for i in range(0,10):
            values[i] = 2        
        # Will only note first 9 outliers
        vOld,oOld = peirceTest.peirceTestOld( values )
#        print 'v=',vOld
#        print vOld.av, vOld.sd
#        print 'obj=',oOld
#        
        v,obj = peirceTest.peirceTest( values )
#        print 'v=',v
#        print v.av, v.sd
#        print 'obj=',obj
    
        self.assertFalse( vOld == v )
        self.assertFalse( oOld == obj )
                
    def testPeirceTest3(self):
        #Note the difference between array sizes 17 and 18. 
        #No outliers identified at 18 but 7 outliers made the cutoff at size 17
        values = []    
        n = 200   # Default value 200. Tested up to 10,000 once before.
        m = 10    # Only tested with default value 10.
        for i in range(0,n):
            values.append(1)        
#        nTdebug("n=", len(values))
        for i in range(0,m):
            values[i] = 2
                
        while n > 3:
            values = values[:n]        
            _v,obj = peirceTest.peirceTest( values )
#            print 'number of outliers at size: '+repr(n)+ ' =',len(obj)
            self.assertTrue(len(obj)<=m)
            n -= 1
                    
    def testPeirceTest4(self):
        values = []    
        n = 2   # Default value 200. Tested up to 10,000 once before.
        for i in range(n):
            values.append(i)        
                
        result = peirceTest.peirceTest( values )
        self.failUnless(result)
        v,obj = result
#        print 'number of outliers at size: '+repr(n)+ ' =',len(obj)
        self.assertTrue(len(v) == n)
        self.assertTrue(len(obj) == 0)
        
    def testPeirceTest5(self):
        values = [61.1080599488, 34.876110084, 63.0380528016, -37.3907919689, 55.7742201359, 158.950985878, 152.580838711, 159.962185469, 39.5242231825, 167.478815798, -45.1721895276, 150.966989049, 38.7181950131, 54.4126758063, 62.9191496902, -41.4928983793, 46.5057394648, -36.3803547969, -48.513237809, 61.4695459467]
                
        result = peirceTest.peirceTest( values )
        self.failUnless(result)
        v,obj = result
#        print 'number of outliers at size: '+repr(n)+ ' =',len(obj)
        self.assertTrue(len(v) == 10)
        self.assertTrue(len(obj) == 10)

                    
if __name__ == "__main__":
    cing.verbosity = verbosityError
    cing.verbosity = verbosityDebug
    unittest.main()
