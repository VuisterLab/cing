from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.helper import compareVersionTuple
from cing.Libs.helper import detectCPUs
from cing.Libs.helper import getSvnRevision
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def test_GetSvnRevision(self):
        x = getSvnRevision()
        nTdebug("x: %s" % val2Str(x,"%d"))
#        self.assertTrue(x>500) # no need to complain.

    def test_detectCPUs(self):
        x = detectCPUs()
        nTdebug("detectCPUs: %s" % x)
        self.assertTrue(x)

#    2   > 1     1
#    1   < 2     0
#    1   < 2    -1
#    1,2 > 1     1
#    Return None on error.
    def test_compareVersionTuple(self):
        cing.verbosity = verbosityDebug
        nTdebug("\nTesting %s" % getCallerName())
        inputLoL = [ 
                     [(2,),(1,)],                    
                     [(1,),(1,)],                    
                     [(1,),(2,)],                    
                     [(1,2),(1,2)],                    
                     [(1,2),(1,)],                    
                     [(1,2),(2,)],                
                     [(2,),(1,1)],                
                     [(2,),(2,1)],                
        ]
        expectedList = [ 1,0,-1,0,1,-1,1,-1]
        for i, inputList in enumerate( inputLoL ):
            nTdebug("Testing input list %d: %s" % (i,str(inputList)))
            result = compareVersionTuple( inputList[0], inputList[1])
            self.assertEqual( result, expectedList[i])
        # end for
    # end def                
# end class

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
