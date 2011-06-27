from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.classes import DistanceRestraint
from cing.core.classes import Project
from cing.core.constants import * #@UnusedWildImport
from cing.core.molecule import Molecule
from cing.main import formatall
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    cingDirTmpTest = os.path.join( cingDirTmp, 'test_classes2' )
    mkdirs( cingDirTmpTest )
    os.chdir(cingDirTmpTest)

    def createSimpleFastProject(self):
        self.createSimpleFastProject2()

    def createSimpleFastProject2(self):
        entryId = 'test'

        self.project = Project( entryId )
        self.project.removeFromDisk()
        self.project = Project.open( entryId, status='new' )


        mol = Molecule('test')
        self.project.appendMolecule(mol)
        c = mol.addChain('A')
        r1 = c.addResidue('VAL', 1, Nterminal = True)
        r2 = c.addResidue('VAL', 2)
        r3 = c.addResidue('GLU', 3)
        r4 = c.addResidue('TYR', 4)
        r5 = c.addResidue('PHE', 5)
        r6 = c.addResidue('GLY', 6)
        r7 = c.addResidue('ARG', 7)
        r8 = c.addResidue('LEU', 8, Cterminal = True)
        for r in mol.allResidues():
            r.addAllAtoms()
        self.r1 = r1
        self.r2 = r2
        self.r3 = r3
        self.r4 = r4
        self.r5 = r5
        self.r6 = r6
        self.r7 = r7
        self.r8 = r8
        mol.updateAll()
#        NTmessage( mol.format() )

    def test_simplifySpecificallyForFcFeature(self):
        self.createSimpleFastProject()
        self.distanceRestraintList = self.project.distances.new(DR_LEVEL, status = 'keep')
        atomPairs = NTlist()
        r1 = self.r1
        r2 = self.r2
#        r3 = self.r3
        atomPairs.append((r1.MG1, r2.MG1))
        atomPairs.append((r1.MG2, r2.MG1))
        atomPairs.append((r1.MG1, r2.MG2))
        atomPairs.append((r1.MG2, r2.MG2))

#        atomPairs.append((r2.HN, r2.MG1))
#        atomPairs.append((r2.HN, r2.MG2))
        distanceRestraint = DistanceRestraint(atomPairs, 0.0, 5.0)
        if distanceRestraint.isValid:
            self.distanceRestraintList.append(distanceRestraint)
        else:
            NTerror('Failed to initialize DR with %s' % atomPairs)
#        NTdebug("dr before: %s" % formatall(distanceRestraint))

        # Takes 4 simplification iterations.
        self.assertEqual(distanceRestraint._simplify(), DistanceRestraint.STATUS_SIMPLIFIED)
#        NTdebug("dr after 1: %s" % formatall(distanceRestraint))
        self.assertEqual(distanceRestraint._simplify(), DistanceRestraint.STATUS_SIMPLIFIED)
#        NTdebug("dr after 2: %s" % formatall(distanceRestraint))
        self.assertEqual(distanceRestraint._simplify(), DistanceRestraint.STATUS_SIMPLIFIED)
#        NTdebug("dr after 3: %s" % formatall(distanceRestraint))
        self.assertEqual(distanceRestraint._simplify(), DistanceRestraint.STATUS_NOT_SIMPLIFIED)
#        NTdebug("dr after 4: %s" % formatall(distanceRestraint)) # don't print as it contains error token.
        _x = "dr after 4: %s" % formatall(distanceRestraint)

    def test_simplifySpecificallyForFcFeature_2(self):
        # disfunctional as of yet
        self.createSimpleFastProject()
        self.distanceRestraintList = self.project.distances.new(DR_LEVEL, status = 'keep')
        atomPairs = NTlist()
#        r1 = self.r1
        r2 = self.r2
#        r3 = self.r3
        atomPairs.append((r2.HN, r2.MG1))
        atomPairs.append((r2.MG2, r2.HN))

#        atomPairs.append((r2.HN, r2.MG1))
#        atomPairs.append((r2.HN, r2.MG2))
        distanceRestraint = DistanceRestraint(atomPairs, 0.0, 5.0)
        self.distanceRestraintList.append(distanceRestraint)
#        NTdebug("dr before: %s" % formatall(distanceRestraint))

        self.assertEqual(distanceRestraint.simplify(), DistanceRestraint.STATUS_SIMPLIFIED)
#        NTdebug("dr after 1: %s" % formatall(distanceRestraint))


    def test_CombinationToPseudo(self):
        self.createSimpleFastProject()

        r1 = self.r1
        r2 = self.r2
        r3 = self.r3
        atomLoL = [[r2.HN],
                          [r3.HB2, r3.HB3],
                          [r3.HB2],
                          [r1.HG11, r1.HG12, r1.HG13],
                          [r1.HG12, r1.HG11, r1.HG13],
                          [r1.HG11, r1.HG12, r1.HG13, r1.HG21, r1.HG22, r1.HG23], # unrepresented by below method.
                          ]
        pseudoListResultExpected = [ None,
                                    r3.QB,
                                    None,
                                    r1.MG1, # TODO: update these to MD1 when CING has IUPAC internally.
                                    r1.MG1,
                                    None,
                                     ]

        i = -1
        for atomList in atomLoL:
            i += 1
            firstAtom = atomList[0]
            self.assertEqual( firstAtom.getRepresentativePseudoAtom(atomList), pseudoListResultExpected[i])

    def test_CombinationToPseudoDouble(self):
