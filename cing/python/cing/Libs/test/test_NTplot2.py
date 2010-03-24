from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityError
from cing.Libs.NTmoleculePlot import selectPointsFromRange
from cing.Libs.NTplot import HelixIconList
from cing.Libs.NTplot import NTplot
from cing.Libs.NTplot import NTplotSet
from cing.Libs.NTplot import boxAttributes
from cing.Libs.NTplot import lineAttributes
from cing.Libs.NTplot import triangularList
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTlist
from cing.Libs.peirceTest import peirceTest
from cing.core.classes import Project
from matplotlib.pylab import figure
from matplotlib.pylab import gca
from matplotlib.pylab import plot
from matplotlib.pylab import text
from numpy.core.numeric import arange
from unittest import TestCase
import cing
import os
import sys
import unittest
#from numpy.ma.core import arange
#from pylab import * # preferred importing. Includes nx imports. #@UnusedWildImport

def plotTestHistoDihedral():
    NTdebug("Starting plotTestHistoDihedral")
    ps = NTplotSet() # closes any previous plots
    ps.hardcopySize = (600,369)

    graphicsFormat = "png"
    residueName = "ASN1"
    dihedralName= "CHI1"
    dihedralNameLatex= "$\chi 1$"

    project     = Project('plotTestHistoDihedral')
    plotparams  = project.plotParameters.getdefault(dihedralName,'dihedralDefault')
    binsize     = int(plotparams.ticksize / 12 ) # 60 over 12 results in 5 degrees. as an int
    bins        = (plotparams.max - plotparams.min)/binsize # int

    angleList = NTlist( 50,60, 51, 53, 52, 54, 62, 90, 93 )
    angleList.cAverage()
    goodAndOutliers = peirceTest( angleList )
    if not goodAndOutliers:
        NTerror("No goodAndOutliers in plotTestHistoDihedral")
        return True
    angleList.good, angleList.outliers = goodAndOutliers


    angleList.limit(          plotparams.min, plotparams.max ) # Actually not plotted angle anymore.?
    angleList.cAverage(       plotparams.min, plotparams.max )
    angleList.good.limit(     plotparams.min, plotparams.max, byItem=1 )
    angleList.good.cAverage(  plotparams.min, plotparams.max, byItem=1 )
    angleList.outliers.limit( plotparams.min, plotparams.max, byItem=1 )

    xTicks = range(int(plotparams.min), int(plotparams.max+1), plotparams.ticksize)
#        NTdebug("xTicks: " + `xTicks`)
#        figWidth  = 600
#        figHeight = None # Golden which turns out to be 369
#            figHeight = figWidth * golden_mean
    plot = NTplot(title  = residueName,
                  xRange = (plotparams.min, plotparams.max),
                  xTicks = xTicks,
                  xLabel = dihedralNameLatex,
                  yLabel = 'Occurrence'
                )
    ps.addPlot(plot)

    if not angleList.__dict__.has_key('good'):
        NTerror("angleList.__dict__.has_key('good')")
        return True

    plot.histogram( angleList.good.zap(1),
                    plotparams.min, plotparams.max, bins,
                    attributes = boxAttributes( fillColor=plotparams.color )
                  )

    if angleList.__dict__.has_key('outliers'):
        plot.histogram( angleList.outliers.zap(1),
                    plotparams.min, plotparams.max, bins,
                    attributes = boxAttributes( fillColor=plotparams.outlier),
                    valueIndexPairList=angleList.outliers
                  )

    aAv  = angleList.cav
    width = 4.0
    lower, upper = 45, 55
    alpha = 0.3

    ylim = plot.get_ylim()
    ylimMax = 5 # Just assume.
    if ylim is not None:
        ylimMax = ylim[1]
    # note plotparams.lower is a color!
    bounds = NTlist(lower, upper)
    bounds.limit(plotparams.min, plotparams.max)
    if bounds[0] < bounds[1]: # single box
        point = (bounds[0], 0) # lower left corner of only box.
        sizes = (bounds[1]-bounds[0],ylimMax)
