from cing.Libs.Geometry import violationAngle
from cing.Libs.NTutils import * #@UnusedWildImport
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def testViolationAngle(self):
#        // lower bound
#        // upper bound
#        // angle
#        // expected violation
        testValues = [
                [   5,    6,    15,     9.  ],
                [ 169, -172,   100,    69.  ], # low viol
                [ 172, -169,   100,    72.  ], # low viol
                [ -10,   20,    25,     5.  ], # upp viol
                [  10,   20,     6,     4.  ],
                [ 180,  180,   180,     0.  ],
                [   0,    0,     0,     0.  ],
                [ 140,  150,   -70,   140.  ], # low viol
                [  90,  100,   -70,   160.  ], # upp viol
                [  70,  100,   -70,   140.  ], # low viol
                [   5,   -5,     2,     3.  ], # pathological low viol
                [-169,  172,   180,     8.  ], # pathological upp viol triggered change in code.
                [-172,  169,   180,     8.  ], # pathological low viol triggered change in code.
                [  -2,    5,     3,     0.  ], # simple setup first
                [-722,  725,   722,     0.  ], # same but subtracted/added 2pi
                [-722,  725,   728,     3.  ], #
                [-722,  725,  -726,     4.  ], #
                [-200, -160,   180,     0.  ], #
                [-120,  120,   -35,     0.  ], #
                [   0,    0,   180,   180.  ], #
                [  -0,    0,   180,   180.  ], #
                [  -0,   -0,   180,   180.  ], #
                [   0,   -0,   180,   180.  ], #
                [-120,  120,   -35,     0.  ], #
                [  23,   41,   -19,    42.  ], #
                [  23,   41,   -24,    47.  ], #
                [ -50,   50,   260,    50.  ], # Angle Name: CHI1_173 Torsional Angle Atoms: (CYS173.N, CYS173.CA, CYS173.CB, CYS173.SG)
        ]

        for i in range( len(testValues)):
            viol = violationAngle(
                    value      = testValues[i][2],
                    lowerBound = testValues[i][0],
                    upperBound = testValues[i][1]
                    )
            NTdebug("Viol angle [%2d]: %8.0f" % (i, viol))
            self.assertEquals(testValues[i][3], viol)

if __name__ == "__main__":
    cing.verbosity = verbosityError
    cing.verbosity = verbosityDebug
    unittest.main()
