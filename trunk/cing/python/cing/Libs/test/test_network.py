"""
Unit test execute as:
python -u $CINGROOT/python/cing/Libs/test/test_network.py
"""

from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.network import * #@UnusedWildImport
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    cingDirTmpTest = os.path.join( cingDirTmp, 'test_network' )
    mkdirs( cingDirTmpTest )
    os.chdir(cingDirTmpTest)

    def _test_putFileBySsh(self):
        fileName = os.path.join(cingDirTestsData, "ccpn", '1brv' + ".tgz") #@UnusedVariable
#        fileName = '%s/bindata/ALCONT.ACT'
#        fileName = '/Users/jd/workspace35/whatif/bindata/ALCONT.ACT'
#        targetUrl = 'jd@dodos.dyndns.org:/Users/jd/tmp/x/y/z/a/b'
#        targetUrl = 'jurgenfd@gb-ui-kun.els.sara.nl:/home/jurgenfd/tmp'
        targetUrl = 'i@nmr.cmbi.ru.nl:/mnt/data/D/NMR_REDO/data/br/1brv'
        self.assertFalse( putFileBySsh( fileName, targetUrl, ntriesMax = 2 ))

    def _test_getFileBySsh(self):
        fn = 't'
        sourceUrl = 'ssh://jurgenfd@gb-ui-kun.els.sara.nl:/home/jurgenfd/' + fn
#        targetUrl = '/Users/jd'
        self.assertFalse( getFileBySsh( sourceUrl, '.', ntriesMax = 2 ))
    # end def
# end class

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