#            NTdebug("point: " + `point`)
#            NTdebug("sizes: " + `sizes`)
        plot.box(point, sizes, boxAttributes(fillColor=plotparams.lower, alpha=alpha))
    else: # two boxes
        # right box
        point = (bounds[0], 0) # lower left corner of first box.
        sizes = (plotparams.max-bounds[0],ylimMax)
#            NTdebug("point: " + `point`)
#            NTdebug("sizes: " + `sizes`)
        plot.box(point, sizes, boxAttributes(fillColor=plotparams.lower, alpha=alpha))
        point = (plotparams.min, 0) # lower left corner of second box.
        sizes = (bounds[1]-plotparams.min,ylimMax)
#            NTdebug("point: " + `point`)
#            NTdebug("sizes: " + `sizes`)
        plot.box(point, sizes, boxAttributes(fillColor=plotparams.lower, alpha=alpha))



#        plot.line( (lower, 0), (lower, ylimMax),
#                   lineAttributes(color=plotparams.lower, width=width) )
#        plot.line( (upper, 0), (upper, ylimMax),
#                   lineAttributes(color=plotparams.upper, width=width) )
#
    # Always plot the cav line
    plot.line( (aAv, 0), (aAv, ylimMax),
               lineAttributes(color=plotparams.average, width=width) )
#                   dashdotline() )
    fnBase = "testPlotHistoDihedral"
    if True:
        fn = fnBase + '.png'
    else:
        i=0
        fn = None
        while not fn or os.path.exists(fn):
            i += 1
            fn = fnBase + '_' + `i` + '.png'
    ps.hardcopy(fn, graphicsFormat)
#        plot.show()


class NTplot2Checks(TestCase):

    # important to switch to temp space before starting to generate files for the project.
    os.chdir(cingDirTmp)

    def testPlotHistoDihedral(self):
        plotTestHistoDihedral()


    def tttestSelectPointsFromRange( self ):
        pointList = [ (-1,9), (0,9), (1,9) ]
        self.assertTrue( len(selectPointsFromRange( pointList, start=-1, length=3))==3)
        self.assertTrue( len(selectPointsFromRange( pointList, start=0, length=1))==1)
        self.assertTrue( len(selectPointsFromRange( pointList, start=1, length=1))==1)
        self.assertTrue( len(selectPointsFromRange( pointList, start=2, length=1))==0)

    def tttestClipOn(self):
        # Bug reported to sf.net project for matplot
        figure().add_subplot(111)
        text(0.5,0.95, 'matplottext',
             horizontalalignment='left',
             verticalalignment='center',
             rotation='vertical',
             transform=gca().transAxes,
                     clip_on=None # BUG fixed: do not set this clip_on parameter. Even to False will lead to clipping.
             )
#        show()

    def tttestHelix(self):
        # Bug reported and fixed on sf.net project for matlibplot
        version = float(sys.version[:3])
        if version < 2.5:
            NTdebug('Not checking for a bug does exist in previous python versions below 2.5 and the related matplotlib.')
            return
        figure().add_subplot(111)
        ax = gca()
        x = 0         # in data coordinate system
        width = 2     # data
        y = 0.8      # axes coordinates
        height = 0.2 # axes.

        helixIconList = HelixIconList(seq=width, startPoint=(x,y),width=width,height=height,axis=ax)
        self.assertFalse(helixIconList.addPatches())
        for p in helixIconList.patchList:
            ax.add_patch(p)
        ax.set_xlim(xmax=10)
        ax.set_ylim(ymax=10)
#        show()

    def tttestZaagtand(self):
        t = arange( 0.,360.,1.)
        s = triangularList( t )
        plot(t,s)
#        show()

#def suite():
#    tests = ['testPlotHistoDihedral']
#    return unittest.TestSuite(map(NTplot2Checks, tests))

if __name__ == "__main__":
    cing.verbosity = verbosityError
    cing.verbosity = verbosityDebug
#    unittest.main('cing.Libs.test.test_NTplot2', 'NTplot2Checks_a')
    unittest.main()
