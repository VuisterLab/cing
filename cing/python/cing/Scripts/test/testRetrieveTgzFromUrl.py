"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_ccpn.py
"""
from cing import cingDirTestsData #@UnusedImport
from cing import cingDirTmp
from cing import verbosityDebug
from cing.Scripts.validateEntry import ARCHIVE_TYPE_BY_ENTRY
from cing.Scripts.validateEntry import ARCHIVE_TYPE_FLAT #@UnusedImport
from cing.Scripts.validateEntry import retrieveTgzFromUrl
from unittest import TestCase
import cing
import os
import unittest

class AllChecks(TestCase):

    def testRetrieveTgzFromUrl(self):
        self.failIf(os.chdir(cingDirTmp), msg = 
            "Failed to change to directory for temporary test files: " + cingDirTmp)
#        url = 'http://restraintsgrid.bmrb.wisc.edu/servlet_data/NRG_ccpn_tmp'
        url = 'file://Library/WebServer/Documents/NRG-CING/recoordSync'
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
