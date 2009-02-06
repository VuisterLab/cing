"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_ccpn_2.py
"""
from cing import verbosityDebug
from cing import verbosityDefault
from cing.PluginCode.Ccpn import Ccpn
from cing.PluginCode.Ccpn import getRestraintBoundList
from cing.core.sml import NTdict
from unittest import TestCase
import cing
import unittest

class AllChecks(TestCase):

    def testRestraintsValuesRegular(self):
        _alsoSee = """See http://code.google.com/p/cing/issues/detail?id=121"""
#        lower, upper, targetValue, error     
        rList = [     
                 (0.0, 3.0, 4.0, 1.0), # Should give a warning and just use lower/upper as is. 
                 (0.0, 3.0, 4.0, None), # Same 
                 (0.0, 5.5, 5.5, None), # failed for entry 2cka with original code. 
                 (None, None, 5.5, None),
                 (None, None, 5.5, 1.0),
                 (None, None, None, None),
                 (None, 4.0, None, None), # upper bound only
                 (2.0, None, None, None), # lower only
                 (-2.0, 5.0, None, None), # should give reasonable error and unset distance lower bound
                  
                 (-5.0, 5.0, None, None, Ccpn.RESTRAINT_IDX_DIHEDRAL), # Is a range of 10 degrees. 
                 (5.0, -5.0, None, None, Ccpn.RESTRAINT_IDX_DIHEDRAL), # Is a range of 350 degrees. 
                 (None, None, -10.0, 20.0, Ccpn.RESTRAINT_IDX_DIHEDRAL), # Is a range of 20 degrees. 
                 (None, None, 350.0, 20.0, Ccpn.RESTRAINT_IDX_DIHEDRAL), # Same. 
                 (None, None, 123.0, 200.0, Ccpn.RESTRAINT_IDX_DIHEDRAL), # Give a reasonable warning and sets to full circle by setting to (0,-SMALL_FLOAT_FOR_DIHEDRAL_ANGLES)
                   ]
        cingRlist = [ 
                     (0.0, 3.0),
                     (0.0, 3.0),
                     (0.0, 5.5),
                     (5.5, 5.5),
                     (4.5, 6.5),
                     None,
                     (None, 4.0),
                     (2.0, None),
                     (None, 5.0),
                     
                     (-5.0, 5.0), # dihedrals
                     (5.0, -5.0),
                     (-30.0, 10.0),                     
                     (-30.0, 10.0),                     
                     (0.0, -Ccpn.SMALL_FLOAT_FOR_DIHEDRAL_ANGLES),                     
                   ]

        for i in range(len(rList)):
            cc = rList[i]
            ccpnConstraint = NTdict()
            ccpnConstraint.lowerLimit = cc[0] 
            ccpnConstraint.upperLimit = cc[1] 
            ccpnConstraint.targetValue = cc[2] 
            ccpnConstraint.error = cc[3]
            restraintTypeIdx = Ccpn.RESTRAINT_IDX_DISTANCE
            if len(cc) >= 5:
                restraintTypeIdx = cc[4]

            cie = cingRlist[i]
#               Output: floats (lower, upper)
            ci = getRestraintBoundList(ccpnConstraint,restraintTypeIdx)

            if not ci:
                self.assertFalse(cie)
            else:
                self.assertEquals(ci[0], cie[0])
                self.assertEquals(ci[1], cie[1])


if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    cing.verbosity = verbosityDefault
    unittest.main()
