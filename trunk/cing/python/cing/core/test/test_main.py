from cing import verbosityDebug
from unittest import TestCase
import cing
import unittest

class AllChecks(TestCase):

    pass
#    def testFormatAll(self):
#        entryIdList = ['foo',456]
#        entryIdListStr = formatall(entryIdList)
#        self.assertEqual(entryIdListStr, "foo\n456\n")
#        entryIdTuple = ('test',123)
##        formatall(entryIdTuple) throws a TypeError
#        self.assertRaises( TypeError, formatall, entryIdTuple)

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
