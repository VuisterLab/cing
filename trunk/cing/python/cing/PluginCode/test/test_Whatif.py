"""
Unit test
python $cingPath/PluginCode/test/test_Whatif.py
"""
from cing import cingDirTestsData
from cing import cingDirTestsTmp
from cing import verbosityError
from cing.Libs.NTutils import printDebug
from cing.PluginCode.Whatif import runWhatif
from cing.core.classes import Project
from unittest import TestCase
import cing
import os
import unittest

class AllChecks(TestCase):
        
    def testparse(self):        
        #entryId = "1ai0" # Most complex molecular system in any PDB NMR entry 
#        entryId = "2hgh" # Small much studied PDB NMR entry; 48 models 
#        entryId = "1bus" # Small much studied PDB NMR entry:  5 models of 57 AA.: 285 residues.
        entryId = "2hgh" # Small much PDB NMR entry
        

#        entryId = "1brv" # Small much studied PDB NMR entry 
        self.failIf( os.chdir(cingDirTestsTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTestsTmp)
        project = Project( entryId )
        self.failIf( project.removeFromDisk() )
        project = Project.open( entryId, status='new' )
        cyanaDirectory = os.path.join(cingDirTestsData,"cyana", entryId)
        pdbFileName = entryId+".pdb"
        pdbFilePath = os.path.join( cyanaDirectory, pdbFileName)
        printDebug("Reading files from directory: " + cyanaDirectory)
        project.initPDB( pdbFile=pdbFilePath, convention = "BMRB" )

#        print project.save()
#        print project.cingPaths.format()
        self.assertFalse(runWhatif(project))                                    

if __name__ == "__main__":
    cing.verbosity = verbosityError
#    cing.verbosity = verbosityDebug
    unittest.main()
