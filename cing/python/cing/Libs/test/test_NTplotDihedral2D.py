"""
Unit test execute as:
python -u $CINGROOT/python/cing/Libs/test/test_NTplotDihedral2D.py
"""

from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityError
from cing.Libs.NTplot import NTplot
from cing.Libs.NTplot import NTplotSet
from cing.Libs.NTplot import plusPoint
from cing.Libs.NTplot import solidLine
from cing.Libs.NTplot import useMatPlotLib
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import fprintf
from cing.Libs.NTutils import getDeepByKeys
from cing.PluginCode.required.reqWhatif import BBCCHK_STR
from cing.PluginCode.required.reqWhatif import VALUE_LIST_STR
from cing.PluginCode.required.reqWhatif import WHATIF_STR
from cing.PluginCode.required.reqWhatif import histJaninBySsAndResType
from cing.PluginCode.required.reqWhatif import histRamaBySsAndResType
from cing.PluginCode.required.reqWhatif import histd1
from cing.PluginCode.required.reqWhatif import histd1ByResTypes
from cing.PluginCode.required.reqWhatif import histd1BySs
from cing.PluginCode.required.reqWhatif import histd1BySsAndResTypes
from cing.PluginCode.required.reqWhatif import histd1d2BySsAndCombinedResType
from cing.PluginCode.required.reqWhatif import histd1d2BySsAndResType
from cing.core.classes import Project
from cing.core.constants import IUPAC
from cing.core.molecule import Dihedral
from cing.core.molecule import commonAAList
from pylab import * #@UnusedWildImport
from unittest import TestCase
import cing
import os #@Reimport
import unittest

def convolute(hist1, hist2):
    """Simple square multiplication; I haven't yet been able to look up the api on this in numpy.
    """
    l = len(hist1)
    h = np.ndarray(shape=(l, l), dtype=float, order='F')
    for r, r_element in enumerate(hist1):
        for c, c_element in enumerate(hist2):
            h[r][c] = r_element * c_element
    return h

class AllChecks(TestCase):

    # important to switch to temp space before starting to generate files for the project.
    os.chdir(cingDirTmp)
    NTdebug("Using matplot (True) or biggles: %s", useMatPlotLib)

    def tttestPlotDihedral2DRama(self):
        showRestraints = False
        showDataPoints = False
        dihedralName1 = "PHI"
        dihedralName2 = "PSI"
        graphicsFormat = "png"

#        outputDir = os.path.join(cingDirTmp,'png')
        outputDir = cingDirTmp
        self.failIf(os.chdir(outputDir), msg=
            "Failed to change to directory for temporary test files: " + cingDirTmp)

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
            x = NTlist(-45, -80, 125) # outside the range.
            y = NTlist(-65, -63, -125)
            # 1 SMALL boxe
            lower1, upper1 = -120.00, -125.05 # if within 0.1 they're considered the same and order shouldn't matter.
            lower2, upper2 = 0, 100
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
            project = Project('testPlotHistoDihedral2D')
            plotparams1 = project.plotParameters.getdefault(dihedralName1, 'dihedralDefault')
            plotparams2 = project.plotParameters.getdefault(dihedralName2, 'dihedralDefault')

            x.limit(plotparams1.min, plotparams1.max)
            y.limit(plotparams2.min, plotparams2.max)

            plot = NTplot(title=title,
              xRange=(plotparams1.min, plotparams1.max),
              xTicks=range(int(plotparams1.min), int(plotparams1.max + 1), plotparams1.ticksize),
              xLabel=dihedralName1,
              yRange=(plotparams2.min, plotparams2.max),
              yTicks=range(int(plotparams2.min), int(plotparams2.max + 1), plotparams2.ticksize),
              yLabel=dihedralName2)
            ps.addPlot(plot)

            if showRestraints:
                self.assertFalse(plot.plotDihedralRestraintRanges2D(lower1, upper1, lower2, upper2))

            # Plot a Ramachandran density background
            histList = []
            ssTypeList = histRamaBySsAndResType.keys() #@UndefinedVariable
            ssTypeList.sort() # in place sort to: space, H, S
            for ssType in ssTypeList:
