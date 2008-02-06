from cing import cingDirTestsData
from cing import cingDirTestsTmp
from cing.Libs.NTutils import SetupError
from cing.Libs.NTutils import printError
from cing.Libs.NTutils import printMessage
from cing.core.classes import Project
from shutil import copytree
from shutil import rmtree
from unittest import TestCase
from cing.Libs.NTutils import findFiles
import os
import unittest

class AllChecks(TestCase):
    def testrun(self): # Can be disabled by extra t's at the beginning of the function name so unittest
        # doesn't pick it up anymore.
        """validate run check taking too long at 100 s. TODO: reduce size of project."""
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
        # Remove the CVS subdirs as even the temp path is under CVS scrutiny and we don't want to upset it.
        cvsFolders = findFiles("CVS", cingProjectFolder)
        if cvsFolders:
            printMessage("Removing the CVS folders") 
            for name in cvsFolders:
                rmtree(name, True)
#        sys.exit(1)
        project = Project.open( cingProjectEntry, status='old' )
        print project.cingPaths.format()

if __name__ == "__main__":
    unittest.main()
