"""
Unit test execute as:
python $cingPath/Scripts/test/test_cyana2cing.py
"""
from cing import cingDirTestsData
from cing import cingDirTestsTmp
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import convert2Web
from cing.Libs.NTutils import findFiles
#from cing.Libs.NTutils import odict
from cing.Libs.NTutils import printDebug
from cing.Libs.NTutils import printException
from cing.core.parameters import cingPaths
from unittest import TestCase
import os
import unittest

class AllChecks(TestCase):

    def tttestPrints(self):
        printException("Now in testPrints")

    def tttestFind(self):
        
        self.assertTrue( os.path.exists( cingDirTestsData) and os.path.isdir(cingDirTestsData ) )
        self.failIf( os.chdir(cingDirTestsData), msg=
            "Failed to change to test directory for data: "+cingDirTestsData)
        namepattern, startdir = "CVS", cingDirTestsData
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
        printDebug( "Got back from convert2Web output file names: " + `fileList`)
        self.assertNotEqual(fileList,True)
        if fileList != True:
            for file in fileList: 
                self.assertNotEqual( file, None)

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
#        s.printAttr()
        s.kees = [0, 1, 3]
        s.name ='ss'
#        s.printAttr()
  
#        print 's=s>', (s==s), (s!=s)
#  
#        print s.items()
#        print s.keys()
#        print s.values()
  
        for _i in s.iteritems():
            pass
#            print 'i>',i
#        print len(s)
  
#        f = [   ('mies', 'mies: %3d '),
#                ('aap' , 'aap: %10s'),
#                ('kees', ' %d ')
#                  ]

        b = s.copy()
#        b.printAttr()
 
        p = s.popitem() 
        while p:
#            print "p>", p
            p = s.popitem()
#        s.printAttr()
  
        s.update( b  )
#        s.printAttr()
  
  
#        _od = odict( ('aap', 10), ('noot', 112), ('mies', 20))
  
#        for item in od.iteritems():
#            print 'od>', item
#            pass
      

#        od2 = odict()
#        od2.append(('aap', 10), ('noot', 112), ('mies', 20))
#        print od2
    
        _l = NTlist( 4, 9, 11, 12, 17, 5, 8, 12, 14 )
#        print _l.average(), l(0)


    
if __name__ == "__main__":
    unittest.main()
