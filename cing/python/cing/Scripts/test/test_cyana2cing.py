"""
Unit test execute as:
python $cingPath/Scripts/test/test_cyana2cing.py
"""
from cing import cingDirTestsData
from cing import cingDirTestsTmp
from cing.Libs.NTutils import printWarning
from cing.core.classes import Project
from unittest import TestCase
import shutil
import os
import sys
import unittest

class AllChecks(TestCase):
        
    def testConversion(self):
        """cyana conversion should take less than 10s"""
        
#        SETUP FIRST
        projectId = "xeasy_project" # Small much studied PDB NMR entry 
        cyanaDirectory = os.path.join( cingDirTestsData, projectId )
        self.assertTrue( os.path.exists( cyanaDirectory) and os.path.isdir(cyanaDirectory ) )
        
        self.failIf( os.chdir(cingDirTestsTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTestsTmp)

        projectRootPath = os.path.join( cingDirTestsTmp, projectId )
        projectRoot = Project.rootPath( projectRootPath ) # xeasy_project.cing in /tmp
        if os.path.exists( projectRoot ):
            printWarning('Output directory "%s" already exists. It will now be removed.' % projectRoot )
            self.failIf( shutil.rmtree(projectRoot), "Failed to remove old project directory." )
            
        project = Project.open(projectRootPath, 'new', verbose=False )
        project.cyana2cing( #project=project,
                            cyanaDirectory=cyanaDirectory, 
                            uplFiles  = ["final"],
                            acoFiles  = ["final","talos"],
                            pdbFile   = "final",
                            nmodels   = 2,
                            copy2sources = True
        )
        
        if not project:
            printWarning("No project generated. Aborting further execution.")
            sys.exit(0)

if __name__ == "__main__":
    unittest.main()
