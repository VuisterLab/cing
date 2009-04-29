from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityError
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTmessage
from cing.core.classes import Project
from cing.core.molecule import Chain
from cing.core.molecule import Coordinate
from cing.core.molecule import Molecule
from cing.core.molecule import NTangleOpt
from cing.core.molecule import NTdihedralOpt
from cing.core.molecule import NTdistanceOpt
from cing.core.molecule import ensureValidChainId
from cing.main import format
from unittest import TestCase
import cing
import os
import unittest #@UnusedImport Too difficult for code analyzer.

class AllChecks(TestCase):

    def test_NTdihedral(self):
        # 1brv phi
        #ATOM      3  C   VAL A 171       2.427   1.356   3.559  1.00  0.00           C
        #ATOM     16  N   PRO A 172       1.878   0.162   3.927  1.00  0.00           N
        #ATOM     17  CA  PRO A 172       0.906  -0.611   3.099  1.00  0.00           C
        #ATOM     18  C   PRO A 172      -0.287   0.182   2.484  1.00  0.00           C
        cc1 = Coordinate( 2.427,   1.356,   3.559 )
        cc2 = Coordinate( 1.878,   0.162,   3.927 )
        cc3 = Coordinate( 0.906,  -0.611,   3.099 )
        cc4 = Coordinate(-0.287,   0.182,   2.484 )
        for _i in range(1 * 100):
            _angle = NTdihedralOpt( cc1, cc2, cc3, cc4 )
        self.assertAlmostEqual( NTdihedralOpt( cc1, cc2, cc3, cc4 ), -47.1, 1)
        self.assertAlmostEqual( NTangleOpt(    cc1, cc2, cc3      ), 124.4, 1)
        self.assertAlmostEqual( NTdistanceOpt( cc1, cc2           ),   1.4, 1)

    def test_EnsureValidChainId(self):
        self.assertEquals( ensureValidChainId('A'), 'A')
        self.assertEquals( ensureValidChainId('a'), 'a')
        self.assertEquals( ensureValidChainId('ABCD'), 'A')
        self.assertEquals( ensureValidChainId('BCDE'), 'B')
        self.assertEquals( ensureValidChainId('1'), '1')
        self.assertEquals( ensureValidChainId('$'), Chain.defaultChainId)
        self.assertEquals( ensureValidChainId('-'), Chain.defaultChainId)
        self.assertEquals( ensureValidChainId('A'), Chain.defaultChainId) # They are the same.
        self.assertEquals( ensureValidChainId(None), Chain.defaultChainId)

    def test_GetNextAvailableChainId(self):
        entryId = 'test'
        project = Project(entryId)
        self.failIf(project.removeFromDisk())
        project = Project.open(entryId, status='new')
        molecule = Molecule(name='moleculeName')
        project.appendMolecule(molecule) # Needed for html.
        chainId = molecule.getNextAvailableChainId()
        self.assertEquals( chainId, Chain.defaultChainId)
        n = 26 * 2 + 10 + 1 # alpha numeric including an extra and lower cased.
        for _c in range(n):
            chainId = molecule.getNextAvailableChainId()
            self.assertTrue( molecule.addChain(chainId))
        NTdebug("Added %d chains to: %s" % (n, format(molecule)))
        self.assertEqual( len(molecule.allChains()), n)

    def test_AddResidue_Standard(self):
        entryId = 'test'
        project = Project(entryId)
        self.failIf(project.removeFromDisk())
        project = Project.open(entryId, status='new')

        mol = Molecule('test')
        project.appendMolecule(mol)
        c = mol.addChain('A')
        r1 = c.addResidue('ALA', 1, Nterminal = True)
        if r1:
            r1.addAllAtoms()
        r2 = c.addResidue('VAL', 2)
        if r2:
            r2.addAllAtoms()
        r2 = c.addResidue('PHE', 3)
        if r2:
            r2.addAllAtoms()
        r2 = c.addResidue('ARG', 4)
        if r2:
            r2.addAllAtoms()
        r3 = c.addResidue('GLU', 5, Cterminal = True)
        if r3:
            r3.addAllAtoms()

        mol.updateAll()

        NTmessage( mol.format() )


if __name__ == "__main__":
    fn = 'fooprof'
    os.chdir(cingDirTmp)
#    os.path.join( cingDirTmp, fn)
    cing.verbosity = verbosityError
    cing.verbosity = verbosityDebug
    # Commented out because profiling isn't part of unit testing.
#    profile.run('unittest.main()', fn)
#    p = pstats.Stats(fn)
##     enable a line or two below for useful profiling info
#    p.sort_stats('time').print_stats(10)
#    p.sort_stats('cumulative').print_stats(2)

    unittest.main()
