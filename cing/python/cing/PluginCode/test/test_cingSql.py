"""
Unit test execute as:
python $CINGROOT/python/cing/Libs/test/test_cingSql.py
"""

from cing import verbosityDebug
from cing.Libs.NTutils import NTdebug
from cing.PluginCode.cingSql import cingSql
from cing.PluginCode.sqlAlchemy import csqlAlchemy
from unittest import TestCase
import cing
import unittest

class AllChecks(TestCase):

    def test_CingSql(self):
        cSql = cingSql()
        self.assertFalse(cSql.connect())
        nextId = cSql.getNextSequenceId()
        NTdebug("Got nextId: %d" % nextId)
        self.assertTrue( nextId )

    def tttest_SqlAlchemy(self):
        csql = csqlAlchemy()
        self.assertFalse(csql.connect())
#        nextId = cSql.getNextSequenceId()
#        NTdebug("Got nextId: %d" % nextId)
#        self.assertTrue( nextId )


if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()


