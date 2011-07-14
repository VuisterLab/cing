"""
Unit test execute as:
python -u $CINGROOT/python/cing/Libs/test/test_NTutils.py
"""

from cing import cingDirTmp
from cing import cingPythonDir
from cing.Libs.NTutils import * #@UnusedWildImport
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def testPrints(self):
#        nTexception("Now in testPrints")
#        nTerror("test")
        pass

    def testRemoveRecursivelyAttribute(self):
        testDict = { 0: 1, "ccpn": 77}
        self.assertEqual(len(testDict.keys()), 2)
        nTdebug(`testDict`)
        removeRecursivelyAttribute(testDict, "ccpn")
        self.assertEqual(len(testDict.keys()), 1)
        nTdebug(`testDict`)


    def test_NTutils(self):
        cingDirTmpTest = os.path.join( cingDirTmp, getCallerName() )
        mkdirs( cingDirTmpTest )
        self.failIf(os.chdir(cingDirTmpTest), msg =
            "Failed to change to test directory for files: " + cingDirTmpTest)
        namepattern, startdir = "test*.py", cingPythonDir # CVS is only for developers
        nameList = findFiles(namepattern, startdir)
        self.assertTrue(len(nameList) > 10)
#        for name in nameList:
#            print name


    def testCircularAverage(self):
        lol = [  [   5, 15, 10],
                [  345, 5, 355],
                 [   5, 345, 355],
                  [180, - 180, None],
                   [90, - 70, 10]]
        for cycle in lol:
            v1, v2, cav = cycle
            angleList = NTlist()
            angleList.append(v1)
            angleList.append(v2)
            result = angleList.cAverage(0, 360, 0, None)
            self.failUnless(result)
            circularAverage, _circularVariance, _n = result
            if cav != None:
                self.assertAlmostEqual(circularAverage, cav, places = 5)

    def testCircularAverage2(self):
        angleList = NTlist()
        angleList.append(1)
        result = angleList.cAverage(0, 360, 0, None)
        self.failUnless(result)
        circularAverage, _circularVariance, _n = result
        self.assertAlmostEqual(circularAverage, 1, places = 5)

    def testCircularAverage3(self):
        angleList = NTlist()
        result = angleList.cAverage(0, 360, 0, None)
        self.failUnless(result)
        _circularAverage, _circularVariance, _n = result


#        double[][] testValues = new double[][] {
#                {    5,  15,   10},
#                {  345,   5,   20},
#                 {   5, 345,  -20},
#                  {180, 180,    0},
#                   {90, -70, -160}
#        };

    def testCircularAverageOfTwoDihdedrals(self):
