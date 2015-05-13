"""
Unit test execute as:
python $CINGROOT/python/cing/NRG/test/test_Utils.py
"""
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG import ARCHIVE_NRG_ID
from cing.NRG.Utils import getArchiveIdFromDirectoryName
from unittest import TestCase
import unittest
from cing.NRG import ARCHIVE_NMR_REDO_ID

class AllChecks(TestCase):

    def test_NrgUtils(self): #DEFAULT disabled because it's a specific test for services not commonly used.
        inputList = """
            .            
            http://dodos.dyndns.org/NRG-CING/input/pc
            /var/NMR_REDO/x
        """.split()
        expectedList = [ 
            None,
            ARCHIVE_NRG_ID,
            ARCHIVE_NMR_REDO_ID            
        ] 
        for i, inputStr in enumerate(inputList):
            archive_id = getArchiveIdFromDirectoryName(inputStr)
#            nTdebug("Found on iteration %s with input: %s the archive_id %s and expected %s" % ( i, inputStr, archive_id, expectedList[i]))
            self.assertEqual( archive_id, expectedList[i])
        # end for
    # end def
# end class


if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()

