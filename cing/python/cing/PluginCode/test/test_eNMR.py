"""
Unit test execute as:
python -u $CINGROOT/python/cing/PluginCode/test/test_eNMR.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityDetail
from cing import verbosityOutput
from cing.PluginCode.Ccpn import Ccpn #@UnusedImport needed to throw a ImportWarning so that the test is handled properly.
from cing.core.classes import Project
from unittest import TestCase
import cing
import os
import unittest

class AllChecks(TestCase):

    def testInitCcpn(self):
#        entryList = "CuTTHAcis CuTTHAtrans Parvulustat TTSco apoTTHAcis apoTTHAtrans BASP mia40 taf3 wln34".split()
#        entryList = "taf3".split()
        entryList = "mia40".split()

#        if you have a local copy you can use it; make sure to adjust the path setting below.
        fastestTest = True
        
        htmlOnly = True # default is False but enable it for faster runs without some actual data.
        doWhatif = False # disables whatif actual run
        doProcheck = False
        doWattos = True
        modelCount=1
        if fastestTest:
            modelCount=1
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

            inputArchiveDir = os.path.join(cingDirTestsData, "eNMRworkshop")

            ccpnFile = os.path.join(inputArchiveDir, entryId, entryId + ".tgz")
            self.assertTrue(project.initCcpn(ccpnFolder = ccpnFile, modelCount=modelCount))
            self.assertTrue(project.save())
            self.assertFalse(project.validate(htmlOnly = htmlOnly,
                                              doProcheck = doProcheck,
                                              doWhatif = doWhatif,
                                              doWattos=doWattos ))

if __name__ == "__main__":
    cing.verbosity = verbosityDetail
    cing.verbosity = verbosityOutput
    cing.verbosity = verbosityDebug
    unittest.main()
