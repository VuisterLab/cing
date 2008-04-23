from cing import verbosityDebug
from cing import verbosityNothing
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTlist
from cing.core.molecule import Molecule
from random import random
from unittest import TestCase
from cing.Libs.NTutils import appendDeepByKeys
import cing
import unittest

class AllChecks(TestCase):

    def testNTdict(self):
        a = NTdict( b=NTdict( anItem='there'))
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

    def testNTdict2(self):
        a = {}
        appendDeepByKeys(a, 1.23, 'b', 'c')
        strComplexObject = '%s' % a
        self.assertEquals(strComplexObject, "{'b': {'c': [1.23]}}")
        a = {'b':[10,[11],12]}
        strComplexObject = '%s' % a
        self.assertEquals(strComplexObject, "{'b': [10, [11], 12]}")
        appendDeepByKeys(a, 13, 'b', 1)
        strComplexObject = '%s' % a
        self.assertEquals(strComplexObject, "{'b': [10, [11, 13], 12]}")
        

    def testNTmessage(self):
        aStringToBe = 123
        NTdebug("testing messaging system for debug: "+`aStringToBe`)
        # Next should not be printing anything when verbosityNothing is the setting.
        NTerror("testing messaging system for MESSAGE TYPE error: "+`aStringToBe`)
        NTdebug("testing messaging system: "+`aStringToBe`)
        NTdebug("testing messaging system: %s", aStringToBe)

    def testNTlistSetConsensus(self):
        l = NTlist( 4., 9., 9. )
        self.assertEqual( l.setConsensus(minFraction=0.6), 9)
        self.assertEqual( l.consensus, 9)

    def testNTlistIndex(self):
        # speed check
        l = NTlist()
        for _i in range( 1*1000):
            l.append( random() )
        middleValue = 0.5
        l.append( middleValue )
        for _i in range( 1*1000):
            l.append( random() )

        for _i in range( 1*1000):
            _x = l.index(middleValue)
#            tree.sibling(1)

    def testNTtreeIndex(self):
        mol = Molecule('mol')
        mol.addChain('top')
        top = mol.allChains()[0]
        for i in range( 1*10):
            top.addResidue( `random()`,i )

        resList = top.allResidues()
        middleValue = resList[len(resList)/2]
        
        for _i in range( 1*10):
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
