from cing import cingDirTestsTmp
from cing import verbosityError
from cing.core.classes import HTMLfile
from unittest import TestCase
import cing
import os
import unittest

class AllChecks(TestCase):

    def test_classes(self):         
        self.failIf( os.chdir(cingDirTestsTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTestsTmp)
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

if __name__ == "__main__":
    cing.verbosity = verbosityError
    unittest.main()
