from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
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
import profile
import pstats
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
        v = cing.verbosity
        cing.verbosity = cing.verbosityNothing # temp disable error msg.
        self.assertEquals( ensureValidChainId('ABCD'), 'A')
        self.assertEquals( ensureValidChainId('BCDE'), 'B')
        cing.verbosity = v
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

    def test_RangeSelection(self):
        entryId = 'testEntry'
        project = Project(entryId)
        self.failIf(project.removeFromDisk())
        project = Project.open(entryId, status='new')
        mol = Molecule('testMol')
        project.appendMolecule(mol)
        offset1 = -10
        # homo dimer
        chainList = ( 'A', 'B' )
        sequence = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        seqL = len(sequence)
        lastResidueI = seqL - 1
        for cId in chainList:
            c = mol.addChain(cId)
            for i, rName in enumerate(sequence):
                rNumber = i+offset1
                Nterminal = False
                Cterminal = False
                if i == 0:
                    Nterminal = True
                if i == lastResidueI:
                    Cterminal = True
                r = c.addResidue(rName, rNumber, Nterminal = Nterminal, Cterminal = Cterminal)
                if r:
#                    NTdebug("Adding atoms to residue: %s" % r)
                    r.addAllAtoms()
#                else:
#                    NTdebug("Skipping atoms for residue: %s" % r)
                # end if
            # end for
        # end for chain

        # another homo dimer with renumbering.
        chainList = ( 'C', 'D' )
        offset2 = 100
        for cId in chainList:
            c = mol.addChain(cId)
            for i, rName in enumerate(sequence):
                rNumber = i+offset2
                Nterminal = False
                Cterminal = False
                if i == 0:
                    Nterminal = True
                if i == lastResidueI:
                    Cterminal = True
                r = c.addResidue(rName, rNumber, Nterminal = Nterminal, Cterminal = Cterminal)
                if r:
#                    NTdebug("Adding atoms to residue: %s" % r)
                    r.addAllAtoms()
#                else:
#                    NTdebug("Skipping atoms for residue: %s" % r)
                # end if
            # end for
        # end for chain
        NTdebug("Done creating simple fake molecule")
        self.assertFalse( mol.updateAll() )
        NTmessage( mol.format() )

        # Nada
        selectedResidueList = mol.ranges2list('')
        self.assertEquals( len(selectedResidueList), 2*len(chainList)*seqL)

        # Single residue
        selectedResidueList = mol.ranges2list('A.'+str(offset1))
        self.assertEquals( len(selectedResidueList), 1)
        NTdebug("Selected residues: %s" % str(selectedResidueList))

        # Two residues
        selectedResidueList = mol.ranges2list(str(offset1))
        self.assertEquals( len(selectedResidueList), 2)
        NTdebug("Selected residues: %s" % str(selectedResidueList))

        # Four residues in ranges
        selectedResidueList = mol.ranges2list('1-2')
        self.assertEquals( len(selectedResidueList), 4)
        NTdebug("Selected residues: %s" % str(selectedResidueList))

        # Eight residues in negative crossing ranges
        selectedResidueList = mol.ranges2list('-1-2')
        self.assertEquals( len(selectedResidueList), 8)
        NTdebug("Selected residues: %s" % str(selectedResidueList))


        selectedResidueList = mol.ranges2list('A.-5--2')
        self.assertEquals( len(selectedResidueList), 4)
        NTdebug("Selected residues: %s" % str(selectedResidueList))

        selectedResidueList = mol.ranges2list('-999-999')
        NTdebug("Selected residues: %s" % str(selectedResidueList))
        self.assertEquals( len(selectedResidueList), 2*len(chainList)*seqL)

        residueList2StartStopList = mol.ranges2StartStopList('-999-999')
        NTdebug('residueList2StartStopList: %s' % str(residueList2StartStopList))
        self.assertEquals( len(residueList2StartStopList), 8 )

#        """
#        Possible 5 situations:
#        a      # 1 # positive int
#        -a     # 2 # single int
#        -a-b   # 3 #
#        -a--b  # 4 #
#        a-b    # 5 # most common
#        """
        inputList = """
                      A.1
                      A.1-3
                      A.-2--1
                      A.-2-1
                      A.-3
                    """.split()
        for i, ranges in enumerate(inputList):
            NTdebug("test_RangeSelection: %d %s" % (i, ranges))
            residueList = mol.setResiduesFromRanges(ranges)
#            NTdebug('residueList: [%s]' % residueList)
            rangesRecycled = mol.residueList2Ranges(residueList)
#            NTdebug('rangesRecycled: [%s]' % rangesRecycled)
            self.assertEquals( ranges, rangesRecycled )


if __name__ == "__main__":
    os.chdir(cingDirTmp)
    cing.verbosity = verbosityDebug
    # Commented out because profiling isn't part of unit testing.
    if False:
        fn = 'fooprof'
        profile.run('unittest.main()', fn)
        p = pstats.Stats(fn)
    #     enable a line or two below for useful profiling info
        p.sort_stats('time').print_stats(10)
        p.sort_stats('cumulative').print_stats(2)
    else:
        unittest.main()
