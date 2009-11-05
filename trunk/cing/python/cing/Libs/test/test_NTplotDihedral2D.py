"""
Unit test execute as:
python -u $CINGROOT/python/cing/Libs/test/test_NTplotDihedral2D.py
"""

from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityError
from cing.Libs.NTplot import NTplot
from cing.Libs.NTplot import NTplotSet
from cing.Libs.NTplot import plusPoint
from cing.Libs.NTplot import useMatPlotLib
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import getDeepByKeys
from cing.PluginCode.required.reqWhatif import histJaninBySsAndResType
from cing.PluginCode.required.reqWhatif import histRamaBySsAndResType
from cing.core.classes import Project
from pylab import * #@UnusedWildImport
from unittest import TestCase
import cing
import os #@Reimport
import unittest

class AllChecks(TestCase):

    # important to switch to temp space before starting to generate files for the project.
    os.chdir(cingDirTmp)
    NTdebug("Using matplot (True) or biggles: %s", useMatPlotLib)

    def testPlotDihedral2DRama(self):
        showRestraints = False
        showDataPoints = False
        dihedralName1= "PHI"
        dihedralName2= "PSI"
        graphicsFormat = "png"

#        outputDir = os.path.join(cingDirTmp,'png')
        outputDir = cingDirTmp
        self.failIf( os.chdir(outputDir), msg=
            "Failed to change to directory for temporary test files: "+cingDirTmp)

#        ssType = 'E'
#        resType = 'GLY'
#        for ssType in histRamaBySsAndResType.keys():
#            ssTypeForFileName = ssType.replace(' ', '_')
        ssTypeFixed = 'H'
        for resType in histRamaBySsAndResType[ssTypeFixed].keys():
            if resType != 'ALA': # for testing enable filtering.
                continue

#                title = ssType + ' ' + resType
            title = resType
#            NTmessage("plotting: %s" % title)
#            hist = histRamaBySsAndResType[ssType][resType]

            ps = NTplotSet() # closes any previous plots
            ps.hardcopySize = (500, 500)

#                residueName = resType + ""
            x = NTlist(-45, -80,  125) # outside the range.
            y = NTlist(-65, -63, -125)
            # 1 SMALL boxe
            lower1, upper1 = -120.00, -125.05 # if within 0.1 they're considered the same and order shouldn't matter.
            lower2, upper2 = 0,  100
            # 4 boxes:
#            lower1, upper1 = 120,   0
#            lower2, upper2 = 130,  20
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
            project     = Project('testPlotHistoDihedral2D')
            plotparams1 = project.plotParameters.getdefault(dihedralName1,'dihedralDefault')
            plotparams2 = project.plotParameters.getdefault(dihedralName2,'dihedralDefault')

            x.limit(plotparams1.min, plotparams1.max)
            y.limit(plotparams2.min, plotparams2.max)

            plot = NTplot( title  = title,
              xRange = (plotparams1.min, plotparams1.max),
              xTicks = range(int(plotparams1.min), int(plotparams1.max+1), plotparams1.ticksize),
              xLabel = dihedralName1,
              yRange = (plotparams2.min, plotparams2.max),
              yTicks = range(int(plotparams2.min), int(plotparams2.max+1), plotparams2.ticksize),
              yLabel = dihedralName2)
            ps.addPlot(plot)

            if showRestraints:
                self.assertFalse( plot.plotDihedralRestraintRanges2D(lower1, upper1,lower2, upper2))

            # Plot a Ramachandran density background
            histList = []
            ssTypeList = histRamaBySsAndResType.keys() #@UndefinedVariable
            ssTypeList.sort() # in place sort to: space, H, S
            for ssType in ssTypeList:
#                NTdebug('appending [%s]' % ssType )
                hist = histRamaBySsAndResType[ssType][resType]
                histList.append(hist)
            self.assertFalse( plot.dihedralComboPlot(histList))
            if showDataPoints:
                myPoint = plusPoint.copy()
                myPoint.pointColor = 'green'
                myPoint.pointSize = 6.0
                myPoint.pointEdgeWidth = 1.0
                myPoint.fill = False
                if resType == 'GLY':
                    myPoint.pointType = 'triangle'
                if resType == 'PRO':
                    myPoint.pointType = 'square'
                plot.points( zip( x,y ), attributes=myPoint )
