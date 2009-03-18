"""
Unit test execute as:
python -u $CINGROOT/python/cing/Libs/test/test_NTutils4.py
"""

from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import switchOutput
from unittest import TestCase
import cing
import unittest

class AllChecks(TestCase):

    def testSwitchOutput(self):
        x1 = "Message to debug"
        x2 = "Message to debug 2 should not show up." 
        x3 = "Message to debug 3"

        
        print x1
        NTdebug(x1)
        switchOutput(showOutput = False, doStdOut = True)
        print x2 # should not show up.and doesn't 
        NTdebug(x2) # TODO: prevent this message from showing up.
        switchOutput(showOutput = True, doStdOut = True)
        print x3
        NTdebug(x3)

    # enable next test when the switchOutput can be used.
#    def testTrace(self):        
#        try:
#            raise ImportError
#        except:
#            traceBackString = format_exc()
#            NTerror(traceBackString)
    

if __name__ == "__main__":
    cing.verbosity = cing.verbosityDebug
    unittest.main()
