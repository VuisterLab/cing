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
from shutil import move #@UnusedImport
from shutil import rmtree
import cing
import os
import tarfile
import unittest

class AllChecks(TestCase):

    def testInitCcpn(self):
#        entryList = "1a4d 1a24 1afp 1ai0 1brv 1bus 1cjg 1hue 1ieh 1iv6 1kr8 2hgh 2k0e".split()
#1iv6 needs better ccpn file from FC
        entryList = ["SRYBDNA"]
#        entryList = ["1brv"]

        self.failIf( os.chdir(cingDirTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTmp)
        for entryId in entryList:
            project = Project.open( entryId, status='new' )
            self.assertTrue(project, 'Failed opening project: ' + entryId)

            ccpnFile = os.path.join(cingDirTestsData,"ccpn", entryId+".tgz")
            try:
                rmtree( entryId )
            except:
                pass
            tar = tarfile.open(ccpnFile, "r:gz")
            for itar in tar:
                tar.extract(itar.name, '.')

            org = 'linkNmrStarData'
            if entryId == 'SRYBDNA': # TODO: mod the NRG examples to follow this convention too.
                org = entryId
            move( org, entryId)
            self.assertFalse(project.initCcpn(ccpnFolder=entryId))
            self.failIf(project.save())
            self.assertFalse(project.validate(htmlOnly=False,
                                              doProcheck = True,
                                              doWhatif=True ))

            self.assertFalse(project.removeCcpnReferences())


if __name__ == "__main__":
    cing.verbosity = verbosityDetail
    cing.verbosity = verbosityOutput
    cing.verbosity = verbosityDebug
    unittest.main()
