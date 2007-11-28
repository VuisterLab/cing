"""
Unit test
python $cingPath/PluginCode/test/test_Wattos.py
"""
from cing import cingRoot
from cing.Libs.NTutils import SetupError
from cing.Libs.NTutils import printMessage
from cing.PluginCode.Whatif import Whatif
from cing.PluginCode.test.settings import cingDirTestsData
from cing.PluginCode.test.settings import cingDirTestsTmp
from cing.core.classes import Project
from unittest import TestCase
import os
import unittest

class AllChecks(TestCase):
        
    def testrun(self):
        """wattos run check"""
#        SETUP FIRST
        # Redefine to be a tiny one included in distribution.
#        fileName = "check.db"
        macroFileName = "QuitBeforeBegun.wcf"
        dirTestsData        = os.path.join(cingRoot, "Tests", "data" )
        filePath = os.path.join( dirTestsData, macroFileName )
        printMessage("filePath: "+ filePath)
        self.assertTrue(os.path.exists(filePath))
 
        #entryId = "1ai0" # Most complex molecular system in any PDB NMR entry 
#        entryId = "1brv" # Small much studied PDB NMR entry 
#        pdbFileName = entryId+".pdb"
#        pdbFilePath = os.path.join( cingDirTestsData, pdbFileName)
        
        if os.chdir(cingDirTestsTmp):
            raise SetupError("Failed to change to directory for temporary test files: "+cingDirTestsTmp)
        # does it matter to import it just now?
        fileName = "check_small.db"
        dirTestsData        = os.path.join(cingRoot, "Tests", "data" )
        filePath = os.path.join( dirTestsData, fileName )
        printMessage("filePath: "+ filePath)
        self.assertTrue(os.path.exists(filePath))
 
        #entryId = "1ai0" # Most complex molecular system in any PDB NMR entry 
        entryId = "1brv" # Small much studied PDB NMR entry 
        pdbFileName = entryId+".pdb"
        pdbFilePath = os.path.join( cingDirTestsData, pdbFileName)
        
        if os.chdir(cingDirTestsTmp):
            raise SetupError("Failed to change to directory for temporary test files: "+cingDirTestsTmp)
        project = Project.open( entryId, status='new' )
        project.initPDB( pdbFile=pdbFilePath, convention = "BMRB" )
        print project.cingPaths.format()
#        project.validate()
        
#        ipshell = IPShellEmbed('',  banner   = '--------Dropping to IPython--------',
#                                    exit_msg = '--------Leaving IPython--------')
#        ipshell()

                
        whatif = Whatif(molecule=project.molecule)
        whatif.checkdbFile=filePath
        self.failIf(whatif.parseCheckdb() is None)                                    

if __name__ == "__main__":
    unittest.main()
