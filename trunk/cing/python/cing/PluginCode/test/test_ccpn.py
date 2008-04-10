"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_ccpn.py
"""
from cing import cingDirTestsData
from cing import cingDirTestsTmp
from cing import verbosityError
from cing.Libs.NTutils import NTdebug
from cing.PluginCode.ccpn import initCcpn
from cing.core.classes import Project
from cing.core.constants import CYANA
from unittest import TestCase
import cing
import os
import unittest

class AllChecks(TestCase):

    def ttttestExport2Ccpn(self):
        entryId = "1brv" # Small much studied PDB NMR entry
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
        project.cyana2cing(cyanaDirectory=cyanaDirectory, convention=CYANA,
                    uplFiles  = [ entryId ],
                    acoFiles  = [ entryId],
                    copy2sources = True
        )
#        project.save()
#        self.assertFalse( project.validate())
#        project.save( )
        self.failIf(project.export2Ccpn() is None)
        self.failIf(project.save())

        del(project)

        entryId = "1brv" # Small much studied PDB NMR entry
        self.failIf( os.chdir(cingDirTestsTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTestsTmp)

    def tttestInitCcpn(self):
        entryId = "1brv" # Small much studied PDB NMR entry
        self.failIf( os.chdir(cingDirTestsTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTestsTmp)
        project = Project( "test_for_ccpn_cing_project" )
        ccpnFile = os.path.join(entryId+".cing", "Data", "CCPN", entryId+".xml")
        project = initCcpn(cingProject=project, ccpnFile=ccpnFile)
        self.failIf(project)

if __name__ == "__main__":
    cing.verbosity = verbosityError
    unittest.main()
