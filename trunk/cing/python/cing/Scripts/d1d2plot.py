"""
Unit test execute as:
python -u $CINGROOT/python/cing/Libs/test/test_NTplotDihedral2D.py

make sure the projects to run are already in the tmpdir.
"""

from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityError
from cing.Libs.NTplot import NTplot
from cing.Libs.NTplot import NTplotSet
from cing.Libs.NTplot import plusPoint
from cing.Libs.NTplot import solidLine
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import fprintf
from cing.Libs.NTutils import getDeepByKeys
from cing.Libs.html import HistogramsForPlotting
from cing.Libs.html import makeDihedralPlot
from cing.Libs.matplotlibExt import blue_inv
from cing.Libs.matplotlibExt import green_inv
from cing.Libs.matplotlibExt import yellow_inv
from cing.PluginCode.required.reqWhatif import BBCCHK_STR
from cing.PluginCode.required.reqWhatif import VALUE_LIST_STR
from cing.PluginCode.required.reqWhatif import WHATIF_STR
from cing.Scripts.d1d2plotConstants import BBCCHK_CUTOFF
from cing.Scripts.d1d2plotConstants import CV_CUTOFF
from cing.core.classes import Project
from cing.core.constants import DIHEDRAL_NAME_Cb4C
from cing.core.constants import DIHEDRAL_NAME_Cb4N
from cing.core.constants import IUPAC
from cing.core.database import NTdb
from cing.core.molecule import Dihedral
from cing.core.molecule import common20AAList
from matplotlib import colors
from matplotlib.pyplot import imshow
from numpy.core.defmatrix import mat
from numpy.core.fromnumeric import amax
from numpy.core.numeric import ndarray
from numpy.core.numeric import zeros
from numpy.ma.core import masked_where
from numpy.ma.core import multiply
import cing
import os
import sys

hPlot = HistogramsForPlotting()
hPlot.initHist()

# important to switch to temp space before starting to generate files for the project.
os.chdir(cingDirTmp)


def plot(entryId):
    "Arbitrary 20 bb occurrences as cuttoff for now"
    dihedralName1 = 'Cb4N'
    dihedralName2 = 'Cb4C'
    graphicsFormat = "png"

    os.chdir(cingDirTmp)
    project = Project.open(entryId, status='old')
    title = 'd1d2 all resType'

    fpGood = open(project.name + '_all_testCb2Good.out', 'w')
    fpBad = open(project.name + '_all_testCb2Bad.out', 'w')

    mCount = project.molecule.modelCount

    residueList = project.molecule.A.allResidues()
#    residueList = project.molecule.A.allResidues()[-2:-1]

    for res in residueList:
        triplet = NTlist()
        for i in [-1, 0, 1]:
            triplet.append(res.sibling(i))
        if None in triplet:
            NTdebug('Skipping because not all in triplet for %s' % res)
            continue

        bb = getDeepByKeys(res, WHATIF_STR, BBCCHK_STR, VALUE_LIST_STR, 0) # check first one.
        if bb == None:
            NTdebug('Skipping without BBCCHK values (please run What If): %s' % res)
            continue

        d1 = getDeepByKeys( res, DIHEDRAL_NAME_Cb4N)
        d2 = getDeepByKeys( res, DIHEDRAL_NAME_Cb4C)

        if d1 == None or d2 == None:
            NTdebug("Skipping residue without both dihedrals expected")
            continue

        if not ( d1.cv < CV_CUTOFF and d2.cv < CV_CUTOFF):
            NTdebug("Skipping unstructured residue (cvs %f %f): %s" % (d1.cv, d2.cv, res))
            continue

        for i in range(mCount): # Consider each model individually
            bb = getDeepByKeys(res, WHATIF_STR, BBCCHK_STR, VALUE_LIST_STR, i)
            if bb == None:
                NTerror('Skipping without BB: %s' % res)
                continue
            angles = NTlist() # store phi, psi, chi1, chi2
            for angle in ['PHI', 'PSI', 'CHI1', 'CHI2']:
                if res.has_key(angle):
                    angles.append(res[angle][i])
                else:
                    angles.append(0.0)
            if bb < BBCCHK_CUTOFF:
                fprintf(fpBad, '%4d   %7.2f  %7.2f  %7.2f  %s  %s %s\n', res.resNum, d1[i], d2[i], bb, angles.format("%7.2f  "), res, res.dssp.consensus)
            else:
                fprintf(fpGood, '%4d   %7.2f  %7.2f  %7.2f  %s  %s %s\n', res.resNum, d1[i], d2[i], bb, angles.format("%7.2f  "), res, res.dssp.consensus)
            #end if
        #end for models
        fn = "d1d2_%03d_%s." % ( res.resNum, res.resName) + graphicsFormat
