"""
Unit test execute as:
python $cingPath/PluginCode/test/test_Procheck.py
"""
from cing import cingDirTestsData
from cing import cingDirTestsTmp
from cing import verbosityDebug
from cing.core.classes import Project
from unittest import TestCase
from cing.Libs.NTutils import NTdebug
import cing
import os 
import unittest

class AllChecks(TestCase):
        
    def testparse(self):        
        #entryId = "1ai0" # Most complex molecular system in any PDB NMR entry 
        entryId = "1brv" # Small much studied PDB NMR entry 
        ranges = None
        if entryId == "2hgh":
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
            
        self.failIf( os.chdir(cingDirTestsTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTestsTmp)
        project = Project( entryId )
        self.failIf( project.removeFromDisk() )
        project = Project.open( entryId, status='new' )
        cyanaDirectory = os.path.join(cingDirTestsData,"cyana", entryId)
        pdbFileName = entryId+".pdb"
        pdbFilePath = os.path.join( cyanaDirectory, pdbFileName)
        project.initPDB( pdbFile=pdbFilePath, convention = "BMRB" )
        NTdebug("Reading files from directory: " + cyanaDirectory)
        project.save()
        self.failIf(project.procheck(ranges = ranges, createPlots=False, runAqua=False) is None)                                    
        for res in project.molecule.allResidues():
            NTdebug(`res` +" "+ `res.procheck.secStruct`)
        
if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
    
