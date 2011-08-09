from cing import cingDirTmp
from cing import cingRoot
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.disk import globLast
from cing.Libs.disk import tail
from unittest import TestCase
import unittest


class AllChecks(TestCase):
    # important to switch to temp space before starting to generate files for the project.
    cingDirTmpTest = os.path.join( cingDirTmp, 'test_disk' )
    mkdirs( cingDirTmpTest )
    os.chdir(cingDirTmpTest)

    def testDisk(self):
        DONE = "DONE"
        f = open(DONE,"w")
        for i in range(10):
            f.write("Line %d\n" % i)
        f.close()
        f2 = open(DONE,"r")
        lastLineList = tail(f2,1)
        lastLine = lastLineList[0]
        self.assertEquals( "Line 9", lastLine )
        self.assertEquals( "['Line 9']", repr(lastLineList) ) # not necessary a test.

    def testGlobLast(self):
        globPattern = os.path.join(cingRoot, '*.txt')
        lastFile = globLast(globPattern)
        nTdebug('lastFile: %s' % lastFile)
        d, _basename, extension = nTpath(lastFile)
        self.assertTrue(lastFile)
        self.assertEquals(d, cingRoot)
        self.assertEquals(extension, '.txt')

        globPattern = os.path.join(cingRoot, '*.xyz')
        lastFile = globLast(globPattern)
        nTdebug('lastFile 2: %s' % lastFile)
        self.assertFalse(lastFile)

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
