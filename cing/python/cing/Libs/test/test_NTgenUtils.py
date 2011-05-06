"""
Unit test execute as:
python -u $CINGROOT/python/cing/Libs/test/test_NTgenUtils.py
"""

from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTgenUtils import * #@UnusedWildImport
from cing.Libs.NTutils import * #@UnusedWildImport
from unittest import TestCase
import unittest

class AllChecks(TestCase):
    cingDirTmpTest = os.path.join( cingDirTmp, 'test_NTgenUtils' )
    mkdirs( cingDirTmpTest )
    os.chdir(cingDirTmpTest)

    def testAnalyzeCingLog(self):
        # used txt instead of the normal log because .log files are excluded by svn by default.
        logFile = os.path.join(cingDirTestsData, 'cing', 'log_validateEntry_1brv.txt')
        timeTaken, entryCrashed, nr_error, nr_warning, nr_message, nr_debug = analyzeCingLog(logFile)
        NTdebug("Found %s/%s timeTaken/entryCrashed and %d/%d/%d/%d error,warning,message, and debug lines." % (timeTaken, entryCrashed, nr_error, nr_warning, nr_message, nr_debug) )
        self.assertFalse(entryCrashed) # The traceback is shown but was caught internally in CING and so it doesn't qualify as a true crash.
        self.assertEqual(nr_error, 2)
        self.assertEqual(nr_warning, 0)
        self.assertEqual(nr_message, 99)
        self.assertEqual(nr_debug, 20)

    def testAnalyzeXplorLog(self):
        # used txt instead of the normal log because .log files are excluded by svn by default.
        logPath = os.path.join(cingDirTestsData, 'xplor')
        fnList      = "test_xplor_crashed.log test_xplor_errors.log test_xplor_normal.log".split()
#        fnList      = "test_xplor_crashed.log test_xplor_errors.log".split()
        timeTakenList   = [ None, 0.2796, 3.3409 ]
        crashList       = [ True, None, None ]
        errorList       = [ 1840,   60, 0 ]
        warningList       = [ 0,   0, 0 ]
        messageList     = [  237,  159, 1166 ]
        totalList       = [ 2077,  219, 1166 ]
        for i,fn in enumerate(fnList):
            logFile = os.path.join( logPath, fn )
            NTdebug("analyzing log: %s" % logFile)
            timeTaken, entryCrashed, nr_error, nr_warning, nr_message, nr_debug = analyzeXplorLog(logFile)
            nr_total = nr_error + nr_warning + nr_message + nr_debug
            self.assertEqual( timeTaken, timeTakenList[i])
            self.assertEqual( entryCrashed, crashList[i])
            self.assertEqual( nr_error, errorList[i])
            self.assertEqual( nr_warning, warningList[i])
            self.assertEqual( nr_message, messageList[i])
            self.assertEqual( nr_total, totalList[i])
        # end for
    # end def


if __name__ == "__main__":
    cing.verbosity = cing.verbosityDebug
    unittest.main()
