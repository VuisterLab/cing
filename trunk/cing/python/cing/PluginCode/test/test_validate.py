"""
Unit test
python $cingPath/PluginCode/test/test_Wattos.py
"""
from cing import cingRoot
from cing.Libs.NTutils import SetupError
from cing.core.classes import Project
from unittest import TestCase
from cing import cingDirTestsTmp
from cing import cingDirTestsData
import os
import unittest

class AllChecks(TestCase):
        
    def testrun(self):
        """wattos run check"""
#        SETUP FIRST
        dirTestsData        = os.path.join(cingRoot, "Tests", "data" )         
        if os.chdir(cingDirTestsTmp):
            raise SetupError("Failed to change to directory for temporary test files: "+cingDirTestsTmp)

        entryId = "1brv" # Small much studied PDB NMR entry 
        pdbFileName = entryId+"_small.pdb"
        pdbFilePath = os.path.join( cingDirTestsData, pdbFileName)
        check_FileName = entryId + "_check_small.db"
        check_FilePath = os.path.join( dirTestsData, check_FileName )
        self.assertTrue(os.path.exists(check_FilePath))
 
        
        if os.chdir(cingDirTestsTmp):
            raise SetupError("Failed to change to directory for temporary test files: "+cingDirTestsTmp)
        project = Project.open( entryId, status='new' )
        project.initPDB( pdbFile=pdbFilePath, convention = "BMRB" )
        print project.cingPaths.format()
        project.validate()
             
if __name__ == "__main__":
    unittest.main()
