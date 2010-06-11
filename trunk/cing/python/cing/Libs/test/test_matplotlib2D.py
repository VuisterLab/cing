"""
Unit test execute as:
python $CINGROOT/python/cing/Libs/test/test_matplotlib2D.py
"""
from cing.Libs.NTplot import gray_inv
from cing.Libs.NTutils import * #@UnusedWildImport
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def testMatplotlibColorSegmented(self):
        palette  = gray_inv # from white to black
        # Testing defaults should be the same when set or not set.
        for doSet in ( False, True):
            NTdebug("doSet: %s" % doSet)
            if doSet:
                palette.set_under(color = 'w', alpha = 1.0 )
                palette.set_over(color = 'k', alpha = 1.0 )
                palette.set_bad(color = 'k', alpha = 0.0 )
            NTdebug("under: %s"   % str(palette._rgba_under))
            NTdebug("over : %s"   % str(palette._rgba_over))
            NTdebug("bad  : %s\n" % str(palette._rgba_bad))
            self.assertEqual(palette(0.0)[0],1.0) # low end is white with alpha 1
            self.assertEqual(palette(0.0)[3],1.0)
            self.assertEqual(palette(1.0)[0],0.0) # hi end is white with alpha 1
            self.assertEqual(palette(1.0)[3],1.0) #
            self.assertEqual(      palette(-1.0  )[0],1.0)   # under should be white with alpha 0 should actually be true, alpha needs to be zero for under.
            self.assertEqual(      palette(-1.0  )[3],1.0)
            self.assertEqual(      palette( 9.0  )[0],0.0)   # over should be black with alpha 1 should actually be true, alpha needs to be zero for under.
            self.assertEqual(      palette( 9.0  )[3],1.0)

    def testMatplotlibColorSegmented3(self):
        palette  = gray_inv
        palette.set_under(color = 'w', alpha = 0.0 )
        # See issue 214
        paletteStr = str( palette([-1,     # under: red but with alpha zero.
                       0.,      # black with alpha 1
                       1,      # white with alpha 1
                       ],
        #               alpha=0)
        ))
        NTdebug( paletteStr )

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
