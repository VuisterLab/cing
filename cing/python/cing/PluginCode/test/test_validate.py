"""
Unit test
python $cingPath/PluginCode/test/test_validate.py
"""
from cing import cingDirTestsData
from cing import cingDirTestsTmp
from cing.Libs.NTutils import SetupError
from cing.Libs.NTutils import printError
from cing.Libs.NTutils import printMessage
from cing.core.classes import Project
from shutil import copytree
from shutil import rmtree
from unittest import TestCase
import os
import unittest

class AllChecks(TestCase):

    def testrun(self):
        """validate run check"""
#        SETUP FIRST
        if os.chdir(cingDirTestsTmp):
            raise SetupError("Failed to change to directory for temporary test files: "+cingDirTestsTmp)

        cingProjectEntry = "1brvV1" # cing project created from a ccpn project via CCPN API branch 4
        cingProjectFolder = cingProjectEntry+".cing"
        cingProjectFilePath = os.path.join( cingDirTestsData, cingProjectFolder)

        if os.chdir(cingDirTestsTmp):
            raise SetupError("Failed to change to directory for temporary test files: "+cingDirTestsTmp)
        if os.path.exists(cingProjectFolder):
            printMessage("Removing existing cing project")
            if rmtree( cingProjectFolder ):
                printError("Failed to remove existing cing project")
                return True
        copytree(cingProjectFilePath, cingProjectFolder)
        project = Project.open( cingProjectEntry, status='old' )
        print project.cingPaths.format()
        project.validate()

if __name__ == "__main__":
    unittest.main()
