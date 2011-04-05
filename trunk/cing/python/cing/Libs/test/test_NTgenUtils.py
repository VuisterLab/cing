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
    cingDirTmpTest = os.path.join( cingDirTmp, 'test_NTgenUtils' )
    mkdirs( cingDirTmpTest )
    os.chdir(cingDirTmpTest)

    def testAnalyzeCingLog(self):
        # used txt instead of the normal log because .log files are excluded by svn by default.
        logFile = os.path.join(cingDirTestsData, 'log_validateEntry_1brv.txt')
        timeTaken, entryCrashed, nr_error, nr_warning, nr_message, nr_debug = analyzeCingLog(logFile)
        NTdebug("Found %s/%s timeTaken/entryCrashed and %d/%d/%d/%d error,warning,message, and debug lines." % (timeTaken, entryCrashed, nr_error, nr_warning, nr_message, nr_debug) )
        self.assertFalse(entryCrashed) # The traceback is shown but was caught internally in CING and so it doesn't qualify as a true crash.
        self.assertEqual(nr_error, 2)
        self.assertEqual(nr_warning, 0)
        self.assertEqual(nr_message, 99)
        self.assertEqual(nr_debug, 20)

if __name__ == "__main__":
    cing.verbosity = cing.verbosityDebug
    unittest.main()
