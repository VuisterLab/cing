"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_RetrieveTgzFromUrl.py
"""
from cing import cingDirTestsData #@UnusedImport
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Scripts.validateEntry import ARCHIVE_TYPE_BY_ENTRY
from cing.Scripts.validateEntry import ARCHIVE_TYPE_FLAT #@UnusedImport
from cing.Scripts.validateEntry import retrieveTgzFromUrl
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def _test_RetrieveTgzFromUrl(self):

        cingDirTmpTest = os.path.join( cingDirTmp, getCallerName() )
        mkdirs( cingDirTmpTest )
        self.failIf(os.chdir(cingDirTmpTest), msg =
            "Failed to change to test directory for files: " + cingDirTmpTest)

#        url = 'http://restraintsgrid.bmrb.wisc.edu/servlet_data/NRG_ccpn_tmp'
        url = 'file:///Library/WebServer/Documents/NRG-CING/recoordSync'
#        url = 'file:/%s/ccpn' % (cingDirTestsData)
        entryId = '108d'
#        entryId = '1brv'
        fileNameTgz = entryId + '.tgz'
        if os.path.exists(fileNameTgz):
            os.unlink(fileNameTgz)
#        self.assertFalse(retrieveTgzFromUrl(entryId, url, archiveType = ARCHIVE_TYPE_FLAT))
        self.assertFalse(retrieveTgzFromUrl(entryId, url, archiveType = ARCHIVE_TYPE_BY_ENTRY))

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()