#                NTdebug('appending [%s]' % ssType )
                hist = histRamaBySsAndResType[ssType][resType]
                histList.append(hist)
            self.assertFalse(plot.dihedralComboPlot(histList))
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
                plot.points(zip(x, y), attributes=myPoint)
#            fn = os.path.join('bySsAndResType', ( ssTypeForFileName+"_"+resType+"."+graphicsFormat))
#            fn = os.path.join('byResType', ( resType+"."+graphicsFormat))
            fn = resType + "_rama." + graphicsFormat
            ps.hardcopy(fn, graphicsFormat)
#        plot.show()


    def tttestPlotDihedral2DJanin(self):
        showRestraints = True
        showDataPoints = True
        dihedralName1 = "CHI1"
        dihedralName2 = "CHI2"
        graphicsFormat = "png"

        outputDir = os.path.join(cingDirTmp, 'janin')
        if not os.path.exists(outputDir):
            os.mkdir(outputDir)
#        outputDir = cingDirTmp
        self.failIf(os.chdir(outputDir), msg=
            "Failed to change to directory for temporary test files: " + outputDir)

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
            x = NTlist(-45, -80, 125) # outside the range.
            y = NTlist(-65, -63, -125)
            # 4 boxes:
            lower1, upper1 = 120, 0
            lower2, upper2 = 130, 20
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
            project = Project('testPlotHistoDihedralJanin')
            plotparams1 = project.plotParameters.getdefault(dihedralName1, 'dihedralDefault')
            plotparams2 = project.plotParameters.getdefault(dihedralName2, 'dihedralDefault')

            x.limit(plotparams1.min, plotparams1.max)
            y.limit(plotparams2.min, plotparams2.max)

            plot = NTplot(title=title,
              xRange=(plotparams1.min, plotparams1.max),
              xTicks=range(int(plotparams1.min), int(plotparams1.max + 1), plotparams1.ticksize),
              xLabel=dihedralName1,
              yRange=(plotparams2.min, plotparams2.max),
              yTicks=range(int(plotparams2.min), int(plotparams2.max + 1), plotparams2.ticksize),
              yLabel=dihedralName2)
            ps.addPlot(plot)

            if showRestraints:
                self.assertFalse(plot.plotDihedralRestraintRanges2D(lower1, upper1, lower2, upper2))

            # Plot a Ramachandran density background
            histList = []
            ssTypeList = histJaninBySsAndResType.keys() #@UndefinedVariable
            ssTypeList.sort() # in place sort to: space, H, S
            for ssType in ssTypeList:
                hist = getDeepByKeys(histJaninBySsAndResType, ssType, resType)
                if hist != None:
                    NTdebug('appending [%s]' % ssType)
                    histList.append(hist)
            if histList:
                self.assertFalse(plot.dihedralComboPlot(histList))
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
                plot.points(zip(x, y), attributes=myPoint)
#            fn = os.path.join('bySsAndResType', ( ssTypeForFileName+"_"+resType+"."+graphicsFormat))
#            fn = os.path.join('byResType', ( resType+"."+graphicsFormat))
            fn = resType + "_janin." + graphicsFormat
            ps.hardcopy(fn, graphicsFormat)
#        plot.show()

    def ttttestPlotDihedralD1(self):
        dihedralName = 'Cb4N'
        graphicsFormat = "png"

        entryId = 'testPlotDihedralD1'

        self.failIf(os.chdir(cingDirTmp), msg=
            "Failed to change to directory for temporary test files: " + cingDirTmp)
        # does it matter to import it just now?
        project = Project(entryId)
        self.failIf(project.removeFromDisk())
        project = Project.open(entryId, status='new')

#        for resType in commonResidueList:
#            for resTypePrev in commonResidueList:

#        ssType = 'E'
#        resType = 'GLY'
#        for ssType in histRamaBySsAndResType.keys():
#            ssTypeForFileName = ssType.replace(' ', '_')
        title = 'd1 all resType all Ss'
        NTmessage("plotting: %s" % title)

