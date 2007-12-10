from cing import cingDirTestsTmp
from cing.STAR.testAll import testAll
from unittest import TestCase
import os
import unittest


class AllChecks(TestCase):
        
    def testparse(self):
        """STAR test routines"""
        os.chdir(cingDirTestsTmp)
        testAll()
    
if __name__ == "__main__":
    unittest.main()
