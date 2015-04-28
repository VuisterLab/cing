'''
Created on Dec 21, 2010

@author: jd
'''
from cing import cingDirTestsData #@UnusedImport
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.required.reqCcpn import CCPN_STR
from matplotlib import mlab
from nose.plugins.skip import SkipTest
from unittest import TestCase
import unittest

# Import using optional plugins.
try:
    from cing.PluginCode.Ccpn import Ccpn #@UnusedImport needed to throw a ImportWarning so that the test is handled properly.
    from cing.Scripts.FC.utils import getBmrbCsCountsFromFile
except ImportWarning, extraInfo: # Disable after done debugging; can't use nTdebug yet.
    print "Got ImportWarning %-10s Skipping unit check %s." % ( CCPN_STR, getCallerFileName() )
    raise SkipTest(CCPN_STR)
# end try

class AllChecks(TestCase):
    'Test case'
    def test_Median(self):
        'test median'
# Wiki: If there is an even number of observations, then there is no single middle value; the median is then usually defined to be the 
# mean of the two middle values.[1][2]      
        lol = [ 
#               [], # fails
               [1.2],
               [1.0, 2.0], # Get 1.5 (matplotlib 1.0.1 or 2.0 (matplotlib 0.99.3) 
               [1.0, 2.0, 4.0],
               ]
        expectedMedianList              = [ 1.2, 1.5, 2.0] # matplotlib 1.0.1
        expectedMedianListOldMatplotlib = [ 1.2, 2.0, 2.0] # matplotlib 0.99.3
        for i,floatList in enumerate(lol):
            ml = mlab.prctile(floatList,[50])
            nTdebug("Found: %s and expected (by new matplotlib): %s" % (ml[0], expectedMedianList[i]))
            if ml[0] != expectedMedianList[i]:
                self.assertEqual(ml[0], expectedMedianListOldMatplotlib[i])
        # end for
    # end def
        
    def test_GetBmrbCsCountsFromFile(self):
        'test getting BMRB CS counts from file.'
        useVersion = '2'

        expectedLoL = [
            [ 4020, '1brv', {'1H':  183, '13C':   73}],
#            [ 4141, '1nk2', {'1H':  840, '13C':  291, '15N':  100, '31P':   18}], # BMRB 2.1 file reports no 1H in overview
#            [15381, '2jsx', {'1H':  443, '13C':  266, '15N':   85}],              # BMRB 2.1 file reports 561 1H instead of the 443 present
#            [16409, '',     {'113Cd':  999}], # absent in PDB.
        ]

        for bmrb_id, pdb_id, expected in expectedLoL:
            nTmessage("Looking at %s %s" % (bmrb_id, pdb_id))
            inputStarFile = os.path.join( cingDirTestsData, 'bmrb','2.1.1','bmr%s.str' )
            if useVersion == '3':
                inputStarFile = os.path.join( cingDirTestsData, 'bmrb','3.0.8.34','bmr%s.str' )
            inputStarFile = inputStarFile % bmrb_id # only in Python ;-)
            assignmentCountMap = getBmrbCsCountsFromFile(inputStarFile)
            self.assertTrue( assignmentCountMap )
            for key in assignmentCountMap.keys():
                value = assignmentCountMap[key]
                if value == 0:
                    continue
                self.assertEqual( value, expected[key])
        # end for
# end class

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()