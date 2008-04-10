from IPython.Magic import pstats
from cing import cingDirTestsTmp
from cing import verbosityError
from cing.core.molecule import Coordinate
from cing.core.molecule import NTangleOpt
from cing.core.molecule import NTdihedralOpt
from cing.core.molecule import NTdistanceOpt
from unittest import TestCase

try:
    import cProfile as cProfile # in python >=2.5 @UnresolvedImport @UnusedImport
except:
    import profile as cProfile # in python <=2.4 @Reimport

import cing
import os
import unittest #@UnusedImport Too difficult for code analyser.

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

if __name__ == "__main__":
    fn = 'fooprof'
    os.chdir(cingDirTestsTmp)
#    os.path.join( cingDirTestsTmp, fn)
    cing.verbosity = verbosityError
    cProfile.run('unittest.main()', fn)
    p = pstats.Stats(fn)
    # enable a line or two below for useful profiling info
#    p.sort_stats('time').print_stats(10)
#    p.sort_stats('cumulative').print_stats(2)

