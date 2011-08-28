"""
Unit test execute as:
python -u $CINGROOT/python/cing/Libs/test/test_NTutils5.py
"""

from cing import cingDirTmp
from cing import cingRoot
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.disk import globLast
from cing.core.database import NTdb
from numpy import * #@UnusedWildImport
from unittest import TestCase
import unittest

class AllChecks(TestCase):
    cingDirTmpTest = os.path.join( cingDirTmp, 'test_NTutils5' )
    mkdirs( cingDirTmpTest )
    os.chdir(cingDirTmpTest)

    def testGetKeyWithLargestCount(self):

        testList = [
            [ ('H', 'H', 'H'), 1.0, False, 'H'], # defaults
            [ ('H', 'H', 'S'), 1.0, False,  False], # all need to be the same
            [ ('H', 'H', 'S'), 1.0, True,  'H'], # just taking the most common
            [ ('H', 'H', 'S'), 0.5, False,  'H'], # just taking the most common
]
        for testTuple in testList:
            testList, minFraction, useLargest, testResult = testTuple
            nTdebug("Testing %s" % repr(testTuple))
            testListNT = NTlist()
            testListNT += testList
            self.assertEquals(testListNT.getConsensus(minFraction=minFraction,useLargest=useLargest),testResult)

    def testCircularAverageOfTwoDih(self):
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
            circularVariance = nTcVarianceAverage(angleList)
            self.assertAlmostEqual(circularVariance, cav, places = 3)

    def testGetEnsembleAvAndSigHist(self):
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
        c_av, _c_sd, _hisMin, _hisMax = getEnsembleAverageAndSigmaHis(m)
        self.assertEqual( c_av, x) # weird average

        c_av, _c_sd, _hisMin, _hisMax = getArithmeticAverageAndSigmaHis(m)
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
        # First column is (1,'a')
        # First row is a header row (1,2)
        myDict = NTdict()
#        myDictExpected = NTdict(1='a')        not allowed to have an integer as the key in this specification.
        myDictExpected = NTdict()
        myDictExpected[1] = 'a'
        myDictExpected[2] = 'b'
        myDict.appendFromTable( myTable, 0, 1)
        self.assertTrue( myDict.isEquivalent( myDictExpected ))

    def testTimedelta(self):
        tList = [ 0, 601.1, 136741.0 ]
        tExpected = [ (0,0,0), (0,10,1), (37,59,1) ]
        for i,t in enumerate(tList):
            self.assertEquals(timedelta2Hms(t), tExpected[i])
    def testNTlist(self):
        ntList = NTlist([7,8,9])
#        nTdebug("ntList: " + str(ntList) +"  length: %s" % len(ntList))
        ntList.clear()
#        nTdebug("ntList: " + str(ntList) +"  length: %s" % len(ntList))

    def testTruth(self):
        inputList = """t True  y yes 1 2 -1
                       f False n no  0 0  0
                    """.split()
        resultList = [1,1,1,1,1,1,1,
                      0,0,0,0,0,0,0]
        for i, inputStr in enumerate(inputList):
#            nTdebug("Test: %d" % i)
            self.assertEquals( stringMeansBooleanTrue(inputStr), resultList[i]==1)

    def testAsci2list(self):
        
        _help = """
        Possible 5 situations:
        a      # 1 # positive int
        -a     # 2 # single int
        -a-b   # 3 #
        -a--b  # 4 #
        a-b    # 5 # most common
        """
        inputList = """
                      1
                      1-3
                      -3:1
                      -2--1
                      -2-1
                      -3
                      1,2,5-8,11,20-22
                      -20:-19,-2:-1,3:4
                    """.split()
        resultLoL = [
                                     '[1]',
                                     '[1, 2, 3]',
                      '[-3, -2, -1, 0, 1]',
                          '[-2, -1]',
                          '[-2, -1, 0, 1]',
                      '[-3]',
                                     '[1, 2, 5, 6, 7, 8, 11, 20, 21, 22]',
                      '[-20, -19, -2, -1, 3, 4]',
                     ]
        for i, inputStr in enumerate(inputList):
            nTdebug("testAsci2list: %d" % i)
            resultStr = str(asci2list(inputStr))
            self.assertEquals( resultStr, resultLoL[i])
        saveVerbosity = cing.verbosity
        cing.verbosity = cing.verbosityNothing
        result = asci2list('1--2') # will cause an error message and an empty return list.
        cing.verbosity = saveVerbosity
        self.assertEquals(len(result),0)


    def testGetDateTimeStampForFileName(self):
        globPattern = os.path.join(cingRoot, '*.txt')
        lastFile = globLast(globPattern)
        dateTimeObject = getDateTimeFromFileName(lastFile)
#        dateTimeString = getDateTimeStampForFileName(lastFile)
#        nTdebug('lastFile: %s dateTimeObject %s' % (lastFile, dateTimeObject))
#        nTdebug('lastFile: %s dateTimeString %s' % (lastFile, dateTimeString))
        self.assertTrue(dateTimeObject)
        self.assertTrue(dateTimeObject.year >= 2009)
#        self.assertEquals(extension, '.txt')

    def testSelectByItems(self):
#        E.g. if adl is the AtomDef NTlist
        byItems = ( 'type', 'C_VIN' )
        vadl = NTdb.allAtomDefs().selectByItems( *byItems )
#       vadl = adl.
        nTdebug("%s in db: %s" % (byItems[1], str(vadl)))
        self.assertTrue( len(vadl) >= 11 ) # allow growth but not shrinkage.
#        for ad in vadl:
#            nTdebug(str(ad))

if __name__ == "__main__":
    cing.verbosity = cing.verbosityDebug
    unittest.main()
