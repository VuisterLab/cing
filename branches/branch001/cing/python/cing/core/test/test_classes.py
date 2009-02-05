from cing import cingDirTmp
from cing import verbosityDebug
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import removedir
from cing.PluginCode.html import HTMLfile
from cing.core.classes import Project
from cing.core.molecule import Molecule
from cing.core.parameters import htmlDirectories
from cing.core.parameters import moleculeDirectories
from unittest import TestCase
from cing.core.molecule import Ensemble
from cing.core.constants import IUPAC
from cing.Libs.NTutils import NTerror
from cing import cingDirTestsData
import cing
import os
import unittest

class AllChecks(TestCase):

    def tttest_HTMLfile_simple(self):
        self.failIf(os.chdir(cingDirTmp), msg=
             "Failed to change to directory for temporary test files: "+cingDirTmp)
        entryId = 'test'
        project = Project(entryId)
        self.failIf(project.removeFromDisk())
        project = Project.open(entryId, status='new')
        molecule = Molecule(name='moleculeName')
        molecule.ensemble = Ensemble(molecule) # Needed for html.
        project.appendMolecule(molecule) # Needed for html.
        
        project.setupHtml() # Needed for creating the sub dirs.
        
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

    def ttttest_rootPath(self):
        p = Project('1brv')
        self.assertEquals('./1brv.cing', p.rootPath('1brv')[0])
        self.assertEquals('1brv', p.rootPath('1brv')[1])


    def testRun(self):
        htmlOnly = True
        pdbConvention = IUPAC
        entryId = "1brv_1model"        # Small much studied PDB NMR entry
        self.failIf(os.chdir(cingDirTmp),
                     msg="Failed to change to directory for temporary test files: "+cingDirTmp)
        project = Project.open(entryId, status='new')
        if not project:
            NTerror('Failed opening project %s', entryId)
            exit(1)

        cyanaDirectory = os.path.join(cingDirTestsData, "cyana", entryId)
        NTdebug("Reading files from directory: " + cyanaDirectory)

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
        

    def tttest_HTMLfile(self):

        """
        Create two html files (project and moleucle) that have relative links to each other.
        Exercising the machinery in HTMLfile class.
        """
        entryId = "test_HTMLfile"
        self.failIf(os.chdir(cingDirTmp), msg=
             "Failed to change to directory for temporary test files: "+cingDirTmp)
        project = Project(entryId)
        self.failIf(project.removeFromDisk())
        project = Project.open(entryId, status='new')
        molecule = Molecule(name='moleculeName')
        project.appendMolecule(molecule)
        # initialize project html page
        # per item always set 2 top level attributes:
        project.htmlLocation = (project.path('index.html'), None)
        project.html = HTMLfile(project.htmlLocation[0], project, title = 'Project')
        NTdebug("project.htmlLocation[0]: %s" % project.htmlLocation[0])
        #create new folders for Molecule/HTML
        htmlPath = project.htmlPath()
        if os.path.exists(htmlPath):
            removedir(htmlPath)
        os.makedirs(htmlPath)
        NTdebug("htmlPath: %s" % htmlPath)

        # initialize molecule html page
        for subdir in htmlDirectories.values():
            project.mkdir(project.molecule.name, moleculeDirectories.html, subdir)

        # NB project.htmlPath is different from project.path
        molecule.htmlLocation = (project.htmlPath('indexMolecule.html'), None)
        NTdebug("molecule.htmlLocation[0]: %s" % molecule.htmlLocation[0])
        molecule.html = HTMLfile(molecule.htmlLocation[0], project,
                                  title = 'Molecule ' + molecule.name)

        # nb: destination is a destination obj (eg molecule object) that is to
        # have a html attribute that points to an HTMLfile instance.
        # In the validate.py code, the source argument is the 'main' section in
        # project.html. JFD doesn't understand why.
        project.html.insertHtmlLinkInTag('li', section=project.html.main,
            source=project, destination=molecule, text='mol ref', id=None)
        # rerun for testing.
        link = project.html.findHtmlLocation(project, molecule, id=None)
        self.assertEquals('moleculeName/HTML/indexMolecule.html#_top',
                           link)
        project.html.main('ul', openTag=False)

        for htmlObj in [ project.html, molecule.html ]:
            self.assertFalse(htmlObj.render())

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
