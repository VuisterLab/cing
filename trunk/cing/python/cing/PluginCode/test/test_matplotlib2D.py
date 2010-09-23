"""
Unit test execute as:
python $CINGROOT/python/cing/Libs/test/test_matplotlib2D.py
"""
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.numpyInterpolation import interp2_linear
from cing.Libs.numpyInterpolation import interpn_linear
from cing.Libs.numpyInterpolation import interpn_nearest
from cing.PluginCode.matplib import gray_inv
from matplotlib.pylab import * #@UnusedWildImport
from numpy import * #@UnusedWildImport
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def testBackEnd(self):

        # important to switch to temp space before starting to generate files for the project.
        self.failIf(os.chdir(cingDirTmp), msg =
            "Failed to change to directory for temporary test files: " + cingDirTmp)

        # Trying to plot without GUI backend.
#        use('Agg') Already present in NTplot.py

        plot( [1,2,3] , 'go' )

        savefig('backendPlot.png')
        savefig('backendPlot.pdf')
        close()

    def tttestNumpyInterpolation(self):
        x,y = ogrid[ -1:1:10j, -1:1:10j ]
        z = sin( x**2 + y**2 )
        vmin = -1.
        vmax =  1.
        binx = (x,y)
        tx = ogrid[ -1:1:10j, -1:1:10j ]

        subplot(221)
        title('original')
        imshow(z, vmin=vmin, vmax=vmax)
        subplot(223)
        title('interpn_nearest')
        imshow( interpn_nearest( z, tx, binx ), vmin=vmin, vmax=vmax )
        subplot(222)
        title('interpn_linear')
        imshow( interpn_linear( z, tx, binx ), vmin=vmin, vmax=vmax )
        subplot(224)
        title('interp2_linear')
        imshow( interp2_linear( z, tx[0],tx[1], x.ravel(),y.ravel() ), vmin=vmin, vmax=vmax )
        show()

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