#            hist = histd1d2BySsAndResType[ssType][resType]

        # important to switch to temp space before starting to generate files for the project.
#        project     = Project('testPlotHistoDihedrald1d2')
        plotparams = project.plotParameters.getdefault(dihedralName, 'dihedralDefault')

        ps = NTplotSet() # closes any previous plots
        ps.hardcopySize = (600, 369)
        plot = NTplot(title=title,
          xRange=(plotparams.min, plotparams.max),
          yRange=(0, 50),
          xTicks=range(int(plotparams.min), int(plotparams.max + 1), plotparams.ticksize),
          xLabel=dihedralName,
          yLabel='Occurence (%)')
        ps.addPlot(plot)

        x = range(5, 360, 10)
        y = 100.0 * histd1 / sum(histd1) # mod inplace
        self.assertEqual(len(x), len(y))
        points = zip(x, y)
        NTdebug("points: %s" % points)
        NTdebug('appending [all]')
#        s = 10 # size
#        c = 'b' # color
#        cPoint   = circlePoint( color='b' )
        lAttr = solidLine()
        plot.lines(points, attributes=lAttr)
#        plot.autoScaleY( points, startAtZero=True)

        ssTypeList = histd1BySs.keys() #@UndefinedVariable
        ssTypeList.sort() # in place sort to: space, H, S
        colorList = [ 'green', 'blue', 'yellow']

        for i, ssType in enumerate(ssTypeList):
            h = getDeepByKeys(histd1BySs, ssType)
            if h == None:
                continue
            NTdebug('appending [%s]' % ssType)
            y = 100.0 * h / sum(h)
            points = zip(x, y)
            lAttr = solidLine(color=colorList[i])
            plot.lines(points, attributes=lAttr)

        fn = title + "_d1d2." + graphicsFormat
        ps.hardcopy(fn, graphicsFormat)
#        plot.show()

    def ttttestPlotDihedralD1_1d(self):
        dihedralName = 'Cb4N'
        graphicsFormat = "png"

        entryId = 'testPlotDihedralD1_2d'

        self.failIf(os.chdir(cingDirTmp), msg=
            "Failed to change to directory for temporary test files: " + cingDirTmp)
        # does it matter to import it just now?
        project = Project(entryId)
        self.failIf(project.removeFromDisk())
        project = Project.open(entryId, status='new')


        for resType in commonAAList:
            for resTypePrev in commonAAList:
#                if resType != 'ALA':
#                    continue
#                if resTypePrev != 'ARG':
#                    continue
                title = 'd1 %s %s' % (resType, resTypePrev)
                NTmessage("plotting: %s" % title)

                plotparams = project.plotParameters.getdefault(dihedralName, 'dihedralDefault')

                ps = NTplotSet() # closes any previous plots
                ps.hardcopySize = (600, 369)
                plot = NTplot(title=title,
                  xRange=(plotparams.min, plotparams.max),
                  yRange=(0, 50),
                  xTicks=range(int(plotparams.min), int(plotparams.max + 1), plotparams.ticksize),
                  xLabel=dihedralName,
                  yLabel='Occurrence (%)')
                ps.addPlot(plot)

                h = getDeepByKeys(histd1ByResTypes, resType, resTypePrev)
                if h == None:
                    continue

                x = range(5, 360, 10)
                y = 100.0 * h / sum(h) # mod inplace
                self.assertEqual(len(x), len(y))
                points = zip(x, y)
                plot.lines(points, attributes=solidLine())
                ssTypeList = histd1BySs.keys() #@UndefinedVariable
                ssTypeList.sort() # in place sort to: space, H, S
                colorList = [ 'green', 'blue', 'yellow']

                for i, ssType in enumerate(ssTypeList):
                    h = getDeepByKeys(histd1BySsAndResTypes, ssType, resType, resTypePrev)
                    if h == None:
                        continue
                    NTdebug('appending [%s]' % ssType)
                    y = 100.0 * h / sum(h)
                    points = zip(x, y)
                    lAttr = solidLine(color=colorList[i])
                    plot.lines(points, attributes=lAttr)

                fn = title + "_d1d2." + graphicsFormat
                ps.hardcopy(fn, graphicsFormat)