#            fn = os.path.join('bySsAndResType', ( ssTypeForFileName+"_"+resType+"."+graphicsFormat))
#            fn = os.path.join('byResType', ( resType+"."+graphicsFormat))
            fn = resType+"_rama."+graphicsFormat
            ps.hardcopy(fn, graphicsFormat)
#        plot.show()


    def tttestPlotDihedral2DJanin(self):
        showRestraints = True
        showDataPoints = True
        dihedralName1= "CHI1"
        dihedralName2= "CHI2"
        graphicsFormat = "png"

        outputDir = os.path.join(cingDirTmp,'janin')
        if not os.path.exists(outputDir):
            os.mkdir(outputDir)
#        outputDir = cingDirTmp
        self.failIf( os.chdir(outputDir), msg=
            "Failed to change to directory for temporary test files: "+outputDir)

#        ssType = 'E'
#        resType = 'GLY'
#        for ssType in histRamaBySsAndResType.keys():
#            ssTypeForFileName = ssType.replace(' ', '_')
        ssTypeFixed = 'H'
        for resType in histRamaBySsAndResType[ssTypeFixed].keys():
            if resType != 'ARG': # for testing enable filtering.
                continue

#                title = ssType + ' ' + resType
            title = resType
            NTmessage("plotting: %s" % title)
#            hist = histRamaBySsAndResType[ssType][resType]

            ps = NTplotSet() # closes any previous plots
            ps.hardcopySize = (500, 500)

#                residueName = resType + ""
            x = NTlist(-45, -80,  125) # outside the range.
            y = NTlist(-65, -63, -125)
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
            project     = Project('testPlotHistoDihedralJanin')
            plotparams1 = project.plotParameters.getdefault(dihedralName1,'dihedralDefault')
            plotparams2 = project.plotParameters.getdefault(dihedralName2,'dihedralDefault')

            x.limit(plotparams1.min, plotparams1.max)
            y.limit(plotparams2.min, plotparams2.max)

            plot = NTplot( title  = title,
              xRange = (plotparams1.min, plotparams1.max),
              xTicks = range(int(plotparams1.min), int(plotparams1.max+1), plotparams1.ticksize),
              xLabel = dihedralName1,
              yRange = (plotparams2.min, plotparams2.max),
              yTicks = range(int(plotparams2.min), int(plotparams2.max+1), plotparams2.ticksize),
              yLabel = dihedralName2)
            ps.addPlot(plot)

            if showRestraints:
                self.assertFalse( plot.plotDihedralRestraintRanges2D(lower1, upper1,lower2, upper2))

            # Plot a Ramachandran density background
            histList = []
            ssTypeList = histJaninBySsAndResType.keys() #@UndefinedVariable
            ssTypeList.sort() # in place sort to: space, H, S
            for ssType in ssTypeList:
                hist = getDeepByKeys(histJaninBySsAndResType,ssType,resType)
                if hist != None:
                    NTdebug('appending [%s]' % ssType )
                    histList.append(hist)
            if histList:
                self.assertFalse( plot.dihedralComboPlot(histList))
            if showDataPoints:
                myPoint = plusPoint.copy()
                myPoint.pointColor = 'green'
                myPoint.pointSize = 6.0
                myPoint.pointEdgeWidth = 1.0
                myPoint.fill = False
                if resType == 'GLY':
                    myPoint.pointType = 'triangle'
                if resType == 'PRO':
                    myPoint.pointType = 'square'
                plot.points( zip( x,y ), attributes=myPoint )
#            fn = os.path.join('bySsAndResType', ( ssTypeForFileName+"_"+resType+"."+graphicsFormat))
#            fn = os.path.join('byResType', ( resType+"."+graphicsFormat))
            fn = resType+"_janin."+graphicsFormat
            ps.hardcopy(fn, graphicsFormat)
#        plot.show()


if __name__ == "__main__":
    cing.verbosity = verbosityError
    cing.verbosity = verbosityDebug
    unittest.main()
