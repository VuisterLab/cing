from cing import cingDirTmp
from cing import verbosityDebug
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import removedir
from cing.core.classes import HTMLfile
from cing.core.classes import Project
from cing.core.molecule import Molecule
from cing.core.parameters import htmlDirectories
from cing.core.parameters import moleculeDirectories
from unittest import TestCase
import cing
import os
import unittest

class AllChecks(TestCase):

    os.chdir(cingDirTmp)
    
    def test_HTMLfile_simple(self):         
        myhtml = HTMLfile('myTest.html', 'A Test')
        myhtml.header("a header")
        myhtml('h1', 'It is a test')
        myhtml.main("a main")
        myhtml.openTag('a', href="http://www.apple.com" )
        myhtml('img', src = 'apple1.jpg')
        myhtml.closeTag('a')
        myhtml('a', 'testing link', href="http://www.bioc.cam.ac.uk/")
        myhtml.render()
    
    ###############
        myhtml = HTMLfile('myTest2.html', 'A Test 2')
    
        myhtml.header('h1', 'It is a test 2')
        myhtml.header('h2','another line')
    
        myhtml.main('a', href="http://www.apple.com", closeTag=False)
        myhtml.main('img', src = 'apple1.jpg')
        myhtml.main('a', openTag=False)
        myhtml.main('a', 'testing link', href="http://www.bioc.cam.ac.uk/")
    
        myhtml('br','used call')
    
        myhtml.render()
        #project = openProject('im2', 'old' )

    def tttest_rootPath(self):
        p = Project('1brv')
        self.assertEquals( './1brv.cing', p.rootPath('1brv')[0] )         
        self.assertEquals( '1brv',        p.rootPath('1brv')[1] )         

    def test_HTMLfile(self):
        
        """
        Create two html files (project and moleucle) that have relative links to each other.
        Exercising the machinery in HTMLfile class.
        """
        entryId = "test_HTMLfile" 
        project = Project( entryId )
        self.failIf( project.removeFromDisk() )
        project = Project.open( entryId, status='new' )
        molecule = Molecule( name='moleculeName' )
        project.appendMolecule(molecule)

        top = '_top'
        # initialize project html page
        # per item always set 2 top level attributes:
        project.htmlLocation = (project.path('index.html'), top)
        project.html = HTMLfile( project.htmlLocation[0], title = 'Project' )
        NTdebug("project.htmlLocation[0]: %s" % project.htmlLocation[0])
        #create new folders for Molecule/HTML
        htmlPath = project.htmlPath()
        if os.path.exists( htmlPath ):
            removedir( htmlPath )
        os.makedirs( htmlPath )
        NTdebug("htmlPath: %s" % htmlPath)

        # initialize molecule html page
        for subdir in htmlDirectories.values():
            project.mkdir( project.molecule.name, moleculeDirectories.html, subdir )

        # NB project.htmlPath is different from project.path
        molecule.htmlLocation = (project.htmlPath('indexMolecule.html'), top)
        NTdebug("molecule.htmlLocation[0]: %s" % molecule.htmlLocation[0])
        molecule.html = HTMLfile( molecule.htmlLocation[0],
                                  title = 'Molecule ' + molecule.name )
        
        # nb: destination is a destination obj (eg molecule object) that is to 
        # have a html attribute that points to an HTMLfile instance.
        # In the validate.py code, the source argument is the 'main' section in 
        # project.html. JFD doesn't understand why.
        project.html.insertHtmlLinkInTag(     'li',    section=project.html.main, 
            source=project,  destination=molecule, text='mol ref', id=top)
        # rerun for testing.
        link = project.html.findHtmlLocation( project, molecule,id=top )
        self.assertEquals( 'moleculeName/HTML/indexMolecule.html#_top',
                           link)
        project.html.main('ul', openTag=False)

        for htmlObj in [ project.html, molecule.html ]:
            self.assertFalse( htmlObj.render() )

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
