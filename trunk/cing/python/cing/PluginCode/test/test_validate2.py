"""
Unit test
python $cingPath/PluginCode/test/test_validate2.py
"""
from cing.Libs.NTutils import SetupError
from cing.core.classes import Project
from unittest import TestCase
from cing import cingDirTestsTmp
from cing import cingDirTestsData
import os
import unittest
from shutil import copytree

class AllChecks(TestCase):

    def testrun(self):
        """validate2 run check"""
#        SETUP FIRST
        if os.chdir(cingDirTestsTmp):
            raise SetupError("Failed to change to directory for temporary test files: "+cingDirTestsTmp)

        cingProjectEntry = "1brvV1" # cing project created from a ccpn project via CCPN API branch 4
        cingProjectFolder = cingProjectEntry+".cing"
        cingProjectFilePath = os.path.join( cingDirTestsData, cingProjectFolder)

        if os.chdir(cingDirTestsTmp):
            raise SetupError("Failed to change to directory for temporary test files: "+cingDirTestsTmp)
        copytree(cingProjectFilePath, cingProjectFolder)
        project = Project.open( cingProjectEntry, status='old' )
        print project.cingPaths.format()
        project.validate()

if __name__ == "__main__":
    unittest.main()
