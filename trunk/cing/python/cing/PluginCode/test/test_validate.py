"""
Unit test
python $cingPath/PluginCode/test/test_validate.py
"""
from cing import cingDirTestsData
from cing import cingDirTestsTmp
from cing import verbosityError
from cing.Libs.NTutils import printDebug
from cing.core.classes import Project
from cing.core.constants import CYANA
from unittest import TestCase
import cing
import os
import unittest
#from cing import verbosityDebug

class AllChecks(TestCase):
 
    def testRun(self):
#        entryId = "2hgh" # RNA-protein complex.
        entryId = "1brv_1model" # Small much studied PDB NMR entry 
        self.failIf( os.chdir(cingDirTestsTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTestsTmp)
        project = Project( entryId )
        self.failIf( project.removeFromDisk() )
        project = Project.open( entryId, status='new' )
        cyanaDirectory = os.path.join(cingDirTestsData,"cyana", entryId)
        pdbFileName = entryId+".pdb"
        pdbFilePath = os.path.join( cyanaDirectory, pdbFileName)
        project.initPDB( pdbFile=pdbFilePath, convention = "BMRB" )
        printDebug("Reading files from directory: " + cyanaDirectory) 
        project.cyana2cing(cyanaDirectory=cyanaDirectory, convention=CYANA,
                    uplFiles  = [ entryId ],
                    acoFiles  = [ entryId ],
                    copy2sources = True
        )
        project.save()
        self.assertFalse( project.validate())

if __name__ == "__main__":
    cing.verbosity = verbosityError
#    cing.verbosity = verbosityDebug
    unittest.main()
