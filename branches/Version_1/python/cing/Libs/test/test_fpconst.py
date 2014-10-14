from cing import verbosityDebug
from cing import verbosityError
from cing.Libs.fpconst import * #@UnusedWildImport
from unittest import TestCase
import cing
import unittest

class AllChecks(TestCase):

    def testIsSomething(self):
        self.assertFalse(isNaN(PosInf))
        self.assertFalse(isNaN(NegInf))
        self.assertTrue(isNaN(NaN))
        self.assertFalse(isNaN(1.0))
        self.assertFalse(isNaN(-1.0))


        self.assertTrue(isInf(PosInf))
        self.assertTrue(isInf(NegInf))
        self.assertFalse(isInf(NaN))
        self.assertFalse(isInf(1.0))
        self.assertFalse(isInf(-1.0))

        self.assertFalse(isFinite(PosInf))
        self.assertFalse(isFinite(NegInf))
        self.assertFalse(isFinite(NaN))
        self.assertTrue(isFinite(1.0))
        self.assertTrue(isFinite(-1.0))

        self.assertTrue(isPosInf(PosInf))
        self.assertFalse(isPosInf(NegInf))
        self.assertFalse(isPosInf(NaN))
        self.assertFalse(isPosInf(1.0))
        self.assertFalse(isPosInf(-1.0))

        self.assertFalse(isNegInf(PosInf))
        self.assertTrue(isNegInf(NegInf))
        self.assertFalse(isNegInf(NaN))
        self.assertFalse(isNegInf(1.0))
        self.assertFalse(isNegInf(-1.0))

if __name__ == "__main__":
    cing.verbosity = verbosityError
    cing.verbosity = verbosityDebug
    unittest.main()
