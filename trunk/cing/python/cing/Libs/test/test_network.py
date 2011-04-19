from cing import cingDirTestsData
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.network import sendFileByScp
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def _test_sendFileByScp(self):
        entryId = '1brv'
        fileName = os.path.join(cingDirTestsData, "ccpn", entryId + ".tgz")
#        fileName = '/home/i/workspace/whatif/bindata/ALCONT.ACT'
#        fileName = '/Users/jd/workspace35/whatif/bindata/ALCONT.ACT'
        targetUrl = 'jd@dodos.dyndns.org:/Users/jd/tmp/x/y/z/a/b'
        NTdebug("Trying targetUrl: %s" % targetUrl)
        self.assertFalse( sendFileByScp( fileName, targetUrl ))

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
