"""
Unit test execute as:
python -u $CINGROOT/python/cing/Libs/test/test_NTutils5.py
"""

from cing import cingDirTmp
from cing import cingRoot
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.disk import globLast
from numpy import * #@UnusedWildImport
from unittest import TestCase
import unittest

class AllChecks(TestCase):
    os.chdir(cingDirTmp)
    def testGetKeyWithLargestCount(self):

        testList = [
            [ ('H', 'H', 'H'), 1.0, False, 'H'], # defaults
            [ ('H', 'H', 'S'), 1.0, False,  False], # all need to be the same
            [ ('H', 'H', 'S'), 1.0, True,  'H'], # just taking the most common
            [ ('H', 'H', 'S'), 0.5, False,  'H'], # just taking the most common
]
        for testTuple in testList:
            testList, minFraction, useLargest, testResult = testTuple
#            NTdebug("Testing %s" % `testTuple`)
            testListNT = NTlist()
            testListNT += testList
            self.assertEquals(testListNT.getConsensus(minFraction=minFraction,useLargest=useLargest),testResult)

    def testCircularAverageOfTwoDihdedrals(self):
# VB van cing procheck routines
#A 189 GLN   0.243   0.071   0.164   0.660   0.153   0.362   1.840   6.256  -0.73  -1.05 999.90  -0.89

        lol = [  [  0.243, 0.071, 0.153 ],
                 [  0.164, 0.660, 0.362 ],
                 [ 0.0, 0.0, 0.0], # extremes
                 [ 1.0, 1.0, 1.0], # extremes
                 [ 0.0, 1.0, 0.293], # doesn't really make sense to JFD but here it is.
                  ]

        for cycle in lol:
            cv1, cv2, cav = cycle
            angleList = NTlist()
            angleList.append(cv1)
            angleList.append(cv2)
            circularVariance = NTcVarianceAverage(angleList)
            self.assertAlmostEqual(circularVariance, cav, places = 3)

    def testGetEnsembleAverageAndSigmaFromHistogram(self):
        n = 6
        x = 10.
        nn = n * n
        m = zeros(nn).reshape(n,n)
#        m[4,4] = x
        m[5,3] = x
#[[ 0.,  0.,  0.,  0.,  0.,  0.],
# [ 0.,  0.,  0.,  0.,  0.,  0.],
# [ 0.,  0.,  0.,  0.,  0.,  0.],
# [ 0.,  0.,  0.,  0.,  1.,  0.],
# [ 0.,  0.,  0.,  0.,  0.,  0.],
# [ 0.,  0.,  1.,  0.,  0.,  0.]]
        c_av, c_sd, hisMin, hisMax = getEnsembleAverageAndSigmaFromHistogram(m) #@UnusedVariable
        self.assertEqual( c_av, x) # weird average

        c_av, c_sd, hisMin, hisMax = getArithmeticAverageAndSigmaFromHistogram(m) #@UnusedVariable
        self.assertEqual( c_av, x/nn) # huge difference.


    def testGrep(self):
        fn = 'toGrepFile.txt'
        writeTextToFile(fn, 'Hello world\nThis is a special line\nAnd this isnot')
        resultList = []
        status = grep(fn, 'mismatch', resultList=resultList, doQuiet=True)
        self.assertEquals( status, 1 )
        resultList = []
        status = grep(fn, 'special', resultList=resultList, doQuiet=True)
        self.assertEquals( status, 0 )
        resultList = []
        status = grep(fn, 'SPECIAL', resultList=resultList, doQuiet=True, caseSensitive=False)
        self.assertEquals( status, 0 )


    def testAppendFromTable(self):
        myTable = [ (1,'a'), (2, 'b') ]
        myDict = NTdict()
#        myDictExpected = NTdict(1='a')        not allowed to have an integer as the key in this specification.
        myDictExpected = NTdict()
        myDictExpected[1] = 'a'
        myDictExpected[2] = 'b'
        myDict.appendFromTable( myTable, 0, 1)
        self.assertTrue( myDict.isEquivalent( myDictExpected ))

    def testTimedelta2HoursMinutesAndSeconds(self):
        tList = [ 0, 601.1, 136741.0 ]
        tExpected = [ (0,0,0), (0,10,1), (37,59,1) ]
        for i,t in enumerate(tList):
            self.assertEquals(timedelta2HoursMinutesAndSeconds(t), tExpected[i])
    def testNTlist(self):
        ntList = NTlist([7,8,9])
        NTdebug("ntList: " + str(ntList) +"  length: %s" % len(ntList))
        ntList.clear()
        NTdebug("ntList: " + str(ntList) +"  length: %s" % len(ntList))

    def testTruth(self):
        inputList = """t True  y yes 1 2 -1
                       f False n no  0 0  0
                    """.split()
        resultList = [1,1,1,1,1,1,1,
                      0,0,0,0,0,0,0]
        for i, inputStr in enumerate(inputList):
#            NTdebug("Test: %d" % i)
            self.assertEquals( stringMeansBooleanTrue(inputStr), resultList[i]==1)

    def testAsci2list(self):
        # Still fails to do -3 - -1 to represent.
        inputList = """1-3
                      -3-1
                      1,2,5-8,11,20-22
                    """.split()
        resultLoL = [
                      '[1, 2, 3]',
                      '[-3, -2, -1, 0, 1]',
                      '[1, 2, 5, 6, 7, 8, 11, 20, 21, 22]',
                     ]
        for i, inputStr in enumerate(inputList):
            NTdebug("testAsci2list: %d" % i)
            resultStr = str(asci2list(inputStr))
            self.assertEquals( resultStr, resultLoL[i])

    def testGetDateTimeStampForFileName(self):
        globPattern = os.path.join(cingRoot, '*.txt')
        lastFile = globLast(globPattern)
        dateTimeObject = getDateTimeFromFileName(lastFile)
        dateTimeString = getDateTimeStampForFileName(lastFile)
        NTdebug('lastFile: %s dateTimeObject %s' % (lastFile, dateTimeObject))
        NTdebug('lastFile: %s dateTimeString %s' % (lastFile, dateTimeString))
        self.assertTrue(dateTimeObject)
        self.assertTrue(dateTimeObject.year >= 2009)
#        self.assertEquals(extension, '.txt')

if __name__ == "__main__":
    cing.verbosity = cing.verbosityDebug
    unittest.main()
