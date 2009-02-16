"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_ccpn.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDetail
from cing import verbosityOutput
from cing.core.classes import Project
from unittest import TestCase
from shutil import move #@UnusedImport
from cing import verbosityDebug
import cing
import os
import unittest

class AllChecks(TestCase):

    def testInitCcpn(self):
        # failing entries: 1ai0, 1kr8 (same for 2hgh)
#        entryList = "1ai0".split()
#        entryList = "1brv".split()
#        entryList = "1a24".split()
#        entryList = "1kr8".split()
        entryList = "1brv".split()
#        entryList = "1ai0".split()
#        entryList = "2k0e_all".split()
#        entryList = "1a4d 1a24 1afp 1ai0 1brv 1bus 1cjg 1hue 1ieh 1iv6 1kr8 2hgh 2k0e SRYBDNA Parvulustat".split()
#        entryList =            "1afp 1ai0 1brv 1bus 1cjg 1hue 1ieh 1iv6 1kr8 2hgh 2k0e SRYBDNA Parvulustat".split()
#1iv6 needs better ccpn file from FC
#        entryList = ["Parvulustat"]
#        entryList = ["1a4d"]

#        if you have a local copy you can use it; make sure to adjust the path setting below.
        useNrgArchive = False # Default is False
        
        fastestTest = True
        htmlOnly = False # default is False but enable it for faster runs without some actual data.
        doWhatif = False # disables whatif actual run
        doProcheck = False
        if fastestTest:
            htmlOnly = True 
            doWhatif = False
            doProcheck = False

        self.failIf( os.chdir(cingDirTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTmp)
        for entryId in entryList:
            project = Project.open( entryId, status='new' )
            self.assertTrue(project, 'Failed opening project: ' + entryId)

            if useNrgArchive: # default is True
                inputArchiveDir = os.path.join(cingDirTestsData,"ccpn")
            else:
                inputArchiveDir = os.path.join('/Library/WebServer/Documents/NRG-CING/recoordSync', entryId)

            ccpnFile = os.path.join(inputArchiveDir, entryId+".tgz")
            self.assertTrue(project.initCcpn(ccpnFolder=ccpnFile))
            self.assertTrue(project.save())
            self.assertFalse(project.validate(htmlOnly=htmlOnly,
                                              doProcheck = doProcheck,
                                              doWhatif=doWhatif ))
#            self.assertTrue(project.exportValidation2ccpn())
#            self.assertFalse(project.removeCcpnReferences()) 

if __name__ == "__main__":
    cing.verbosity = verbosityDetail
    cing.verbosity = verbosityOutput
    cing.verbosity = verbosityDebug
    unittest.main()
