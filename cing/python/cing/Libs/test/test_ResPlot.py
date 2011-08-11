from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.Whatif import runWhatif
from cing.PluginCode.dssp import runDssp #@UnusedImport Added trigger import error . Needed for when whatif is but dssp isn't installed. 
from cing.PluginCode.matplib import * #@UnusedWildImport
from cing.core.classes import Project
from cing.core.constants import * #@UnusedWildImport
from unittest import TestCase
import os #@Reimport
import unittest

class AllChecks(TestCase):

    # important to switch to temp space before starting to generate files for the project.

    cingDirTmpTest = os.path.join( cingDirTmp, 'test_ResPlot' )
    mkdirs( cingDirTmpTest )
    os.chdir(cingDirTmpTest)

    def testResPlot(self):

        actuallyRunProcheck = False
        actuallyRunWhatif   = False
        showValues          = False
        modelNum            = 1 # Only used when simulating data
        #entryId = "1ai0" # Most complex molecular system in any PDB NMR entry
#        entryId = "2hgh" # Small much studied PDB NMR entry; 48 models
#        entryId = "1bus" # Small much studied PDB NMR entry:  5 models of 57 AA.: 285 residues.
#        entryId = "2hgh_1model"
        entryId = "1brv_1model"

        pdbConvention = IUPAC
        ranges = None
        if entryId.startswith("2hgh"):
            pdbConvention = CYANA
            # Compile a NTlist instance with residue objects.
            ranges = "2-54,111-136,145-193"
                # 1 and 55 are 5' and 3' terminii which are a little looser.
                # 12, and 34 are bases that are not basepaired.
                # 191-193 are bound ZN ions.
        elif entryId.startswith("1brv"):
            # Truncate from Val171-Glu189 to:
            ranges = "176-188"

        project = Project( entryId )
        project.removeFromDisk()
        project = Project.open( entryId, status='new' )
        cyanaDirectory = os.path.join(cingDirTestsData,"cyana", entryId)
        pdbFileName = entryId+".pdb"
        pdbFilePath = os.path.join( cyanaDirectory, pdbFileName)
        nTdebug("Reading files from directory: " + cyanaDirectory)
        # Fast
        project.initPDB( pdbFile=pdbFilePath, convention = pdbConvention )
        project.runDssp()

        rangeList = project.molecule.getFixedRangeList(
            max_length_range = ResPlot.MAX_WIDTH_IN_RESIDUES, ranges=ranges )

        if actuallyRunProcheck:
            self.failIf(project.procheck(createPlots=False, runAqua=False) is None)
        if actuallyRunWhatif:
            self.assertFalse(runWhatif(project))

        pointsANGCHK = [] # list per res in rangeList of lists
        pointsBNDCHK = []
        pointsQUACHK = []
        pointsRAMCHK = []
        pointsC12CHK = []
        pointsBBCCHK = []
        resNumb = 0
        for resList in rangeList:
            for res in resList:
                resNumb += 1

    #            nTdebug(repr(res))

    #            if random() < 0.2: # Skip a 10%
    #                continue

                whatifResDict = res.setdefault(WHATIF_STR, NTdict())
                procheckResDict = res.setdefault(PROCHECK_STR, NTdict())
    #            if not whatifResDict: # empty dict
    #                continue

                angList = NTlist()
                bndList = NTlist()

                quaList = NTlist()
                ramList = NTlist()
                c12List = NTlist()
                bbcList = NTlist()

                accList = NTlist()
                sstList = NTlist()
                sstListPossibilities='SH' # secondary structure elements.

                for _modelID in range(modelNum):
                    if not actuallyRunWhatif:
                        angList.append(random()*10-0) # Simulate abs max of Z-scores.
                        bndList.append(random()*5+1)  # offset by 1 but still want to start from zero?

                        quaList.append(random()*5+1)
                        ramList.append(random()*5+1)
                        c12List.append(random()*5+1)
                        bbcList.append(random()*5+1)

                        accList.append(random()*4-2)
                    if not actuallyRunProcheck:
                        sstList.append( sstListPossibilities[ int(random()*2)])  # Simulate secondary structure

                if not actuallyRunWhatif:
                    self.assertFalse (   whatifResDict.setDeepByKeys(angList,  ANGCHK_STR,VALUE_LIST_STR) )
                    self.assertFalse (   whatifResDict.setDeepByKeys(bndList,  BNDCHK_STR,VALUE_LIST_STR) )

                    self.assertFalse (   whatifResDict.setDeepByKeys(quaList,  QUACHK_STR,VALUE_LIST_STR) )
                    self.assertFalse (   whatifResDict.setDeepByKeys(ramList,  RAMCHK_STR,VALUE_LIST_STR) )
                    self.assertFalse (   whatifResDict.setDeepByKeys(c12List,  C12CHK_STR,VALUE_LIST_STR) )
                    self.assertFalse (   whatifResDict.setDeepByKeys(bbcList,  BBCCHK_STR,VALUE_LIST_STR) )

                    self.assertFalse (   whatifResDict.setDeepByKeys(accList,  INOCHK_STR,VALUE_LIST_STR) )

                if not actuallyRunProcheck:
                    self.assertFalse ( procheckResDict.setDeepByKeys(sstList,  SECSTRUCT_STR) )

                for d in [whatifResDict, procheckResDict]:
                    checkIDList = d.keys()
                    for checkID in checkIDList:
                        if d==whatifResDict:
                            valueList = d.getDeepByKeys(checkID,VALUE_LIST_STR)
                        else:
                            valueList = d.getDeepByKeys(checkID)

                        if checkID == ANGCHK_STR:
                            zScore = valueList.average()[0]
                            pointsANGCHK.append( (resNumb-.5, zScore) )
                        elif checkID == BNDCHK_STR:
                            zScore = valueList.average()[0]
                            pointsBNDCHK.append( (resNumb-.5, zScore) )
                        elif checkID == QUACHK_STR:
                            zScore = valueList.average()[0]
                            pointsQUACHK.append( (resNumb-.5, zScore) )
                        elif checkID == RAMCHK_STR:
                            zScore = valueList.average()[0]
                            pointsRAMCHK.append( (resNumb-.5, zScore) )
                        elif checkID == C12CHK_STR:
                            zScore = valueList.average()[0]
                            pointsC12CHK.append( (resNumb-.5, zScore) )
                        elif checkID == BBCCHK_STR:
                            zScore = valueList.average()[0]
                            pointsBBCCHK.append( (resNumb-.5, zScore) )
