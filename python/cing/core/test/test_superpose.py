"""
Unit test execute as:
python $CINGROOT/python/cing/core/test/test_superpose.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.classes import Project
from cing.core.constants import * #@UnusedWildImport
from cing.core.molecule import Coordinate
from cing.core.molecule import Model
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def test_superpose(self):
        pdbConvention = IUPAC
        entryId = "1brv"
#        entryId = "2vb1_simple" # Protein solved by X-ray.

        cingDirTmpTest = os.path.join( cingDirTmp, getCallerName() )
        mkdirs( cingDirTmpTest )
        self.failIf(os.chdir(cingDirTmpTest), msg =
            "Failed to change to test directory for files: " + cingDirTmpTest)

        pdbDirectory = os.path.join(cingDirTestsData,"pdb", entryId)
        pdbFileName = "pdb" + entryId + ".ent"
        pdbFilePath = os.path.join( pdbDirectory, pdbFileName)
        self.failIf( not os.path.exists(pdbFilePath), msg= "Failed to find file: "+pdbFilePath)

        # does it matter to import it just now?
        project = Project( entryId )
        self.failIf( project.removeFromDisk())
        project = Project.open( entryId, status='new' )
        project.initPDB( pdbFile=pdbFilePath, convention = pdbConvention )

        # Compare with molmol on 1brv's 48 models:
#        mean global bb    RMSD:  0.98 +/-  0.40 A  ( 0.10.. 2.19 A)
#        mean global heavy RMSD:  1.75 +/-  0.51 A  ( 0.54.. 3.33 A)
        # Note that in molmol the backbone protein atoms are defined: N, CA, C
        # CING used to include the carbonyl atom

        # using default parameters.
        ens = project.molecule.superpose(backboneOnly=True, includeProtons = False, iterations=2)
        nTdebug( 'ens %s' % ens)
        nTdebug( 'ens.averageModel %s' % ens.averageModel)
        self.assertAlmostEquals( 0.7643199324863148, ens.averageModel.rmsd, 3 )
        # Confirmed to be the 'averaage RMSD to mean: 0.698' in molmol using command
        #    Fit 'to_mean'.
        ens = project.molecule.superpose(backboneOnly=False, includeProtons = False,
                                         iterations=3) # no improvement to do 3 over the default 2 but left in for speed checking.
        nTdebug( 'ens.averageModel %s' % ens.averageModel)
        self.assertAlmostEquals( 0.99383582432002637, ens.averageModel.rmsd, 3 )
        # Confirmed to be the 'averaage RMSD to mean: 1.238' in molmol using command
        #    Fit 'to_mean'. Using 'heavy' atom selection. CING got there much faster.
        # because algorithm in molmol probably does a full list of iterations (47 or so)
        # and CING only 3.

    def test_superpose_atoms(self):
        coordList = NTlist()
        coordList.append(Coordinate( 2.427,   1.356,   3.559 ) )
        coordList.append(Coordinate( 1.878,   0.162,   3.927 ) )
        coordList.append(Coordinate( 0.906,  -0.611,   3.099 ) )
        coordList.append(Coordinate(-0.287,   0.182,   2.484 ) )

        model1 = Model('A', 0)
        model2 = Model('B', 1)

        model1.fitCoordinates.append( coordList[0].copy() )
        model1.fitCoordinates.append( coordList[1].copy() )
        model2.fitCoordinates.append( coordList[2].copy() )
        model2.fitCoordinates.append( coordList[3].copy() )

        rmsd = model2.superpose(model1)
        if rmsd  == None:
            nTerror("Failed to %s" % getCallerName())
        self.assertAlmostEquals(             rmsd, 2.566, places=3 )
        self.assertAlmostEquals( coordList[0].e.x, 2.427, places=3 )
        self.assertAlmostEquals( coordList[2].e.z, 3.099, places=3 )
        
    #end def

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
#
#mean global bb    RMSD:  0.98 +/-  0.40 A  ( 0.10.. 2.19 A)
#mean global heavy RMSD:  1.75 +/-  0.51 A  ( 0.54.. 3.33 A)


