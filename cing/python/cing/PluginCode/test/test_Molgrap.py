"""
Unit test execute as:
python $cingPath/PluginCode/test/test_Procheck.py
"""
from cing import cingDirTestsData
from cing import cingDirTestsTmp
from cing import verbosityDebug
from cing.core.classes import Project
from cing.core.constants import CYANA
from unittest import TestCase
import cing
import os
import unittest

class AllChecks(TestCase):
        
    def testMolgrapRun(self):
        pdbConvention = CYANA
#        SETUP FIRST
        #entryId = "1ai0" # Most complex molecular system in any PDB NMR entry 
#        entryId = "1brv" # Small much studied PDB NMR entry         
        entryId = "2hgh_1model"      
        cyanaDirectory = os.path.join(cingDirTestsData,"cyana", entryId)
        pdbFileName = entryId+".pdb"
        pdbFilePath = os.path.join( cyanaDirectory, pdbFileName)
        
        self.failIf( os.chdir(cingDirTestsTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTestsTmp)
        # does it matter to import it just now?
        project = Project.open( entryId, status='new' )
        project.initPDB( pdbFile=pdbFilePath, convention = pdbConvention )
        gifFileName = entryId+".gif"
        pathGif = os.path.join( cingDirTestsTmp, gifFileName)
        self.assertFalse(project.molecule.export2gif(pathGif))                                    

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
