from cing import NaNstring
from cing import cingDirTmp
from cing import cingPythonDir
from cing import verbosityDebug
from cing import verbosityNothing
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import findFiles
from cing.Libs.NTutils import removeRecursivelyAttribute
from cing.Libs.NTutils import val2Str
from cing.Libs.fpconst import isNaN
from unittest import TestCase
import cing
import os
import unittest

class AllChecks(TestCase):

    def testPrints(self):
#        NTexception("Now in testPrints")
#        NTerror("test")
        pass

    def testRemoveRecursivelyAttribute(self):
        testDict = { 0: 1, "ccpn": 77}
        self.assertEqual( len(testDict.keys()), 2 )
        NTdebug( `testDict` )
        removeRecursivelyAttribute(testDict, "ccpn")
        self.assertEqual( len(testDict.keys()), 1 )
        NTdebug( `testDict` )


    def testFind(self):
        self.failIf( os.chdir(cingDirTmp), msg=
            "Failed to change to temp test directory for data: "+cingDirTmp)
        namepattern, startdir = "test*.py", cingPythonDir # CVS is only for developers
        nameList = findFiles(namepattern, startdir)
        self.assertTrue( len(nameList) > 10 )
#        for name in nameList:
#            print name


    def testCircularAverage(self):
        lol = [  [   5,  15,   10],
                [  345,   5,  355],
                 [   5, 345,  355],
                  [180,-180, None],
                   [90, -70,   10]]
        for cycle in lol:
            v1, v2, cav = cycle
            angleList = NTlist()
            angleList.append(v1)
            angleList.append(v2)
            result = angleList.cAverage(0, 360, 0, None)
            self.failUnless(result)
            circularAverage,_circularVariance,_n = result
            if cav != None:
                self.assertAlmostEqual(circularAverage, cav, places=5)

    def testCircularAverage2(self):
        angleList = NTlist()
        angleList.append(1)
        result = angleList.cAverage(0, 360, 0, None)
        self.failUnless(result)
        circularAverage,_circularVariance,_n = result
        self.assertAlmostEqual(circularAverage, 1, places=5)

    def testCircularAverage3(self):
        angleList = NTlist()
        result = angleList.cAverage(0, 360, 0, None)
        self.failUnless(result)
        _circularAverage,_circularVariance,_n = result


#        double[][] testValues = new double[][] {
#                {    5,  15,   10},
#                {  345,   5,   20},
#                 {   5, 345,  -20},
#                  {180, 180,    0},
#                   {90, -70, -160}
#        };

    def testGeneral(self):
        s = NTdict(aap='noot', mies=1)
        s.setdefault('mies',2)
        s.setdefault('kees',[])
        s.kees = [0, 1, 3]
        s.name ='ss'

        b = s.copy()

        p = s.popitem()
        while p:
            p = s.popitem()
        s.update( b  )


    def testNTaverage(self):
        l = NTlist( 4, 9, 11, 12, 17, 5, 8, 12, 14 )
        (av,sd,n) = l.average()
        NTdebug( "av %s, sd %s, n %s" % (av,sd,n) )
        self.assertAlmostEqual( av, 10.22, places=1) # verified in Excel stddev function.
        self.assertAlmostEqual( sd,  4.18, places=1)
        self.assertEquals(       n, 9)

        l = NTlist( 1,None,1,1 )
        (av,sd,n) = l.average()
        NTdebug( "av %s, sd %s, n %s" % (av,sd,n) )
        self.assertAlmostEqual( av,   1.0, places=1)
        self.assertAlmostEqual( sd,   0.0, places=1)
        self.assertEquals(       n, 3)

        l = NTlist( 1,2 )
        (av,sd,n) = l.average()
        NTdebug( "av %s, sd %s, n %s" % (av,sd,n) )
        self.assertAlmostEqual( av,   1.5, places=1)
        self.assertAlmostEqual( sd, 0.707, places=2)
        self.assertEquals(       n, 2)

        l = NTlist( 1 )
        (av,sd,n) = l.average()
        NTdebug( "(one element) av %s, sd %f, n %s" % (av,sd,n) )
        self.assertAlmostEqual( av,   1.0, places=1)
        self.assertTrue( isNaN(sd) )
        self.assertEquals(       n,   1)

        l = NTlist()
        (av,sd,n) = l.average()
        NTdebug( "av %s, sd %s, n %s" % (av,sd,n) )
        self.assertTrue( isNaN(av))
        self.assertTrue( isNaN(sd) )
        self.assertEquals(       n,   0)

        l = NTlist(0.0, 0.0, 0.0)
        (av,sd,n) = l.average()
        NTdebug( "av %s, sd %s, n %s" % (av,sd,n) )
        self.assertEquals(      av,  0)
        self.assertEquals(      sd,  0)
        self.assertEquals(       n,  3)

    def testValueToFormattedString(self):
        self.assertEquals( val2Str(None,"%5.2f",None),NaNstring)
        self.assertEquals( val2Str(None,"%5.2f",5),   "%5s" % NaNstring)
        self.assertEquals( val2Str(6.3, "%5.2f",5),   " 6.30")
        self.assertEquals( val2Str(6.3, "%.2f"),      "6.30")
        self.assertEquals( val2Str(6.3, "%03d"),      "006")


if __name__ == "__main__":
    cing.verbosity = verbosityNothing
    cing.verbosity = verbosityDebug
#    cProfile.run('unittest.main()', 'fooprof')
#    p = pstats.Stats('fooprof')
#    p.sort_stats('time').print_stats(10)
#    p.sort_stats('cumulative').print_stats(40)
    unittest.main()
