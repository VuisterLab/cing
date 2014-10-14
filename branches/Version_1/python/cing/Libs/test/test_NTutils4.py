"""
Unit test execute as:
python -u $CINGROOT/python/cing/Libs/test/test_NTutils4.py
"""

from cing.Libs.NTutils import * #@UnusedWildImport
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def testSwitchOutput(self):
        x1 = "Message to debug"
        x2 = "Message to debug 2 should not show up."
        x3 = "Message to debug 3"


#        print x1
        nTdebug(x1)
        switchOutput(showOutput = False, doStdOut = True)
#        print x2 # should not show up.and doesn't
        nTdebug(x2) # TODO: prevent this message from showing up.
        switchOutput(showOutput = True, doStdOut = True)
#        print x3
        nTdebug(x3)

    # enable next test when the switchOutput can be used.
#    def testTrace(self):
#        try:
#            raise ImportError
#        except:
#            traceBackString = format_exc()
#            nTerror(traceBackString)

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
        strMsg = """a
b
"""
        expectedOutput = """# a
# b
# """
        self.assertEquals(expectedOutput, toPoundedComment(strMsg))


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

    def testLenRecursive(self):
        x = NTdict(a=None)
        self.assertEquals( x.lenRecursive(), 1)
        x.b = NTlist(1,2)
        self.assertEquals( x.lenRecursive(), 3)
        x.c = {'foo': {'bar': [ 1,2 ]}} # Can be any mix of elements. Only finals count
        self.assertEquals( x.lenRecursive(), 5)
        x.d = ( 3, None, 5) # even tuples
        self.assertEquals( x.lenRecursive(), 8)

    def testLenRecursiveCyclic(self):
        x = NTdict(a=None)
        y = NTdict(b=x)
        self.assertEquals( y.lenRecursive(), 1)
        x.cyclic = y        
        self.assertRaises( RuntimeError, y.lenRecursive, max_depth = 999 ) # 99 is allowed and would fail this unit check.       
        self.assertEquals( y.lenRecursive(max_depth = 0), 1) # y.b
        self.assertEquals( y.lenRecursive(max_depth = 1), 2) # y.b.a
        self.assertEquals( y.lenRecursive(max_depth = 2), 2) # y.b.a and y.b.cyclic ?
        self.assertEquals( y.lenRecursive(max_depth = 3), 3) # y.b.a, y.b.cyclic, and y.b.cyclic.b ?
        self.assertEquals( y.lenRecursive(max_depth = 5), 4) 
        self.assertEquals( y.lenRecursive(max_depth = 9), 6) 
        self.assertEquals( y.lenRecursive(max_depth = 99),51) 
        
        z = [[1,2],[3,4,5]]
        self.assertEquals( lenRecursive(z, max_depth = 0),2) 
        self.assertEquals( lenRecursive(z, max_depth = 1),5) 
        self.assertEquals( lenRecursive(z, max_depth = 2),5) 

    def testGetDeepAvgByKeys(self):
        d=NTdict()
        a = NTlist()
        d['key'] = a
        a.append('abc')
        a.append('abc')
        x = d.getDeepAvgByKeys('key')
#        print 'x=', x
        self.assertEquals( x, 'abc')

        # Fraction by default needs to be 1.0; complete consensus
        a.append('def')
        x = d.getDeepAvgByKeys('key')
        self.assertEquals( x, False)

        # Should crash on None element
        a.append(None)
        x = d.getDeepAvgByKeys('key')
        self.assertEquals( x, False)

        x = a.getConsensus(minFraction=0.5)
        self.assertEquals( x, 'abc')

    def testGetDeepByKeysOrAttrS(self):
#        cing.verbosity = cing.verbosityDebug
        d = {}
        keyList = 'a b c'.split()
        setDeepByKeys(d, None, *keyList)
        nTdebug("Simpler object: %r" % d)

    def testGetDeepByKeysOrAttributes(self):
#        cing.verbosity = cing.verbosityDebug
        value = 123
        d = {}
        keyList = 'a b c'.split()
        setDeepByKeys(d, value, *keyList)
        nTdebug("complex object: %s" % d)
        valueOut = getDeepByKeysOrAttributes(d,*keyList)
        self.assertEquals(value,valueOut)
        keyList = [ 'a.b', 'c' ]
        valueOut = getDeepByKeysOrAttributes(d,*keyList)
        self.assertEquals(value,valueOut)
        keyList = [ 'a.b.', 'c' ] # extra dot should mess this up.
        valueOut = getDeepByKeysOrAttributes(d,*keyList)
        self.assertFalse(valueOut) # None will evaluate to False as well.

    def testGetDeepByKeysOrAttributes2(self):
#        cing.verbosity = cing.verbosityDebug

        inputTable = [['a'],['b']]
        expected = NTdict( a=None, b=None )
        result = NTdict()
#        idxColumnKeyList = [0]
        idxColumnKeyList = [] # indicates all.
        result.appendFromTableGeneric(inputTable, *idxColumnKeyList)
        nTdebug("Created: %r" % result)
        self.assertTrue( expected.isEquivalent(result ))

        # 2D
        inputTable = [['a','foo'],['b','bar']]
        expected = NTdict( a='foo', b='bar' )
        result = NTdict()
#        idxColumnKeyList = [0, 1]
        result.appendFromTableGeneric(inputTable, *idxColumnKeyList)
        nTdebug("Created: %r" % result)
        self.assertTrue( expected.isEquivalent(result ))

#        # 3D
        inputTable = [['a','foo', 'abba'],['b','bar', 'waterloo']]
        expected = { 'a':{ 'foo':'abba'}, 'b':{ 'bar':'waterloo'}}
        result = NTdict()
#        idxColumnKeyList = [0, 1,2]
        result.appendFromTableGeneric(inputTable, *idxColumnKeyList)
        nTdebug("Created: %r" % result)
        self.assertTrue( result.isEquivalent(expected ))
##        self.failUnlessRaises( AttributeError, expected.isEquivalent(result )) Dont care why this fails....

        nTdebug("3D done but first transposing")
        result = NTdict()
        inputTable = [['a','b'],['foo','bar'],['abba','waterloo'],]
        expected = { 'a':{ 'foo':'abba'}, 'b':{ 'bar': 'waterloo'}}        
        result.appendFromTableGeneric(inputTable, *idxColumnKeyList, invertFirst=True)
        nTdebug("Created: %r" % result)
        self.assertTrue( result.isEquivalent( expected ))
##        self.failUnlessRaises( AttributeError, expected.isEquivalent(result )) Dont care why this fails....

        nTdebug("3D transposing and added column")
        result = NTdict()
        x = 'abba' # Needs to evaluate to True
        inputTable = [['a','b'],['foo','bar']]
        expected = { 'a':{ 'foo':x}, 'b':{ 'bar': x}}        
        result.appendFromTableGeneric(inputTable, *idxColumnKeyList, invertFirst=True, appendBogusColumn=x)
        nTdebug("Created: %r" % result)
        self.assertTrue( result.isEquivalent( expected ))
##        self.failUnlessRaises( AttributeError, expected.isEquivalent(result )) Dont care why this fails....
    # end def


    def test_transpose(self):
#        Compute the transpose of a matrix.
        input = [ [1,2,3], [4,5,6] ]
        expected = [ [1,4], [2,5], [3,6] ]
        output = transpose(input)
        self.assertEquals(output, expected)
    # end def
# end class

if __name__ == "__main__":
    cing.verbosity = cing.verbosityDebug
    unittest.main()
