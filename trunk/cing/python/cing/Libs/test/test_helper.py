from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.helper import detectCPUs
from cing.Libs.helper import getSvnRevision
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def test_GetSvnRevision(self):
        x = getSvnRevision()
        NTdebug("x: %s" % val2Str(x,"%d"))
#        self.assertTrue(x>500) # no need to complain.

    def test_detectCPUs(self):
        x = detectCPUs()
        NTdebug("detectCPUs: %s" % x)
        self.assertTrue(x)

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
