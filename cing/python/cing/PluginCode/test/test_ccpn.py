"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_ccpn.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityDetail
from cing import verbosityOutput
from cing.Libs.NTutils import NTdebug
from cing.core.classes import Project
from cing.core.constants import CYANA
from unittest import TestCase
import cing
import os
import unittest

class AllChecks(TestCase):

    def ttttestExport2Ccpn(self):
        entryId = "1brv" # Small much studied PDB NMR entry
        self.failIf( os.chdir(cingDirTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTmp)
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
#        project.save()
        self.failIf(project.export2Ccpn() is None)
        self.failIf(project.save())

        del(project)

        entryId = "1brv" # Small much studied PDB NMR entry
        self.failIf( os.chdir(cingDirTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTmp)

    def testInitCcpn(self):
        entryId = "1brv" # Small much studied PDB NMR entry
        self.failIf( os.chdir(cingDirTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTmp)
        project = Project.open( entryId, status='new' )
        self.assertTrue(project, 'Failed opening project: ' + entryId)

        ccpnFile = os.path.join(cingDirTestsData,"ccpn", entryId)
        self.assertFalse(project.initCcpn(ccpnFile=ccpnFile))
        self.failIf(project.save())
#        htmlOnly = False # default is False but enable it for faster runs without some actual data.
#        doWhatif = False # disables whatif actual run
#        doProcheck = False
        
#        self.assertFalse(project.validate(htmlOnly=htmlOnly,
#                                          doProcheck = doProcheck,
#                                          doWhatif=doWhatif ))
        

if __name__ == "__main__":
    cing.verbosity = verbosityDetail
    cing.verbosity = verbosityOutput
    cing.verbosity = verbosityDebug
    unittest.main()