#        plot.show()


    def tttestConvolute(self):
        hist1 = [ 0, 1, 2]
        hist2 = [10, 21, 22]
        NTdebug("%s" % convolute(hist1, hist2))

    def tttestPlotDihedralD1_2d(self):
        dihedralName1 = 'Cb4N'
        dihedralName2 = 'Cb4C'
        graphicsFormat = "png"

        entryId = 'testPlotDihedralD1_2dB'

        self.failIf(os.chdir(cingDirTmp), msg=
            "Failed to change to directory for temporary test files: " + cingDirTmp)
        # does it matter to import it just now?
        project = Project(entryId)
        self.failIf(project.removeFromDisk())
        project = Project.open(entryId, status='new')


        for resType in commonAAList:
            for resTypePrev in commonAAList:
                for resTypeNext in commonAAList:
                    if resType != 'ALA':
                        continue
#                    if resTypePrev != 'ALA':
#                        continue
#                    if resTypeNext != 'ALA':
#                        continue
                    title = 'd1d2B %s-%s-%s' % (resTypePrev, resType, resTypeNext)
                    NTmessage("plotting: %s" % title)

                    ps = NTplotSet() # closes any previous plots
                    ps.hardcopySize = (500, 500)

    #        #                residueName = resType + ""
    #                x = NTlist(-45, -80,  125) # outside the range.
    #                y = NTlist(-65, -63, -125)

                    # important to switch to temp space before starting to generate files for the project.
            #        project     = Project('testPlotHistoDihedrald1d2')
                    plotparams1 = project.plotParameters.getdefault(dihedralName1, 'dihedralDefault')
                    plotparams2 = project.plotParameters.getdefault(dihedralName2, 'dihedralDefault')

    #                x.limit(plotparams1.min, plotparams1.max)
    #                y.limit(plotparams2.min, plotparams2.max)

                    plot = NTplot(title=title,
                      xRange=(plotparams1.min, plotparams1.max),
                      xTicks=range(int(plotparams1.min), int(plotparams1.max + 1), plotparams1.ticksize),
                      xLabel=dihedralName1,
                      yRange=(plotparams2.min, plotparams2.max),
                      yTicks=range(int(plotparams2.min), int(plotparams2.max + 1), plotparams2.ticksize),
                      yLabel=dihedralName2)
                    ps.addPlot(plot)

                    # Plot a density background
                    histList = []
                    hist1 = getDeepByKeys(histd1ByResTypes, resType, resTypePrev)
                    hist2 = getDeepByKeys(histd1ByResTypes, resType, resTypeNext)
                    if hist1 == None:
                        NTdebug('skipping for hist1 is empty for [%s] [%s]' % (resType, resTypePrev))
                        continue
                    if hist2 == None:
                        NTdebug('skipping for hist2 is empty for [%s] [%s]' % (resType, resTypeNext))
                        continue
                    hist1 = 100.0 * hist1 / sum(hist1)
                    hist2 = 100.0 * hist2 / sum(hist2)

#                        hist = None # TODO: convolute here
                    hist = convolute(hist1, hist2)
                    histList.append(hist)
                    if histList:
                        self.assertFalse(plot.dihedralComboPlot(histList))
                    fn = title + "_d1d2." + graphicsFormat
                    ps.hardcopy(fn, graphicsFormat)

    def ttttestPlotDihedralD1_2d(self):
        dihedralName1 = 'Cb4N'
        dihedralName2 = 'Cb4C'
        graphicsFormat = "png"

        entryId = 'testPlotDihedralD1_2d'

        self.failIf(os.chdir(cingDirTmp), msg=
            "Failed to change to directory for temporary test files: " + cingDirTmp)
        # does it matter to import it just now?
        project = Project(entryId)
        self.failIf(project.removeFromDisk())
        project = Project.open(entryId, status='new')


        for resType in commonAAList:
            for resTypePrev in commonAAList:
                for resTypeNext in commonAAList:
                    if resType != 'ALA':
                        continue
                    if resTypePrev != 'ALA':
                        continue
