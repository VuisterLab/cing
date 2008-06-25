"""
Unit test
python $CINGROOT/python/cing/Libs/test/test_disulfides.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityNothing
from cing.Libs.NTutils import NTdebug
from cing.Libs.disulfides import chi3SS
from cing.Libs.disulfides import disulfideScore
from cing.core.classes import Project
from cing.core.constants import IUPAC
from unittest import TestCase
import cing
import os
import unittest


class AllChecks(TestCase):

    def test_disulfide(self):
        #entryId = "1ai0" # Most complex molecular system in any PDB NMR entry
        entryId = "1brv_1model" # Small much studied PDB NMR entry; 48 models
#        entryId = "1bus" # Small much studied PDB NMR entry:  5 models of 57 AA.: 285 residues.

        self.failIf( os.chdir(cingDirTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTmp)
        project = Project( entryId )
        self.failIf( project.removeFromDisk() )
        project = Project.open( entryId, status='new' )
        cyanaDirectory = os.path.join(cingDirTestsData,"cyana", entryId)
        pdbFileName = entryId+".pdb"
        pdbFilePath = os.path.join( cyanaDirectory, pdbFileName)
        NTdebug("Reading files from directory: " + cyanaDirectory)
        project.initPDB( pdbFile=pdbFilePath, convention = IUPAC )

#        print project.save()
#        NTdebug( project.cingPaths.format() )
#        self.assertTrue(runWattos(project))
        ###
        # testing
        ###
        cys=project.molecules[0].residuesWithProperties('C')
        # all cys(i), cys(j) pairs with j>i
        for i in range(len(cys)):
            c1 = cys[i]
            for j in range(i+1, len(cys)):
                c2 = cys[j]
                da = c1.CA.distance( c2.CA )
                db = c1.CB.distance( c2.CB )
                dg = c1.SG.distance( c2.SG )
                NTdebug( 'Considering pair : %s with %s' % (c1, c2)) 
                NTdebug( 'Ca-Ca            : %s', da)
                NTdebug( 'Cb-Cb            : %s', db)
                NTdebug( 'Sg-Sg            : %s', dg)
                NTdebug( 'chi3             : %s', chi3SS( db[0] ))
                NTdebug( 'scores           : %s', disulfideScore( c1, c2))
                NTdebug( '\n\n' )
        
                        
if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    cing.verbosity = verbosityNothing
    unittest.main()
