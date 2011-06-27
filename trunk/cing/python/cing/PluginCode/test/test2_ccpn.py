"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test2_ccpn.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.classes import Project
from shutil import move #@UnusedImport
from unittest import TestCase
import shutil
import unittest

class AllChecks(TestCase):

    def _test_2ccpn(self):
        # failing entries: 1ai0, 1kr8 (same for 2hgh)
        entryList = "1iv6".split()
#        entryList = "1brv".split()
#        entryList = "1a4d".split()
#        entryList = "2k0e_all".split()
#        entryList = "1a4d 1a24 1afp 1ai0 1brv 1bus 1cjg 1hue 1ieh 1iv6 1kr8 2hgh 2k0e".split()
#        entryList =            "1afp 1ai0 1brv 1bus 1cjg 1hue 1ieh 1iv6 1kr8 2hgh 2k0e SRYBDNA Parvulustat".split()
#1iv6 needs better ccpn file from FC
#        entryList = ["Parvulustat"]
#        entryList = ["1a4d"]

        fastestTest = True
        htmlOnly = True # default is False but enable it for faster runs without some actual data.
        doWhatif = True # disables whatif actual run
        doProcheck = True
        doWattos = True
        if fastestTest:
            htmlOnly = True
            doWhatif = False
            doProcheck = False
            doWattos = False

        cingDirTmpTest = os.path.join( cingDirTmp, getCallerName() )
        mkdirs( cingDirTmpTest )
        self.failIf(os.chdir(cingDirTmpTest), msg =
            "Failed to change to test directory for files: " + cingDirTmpTest)

        for entryId in entryList:
            project = Project.open( entryId, status='new' )
            self.assertTrue(project, 'Failed opening project: ' + entryId)

            ccpnFile = os.path.join(cingDirTestsData,"ccpn", entryId+".tgz")
            self.assertTrue(project.initCcpn(ccpnFolder=ccpnFile))
            self.assertTrue(project.save())
            self.assertFalse(project.validate(htmlOnly=htmlOnly,
                                              doProcheck = doProcheck,
                                              doWhatif=doWhatif,
                                              doWattos=doWattos,
                                               ))
#            self.assertFalse(project.removeCcpnReferences())
            # Do not leave the old CCPN directory laying around since it might get added to by another test.
            if os.path.exists(entryId):
                self.assertFalse(shutil.rmtree(entryId))

if __name__ == "__main__":
    cing.verbosity = verbosityDetail
    cing.verbosity = verbosityOutput
    cing.verbosity = verbosityDebug
    unittest.main()