#        residueHTMLfile = ResidueHTMLfile(project, res)
        ps = makeDihedralPlot( project, [res], dihedralName1, dihedralName2,
                          plotTitle = title, plotCav=False,htmlOnly=False )
        ps.hardcopy(fn, graphicsFormat)
    #        plot.show()
    #end for residues
    fpBad.close()
    fpGood.close()

    project.close(save=False)


def plotDihedral2DRama():
    showRestraints = False
    showDataPoints = False
    dihedralName1 = "PHI"
    dihedralName2 = "PSI"
    graphicsFormat = "png"

#        ssType = 'E'
#        resType = 'GLY'
#        for ssType in histRamaBySsAndResType.keys():
#            ssTypeForFileName = ssType.replace(' ', '_')
    ssTypeFixed = 'H'
    for resType in hPlot.histRamaBySsAndResType[ssTypeFixed].keys():
        if resType != 'HIS': # for testing enable filtering.
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
            if plot.plotDihedralRestraintRanges2D(lower1, upper1, lower2, upper2):
                NTerror("Failed plot.plotDihedralRestraintRanges2D")
                sys.exit(1)

        # Plot a Ramachandran density background
        histList = []
        ssTypeList = hPlot.histRamaBySsAndResType.keys() #@UndefinedVariable
        ssTypeList.sort() # in place sort to: space, H, S
        for ssType in ssTypeList:
#                NTdebug('appending [%s]' % ssType )
            hist = hPlot.histRamaBySsAndResType[ssType][resType]
            histList.append(hist)
        if plot.dihedralComboPlot(histList):
                NTerror("Failed plot.plotDihedralRestraintRanges2D -b-")
                sys.exit(1)
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


def plotDihedral2DJanin():
    showRestraints = True
    showDataPoints = True
    dihedralName1 = "CHI1"
    dihedralName2 = "CHI2"
    graphicsFormat = "png"

    outputDir = os.path.join(cingDirTmp, 'janin')
    if not os.path.exists(outputDir):
        os.mkdir(outputDir)
#        outputDir = cingDirTmp
    os.chdir(outputDir)

#        ssType = 'E'
#        resType = 'GLY'
#        for ssType in histRamaBySsAndResType.keys():
#            ssTypeForFileName = ssType.replace(' ', '_')
    ssTypeFixed = 'H'
    for resType in hPlot.histRamaBySsAndResType[ssTypeFixed].keys():
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
            plot.plotDihedralRestraintRanges2D(lower1, upper1, lower2, upper2)

        # Plot a Ramachandran density background
        histList = []
        ssTypeList = histJaninBySsAndResType.keys() #@UndefinedVariable
        ssTypeList.sort() # in place sort to: space, H, S
        for ssType in ssTypeList:
            hist = getDeepByKeys(hPlot.histJaninBySsAndResType, ssType, resType)
            if hist != None:
                NTdebug('appending [%s]' % ssType)
                histList.append(hist)
        if histList:
            if plot.dihedralComboPlot(histList):
                NTerror("Failed plot.plotDihedralRestraintRanges2D -b-")
                sys.exit(1)

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

