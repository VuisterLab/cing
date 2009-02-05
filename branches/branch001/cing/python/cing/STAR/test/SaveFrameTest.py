"""
Unit test for SaveFrameTest.py
Setup taken from "Dive Into Python"
"""
from cing.STAR.SaveFrame import SaveFrame
from cing.STAR.TagTable import TagTable
from unittest import TestCase
import unittest


class AllChecks(TestCase):
    sf = SaveFrame()
    tT = TagTable()
    tT.tagnames=['_File_characteristics.Sf_category']
    tT.tagvalues=[['file_characteristics']]
    sf.tagtables.append(tT)

    def testcheck_integrity(self):
        self.assertFalse(self.sf.check_integrity())
    
    def testSTARrepresentation(self):
        starText = """\nsave_general_sf_title\n   loop_\n      _File_characteristics.Sf_category\n\nfile_characteristics \n\n   stop_\n\nsave_\n"""
        self.assertEqual(self.sf.star_text(), starText)
        
    def testgetSaveFrameCategory(self):
        sfCategory = "file_characteristics"
        self.assertEqual(self.sf.getSaveFrameCategory(), sfCategory)


if __name__ == "__main__":
    unittest.main()
