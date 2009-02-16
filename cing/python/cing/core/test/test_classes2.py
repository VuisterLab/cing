from cing import verbosityDebug
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTmessage
from cing.core.classes import DistanceRestraint
from cing.core.classes import Project
from cing.core.constants import DR_LEVEL
from cing.core.molecule import Molecule
from cing.core.sml import NTlist
from cing.main import formatall
from unittest import TestCase
import cing
import unittest

class AllChecks(TestCase):

    def creatSimpleFastProject(self):
        entryId = 'test'
        self.project = Project(entryId)

        mol = Molecule('test')
        self.project.appendMolecule(mol)
        c = mol.addChain('A')
        r1 = c.addResidue('VAL', 1, Nterminal = True)
        if r1:
            r1.addAllAtoms()
        r2 = c.addResidue('VAL', 2)
        if r2:
            r2.addAllAtoms()
#        r3 = c.addResidue('GLU', 3, Cterminal = True)
#        if r3:
#            r3.addAllAtoms()
        self.r1 = r1
        self.r2 = r2
        mol.updateAll()                
#        NTmessage( mol.format() )        
        
    def tttest_simplifySpecificallyForFcFeature(self):
        self.creatSimpleFastProject()
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
        self.distanceRestraintList.append(distanceRestraint)
#        NTdebug("dr before: %s" % formatall(distanceRestraint))
        self.assertEqual(distanceRestraint.simplifySpecificallyForFcFeature(), DistanceRestraint.STATUS_SIMPLIFIED)
#        NTdebug("dr after 1: %s" % formatall(distanceRestraint))
        self.assertEqual(distanceRestraint.simplifySpecificallyForFcFeature(), DistanceRestraint.STATUS_SIMPLIFIED)
#        NTdebug("dr after 2: %s" % formatall(distanceRestraint))
        self.assertEqual(distanceRestraint.simplifySpecificallyForFcFeature(), DistanceRestraint.STATUS_SIMPLIFIED)
#        NTdebug("dr after 3: %s" % formatall(distanceRestraint))
        self.assertEqual(distanceRestraint.simplifySpecificallyForFcFeature(), DistanceRestraint.STATUS_NOT_SIMPLIFIED)
#        NTdebug("dr after 4: %s" % formatall(distanceRestraint))
        
    def tttest_simplifySpecificallyForFcFeature_2(self):
        self.creatSimpleFastProject()
        self.distanceRestraintList = self.project.distances.new(DR_LEVEL, status = 'keep')
        atomPairs = NTlist()
        r1 = self.r1        
        r2 = self.r2        
#        r3 = self.r3
        atomPairs.append((r1.HN, r2.MG1))
        atomPairs.append((r2.MG2, r1.HN))

#        atomPairs.append((r2.HN, r2.MG1))
#        atomPairs.append((r2.HN, r2.MG2))
        distanceRestraint = DistanceRestraint(atomPairs, 0.0, 5.0)
        self.distanceRestraintList.append(distanceRestraint)
#        NTdebug("dr before: %s" % formatall(distanceRestraint))
        self.assertEqual(distanceRestraint.simplifySpecificallyForFcFeature(), DistanceRestraint.STATUS_SIMPLIFIED)
#        NTdebug("dr after 1: %s" % formatall(distanceRestraint))
        self.assertEqual(distanceRestraint.simplifySpecificallyForFcFeature(), DistanceRestraint.STATUS_NOT_SIMPLIFIED)
#        NTdebug("dr after 2: %s" % formatall(distanceRestraint))
        
    def test_simplifySpecificallyForFcFeature_2(self):
        self.creatSimpleFastProject()
        self.distanceRestraintList = self.project.distances.new(DR_LEVEL, status = 'keep')
        atomPairs = NTlist()
        r1 = self.r1        
        r2 = self.r2        
#        r3 = self.r3
        atomPairs.append((r1.HN, r2.MG1))
        atomPairs.append((r2.MG2, r1.HN))

#        atomPairs.append((r2.HN, r2.MG1))
#        atomPairs.append((r2.HN, r2.MG2))
        distanceRestraint = DistanceRestraint(atomPairs, 0.0, 5.0)
        self.distanceRestraintList.append(distanceRestraint)
        NTdebug("dr before: %s" % formatall(distanceRestraint))
        
        self.assertFalse(distanceRestraint.simplify())
        NTdebug("dr after 1: %s" % formatall(distanceRestraint))
        
        
        
if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