# VB van cing procheck routines
#A 189 GLN   0.243   0.071   0.164   0.660   0.153   0.362   1.840   6.256  -0.73  -1.05 999.90  -0.89

        lol = [  [  0.243, 0.071, 0.153 ],
                 [  0.164, 0.660, 0.362 ],
                 [ 0.0, 0.0, 0.0], # extremes
                 [ 1.0, 1.0, 1.0], # extremes
                 [ 0.0, 1.0, 0.293], # doesn't really make sense to JFD but here it is.
                 [ 0.0, 0.2, 0.0945], # same
                 [ None, 1.0, 1.0], # None for input is allowed.
                 [ None, 0.0, 0.0], # None for input is allowed.
                 [ None, None, None], # Returns None if all input is None
                  ]

        for cycle in lol:
            cv1, cv2, cav = cycle
            angleList = NTlist()
            angleList.append(cv1)
            angleList.append(cv2)
            circularVariance = nTcVarianceAverage(angleList)
            if circularVariance == None:
                self.assertEqual(circularVariance, cav)
            else:
                self.assertAlmostEqual(circularVariance, cav, places = 3)

    def testGeneral(self):
        s = NTdict(aap = 'foo', mies = 1)
        self.assertEqual( len(s.keys()), 2)
        s.setdefault('mies', 2)
        s.setdefault('kees', [])
        s.kees = [0, 1, 3]
        s.name = 'ss'
        self.assertEqual( len(s.keys()), 4) # aap mies kees name

        b = s.copy()
        self.assertEqual( len(b.keys()), 4)

        p = s.popitem()
        while p:
            p = s.popitem()
        s.update(b)


    def testNTaverage(self):
        myList = NTlist(4, 9, 11, 12, 17, 5, 8, 12, 14)
        (av, sd, n) = myList.average()
        nTdebug("av %s, sd %s, n %s" % (av, sd, n))
        self.assertAlmostEqual(av, 10.22, places = 1) # verified in Excel stddev function.
        self.assertAlmostEqual(sd, 4.18, places = 1)
        self.assertEquals(n, 9)

        myList = NTlist(1, None, 1, 1)
        (av, sd, n) = myList.average()
        nTdebug("av %s, sd %s, n %s" % (av, sd, n))
        self.assertAlmostEqual(av, 1.0, places = 1)
        self.assertAlmostEqual(sd, 0.0, places = 1)
        self.assertEquals(n, 3)

        myList = NTlist(1, 2)
        (av, sd, n) = myList.average()
        nTdebug("av %s, sd %s, n %s" % (av, sd, n))
        self.assertAlmostEqual(av, 1.5, places = 1)
        self.assertAlmostEqual(sd, 0.707, places = 2)
        self.assertEquals(n, 2)

        myList = NTlist(1)
        (av, sd, n) = myList.average()
        nTdebug("(one element) av %s, sd %f, n %s" % (av, sd, n))
        self.assertAlmostEqual(av, 1.0, places = 1)
        self.assertTrue(isNaN(sd))
        self.assertEquals(n, 1)

        myList = NTlist()
        (av, sd, n) = myList.average()
        nTdebug("av %s, sd %s, n %s" % (av, sd, n))
        self.assertTrue(isNaN(av))
        self.assertTrue(isNaN(sd))
        self.assertEquals(n, 0)

        myList = NTlist(0.0, 0.0, 0.0)
        (av, sd, n) = myList.average()
        nTdebug("av %s, sd %s, n %s" % (av, sd, n))
        self.assertEquals(av, 0)
        self.assertEquals(sd, 0)
        self.assertEquals(n, 3)

    def testValueToFormattedString(self):
        self.assertEquals(val2Str(None, "%5.2f", None), NaNstring)
        self.assertEquals(val2Str(None, "%5.2f", 5), "%5s" % NaNstring)
        self.assertEquals(val2Str(6.3, "%5.2f", 5), " 6.30")
        self.assertEquals(val2Str(6.3, "%.2f"), "6.30")
        self.assertEquals(val2Str(6.3, "%03d"), "006")
        self.assertEquals(val2Str("6.3", "%03d"), "006")
        self.assertEquals(val2Str("f6.3", "%03d"), None)
        self.assertEquals(val2Str(None, "%03d", useNanString=False), '')


    def testNTlistDifferenceIntersection(self):
        xL = NTlist( 'a', 'b' )
        yL = NTlist( 'b', 'c', 'c' )
        xLdiff = xL.difference(yL)
        self.assertEquals(xLdiff, ['a'])
        xLyLintersection = xL.intersection(yL)
        self.assertEquals(xLyLintersection, ['b'])
        xLyLunion = xL.union(yL) # Uses multi set semantics
        self.assertEquals(xLyLunion, ['a', 'b', 'c', 'c'])

    def _testSwitchOutput( self):
        """Note that this fails but used to work.
        Is this because it gets called upon importing the CCPN module already. Nop.?
        """
        nTdebug("Message to debug")
        nTerror("Intended message to error")
        switchOutput( showOutput=False, doStdOut=True, doStdErr=True)
        print "Message to regular sys.stdout should not be printed"
        nTdebug("Message to debug 2 should not be printed")
        nTerror("Message to error 2 should not be printed")
        switchOutput( showOutput=True, doStdOut=True, doStdErr=True)
        nTdebug("Message to debug 3")
        nTerror("Intended message to error 3")


if __name__ == "__main__":
    cing.verbosity = verbosityNothing
    cing.verbosity = verbosityDebug
#    cProfile.run('unittest.main()', 'fooprof')
#    p = pstats.Stats('fooprof')
#    p.sort_stats('time').print_stats(10)
#    p.sort_stats('cumulative').print_stats(40)
    unittest.main()