#                            nTdebug("pointsBBCCHK: %s", pointsBBCCHK)

                        if showValues:
                            nTdebug("%10s valueList: %-80s" % ( checkID, valueList))
        fileNameList =[]
        ps = None
        r = 0
        for resList in rangeList:
            r += 1
#            nTdebug("resList: %s" % resList)
            ps = NTplotSet() # closes any previous plots
            ps.hardcopySize = (600,600)
            nrows = 2
            ntPlotList = []
            for i in range(nrows):
                ntPlotList.append( ps.createSubplot(nrows,1,i+1,useResPlot=True,molecule=project.molecule,resList=resList) )


            ps.subplotsAdjust(hspace  = .1) # no height spacing between plots.
            ps.subplotsAdjust(top     = 0.9) # Accommodate icons and res types.
            ps.subplotsAdjust(left    = 0.15) # Accommodate extra Y axis label.

            attr = fontVerticalAttributes()
            attr.fontColor  = 'blue'
            # Left of actual yLabel.
            labelAxesExtraList = [
              'Backbone',
              'Quality',
              'Angle',
              '',
              '' ]
            labelAxesList = [
              'Ramachandr. Z',
              'Chi 1/2. Z',
              'Bond max Z',
              'Restraint RMSD',
              '' ]
            for i in range(nrows):
                position = (-0.12, 0.5)
                ntPlotList[i].labelAxes( position, labelAxesExtraList[i], attributes=attr)
                ntPlotList[i].yLabel = labelAxesList[i]
                if i != nrows-1:
                    ntPlotList[i].xLabel = None



            plusPoint   = pointAttributes( type='plus',   size=1.5, color='black' )
            circlePoint = pointAttributes( type='circle', size=1.5, color='blue')
            plusPoint.lineColor   = 'black'
            circlePoint.lineColor = 'blue'
            length = ntPlotList[0].MAX_WIDTH_IN_RESIDUES
            start = (r-1)*length

