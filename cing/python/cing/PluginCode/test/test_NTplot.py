"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_NTplot.py
"""
from cing import cingDirTmp
from cing.Libs.NTplot import * #@UnusedWildImport
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.matplib import * #@UnusedWildImport
from unittest import TestCase
import unittest
#from pylab import * # preferred importing. Includes nx imports. #@UnusedWildImport

class AllChecks(TestCase):

    # important to switch to temp space before starting to generate files for the project.
    cingDirTmpTest = os.path.join( cingDirTmp, 'test_NTplot' )
    mkdirs( cingDirTmpTest )
    os.chdir(cingDirTmpTest)

    def testPlotVaria(self):
        ps = NTplotSet() # closes any previous plots
        p = ps.createSubplot(1,1,1)
        p.title = 'test'
        p.xRange=(0,10)
        p.yRange=(0,10)
        p.xLabel='aap'
        ps.subplotsAdjust(left = 0.2) # Accommodate extra Y axis label.

        p.box( (1,0), (0.9,2), boxAttributes( lineColor='black', line=True, fillColor='blue', fill=True) )
        p.box( (2,0), (0.9,5), boxAttributes( lineColor='green', line=True, fillColor='red',  fill=True) )
        p.box( (3,0), (0.9,4), boxAttributes( lineColor='green', line=True, fillColor='red',  fill=False) )
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
        p.points(map(None,x,y,nTfill(0.0,len(x)), ey))
        p.setMinorTicks(.5)

        attr = fontVerticalAttributes()
        attr.fontColor  = 'blue'
        p.labelAxes( (-0.12, 0.5), 'Backbone', attributes=attr)
        attr.fontColor  = 'black'
        p.labelAxes( (-0.2, 0.5), 'Z-scores throughout', attributes=attr)

#        p.yRange = None # Should autoscale the plot in y.
        ps.hardcopy('testPlotVaria.png')
        ps.show()


    def _testPlotModelHisto(self):
        ps = NTplotSet() # closes any previous plots
        outliersPerModel = { 0:2, 1:3 }
        valueList = outliersPerModel.values()

        modelCount = len(outliersPerModel.keys())
        plot = NTplot(        xLabel = 'Model',
                              xRange = (0, modelCount),
#                              yRange = (0, 5),
                              yLabel = 'Outliers',
                              hardcopySize= (600,300),
#                              aspectRatio = 0.5
                            )
        ps.addPlot(plot)
        plot.autoScaleYByValueList(valueList,
                    startAtZero=True,
                    useIntegerTickLabels=True
                    )
        plot.barChart( outliersPerModel.items(),
                       0.05, 0.95,
                       attributes = boxAttributes(fillColor='green' ) )
        ps.hardcopy( 'testPlotModelHisto.png' )
#        plot.show()



    def _testTo3StateUpper(self):
        self.assertEquals(     to3StateDssp(['S','E']), [' ','S'])
        self.assertEquals(     to3StateDssp(['h','H']), [' ','H'])
        self.assertNotEquals(  to3StateDssp([' ','H']), ['H','H'])
        self.assertEquals(     to3StateDssp(['X','H']), [' ','H'])

    def _testPlotSet(self):
#        hardcopySize = (60,30)
        ps = NTplotSet() # closes any previous plots
        nrows = 3
        ntPlot1 = ps.createSubplot(nrows,1,1,useResPlot=True)
        ntPlot2 = ps.createSubplot(nrows,1,2)
        ntPlot3 = ps.createSubplot(nrows,1,3)
        ntPlot1.xTicks = []
        point = [0,1]
        sizes = [.2,.3]
        ntPlot1.box(point, sizes)
        ntPlot2.box(point, sizes)
        ntPlot3.box(point, sizes)

        ps.hardcopySize = (400,300)
#        ps.show()
        ps.hardcopy('testPlotSet.png')

if __name__ == "__main__":
    cing.verbosity = verbosityError
#    cing.verbosity = verbosityDebug
    unittest.main()
