"""
Unit test execute as:
python -u $CINGROOT/python/cing/Libs/test/test_NTutils6.py
"""

from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from unittest import TestCase
import unittest

class AllChecks(TestCase):
    os.chdir(cingDirTmp)

    def testGetCallerName(self):
        self.failIf( getCallerName() != 'testGetCallerName')
        self.failIf( additionalTestRoutineByItself() != 'additionalTestRoutineByItself')
        
def additionalTestRoutineByItself():
    return getCallerName() 

if __name__ == "__main__":
    cing.verbosity = cing.verbosityDebug
    unittest.main()
