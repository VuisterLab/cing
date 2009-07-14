"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_cingTestData.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityDetail
from cing import verbosityOutput
from cing.Libs.NTutils import NTmessage
from cing.PluginCode.Ccpn import Ccpn #@UnusedImport needed to throw a ImportWarning so that the test is handled properly.
from cing.core.classes import Project
from unittest import TestCase
import cing
import os
import shutil
import unittest

class AllChecks(TestCase):

    def testInitCcpn(self):
        entryList = "1brv".split()
#        entryList = "1i1s 1ka3 1tgq 1y4o".split()
#        if you have a local copy you can use it; make sure to adjust the path setting below.
        fastestTest = True

        htmlOnly = False # default is False but enable it for faster runs without some actual data.
        doWhatif = False # disables whatif actual run
        doProcheck = False
        doWattos = False
        useNrgArchive = False
        if fastestTest:
            htmlOnly = True
            doWhatif = False
            doProcheck = False
            doWattos = False
#            useNrgArchive = False
        self.failIf(os.chdir(cingDirTmp), msg =
            "Failed to change to directory for temporary test files: " + cingDirTmp)
        for entryId in entryList:
            if useNrgArchive: # default is False
#                inputArchiveDir = os.path.join('/Library/WebServer/Documents/NRG-CING/recoordSync', entryId)
                # Mounted from nmr.cmbi.ru.nl
#                inputArchiveDir = os.path.join('/Volumes/tera1/Library/WebServer/Documents/NRG-CING/recoordSync', entryId)
                inputArchiveDir = os.path.join('/Volumes/tera1//Users/jd/ccpn_tmp/data/recoord', entryId)
            else:
                inputArchiveDir = os.path.join(cingDirTestsData, "cing")

            cingFile = os.path.join(inputArchiveDir, entryId + ".cing.tgz")
            self.assertTrue( os.path.exists(cingFile), "Failed to find file: " + cingFile)

            cingDirNew = os.path.join(cingDirTmp, entryId + ".cing")
            if os.path.exists(cingDirNew):
                NTmessage("Removing old cing project directory: " + cingDirNew )
                shutil.rmtree( cingDirNew )

            shutil.copy(cingFile, cingDirTmp)
            project = Project.open(entryId, status = 'old')
            self.assertTrue(project, 'Failed opening project: ' + entryId)

            self.assertFalse(project.validate(htmlOnly = htmlOnly,
                                              doProcheck = doProcheck,
                                              doWhatif = doWhatif,
                                              doWattos=doWattos ))
            self.assertTrue(project.save())

if __name__ == "__main__":
    cing.verbosity = verbosityDetail
    cing.verbosity = verbosityOutput
    cing.verbosity = verbosityDebug
    unittest.main()
