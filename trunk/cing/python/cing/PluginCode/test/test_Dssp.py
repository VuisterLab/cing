"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_Dssp.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityDefault
from cing.Libs.NTutils import NTdebug
from cing.core.classes import Project
from cing.core.constants import BMRB
from cing.core.constants import CYANA
from cing.core.constants import PDB
from cing.core.constants import XPLOR
from unittest import TestCase
from cing.Libs.NTutils import getDeepByKeys
from cing.PluginCode.dssp import DSSP_STR
from cing.PluginCode.procheck import SECSTRUCT_STR
import cing
import os 
import unittest

class AllChecks(TestCase):
        
    def testDssp(self):
        showDsspResults = True        
        #entryId = "1ai0" # Most complex molecular system in any PDB NMR entry 
        entryId = "1brv_1model" # Small much studied PDB NMR entry 
#        entryId = "1YWUcdGMP" # Example entry from external user, Martin Allan
        ranges = None
        pdbConvention = BMRB
        if entryId.startswith("1YWUcdGMP"):
            pdbConvention = XPLOR
        if entryId.startswith("2hgh"):
            pdbConvention = CYANA
        if entryId.startswith("1tgq"):
            pdbConvention = PDB
        if entryId.startswith("1brv"):
            pdbConvention = CYANA
            
        if entryId == "2hgh":
            # Note that CING doesn't support chain ids in range selection for dssp. TODO
            # in the case of 2hgh this is not a problem because the residue numbering doesn't
            # overlap between the chain A protein and chain B RNA.
            ranges = "2-11,13-33,35-54"  
                # 1 and 55 are 5' and 3' terminii which are a little looser.
                # 12, and 34 are bases that are not basepaired.
            ranges += ",104-105,115-136,145-190"  
                # 106-114 is a loop
                # 137-144 is a loop
                # 191-193 are 3 Zn ions.
    #This leads to a dssp ranges file like:
    #        RESIDUES   2  B   11  B
    #        RESIDUES  13  B   33  B
    #        RESIDUES  35  B   54  B
    #        RESIDUES 104  A  105  A
    #        RESIDUES 115  A  136  A
    #        RESIDUES 145  A  190  A        
            
        self.failIf( os.chdir(cingDirTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTmp)
        project = Project( entryId )
        self.failIf( project.removeFromDisk() )
        project = Project.open( entryId, status='new' )
        cyanaDirectory = os.path.join(cingDirTestsData,"cyana", entryId)
        pdbFileName = entryId+".pdb"
        pdbFilePath = os.path.join( cyanaDirectory, pdbFileName)
        project.initPDB( pdbFile=pdbFilePath, convention = pdbConvention )

        project.save()
        self.failIf(project.dssp() is None)
        
        if showDsspResults:                                    
            for res in project.molecule.allResidues():
                NTdebug(`res` +" "+ `getDeepByKeys(res,DSSP_STR,SECSTRUCT_STR)`)
        
if __name__ == "__main__":
    cing.verbosity = verbosityDefault
    cing.verbosity = verbosityDebug
    unittest.main()    
