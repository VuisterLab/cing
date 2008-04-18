from cing import cingDirTestsTmp
from cing import verbosityDebug
from cing import verbosityError
from cing.core.classes import HTMLfile
from cing.core.classes import Project
from unittest import TestCase
from cing.Libs.NTutils import removedir
from cing.Libs.NTutils import NTdebug
from cing.core.parameters import htmlDirectories
from cing.core.parameters import moleculeDirectories
from cing.core.molecule import Molecule
import cing
import os
import unittest

class AllChecks(TestCase):

    os.chdir(cingDirTestsTmp)
    
    def tttest_HTMLfile_simple(self):         
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

    def test_HTMLfile_links(self):
        
        """
        Create two html files that have relative links to each other.
        Exercising the machinery in HTMLfile class.
        """
        entryId = "test_HTMLfile_links" # Small much studied PDB NMR entry 
        self.failIf( os.chdir(cingDirTestsTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTestsTmp)
        project = Project( entryId )
        self.failIf( project.removeFromDisk() )
        project = Project.open( entryId, status='new' )
        molecule = Molecule( name='moleculeName' )
        project.appendMolecule(molecule)

        # initialize project html page
        top = '#_top'
        
        # per item always set 2 toplevel attributes:
        project.htmlLocation = (project.path('index.html'), top)
        project.html = HTMLfile( project.htmlLocation[0], title = 'Project' )
        #create new folders for Molecule/HTML
        htmlPath = project.htmlPath() # JFD doesn't understand why this is specific to the molecule too.
        if os.path.exists( htmlPath ):
            removedir( htmlPath )
        os.makedirs( htmlPath )
        NTdebug("htmlPath: %s" % htmlPath)

        # initialize molecule html page
        for subdir in htmlDirectories.values():
            project.mkdir( project.molecule.name, moleculeDirectories.html, subdir )

        if hasattr(molecule, 'html'):
            del(molecule['html'])

        molecule.htmlLocation = (project.htmlPath('index.html'), top)
        NTdebug("molecule.htmlLocation[0]: %s" % molecule.htmlLocation[0])
        molecule.html = HTMLfile( molecule.htmlLocation[0],
                                  title = 'Molecule ' + molecule.name )
        
        # nb: destination is a destination obj (eg molecule object) that is to 
        # have a html attribute that points to an HTMLfile instance.
        # In the validate.py code, the source argument is the 'main' section in 
        # project.html. JFD doesn't understand why.
        project.html.insertHtmlLinkInTag(     'li',    section=project.html.main, 
            source=project.html.main,  destination=molecule, text='mol ref')
        project.html.main('ul', openTag=False)

        for htmlObj in [ project.html, molecule.html ]:
            self.assertFalse( htmlObj.render() )

if __name__ == "__main__":
    cing.verbosity = verbosityError
    cing.verbosity = verbosityDebug
    unittest.main()
