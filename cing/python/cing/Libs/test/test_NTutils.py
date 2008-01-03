"""
Unit test execute as:
python $cingPath/Scripts/test/test_cyana2cing.py
"""
from cing import cingDirTestsData
from cing.Libs.NTutils import find
from unittest import TestCase
import os
import unittest

class AllChecks(TestCase):
        
    def testFind(self):
        """recursive finder"""
        
        self.assertTrue( os.path.exists( cingDirTestsData) and os.path.isdir(cingDirTestsData ) )
        self.failIf( os.chdir(cingDirTestsData), msg=
            "Failed to change to test directory for data: "+cingDirTestsData)
        namepattern, startdir = "CVS", cingDirTestsData
        for name in find(namepattern, startdir):
            print name
            
if __name__ == "__main__":
    unittest.main()
