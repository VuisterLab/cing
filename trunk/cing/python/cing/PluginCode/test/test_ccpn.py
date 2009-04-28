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
from cing.PluginCode.Ccpn import Ccpn #@UnusedImport needed to throw a ImportWarning so that the test is handled properly.
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

    def testInitCcpn(self):
        entryList = "1kr8".split()
#        entryList = "1ai0".split()
#        entryList = "1ti3".split()
#        entryList = "Cu_CopK".split()
#        entryList = "1hue".split()
#        entryList = "H1GI".split()
#        entryList = "taf3".split()
#        entryList = "1a4d".split()
#        entryList = "2k0e_all".split()

#        entryList = "a18v_xeasy".split()
#        entryList = "1a4d 1a24 1afp 1ai0 1brv 1bus 1cjg 1hue 1ieh 1iv6 1kr8 2hgh 2k0e SRYBDNA Parvulustat".split()

#        if you have a local copy you can use it; make sure to adjust the path setting below.
        fastestTest = True

        htmlOnly = False # default is False but enable it for faster runs without some actual data.
        doWhatif = True # disables whatif actual run
        doProcheck = True
        doWattos = True
        useNrgArchive = False
        modelCount=None
        if fastestTest:
            modelCount=2
            htmlOnly = True
            doWhatif = False
            doProcheck = False
            doWattos = False
#            useNrgArchive = False
        self.failIf(os.chdir(cingDirTmp), msg =
            "Failed to change to directory for temporary test files: " + cingDirTmp)
        for entryId in entryList:
            project = Project.open(entryId, status = 'new')
            self.assertTrue(project, 'Failed opening project: ' + entryId)

            if useNrgArchive: # default is False
#                inputArchiveDir = os.path.join('/Library/WebServer/Documents/NRG-CING/recoordSync', entryId)
                # Mounted from nmr.cmbi.ru.nl
#                inputArchiveDir = os.path.join('/Volumes/tera1/Library/WebServer/Documents/NRG-CING/recoordSync', entryId)
                inputArchiveDir = os.path.join('/Volumes/tera1//Users/jd/ccpn_tmp/data/recoord', entryId)
            else:
                inputArchiveDir = os.path.join(cingDirTestsData, "ccpn")

            ccpnFile = os.path.join(inputArchiveDir, entryId + ".tgz")
            if not os.path.exists(ccpnFile):
                ccpnFile = os.path.join(inputArchiveDir, entryId + ".tar.gz")

            self.assertTrue(project.initCcpn(ccpnFolder = ccpnFile, modelCount=modelCount))
            self.assertTrue(project.save())
            self.assertFalse(project.validate(htmlOnly = htmlOnly,
                                              doProcheck = doProcheck,
                                              doWhatif = doWhatif,
                                              doWattos=doWattos ))
#            self.assertTrue(project.exportValidation2ccpn())
#            self.assertFalse(project.removeCcpnReferences())

    def tttestCreateCcpn(self):
        pdbConvention = IUPAC
        restraintsConvention = CYANA
        entryId = "1brv_1model" # Small much studied PDB NMR entry
        if entryId.startswith("1YWUcdGMP"):
            pdbConvention = XPLOR
        if entryId.startswith("2hgh"):
            pdbConvention = CYANA
        if entryId.startswith("1tgq"):
            pdbConvention = PDB
        if entryId.startswith("1brv"):
            pdbConvention = IUPAC

        self.failIf(os.chdir(cingDirTmp), msg =
            "Failed to change to directory for temporary test files: " + cingDirTmp)
        project = Project(entryId)
        self.failIf(project.removeFromDisk())
        project = Project.open(entryId, status = 'new')
        cyanaDirectory = os.path.join(cingDirTestsData, "cyana", entryId)
        pdbFileName = entryId + ".pdb"
        pdbFilePath = os.path.join(cyanaDirectory, pdbFileName)
        project.initPDB(pdbFile = pdbFilePath, convention = pdbConvention)

        NTdebug("Reading files from directory: " + cyanaDirectory)
        kwds = {'uplFiles': [ entryId ],
                'acoFiles': [ entryId ]
                  }
        if entryId.startswith("1YWUcdGMP"):
            del(kwds['acoFiles'])

        if os.path.exists(os.path.join(cyanaDirectory, entryId + ".prot")):
            self.assertTrue(os.path.exists(os.path.join(cyanaDirectory, entryId + ".seq")),
                "Converter for cyana also needs a seq file before a prot file can be imported")
            kwds['protFile'] = entryId
            kwds['seqFile'] = entryId

        # Skip restraints if absent.
        if os.path.exists(os.path.join(cyanaDirectory, entryId + ".upl")):
            project.cyana2cing(cyanaDirectory = cyanaDirectory, convention = restraintsConvention,
                        copy2sources = True,
                        **kwds)
#        project.save()
        ccpnFolder = entryId
        self.assertTrue(project.createCcpn(ccpnFolder))
        self.assertTrue(project.saveCcpn())

if __name__ == "__main__":
    cing.verbosity = verbosityDetail
    cing.verbosity = verbosityOutput
    cing.verbosity = verbosityDebug
    unittest.main()
