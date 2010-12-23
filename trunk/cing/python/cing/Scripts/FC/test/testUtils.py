'''
Created on Dec 21, 2010

@author: jd
'''
from cing import cingDirTestsData #@UnusedImport
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Scripts.FC.utils import getBmrbCsCountsFromFile
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def testGetBmrbCsCountsFromFile(self):
        useVersion = '2'

        bmrb_id = 4020
        inputStarFile = os.path.join( cingDirTestsData, 'bmrb','2.1.1','bmr%s.str' )
        if useVersion == '3':
            inputStarFile = os.path.join( cingDirTestsData, 'bmrb','3.0.8.34','bmr%s.str' )
        inputStarFile = inputStarFile % bmrb_id # only in Python ;-)
        assignmentCountMap = getBmrbCsCountsFromFile(inputStarFile)
        self.assertTrue( assignmentCountMap )

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    cing.verbosity = verbosityDebug
    unittest.main()