# No mat plot lib items imported here.
# Only code specific for molecule.py related things.
# It would be good to move the ResPlot class here too.

from cing.Libs.Imagery import convert2Web
from cing.Libs.Imagery import joinPdfPages
from cing.Libs.Imagery import montage
from cing.Libs.NTplot import NTplotSet
from cing.Libs.NTplot import ResPlot
from cing.Libs.NTplot import cingLineTypeList
from cing.Libs.NTplot import circlePoint
from cing.Libs.NTplot import fontVerticalAttributes
from cing.Libs.NTplot import plusPoint
from cing.Libs.NTplot import pointAttributes
from cing.Libs.NTutils import * #@UnusedWildImport

KEY_LIST_STR = 'keyList'
KEY_LIST2_STR = 'keyList2'
KEY_LIST3_STR = 'keyList3'
KEY_LIST4_STR = 'keyList4'
KEY_LIST5_STR = 'keyList5'

XLABEL_STR = 'xLabel'
YLABEL_STR = 'yLabel'
USE_ZERO_FOR_MIN_VALUE_STR = 'useZeroForMinValue'
USE_VERBOSE_Y_LOCATOR_STR = 'useVerboseYLocator' # Potentially more than the default 10 major ticks on Y axis.
USE_MIN_VALUE_STR = 'useMinValue'
USE_MAX_VALUE_STR = 'useMaxValue'
USE_ROG_FOR_COLOR_STR = 'useRogForColor'

NT_MOLECULE_PLOT_IDX_X_VALUE = 0
NT_MOLECULE_PLOT_IDX_VALUE_LIST = 1
NT_MOLECULE_PLOT_IDX_ROG_COLOR = 2

class MoleculePlotSet:
    """A set of ResPlotSet (pages)."""
    def __init__(self, project, ranges, keyLoLoL, makeCorrelationPlot = False):
        self.project = project
        self.ranges = ranges
        self.keyLoLoL = keyLoLoL
        self.colorMain = 'black'
        self.colorAlt = 'blue'
        self.pointSize = 3.0 # was 1.5
        self.makeCorrelationPlot = makeCorrelationPlot
        self.rangeList = self.project.molecule.getFixedRangeList(
            max_length_range = ResPlot.MAX_WIDTH_IN_RESIDUES,
            ranges = self.ranges)

    def renderMoleculePlotSet(self, fileName, createPngCopyToo = True):
        """
        Create a PDF with possibly multiple pages of this MoleculePlotSet.

        If createPngCopyToo is set then also created are:
        - _pin.gif file per set,
        - png file per set, and
        - png files per page.


        The fileName is for the output of course.

        The directory of that filename is also take for any other plots created.
        """
        self.fileName = fileName
        self.createPngCopyToo = createPngCopyToo

        # next variable must have same dimensions as self.keyLoLoL
        self.pointsLoLoL = [] # list per res in rangeList of lists
        for row in self.keyLoLoL:
            pointsLoL = []
            self.pointsLoLoL.append(pointsLoL)
            for mainOrAlt in row:
                pointsL = []
                pointsLoL.append(pointsL)
                for item in mainOrAlt:
                    points = []
                    pointsL.append(points)
                    itemDictKeyList = item.keys()
                    itemDictKeyList.sort()
                    for keyList in itemDictKeyList:
                        if not (keyList in [ KEY_LIST_STR, KEY_LIST2_STR, KEY_LIST3_STR, KEY_LIST4_STR, KEY_LIST5_STR]):
                            continue
                        serie = []
                        points.append(serie)
#        NTdebug('self.keyLoLoL filled: %s' % self.keyLoLoL )
#        NTdebug('pointsLoLoL init: %s' % pointsLoLoL )
        resNumb = 0

        # start a new plot page for each resList
        for resList in self.rangeList:
            for res in resList:
                resNumb += 1
#                NTdebug(`res`)
                r = 0 # r for row
                for row in self.keyLoLoL:
                    pointsLoL = self.pointsLoLoL[r]
                    i = 0 # for each serie; main or alternative.
                    for mainOrAlt in row:
