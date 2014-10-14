from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.html import HTMLfile
from cing.core.classes import Project
from cing.core.classes import ROGscore
from cing.core.constants import * #@UnusedWildImport
from cing.core.molecule import Atom
from cing.core.molecule import Ensemble
from cing.core.molecule import Molecule
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    cingDirTmpTest = os.path.join( cingDirTmp, 'test_NTutils3' )
    mkdirs( cingDirTmpTest )
    os.chdir(cingDirTmpTest)

    def testROGscore(self):
        entryId = 'test'
        project = Project(entryId)
        self.failIf(project.removeFromDisk())
        project = Project.open(entryId, status='new')
        molecule = Molecule(name='moleculeName')
        molecule.ensemble = Ensemble(molecule) # Needed for html.
        project.appendMolecule(molecule) # Needed for html.

        # Add some crud to prevent warnings/errors later.
        molecule.addChain('top')
        top = molecule.allChains()[0]
        # Disable warnings temporarily
        v = cing.verbosity
        cing.verbosity = verbosityNothing
        for i in range( 1*10):
            res = top.addResidue( repr(random()),i )
            for j in range( 5):
                _atom = res.addAtom( repr(random()),j )
        cing.verbosity = v


        molecule.updateAll()
        project.setupHtml() # Needed for creating the sub dirs.

        a = Atom(resName='ALA', atomName='HN')
        a.criticize()
        self.assertTrue(a)
        self.assertEquals(a.rogScore.colorLabel, COLOR_ORANGE)
        self.assertEquals(a.rogScore.colorCommentList[0][0], COLOR_ORANGE)
        self.assertEquals(a.rogScore.colorCommentList[0][1], ROGscore.ROG_COMMENT_NO_COOR)
        lotr_remark = 'One ring to rule them all'
        preserved_remark = 'Preserved'
        nowHasEffect_remark = 'Now has effect'
        nowHasEffectToo_remark = 'Now has effect too'
        # Next line will have to wipe out the orange comments.
        a.rogScore.setMaxColor(COLOR_RED, lotr_remark)
        a.rogScore.setMaxColor(COLOR_ORANGE, nowHasEffect_remark )
        a.rogScore.setMaxColor(COLOR_RED, preserved_remark)
        a.rogScore.setMaxColor(COLOR_ORANGE, nowHasEffectToo_remark)
        self.assertEquals(len(a.rogScore.colorCommentList), 5)
        self.assertEquals(a.rogScore.colorCommentList[0][1], ROGscore.ROG_COMMENT_NO_COOR)
        self.assertEquals(a.rogScore.colorCommentList[1][1], nowHasEffect_remark)

        myhtml = HTMLfile('testROGscore.html', project, 'A Test')
        myhtml.main("a main")
        a.rogScore.createHtmlForComments(myhtml.main)

        kw = {}
        a.rogScore.addHTMLkeywords(kw)
        myhtml.main("a", 'or by popup', **kw)
        myhtml.render()

    def testBytesToFormattedString(self):
        byteList = [ 1, 1000, 1300, 1600, 13000 * 1024, 130 * 1000 * 1024 * 1024  ]
        expectedResults = [ '0K', '1K', '1K', '2K', '13M', '127G' ]
        for i in range(len(byteList)):
            r = bytesToFormattedString(byteList[i])
    #        self.assertEqual( r, expectedResults[i] )
            self.assertEquals(r, expectedResults[i])

#    def _testQuoteForJson(self):
#        inList = [ "a", "a b", "a'b" ]
#        expectedResults= [ 'a', "'a b'" , 'a"b'  ]
#        i = 0
#        for inputStr in inList:
#            r = quoteForJson(inputStr)
#            self.assertEquals(r,expectedResults[i])
#            i += 1

    def testNTpath(self):
        nTmessage("Now in " + getCallerName())
        # First item changed perhaps. used to be put in extension.
        pathList = [            '/Users/jd/.cshrc', '/Users/jd/workspace35', '/Users/jd/workspace35/', '1brv.pdb', '.cshrc' ]
        expectedDirectory = [   '/Users/jd',        '/Users/jd',             '/Users/jd/workspace35',  '.',        '.' ]
        expectedBasename = [    '.cshrc',           'workspace35',           '',                       '1brv',     '.cshrc' ]
        expectedExtension = [   '',                 '',                      '',                       '.pdb',     '' ]
        for i in range(len(pathList)):
            (directory, basename, extension) = nTpath(pathList[i])
            self.assertEquals(directory, expectedDirectory[i])
            self.assertEquals(basename, expectedBasename[i])
            self.assertEquals(extension, expectedExtension[i])

    def testMsgHoL(self):
        msgHol = MsgHoL()
        for i in range(5):
            msgHol.appendMessage("Message %d" % i)
            msgHol.appendDebug("Debug %d" % i)
        msgHol.showMessage(max_messages=2)

    def testCSV(self):
        input = ['1brv', '9pcy' ]
        nTdebug("csv: [" + toCsv(input) + "]")

    def testGetDateTimeStampForFileName(self):
        nTdebug("getDateTimeStampForFileName: [" + getDateTimeStampForFileName() + "]")


if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
