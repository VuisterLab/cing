from cing import cingDirTestsTmp
from cing.Libs.NTplot import NTplot
from cing.Libs.NTplot import boxAttributes
from cing.Libs.NTplot import greenLine
from cing.Libs.NTplot import plusPoint
from cing.Libs.NTutils import NTfill
from cing.Libs.NTutils import NTlist
from cing.Libs.peirceTest import peirceTest
from cing.core.classes import Project
from pylab import * #@UnusedWildImport
from unittest import TestCase
from cing.Libs.NTplot import circlePoint
from cing.Libs.NTplot import lineAttributes
from cing.Libs.NTutils import printDebug
from cing import verbosityDebug
import cing
import os #@Reimport
import unittest

class AllChecks(TestCase):

    def tttestPlotVaria(self):
        p = NTplot( title = 'test', xRange=(0,10), yRange=(0,10), xLabel='aap' )
    
        p.box( (1,0), (0.9,2), boxAttributes( lineColor='black', line=True, fillColor='blue', fill=True) )
        p.box( (2,0), (0.9,5), boxAttributes( lineColor='green', line=True, fillColor='red',  fill=True) )
#        p.point( (3,3.5,0,1),  pointAttributes(color='red') )
        color = 'red'
        p.point( (7,6,0,2), circlePoint(pointColor=color, fillColor=color, lineColor=color) )
        p.label( (7,6), 'label', plusPoint)
        p.line( (5,1), (10,0), greenLine )
#    
        p.labeledPoint( (5,5), 'point 5' )
#    
        x=[3,5,6,2,8,9,4,5]
        y=[5,2,3,1,7,8,6,3]
        ey=[0.1,0.2,0.5,0,0.2,0.1]
#    
        p.points(map(None,x,y,NTfill(0.0,len(x)), ey))
        p.setMinorTicks(.5)
#        p.show()


    def tttestPlotModelHisto(self):
        modelCount = 2
        plot = NTplot(        xLabel = 'Model',
                              xRange = (0, modelCount),
                              yLabel = 'Outliers',
                              hardcopySize= (600,300),
                              aspectRatio = 0.5
                            )
#        project.models[i] holds the number of outliers for model i.
#        models is a NTdict.
        outliersPerModel = { 0:0, 1:0 } # actual data for 1brv's first models.
        plot.barChart( outliersPerModel.items(),
                       0.05, 0.95,
                       attributes = boxAttributes( fillColor='green' )
                     )
        self.failIf( os.chdir(cingDirTestsTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTestsTmp)
        graphicsFormat = NTplot().graphicsOutputFormat
        plot.hardcopy( 'outliers.'+graphicsFormat, graphicsFormat )
    
                    
        
    def testPlotHistoDihedral(self):
        
#        printDebug("Using mat plot (True) or biggles: "+ `useMatPlotLib`)
        graphicsFormat = "png"
        residueName = "ASN1"
        dihedralName= "CHI1"
        dihedralNameLatex= "$\chi 1$"

        # important to switch to temp space before starting to generate files for the project.
        self.failIf( os.chdir(cingDirTestsTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTestsTmp)
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
#        printDebug("xTicks: " + `xTicks`)
        figWidth  = 600
        figHeight = None # Golden which turns out to be 369
#            figHeight = figWidth * golden_mean
        plot = NTplot(title  = residueName,
                      xRange = (plotparams.min, plotparams.max),
                      xTicks = xTicks,
                      xLabel = dihedralNameLatex,
                      yLabel = 'Occurrence',
                      hardcopySize= (figWidth,figHeight)
                    )
    
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
            printDebug("point: " + `point`)
            printDebug("sizes: " + `sizes`)
            plot.box(point, sizes, boxAttributes(fillColor=plotparams.lower, alpha=alpha))
        else: # two boxes
            # right box
            point = (bounds[0], 0) # lower left corner of first box.
            sizes = (plotparams.max-bounds[0],ylimMax)
            printDebug("point: " + `point`)
            printDebug("sizes: " + `sizes`)
            plot.box(point, sizes, boxAttributes(fillColor=plotparams.lower, alpha=alpha))
            point = (plotparams.min, 0) # lower left corner of second box.
            sizes = (bounds[1]-plotparams.min,ylimMax)
            printDebug("point: " + `point`)
            printDebug("sizes: " + `sizes`)
            plot.box(point, sizes, boxAttributes(fillColor=plotparams.lower, alpha=alpha))
        
        
        
#        plot.line( (lower, 0), (lower, ylimMax),
#                   lineAttributes(color=plotparams.lower, width=width) )
#        plot.line( (upper, 0), (upper, ylimMax),
#                   lineAttributes(color=plotparams.upper, width=width) )
#
        # Always plot the cav line
        plot.line( (aAv, 0), (aAv, ylimMax), 
                   lineAttributes(color=plotparams.average, width=width) )
#        plot.show()
        plot.hardcopy("testPlotHistoDihedral."+graphicsFormat, graphicsFormat)

    

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