#                    if resTypeNext != 'ALA':
#                        continue
                    title = 'd1d2 %s-%s-%s' % (resTypePrev, resType, resTypeNext)
                    NTmessage("plotting: %s" % title)

                    ps = NTplotSet() # closes any previous plots
                    ps.hardcopySize = (500, 500)

    #        #                residueName = resType + ""
    #                x = NTlist(-45, -80,  125) # outside the range.
    #                y = NTlist(-65, -63, -125)

                    # important to switch to temp space before starting to generate files for the project.
            #        project     = Project('testPlotHistoDihedrald1d2')
                    plotparams1 = project.plotParameters.getdefault(dihedralName1, 'dihedralDefault')
                    plotparams2 = project.plotParameters.getdefault(dihedralName2, 'dihedralDefault')

    #                x.limit(plotparams1.min, plotparams1.max)
    #                y.limit(plotparams2.min, plotparams2.max)

                    plot = NTplot(title=title,
                      xRange=(plotparams1.min, plotparams1.max),
                      xTicks=range(int(plotparams1.min), int(plotparams1.max + 1), plotparams1.ticksize),
                      xLabel=dihedralName1,
                      yRange=(plotparams2.min, plotparams2.max),
                      yTicks=range(int(plotparams2.min), int(plotparams2.max + 1), plotparams2.ticksize),
                      yLabel=dihedralName2)
                    ps.addPlot(plot)

                    # Plot a density background
                    histList = []
                    ssTypeList = histd1BySsAndResTypes.keys() #@UndefinedVariable
                    ssTypeList.sort() # in place sort to: space, H, S
                    for ssType in ssTypeList:

                        hist1 = getDeepByKeys(histd1BySsAndResTypes, ssType, resType, resTypePrev)
                        hist2 = getDeepByKeys(histd1BySsAndResTypes, ssType, resType, resTypeNext)
                        if hist1 == None:
                            NTdebug('skipping for hist1 is empty for [%s] [%s] [%s]' % (ssType, resType, resTypePrev))
                            continue
                        if hist2 == None:
                            NTdebug('skipping for hist2 is empty for [%s] [%s] [%s]' % (ssType, resType, resTypeNext))
                            continue
                        hist1 = 100.0 * hist1 / sum(hist1)
                        hist2 = 100.0 * hist2 / sum(hist2)

#                        hist = None # TODO: convolute here
                        hist = convolute(hist1, hist2)
                        l = len(hist1)
                        if ssType == ' ':
                            hist = np.ndarray(shape=(l, l), dtype=float, order='F')
                        histList.append(hist)
                    if histList:
                        self.assertFalse(plot.dihedralComboPlot(histList))
                    fn = title + "_d1d2." + graphicsFormat
                    ps.hardcopy(fn, graphicsFormat)


    def ttttestPlotDihedralD1D2(self):
        dihedralName1 = 'Cb4N'
        dihedralName2 = 'Cb4C'
        graphicsFormat = "png"


        entryId = "1brv" # Small much studied PDB NMR entry
#        entryId = "1hy8" # small, single model, very low scoring entry

        pdbDirectory = os.path.join(cingDirTestsData, "pdb", entryId)
        pdbFileName = "pdb" + entryId + ".ent"
        pdbFilePath = os.path.join(pdbDirectory, pdbFileName)

        self.failIf(os.chdir(cingDirTmp), msg=
            "Failed to change to directory for temporary test files: " + cingDirTmp)
        # does it matter to import it just now?
        project = Project(entryId)
        self.failIf(project.removeFromDisk())
        project = Project.open(entryId, status='new')
        project.initPDB(pdbFile=pdbFilePath, convention=IUPAC)

#        ssType = 'E'
#        resType = 'GLY'
#        for ssType in histRamaBySsAndResType.keys():
#            ssTypeForFileName = ssType.replace(' ', '_')
        title = 'd1d2 all resType'
        NTmessage("plotting: %s" % title)
#            hist = histd1d2BySsAndResType[ssType][resType]

        ps = NTplotSet() # closes any previous plots
        ps.hardcopySize = (500, 500)

