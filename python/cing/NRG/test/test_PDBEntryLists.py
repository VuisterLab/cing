"""
Unit test execute as:
python $CINGROOT/python/cing/NRG/test/test_PDBEntryLists.py
"""

from cing import cingDirTestsData #@UnusedImport
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.helper import isInternetConnected
from cing.NRG.PDBEntryLists import * #@UnusedWildImport
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def _test_PDBEntryLists(self):

        if not cing.internetConnected:
            nTdebug("Skipping checks for there is no internet connection detected")
            return

        cingDirTmpTest = os.path.join( cingDirTmp, getCallerName() )
        mkdirs( cingDirTmpTest )
        self.failIf(os.chdir(cingDirTmpTest), msg =
            "Failed to change to test directory for files: " + cingDirTmpTest)

        if False:
            status = isInternetConnected()
            nTdebug("isInternetConnected: %s" % status)
            self.assertTrue(status)

        if False:
            a = getBmrbNmrGridEntriesDOCRDone()
            nTdebug("getBmrbNmrGridEntriesDOCRDone NMR: %d %s" % (len(a), a))
            self.assertTrue(a)
        if False:
            a = getBmrbNmrGridEntries()
            nTdebug("getBmrbNmrGridEntries NMR            : %d %s" % (len(a), a))
            self.assertTrue(a)
            self.assertTrue(len(a) > 5000) # Fails if NRG is down or corrupted.

        if False:
            # fast check because there are only a few.
            nmrSolidExpList = getPdbEntries(onlySolidState = True)
            self.assertTrue(nmrSolidExpList)
            self.assertTrue(len(nmrSolidExpList) >= 35)  # November 10, 2009
            nTdebug("getPdbEntries NMR solid: %d" % (len(nmrSolidExpList)))

        if False:
            nmrExpList = getPdbEntries(onlyNmr = True, mustHaveExperimentalNmrData = True)
            self.assertTrue(nmrExpList)
            self.assertTrue(len(nmrExpList) >= 5385)  # November 10, 2009
            nTdebug("getPdbEntries NMR exp: %d" % (len(nmrExpList)))

        if 0:
            nmrList = getPdbEntries(onlyNmr = True)
            self.assertTrue(nmrList)
            nTdebug("getPdbEntries NMR: %d" % (len(nmrList)))
            nTdebug("getPdbEntries NMR: %s" % str(nmrList))
            for entry_code in nmrList:
                if len(entry_code) != 4:
                    nTerror("No entry code: %s" % str(entry_code))
            self.assertTrue(len(nmrList) >= 8800)
            # end for

        if False:
            pdbList = getPdbEntries(onlyNmr = False)
            self.assertTrue(pdbList)
            self.assertTrue(len(pdbList) >= 61248)
            nTdebug("getPdbEntries ALL: %d" % (len(pdbList)))

        if False:
            pdbList = getPdbEntries(mustHaveExperimentalNmrData = True)
            self.assertTrue(pdbList)
            self.assertTrue(len(pdbList) >= 1)
            nTdebug("getPdbEntries exp: %d" % (len(pdbList)))
#            nTdebug("%s" % pdbList)

        if True:
            matches_many2one = getBmrbLinks()
            self.assertTrue(matches_many2one)
            inputPdbId = '1brv'
            bmrb_id = matches_many2one[inputPdbId]
#            self.assertEqual(pdb_id,inputPdbId)
            self.assertEqual(bmrb_id, '4020')


if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()

