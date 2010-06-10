"""
Unit test execute as:
python $CINGROOT/python/cing/NRG/test/test_PDBEntryLists.py
"""
from cing import cingDirTestsData #@UnusedImport
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.helper import isInternetConnected
from cing.NRG.PDBEntryLists import getBmrbNmrGridEntries
from cing.NRG.PDBEntryLists import getBmrbNmrGridEntriesDOCRfREDDone
from cing.NRG.PDBEntryLists import getPdbEntries
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def test_PDBEntryLists(self):

        if not cing.internetConnected:
            NTdebug("Skipping checks for there is not internet connection detected")
            return

        self.failIf(os.chdir(cingDirTmp), msg =
            "Failed to change to directory for temporary test files: " + cingDirTmp)

        if False:
            status = isInternetConnected()
            NTdebug("isInternetConnected: %s" % status)
            self.assertTrue(status)

        if False:
            l = getBmrbNmrGridEntriesDOCRfREDDone()
            NTdebug("getBmrbNmrGridEntriesDOCRfREDDone NMR: %d %s" % (len(l), l))
            self.assertTrue(l)
        if False:
            l = getBmrbNmrGridEntries()
            NTdebug("getBmrbNmrGridEntries NMR            : %d %s" % (len(l), l))
            self.assertTrue(l)
            self.assertTrue(len(l) > 5000) # Fails if NRG is down or corrupted.

        if False:
            # fast check because there are only a few.
            nmrSolidExpList = getPdbEntries(onlySolidState = True)
            self.assertTrue(nmrSolidExpList)
            self.assertTrue(len(nmrSolidExpList) >= 35)  # November 10, 2009
            NTdebug("getPdbEntries NMR solid: %d" % (len(nmrSolidExpList)))

        if False:
            nmrExpList = getPdbEntries(onlyNmr = True, mustHaveExperimentalNmrData = True)
            self.assertTrue(nmrExpList)
            self.assertTrue(len(nmrExpList) >= 5385)  # November 10, 2009
            NTdebug("getPdbEntries NMR exp: %d" % (len(nmrExpList)))

        if False:
            nmrList = getPdbEntries(onlyNmr = True)
            self.assertTrue(nmrList)
            self.assertTrue(len(nmrList) >= 8107)
            NTdebug("getPdbEntries NMR: %d" % (len(nmrList)))

        if False:
            pdbList = getPdbEntries(onlyNmr = False)
            self.assertTrue(pdbList)
            self.assertTrue(len(pdbList) >= 61248)
            NTdebug("getPdbEntries ALL: %d" % (len(pdbList)))

        if True:
            pdbList = getPdbEntries(mustHaveExperimentalNmrData = True)
            self.assertTrue(pdbList)
            self.assertTrue(len(pdbList) >= 1)
            NTdebug("getPdbEntries exp: %d" % (len(pdbList)))
#            NTdebug("%s" % pdbList)

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()

