"""
Unit test execute as:
python -u $CINGROOT/python/cing/Libs/test/test_NTplotDihedral2D.py
"""

from cing import verbosityDebug
from cing import verbosityError
from cing.Libs.NTutils import NTdebug
from pylab import * #@UnusedWildImport
from unittest import TestCase
import cing
import unittest

class AllChecks(TestCase):

    def testConvoluteNumpy(self):
        hist1 = [ 0, 1, 2]
        hist2 = [10, 21, 22]
        m1 = mat(hist1)
        m2 = mat(hist2).transpose()
#        m2 = mat( [[10],[21],[22] ] )
        mr = multiply(m1,m2)
        NTdebug("%s" % mr)
        _expecting = """
matrix([[ 0, 10, 20],
        [ 0, 21, 42],
        [ 0, 22, 44]])
"""


if __name__ == "__main__":
    cing.verbosity = verbosityError
    cing.verbosity = verbosityDebug
    unittest.main()
