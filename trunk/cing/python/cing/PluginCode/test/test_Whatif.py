"""
Unit test
python $cingPath/PluginCode/test/test_Whatif.py
"""
from cing import cingDirTestsData
from cing import cingDirTestsTmp
from cing.Libs.NTutils import SetupError
from cing.PluginCode.Whatif import runWhatif
from cing.core.classes import Project
from unittest import TestCase
import os
import unittest

class AllChecks(TestCase):
        
    def testparse(self):
        """whatif db parse"""
        
        #entryId = "1ai0" # Most complex molecular system in any PDB NMR entry 
#        entryId = "2hgh" # Small much studied PDB NMR entry; 48 models 
#        entryId = "1bus" # Small much studied PDB NMR entry:  5 models of 57 AA.: 285 residues.
        entryId = "2hgh" # Small much PDB NMR entry
        pdbFileName = entryId+"_small.pdb"
        pdbFilePath = os.path.join( cingDirTestsData, pdbFileName)
        
        if os.chdir(cingDirTestsTmp):
            raise SetupError("Failed to change to directory for temporary test files: "+cingDirTestsTmp)
        # does it matter to import it just now?
#        project = Project.open( entryId, status='old' )
        project = Project.open( entryId, status='new' )
        project.initPDB( pdbFile=pdbFilePath, convention = "BMRB" )
        print project.save()
        print project.cingPaths.format()
        self.assertTrue(runWhatif(project))                                    

if __name__ == "__main__":
    unittest.main()
