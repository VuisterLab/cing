from cing import cingDirTmp
from cing import verbosityDebug
from cing.cgi.FileUpload import bytesToFormattedString
from unittest import TestCase
import cing
import os 
import unittest

class AllChecks(TestCase):

    os.chdir(cingDirTmp)

    def testBytesToFormattedString(self):
        byteList = [ 1, 1000, 1300, 1600, 13000*1024, 130*1000*1024*1024  ]
        expectedResults= [ '0K', '1K', '1K', '2K', '13M', '127G' ]
        for i in range(len(byteList)):
            r = bytesToFormattedString(byteList[i])
            self.assertEqual( r, expectedResults[i] )
        
if __name__ == "__main__":
#    cing.verbosity = verbosityNothing
    cing.verbosity = verbosityDebug
    unittest.main()
