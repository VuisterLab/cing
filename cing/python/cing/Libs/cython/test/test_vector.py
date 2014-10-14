from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.cython.superpose  import NTcVector #@UnresolvedImport
from cing.core.molecule import Coordinate #@UnusedImport
from cing.core.molecule import CoordinateOld #@UnusedImport
from cing.core.molecule import nTdihedralOpt
from unittest import TestCase
import profile
import pstats
import unittest #@UnusedImport

class AllChecks(TestCase):

    def testVector0(self):
        v = NTcVector(0.0,1.0,2.0)
        nTdebug("v: %r or %s" % (v,v) )

    def testVector(self):
        n = 10 * 1000
        cList = []
        for _j in range(4):
            # performance is 3.1 s per 10,000
#            c = CoordinateOld(random(),random(),random())
            # performance is 8.2 s per 10,000
            c = Coordinate(random(),random(),random())
            cList.append(c)
        for _i in range(n):
            _d = nTdihedralOpt(cList[0], cList[1], cList[2], cList[3])
#            nTdebug("d: %8.3f" % d )

    def testSuperposeChains(self):
        pass
    
if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    profile.run('unittest.main()', 'fooprof')
    p = pstats.Stats('fooprof')
#    p.sort_stats('time').print_stats(10)
    p.sort_stats('cumulative').print_stats(20)
#    unittest.main()