def plotDihedralD1():
    dihedralName = 'Cb4N'
    graphicsFormat = "png"

    entryId = 'testPlotDihedralD1'

    # does it matter to import it just now?
    project = Project(entryId)
    project.removeFromDisk()
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
    y = 100.0 * hPlot.histd1 / sum(hPlot.histd1) # mod inplace
    if len(x) != len(y):
        NTerror("x was expected to be y in lenght")
        sys.exit(1)
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
        h = getDeepByKeys(hPlot.histd1BySs, ssType)
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

def plotDihedralD1_1d():
    dihedralName = 'Cb4N'
    graphicsFormat = "png"

    subDir = 'doublets'
    os.chdir(os.path.join(cingDirTmp,subDir))

    entryId = 'testPlotDihedralD1_2d'

    project = Project(entryId)
    project.removeFromDisk()
    project = Project.open(entryId, status='new')

#    interestingResTypeList = [ 'GLY' ]
    interestingResTypeList = [ 'GLY', 'ALA' ]
    for resType in common20AAList:
        for resTypePrev in common20AAList:
            if resType not in interestingResTypeList:
                continue
            if resTypePrev not in interestingResTypeList:
                continue
#            if resType != 'GLY':
#                continue
#            if resTypePrev != 'ALA':
#                continue

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

            h = getDeepByKeys(hPlot.histd1ByResTypes, resType, resTypePrev)
            if h == None:
                continue
            sumh = sum(h)
            plot.title += ' tot: %d' % sumh

            x = range(5, 360, 10)
            y = 100.0 * h / sumh # mod inplace
            points = zip(x, y)
            lAttr = solidLine(color='black' )
            plot.lines(points, attributes=lAttr)
            ssTypeList = hPlot.histd1BySs.keys() #@UndefinedVariable
            ssTypeList.sort() # in place sort to: space, H, S
            colorList = [ 'green', 'blue', 'yellow']

            for i, ssType in enumerate(ssTypeList):
                h = getDeepByKeys(hPlot.histd1BySsAndResTypes, ssType, resType, resTypePrev)
                sumh = sum(h)
                plot.title += ' %s: %d' % (ssType,sumh)
                if h == None:
                    continue
#                NTdebug('appending [%s]' % ssType)
                y = 100.0 * h / sumh
                points = zip(x, y)
                lAttr = solidLine(color=colorList[i])
                plot.lines(points, attributes=lAttr)

            fn = title + "_d1d2." + graphicsFormat
            ps.hardcopy(fn, graphicsFormat)
#        plot.show()
    project.removeFromDisk()

def plotDihedralD1_2d(doOnlyOverall = True):
    dihedralName1 = 'Cb4N'
    dihedralName2 = 'Cb4C'
    graphicsFormat = "png"


    entryId = 'testPlotDihedralD1_2d'


    if doOnlyOverall:
        subDir = 'triplets_ov'
    else:
        subDir = 'triplets'
    os.chdir(os.path.join(cingDirTmp,subDir))

    # does it matter to import it just now?
    project = Project(entryId)
    project.removeFromDisk()
    project = Project.open(entryId, status='new')

    for resType in common20AAList:
        for resTypePrev in common20AAList:
            for resTypeNext in common20AAList:
                if resType != 'VAL':
                    continue
                if resTypePrev != 'ALA':
                    continue
                if resTypeNext != 'THR':
                    continue


                # Plot a density background
                histList = []

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

                hist1 = getDeepByKeys(hPlot.histd1ByResTypes, resType, resTypePrev)
                hist2 = getDeepByKeys(hPlot.histd1ByResTypes, resType, resTypeNext)
                if hist1 == None:
                    NTdebug('skipping for hist1 is empty for [%s] [%s]' % (resType, resTypePrev))
                    continue
                if hist2 == None:
                    NTdebug('skipping for hist2 is empty for [%s] [%s]' % (resType, resTypeNext))
                    continue
                sumh1 = sum(hist1)
                sumh2 = sum(hist2)
                plot.title += ' %d-%d' % (sumh1,sumh2)
                if doOnlyOverall:
                    m1 = mat(hist1)
                    m2 = mat(hist2).transpose()
                    hist = multiply(m1,m2)
                    histList.append(hist)
                else:
                    plot.title += '\n'
                    ssTypeList = hPlot.histd1BySsAndResTypes.keys() #@UndefinedVariable
                    ssTypeList.sort() # in place sort to: space, H, S
                    for ssType in ssTypeList:
                        hist1 = getDeepByKeys(hPlot.histd1BySsAndResTypes, ssType, resType, resTypePrev)
                        hist2 = getDeepByKeys(hPlot.histd1BySsAndResTypes, ssType, resType, resTypeNext)
                        if hist1 == None:
                            NTdebug('skipping for hist1 is empty for [%s] [%s] [%s]' % (ssType, resType, resTypePrev))
                            continue
                        if hist2 == None:
                            NTdebug('skipping for hist2 is empty for [%s] [%s] [%s]' % (ssType, resType, resTypeNext))
                            continue

                        sumh1 = sum(hist1)
                        sumh2 = sum(hist2)
                        plot.title += " '%s' %d-%d" % (ssType, sumh1,sumh2)

