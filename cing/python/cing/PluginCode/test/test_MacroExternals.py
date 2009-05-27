"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_MacroExternals.py
"""
from cing import verbosityDebug
from cing.PluginCode.MacroExternals import mapValueToMolmolColor
from unittest import TestCase
import cing
import unittest

class AllChecks(TestCase):

    def testMapValueToMolmolColor(self):
        # test blue, red, yellow; in rgb:
        # 0 0 0, 1 0 0, 1 1 0
        valueList = [ 0., .5, 1. ]
        molmolColorExpectedList = [ '0.0 0.0 1.0', '1.0 0.0 0.0', '1.0 1.0 0.0' ]
        for i,v in enumerate(valueList):
#            NTdebug("i,v: %s %s" % (i,v))
            r = mapValueToMolmolColor(v, 0, 1, False)
            self.assertEquals( r, molmolColorExpectedList[i] )

        valueList = [ -3., -1., 1. ]
        molmolColorExpectedList = [ '0.0 0.0 1.0', '1.0 0.0 0.0', '1.0 1.0 0.0' ]
        for i,v in enumerate(valueList):
#            NTdebug("i,v: %s %s" % (i,v))
            r = mapValueToMolmolColor(v, -3., 1., False)
            self.assertEquals( r, molmolColorExpectedList[i] )

        # Reverse colors
        valueList = [ 0., .5, 1. ]
        molmolColorExpectedList = [ '1.0 1.0 0.0', '1.0 0.0 0.0', '0.0 0.0 1.0' ]
        for i,v in enumerate(valueList):
#            NTdebug("i,v: %s %s" % (i,v))
            r = mapValueToMolmolColor(v, 0, 1, True)
            self.assertEquals( r, molmolColorExpectedList[i] )

    def testPyMolIntegration(self):
        pass

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
