#import matplotlib # to pop-up a xwindow with command 'show()'
#matplotlib.use('GTKAgg') # enable this line and above.
from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityNothing
from cing.Libs.NTutils import NTdebug
from cing.Libs.html import hPlot
from cing.Libs.numpyInterpolation import interp2_linear
from cing.Libs.numpyInterpolation import interpn_linear
from cing.Libs.numpyInterpolation import interpn_nearest
from matplotlib.pylab import subplot, title, imshow, show
from numpy import sin #@UnresolvedImport
from numpy.core.arrayprint import set_printoptions
from numpy.core.numeric import nan
from numpy.lib.index_tricks import ogrid
from unittest import TestCase
import cing
import os
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

    def test_jfd_1(self):
        r,c = ogrid[ 0:10:5j, 0:1:5j ]
        # r is the row and
        # c is the column
        # but when printed the matrix is printed differently?
        z = r + c
#        z = sin( x - y )
        bins = (r,c)
        testList = [
                    [ 0.0, 0.0, 0.0], # first the corners
                    [10.0, 0.0,10.0],
                    [ 0.0, 1.0, 1.0],
                    [10.0, 1.0,11.0],
                    [ 5.0, 0.5, 5.5], # center
                    ]
        for testTuple in testList:
            qr, qc, resultExpected = testTuple
            tx = ogrid[ qr:qr:1j, qc:qc:1j ]
    #        tx = ( (-0.9), (-0.9) ) # single point interpolation
            interpolatedValueSection = interpn_linear( z, tx, bins )
            interpolatedValue = interpolatedValueSection[ 0,0 ] # need to use comma to separate
            # the rows and columns in numpy matrixes.
    #        NTdebug(" r: \n%s" % r)
    #        NTdebug(" c: \n%s" % c)
#            NTdebug(" z: \n%s" % z)
#            NTdebug(" tx: \n%s" % tx)
#            NTdebug(" interpolatedValueSection: \n%s" % interpolatedValueSection)
#            NTdebug(" interpolatedValue: %s" % interpolatedValue)
            self.assertAlmostEquals( resultExpected, interpolatedValue, 8)

    def test_jfd_2(self):
        r,c = ogrid[ 0:360:37j, 0:360:37j ]
        z = r + 2.0 * c
        bins = (r,c)
        testList = [
                    [  0.0,   0.0,   0.0], # first the corners
                    [360.0,   0.0, 360.0],
                    [  0.0, 360.0, 720.0],
                    [360.0, 360.0,1080.0],
                    [180.0, 180.0, 540.0], # center
                    [350.0, 350.0,1050.0],
                    ]
        for testTuple in testList:
            qr, qc, resultExpected = testTuple
            tx = ogrid[ qr:qr:1j, qc:qc:1j ]
            interpolatedValueSection = interpn_linear( z, tx, bins )
            interpolatedValue = interpolatedValueSection[ 0,0 ] # need to use comma to separate
            self.assertAlmostEquals( resultExpected, interpolatedValue, 8)

    def test_jfd_2b(self):
        r,c = ogrid[ -180:180:37j, -180:180:37j ]
        z = r + 2.0 * c
        bins = (r,c)
        testList = [# y, x
                    # r, c
                    [-180.0,-180.0,-540.0], # first the corners starting with r_id,c_id = 0,0 (-180, -180)
                    [ 180.0,-180.0,-180.0],
                    [-180.0, 180.0, 180.0],
                    [ 180.0, 180.0, 540.0],
                    [   0.0,   0.0,   0.0],  # center
                    [ 170.0, 170.0, 510.0],
                    ]
        for testTuple in testList:
#            print 'testing', testTuple
            qr, qc, resultExpected = testTuple
            tx = ogrid[ qr:qr:1j, qc:qc:1j ]
            interpolatedValueSection = interpn_linear( z, tx, bins )
            interpolatedValue = interpolatedValueSection[ 0,0 ] # need to use comma to separate
            self.assertAlmostEquals( resultExpected, interpolatedValue, 8)

    def test_jfd_3(self):
        r,c = ogrid[ -180:180:10, -180:180:10 ]
        if hPlot.histRamaBySsAndCombinedResType == None:
            hPlot.initHist()
        set_printoptions(linewidth=100000) # insert no line endings for end of teriminal
        set_printoptions(threshold=nan) # show all elements
        z = hPlot.histRamaBySsAndResType[' ']['PRO']
#        print z
        bins = (r,c)

        testLoL = [[
                    [  0.0,   0.0,    0.0], # first the corners
                    [-180.0,-140.0,   1.0], # smack on one. That is from a hi bfactor 1a7s,A,PRO ,  48, ,-136.5,-177.2,  60.9
                    [-177.2,-136.5,   1.0], # from the db the exact value
                    [-180.0, -80.0,   7.0], # smack on seven
                    [ 140.0, -50.0,  11.0], # smack on seven
                    ],[
                    [  0.0,   0.0,    0.0], # first the corners
                    [-177.2,-136.5,   0.5], # from the db. Is truncated to 0.5 because there is nothing around.
                    [ 138.0, -47.1,  10.3], # model 1 of 1brv PRO172
        ]]

        for i, interpolationTypeIsNearest in enumerate( [True, False] ):
            testList = testLoL[i]
            for testTuple in testList:
                NTdebug( 'testing (interpolationTypeIsNearest %s) %s' % (interpolationTypeIsNearest, `testTuple`))
                qr, qc, resultExpected = testTuple
                tx = ogrid[ qr:qr:1j, qc:qc:1j ]
                f = interpn_linear
                if interpolationTypeIsNearest:
                    f = interpn_nearest
                interpolatedValueSection = f( z, tx, bins )
                interpolatedValue = interpolatedValueSection[ 0,0 ] # need to use comma to separate
                self.assertAlmostEquals( resultExpected, interpolatedValue, 1)


if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    cing.verbosity = verbosityNothing
    unittest.main()
