"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_pdb.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityNothing
from cing.Libs.NTutils import NTdebug
from cing.core.classes import Project
from cing.core.constants import BMRB
from unittest import TestCase
from cing import verbosityDebug
import cing
import os
import unittest

class AllChecks(TestCase):

    def testRun(self):
        pdbConvention = BMRB
        entryId = "1brv"
#        entryId = "2vb1_simple" # Protein solved by X-ray.

        self.failIf( os.chdir(cingDirTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTmp)

        cyanaDirectory = os.path.join(cingDirTestsData,"cyana", entryId)
        pdbFileName = entryId+".pdb"
        pdbFilePath = os.path.join( cyanaDirectory, pdbFileName)

        self.failIf( os.chdir(cingDirTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTmp)
        # does it matter to import it just now?
        project = Project( entryId )
        self.failIf( project.removeFromDisk())
        project = Project.open( entryId, status='new' )
        project.initPDB( pdbFile=pdbFilePath, convention = pdbConvention )
        ens = project.molecule.superpose()
        NTdebug( 'ens %s' % ens)
        NTdebug( 'ens.averageModel %s' % ens.averageModel)
        self.assertAlmostEquals( 0.79258554728692587, ens.averageModel.rmsd, 3 )
        ens = project.molecule.superpose(backboneOnly=False, includeProtons = True,
                                         iterations=3) # no improvement to do 3 over the default 2 but left in for speed checking.
        NTdebug( 'ens.averageModel %s' % ens.averageModel)
        self.assertAlmostEquals( 1.2723930097942036, ens.averageModel.rmsd, 3 )

if __name__ == "__main__":
    cing.verbosity = verbosityNothing
    cing.verbosity = verbosityDebug
    unittest.main()
