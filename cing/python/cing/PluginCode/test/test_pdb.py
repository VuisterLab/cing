"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_pdb.py
"""
from cing import cingDirTestsData
from cing import cingDirTestsTmp
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
        entryId = "1brv_1model"
#        entryId = "2vb1_simple" # Protein solved by X-ray.

        self.failIf( os.chdir(cingDirTestsTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTestsTmp)

        cyanaDirectory = os.path.join(cingDirTestsData,"cyana", entryId)
        pdbFileName = entryId+".pdb"
        pdbFilePath = os.path.join( cyanaDirectory, pdbFileName)

        self.failIf( os.chdir(cingDirTestsTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTestsTmp)
        # does it matter to import it just now?
        project = Project( entryId )
        self.failIf( project.removeFromDisk())
        project = Project.open( entryId, status='new' )
        project.initPDB( pdbFile=pdbFilePath, convention = pdbConvention )

        for chain in project.molecule.allChains():
            if chain.name != 'A':
                NTdebug('Skipping chain in: entry %s for chain code: %s' % (entryId,chain.name) )
                continue

            for res in chain.allResidues():
                NTdebug('Doing entry %s for chain code %s residue %s' % (entryId,chain.name,res))

                self.failUnless( res.has_key('PHI') and res.has_key('PSI'))
#                if res.resNum != 172:
#                    self.failUnless( res.PHI )
#                if res.resNum != 2:
#                    self.failUnless( res.PSI )

        project.save()

if __name__ == "__main__":
    cing.verbosity = verbosityNothing
    cing.verbosity = verbosityDebug
    unittest.main()
