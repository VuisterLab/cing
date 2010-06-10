"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_ccpn.py
"""
from cing import cingDirScripts
from cing import cingDirTestsData #@UnusedImport
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList
from cing.Scripts.validateEntry import ARCHIVE_TYPE_BY_CH23
from cing.Scripts.validateEntry import ARCHIVE_TYPE_FLAT #@UnusedImport
from cing.Scripts.validateEntry import PROJECT_TYPE_PDB
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def testRetrieveTgzFromUrl(self):
        self.failIf(os.chdir(cingDirTmp), msg =
            "Failed to change to directory for temporary test files: " + cingDirTmp)
        entryListFileName = "entry_list_todo.csv"
        entry_list_todo = [ 0,1,2,3,4,5,6,7,8,9 ]
        writeTextToFile(entryListFileName, toCsv(entry_list_todo))

        pythonScriptFileName = os.path.join(cingDirScripts, 'doNothing.py')
        extraArgList = ('.', '.', '.', '.', ARCHIVE_TYPE_BY_CH23, PROJECT_TYPE_PDB)

        self.assertFalse(
            doScriptOnEntryList(pythonScriptFileName,
                            entryListFileName,
                            '.',
                            processes_max = 8,
                            delay_between_submitting_jobs = 5,
                            max_time_to_wait = 2,
                            START_ENTRY_ID = 0,
                            MAX_ENTRIES_TODO = 1,
                            extraArgList = extraArgList,
                            shuffleBeforeSelecting = True ))

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
