"""
Unit test execute as:
python $CINGROOT/python/cing/NRG/test/test_WhyNot.py
"""
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG.WhyNot import FAILED_TO_BE_VALIDATED_CING
from cing.NRG.WhyNot import NOT_NMR_ENTRY
from cing.NRG.WhyNot import WhyNot
from cing.NRG.WhyNot import WhyNotEntry
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def test_WhyNot(self):
        cingDirTmpTest = os.path.join( cingDirTmp, getCallerName() )
        mkdirs( cingDirTmpTest )
        self.failIf(os.chdir(cingDirTmpTest), msg =
            "Failed to change to test directory for files: " + cingDirTmpTest)
        whyNot = WhyNot()
        for entryId in ['1brv', '9pcy']:
            whyNotEntry = WhyNotEntry(entryId)
            whyNot[entryId] = whyNotEntry
            if entryId not in ['1brv']:
                whyNotEntry.comment = NOT_NMR_ENTRY
                whyNotEntry.exists = False
                continue
            whyNotEntry.comment = FAILED_TO_BE_VALIDATED_CING
        whyNotStr = '%s' % whyNot
        nTdebug("whyNotStr: ["+ whyNotStr +"]")
        writeTextToFile("NRG-CING.txt", whyNotStr)    
    # end def
# end class

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
# end def