#                        NTdebug("mainOrAlt: %s" % mainOrAlt)
                        pointsL = pointsLoL[i]
                        j = 0 # for each
                        for item in mainOrAlt:
#                            NTdebug("item: %s" % item)
                            points = pointsL[j]
                            itemDictKeyList = item.keys()
                            itemDictKeyList.sort()
#                            NTdebug("itemDictKeyList: %s" % itemDictKeyList)
                            color = None
                            if getDeepByKeys( item, USE_ROG_FOR_COLOR_STR):
                                color = res.rogScore.colorLabel
                            k = 0
                            for keyList in itemDictKeyList:
                                if not (keyList in [ KEY_LIST_STR, KEY_LIST2_STR, KEY_LIST3_STR, KEY_LIST4_STR, KEY_LIST5_STR]):
                                    continue
                                serie = points[k]
                                keys = item[keyList]
                                point = getDeepByKeysOrAttributes(res, *keys)
#                                NTdebug("Found point %s for keys %s" % (point, keys) )
                                # Note that for a correlationPlot we keep the residue value as a list for all models.
                                if isinstance(point, NTlist) and not self.makeCorrelationPlot:
                                    av, _sd, _n = point.average()
    #                                NTdebug("Found av, sd, n %s %s %s" % (val2Str(av, "%.3f", 8),val2Str(sd, "%.3f", 8),val2Str(n, "%.3f", 8)))
                                    point = av
    #                                point = point.average()[0]
                                serie.append((resNumb - .5, point, color))
                                k += 1
                            j += 1
                        i += 1
                    r += 1
                # end for row
            # end for res
        # end for resList
#        NTdebug('pointsLoLoL filled: %s' % pointsLoLoL )

        self.fileNameList = []
        self.pathPngList = []
        self.ps = None

        f = self._renderMoleculePlotSetOriginal
        if self.makeCorrelationPlot:
            f = self._renderMoleculePlotSetCorrelation
        if f():
            return True

        if joinPdfPages(self.fileNameList, self.fileName):
            NTerror('Failed to joinPdfPages from %s to: %s' % (self.fileNameList, fileName))
            return True

        if createPngCopyToo:
            head, _tail = os.path.split(fileName)             # split is on last /
            # Just do the _pin.gif
            if not convert2Web(self.pathPngList, outputDir = head, doPrint = False, doFull = False):
                NTerror('Failed to convert2Web from %s to: %s' % (self.pathPngList, head))
                return True

            if montage(self.pathPngList, fileName[: - 4] + ".png"):
                NTerror('Failed to montage from %s to: %s' % (self.pathPngList, fileName[: - 4] + ".png"))
                return True

        # Remove the single pdf files.
        for fn in self.fileNameList:
            os.unlink(fn)

    def _renderMoleculePlotSetOriginal(self):
        nrows = len(self.keyLoLoL)
        r = 0 # r now for resList
        for resList in self.rangeList:
            r += 1
#            NTdebug("resList: %s" % resList)
            ps = ResPlotSet() # closes any previous plots
            ntPlotList = []
            # create all subplots
            for i in range(nrows):
                ntPlotList.append(ps.createSubplot(nrows, 1, i + 1,
                                            useResPlot = True,
                                            molecule = self.project.molecule,
                                            resList = resList))
            # Set y and x labels for all rows.
            attr = fontVerticalAttributes()
            attr.fontColor = self.colorAlt
            position = (-0.12, 0.5)
            for i in range(nrows):
                if i != nrows - 1:
                    ntPlotList[i].xLabel = None
                row = self.keyLoLoL[i]
                for m in range(len(row)): # m in range [0,1] # 1 maybe absent
                    mainOrAlt = row[m]
                    key = mainOrAlt[0] # take first main first
                    label = key[YLABEL_STR]
