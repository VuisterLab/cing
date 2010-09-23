"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_xplor_nih.py

For testing execution of cing inside of Xplor-NIH python interpreter with the data living outside of it.
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.classes import Project
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def testTalosPlus(self):
        self.failIf( os.chdir(cingDirTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTmp)

        entryId = "gb1"
        pdbDirectory = os.path.join(cingDirTestsData,"xplor", entryId)
        pdbFileName = entryId+".pdb"
        pdbFilePath = os.path.join( pdbDirectory, pdbFileName)

        self.failIf( os.chdir(cingDirTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTmp)

        project = Project( entryId )
        self.failIf( project.removeFromDisk())
        project = Project.open( entryId, status='new' )
        project.initPDB( pdbFile=pdbFilePath, convention = XPLOR )
#        project.validate(ranges, parseOnly, htmlOnly, doProcheck, doWhatif, doWattos, doTalos)
        project.validate(htmlOnly=True, doProcheck=False, doWhatif=False, doWattos=False, doTalos=False)
        project.save()



if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
