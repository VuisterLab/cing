from cing import cingDirTmp
from cing import verbosityDebug
from cing.Libs.NTutils import ROGscore
from cing.PluginCode.html import HTMLfile
from cing.core.constants import COLOR_ORANGE
from cing.core.constants import COLOR_RED
from cing.core.molecule import Atom
from unittest import TestCase
import cing
import os 
import unittest

class AllChecks(TestCase):

    os.chdir(cingDirTmp)

    def testROGscore(self):
        a = Atom(resName='ALA', atomName='HN' )
        a.criticize()
        self.assertTrue(a)
        self.assertEquals(a.rogScore.colorLabel, COLOR_ORANGE )
        self.assertEquals(a.rogScore.colorCommentList[0], ROGscore.ROG_COMMENT_NO_COOR )
        LOTR_remark = 'One ring to rule them all'
        Preserved_remark = 'Preserved'
        # Next line will have to wipe out the orange comments.
        a.rogScore.setMaxColor(COLOR_RED, LOTR_remark)
        a.rogScore.setMaxColor(COLOR_ORANGE, 'No effect')
        a.rogScore.setMaxColor(COLOR_RED, Preserved_remark)
        a.rogScore.setMaxColor(COLOR_ORANGE, 'No effect either')
        self.assertEquals(len(a.rogScore.colorCommentList), 2 )
        self.assertEquals(a.rogScore.colorCommentList[0], LOTR_remark )
        self.assertEquals(a.rogScore.colorCommentList[1], Preserved_remark )

        # Note that this inserts some multi line popups by use of a alternative tag
        # which gets rendered by java script.
        myhtml = HTMLfile('testROGscore.html', 'A Test')
        myhtml.main("a main")
        a.rogScore.createHtmlForComments(myhtml.main)

        kw = {}
        a.rogScore.addHTMLkeywords( kw )
        myhtml.main("a", 'or by popup', **kw)

#        myhtml.render() # Can't be done without whole project and content anymore.
        
if __name__ == "__main__":
#    cing.verbosity = verbosityNothing
    cing.verbosity = verbosityDebug
    unittest.main()
