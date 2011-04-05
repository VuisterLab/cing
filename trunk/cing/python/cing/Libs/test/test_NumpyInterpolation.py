#import matplotlib # to pop-up a xwindow with command 'show()'
#matplotlib.use('GTKAgg') # enable this line and above.
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.html import hPlot
from cing.Libs.numpyInterpolation import * #@UnusedWildImport
from numpy import * #@UnusedWildImport
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    cingDirTmpTest = os.path.join( cingDirTmp, 'test_NumpyInterpolation' )
    mkdirs( cingDirTmpTest )
    os.chdir(cingDirTmpTest)


    def tttest_jfd_1(self):
        r,c = ogrid[ 0:10:5j, 0:1:5j ]
        # r is the row and
        # c is the column
        # but when printed the matrix is printed differently?
        z = r + c
        print z
#        z = sin( x - y )
        bins = (r,c)
        print bins
        testList = [
                    [ 1.25, 0.0, 1.25], # first the corners
                    [ 1.25, 0.125, 1.375], # first the corners
                    [ 0.0, 0.0, 0.0], # first the corners
                    [10.0, 0.0,10.0],
                    [ 0.0, 1.0, 1.0],
                    [10.0, 1.0,11.0],
                    [ 5.0, 0.5, 5.5], # center
                    ]
        for testTuple in testList:
            NTdebug("testTuple: %s" % testTuple)
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
            NTdebug(" interpolatedValue: %s" % interpolatedValue)
            self.assertAlmostEquals( resultExpected, interpolatedValue, 8)

    def tttest_jfd_2(self):
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

    def ttttest_jfd_2b(self):
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

    def tttest_jfd_3(self):
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

    def test_ExtendingMatrix(self):
        qExpectedList = [
    [
       [0.,0.,0.],
       [0.,0.,0.],
       [0.,0.,0.],
    ],
    [
       [ 3.,  2.,  3.,  2.],
       [ 1.,  0.,  1.,  0.],
       [ 3.,  2.,  3.,  2.],
       [ 1.,  0.,  1.,  0.],
    ],
    [
       [ 8.,  6.,  7.,  8.,  6.],
       [ 2.,  0.,  1.,  2.,  0.],
       [ 5.,  3.,  4.,  5.,  3.],
       [ 8.,  6.,  7.,  8.,  6.],
       [ 2.,  0.,  1.,  2.,  0.]
    ]
]
        for i in range(len(qExpectedList)):
            qExpected = qExpectedList[i]
            binCount = len(qExpected)-2
            p = numpy.arange(binCount*binCount).reshape(binCount,binCount)
            q = circularlizeMatrix(p)
            self.assertTrue((q==qExpected).all())

    def tttest_ExtendingMatrix2(self):
        binCount = 36
        p = numpy.arange(binCount*binCount).reshape(binCount,binCount)
        _q = circularlizeMatrix(p)
        self.assertFalse(circularlizeMatrix(None)) # shows error message
#        print p
#        print q


if __name__ == "__main__":
    cing.verbosity = verbosityDebug
#    cing.verbosity = verbosityNothing
    unittest.main()
