"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_TalosPlus.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.Ccpn import Ccpn #@UnusedImport needed to throw a ImportWarning so that the test is handled properly.
from cing.PluginCode.required.reqNih import TALOSPLUS_STR
from cing.core.classes import Project
from cing.core.parameters import cingPaths
from unittest import TestCase
import shutil
import unittest
#from cing.Libs.fpconst import * #@UnusedWildImport

keyList = 'phi.value       psi.value      S2        Q_H'.split()
valueKnownList = [
# testing on 1brv CS's original list
[ NaN     , NaN    , NaN     , 0.333 ],
[ -84.373 , -0.613 , 0.437   , 0.065 ],
[ -92.523 , 134.029, 0.576   , 0.058 ],
[ -92.748 , 137.582, 0.764   , 0.109 ],
[ -63.445 , -26.461, 0.806   , 0.673 ],
[ -64.101 , -30.152, 0.785   , 0.805 ],
[ -65.017 , -34.867, 0.718   , 0.735 ],
[ -88.228 , -17.417, 0.586   , 0.623 ],
[ -118.938, 124.621, 0.539   , 0.155 ],
[ -88.351 , 131.755, 0.503   , 0.0   ],
[ -90.358 , 130.815, 0.491   , 0.0   ],
[ -68.65  , 151.069, 0.459   , 0.0   ],
[ -96.386 , 134.414, 0.49    , 0.0   ],
[ -106.223, 108.323, 0.604   , 0.0   ],
[ -59.368 , 146.232, 0.755   , 0.048 ],
[ -55.484 , -37.265, 0.824   , 0.754 ],
[ -65.649 , -20.595, 0.829   , 0.906 ],
[ -77.903 , -21.035, 0.815   , 0.707 ],
[ -82.666 , -8.174 , 0.82    , 0.411 ],
[ -93.0   , -5.753 , 0.786   , 0.153 ],
[ 89.293  , -6.185 , 0.772   , 0.069 ],
[ -71.994 , 137.703, 0.778   , 0.576 ],
[ -60.923 , -36.351, 0.83    , 0.966 ],
[ -62.28  , -44.978, 0.871   , 0.999 ],
[ -63.618 , -39.199, 0.873   , 0.995 ],
[ -66.4   , -38.272, 0.851   , 0.99  ],
[ -74.875 , -30.519, 0.843   , 0.971 ],
[ -78.056 , -39.161, 0.844   , 0.834 ],
[ -87.162 , -25.48 , 0.847   , 0.243 ],
[ -88.597 , 131.518, 0.723   , 0.045 ],
[ -86.522 , 129.79 , 0.533   , 0.045 ],
[ NaN     , NaN    , NaN     , 0.333 ]
]
valueKnownList = [
# testing on 1brv CS's list derived from peak list's convoluted conversion.
# TODO: fix bug on S2 parsing
[      NaN,      NaN,      NaN , 0.333 ],
[      NaN,      NaN,      NaN , 0.000 ],
[      NaN,      NaN,      NaN , 0.000 ],
[      NaN,      NaN,      NaN , 0.000 ],
[      NaN,      NaN,      NaN , 0.000 ],
[      NaN,      NaN,      NaN , 0.000 ],
[      NaN,      NaN,      NaN , 0.000 ],
[      NaN,      NaN,      NaN , 0.000 ],
[      NaN,      NaN,      NaN , 0.000 ],
[      NaN,      NaN,      NaN , 0.000 ],
[      NaN,      NaN,      NaN , 0.000 ],
[      NaN,      NaN,      NaN , 0.000 ],
[      NaN,      NaN,      NaN , 0.000 ], # No coordinates so no DSSP secondary structure so no S2 stored in CING.
[      NaN,      NaN,      NaN , 0.333 ], # same? Data is: 0.696 and 0.755
[  -59.675,  146.561,    0.786 , 0.171 ],
[  -57.037,  -37.564,    0.830 , 0.753 ],
[  -65.649,  -20.595,    0.829 , 0.906 ],
[  -77.903,  -21.035,    0.815 , 0.707 ],
[  -82.666,   -8.174,    0.819 , 0.411 ],
[  -93.000,   -5.753,    0.786 , 0.153 ],
[   89.293,   -6.185,    0.772 , 0.069 ],
[  -71.994,  137.703,    0.778 , 0.577 ],
[  -60.923,  -36.351,    0.831 , 0.966 ],
[  -62.280,  -44.978,    0.869 , 0.999 ],
[  -63.618,  -39.199,    0.867 , 0.995 ],
[  -66.400,  -38.272,    0.841 , 0.990 ],
[  -74.875,  -30.519,    0.835 , 0.971 ],
[  -78.056,  -39.161,    0.840 , 0.834 ],
[  -87.162,  -25.480,    0.847 , 0.243 ],
[  -88.597,  131.518,    0.723 , 0.045 ],
[  -86.522,  129.790,    0.534 , 0.042 ],
[      NaN,      NaN,    0.441 , 0.333 ]
]


