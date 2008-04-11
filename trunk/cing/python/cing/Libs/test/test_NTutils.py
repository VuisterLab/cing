"""
Unit test execute as:
python $cingPath/Scripts/test/test_cyana2cing.py
"""
from cing import NaNstring
from cing import cingDirTestsData
from cing import cingDirTestsTmp
from cing import cingPythonDir
from cing import verbosityDebug
from cing import verbosityNothing
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import convert2Web
from cing.Libs.NTutils import findFiles
from cing.Libs.NTutils import val2Str
from cing.core.constants import NOSHIFT
from cing.core.molecule import Molecule
from cing.core.parameters import cingPaths
from random import random
from unittest import TestCase
import cing
import os
import unittest

class AllChecks(TestCase):

    def tttestPrints(self):
#        NTexception("Now in testPrints")
#        NTerror("test")
        pass
    
    def tttestFind(self):
        self.failIf( os.chdir(cingDirTestsTmp), msg=
            "Failed to change to temp test directory for data: "+cingDirTestsTmp)
        namepattern, startdir = "CVS", cingPythonDir
        nameList = findFiles(namepattern, startdir)
        self.assertTrue( len(nameList) > 10 ) 
#        for name in nameList:
#            print name

    def tttestConvert2Web(self):
        fn = "pc_nmr_11_rstraints.ps"
        self.assertTrue( os.path.exists( cingDirTestsData) and os.path.isdir(cingDirTestsData ) )
        inputPath = os.path.join(cingDirTestsData,fn)
        outputPath = cingDirTestsTmp
        self.failIf( os.chdir(outputPath), msg=
            "Failed to change to temporary test directory for data: "+outputPath)
        fileList = convert2Web( cingPaths.convert, cingPaths.ps2pdf, inputPath, outputDir=outputPath ) 
        NTdebug( "Got back from convert2Web output file names: " + `fileList`)
        self.assertNotEqual(fileList,True)
        if fileList != True:
            for file in fileList: 
                self.assertNotEqual( file, None)

    def tttestCircularAverage(self):
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
                
    def tttestCircularAverage2(self):
        angleList = NTlist()
        angleList.append(1)
        result = angleList.cAverage(0, 360, 0, None)
        self.failUnless(result)
        circularAverage,_circularVariance,_n = result
        self.assertAlmostEqual(circularAverage, 1, places=5)
                
    def tttestCircularAverage3(self):
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

    def tttestGeneral(self):
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

        
    def tttestNTaverage(self):
        l = NTlist( 4, 9, 11, 12, 17, 5, 8, 12, 14 )
        (av,sd,n) = l.average()
        NTdebug((av,sd,n))
        self.assertAlmostEqual( av, 10.22, places=1) # verified in Excel stddev function.
        self.assertAlmostEqual( sd,  4.18, places=1) 
        self.assertEquals(       n, 9) 

        l = NTlist( 1,None,1,1 )
        (av,sd,n) = l.average()
        NTdebug((av,sd,n))
        self.assertAlmostEqual( av,   1.0, places=1) 
        self.assertAlmostEqual( sd,   0.0, places=1) 
        self.assertEquals(       n, 3) 
        
        l = NTlist( 1,2 )
        (av,sd,n) = l.average()
        NTdebug((av,sd,n))
        self.assertAlmostEqual( av,   1.5, places=1) 
        self.assertAlmostEqual( sd, 0.707, places=2) 
        self.assertEquals(       n, 2) 
        
        l = NTlist( 1 )
        (av,sd,n) = l.average()
        NTdebug((av,sd,n))
        self.assertAlmostEqual( av,   1.0, places=1) 
        self.assertEquals(      sd,  None) 
        self.assertEquals(       n,   1) 
        
        l = NTlist()
        (av,sd,n) = l.average()
        NTdebug((av,sd,n))
        self.assertEquals(      av,  None) 
        self.assertEquals(      sd,  None) 
        self.assertEquals(       n,   0) 

        l = NTlist(0.0, 0.0, 0.0)
        (av,sd,n) = l.average()
        NTdebug((av,sd,n))
        self.assertEquals(      av,  0) 
        self.assertEquals(      sd,  0) 
        self.assertEquals(       n,  3) 

    def tttestValueToFormattedString(self):
        self.assertEquals( val2Str(None,"%5.2f",None),NaNstring)
        self.assertEquals( val2Str(None,"%5.2f",5),   "%5s" % NaNstring)
        self.assertEquals( val2Str(6.3, "%5.2f",5),   " 6.30")
        self.assertEquals( val2Str(6.3, "%.2f"),      "6.30")
        self.assertEquals( val2Str(6.3, "%03d"),      "006")
        self.assertEquals( val2Str(6.3, "%6.2f",nullValue=NOSHIFT),"  6.30")
        self.assertEquals( val2Str(999.,"%6.2f",nullValue=NOSHIFT),NaNstring) # Oops an xeasy nan
        self.assertNotEquals(val2Str(999.1,"%6.2f",nullValue=NOSHIFT),NaNstring)

    def testNTdict(self):
        a = NTdict(b=NTdict(anItem='there'))
