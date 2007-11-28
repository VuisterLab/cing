"""
Unit test execute as:
python $cingPath/PluginCode/test/test_Procheck.py
"""
from cing.PluginCode.test.localSettings import procheckPath
from cing.PluginCode.test.settings import cingDirTestsData
from cing.PluginCode.test.settings import cingDirTestsTmp
from cing.core.classes import Project
from cing.core.parameters import cingPaths
from unittest import TestCase
import os
import unittest

class AllChecks(TestCase):
        
    def testparse(self):
        """procheck parse"""
        
#        SETUP FIRST
        #entryId = "1ai0" # Most complex molecular system in any PDB NMR entry 
        entryId = "1brv" # Small much studied PDB NMR entry 
        pdbFileName = entryId+".pdb"
        pdbFilePath = os.path.join( cingDirTestsData, pdbFileName)
        
        self.failIf( os.chdir(cingDirTestsTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTestsTmp)
        # does it matter to import it just now?
        project = Project.open( entryId, status='new' )
        project.initPDB( pdbFile=pdbFilePath, convention = "BMRB" )

        cingPaths.procheck_nmr = procheckPath # somehow this doesn't get in despite the above
        self.failIf(project.procheck() is None,"Was biggles installed properly and is the X11 up to display; even you would expect you don't need it")                                    

if __name__ == "__main__":
    unittest.main()