#                residueName = resType + ""
        x = NTlist(-45, -80, 125) # outside the range.
        y = NTlist(-65, -63, -125)

        # important to switch to temp space before starting to generate files for the project.
#        project     = Project('testPlotHistoDihedrald1d2')
        plotparams1 = project.plotParameters.getdefault(dihedralName1, 'dihedralDefault')
        plotparams2 = project.plotParameters.getdefault(dihedralName2, 'dihedralDefault')

        x.limit(plotparams1.min, plotparams1.max)
        y.limit(plotparams2.min, plotparams2.max)

        plot = NTplot(title=title,
          xRange=(plotparams1.min, plotparams1.max),
          xTicks=range(int(plotparams1.min), int(plotparams1.max + 1), plotparams1.ticksize),
          xLabel=dihedralName1,
          yRange=(plotparams2.min, plotparams2.max),
          yTicks=range(int(plotparams2.min), int(plotparams2.max + 1), plotparams2.ticksize),
          yLabel=dihedralName2)
        ps.addPlot(plot)

        # Plot a density background
        histList = []
        ssTypeList = histd1d2BySsAndCombinedResType.keys() #@UndefinedVariable
        ssTypeList.sort() # in place sort to: space, H, S
        for ssType in ssTypeList:
            hist = getDeepByKeys(histd1d2BySsAndCombinedResType, ssType)
            if hist != None:
                NTdebug('appending [%s]' % ssType)
                histList.append(hist)
        if histList:
            self.assertFalse(plot.dihedralComboPlot(histList))
#            fn = os.path.join('bySsAndResType', ( ssTypeForFileName+"_"+resType+"."+graphicsFormat))
 #            fn = os.path.join('byResType', ( resType+"."+graphicsFormat))


        fpGood = open(project.name + '.testCb2Good.out', 'w')
        fpBad = open(project.name + '.testCb2Bad.out', 'w')

        mCount = project.molecule.modelCount

        for res in project.molecule.A.allResidues():
            triplet = NTlist()
            for i in [-1, 0, 1]:
                triplet.append(res.sibling(i))
            if None in triplet:
                NTdebug('Skipping ' % res)

            else:
                CA_atms = triplet.zap('CA')
                CB_atms = triplet.zap('CB')

                NTdebug("%s %s %s %s" % (res, triplet, CA_atms, CB_atms))

                if None in CB_atms: # skip Gly for now
                    NTdebug('Skipping %s' % res)
                else:
                    d1 = Dihedral(res, 'Cb4N', range=[0.0, 360.0])
                    d1.atoms = [CB_atms[0], CA_atms[0], CA_atms[1], CB_atms[1]]
                    d1.calculateValues()
                    res['Cb4N'] = d1 # append dihedral to residue

                    d2 = Dihedral(res, 'Cb4C', range=[0.0, 360.0])
                    d2.atoms = [CB_atms[1], CA_atms[1], CA_atms[2], CB_atms[2]]
                    d2.calculateValues()
                    res['Cb4C'] = d2 # append dihedral to residue

                    bb = getDeepByKeys(res, WHATIF_STR, BBCCHK_STR, VALUE_LIST_STR, 0) # check first one.
                    if bb == None:
                        NTdebug('Skipping without BB %s' % res)
                        continue

                    if d1.cv < 0.03 and d2.cv < 0.03: # Only include structured residues
                        for i in range(mCount): # Consider each model individually
        #                    bb = res.Whatif.bbNormality.valueList[i]
                            bb = getDeepByKeys(res, WHATIF_STR, BBCCHK_STR, VALUE_LIST_STR, i)
                            if bb == None:
                                NTdebug('Skipping without BB %s' % res)
                                continue
                            angles = NTlist() # store phi, psi, chi1, chi2
                            for angle in ['PHI', 'PSI', 'CHI1', 'CHI2']:
                                if res.has_key(angle):
                                    angles.append(res[angle][i])
                                else:
                                    angles.append(0.0)
                            #end for
                            if bb < 20.0: # Arbitrary 20 bb occurences as cuttoff for now
                                fprintf(fpBad, '%4d   %7.2f  %7.2f  %7.2f  %s  %s %s\n', res.resNum, d1[i], d2[i], bb, angles.format("%7.2f  "), res, res.dssp.consensus)
                            else:
                                fprintf(fpGood, '%4d   %7.2f  %7.2f  %7.2f  %s  %s %s\n', res.resNum, d1[i], d2[i], bb, angles.format("%7.2f  "), res, res.dssp.consensus)
                    #end if
                #end if
            #end if
        #end for
        fpBad.close()
        fpGood.close()

        fn = "allRestype_d1d2." + graphicsFormat
        ps.hardcopy(fn, graphicsFormat)
