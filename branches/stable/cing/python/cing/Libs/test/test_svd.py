"""
Unit test execute as:
python -u $CINGROOT/python/cing/Libs/test/test_svd.py
"""

from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.svd import * #@UnusedWildImport
from unittest import TestCase
import unittest

class AllChecks(TestCase):
    pass
# end class
            
if __name__ == "__main__":
    cing.verbosity = cing.verbosityDebug
    unittest.main()
