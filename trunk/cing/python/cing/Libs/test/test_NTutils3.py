from cing import cingDirTmp
from cing import verbosityDebug
from cing.Libs.NTutils import MsgHoL
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTpath
from cing.Libs.NTutils import bytesToFormattedString
from cing.Libs.NTutils import getDateTimeStampForFileName
from cing.Libs.NTutils import toCsv
from cing.core.classes import Project
from cing.core.classes import ROGscore
from cing.core.constants import COLOR_ORANGE
from cing.core.constants import COLOR_RED
from cing.core.molecule import Atom
from cing.core.molecule import Ensemble
from cing.core.molecule import Molecule
from unittest import TestCase
from cing.Libs.html import HTMLfile
import cing
import os
import unittest

class AllChecks(TestCase):

    os.chdir(cingDirTmp)

    def testROGscore(self):
        entryId = 'test'
        project = Project(entryId)
        self.failIf(project.removeFromDisk())
        project = Project.open(entryId, status='new')
        molecule = Molecule(name='moleculeName')
        molecule.ensemble = Ensemble(molecule) # Needed for html.
        project.appendMolecule(molecule) # Needed for html.
        molecule.updateAll()
        project.setupHtml() # Needed for creating the sub dirs.

        a = Atom(resName='ALA', atomName='HN')
        a.criticize()
        self.assertTrue(a)
        self.assertEquals(a.rogScore.colorLabel, COLOR_ORANGE)
        self.assertEquals(a.rogScore.colorCommentList[0][0], COLOR_ORANGE)
        self.assertEquals(a.rogScore.colorCommentList[0][1], ROGscore.ROG_COMMENT_NO_COOR)
        LOTR_remark = 'One ring to rule them all'
        Preserved_remark = 'Preserved'
        NowHasEffect_remark = 'Now has effect'
        NowHasEffectToo_remark = 'Now has effect too'
        # Next line will have to wipe out the orange comments.
        a.rogScore.setMaxColor(COLOR_RED, LOTR_remark)
        a.rogScore.setMaxColor(COLOR_ORANGE, NowHasEffect_remark )
        a.rogScore.setMaxColor(COLOR_RED, Preserved_remark)
        a.rogScore.setMaxColor(COLOR_ORANGE, NowHasEffectToo_remark)
        self.assertEquals(len(a.rogScore.colorCommentList), 5)
        self.assertEquals(a.rogScore.colorCommentList[0][1], ROGscore.ROG_COMMENT_NO_COOR)
        self.assertEquals(a.rogScore.colorCommentList[1][1], NowHasEffect_remark)

        myhtml = HTMLfile('testROGscore.html', project, 'A Test')
        myhtml.main("a main")
        a.rogScore.createHtmlForComments(myhtml.main)

        kw = {}
        a.rogScore.addHTMLkeywords(kw)
        myhtml.main("a", 'or by popup', **kw)
        myhtml.render()

    def tttestBytesToFormattedString(self):
        byteList = [ 1, 1000, 1300, 1600, 13000 * 1024, 130 * 1000 * 1024 * 1024  ]
        expectedResults = [ '0K', '1K', '1K', '2K', '13M', '127G' ]
        for i in range(len(byteList)):
            r = bytesToFormattedString(byteList[i])
    #        self.assertEqual( r, expectedResults[i] )
            self.assertEquals(r, expectedResults[i])

#    def ttttestQuoteForJson(self):
#        inList = [ "a", "a b", "a'b" ]
#        expectedResults= [ 'a', "'a b'" , 'a"b'  ]
#        i = 0
#        for inputStr in inList:
#            r = quoteForJson(inputStr)
#            self.assertEquals(r,expectedResults[i])
#            i += 1


    def tttestNTpath(self):
        pathList = [ "/Users/jd/.cshrc", "/Users/jd/workspace35", "/Users/jd/workspace35/" ]
        expectedDirectory = [ '/Users/jd' , "/Users/jd" , "/Users/jd/workspace35"]
        expectedBasename = [ '','workspace35', '' ]
        expectedExtension = [ '.cshrc', '', '' ]
        for i in range(len(pathList)):
            (directory, basename, extension) = NTpath(pathList[i])
    #        self.assertEqual( r, expectedResults[i] )
            self.assertEquals(directory, expectedDirectory[i])
            self.assertEquals(basename, expectedBasename[i])
            self.assertEquals(extension, expectedExtension[i])

    def tttestMsgHoL(self):
        msgHol = MsgHoL()
        for i in range(5):
            msgHol.appendMessage("Message %d" % i)
            msgHol.appendDebug("Debug %d" % i)
        msgHol.showMessage(MAX_MESSAGES=2)

    def tttestCSV(self):
        input = ['1brv', '9pcy' ]
        NTdebug("csv: [" + toCsv(input) + "]")
    def tttestGetDateTimeStampForFileName(self):
        NTdebug("getDateTimeStampForFileName: [" + getDateTimeStampForFileName() + "]")


if __name__ == "__main__":
#    cing.verbosity = verbosityNothing
    cing.verbosity = verbosityDebug
    unittest.main()