#            pointsBBCCHK = removeNulls(pointsBBCCHK)
            # buildin max is overridden by matplotlib
#            end   = NTmin(start + ntPlot1.MAX_WIDTH_IN_RESIDUES,len(pointsANGCHK))
            pointsANGCHKOffset = convertPointsToPlotRange(pointsANGCHK, xOffset=-start, yOffset=0, start=0, length=length)
            pointsBNDCHKOffset = convertPointsToPlotRange(pointsBNDCHK, xOffset=-start, yOffset=0, start=0, length=length)
            pointsQUACHKOffset = convertPointsToPlotRange(pointsQUACHK, xOffset=-start, yOffset=0, start=0, length=length)
            pointsRAMCHKOffset = convertPointsToPlotRange(pointsRAMCHK, xOffset=-start, yOffset=0, start=0, length=length)
            pointsC12CHKOffset = convertPointsToPlotRange(pointsC12CHK, xOffset=-start, yOffset=0, start=0, length=length)
            pointsBBCCHKOffset = convertPointsToPlotRange(pointsBBCCHK, xOffset=-start, yOffset=0, start=0, length=length)

            pointsOffsetList = [pointsRAMCHKOffset,
                                pointsQUACHKOffset,
                                pointsANGCHKOffset ]
            pointsOffsetList2 = [pointsBBCCHKOffset,
                                 pointsC12CHKOffset,
                                 pointsBNDCHKOffset ]
#            nTdebug("pointsRAMCHKOffset: %s" % pointsRAMCHKOffset)
#            nTdebug("start:end: %s %s" % (start,end))
            for i in range(nrows):
                if i >= len( pointsOffsetList ):
                    continue
                ntPlotList[i].lines(pointsOffsetList[i],  plusPoint)
                ntPlotList[i].lines(pointsOffsetList2[i], circlePoint)
                ntPlotList[i].autoScaleY( pointsOffsetList[i]+pointsOffsetList2[i] )
                if i == 2: # by chance
                    ntPlotList[i].setYrange((.0, ntPlotList[i].yRange[1]))

            ySpaceAxisResTypes = .02 + (nrows-1) * .01
            ntPlotList[0].drawResTypes(ySpaceAxis=ySpaceAxisResTypes) # Weirdly can only be called after yRange is set.

            for i in range(nrows):
                showLabels = False
                if i == nrows-1:
                    showLabels = True
                # also sets the grid lines for major. Do last as it won't rescale with plot yet.
                ntPlotList[i].drawResNumbers( showLabels=showLabels)

            # Draw secondary structure elements and accessibility
            # Set x range and major ticker.
            # The major ticker determines the grid layout.
            # leave space for res types but get it right on top.
#            .18 at nrows = 4
            # Needs to be done before re-scaling the y axis from [0,1] ???????
            ySpaceAxisResIcons = .06 + (nrows-1) * .04
            ntPlotList[0].iconBoxYheight = 0.16 * nrows / 3. # .16 at nrows=3
            ntPlotList[0].drawResIcons( ySpaceAxis=ySpaceAxisResIcons )

            # Set the grid and major tickers
            fileNameList.append( 'residuePlotSet%03d.pdf' % r)
            ps.hardcopy(fileNameList[r-1])
        # end for resList in rangeList:
        self.assertFalse( joinPdfPages( fileNameList, 'residuePlotSetAll.pdf' ))
        for fileName in fileNameList:
            os.unlink( fileName )

if __name__ == "__main__":
    cing.verbosity = verbosityError
    cing.verbosity = verbosityDebug
    unittest.main()
