"""
Unit test execute as:
python -u $CINGROOT/python/cing/Libs/test/test_NTutils4.py
"""

from cing.Libs.NTutils import * #@UnusedWildImport
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def tttestSwitchOutput(self):
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
        serie.append(0.0)
        rms = serie.rms()
        self.assertEquals(rms, 0.0)
        serie.append(1.0)
        rms = serie.rms()
        self.assertAlmostEquals(rms, 0.707, 3)
        serie.append(2.0)
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


    def testNTlistRemoveDuplicates(self):
        # Note the test for an empty line is included.
        x = NTlist()
#        x.removeDuplicates()
#        self.assertFalse(x)
        n = 5000
        y = range(n)
        x.addList(['a', 'b', 'b', 'c'])
        x.addList(y)
        # For n = 1000 this takes
        # 0  0.9 seconds
        # 1  0.8
        # 2  0.007
        # For n = 5000 this takes
        # 0  21.0 seconds
        # 1  ??
        # 2  0.035 (linear)
        x.removeDuplicates(useVersion = 2)
        self.assertTrue(len(x) == n + 3)
#        x.removeDuplicates()
#        self.assertTrue( len(x) == 3)

    def testNTlistSort(self):
        x = NTlist()
        y = range(5)
        x.addList(y)
        x.sort()
        y.sort()
        list.sort(x)
        list.sort(y)

    def testNTlistLenRecursive(self):
        x = NTlist()
        y = NTlist()
        z = NTlist()
        x.append(y)
        x.append(z)
        x.append(100)
        y.append(200)
        y.append(300)
        self.assertEquals( x.lenRecursive(), 3)
    def testGetDeepAvgByKeys(self):
        d=NTdict()
        l = NTlist()
        d['key'] = l
        l.append('abc')
        l.append('abc')
        x = d.getDeepAvgByKeys('key')
#        print 'x=', x
        self.assertEquals( x, 'abc')

        # Fraction by default needs to be 1.0; complete consensus
        l.append('def')
        x = d.getDeepAvgByKeys('key')
        self.assertEquals( x, False)

        # Should crash on None element
        l.append(None)
        x = d.getDeepAvgByKeys('key')
        self.assertEquals( x, False)

        x = l.getConsensus(minFraction=0.5)
        self.assertEquals( x, 'abc')

    def testGetDeepByKeysOrAttributes(self):
        value = 123
        d = {}
        keyList = 'a b c'.split()
        setDeepByKeys(d, value, *keyList)
        NTdebug("complex object: %s" % d)
        valueOut = getDeepByKeysOrAttributes(d,*keyList)
        self.assertEquals(value,valueOut)
        keyList = [ 'a.b', 'c' ]
        valueOut = getDeepByKeysOrAttributes(d,*keyList)
        self.assertEquals(value,valueOut)
        keyList = [ 'a.b.', 'c' ] # extra dot should mess this up.
        valueOut = getDeepByKeysOrAttributes(d,*keyList)
        self.assertFalse(valueOut) # None will evaluate to False as well.

if __name__ == "__main__":
    cing.verbosity = cing.verbosityDebug
    unittest.main()
