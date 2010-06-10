from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.helper import getSvnRevision
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def test_GetSvnRevision(self):
        x = getSvnRevision()
        NTdebug("x: %s" % val2Str(x,"%d"))
#        self.assertTrue(x>500) # no need to complain.

if __name__ == "__main__":
    cing.verbosity = verbosityError
    cing.verbosity = verbosityDebug
    unittest.main()
