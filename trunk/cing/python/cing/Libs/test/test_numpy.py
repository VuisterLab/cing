"""
Unit test execute as:
python -u $CINGROOT/python/cing/Libs/test/test_NTplotDihedral2D.py
"""
from cing.Libs.NTutils import * #@UnusedWildImport
from numpy import * #@UnusedWildImport
from numpy.testing.utils import assert_equal
from unittest import TestCase
import unittest

class AllChecks(TestCase):
    'Test case.'
    def test_ConvoluteNumpy(self):
        "Try to test numpy's matrices"
        hist1 = [ 0, 1, 2]
        hist2 = [10, 21, 22]
#        m1 = mat(hist1)
        m1 = mat(hist1)
        m2 = transpose( mat(hist2))
#        m2 = mat( [[10],[21],[22] ] )
        mr = multiply(m1,m2)
        nTdebug("%s" % mr)
        expected = matrix([[ 0, 10, 20],
                            [ 0, 21, 42],
                            [ 0, 22, 44]])
        assert_equal(mr, expected)

if __name__ == "__main__":
    cing.verbosity = cing.verbosityDebug
    unittest.main()
