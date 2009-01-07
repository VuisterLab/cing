"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_pdb.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDebug
from cing.core.classes import Project
from cing.core.constants import IUPAC
from unittest import TestCase
import cing
import os
import unittest

class AllChecks(TestCase):

    def testPdbFile(self):
        #entryId = "1ai0" # Most complex molecular system in any PDB NMR entry
        entryId = "1a4d" # Small much studied PDB NMR entry
#        entryId = "1brv_1model" # Small much studied PDB NMR entry
#        entryId = "2hgh_1model"

        pdbDirectory = os.path.join(cingDirTestsData,"pdb", entryId)
        pdbFileName = "pdb"+entryId+".ent"
        pdbFilePath = os.path.join( pdbDirectory, pdbFileName)

        self.failIf( os.chdir(cingDirTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTmp)
        # does it matter to import it just now?
        project = Project( entryId )
        self.failIf( project.removeFromDisk())
        project = Project.open( entryId, status='new' )
        project.initPDB( pdbFile=pdbFilePath, convention = IUPAC )
                
        
if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
