"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_Molgrap.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDebug
from cing.core.classes import Project
from cing.core.constants import CYANA
from cing.core.constants import IUPAC
from cing.core.constants import PDB
from cing.core.constants import XPLOR
from unittest import TestCase
import cing
import os
import unittest

class AllChecks(TestCase):

    def testMolgrapRun(self):
        pdbConvention = CYANA
#        SETUP FIRST
        #entryId = "1ai0" # Most complex molecular system in any PDB NMR entry
        entryId = "1brv_1model" # Small much studied PDB NMR entry
#        entryId = "2hgh_1model"
        if entryId.startswith("1YWUcdGMP"):
            pdbConvention = XPLOR
        if entryId.startswith("2hgh"):
            pdbConvention = CYANA
        if entryId.startswith("1tgq"):
            pdbConvention = PDB
        if entryId.startswith("1brv"):
            pdbConvention = IUPAC
        
        cyanaDirectory = os.path.join(cingDirTestsData,"cyana", entryId)
        pdbFileName = entryId+".pdb"
        pdbFilePath = os.path.join( cyanaDirectory, pdbFileName)

        self.failIf( os.chdir(cingDirTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTmp)
        # does it matter to import it just now?
        project = Project( entryId )
        self.failIf( project.removeFromDisk())
        project = Project.open( entryId, status='new' )
        project.initPDB( pdbFile=pdbFilePath, convention = pdbConvention )
        project.save( )
        gifFileName = entryId+".gif"
        pathGif = os.path.join( cingDirTmp, gifFileName)
        self.assertFalse(project.molecule.export2gif(pathGif, project=None))
        self.assertTrue(os.path.exists(pathGif))
        
if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
