"""
Unit test execute as:
python $CINGROOT/python/xplornih/test/test_anneal.py
"""
from cing import verbosityDebug
from unittest import TestCase
from xplorcing.Utils import getRandomSeed
import cing
import unittest

class AllChecks(TestCase):

    def test_getRandomSeed(self):
        self.assertTrue( getRandomSeed()>1 )

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
