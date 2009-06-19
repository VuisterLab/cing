from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityError
from cing.Libs.disk import tail
from unittest import TestCase
import cing
import os
import unittest

class AllChecks(TestCase):
    # important to switch to temp space before starting to generate files for the project.
    os.chdir(cingDirTmp)

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
        self.assertEquals( "['Line 9']", `lastLineList` ) # not necessary a test.

if __name__ == "__main__":
    cing.verbosity = verbosityError
    cing.verbosity = verbosityDebug
    unittest.main()
