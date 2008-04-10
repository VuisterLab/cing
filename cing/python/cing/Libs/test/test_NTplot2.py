from cing import cingDirTestsTmp
from cing import cingPythonCingDir
from cing import verbosityDebug
from cing import verbosityError
from cing.Libs.NTplot import HelixIconList
from cing.Libs.NTplot import NTplot
from cing.Libs.NTplot import NTplotSet
from cing.Libs.NTplot import boxAttributes
from cing.Libs.NTplot import lineAttributes
from cing.Libs.NTplot import plusPoint
from cing.Libs.NTplot import selectPointsFromRange
from cing.Libs.NTplot import triangularList
from cing.Libs.NTplot import useMatPlotLib
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTlist
from cing.Libs.peirceTest import peirceTest
from cing.core.classes import Project
from matplotlib.pylab import Float
from matplotlib.pylab import UInt8
from matplotlib.pylab import figure
from matplotlib.pylab import fromstring
from matplotlib.pylab import gca
from matplotlib.pylab import imshow
from matplotlib.pylab import nx
from matplotlib.pylab import plot
from matplotlib.pylab import resize
from matplotlib.pylab import text
from unittest import TestCase
import Image
import cing
import os
import unittest
#from pylab import * # preferred importing. Includes nx imports.

class AllChecks(TestCase):

    # important to switch to temp space before starting to generate files for the project.
    os.chdir(cingDirTestsTmp)
    NTdebug("Using matplot (True) or biggles: %s", useMatPlotLib)


    def testPlotHistoDihedral(self):
        ps = NTplotSet() # closes any previous plots
        ps.hardcopySize = (600,369)

        graphicsFormat = "png"
        residueName = "ASN1"
        dihedralName= "CHI1"
        dihedralNameLatex= "$\chi 1$"

        project     = Project('testPlotHistoDihedral')
        plotparams  = project.plotParameters.getdefault(dihedralName,'dihedralDefault')
        binsize     = int(plotparams.ticksize / 12 ) # 60 over 12 results in 5 degrees. as an int
        bins        = (plotparams.max - plotparams.min)/binsize # int

        angleList = NTlist( 50,60, 51, 53, 52, 54, 62, 90, 93 )
        angleList.cAverage()
        goodAndOutliers = peirceTest( angleList )
        self.failUnless( goodAndOutliers )
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

        self.failUnless( angleList.__dict__.has_key('good'))
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
        if ylim:
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
        ps.hardcopy("testPlotHistoDihedral."+graphicsFormat, graphicsFormat)
#        plot.show()

    def testPlotDihedral2D(self):
        ps = NTplotSet() # closes any previous plots
        ps.hardcopySize = (500,500)

        graphicsFormat = "png"
        residueName = "ASN1"
        dihedralName1= "PHI"
        dihedralName2= "PSI"
        d1 = NTlist(-45, -50) # outside the range.
        d2 = NTlist(60,70)

        # 4 boxes:
        lower1, upper1 = 120,   0
        lower2, upper2 = 130,  20
        # left/right boxes:
#        lower1, upper1 =  90, 270
#        lower2, upper2 =   0,  70
        # upper/lower boxes:
#        lower1, upper1 =   0,  70
#        lower2, upper2 =  80, 270
        # borring one box
#        lower1, upper1 =   0,  70
#        lower2, upper2 =  10,  60

        # important to switch to temp space before starting to generate files for the project.
        self.failIf( os.chdir(cingDirTestsTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTestsTmp)
        project     = Project('testPlotHistoDihedral2D')
        plotparams1 = project.plotParameters.getdefault(dihedralName1,'dihedralDefault')
        plotparams2 = project.plotParameters.getdefault(dihedralName2,'dihedralDefault')

        d1.limit(plotparams1.min, plotparams1.max)
        d1.limit(plotparams2.min, plotparams2.max)

        plot = NTplot( title  = residueName,
          xRange = (plotparams1.min, plotparams1.max),
          xTicks = range(int(plotparams1.min), int(plotparams1.max+1), plotparams1.ticksize),
          xLabel = dihedralName1,
          yRange = (plotparams2.min, plotparams2.max),
          yTicks = range(int(plotparams2.min), int(plotparams2.max+1), plotparams2.ticksize),
          yLabel = dihedralName2)
        ps.addPlot(plot)

        # Plot a Ramachandran density background
        imageFileName = os.path.join( cingPythonCingDir,'PluginCode','data', 'RamachandranLaskowski.png' )
        self.assertTrue( os.path.exists(imageFileName) )

        im = Image.open( imageFileName )
        s = im.tostring()
        rgb = fromstring( s, UInt8).astype(Float)/255.0
        rgb = resize(rgb, (im.size[1],im.size[0], 3))
        extent = (plotparams1.min, plotparams1.max,plotparams2.min, plotparams2.max)
        im = imshow(rgb, alpha=0.05, extent=extent)


        self.assertFalse( plot.plotDihedralRestraintRanges2D(lower1, upper1,lower2, upper2))

        plot.points( zip( d1, d2), attributes=plusPoint )
        ps.hardcopy("testPlotDihedral2D."+graphicsFormat, graphicsFormat)
#        plot.show()


    def testSelectPointsFromRange( self ):
        pointList = [ (-1,9), (0,9), (1,9) ]
        self.assertTrue( len(selectPointsFromRange( pointList, start=-1, length=3))==3)
        self.assertTrue( len(selectPointsFromRange( pointList, start=0, length=1))==1)
        self.assertTrue( len(selectPointsFromRange( pointList, start=1, length=1))==1)
        self.assertTrue( len(selectPointsFromRange( pointList, start=2, length=1))==0)



    def testClipOn(self):
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

    def testHelix(self):
        # Bug reported and fixed on sf.net project for matlibplot
        figure().add_subplot(111)
        ax = gca()
        x = 0         # in data coordinate system
        width = 2     # data
        y = 0.8      # axes coordinates
        height = 0.2 # axes.

        helixIconList = HelixIconList(axis=ax,seq=width, xy=(x,y),width=width,height=height)
        self.assertFalse(helixIconList.addPatches())
        for p in helixIconList.patchList:
            ax.add_patch(p)
        ax.set_xlim(xmax=10)
        ax.set_ylim(ymax=10)
#        show()

    def testZaagtand(self):
        t = nx.arange( 0.,360.,1.)
        s = triangularList( t )
        plot(t,s)
#        show()


if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    cing.verbosity = verbosityError
    unittest.main()
