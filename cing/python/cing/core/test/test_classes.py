from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.html import HTMLfile
from cing.core.classes import Project
from cing.core.constants import * #@UnusedWildImport
from cing.core.molecule import Ensemble
from cing.core.molecule import Molecule
from cing.core.parameters import htmlDirectories
from cing.core.parameters import moleculeDirectories
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    cingDirTmpTest = os.path.join( cingDirTmp, 'test_classes' )
    mkdirs( cingDirTmpTest )
    os.chdir(cingDirTmpTest)

    def setupSimplestProject(self):
        entryId = 'setupSimplestProject'
        project = Project(entryId)
        self.failIf(project.removeFromDisk())
        project = Project.open(entryId, status='new')
        molecule = Molecule(name='moleculeName')
        molecule.ensemble = Ensemble(molecule) # Needed for html.
        project.appendMolecule(molecule) # Needed for html.
        c = molecule.addChain('A')
        r1 = c.addResidue('ALA', 1, Nterminal = True)
        if r1:
            r1.addAllAtoms()

        molecule.updateAll()
        project.setupHtml() # Needed for creating the sub dirs.
        return project

    def test_HTMLfile_simple(self):
        project = self.setupSimplestProject()

        myhtml = HTMLfile('myTest.html', project, 'A Test')
        myhtml.header("a header")
        myhtml('h1', 'It is a test')
        myhtml.main("a main")
        myhtml.openTag('a', href="http://www.apple.com")
        myhtml('img', src = 'apple1.jpg')
        myhtml.closeTag('a')
        myhtml('a', 'testing link', href="http://www.bioc.cam.ac.uk/")
        myhtml.render()

    ###############
        myhtml = HTMLfile('myTest2.html', project, 'A Test 2')

        myhtml.header('h1', 'It is a test 2')
        myhtml.header('h2', 'another line')

        myhtml.main('a', href="http://www.apple.com", closeTag=False)
        myhtml.main('img', src = 'apple1.jpg')
        myhtml.main('a', openTag=False)
        myhtml.main('a', 'testing link', href="http://www.bioc.cam.ac.uk/")

        myhtml('br', 'used call')

        myhtml.render()
        #project = openProject('im2', 'old' )

    def testRootPath(self):
        p = Project('1brv')
        self.assertEquals('./1brv.cing', p.rootPath('1brv')[0])
        self.assertEquals('1brv', p.rootPath('1brv')[1])
        nTmessage("hello")
        nTdebug(p.root)

    def test_classes(self):
        htmlOnly = True
        pdbConvention = IUPAC
        entryId = "1brv_1model"        # Small much studied PDB NMR entry

        project = Project.open(entryId, status='new')
        if not project:
            nTerror('Failed opening project %s', entryId)
            exit(1)

        cyanaDirectory = os.path.join(cingDirTestsData, "cyana", entryId)
        nTdebug("Reading files from directory: " + cyanaDirectory)

        kwds = {}
        kwds['pdbFile'] = entryId
        project.cyana2cing(cyanaDirectory=cyanaDirectory,
                           convention=None,
                           coordinateConvention=pdbConvention,
                           copy2sources = True,
                           **kwds)
#        project.save()
        project.runCingChecks()
        project.setupHtml()
        project.generateHtml(htmlOnly = htmlOnly)
        project.renderHtml()


    def _test_HTMLfile(self):

        """
        Create two html files (project and molecule) that have relative links to each other.
        Exercising the machinery in HTMLfile class.
        """
        entryId = "test_HTMLfile"

        project = Project(entryId)
        self.failIf(project.removeFromDisk())
        project = Project.open(entryId, status='new')
        molecule = Molecule(name='moleculeName')
        project.appendMolecule(molecule)
        # initialize project html page
        # per item always set 2 top level attributes:
        project.htmlLocation = (project.path('index.html'), None)
        project.html = HTMLfile(project.htmlLocation[0], project, title = 'Project')
        nTdebug("project.htmlLocation[0]: %s" % project.htmlLocation[0])
        #create new folders for Molecule/HTML
        htmlPath = project.htmlPath()
        if os.path.exists(htmlPath):
            removedir(htmlPath)
        os.makedirs(htmlPath)
        nTdebug("htmlPath: %s" % htmlPath)

        # initialize molecule html page
        for subdir in htmlDirectories.values():
            project.mkdir(project.molecule.name, moleculeDirectories.html, subdir)

        # NB project.htmlPath is different from project.path
        molecule.htmlLocation = (project.htmlPath('indexMolecule.html'), None)
        nTdebug("molecule.htmlLocation[0]: %s" % molecule.htmlLocation[0])
        molecule.html = HTMLfile(molecule.htmlLocation[0], project,
                                  title = 'Molecule ' + molecule.name)

        # nb: destination is a destination obj (eg molecule object) that is to
        # have a html attribute that points to an HTMLfile instance.
        # In the validate.py code, the source argument is the 'main' section in
        # project.html. JFD doesn't understand why.
        project.html.insertHtmlLinkInTag('li', section=project.html.main,
            source=project, destination=molecule, text='mol ref', id=None)
        # rerun for testing.
        _link = project.html.findHtmlLocation(project, molecule, id=None)
#        self.assertEquals('moleculeName/HTML/indexMolecule.html#_top', link)
        project.html.main('ul', openTag=False)

        for htmlObj in [ project.html, molecule.html ]:
            self.assertFalse(htmlObj.render())

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
