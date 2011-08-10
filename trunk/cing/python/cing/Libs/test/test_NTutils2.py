"""
Unit test execute as:
python -u $CINGROOT/python/cing/Libs/test/test_NTutils2.py
"""

from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.molecule import Molecule
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def testNTdict(self):
        a = NTdict( b=NTdict( anItem='there'))
#        nTdebug( '0 '+ repr(a) )
#        nTdebug( '1 '+ repr(a['b']))
#        nTdebug( '2 '+ repr(a.getDeepByKeys('b')))
#        nTdebug( '3 '+ repr(a.getDeepByKeys(9)))
        # Tests below make sure no throwables are thrown.
        self.assertTrue(a)
        self.assertTrue(a['b'])
        self.assertTrue(a.getDeepByKeys('b'))
        self.assertFalse(a.getDeepByKeys(9))


        a = NTdict(b=NTdict(c=NTdict(anItem='there')))
#        nTdebug( '4 '+ repr(a) )
#        nTdebug( '5 '+ repr(a['b']))
#        nTdebug( '6 '+ repr(a.getDeepByKeys('b')))
#        nTdebug( '7 '+ repr(a.getDeepByKeys('b','c')))
#        nTdebug( '8 '+ repr(a.getDeepByKeys('b','9')))
#        nTdebug( '9 '+ repr(a.getDeepByKeys('b','c','d')))
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


    def testnTmessage(self):
        aStringToBe = 123
        nTdebug("testing messaging system for debug: " + repr(aStringToBe))
        # Next should not be printing anything when verbosityNothing is the setting.
#        nTerror("testing messaging system for MESSAGE TYPE error (This is not a real error): "+repr(aStringToBe))
        nTdebug("testing messaging system: "+repr(aStringToBe))
        nTdebug("testing messaging system: %s", aStringToBe)

    def testNTlistSetConsensus(self):
        myList = NTlist( 4., 9., 9. )
        self.assertEqual( myList.setConsensus(minFraction=0.6), 9)

    def testNTlistIndex(self):
        # speed check
        a = NTlist()
        for _i in range( 1*1000):
            a.append( random() )
        middleValue = 0.5
        a.append( middleValue )
        for _i in range( 1*1000):
            a.append( random() )

        for _i in range( 1*1000):
            _x = a.index(middleValue)
#            tree.sibling(1)

    def testNTtreeIndex(self):
        mol = Molecule('mol')
        mol.addChain('top')
        top = mol.allChains()[0]
        # Disable warnings temporarily
        v = cing.verbosity
        cing.verbosity = verbosityNothing
        for i in range( 1*10):
            res = top.addResidue( repr(random()),i )
            for j in range( 5):
                atom = res.addAtom( repr(random()),j )
        cing.verbosity = v

        resList = top.allResidues()
        middleValue = resList[len(resList)/2]

        for _i in range( 1*10):