#                    NTdebug( 'row %d Label: %s' % (m,label))
                    if not m:      # main y-axis?
                        ntPlotList[i].yLabel = label
                    else: # alternative y-axis?
                        ntPlotList[i].labelAxes(position, label, attributes = attr)

            plusPoint = pointAttributes(type = 'plus', size = self.pointSize, color = self.colorMain)
            circlePoint = pointAttributes(type = 'circle', size = self.pointSize, color = self.colorAlt)
            plusPoint.lineColor = self.colorMain
            circlePoint.lineColor = self.colorAlt
            length = ntPlotList[0].MAX_WIDTH_IN_RESIDUES
            start = (r - 1) * length


            for i in range(nrows):
                pointsLoL = self.pointsLoLoL[i]
                pointsForAutoscaling = [] # might be done differently in future when alternative axis doesn't have same scale as main axis.
                for j in range(len(pointsLoL)): # j is 0 for main or 1 for alt
                    pointsL = pointsLoL[j]
                    for k in range(len(pointsL)): # k usually just 0
                        points = pointsL[k]
                        for lineTypeIdx, serie in enumerate(points): # extra loop for potentially multiple series
                            pointsOffset = convertPointsToPlotRange(serie, xOffset = - start, yOffset = 0, start = 0, length = length)
                            pointAttr = plusPoint
                            if j:      # alternative y-axis
                                pointAttr = circlePoint
#                            NTdebug("Using lineTypeIdx %d %s"%(lineTypeIdx, cingLineTypeList[lineTypeIdx]))
                            pointAttr.lineType = cingLineTypeList[lineTypeIdx]
    #                        NTdebug( 'plotting row %d pointsLoL %d pointsL %d' % (i, j, k))
                            ntPlotList[i].lines(pointsOffset, pointAttr)
                            pointsForAutoscaling += pointsOffset

#                NTdebug( 'autoScaleY row %d' % (i))
                useVerboseLocator = getDeepByKeys(self.keyLoLoL, i, 0, 0, USE_VERBOSE_Y_LOCATOR_STR)
                ntPlotList[i].autoScaleY(pointsForAutoscaling, useVerboseLocator=useVerboseLocator)
                if getDeepByKeys(self.keyLoLoL, i, 0, 0, USE_ZERO_FOR_MIN_VALUE_STR):
#                    NTdebug('Setting minimum y value to zero for subplot: %d' % i)
                    ntPlotList[i].setYrange((.0, ntPlotList[i].yRange[1]))

                maxValue = getDeepByKeys(self.keyLoLoL, i, 0, 0, USE_MAX_VALUE_STR)
                if maxValue != None:
#                    NTdebug('Setting maximum y value to %s for subplot: %d' % (maxValue,i))
                    ntPlotList[i].setYrange((ntPlotList[i].yRange[0], maxValue))

                minValue = getDeepByKeys(self.keyLoLoL, i, 0, 0, USE_MIN_VALUE_STR)
                if minValue != None:
#                    NTdebug('Setting minimum y value to %s for subplot: %d' % (minValue, i))
                    ntPlotList[i].setYrange((minValue, ntPlotList[i].yRange[1]))


            ySpaceAxisResTypes = .02 + (nrows - 1) * .01 # ..05
            ntPlotList[0].drawResTypes(ySpaceAxis = ySpaceAxisResTypes) # Weirdly can only be called after yRange is set.

            for i in range(nrows):
                showLabels = False
                if i == nrows - 1:
                    showLabels = True
                # Set the grid and major tickers
                # also sets the grid lines for major. Do last as it won't rescale with plot yet.
                ntPlotList[i].drawResNumbers(showLabels = showLabels)

            # Draw secondary structure elements and accessibility
            # Set x range and major ticker.
            # The major ticker determines the grid layout.
            # leave space for res types but get it right on top.
            # .18 at nrows = 4
            # Needs to be done before re-scaling the y axis from [0,1]
            ySpaceAxisResIcons = .06 + (nrows - 1) * .04 # .14
            ntPlotList[0].iconBoxYheight = 0.16 * nrows / 3. # .16 at nrows=3
            ntPlotList[0].drawResIcons(ySpaceAxis = ySpaceAxisResIcons)

            # Actually plot
            self.fileNameList.append('%s%03d.pdf' % (self.fileName[: - 4], r))
            if ps.hardcopy(self.fileNameList[r - 1]):
                NTerror('Failed to ps.hardcopy to: %s' % self.fileNameList[r - 1])
                return True

            if self.createPngCopyToo:
                fileNamePng = '%s%03d.png' % (self.fileName[: - 4], r)
                if ps.hardcopy(fileNamePng):
                    NTerror('Failed to ps.hardcopy to: %s' % fileNamePng)
                    return True
                self.pathPngList.append(fileNamePng)
        # end for resList in rangeList:

    def _renderMoleculePlotSetCorrelation(self):
        nrows = len(self.keyLoLoL)
        ps = NTplotSet() # closes any previous plots
        ntPlotList = []
        # create all subplots
        for i in range(nrows):
            ntPlotList.append(ps.createSubplot(nrows, 1, i + 1))
        # Set y and x labels for all rows.
        attr = fontVerticalAttributes()
        attr.fontColor = self.colorAlt
        position = (-0.12, 0.5)
        for i in range(nrows):
            if i != nrows - 1:
                ntPlotList[i].xLabel = None
            row = self.keyLoLoL[i]
            for m in range(len(row)): # m in range [0,1] # 1 maybe absent
                mainOrAlt = row[m]
                key = mainOrAlt[0] # take first main first
                label = key[YLABEL_STR]
