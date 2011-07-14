from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.STAR.Text import comments_strip
from unittest import TestCase
import unittest
#from cing import verbosityDebug
#import cing


class AllChecks(TestCase):
    cingDirTmpTest = os.path.join( cingDirTmp, 'test_Text' )
    mkdirs( cingDirTmpTest )
    os.chdir(cingDirTmpTest)


    def test_Star(self):
#        textExpectedAfterCollapse = ';<eol-string>mmy xie<eol-string>;\n_Test'
#        text = """;
#mmy xie
#;
#_Test"""
#        textCollapsed = semicolon_block_collapse( text )
#        self.assertEqual( textExpectedAfterCollapse, textCollapsed)
#
#        value, pos = tag_value_quoted_parse( textCollapsed, 0 )
#        valueExpected = '\nmmy xie\n'
#        posExpected = 34
#        self.assertEqual( valueExpected, value )
#        self.assertEqual( posExpected, pos)

# JFD had to remove the beginning space before the pound because Eclipse removes it in the expected too.
        t2 = """
# comment 1
"""
        t2noComment = """

"""
        self.assertEqual(t2noComment,comments_strip( t2 ))

    def test_comments_strip(self):
        text = """
# my comment exactly
foo # comment
value#still a value
bar
; # actual data
;
"""
        textExpected = "\n\nfoo "+"""
value#still a value
bar
; # actual data
;
"""
        textNew = comments_strip( text )
        self.assertEqual( textNew, textExpected)

    def test_comments_strip2(self):
        text = """
H' # comment
H" # also
"""
        textExpected = """\nH' \nH" \n"""
        textNew = comments_strip( text )
        self.assertEqual( textNew, textExpected)

    def test_comments_strip3a(self):
        text = """
H# # comment
"""
        textExpected = "\nH# \n"

        textNew = comments_strip( text )
        self.assertEqual( textNew, textExpected)

    def test_comments_strip3(self):
        text = """
H#
"""
        textExpected = "\nH#\n"

        textNew = comments_strip( text )
        self.assertEqual( textNew, textExpected)

    def test_comments_strip4(self):
        text = """
;
test1 # no comment 1
;
;
test2 # no comment 2
;
"""
        textExpected = """
;
test1 # no comment 1
;
;
test2 # no comment 2
;
"""
        textNew = comments_strip( text )
        self.assertEqual( textNew, textExpected)

    def test_comments_strip5(self):
        text = """
'quoted value with embedded # comment' # real comment
"""
        textExpected = "\n'quoted value with embedded # comment' \n"
        textNew = comments_strip( text )
        self.assertEqual( textNew, textExpected)

    def test_comments_strip6(self):
        text = """
"quoted value with embedded # comment" # real comment
"""
        textExpected = '\n"quoted value with embedded # comment" \n'

        textNew = comments_strip( text )
        self.assertEqual( textNew, textExpected)

    def test_comments_strip7(self):
        text = """
"quoted 'complications ; ' with embedded # comment" # real comment
"""
        textExpected = """
"quoted 'complications ; ' with embedded # comment" \n"""
        textNew = comments_strip( text )
        self.assertEqual( textNew, textExpected)

    def test_comments_strip8(self):
        text = """
"quoted 'complications;' with embedded # comment" # real comment
"""
        textExpected = """
"quoted 'complications;' with embedded # comment" \n"""
        textNew = comments_strip( text )
        self.assertEqual( textNew, textExpected)

    def test_comments_strip9(self):
        text = """
;

;
"""
        textExpected = """
;

;
"""
        textNew = comments_strip( text )
        self.assertEqual( textNew, textExpected)

if __name__ == "__main__":
#    cing.verbosity = verbosityDebug
    unittest.main()
