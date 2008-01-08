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
        
    def testparse(self):
        """procheck parse"""
        
#        SETUP FIRST
        #entryId = "1ai0" # Most complex molecular system in any PDB NMR entry 
        entryId = "2hgh" # Small much studied PDB NMR entry 
        pdbFileName = entryId+"_small.pdb"
        pdbFilePath = os.path.join( cingDirTestsData, pdbFileName)
        
        self.failIf( os.chdir(cingDirTestsTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTestsTmp)
        # does it matter to import it just now?
        project = Project.open( entryId, status='new' )
        project.initPDB( pdbFile=pdbFilePath, convention = "BMRB" )
        # Note that CING doesn't support chain ids in range selection for procheck. TODO
        # in the case of 2hgh this is not a problem because the residue numbering doesn't
        # overlap between the chain A protein and chain B RNA.
        ranges = "2-11,13-33,35-54"  
            # 1 and 55 are 5' and 3' terminii which are a little looser.
            # 12, and 34 are bases that are not basepaired.
        ranges += ",104-105,115-136,145-190"  
            # 106-114 is a loop
            # 137-144 is a loop
            # 191-193 are 3 Zn ions.
#This leads to a procheck ranges file like:
#        RESIDUES   2  B   11  B
#        RESIDUES  13  B   33  B
#        RESIDUES  35  B   54  B
#        RESIDUES 104  A  105  A
#        RESIDUES 115  A  136  A
#        RESIDUES 145  A  190  A        
        msg = "Was biggles installed properly and is the X11 up to display; even you would expect you don't need it"
        self.failIf(project.procheck(ranges = ranges) is None, msg)                                    

if __name__ == "__main__":
    unittest.main()
