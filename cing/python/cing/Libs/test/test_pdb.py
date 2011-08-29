"""
Unit test execute as:
python $CINGROOT/python/cing/Libs/test/test_pdb.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Scripts.utils import printSequenceFromPdbFile
from cing.core.classes import Project
from cing.core.constants import * #@UnusedWildImport
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def test_pdb(self):

        cingDirTmpTest = os.path.join( cingDirTmp, getCallerName() )
        mkdirs( cingDirTmpTest )
        self.failIf(os.chdir(cingDirTmpTest), msg =
            "Failed to change to test directory for files: " + cingDirTmpTest)

        entryId = "1brv" # Small much studied PDB NMR entry
#        entryId = "tightTurn_IIb"
#        entryId = "1hy8" # small, single model, very low scoring entry

        pdbDirectory = os.path.join(cingDirTestsData,"pdb", entryId)
        pdbFileName = "pdb"+entryId+".ent"
        pdbFilePath = os.path.join( pdbDirectory, pdbFileName)

        # does it matter to import it just now?
        project = Project( entryId )
        self.failIf( project.removeFromDisk())
        project = Project.open( entryId, status='new' )
        project.initPDB( pdbFile=pdbFilePath, convention = IUPAC )

        m = project.molecule
        ranges = 'A.173-178'
        nTdebug("m: %s" % m)
        self.assertTrue( m.toPDB('m001.pdb', model=0, ranges=ranges, convention='XPLOR'))
#        nTdebug("Manual reimport")
#        m.initCoordinates()
#        m.importFromPDB('m001.pdb',convention='XPLOR')
        nTdebug("Reimport 1")
        m.replaceCoordinatesByPdb(pdbFilePath, name = entryId+'_reimport', convention=IUPAC)
#        nTdebug("Reimport 2")
#        m.replaceCoordinatesByPdb(pdbFilePath, name = entryId+'_reimport', useModels = "1", convention=IUPAC)

        self.assertFalse(project.mkMacros())
#       self.assertFalse(project.validate(htmlOnly=False, doWhatif = False, doProcheck = False))

    def _testPrintSequenceFromPdbFile(self):
        entryId = "1brv" # Small much studied PDB NMR entry
#        entryId = "1hy8" # small, single model, very low scoring entry

        pdbDirectory = os.path.join(cingDirTestsData,"pdb", entryId)
        pdbFileName = "pdb"+entryId+".ent"
        fn = os.path.join( pdbDirectory, pdbFileName)

        self.failIf( os.chdir(cingDirTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTmp)
        self.assertFalse(printSequenceFromPdbFile(fn))


if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
