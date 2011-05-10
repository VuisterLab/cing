"""
Unit test execute as:
python -u $CINGROOT/python/cing/Libs/test/test_NTutils6.py
"""

from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.classes2 import ResonanceList
from unittest import TestCase
import unittest

class AllChecks(TestCase):
    cingDirTmpTest = os.path.join( cingDirTmp, 'test_NTutils6' )
    mkdirs( cingDirTmpTest )
    os.chdir(cingDirTmpTest)

    def testGetCallerName(self):
        self.failIf( getCallerName() != 'testGetCallerName')
        self.failIf( additionalTestRoutineByItself() != 'additionalTestRoutineByItself')

    def testGetUniqueName(self):
        resonanceSources = NTlist()
        resonanceSources.append(ResonanceList('a'))
        inputList           = ['b', 'a']
        expectedOutputList  = ['b', 'a_1']
        for i,input in enumerate(inputList):
            output = getUniqueName(resonanceSources, input)
            self.assertEqual( output, expectedOutputList[i])
        self.assertEqual( getUniqueName(resonanceSources, 'a', nameFormat = '%s---%06d'), 'a---000001')

    def testFilterListByObjectClassName(self):
        l = ['a', 'b', 1.0, 2.0, 3.0, NTdict(), None, None, None, None ]
        ls = filterListByObjectClassName(l, 'str')
        self.assertEqual( len(ls), 2)
        lf = filterListByObjectClassName(l, 'float')
        self.assertEqual( len(lf), 3)
        ld = filterListByObjectClassName(l, 'NTdict')
        self.assertEqual( len(ld), 1)
#        ln = filterListByObjectClassName(l, 'NoneType')
        ln = filterListByObjectClassName(l, None) # NB don't use NoneType for this as the routine isn't that smart.
        self.assertEqual( len(ln), 4)

    def testgetListByName(self):
        lol = NTlist(ResonanceList('a'), ResonanceList('b'))
        l = getObjectByName(lol, 'b')
        self.assertTrue( l != None )
        self.assertTrue( l.name == 'b' )

    def testGetRevisionAndDateTimeFromCingLog(self):
        inputArchiveDir = os.path.join(cingDirTestsData, "cing")
        fileName = '1brv_2011-04-07_11-12-19.log'
        result = getRevisionAndDateTimeFromCingLog( os.path.join(inputArchiveDir, fileName ))
        self.assertTrue( result )
        self.assertEqual( result[0], 962 )
        if 0:
            date_string = 'Thu Apr  7 11:12:26 2011'
            expectedDt = datetime.datetime(*(time.strptime(date_string)[0:6])) # 7 items?
        else:
            expectedDt = datetime.datetime(2011, 4, 7, 11, 12, 26)
        self.assertEqual( result[1], expectedDt )

    def testNTflatten(self):
        inputList = [ (1,), # stupid tuples need an extra comma
                      [2],
                      (3,4),
                      (5,(6,7)),
                      (('A', 6), ('A', 9)),
                     ]
        expectedList = [ (1,),
                         (2,),
                         (3,4),
                         (5,6,7),
                         ('A', 6, 'A', 9),
                        ]
        for i, obj in enumerate(inputList):
            self.assertEquals( NTflatten(obj), expectedList[i] )
        pair = (('A', 6), ('A', 9))
#        valueList =  NTflatten(pair)        
#        NTmessage("valueList: %s" % valueList)
        _x = "patch DISU  reference=1  =( segi %s and resid %s )  reference=2=( segi %s and resid %s )        end\n" % NTflatten(pair)
#        NTmessage("x: %s" % x)
# end class
            
def additionalTestRoutineByItself():
    return getCallerName()
# end def

if __name__ == "__main__":
    cing.verbosity = cing.verbosityDebug
    unittest.main()
