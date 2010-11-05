"""
Unit test execute as:
python -u $CINGROOT/python/cing/Libs/test/test_NTgenUtils.py
"""

from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTgenUtils import analyzeCingLog
from cing.Libs.NTutils import * #@UnusedWildImport
from unittest import TestCase
import unittest

class AllChecks(TestCase):
    os.chdir(cingDirTmp)

    def testAnalyzeCingLog(self):
        logFile = os.path.join(cingDirTestsData, 'log_validateEntry_1brv.log')
        _timeTaken, entryCrashed, nr_error, nr_warning, nr_message, nr_debug = analyzeCingLog(logFile)
        NTdebug("Found %d/%d/%d/%d error,warning,message, and debug lines." % (nr_error, nr_warning, nr_message, nr_debug) )
        self.assertFalse(entryCrashed) # The traceback is shown but was caught internally in CING and so it doesn't qualify as a true crash.
        self.assertEqual(nr_error, 2)
        self.assertEqual(nr_warning, 0)
        self.assertEqual(nr_message, 99)
        self.assertEqual(nr_debug, 20)

if __name__ == "__main__":
    cing.verbosity = cing.verbosityDebug
    unittest.main()
