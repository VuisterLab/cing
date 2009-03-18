from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityDetail
from cing import verbosityOutput
from cing.Libs.NTutils import NTdebug
from cing.STAR.TagTable import TagTable
from unittest import TestCase
import cing
import os
import unittest


class AllChecks(TestCase):

    os.chdir(cingDirTmp)

    def tttestcheck_integrity(self):

        text = """_A a b c d e"""; free = None
        tt = TagTable(  free      = free,
                        tagnames  = [],
                        tagvalues = [],
                        verbosity = 2)
        pos = tt.parse( text = text, pos = 0)
        self.assertEqual(pos,len(text))
        
        tt.tagvalues[0][0] = "A"
        tt.tagvalues[0][1] = "B\nC\n"
        tt.tagvalues[0][2] = "H1'"
        tt.tagvalues[0][3] = "H1'H2\""
        tt.tagvalues[0].append( 'H2"' )
        tt.tagvalues[0].append( "_a" ) # invalid without quotes.
        
#        print tt
        exp = """   loop_
      _A

A

;
B
C
;
 
"H1'" 

;
H1'H2"
;
 
e
'H2"' 
"_a" 

   stop_
"""        
        self.assertEqual(exp,tt.star_text())
        NTdebug("column %s: %s" % ( "_A", tt.getStringListByColumnName("_A") )) 

    def testGetValueListIntByColumnName(self):

        text = """_A 1 2 . 3 4 5"""
        tt = TagTable(  free      = None,
                        tagnames  = [],
                        tagvalues = [],
                        verbosity = 2)
        pos = tt.parse( text = text, pos = 0)
        self.assertEqual(pos,len(text))
        
        NTdebug("column %s: %s" % ( "_A", tt.getIntListByColumnName("_A") )) 

        text = """_A 1.0 2.0 . 3.0 4 5.0"""
        tt = TagTable(  free      = None,
                        tagnames  = [],
                        tagvalues = [],
                        verbosity = 2)
        pos = tt.parse( text = text, pos = 0)
        self.assertEqual(pos,len(text))
        
        NTdebug("column %s: %s" % ( "_A", tt.getFloatListByColumnName("_A") )) 

if __name__ == "__main__":
    cing.verbosity = verbosityDetail
    cing.verbosity = verbosityOutput
    cing.verbosity = verbosityDebug
    unittest.main()
    