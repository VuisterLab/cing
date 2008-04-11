"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_pdb.py
"""
from cing import cingDirTestsData
from cing import cingDirTestsTmp
from cing import verbosityError
from cing import verbosityNothing
from cing.Libs.NTutils import NTdebug
from cing.core.classes import Project
from cing.core.constants import BMRB
from unittest import TestCase
import cing
import os
import unittest

class AllChecks(TestCase):

    def testRun(self):
        pdbConvention = BMRB
        entryCode = "2vb1_simple" # Protein solved by X-ray.

        self.failIf( os.chdir(cingDirTestsTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTestsTmp)

        project = Project( entryCode )
        self.failIf( project.removeFromDisk())
        project = Project.open( entryCode, status='new' )

        pdbFileName = entryCode+".pdb"
        pdbFilePath = os.path.join( cingDirTestsData, pdbFileName)

        project.initPDB( pdbFile=pdbFilePath, convention = pdbConvention )

        for chain in project.molecule.allChains():
            if chain.name != 'A':
                NTdebug('Skipping chain in: entry %s for chain code: %s' % (entryCode,chain.name) )
                continue

            for res in chain.allResidues():
                NTdebug('Doing entry %s for chain code %s residue %s' % (entryCode,chain.name,res))

                self.failUnless( res.has_key('PHI') and res.has_key('PSI'))
                if res.resNum != 1:
                    self.failUnless( res.PHI )
                if res.resNum != 2:
                    self.failUnless( res.PSI )

        project.save()

if __name__ == "__main__":
    cing.verbosity = verbosityNothing
    cing.verbosity = verbosityError
    unittest.main()
