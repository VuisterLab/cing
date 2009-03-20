"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_html.py
"""
from cing import verbosityDebug
from cing.PluginCode.html import HTML_TAG_PRE
from cing.PluginCode.html import HTML_TAG_PRE2
from cing.PluginCode.html import removePreTagLines
from unittest import TestCase
import cing
import unittest

class AllChecks(TestCase):

    def testRemovePreTagLines(self):
        spuriousSpaceMsg = 'something     with     many spaces'
        msg = '\n'.join( [HTML_TAG_PRE, spuriousSpaceMsg, HTML_TAG_PRE2 ])
        self.assertNotEquals( msg, spuriousSpaceMsg)
        self.assertEquals( removePreTagLines(msg), spuriousSpaceMsg)
        
if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
