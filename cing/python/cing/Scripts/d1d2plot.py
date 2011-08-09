"""
Execute as:
python -u $CINGROOT/python/cing/Scripts/d1d2plot.py

Please make sure the projects to run are already in the tmpdir.
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTplot import * #@UnusedWildImport
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.html import hPlot
from cing.Libs.html import makeDihedralPlot
from cing.Libs.test.test_NTplot2 import plotTestHistoDihedral
from cing.PluginCode.matplib import * #@UnresolvedImport @UnusedWildImport
from cing.PluginCode.required.reqWhatif import * #@UnusedWildImport
from cing.Scripts.d1d2plotConstants import BBCCHK_CUTOFF
from cing.Scripts.d1d2plotConstants import CV_CUTOFF
from cing.core.classes import Project
from cing.core.constants import * #@UnusedWildImport
from cing.core.database import NTdb
from cing.core.molecule import Dihedral
from cing.core.molecule import common20AAList
from cing.core.molecule import getTripletHistogramList
from matplotlib.pylab import * #@UnusedWildImport for most imports
from numpy.ma.core import masked_where
import numpy
import profile
import pstats


dihedralName1 = 'Cb4N'
dihedralName2 = 'Cb4C'

rootDir = '/Users/jd/workspace/d1d2project'
reportsDir = os.path.join(rootDir, 'reports')
#plotHistogramBySsTypeResidueTypesDir = os.path.join(rootDir, 'plotHistogramBySsTypeResidueTypesNoNormalizing')
plotHistogramBySsTypeResidueTypesDir = os.path.join(rootDir, 'plotHistogramBySsTypeResidueTypesNew')
tripletsOvDir = os.path.join(rootDir, 'triplets_ov')
doubletsDir = os.path.join(rootDir, 'doublets')

if hPlot.histRamaBySsAndCombinedResType == None:
    hPlot.initHist()
set_printoptions(linewidth=100000)

# In some plots a specific directory is switched to first.
os.chdir(cingDirTmp) #


def plotForEntry(entryId):
    "Arbitrary 20 bb occurrences as cuttoff for now"
    dihedralName1 = 'Cb4N'
    dihedralName2 = 'Cb4C'
    graphicsFormat = "png"

    os.chdir(cingDirTmp)
    project = Project.open(entryId, status='old')
#    titleStr = 'd1d2 all resType'

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
            nTmessage('Skipping because not all in triplet for %s' % res)
            continue

#        bb = getDeepByKeys(res, WHATIF_STR, BBCCHK_STR, VALUE_LIST_STR, 0) # check first one.
#        if bb == None:
#            nTmessage('Skipping without BBCCHK values (please run What If): %s' % res)
#            continue

        d1 = getDeepByKeys(res, DIHEDRAL_NAME_Cb4N)
        d2 = getDeepByKeys(res, DIHEDRAL_NAME_Cb4C)

        if d1 == None or d2 == None:
            nTmessage("Skipping residue without both dihedrals expected")
            continue

        if d1.cv == None or d2.cv == None:
            nTmessage("Skipping unstructured residue: %s" % res)
            continue
        if not (d1.cv < CV_CUTOFF and d2.cv < CV_CUTOFF):
            nTmessage("Skipping unstructured residue (cvs %f %f): %s" % (d1.cv, d2.cv, res))
            continue

        for i in range(mCount): # Consider each model individually
            bb = getDeepByKeys(res, WHATIF_STR, BBCCHK_STR, VALUE_LIST_STR, i)
            if bb == None:
                nTmessage('Skipping without BB: %s' % res)
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
        fn = "d1d2_%03d_%s." % (res.resNum, res.resName) + graphicsFormat
#        residueHTMLfile = ResidueHTMLfile(project, res)
        ps = makeDihedralPlot(project, [res], dihedralName1, dihedralName2,
#                          plotTitle = titleStr,
                          plotCav=False, htmlOnly=False)
        if ps:
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
        if resType != 'ALA': # for testing enable filtering.
            continue

#                titleStr = ssType + ' ' + resType
        titleStr = resType
#            nTmessage("plotting: %s" % titleStr)
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

        plot = NTplot(title=titleStr,
          xRange=(plotparams1.min, plotparams1.max),
          xTicks=range(int(plotparams1.min), int(plotparams1.max + 1), plotparams1.ticksize),
          xLabel=dihedralName1,
          yRange=(plotparams2.min, plotparams2.max),
          yTicks=range(int(plotparams2.min), int(plotparams2.max + 1), plotparams2.ticksize),
          yLabel=dihedralName2)
        ps.addPlot(plot)

        if showRestraints:
            if plot.plotDihedralRestraintRanges2D(lower1, upper1, lower2, upper2):
                nTerror("Failed plot.plotDihedralRestraintRanges2D")
                sys.exit(1)

        # Plot a Ramachandran density background
        histList = []
        ssTypeList = hPlot.histRamaBySsAndResType.keys() #@UndefinedVariable
        ssTypeList.sort() # in place sort to: space, H, S
        for ssType in ssTypeList:
#                nTdebug('appending [%s]' % ssType )
            hist = hPlot.histRamaBySsAndResType[ssType][resType]
            histList.append(hist)
        if plot.dihedralComboPlot(histList):
            nTerror("Failed plot.plotDihedralRestraintRanges2D -b-")
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
#        fn = resType + "_rama." + graphicsFormat
        fnBase = resType + "_rama"
        if True:
            fn = fnBase + '.png'
        else:
            i = 0
            fn = None
            while not fn or os.path.exists(fn):
                i += 1
                fn = fnBase + '_' + str(i) + '.png'
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

#                titleStr = ssType + ' ' + resType
        titleStr = resType
        nTmessage("plotting: %s" % titleStr)
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

        plot = NTplot(title=titleStr,
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
                nTdebug('appending [%s]' % ssType)
                histList.append(hist)
        if histList:
            if plot.dihedralComboPlot(histList):
                nTerror("Failed plot.plotDihedralRestraintRanges2D -b-")
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

#        plot.show()

def plotDihedralD1_1d():
    dihedralName = 'Cb4N'
    graphicsFormat = "png"

    nTmessage("Starting plotDihedralD1_1d")
#    interestingResTypeList = [ 'GLY' ]
    interestingResTypeList = common20AAList
#    interestingResTypeList = [ 'GLY', 'ALA' ]
#    interestingResTypeList = [ 'CYS', 'PRO' ]
    for resType in common20AAList:
        for resTypePrev in common20AAList:
#                nTmessage("Looking at %s %s" % ( resType, resTypePrev))
            if resType not in interestingResTypeList:
                continue
            if resTypePrev not in interestingResTypeList:
                continue
            if resType != 'GLY':
                continue
#                if resTypePrev != 'ALA':
#                    continue

            titleStr = 'd1 %s(i-1) %s(i)' % (resTypePrev, resType)
            nTmessage("plotting: %s" % titleStr)

            plotparams = plotParameters.getdefault(dihedralName, 'dihedralDefault')

            ps = NTplotSet() # closes any previous plots
            ps.hardcopySize = (600, 369)
            plot = NTplot(title=titleStr,
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
            lAttr = solidLine(color='black')
            plot.lines(points, attributes=lAttr)
            ssTypeList = hPlot.histd1BySs0.keys()
            ssTypeList.sort() # in place sort to: space, H, S
            colorList = [ 'green', 'blue', 'yellow']

            for isI in (1, 0):
                if isI:
#                    histd1BySs = hPlot.histd1BySs0
                    histd1BySsAndResTypes = hPlot.histd1BySs0AndResTypes
                else:
#                    histd1BySs = hPlot.histd1BySs1
                    histd1BySsAndResTypes = hPlot.histd1BySs1AndResTypes

                for i, ssType in enumerate(ssTypeList):
                    h = getDeepByKeys(histd1BySsAndResTypes, ssType, resType, resTypePrev)
                    sumh = sum(h)
                    plot.title += ' %s: %d' % (ssType, sumh)
                    if h == None:
                        continue
    #                nTdebug('appending [%s]' % ssType)
                    y = 100.0 * h / sumh
                    points = zip(x, y)
                    lAttr = solidLine(color=colorList[i])
                    plot.lines(points, attributes=lAttr)

            fn = "d1 %s %s_d1d2." % (resTypePrev, resType)
            fn += graphicsFormat
            ps.hardcopy(fn, graphicsFormat)
#        plot.show()

def plotDihedralD1_2d(doOnlyOverall=True):
    graphicsFormat = "png"
#    minPercentage = MIN_Z_D1D2
#    maxPercentage = MAX_Z_D1D2
#                scaleBy = SCALE_BY_Z
    minPercentage = MIN_PERCENTAGE_D1D2
    maxPercentage = MAX_PERCENTAGE_D1D2
    scaleBy = SCALE_BY_SUM

    for resType in common20AAList:
        for resTypePrev in common20AAList:
            for resTypeNext in common20AAList:
                if resType != 'PHE':
                    continue
                if resTypePrev != 'SER':
                    continue
                if resTypeNext != 'VAL':
                    continue

                # Plot a density background
                histList = []
                resTypeListBySequenceOrder = [ resTypePrev, resType, resTypeNext ]
                titleStr = 'd1d2 %s-%s-%s' % ( resTypePrev, resType, resTypeNext )
#                nTmessage("plotting: %s" % titleStr)

                # important to switch to temp space before starting to generate files for the project.
        #        project     = Project('testPlotHistoDihedrald1d2')
                plotparams1 = plotParameters.getdefault(dihedralName1, 'dihedralDefault')
                plotparams2 = plotParameters.getdefault(dihedralName2, 'dihedralDefault')

                hist1 = getDeepByKeys(hPlot.histd1ByResTypes, resType, resTypePrev) #
                hist2 = getDeepByKeys(hPlot.histd1ByResTypes, resTypeNext, resType) #L
                if hist1 == None:
                    nTdebug('skipping for hist1 is empty for [%s] [%s]' % (resType, resTypePrev))
                    continue
                if hist2 == None:
                    nTdebug('skipping for hist2 is empty for [%s] [%s]' % (resType, resTypeNext))
                    continue
                sumh1 = sum(hist1)
                sumh2 = sum(hist2)
                titleStr += ' %d-%d' % (sumh1, sumh2)
#                if doOnlyOverall:
                histList = getTripletHistogramList(resTypeListBySequenceOrder, doOnlyOverall = doOnlyOverall, ssTypeRequested = None, doNormalize = False, normalizeSeparatelyToZ = False)

#                else:
#                    titleStr += '\n'
#                    histList = getTripletHistogramList(resTypeListBySequenceOrder, doOnlyOverall = doOnlyOverall, ssTypeRequested = None, doNormalize = True, normalizeSeparatelyToZ = True)
#                    scaleBy = SCALE_BY_ONE


                ps = NTplotSet() # closes any previous plots
                ps.hardcopySize = (500, 500)

                myplot = NTplot(title=titleStr,
                  xRange=(plotparams1.min, plotparams1.max),
                  xTicks=range(int(plotparams1.min), int(plotparams1.max + 1), plotparams1.ticksize),
                  xLabel=dihedralName1,
                  yRange=(plotparams2.min, plotparams2.max),
                  yTicks=range(int(plotparams2.min), int(plotparams2.max + 1), plotparams2.ticksize),
                  yLabel=dihedralName2)
                ps.addPlot(myplot)

                myplot.dihedralComboPlot(histList, minPercentage=minPercentage, maxPercentage=maxPercentage, scaleBy=scaleBy)

                fn = 'd1d2_%s-%s-%s' % (resTypePrev, resType, resTypeNext)
                if doOnlyOverall:
                    fn += '_ov_'
                fn += "." + graphicsFormat
#                savefig(fn)

                ps.hardcopy(fn, graphicsFormat)

def plotHistogramOverall():
    graphicsFormat = "png"
    alpha = 0.8 # was 0.8; looks awful with alpha = 1
    n = 20
#    d = 3 # number of ss types.
    extent = (0, n) + (0, n)
    cmapList = [   green_inv, blue_inv, yellow_inv ]
    colorList = [ 'green', 'blue', 'yellow']
    i = 1 # decides on color picked.

    # If set it will do a single ssType otherwise the overall.
    for doOverall in [ False, True ]:
#    for doOverall in [ True ]:
        if doOverall:
            ssTypeList = [ None ]
        else:
            ssTypeList = [' ', 'S', 'H']

        for ssType in ssTypeList:
            m = zeros((n * n), dtype=int).reshape(n, n)
        #    mBySs = zeros((n,n,d), dtype=int).reshape(n,n,d)
            tickList = [ NTdb.getResidueDefByName(resType).shortName for resType in common20AAList]
    #        tickListRev = tickList[:]
    #        tickListRev.reverse()
            for r, resTypePrev in enumerate(common20AAList):
                for c, resType in enumerate(common20AAList):
                    if doOverall:
                        hist1 = getDeepByKeys(hPlot.histd1ByResTypes, resType, resTypePrev)
                    else:
                        hist1 = getDeepByKeys(hPlot.histd1BySs0AndResTypes, ssType, resType, resTypePrev)
                    if hist1 == None:
                        nTdebug('skipping for hist1 is empty for [%s] [%s]' % (resType, resTypePrev))
                        continue
                    m[r, c] = sum(hist1)

            clf()

#            axes([.1, .1, .8, .8 ] )
            xlabel('resType')
            ylabel('resTypePrev')
            xlim((0, n))
            ylim((0, n))
            offset = 0.5
            xticks(arange(offset, n), tickList)
            yticks(arange(offset, n), tickList)
#            print 'just before call to set_ticks_position'
    #        axis.xaxis.set_ticks_position('top')
    #        axis.xaxis.set_label_position('top')
        #    axis.yaxis.set_ticks_position('both')
        #    axis.yaxis.set_label_position('left')
            grid(True)
            strTitle = "ssType: [%s]" % ssType
            title(strTitle)
            plot([0, n], [0, n], 'b-', linewidth=1)
            minCount = 300.
            maxCount = 1000.
            if False:
                minCount = 0.
                maxCount = 1.
            if ssType:
                minCount /= 3.
                maxCount /= 3.
            maxHist = amax(m)
            minHist = amin(m)
            sumHist = sum(m)
            nTmessage('ssType: %s' % ssType)
            nTmessage('maxHist: %s' % maxHist) # 9165 of total of ~ 1 M.
            nTmessage('minHist: %s' % minHist) # 210
            nTmessage('sumHist: %s' % sumHist) # 210
#            nTmessage('tickList: %s' % tickList) # 210
        #    his *= 100./maxHist
            his = masked_where(m <= minCount, m, copy=1)

            palette = cmapList[i]
            palette.set_under(color='red', alpha=1.0) # alpha is 0.0
            palette.set_over(color=colorList[i], alpha=1.0) # alpha is 1.0 Important to make it a hard alpha; last plotted will rule.
            palette.set_bad(color='red', alpha=1.0)


            norm = Normalize(vmin=minCount, vmax=maxCount, clip=True) # clip is False
            imshow(his,
                    interpolation='nearest',
        #            interpolation='bicubic',
                    origin='lower',
                    extent=extent,
                    alpha=alpha,
                    cmap=palette,
                    norm=norm)
#            mr = m[::-1] # reverses the rows, nice!
#            nTmessage('mr: %s' % mr)

            fn = "plotHistogram_%s_d1d2.%s" % (ssType, graphicsFormat)
            savefig(fn)

            clf()
            l = m.reshape(n * n)
            hist(l, 20)
            xlabel('pair count')
            ylabel('number of occurrences')
            title(strTitle)
            fn = "plotHistOfHist_%s_d1d2.%s" % (ssType, graphicsFormat)
            savefig(fn)

        # end loop over ssType
    # end over ssType overall
    return m


def plotHistogramBySsTypeResidueTypes():
    graphicsFormat = "png"

    doOnlyOverall = False
    # If set it will do a single ssType otherwise the overall.
#    for doOverall in [ False, True ]:
    for doOverall in [ True ]:
        if doOverall:
            ssTypeList = [ None ]
        else:
            ssTypeList = [' ', 'S', 'H']
        for ssType in ssTypeList:
#met-asp-leu
            for _i, resType in enumerate(common20AAList):
                if resType != 'PHE':
                    continue
                for _j, resTypePrev in enumerate(common20AAList):
                    if resTypePrev != 'SER':
                        continue
                    for _k, resTypeNext in enumerate(common20AAList):
                        if resTypeNext != 'VAL':
                            continue
                        resTypeListBySequenceOrder = (resTypePrev, resType , resTypeNext)
                        myHistList = getTripletHistogramList(resTypeListBySequenceOrder, doOnlyOverall=doOnlyOverall, ssTypeRequested=ssType, doNormalize = True)
                        if myHistList == None:
                            nTwarning("Encountered an error getting the D1D2 hist for %s; skipping" % str(resTypeListBySequenceOrder))
                            continue
                        if len(myHistList) != 1:
                            nTdebug("Expected exactly one but Found %s histogram for %s; skipping" % (len(myHistList), str(resTypeListBySequenceOrder)))
                            continue
                        myHist = deepcopy(myHistList[0])
#                        nTdebug("myHist: %s" % str(myHist))

                        myList = numpy.asarray(myHist).flatten()
                        maxl = numpy.max(myList)
                        sdl = numpy.std(myList)
                        avl = numpy.average(myList)
                        suml = numpy.sum(myList)
                        n = 36
                        suml2 = avl * n * n
                        if math.fabs(suml2 - suml) > 1:
                            # Perhaps because sum is misinterpreted?
                            msg = "Math is off for suml != suml2: %s != $s" % (suml, suml2) # pylint: disable=E9905 
                            nTerror(msg)
                        if maxl > suml:
                            msg = "Math is off for maxl > suml: %s != $s" % (maxl, suml)    # pylint: disable=E9905 
                            nTerror(msg)

                        vL = []
                        for value in  (avl, sdl, maxl, suml):
                            vL.append( locale.format('%12.3f', value, True))
                        strTitle = "av: %s sd: %s\nmax: %s sum: %s" % (vL[0],vL[1],vL[2],vL[3])
                        nTdebug("myHist: %s" % strTitle)

                        if True: # plot distribution itself too?
                            clf()
                            ps = NTplotSet() # closes any previous plots
                            ps.hardcopySize = (500, 500)
                            plotparams1 = plotParameters.getdefault(dihedralName1, 'dihedralDefault')
                            plotparams2 = plotParameters.getdefault(dihedralName2, 'dihedralDefault')

                            myplot = NTplot(title=strTitle,
                              xRange=(plotparams1.min, plotparams1.max),
                              xTicks=range(int(plotparams1.min), int(plotparams1.max + 1), plotparams1.ticksize),
                              xLabel=dihedralName1,
                              yRange=(plotparams2.min, plotparams2.max),
                              yTicks=range(int(plotparams2.min), int(plotparams2.max + 1), plotparams2.ticksize),
                              yLabel=dihedralName2)
                            ps.addPlot(myplot)

                            myplot.dihedralComboPlot([myHist], minPercentage=MIN_Z_D1D2, maxPercentage=MAX_Z_D1D2, scaleBy=SCALE_BY_Z, ssType = ssType)

                            fn = 'd1d2_%s_%s-%s-%s' % (ssType, resTypePrev, resType, resTypeNext)
                            if doOverall:
                                fn += '_ov_'
                            fn += "." + graphicsFormat
                            ps.hardcopy(fn, graphicsFormat)

                        if True:
                            clf()
                            hist(myList, 40)
                            xlabel('triplet count')
                            ylabel('number of occurrences')
                            title(strTitle)
                            fn = "plotHistOfHist_%s_%s_d1d2.%s" % (ssType, str('-'.join(resTypeListBySequenceOrder)), graphicsFormat)
                            savefig(fn)

        # end loop over ssType
    # end over ssType overall
    return

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
    titleStr = 'd1d2 all resType'
    nTmessage("plotting: %s" % titleStr)
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

    plot = NTplot(title=titleStr,
      xRange=(plotparams1.min, plotparams1.max),
      xTicks=range(int(plotparams1.min), int(plotparams1.max + 1), plotparams1.ticksize),
      xLabel=dihedralName1,
      yRange=(plotparams2.min, plotparams2.max),
      yTicks=range(int(plotparams2.min), int(plotparams2.max + 1), plotparams2.ticksize),
      yLabel=dihedralName2)
    ps.addPlot(plot)

    # Plot a density background
    histList = []
    ssTypeList = hPlot.histd1BySs0.keys() # TODO: check this histd1BySs0 attribute. UNTESTED.
    ssTypeList.sort() # in place sort to: space, H, S
    for ssType in ssTypeList:
        hist = getDeepByKeys(hPlot.histd1BySs0, ssType)
        if hist != None:
            nTdebug('appending [%s]' % ssType)
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
            nTdebug('Skipping ' % res)

        else:
            CA_atms = triplet.zap('CA')
            CB_atms = triplet.zap('CB')

            nTdebug("%s %s %s %s" % (res, triplet, CA_atms, CB_atms))

            if None in CB_atms: # skip Gly for now
                nTdebug('Skipping %s' % res)
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
                    nTdebug('Skipping without BB %s' % res)
                    continue

                if d1.cv < 0.03 and d2.cv < 0.03: # Only include structured residues
                    for i in range(mCount): # Consider each model individually
    #                    bb = res.Whatif.bbNormality.valueList[i]
                        bb = getDeepByKeys(res, WHATIF_STR, BBCCHK_STR, VALUE_LIST_STR, i)
                        if bb == None:
                            nTdebug('Skipping without BB %s' % res)
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
#    graphicsFormat = "png"

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
    for resType in hPlot.histd1BySs0AndResTypes[ssTypeFixed].keys(): # TODO: check UNTESTED code for attribute histd1BySs0AndResTypes
#            if resType != 'ARG': # for testing enable filtering.
#                continue
        if resType in resTypeListSkip:
            continue
        titleStr = 'd1d2 ' + resType
        nTmessage("plotting: %s" % titleStr)
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

        plot = NTplot(title=titleStr,
          xRange=(plotparams1.min, plotparams1.max),
          xTicks=range(int(plotparams1.min), int(plotparams1.max + 1), plotparams1.ticksize),
          xLabel=dihedralName1,
          yRange=(plotparams2.min, plotparams2.max),
          yTicks=range(int(plotparams2.min), int(plotparams2.max + 1), plotparams2.ticksize),
          yLabel=dihedralName2)
        ps.addPlot(plot)

        # Plot a density background
        histList = []
        ssTypeList = hPlot.histd1BySs0AndResTypes.keys() # TODO: test this untested histd1BySs0AndResTypes parameter
        ssTypeList.sort() # in place sort to: space, H, S
        for ssType in ssTypeList:
            hist = getDeepByKeys(hPlot.histd1BySs0AndResTypes, ssType, resType)
            if hist != None:
                nTdebug('appending [%s]' % ssType)
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
#        fn = resType + "_d1d2." + graphicsFormat
#        ps.hardcopy(fn, graphicsFormat)
        plot.show()

def plotDihedral2DRamaWrapper():
    for _i in range(20):
        plotDihedral2DRama()

def plotHistoDihedralWrapper():
    for _i in range(2):
#        unittest.main('cing.Libs.test.test_NTplot2', 'NTplot2Checks_a')
        plotTestHistoDihedral()


if __name__ == "__main__":
    os.chdir(cingDirTmp)
    cing.verbosity = verbosityDebug
    # Commented out because profiling isn't part of unit testing.
    if False:
        fn = 'fooprof'
#            profile.run('plotDihedral2DRamaWrapper()', fn)
        profile.run('plotHistoDihedralWrapper()', fn)
        p = pstats.Stats(fn)
    #     enable a line or two below for useful profiling info
        p.sort_stats('time').print_stats(100)
        p.sort_stats('cumulative').print_stats(100)
    if False:
        plotDihedral2DRama()
#            plotDihedral2DRamaWrapper()
#            plotHistoDihedralWrapper()
    if False:
#        entryList = "1y4o".split()
    #    entryList = "1tgq 1y4o".split()
        entryList = "1brv".split()
        for entryId in entryList:
            plotForEntry(entryId)
    if False:
        os.chdir(doubletsDir)
        plotDihedralD1_1d()
    if True:
        os.chdir(tripletsOvDir)
        plotDihedralD1_2d(doOnlyOverall=False)

    if False:
        m = plotHistogramOverall()

    if False:
        plotDihedralD1D2()

    if False:
        os.chdir(plotHistogramBySsTypeResidueTypesDir)
        plotHistogramBySsTypeResidueTypes()
