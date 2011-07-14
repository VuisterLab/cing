"""
Unit test execute as:
python -u $CINGROOT/python/cing/PluginCode/test/test_eNMR.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.Ccpn import Ccpn #@UnusedImport needed to throw a ImportWarning so that the test is handled properly.
from cing.core.classes import Project
from unittest import TestCase
import shutil
import unittest

class AllChecks(TestCase):

    # can only be done with eNMRworkshop data so disabled for now.
    def _testEnmr(self):
        entryList = "ET109AredOrg".split()
#        entryList = """
#        apoTTHAtransOrg mia40Frankfurt mia40Lyon mia40Org
#        mia40Piscataway taf3Lyon taf3Org taf3Piscataway wln34Frankfurt wln34Lyon wln34Org wln34Paris wln34Piscataway""".split()
#        entryList = """AR3436Lyon AR3436Org AR3436Piscataway AR3436Utrecht BASPLyon BASPOrg CuTTHAcisFrankfurt
#        CuTTHAcisLyon CuTTHAcisOrg CuTTHAcisPiscataway CuTTHAtransFrankfurt CuTTHAtransLyon CuTTHAtransOrg
#        CuTTHAtransPiscataway ParvulustatFrankfurt ParvulustatLyon ParvulustatOrg ParvulustatParis
#        ParvulustatPiscataway TTScoFrankfurt TTScoLyon TTScoOrg TTScoParis TTScoPiscataway VpR247Lyon
#        VpR247Org VpR247Paris VpR247Piscataway apoTTHAcisFrankfurt apoTTHAcisLyon apoTTHAcisOrg
#        apoTTHAtransFrankfurt apoTTHAtransLyon apoTTHAtransOrg mia40Frankfurt mia40Lyon mia40Org
#        mia40Piscataway taf3Lyon taf3Org taf3Piscataway wln34Frankfurt wln34Lyon wln34Org wln34Paris wln34Piscataway
#""".split()

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
        cingDirTmpTest = os.path.join( cingDirTmp, getCallerName() )
        mkdirs( cingDirTmpTest )
        self.failIf(os.chdir(cingDirTmpTest), msg =
            "Failed to change to test directory for files: " + cingDirTmpTest)


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
                                              doWattos = doWattos ))
            # Do not leave the old CCPN directory laying around since it might get added to by another test.
            if os.path.exists(entryId):
                self.assertFalse(shutil.rmtree(entryId))

if __name__ == "__main__":
    cing.verbosity = verbosityDetail
    cing.verbosity = verbosityOutput
    cing.verbosity = verbosityDebug
    unittest.main()
