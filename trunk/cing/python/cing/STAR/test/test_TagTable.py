from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.STAR.TagTable import TagTable
from unittest import TestCase
import unittest


class AllChecks(TestCase):

    os.chdir(cingDirTmp)

    def testcheck_integrity(self):

        text = """_A a b c d e"""
        free = None
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
        _exp = """   loop_
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
#        self.assertEqual(exp,tt.star_text())
        NTdebug("column %s: %s" % ( "_A", tt.getStringListByColumnName("_A") ))

    def testcheck_integrity_2(self):

        text = """_A _B a b c d e f"""
        tt = TagTable(  free      = None,
                        tagnames  = [],
                        tagvalues = [],
                        verbosity = 2)
        pos = tt.parse( text = text, pos = 0)
        self.assertEqual(pos,len(text))
        self.assertEqual(tt.getRowCount(), 3)
        self.assertEqual(tt.getColCount(), 2)


    def testGetValueListIntByColumnName(self):

        text = """_A 1 2 . 3 4 5"""
        tt = TagTable(  free      = None,
                        tagnames  = [],
                        tagvalues = [],
                        verbosity = 2)
        pos = tt.parse( text = text, pos = 0)
        self.assertEqual(pos,len(text))
        self.assertEqual(tt.getRowCount(), 6)
        self.assertEqual(tt.getColCount(), 1)
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
    cing.verbosity = verbosityDebug
    unittest.main()