#        'Simulate 1a24 1254.00     A    3    TYR    QD    A    8    GLN    QG'
        self.createSimpleFastProject()

        e = self.r3 # GLN
        y = self.r4 # TYR
        self.distanceRestraintList = self.project.distances.new(DR_LEVEL, status = 'keep')
        atomPairs = NTlist((e.HG2, y.HB2),
                           (e.HG3, y.HB2),
                           (e.HG2, y.HB3),
                           (e.HG3, y.HB3))
        distanceRestraint = DistanceRestraint(atomPairs, 0.0, 5.0)
#        NTdebug("before: %r" % distanceRestraint  )
        self.assertEqual(distanceRestraint.simplify(), DistanceRestraint.STATUS_SIMPLIFIED)
#        NTdebug("after: %r" % distanceRestraint  )

    def test_CombinationToPseudoDouble_2(self):
#        'Simulate 1a24 1254.00     A    3    TYR    QD    A    8    GLN    QB'
        self.createSimpleFastProject()

#        e = self.r3 # GLN
        y = self.r4 # TYR
        self.distanceRestraintList = self.project.distances.new(DR_LEVEL, status = 'keep')
        atomPairs = NTlist((y.HE1, y.HB2),
                           (y.HE2, y.HB2),
                           (y.HE1, y.HB3),
                           (y.HE2, y.HB3))
        distanceRestraint = DistanceRestraint(atomPairs, 0.0, 5.0)
#        NTdebug("before: %r" % distanceRestraint  )
        self.assertEqual(distanceRestraint.simplify(), DistanceRestraint.STATUS_SIMPLIFIED)
#        NTdebug("after: %r" % distanceRestraint  )

    def test_CombinationToPseudoQuadruple(self):
#        'Simulate 1a24 1254.00     A    3    TYR    QR    A    8    GLN    QB'
        self.createSimpleFastProject()

        y = self.r5 # PHE
        self.distanceRestraintList = self.project.distances.new(DR_LEVEL, status = 'keep')
        atomPairs = NTlist((y.QE, y.H),
                           (y.QD, y.H)
                           )
        distanceRestraint = DistanceRestraint(atomPairs, 0.0, 5.0)
#        NTdebug("before: %r" % distanceRestraint  )
        self.assertEqual(distanceRestraint.simplify(), DistanceRestraint.STATUS_NOT_SIMPLIFIED)
#        NTdebug("after: %r" % distanceRestraint  )

    def test_Simplify(self):
        self.createSimpleFastProject()

        y = self.r5 # PHE
        self.distanceRestraintList = self.project.distances.new(DR_LEVEL, status = 'keep')
        atomPairs = NTlist((y.QE, y.H),
                           (y.QE, y.H)
                           )
        distanceRestraint = DistanceRestraint(atomPairs, 0.0, 5.0)
#        NTdebug("before: %r" % distanceRestraint  )
        self.assertEqual(distanceRestraint.simplify(), DistanceRestraint.STATUS_NOT_SIMPLIFIED)
#        NTdebug("after: %r" % distanceRestraint  )

    def test_Simplify2(self):
        _help = """
        For 1a24
        783.00    A    20    PRO    QB    A    23    LEU    MD1   3.20    7.90    2.96    0.56    2.56    3.35    0.32    0.45    0.64    0    0    0
        783.01    A    20    PRO    QB    A    23    LEU    QD    3.20    7.90    2.96    0.56    2.56    3.35    0.32    0.45    0.64    0    0    0
        """
        self.createSimpleFastProject()

        y = self.r5 # PHE
        self.distanceRestraintList = self.project.distances.new(DR_LEVEL, status = 'keep')
        atomPairs = NTlist((y.QE, y.H),
                           (y.QE, y.H)
                           )
        distanceRestraint = DistanceRestraint(atomPairs, 0.0, 5.0)
#        NTdebug("before: %r" % distanceRestraint  )
        self.assertEqual(distanceRestraint.simplify(), DistanceRestraint.STATUS_NOT_SIMPLIFIED)
#        NTdebug("after: %r" % distanceRestraint  )

    def test_Simplify3(self):
        _help = """
        For 1a24
        783.00    A    20    PRO    QB    A    23    LEU    MD1   3.20    7.90    2.96    0.56    2.56    3.35    0.32    0.45    0.64    0    0    0
        783.01    A    20    PRO    QB    A    23    LEU    QD    3.20    7.90    2.96    0.56    2.56    3.35    0.32    0.45    0.64    0    0    0
        """
        self.createSimpleFastProject()

        y = self.r8 # LEU
        self.distanceRestraintList = self.project.distances.new(DR_LEVEL, status = 'keep')
        atomPairs = NTlist((y.QD,  y.H),
                           (y.MD1, y.H)
                           )
        distanceRestraint = DistanceRestraint(atomPairs, 0.0, 5.0)
#        NTdebug("before: %r" % distanceRestraint  )
        self.assertEqual(distanceRestraint._removeDuplicateAtomPairs2(), DistanceRestraint.STATUS_REMOVED_DUPLICATE)
#        NTdebug("after: %r" % distanceRestraint  )


if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