#        plot.show()

    def tttestPlotDihedralD1D2byResType(self):
        showDataPoints = False
        dihedralName1 = 'Cb4N'
        dihedralName2 = 'Cb4C'
        graphicsFormat = "png"

        outputDir = os.path.join(cingDirTmp, 'd1d2')
        if not os.path.exists(outputDir):
            os.mkdir(outputDir)
#        outputDir = cingDirTmp
        self.failIf(os.chdir(outputDir), msg=
            "Failed to change to directory for temporary test files: " + outputDir)

#        ssType = 'E'
#        resType = 'GLY'
#        for ssType in histRamaBySsAndResType.keys():
#            ssTypeForFileName = ssType.replace(' ', '_')
        ssTypeFixed = 'H'
        resTypeListSkip = ['CSB', 'GLUH', 'HISE', 'HISH', 'MSE', '', '', '', '', '']
        for resType in histd1d2BySsAndResType[ssTypeFixed].keys():
#            if resType != 'ARG': # for testing enable filtering.
#                continue
            if resType in resTypeListSkip:
                continue
            title = 'd1d2 ' + resType
            NTmessage("plotting: %s" % title)
#            hist = histd1d2BySsAndResType[ssType][resType]

            ps = NTplotSet() # closes any previous plots
            ps.hardcopySize = (500, 500)

#                residueName = resType + ""
            x = NTlist(-45, -80, 125) # outside the range.
            y = NTlist(-65, -63, -125)

            # important to switch to temp space before starting to generate files for the project.
            project = Project('testPlotHistoDihedrald1d2')
            plotparams1 = project.plotParameters.getdefault(dihedralName1, 'dihedralDefault')
            plotparams2 = project.plotParameters.getdefault(dihedralName2, 'dihedralDefault')

            x.limit(plotparams1.min, plotparams1.max)
            y.limit(plotparams2.min, plotparams2.max)

            plot = NTplot(title=title,
              xRange=(plotparams1.min, plotparams1.max),
              xTicks=range(int(plotparams1.min), int(plotparams1.max + 1), plotparams1.ticksize),
              xLabel=dihedralName1,
              yRange=(plotparams2.min, plotparams2.max),
              yTicks=range(int(plotparams2.min), int(plotparams2.max + 1), plotparams2.ticksize),
              yLabel=dihedralName2)
            ps.addPlot(plot)

            # Plot a density background
            histList = []
            ssTypeList = histd1d2BySsAndResType.keys() #@UndefinedVariable
            ssTypeList.sort() # in place sort to: space, H, S
            for ssType in ssTypeList:
                hist = getDeepByKeys(histd1d2BySsAndResType, ssType, resType)
                if hist != None:
                    NTdebug('appending [%s]' % ssType)
                    histList.append(hist)
            if histList:
                self.assertFalse(plot.dihedralComboPlot(histList))
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
                plot.points(zip(x, y), attributes=myPoint)
#            fn = os.path.join('bySsAndResType', ( ssTypeForFileName+"_"+resType+"."+graphicsFormat))
#            fn = os.path.join('byResType', ( resType+"."+graphicsFormat))
            fn = resType + "_d1d2." + graphicsFormat
            ps.hardcopy(fn, graphicsFormat)
#        plot.show()


if __name__ == "__main__":
    cing.verbosity = verbosityError
    cing.verbosity = verbosityDebug
    unittest.main()
