from cing import verbosityNothing
from cing.STAR.TagTable import TagTable
from unittest import TestCase
import unittest


class AllChecks(TestCase):
    def testcheck_integrity(self):
        """TagTable"""

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
    

if __name__ == "__main__":
    verbosity = verbosityNothing
    unittest.main()
    