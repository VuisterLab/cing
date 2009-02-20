"""
Unit test
python $CINGROOT/python/cing/PluginCode/test/test_Wattos.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityError
from cing.Libs.NTutils import NTdebug
from cing.PluginCode.Wattos import runWattos
from cing.core.classes import Project
from cing.core.constants import IUPAC
from unittest import TestCase
import cing
import os
import unittest


class AllChecks(TestCase):

    def testparse(self):
        #entryId = "1ai0" # Most complex molecular system in any PDB NMR entry
        entryId = "1brv_1model" # Small much studied PDB NMR entry; 48 models
#        entryId = "1bus" # Small much studied PDB NMR entry:  5 models of 57 AA.: 285 residues.

        self.failIf( os.chdir(cingDirTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTmp)
        project = Project( entryId )
        self.failIf( project.removeFromDisk() )
        project = Project.open( entryId, status='new' )
        cyanaDirectory = os.path.join(cingDirTestsData,"cyana", entryId)
        pdbFileName = entryId+".pdb"
        pdbFilePath = os.path.join( cyanaDirectory, pdbFileName)
        NTdebug("Reading files from directory: " + cyanaDirectory)
        project.initPDB( pdbFile=pdbFilePath, convention = IUPAC )

#        print project.save()
#        NTdebug( project.cingPaths.format() )
        self.assertTrue(runWattos(project))

if __name__ == "__main__":
    cing.verbosity = verbosityError
    cing.verbosity = verbosityDebug
#    NTdebug("This should not show up")
#    NTmessage("And this also not")
    unittest.main()
