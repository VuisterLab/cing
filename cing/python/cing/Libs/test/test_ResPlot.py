from cing import cingDirTestsData
from cing import cingDirTestsTmp
from cing import verbosityDebug
from cing import verbosityError
from cing.Libs.NTplot import NTplotSet
from cing.Libs.NTplot import ResPlot
from cing.Libs.NTplot import circlePoint
from cing.Libs.NTplot import convertPointsToPlotRange
from cing.Libs.NTplot import fontVerticalAttributes
from cing.Libs.NTplot import plusPoint
from cing.Libs.NTplot import pointAttributes
from cing.Libs.NTplot import useMatPlotLib
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTlist
from cing.PluginCode.Whatif import ANGCHK_STR
from cing.PluginCode.Whatif import BBCCHK_STR
from cing.PluginCode.Whatif import BNDCHK_STR
from cing.PluginCode.Whatif import C12CHK_STR
from cing.PluginCode.Whatif import INOCHK_STR
from cing.PluginCode.Whatif import QUACHK_STR
from cing.PluginCode.Whatif import RAMCHK_STR
from cing.PluginCode.Whatif import VALUE_LIST_STR
from cing.PluginCode.Whatif import WHATIF_STR
from cing.PluginCode.Whatif import runWhatif
from cing.PluginCode.procheck import PROCHECK_STR
from cing.PluginCode.procheck import SECSTRUCT_STR
from cing.core.classes import Project
from cing.core.constants import BMRB
from cing.core.constants import CYANA
from random import random
from unittest import TestCase
import cing
import os #@Reimport
import unittest
#from pylab import * # preferred importing. Includes nx imports. #@UnusedWildImport

class AllChecks(TestCase):

    # important to switch to temp space before starting to generate files for the project.
    os.chdir(cingDirTestsTmp)
    NTdebug("Using matplot (True) or biggles: %s", useMatPlotLib)

    def testResPlot(self):
        
        actuallyRunProcheck = False
        actuallyRunWhatif   = False
        showValues          = False
        modelNum            = 1 # Only used when simulating data 
        #entryId = "1ai0" # Most complex molecular system in any PDB NMR entry 
#        entryId = "2hgh" # Small much studied PDB NMR entry; 48 models 
#        entryId = "1bus" # Small much studied PDB NMR entry:  5 models of 57 AA.: 285 residues.
        entryId = "1brv_1model" 
#        entryId = "2hgh_1model"
        
        pdbConvention = BMRB
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
           
        self.failIf( os.chdir(cingDirTestsTmp), msg=
            "Failed to change to temp test directory for data: "+cingDirTestsTmp)
        project = Project( entryId )
        project.removeFromDisk()
        project = Project.open( entryId, status='new' )
        cyanaDirectory = os.path.join(cingDirTestsData,"cyana", entryId)
        pdbFileName = entryId+".pdb"
        pdbFilePath = os.path.join( cyanaDirectory, pdbFileName)
        NTdebug("Reading files from directory: " + cyanaDirectory)
        # Fast
        project.initPDB( pdbFile=pdbFilePath, convention = pdbConvention )
        
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
                
    #            NTdebug(`res`)
                
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
#                            NTdebug("pointsBBCCHK: %s", pointsBBCCHK)
                                                
                        if showValues:
                            NTdebug("%10s valueList: %-80s" % ( checkID, valueList))
        
        ps = None
        i = 0
        for resList in rangeList:
            i += 1
#            NTdebug("resList: %s" % resList)
            ps = NTplotSet() # closes any previous plots
            ps.hardcopySize = (600,600)
            nrows = 4
            ntPlot1 = ps.createSubplot(nrows,1,1,useResPlot=True,molecule=project.molecule,resList=resList)
            ntPlot2 = ps.createSubplot(nrows,1,2,useResPlot=True,molecule=project.molecule,resList=resList)
            ntPlot3 = ps.createSubplot(nrows,1,3,useResPlot=True,molecule=project.molecule,resList=resList)
            ntPlot4 = ps.createSubplot(nrows,1,4,useResPlot=True,molecule=project.molecule,resList=resList)

            ps.subplotsAdjust(hspace  = .0) # no height spacing between plots.
            ps.subplotsAdjust(top     = 0.9) # Accommodate icons and res types.
            ps.subplotsAdjust(left    = 0.15) # Accommodate extra Y axis label.
    
            attr = fontVerticalAttributes()
            attr.fontColor  = 'blue' 
            # Left of actual yLabel.
            ntPlot1.labelAxes( (-0.12, 0.5), 'Backbone', attributes=attr) 
            ntPlot2.labelAxes( (-0.12, 0.5), 'Quality',  attributes=attr) 
            ntPlot3.labelAxes( (-0.12, 0.5), 'Angle',    attributes=attr) 
