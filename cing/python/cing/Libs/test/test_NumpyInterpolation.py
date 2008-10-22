from cing import cingDirTmp
from cing import verbosityDebug
from cing.Libs.NTutils import NTdebug
from cing.Libs.numpyInterpolation import interp2_linear
from cing.Libs.numpyInterpolation import interpn_linear
from cing.Libs.numpyInterpolation import interpn_nearest
from numpy import * #@UnusedWildImport
from numpy.lib.index_tricks import ogrid
from pylab import * #@UnusedWildImport
from unittest import TestCase
import os #@Reimport
import cing
import unittest

class AllChecks(TestCase):
        
    os.chdir(cingDirTmp)

    def testNumpyInterpolation(self):
        x,y = ogrid[ -1:1:10j, -1:1:10j ]
        z = sin( x**2 + y**2 )

        binx = (x,y)
        tx = ogrid[ -2:2:100j, -2:2:100j ]

        subplot(221)
        title('original')
        imshow(z)
        subplot(223)
        title('interpn_nearest')
        imshow( interpn_nearest( z, tx, binx ) )
        subplot(222)
        title('interpn_linear')
        imshow( interpn_linear( z, tx, binx ) )
        subplot(224)
        title('interp2_linear')
        imshow( interp2_linear( z, tx[0],tx[1], x.ravel(),y.ravel() ) )
        show()

    def test_jfd(self):
        r,c = ogrid[ 0:10:5j, 0:1:5j ]
        # x is the row and 
        # y is the column but when printed the matrix is printed differently.
        z = r + c
#        z = sin( x - y )
        bins = (r,c)
        qr =  9.9
        qc =  0.1
        tx = ogrid[ qr:qr:1j, qc:qc:1j ]
#        tx = ( (-0.9), (-0.9) ) # single point interpolation
        interpolatedValueSection = interpn_linear( z, tx, bins )
        interpolatedValue = interpolatedValueSection[ 0,0 ] # need to use comma to separate
        # the rows and columns in numpy matrixes.
        NTdebug(" r: \n%s" % r)
        NTdebug(" c: \n%s" % c)
        NTdebug(" z: \n%s" % z)
        NTdebug(" tx: \n%s" % tx)
        NTdebug(" interpolatedValueSection: \n%s" % interpolatedValueSection)
        NTdebug(" interpolatedValue: %s" % interpolatedValue)
                    
if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
