"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_Molgrap.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.molgrap import Molgrap #@UnusedImport Keep to indicate dep and proper handeling.
from cing.core.classes import Project
from cing.core.constants import * #@UnusedWildImport
from unittest import TestCase
import shutil
import unittest

class AllChecks(TestCase):

    cingDirTmpTest = os.path.join( cingDirTmp, 'test_Molgrap' )
    mkdirs( cingDirTmpTest )
    os.chdir(cingDirTmpTest)

    def testMolgrapRunFromPdbFile(self):
        pdbConvention = CYANA
#        SETUP FIRST
        #entryId = "1ai0" # Most complex molecular system in any PDB NMR entry
#        entryId = "1a4d" # Small much studied PDB NMR entry
        entryId = "1brv_1model" # Small much studied PDB NMR entry
#        entryId = "2hgh_1model"
        if entryId.startswith("1YWUcdGMP"):
            pdbConvention = XPLOR
        if entryId.startswith("2hgh"):
            pdbConvention = CYANA
        if entryId.startswith("1tgq") or entryId.startswith("1a4d"):
            pdbConvention = PDB
        if entryId.startswith("1brv"):
            pdbConvention = IUPAC

        cyanaDirectory = os.path.join(cingDirTestsData,"cyana", entryId)
        pdbFileName = entryId+".pdb"
        pdbFilePath = os.path.join( cyanaDirectory, pdbFileName)

        # does it matter to import it just now?
        project = Project( entryId )
        self.failIf( project.removeFromDisk())
        project = Project.open( entryId, status='new' )
        project.initPDB( pdbFile=pdbFilePath, convention = pdbConvention )
        project.save( )
        gifFileName = entryId+".gif"
        pathGif = os.path.join( self.cingDirTmpTest, gifFileName)
        self.assertFalse(project.molecule.export2gif(pathGif, project=None))
        self.assertTrue(os.path.exists(pathGif))

    def ttttestMolgrapRunFromCcpnFile(self):
#        entryId = "1cjg" # Nucleic acid entry.

        entryId = "1brv" # Nucleic acid entry.
        project = Project.open( entryId, status='new' )
        self.assertTrue(project, 'Failed opening project: ' + entryId)

        ccpnFile = os.path.join(cingDirTestsData,"ccpn", entryId+".tgz")
        self.assertTrue(project.initCcpn(ccpnFolder=ccpnFile))
        self.assertTrue(project.save())

        gifFileName = entryId+".gif"
        pathGif = os.path.join( cingDirTmp, gifFileName)
        self.assertFalse(project.molecule.export2gif(pathGif, project=None))
        self.assertTrue(os.path.exists(pathGif))
        # Do not leave the old CCPN directory laying around since it might get added to by another test.
        if os.path.exists(entryId):
            self.assertFalse(shutil.rmtree(entryId))


if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
