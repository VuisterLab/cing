"""
Unit test execute as:
python $CINGROOT/python/cing/NRG/test/test_NrgCingRdb.py
"""
from cing import cingDirTmp
from cing.Libs.DBMS import DBMS
from cing.Libs.DBMS import Relation
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG import NMR_REDO_DB_SCHEMA
from cing.NRG import NRG_DB_NAME
from cing.NRG import RECOORD_DB_SCHEMA
from cing.NRG.nrgCingRdb import NrgCingRdb
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def _test_NrgCingRdb(self):
        cingDirTmpTest = os.path.join( cingDirTmp, getCallerName() )
        mkdirs( cingDirTmpTest )
        self.failIf(os.chdir(cingDirTmpTest), msg =
            "Failed to change to test directory for files: " + cingDirTmpTest)
        host = 'localhost'
        if 1: # DEFAULT False
            host = 'nmr.cmbi.umcn.nl'
        schema=RECOORD_DB_SCHEMA #@UnusedVariable
        schema=NRG_DB_NAME
        m = NrgCingRdb(host=host,schema=schema)

#        self.assertFalse( m.showCounts())
#        self.assertFalse( m.createScatterPlots())
        self.assertFalse( m.createPlotsCompareBetweenDb(other_schema=NMR_REDO_DB_SCHEMA))
        
        if False:
            a = m.getPdbIdList()
            nTdebug("pdbIdList length: %d %s" % (len(a), a))
            self.assertTrue(a)
            if 0 and a: # DEFAULT 0 watch out!
                lToRemove = \
                    '1sae 1sah 1saj 1sak 1sal 1y0j 2k0a 2kiu 2ku2 2kx7 2ky5 2l0l 2l0m 2l0n 2l0o 2l2f 2l2x 2l3r 2l8m 2rqf 3sak'.split()
                for entry_code in lToRemove:
                    self.assertFalse( m.removeEntry(entry_code))
    #            entry_code = a[0]
    #            self.assertFalse( m.removeEntry(entry_code))
            # end if
        # end if
    # end def

    def _test_writeCsvNRG(self):
        cingDirTmpTest = os.path.join( cingDirTmp, getCallerName() )
        mkdirs( cingDirTmpTest )
        self.failIf(os.chdir(cingDirTmpTest), msg =
            "Failed to change to test directory for files: " + cingDirTmpTest)
        myLoL = [ [0,1,2], [3,4,5] ]
        dbms = DBMS()
        r = Relation('mTable', dbms, columnList=['x', 'y'])
        r.fromLol(myLoL)
        r.writeCsvFile('myLoL')
    # end def
        
    
if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()