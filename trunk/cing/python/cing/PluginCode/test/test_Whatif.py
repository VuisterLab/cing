"""
Unit test
python $cingPath/PluginCode/test/test_Whatif.py
"""
from cing.Libs.NTutils import SetupError
from cing.PluginCode.Whatif import runWhatif
from cing.PluginCode.test.settings import cingDirTestsTmp
from cing.core.classes import Project
from unittest import TestCase
import os
import unittest


class AllChecks(TestCase):
        
    def testparse(self):
        """whatif db parse"""
        
        #entryId = "1ai0" # Most complex molecular system in any PDB NMR entry 
#        entryId = "1brv" # Small much studied PDB NMR entry; 48 models 
        entryId = "1bus" # Small much studied PDB NMR entry:  5 models of 57 AA.: 285 residues.
#        pdbFileName = entryId+".pdb"
#        pdbFilePath = os.path.join( cingDirTestsData, pdbFileName)
        
        if os.chdir(cingDirTestsTmp):
            raise SetupError("Failed to change to directory for temporary test files: "+cingDirTestsTmp)
        # does it matter to import it just now?
        project = Project.open( entryId, status='old' )
#        project = cing.Project.open( entryId, status='new' )
#        project.initPDB( pdbFile=pdbFilePath, convention = "BMRB" )
        print project.save()
        print project.cingPaths.format()
#        project.validate()        
#        ipshell = IPShellEmbed('',  banner   = '--------Dropping to IPython--------',
#                                    exit_msg = '--------Leaving IPython--------')
#        ipshell()
        self.assertTrue(runWhatif(project))                                    

if __name__ == "__main__":
    unittest.main()