#            _x = middleValue.sibling(0) # getting myself back should not take time.
            _x = middleValue.sibling(1) # this tends to be very expensive

        newMol = atom.getParent(level = 3)
        self.assertEqual(mol,newMol)
        newMol = atom.getMolecule()
        self.assertEqual(mol,newMol)
        res.removeAtom(atom.name)
        newMol = atom.getMolecule()
        self.assertEqual(newMol, mol)

    def testNTvalue(self):
        s = "%s"  % NTvalue(value=None,  error=None, fmt='%.3f (+- %.3f)')
        self.assertEquals( s, '. (+- .)')
        s = "%s"  % NTvalue(value=1.0,   error=None, fmt='%.3f (+- %.3f)')
        self.assertEquals( s, '1.0 (+- .)')
        s = "%s"  % NTvalue(value=1.000, error=None, fmt='%.3f (+- %.3f)') # still this mistake was not detected for a number:  -0.54700000000000004 (+- .) that's why the below extra tests.
        self.assertEquals( s, '1.0 (+- .)')
        s = "%s"  % NTvalue(value=2.000, error=0.2,  fmt='%.3f (+- %.3f)')
        self.assertEquals( s, '2.000 (+- 0.200)')
        s = "%s"  % NTvalue(value=3000, error=300,   fmt='%.3f (+- %.3f)')
        self.assertEquals( s, '3000.000 (+- 300.000)')
        s = "%s"  % NTvalue(value=3e7, error=3e6,    fmt='%.3e (+- %.3e)')
        self.assertEquals( s, '3.000e+07 (+- 3.000e+06)')
        s = "%s"  % NTvalue(value=0.75, error=None )
        self.assertEquals( s, '0.75 (+- .)')
        s = "%s"  % NTvalue(value=0.75, error=None, fmt='%.2f (+- %.2f)' )
        self.assertEquals( s, '0.75 (+- .)')
        s = "%s"  % NTvalue(value=0.75, error=NaN, fmt='%.2f (+- %.2f)' )
        self.assertEquals( s, '0.75 (+- .)')
        fmt = '%.2f (+- %.2f)'
        fmt2 = '%.2f'
        self.assertEquals(  "-0.55 (+- 1.23)", "%s"  % NTvalue(value=-0.5471, error=1.23, fmt=fmt, fmt2=fmt2 ))
        self.assertEquals(  "-0.55 (+- .)",    "%s"  % NTvalue(value=-0.5471, error=None, fmt=fmt, fmt2=fmt2 ))
        self.assertEquals(  ". (+- .)",        "%s"  % NTvalue(value=None,    error=None, fmt=fmt, fmt2=fmt2 ))

    def testGetTextBetween(self):

        s = "abcdefg"
        start = 'bc'
        end = 'f'
        expected = "bcdef"
        t = getTextBetween( s, start, end )
        self.assertEquals( t, expected )

        # Some multi line stuff.
        s = """# 79 # Note: Summary report for users of a structure
This is an overall summary of the quality of the structure as
compared with current reliable structures. This summary is most
useful for biologists seeking a good structure to use for modelling
calculations.

The second part of the table mostly gives an impression of how well
the model conforms to common refinement constraint values. The
first part of the table shows a number of constraint-independent
quality indicators.

 Structure Z-scores, positive is better than average:
  1st generation packing quality :  -3.135
  2nd generation packing quality :  -1.174
  Ramachandran plot appearance   :  -3.291 (poor)
  chi-1/chi-2 rotamer normality  :  -5.390 (bad)
  Backbone conformation          :  -3.116 (poor)

 RMS Z-scores, should be close to 1.0:
  Bond lengths                   :   1.642 (loose)
  Bond angles                    :   1.394
  Omega angle restraints         :   0.245 (tight)
  Side chain planarity           :   1.031
  Improper dihedral distribution :   1.383
  Inside/Outside distribution    :   1.030
==============


WHAT IF
    G.Vriend,
      WHAT IF: a molecular modelling and drug design program,
    J. Mol. Graph. 8, 52--56 (1990).

"""
        start       = 'Summary report for users of a structure'
        end         ='=============='
        expected    = """Summary report for users of a structure
This is an overall summary of the quality of the structure as
compared with current reliable structures. This summary is most
useful for biologists seeking a good structure to use for modelling
calculations.

The second part of the table mostly gives an impression of how well
the model conforms to common refinement constraint values. The
first part of the table shows a number of constraint-independent
quality indicators.

 Structure Z-scores, positive is better than average:
  1st generation packing quality :  -3.135
  2nd generation packing quality :  -1.174
  Ramachandran plot appearance   :  -3.291 (poor)
  chi-1/chi-2 rotamer normality  :  -5.390 (bad)
  Backbone conformation          :  -3.116 (poor)

 RMS Z-scores, should be close to 1.0:
  Bond lengths                   :   1.642 (loose)
  Bond angles                    :   1.394
  Omega angle restraints         :   0.245 (tight)
  Side chain planarity           :   1.031
  Improper dihedral distribution :   1.383
  Inside/Outside distribution    :   1.030
"""
        t = getTextBetween( s, start, end, endIncl=False )
        self.assertEquals( t, expected )

if __name__ == "__main__":
    cing.verbosity = verbosityNothing
    cing.verbosity = verbosityDebug
#    cProfile.run('unittest.main()', 'fooprof')
#    p = pstats.Stats('fooprof')
#    p.sort_stats('time').print_stats(10)
#    p.sort_stats('cumulative').print_stats(40)
    unittest.main()