#        NTdebug( '0 '+ `a` )
#        NTdebug( '1 '+ `a['b']`)
#        NTdebug( '2 '+ `a.getDeepByKeys('b')`)
#        NTdebug( '3 '+ `a.getDeepByKeys(9)`)
        # Tests below make sure no throwables are thrown.
        self.assertTrue(a)
        self.assertTrue(a['b'])
        self.assertTrue(a.getDeepByKeys('b'))
        self.assertFalse(a.getDeepByKeys(9))

        
        a = NTdict(b=NTdict(c=NTdict(anItem='there')))
#        NTdebug( '4 '+ `a` )
#        NTdebug( '5 '+ `a['b']`)
#        NTdebug( '6 '+ `a.getDeepByKeys('b')`)
#        NTdebug( '7 '+ `a.getDeepByKeys('b','c')`)
#        NTdebug( '8 '+ `a.getDeepByKeys('b','9')`)
#        NTdebug( '9 '+ `a.getDeepByKeys('b','c','d')`)
        self.assertTrue(a.getDeepByKeys('b','c','anItem'))
        self.assertFalse(a.getDeepByKeys('b','c',9))
        a.b.c=NTlist(1,2,3)
        self.assertFalse(a.getDeepByKeys('b','c',9)) # better not throw an error.
        self.assertEquals('default value',
            a.getDeepByKeysOrDefault('default value',9)) # returns default
        self.assertEquals(2,
            a.getDeepByKeys('b','c',1)) # get the second element by key 1

    def tttestNTmessage(self):
        aStringToBe = 123
        NTdebug("testing messaging system for debug: "+`aStringToBe`)
        # Next should not be printing anything when verbosityNothing is the setting.
        NTerror("testing messaging system for error: "+`aStringToBe`) 
        NTdebug("testing messaging system: "+`aStringToBe`)
        NTdebug("testing messaging system: %s", aStringToBe)

    def tttestNTlistSetConsensus(self):
        l = NTlist( 4., 9., 9. )
        self.assertEqual( l.setConsensus(minFraction=0.6), 9)
        self.assertEqual( l.consensus, 9)
        
    def tttestNTlistIndex(self):
        # speed check
        l = NTlist()
        for _i in range( 10*1000):
            l.append( random() )
        middleValue = 0.5
        l.append( middleValue )
        for _i in range( 10*1000):
            l.append( random() )

        for _i in range( 10*1000):
            _x = l.index(middleValue)
#            tree.sibling(1)

    def tttestNTtreeIndex(self):
        mol = Molecule('mol')
        mol.addChain('top')
        top = mol.allChains()[0]
        for i in range( 1*1000):
            top.addResidue( `random()`,i )
        
        resList = top.allResidues()
        middleValue = resList[len(resList)/2]
        

        for _i in range( 1*100):
#            _x = middleValue.sibling(0) # getting myself back should not take time.
            _x = middleValue.sibling(1) # this tends to be very expensive
            
if __name__ == "__main__":
    cing.verbosity = verbosityNothing
    cing.verbosity = verbosityDebug
#    cProfile.run('unittest.main()', 'fooprof')
#    p = pstats.Stats('fooprof')
#    p.sort_stats('time').print_stats(10)
#    p.sort_stats('cumulative').print_stats(40)
    unittest.main()