#                        hist1 = 100.0 * hist1 / sumh1
#                        hist2 = 100.0 * hist2 / sumh2
                        m1 = mat(hist1)
                        m2 = mat(hist2).transpose()
                        hist = multiply(m1,m2)
    #                    hist = convolute(hist1, hist2)
    # TODO: why the next 3 lines?
                        l = len(hist1)
                        if ssType == ' ':
                            hist = ndarray(shape=(l, l), dtype=float, order='F')
                        histList.append(hist)
                if histList:
                    plot.dihedralComboPlot(histList, minPercentage =  3.0, maxPercentage = 10.0)
                if doOnlyOverall:
                    fn = 'ov_'
                else:
                    fn = ''
                fn += title + "_d1d2"
                fn += "." + graphicsFormat

                ps.hardcopy(fn, graphicsFormat)
    project.removeFromDisk()

def plotHistogramOverall():
    dihedralName1 = 'Cb4N'
    dihedralName2 = 'Cb4C'
    graphicsFormat = "png"
    alpha = 0.8 # was 0.8; looks awful with alpha = 1
    n = 20
    d = 3 # number of ss types.
    extent = ( 0, n ) + ( 0, n )
    minPercentage =  100.
    maxPercentage = 200.
    cmapList= [   green_inv, blue_inv, yellow_inv ]
    colorList= [ 'green',   'blue',   'yellow']
    i = 1 # decides on color picked.

    entryId = 'plotHistogramOverall'
    title = entryId
    # does it matter to import it just now?
    project = Project(entryId)
    project.removeFromDisk()
    project = Project.open(entryId, status='new')

    m = zeros((n*n), dtype=int).reshape(n,n)
    mBySs = zeros((n,n,d), dtype=int).reshape(n,n,d)
    tickList = []
    for r,resTypePrev in enumerate(common20AAList):
#        if r !=0: # for debugging.
#            continue
        db = NTdb.getResidueDefByName( resTypePrev )
        tickList.append(db.shortName)
        for c,resType in enumerate(common20AAList):
