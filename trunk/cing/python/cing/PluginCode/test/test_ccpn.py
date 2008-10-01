"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_ccpn.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityDetail
from cing import verbosityOutput
from cing.core.classes import Project
from unittest import TestCase
from shutil import move
import cing
import os
import tarfile
import unittest

class AllChecks(TestCase):

    def testInitCcpn(self):
#        entryId = "1brv" # Small much studied PDB NMR entry
        entryId = "2k0e" # Small much studied PDB NMR entry
#        entryId = "berlin_demo" # Small much studied PDB NMR entry
        entryList = [ ]
        self.failIf( os.chdir(cingDirTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTmp)
        project = Project.open( entryId, status='new' )
        self.assertTrue(project, 'Failed opening project: ' + entryId)

        ccpnFile = os.path.join(cingDirTestsData,"ccpn", entryId+".tgz")
        tar = tarfile.open(ccpnFile, "r:gz")
        for itar in tar:
            tar.extract(itar.name, '.')
            
#        move( 'linkNmrStarData', entryId)
        self.assertFalse(project.initCcpn(ccpnFile=entryId))
        self.failIf(project.save())
        self.assertFalse(project.validate(htmlOnly=True,
                                          doProcheck = False,
                                          doWhatif=False ))


if __name__ == "__main__":
    cing.verbosity = verbosityDetail
    cing.verbosity = verbosityOutput
    cing.verbosity = verbosityDebug
    unittest.main()