#            ntPlot4.labelAxes( (-0.12, 0.5), 'Backbone', attributes=attr) 
            
            ntPlot1.yLabel  = 'Ramachandr. Z'
            ntPlot2.yLabel = 'Chi 1/2. Z'
            ntPlot3.yLabel = 'Bond max Z'
            ntPlot4.yLabel = 'Restraint RMSD'
            
            ntPlotBottom = ntPlot4
            
            ntPlot1.xLabel = None
            ntPlot2.xLabel = None
            ntPlot3.xLabel = None
            
#            ntPlot1.yRange= (0, 3) # to be reset later automatically..
#            ntPlot2.yRange= (0, 3)
            # Draw secondary structure elements and accessibility
            # Set x range and major ticker.
            # The major ticker determines the grid layout.
            ntPlot1.drawResIcons( ySpaceAxis=.03+.13 ) # leave space for res types but get it right on top.
#            ntPlot3.drawResNumbers() # accept default -bottom- position.
            # Reset the minor ticker
#            ntPlot3.xRange = ntPlot1.xRange 
    
            
            plusPoint   = pointAttributes( type='plus',   size=1.5, color='black' )
            circlePoint = pointAttributes( type='circle', size=1.5, color='blue')
            plusPoint.lineColor   = 'black'
            circlePoint.lineColor = 'blue'
            length = ntPlot1.MAX_WIDTH_IN_RESIDUES
            start = (i-1)*length

#            pointsBBCCHK = removeNulls(pointsBBCCHK)
            # buildin max is overridden by matplotlib
#            end   = NTmin(start + ntPlot1.MAX_WIDTH_IN_RESIDUES,len(pointsANGCHK))
            pointsANGCHKOffset = convertPointsToPlotRange(pointsANGCHK, xOffset=-start, yOffset=0, start=0, length=length)
            pointsBNDCHKOffset = convertPointsToPlotRange(pointsBNDCHK, xOffset=-start, yOffset=0, start=0, length=length)
            pointsQUACHKOffset = convertPointsToPlotRange(pointsQUACHK, xOffset=-start, yOffset=0, start=0, length=length)
            pointsRAMCHKOffset = convertPointsToPlotRange(pointsRAMCHK, xOffset=-start, yOffset=0, start=0, length=length)
            pointsC12CHKOffset = convertPointsToPlotRange(pointsC12CHK, xOffset=-start, yOffset=0, start=0, length=length)
            pointsBBCCHKOffset = convertPointsToPlotRange(pointsBBCCHK, xOffset=-start, yOffset=0, start=0, length=length)
                        
            NTdebug("pointsRAMCHKOffset: %s" % pointsRAMCHKOffset)
#            NTdebug("start:end: %s %s" % (start,end))
            ntPlot1.lines(pointsRAMCHKOffset, plusPoint)
            ntPlot1.lines(pointsBBCCHKOffset, circlePoint)
            ntPlot2.lines(pointsQUACHKOffset, plusPoint)
            ntPlot2.lines(pointsC12CHKOffset, circlePoint)
            ntPlot3.lines(pointsANGCHKOffset, plusPoint)
            ntPlot3.lines(pointsBNDCHKOffset, circlePoint)
            
#            QUACHK   Poor   : <   -3.00   Bad    : <   -5.00
#            RAMCHK   Poor   : <   -3.00   Bad    : <   -4.00
#            C12CHK   Poor   : <   -3.00   Bad    : <   -4.00
#            BBCCHK   Poor   : <   10.00   Bad    : <    5.00
            
            ntPlot1.autoScaleY( pointsRAMCHKOffset+pointsBBCCHKOffset )
            ntPlot2.autoScaleY( pointsQUACHKOffset+pointsC12CHKOffset )
            ntPlot3.autoScaleY( pointsANGCHKOffset+pointsBNDCHKOffset )

            ntPlot3.setYrange((.0, ntPlot3.yRange[1])) 

            ntPlot1.drawResTypes( ) # accept default -top- position.
            ntPlot2.xRange = ntPlot1.xRange 
            ntPlot3.xRange = ntPlot1.xRange 
            ntPlot4.xRange = ntPlot1.xRange
             
            ntPlot1.drawResNumbers( showLabels=False) # also sets the grid lines for major. Do last as it won't rescale with plot yet.
            ntPlot2.drawResNumbers( showLabels=False) 
            ntPlot3.drawResNumbers( showLabels=False) 
            ntPlotBottom.drawResNumbers() 
            # Set the grid and major tickers
            ps.hardcopy('residuePlotSet%03d.png'%i)
#            if ps: # Can only show one
#                ps.show()
        

if __name__ == "__main__":
    cing.verbosity = verbosityError
    cing.verbosity = verbosityDebug
    unittest.main()