#            if c !=0:
#                continue

            hist1 = getDeepByKeys(hPlot.histd1ByResTypes, resType, resTypePrev)
            if hist1 == None:
                NTdebug('skipping for hist1 is empty for [%s] [%s]' % (resType, resTypePrev))
                continue
            sumh1 = sum(hist1)
            m[r,c] = sumh1

            ssTypeList = hPlot.histd1BySsAndResTypes.keys() #@UndefinedVariable
            ssTypeList.sort() # in place sort to: space, H, S
            for l, ssType in enumerate(ssTypeList):
                hist1 = getDeepByKeys(hPlot.histd1BySsAndResTypes, ssType, resType, resTypePrev)
                if hist1 == None:
                    NTdebug('skipping for hist1 is empty for [%s] [%s] [%s]' % (ssType, resType, resTypePrev))
                    continue
                sumh1 = sum(hist1)
                mBySs[r,c,l] = sumh1
            # end ssType
        # end

    ps = NTplotSet() # closes any previous plots
    ps.hardcopySize = (500, 500)

    plot = NTplot(title=title,
      xRange=(0., n),
      xTicks=tickList,
      xLabel=dihedralName1,
      yRange=(0., n),
      yTicks=tickList,
      yLabel=dihedralName2)
    ps.addPlot(plot)

    NTmessage('m: %s' % m)
    hist = m
    maxHist = amax(amax( hist ))
    hist *= 100./maxHist
    hist = masked_where(hist <= minPercentage, hist, copy=1)

    palette = cmapList[i]
    palette.set_under(color = 'red', alpha = 1.0 ) # alpha is 0.0
    palette.set_over( color = colorList[i], alpha = 1.0) # alpha is 1.0 Important to make it a hard alpha; last plotted will rule.
    palette.set_bad(color = 'red', alpha = 1.0 )
    norm = colors.Normalize(vmin = minPercentage,
                            vmax = maxPercentage, clip = True) # clip is False
    imshow( hist,
            interpolation=None,
#            interpolation='bicubic',
            origin='lower',
            extent=extent,
            alpha=alpha,
            cmap=palette,
            norm = norm )

    fn = title + "_d1d2." + graphicsFormat
    ps.hardcopy(fn, graphicsFormat)


def plotDihedralD1D2():
    dihedralName1 = 'Cb4N'
    dihedralName2 = 'Cb4C'
    graphicsFormat = "png"


    entryId = "1brv" # Small much studied PDB NMR entry
#        entryId = "1hy8" # small, single model, very low scoring entry

    pdbDirectory = os.path.join(cingDirTestsData, "pdb", entryId)
    pdbFileName = "pdb" + entryId + ".ent"
    pdbFilePath = os.path.join(pdbDirectory, pdbFileName)

    # does it matter to import it just now?
    project = Project(entryId)
    project.removeFromDisk()
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
    ssTypeList = hPlot.histd1d2BySsAndCombinedResType.keys() #@UndefinedVariable
    ssTypeList.sort() # in place sort to: space, H, S
    for ssType in ssTypeList:
        hist = getDeepByKeys(hPlot.histd1d2BySsAndCombinedResType, ssType)
        if hist != None:
            NTdebug('appending [%s]' % ssType)
            histList.append(hist)
    if histList:
        plot.dihedralComboPlot(histList)
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

def plotDihedralD1D2byResType():
    showDataPoints = False
    dihedralName1 = 'Cb4N'
    dihedralName2 = 'Cb4C'
    graphicsFormat = "png"

    outputDir = os.path.join(cingDirTmp, 'd1d2')
    if not os.path.exists(outputDir):
        os.mkdir(outputDir)
#        outputDir = cingDirTmp
    os.chdir(outputDir)

#        ssType = 'E'
#        resType = 'GLY'
#        for ssType in histRamaBySsAndResType.keys():
#            ssTypeForFileName = ssType.replace(' ', '_')
    ssTypeFixed = 'H'
    resTypeListSkip = ['CSB', 'GLUH', 'HISE', 'HISH', 'MSE', '', '', '', '', '']
    for resType in hPlot.histd1d2BySsAndResType[ssTypeFixed].keys():
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
        ssTypeList = hPlot.histd1d2BySsAndResType.keys() #@UndefinedVariable
        ssTypeList.sort() # in place sort to: space, H, S
        for ssType in ssTypeList:
            hist = getDeepByKeys(hPlot.histd1d2BySsAndResType, ssType, resType)
            if hist != None:
                NTdebug('appending [%s]' % ssType)
                histList.append(hist)
        if histList:
            plot.dihedralComboPlot(histList)
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
    if False:
#        entryList = "1y4o".split()
    #    entryList = "1tgq 1y4o".split()
        entryList = "1brv".split()
        for entryId in entryList:
            plot(entryId)
    if False:
        plotDihedralD1_1d()
    if False:
        for doOnlyOverall in ( True, False ):
            plotDihedralD1_2d(doOnlyOverall)
    if True:
        plotHistogramOverall()
    if False:
        plotDihedral2DRama()
