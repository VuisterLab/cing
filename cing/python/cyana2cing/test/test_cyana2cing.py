"""
Unit test execute as:
python $CINGROOT/python/cing/Scripts/test/test_cyana2cing.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.classes import Project
from unittest import TestCase
import shutil
import unittest

class AllChecks(TestCase):

    def test_cyana2cing(self):
#        SETUP FIRST
        projectId = "1pdb"
        cyanaDirectory = os.path.join( cingDirTestsData, "cyana", projectId )
        self.assertTrue( os.path.exists( cyanaDirectory) and os.path.isdir(cyanaDirectory ) )

        cingDirTmpTest = os.path.join( cingDirTmp, getCallerName() )
        mkdirs( cingDirTmpTest )
        self.failIf(os.chdir(cingDirTmpTest), msg =
            "Failed to change to test directory for files: " + cingDirTmpTest)

        projectRootPath = os.path.join( cingDirTmp, projectId )
        projectRoot = Project.rootPath( projectRootPath )[0] # xeasy_project.cing in /tmp
        if os.path.exists( projectRoot ):
            NTwarning('Output directory "%s" already exists. It will now be removed.' % projectRoot )
            self.failIf( shutil.rmtree(projectRoot), "Failed to remove old project directory." )

        project = Project.open(projectRootPath, 'new')
        project.cyana2cing( #project=project,
                            cyanaDirectory=cyanaDirectory,
                            uplFiles  = [projectId],
                            acoFiles  = [projectId,"talos"],
                            pdbFile   = projectId,
                            nmodels   = 2,
                            copy2sources = True
        )

        if not project:
            NTwarning("No project generated. Aborting further execution.")
            sys.exit(0)
        project.save()


if __name__ == "__main__":
    cing.verbosity = verbosityError
    cing.verbosity = verbosityDebug
    unittest.main()
