"""
Unit test execute as:
python -u $CINGROOT/python/cing/Libs/test/test_NTutils4.py
"""

from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import switchOutput
from unittest import TestCase
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import toPoundedComment
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

    def testRmsNTlist(self):
        serie = NTlist()
        serie.append( 0.0 )
        rms = serie.rms()
        self.assertEquals(rms, 0.0)
        serie.append( 1.0 )
        rms = serie.rms()
        self.assertAlmostEquals(rms, 0.707, 3)
        serie.append( 2.0 )
        rms = serie.rms()
        self.assertAlmostEquals(rms, 1.291, 3)

    def testToPoundedComment(self):
        # Note the test for an empty line is included.
        str = """a
b
"""
        expectedOutput = """# a
# b
# """
        self.assertEquals(expectedOutput, toPoundedComment(str))


if __name__ == "__main__":
    cing.verbosity = cing.verbosityDebug
    unittest.main()
