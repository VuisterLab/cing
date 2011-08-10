"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_MacroExternals.py
"""
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.MacroExternals import mapValueToMolmolColor
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def testMapValueToMolmolColor(self):
        # test blue, red, yellow; in rgb:
        # 0 0 0, 1 0 0, 1 1 0
        valueList = [ 0., .5, 1. ]
        molmolColorExpectedList = [ '0.0 0.0 1.0', '1.0 0.0 0.0', '1.0 1.0 0.0' ]
        for i,v in enumerate(valueList):
#            nTdebug("i,v: %s %s" % (i,v))
            r = mapValueToMolmolColor(v, 0, 1, False)
            self.assertEquals( r, molmolColorExpectedList[i] )

        valueList = [ -3., -1., 1. ]
        molmolColorExpectedList = [ '0.0 0.0 1.0', '1.0 0.0 0.0', '1.0 1.0 0.0' ]
        for i,v in enumerate(valueList):
#            nTdebug("i,v: %s %s" % (i,v))
            r = mapValueToMolmolColor(v, -3., 1., False)
            self.assertEquals( r, molmolColorExpectedList[i] )

        # Reverse colors
        valueList = [ 0., .5, 1. ]
        molmolColorExpectedList = [ '1.0 1.0 0.0', '1.0 0.0 0.0', '0.0 0.0 1.0' ]
        for i,v in enumerate(valueList):
#            nTdebug("i,v: %s %s" % (i,v))
            r = mapValueToMolmolColor(v, 0, 1, True)
            self.assertEquals( r, molmolColorExpectedList[i] )

        # test outlier messaging.
        msgHol = MsgHoL()
        valueList = [ 9., 99., 999. ]
        for i,v in enumerate(valueList):
            r = mapValueToMolmolColor(v, 0, 1, False, msgHol=msgHol)
        msgHol.showMessage(max_warnings=1)

    def testPyMolIntegration(self):
        pass

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
