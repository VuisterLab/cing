"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test2_pdb.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDebug
from cing.Libs.NTutils import NTwarning
from cing.core.classes import Project
from cing.core.constants import IUPAC
from unittest import TestCase
import cing
import os
import unittest

class AllChecks(TestCase):

    def testPdbFile(self):
        NTwarning("This test case will take about 5 minutes and is recommended to be done before major releases.")
    #        entryId = "1ai0" # Most complex molecular system in any PDB NMR entry
        entryList = "1a4d".split() # Small much studied PDB NMR entry
    #        entryId = "1brv" # Small much studied PDB NMR entry
    #        entryId = "2hgh_1model"
#        entryList = "1kr8".split()
#        entryList = "1otz".split() # 61 chains of which one is ' '
#        entryList = "1a4d 1a24 1afp 1ai0 1brv 1bus 1cjg 1hue 1ieh 1iv6 1kr8 1otz 2hgh 2k0e".split()
        for entryId in entryList:        
    
            pdbDirectory = os.path.join(cingDirTestsData,"pdb", entryId)
            pdbFileName = "pdb"+entryId+".ent"
            pdbFilePath = os.path.join( pdbDirectory, pdbFileName)
    
            self.failIf( os.chdir(cingDirTmp), msg=
                "Failed to change to directory for temporary test files: "+cingDirTmp)
            # does it matter to import it just now?
            project = Project( entryId )
            self.failIf( project.removeFromDisk())
            project = Project.open( entryId, status='new' )
            self.assertTrue( project.initPDB( pdbFile=pdbFilePath, convention=IUPAC, allowNonStandardResidue=True ))
            self.assertTrue( project.save() )
        
if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
