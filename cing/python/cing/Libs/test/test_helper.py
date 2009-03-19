from cing import verbosityDebug
from cing import verbosityError
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import val2Str
from cing.Libs.helper import getSvnRevision
from unittest import TestCase
import cing
import unittest

class AllChecks(TestCase):

    def test_GetSvnRevision(self):
        x = getSvnRevision()
        NTdebug("x: %s" % val2Str(x,"%d"))
        self.assertTrue(x>500)

if __name__ == "__main__":
    cing.verbosity = verbosityError
    cing.verbosity = verbosityDebug
    unittest.main()