#                    NTdebug( 'row %d Label: %s' % (m,label))
                if not m:      # main y-axis?
                    ntPlotList[i].xLabel = key[XLABEL_STR]
                    ntPlotList[i].yLabel = label
                else: # alternative y-axis?
                    ntPlotList[i].labelAxes(position, label, attributes = attr)


        for i in range(nrows):
#            NTdebug("i (nrows): %d" % i)
            pointsLoL = self.pointsLoLoL[i]
            pointsForAutoscalingY = [] # might be done differently in future when alternative axis doesn't have same scale as main axis.
            pointsForAutoscalingX = []
            for j in range(len(pointsLoL)): # j is 0 for main or 1 for alt
                pointsL = pointsLoL[j]
#                NTdebug("j: %d pointsL %s" % (j, pointsL))
                for k in range(len(pointsL)): # k odd is x and k even is y.
                    points = pointsL[k]
#                    NTdebug("k: %d points %s" % (k, points))
#                    x,y,s,c,verts = [],[],[],[],[]
                    for l in range(len(points)):
                        point = points[l]
#                        NTdebug("l: %d point %s" % (l, point))
                        if not (l % 2):
                            xValueList = point
                            continue
                        yValueList = point
                        for resId, resValueListTupleX in enumerate(xValueList):
                             # skip the residue location; it's not used in this variant of the code.
#                            NTdebug("resId: %d" % resId)
                            resValueListTupleY = yValueList[resId]
                            resValueListX = resValueListTupleX[NT_MOLECULE_PLOT_IDX_VALUE_LIST]
                            resValueListY = resValueListTupleY[NT_MOLECULE_PLOT_IDX_VALUE_LIST]
                            if not resValueListX:
#                                NTdebug("No resValueListX")
                                continue
                            if not resValueListY:
#                                NTdebug("No resValueListY")
                                continue

#                            NTdebug("resValueListX: %s" % resValueListX)
#                            NTdebug("resValueListY: %s" % resValueListY)
                            Xav, Xsd, _n = resValueListX.average()
                            Yav, Ysd, _n = resValueListY.average()
                            if isNaN(Xsd): # No sd for single model ensembles.
                                Xsd = 0.1
                            if isNaN(Ysd):
                                Ysd = 0.1
                            width = Xsd * 2
                            height = Ysd * 2
                            if False: # while testing since sd are too large to plot then.
                                width /= 5
                                height /= 5
                            if False: # while testing since sd are too large to plot then.
                                width *= 5
                                height *= 5
