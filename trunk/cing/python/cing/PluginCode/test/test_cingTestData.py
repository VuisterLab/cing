"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_cingTestData.py

This routine will test the backwards compatibility, that is:
reading cing projects that have been created with the CING api before the current one.
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.required.reqCcpn import CCPN_STR
from cing.core.classes import Project
from nose.plugins.skip import SkipTest
from unittest import TestCase
import shutil
import unittest

# Import using optional plugins.
try:
    from cing.PluginCode.Ccpn import Ccpn #@UnusedImport needed to throw a ImportWarning so that the test is handled properly.
except ImportWarning, extraInfo: # Disable after done debugging; can't use nTdebug yet.
    print "Got ImportWarning %-10s Skipping unit check %s." % ( CCPN_STR, getCallerFileName() )
    raise SkipTest(CCPN_STR)
# end try

class AllChecks(TestCase):

    def _test_cingTestData(self): # Disabled all together because JFD can't figure out why it works on all but the master node.
        # and even there it works fine when testing manually with right setup and:
        # nosetests /Users/jd/.jenkins/jobs/CING/workspace/Slaves/master/python/cing/PluginCode/test/test_cingTestData.py
        entryList = "1brv_023 1brv_024 1brv_025".split() # 0.24 version project with CS from NRG-CING.
#        entryList = "1brv_024 1brv_025".split() # 0.23 version skipped because unknown error causes it to fail.
#        entryList = "1brv_025".split()
#        entryList = "H2_2Ca_64_100".split()   # 0.24 version project with CS.
#        entryList = "1i1s 1ka3 1tgq 1y4o".split()
#        if you have a local copy you can use it; make sure to adjust the path setting below.
        validateFastest = True

        htmlOnly = False # default is False but enable it for faster runs without some actual data.
        doWhatif = False # disables whatif actual run
        doProcheck = False
        doWattos = False
        useNrgArchive = False

        cingDirTmpTest = os.path.join( cingDirTmp, getCallerName() )
        mkdirs( cingDirTmpTest )
        self.failIf(os.chdir(cingDirTmpTest), msg =
            "Failed to change to test directory for files: " + cingDirTmpTest)

        for entryId in entryList:
            nTmessage('Doing %s' % entryId)
            if useNrgArchive: # default is False
#                inputArchiveDir = os.path.join('/Library/WebServer/Documents/NRG-CING/recoordSync', entryId)
                # Mounted from nmr.cmbi.ru.nl
#                inputArchiveDir = os.path.join('/Library/WebServer/Documents/NRG-CING/recoordSync', entryId)
                inputArchiveDir = os.path.join('/Users/jd/ccpn_tmp/data/recoord', entryId)
            else:
                inputArchiveDir = os.path.join(cingDirTestsData, "cing")

            cingFile = os.path.join(inputArchiveDir, entryId + ".cing.tgz")
            self.assertTrue( os.path.exists(cingFile), "Failed to find file: " + cingFile)

            cingDirNew = os.path.join(cingDirTmp, entryId + ".cing")
            if os.path.exists(cingDirNew):
                nTmessage("Removing old cing project directory: " + cingDirNew )
                shutil.rmtree( cingDirNew )

            shutil.copy(cingFile, cingDirTmpTest)
            project = Project.open(entryId, status = 'old')
            self.assertTrue(project, 'Failed opening project: ' + entryId)

            if 1:
                self.assertFalse(project.validate(htmlOnly = htmlOnly,
                                                  doProcheck = doProcheck,
                                                  doWhatif = doWhatif,
                                                  doWattos=doWattos,
                                                  validateFastest=validateFastest ))
            self.assertTrue(project.save())
            # Do not leave the old CCPN directory laying around since it might get added to by another test.
            if os.path.exists(entryId):
                self.assertFalse(shutil.rmtree(entryId))


if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
