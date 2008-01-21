"""
Unit test execute as:
python $cingPath/PluginCode/test/test_Procheck.py
"""
from cing import cingDirTestsData
from cing import cingDirTestsTmp
from unittest import TestCase
from cing.core.classes import Project
import os
import unittest

class AllChecks(TestCase):
        
    def testMolgrapRun(self):
        
#        SETUP FIRST
        #entryId = "1ai0" # Most complex molecular system in any PDB NMR entry 
        entryId = "xeasy_small" # Small much studied PDB NMR entry 
        pdbFileName = entryId+".pdb"
        pdbFilePath = os.path.join( cingDirTestsData, pdbFileName)
        
        self.failIf( os.chdir(cingDirTestsTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTestsTmp)
        # does it matter to import it just now?
        project = Project.open( entryId, status='new' )
        project.initPDB( pdbFile=pdbFilePath, convention = "BMRB" )
        gifFileName = "out.gif"
        pathGif = os.path.join( cingDirTestsTmp, gifFileName)
        self.assertFalse(project.molecule.export2gif(pathGif))                                    

if __name__ == "__main__":
    unittest.main()
