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

    # can only be done with eNMRworkshop data so disabled for now.
    def tttestEnmr(self):
        entryList = "AR3436AOrg BASPOrg CuTTHAcisOrg CuTTHAtransOrg ParvulustatOrg TTScoOrg TTScoParis VpR247Org "+\
                    "VpR247Paris VpR247Piscataway Wln34Paris apoTTHAcisOrg apoTTHAtransOrg mia40Org taf3Org wln34Org wln34Piscataway"
        entryList = entryList.split()
#        entryList = "taf3".split()
#        entryList = "mia40".split()

#        entryList = "VpR247Org".split()
#        entryList = "VpR247Paris".split()

#        if you have a local copy you can use it; make sure to adjust the path setting below.
        fastestTest = True
        
        htmlOnly = False # default is False but enable it for faster runs without some actual data.
        doWhatif = True # disables whatif actual run
        doProcheck = True
        doWattos = True
        modelCount=None
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
            print "Doing "+entryId
            project = Project.open(entryId, status = 'new')
            self.assertTrue(project, 'Failed opening project: ' + entryId)

            inputArchiveDir = os.path.join(cingDirTestsData, "eNMR")

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