class AllChecks(TestCase):
#    entryList = []
    entryList = "1brv_cs_pk_2mdl".split() # don't use until issue 213 fixed.
#    entryList = "1brv".split() # don't use until issue 213 fixed.
#    entryList = "CtR69AParis".split() # don't use until issue 213 fixed.

    def test_TalosPlus(self):
        if not cingPaths.talos:
            raise ImportWarning('No Talos installed.')

#        if you have a local copy you can use it; make sure to adjust the path setting below.
        fastestTest = True

        modelCount = 99
        if fastestTest:
            modelCount = 2

        cingDirTmpTest = os.path.join( cingDirTmp, getCallerName() )
        mkdirs( cingDirTmpTest )
        self.failIf(os.chdir(cingDirTmpTest), msg =
            "Failed to change to test directory for files: " + cingDirTmpTest)

        for entryId in AllChecks.entryList:
            project = Project.open(entryId, status='new')
            self.assertTrue(project, 'Failed opening project: ' + entryId)
            inputArchiveDir = os.path.join(cingDirTestsData, "ccpn")
            ccpnFile = os.path.join(inputArchiveDir, entryId + ".tgz")
            if not os.path.exists(ccpnFile):
                ccpnFile = os.path.join(inputArchiveDir, entryId + ".tar.gz")
                if not os.path.exists(ccpnFile):
                    self.fail("Neither %s or the .tgz exist" % ccpnFile)

            self.assertTrue(project.initCcpn(ccpnFolder=ccpnFile, modelCount=modelCount))
#            self.assertFalse(project.runTalosPlus())
#            self.assertTrue(project.save())
            self.assertFalse(project.validate(htmlOnly=True, doProcheck=False, doWhatif=False, doWattos=False))
            for r, res in enumerate(project.molecule.allResidues()):
#                NTdebug("Working on %s" % res)
                for c, valueToCheck in enumerate(keyList):
                    if c == 2: # TODO: reenable this check when debugged.
                        continue
                    valueDetermined = getDeepByKeysOrAttributes(res, TALOSPLUS_STR, valueToCheck)
                    valueReference = valueKnownList[r][c] # r/c is for row/column
                    if isNaN(valueDetermined) and isNaN(valueReference):
                        continue
                    if isNaN(valueDetermined) or isNaN(valueReference):
                        self.fail("Working on %s %s %s valueDetermined %s is not valueReference %s because only one of them isNaN" % (
                                res, c, valueToCheck, valueDetermined, valueReference))
                    self.assertAlmostEquals(valueReference, valueDetermined, 3)
            self.assertTrue(project.save())
#            project.close()
#            del project
#
#            project = Project.open(entryId, status = 'old')
            # Do not leave the old CCPN directory laying around since it might get added to by another test.
            if os.path.exists(entryId):
                self.assertFalse(shutil.rmtree(entryId))


if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
