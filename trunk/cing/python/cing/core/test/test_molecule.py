from cing import cingDirTmp
from cing import verbosityError
from cing.core.molecule import Chain
from cing.core.molecule import Coordinate
from cing.core.molecule import NTangleOpt
from cing.core.molecule import NTdihedralOpt
from cing.core.molecule import NTdistanceOpt
from unittest import TestCase
from cing.core.molecule import ensureValidChainId
from cing import verbosityDebug
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
        self.assertEquals( ensureValidChainId('ABCD'), 'A')
        self.assertEquals( ensureValidChainId('BCDE'), 'B')
        self.assertEquals( ensureValidChainId('1'), Chain.defaultChainId)
        self.assertEquals( ensureValidChainId('$'), Chain.defaultChainId)
        self.assertEquals( ensureValidChainId('-'), Chain.defaultChainId)
        self.assertEquals( ensureValidChainId('_'), Chain.defaultChainId)
        self.assertEquals( ensureValidChainId(None), Chain.defaultChainId)

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