#                            NTdebug("resId: %2d  x %8s width  %8s" % (resId, val2Str(Xav, "%.3f", 8), val2Str(width, "%.3f", 8)))
#                            NTdebug("           y %8s height %8s" % (val2Str(Yav, "%.3f", 8), val2Str(height, "%.3f", 8)))
#                            p = (Xav+0.1, Yav) # just for debugging.
#                            pointAttr = circlePoint
#                            pointAttr.pointSize = 10
#                            ntPlotList[i].lines([(0,0), p], plusPoint)
#                            ntPlotList[i].lines([(0,0), p], pointAttr)
                            color = "blue"
                            if getDeepByKeys( key, USE_ROG_FOR_COLOR_STR):
                                color = resValueListTupleX[NT_MOLECULE_PLOT_IDX_ROG_COLOR]
                            ntPlotList[i].ellipse(point = (Xav, Yav), width = width, height = height, color=color, alpha = 0.9)
#                            x.append(Xav)
#                            y.append(Yav)
                            pointsForAutoscalingX.append([None, Xav])
                            pointsForAutoscalingY.append([None, Yav])
                    # While building code:
#                    lx = len(x)
#                    s = rand(lx)
#                    s *= 1000
#                    c = rand(lx)
##                    v1 = rand(lx)
##                    v2 = rand(lx)
##                    verts = zip( v1, v2 )
#                    rx, ry = 3., 1. # same geometry for each.
#                    area = rx * ry * pi
#                    theta = arange(0, 2*pi+0.01, 0.1)
#                    verts = zip(rx/area*cos(theta), ry/area*sin(theta))
#
#                    ntPlotList[i].scatter(x,y,s,c,marker=None,verts =verts)

            ntPlotList[i].autoScaleX(pointsForAutoscalingX)
            ntPlotList[i].autoScaleY(pointsForAutoscalingY)

            if getDeepByKeys(self.keyLoLoL, i, 0, 0, USE_ZERO_FOR_MIN_VALUE_STR):
                ntPlotList[i].setYrange((.0, ntPlotList[i].yRange[1]))

            maxValue = getDeepByKeys(self.keyLoLoL, i, 0, 0, USE_MAX_VALUE_STR)
            if maxValue != None:
                ntPlotList[i].setYrange((ntPlotList[i].yRange[0], maxValue))
        # Actually plot
        r = 1
        self.fileNameList.append('%s%03d.pdf' % (self.fileName[: - 4], r))
#        ps.axis.add_artist(Line2D((0,1), (0,1)))
        if ps.hardcopy(self.fileNameList[r - 1]):
            NTerror('Failed to ps.hardcopy to: %s' % self.fileNameList[r - 1])
            return True

        if self.createPngCopyToo:
            fileNamePng = '%s%03d.png' % (self.fileName[: - 4], r)
            if ps.hardcopy(fileNamePng):
                NTerror('Failed to ps.hardcopy to: %s' % fileNamePng)
                return True
            self.pathPngList.append(fileNamePng)
    # end for resList in rangeList:


class ResPlotSet(NTplotSet):
    """A single page with one or more rows of plots."""
    def __init__(self):
        NTplotSet.__init__(self)
        self.hardcopySize = (600, 600)
        self.subplotsAdjust(hspace = .1) # no height spacing between plots.
        self.subplotsAdjust(top = 0.9) # Accommodate icons and res types.
        self.subplotsAdjust(left = 0.15) # Accommodate extra Y axis label.

def offSet(inputList, xOffset = 0., yOffset = 0.):
    result = []
    for i in inputList:
        if i[0] == None:
            x = None
        else:
            x = i[0] + xOffset
        if i[1] == None:
            y = None
        else:
            y = i[1] + yOffset
        result.append((x, y))
    return result

def selectPointsFromRange(pointList, start = 0, length = None):
    """Length is exclusive; eg from 0 to 1 exclusive should
    have length one and not two."""

    if not length:
        NTerror('expected a non-zero length in selectPointsFromRange')
        return True
    end = start + length
    result = []
    for point in pointList:
        x = point[0]
        if x >= start and x < end:
            result.append((x, point[1]))
    return result

def convertPointsToPlotRange(inputList, xOffset = 0, yOffset = 0, start = 0, length = None):
    """Convenience method combining offSet and selectPointsFromRange"""
    result = offSet(inputList, xOffset = xOffset, yOffset = yOffset)
    result = selectPointsFromRange(result, start = start, length = length)
    return result
