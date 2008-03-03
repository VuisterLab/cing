"""
Unit test execute as:
python $cingPath/Scripts/test/test_cyana2cing.py
"""
from cing import cingDirTestsData
from cing import cingDirTestsTmp
from cing import verbosityError
from cing.Libs.NTplot import circlePoint
from cing.Libs.NTplot import plusPoint
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTlist
from cing.Libs.ResPlot import HelixIconList
from cing.Libs.ResPlot import ResPlot
from cing.Libs.ResPlot import to3StateUpper
from cing.Libs.ResPlot import triangularList
from cing.PluginCode.Whatif import ANGCHK_STR
from cing.PluginCode.Whatif import BNDCHK_STR
from cing.PluginCode.Whatif import INOCHK_STR
from cing.PluginCode.Whatif import VALUE_LIST_STR
from cing.PluginCode.Whatif import WHATIF_STR
from cing.PluginCode.Whatif import runWhatif
from cing.PluginCode.procheck import PROCHECK_STR
from cing.PluginCode.procheck import SECSTRUCT_STR
from cing.core.classes import Project
from pylab import * # preferred importing. Includes nx imports. #@UnusedWildImport
from random import random
from unittest import TestCase
import cing
import os #@Reimport
import unittest

class AllChecks(TestCase):
    
    def testResPlot(self):
        
        actuallyRunProcheck = False
        actuallyRunWhatif   = False
        showValues          = True
        #entryId = "1ai0" # Most complex molecular system in any PDB NMR entry 
#        entryId = "2hgh" # Small much studied PDB NMR entry; 48 models 
#        entryId = "1bus" # Small much studied PDB NMR entry:  5 models of 57 AA.: 285 residues.
        entryId = "1brv_1model" 
#        entryId = "2hgh_1model"
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
        project.initPDB( pdbFile=pdbFilePath, convention = "BMRB" )
        
        if actuallyRunProcheck:
            self.failIf(project.procheck(createPlots=False, runAqua=False) is None)                                    
        if actuallyRunWhatif:
            self.assertFalse(runWhatif(project))   
            
        pointsANGCHK = []
        pointsBNDCHK = []
        resNumb = 0
        for res in project.molecule.allResidues():
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
            accList = NTlist()
            sstList = NTlist()
            sstListPossibilities='HH' # secondary structure elements.
            
            for _modelID in range(2):
                if not actuallyRunWhatif:
                    angList.append(random()*10-2) # Simulate Z-scores.
                    bndList.append(random()*5-1)  # Simulate Z-scores.
                    accList.append(random()*4-2)  # Simulate Z-scores.
                if not actuallyRunProcheck:
                    sstList.append( sstListPossibilities[ int(random()*2)])  # Simulate secondary structure

            if not actuallyRunWhatif:
                self.assertFalse (   whatifResDict.setDeepByKeys(angList,  ANGCHK_STR,VALUE_LIST_STR) )
                self.assertFalse (   whatifResDict.setDeepByKeys(bndList,  BNDCHK_STR,VALUE_LIST_STR) )
                self.assertFalse (   whatifResDict.setDeepByKeys(accList,  INOCHK_STR,VALUE_LIST_STR) )
            if not actuallyRunProcheck:
                self.assertFalse ( procheckResDict.setDeepByKeys(sstList,  SECSTRUCT_STR) )

            if showValues:
                for d in [whatifResDict, procheckResDict]:
                    checkIDList = d.keys()
                    for checkID in checkIDList:
                        if d==whatifResDict:
                            valueList = d.getDeepByKeys(checkID,VALUE_LIST_STR)
                        else:
                            valueList = d.getDeepByKeys(checkID)
                        if checkID == ANGCHK_STR:                            
                            zScore = valueList.average()[0]
                            NTdebug( 'angle Z: %8.3f', zScore )
                            pointsANGCHK.append( (resNumb-.5, zScore) )
                        if checkID == BNDCHK_STR:                            
                            zScore = valueList.average()[0]
                            NTdebug( 'bond  Z: %8.3f', zScore )
                            pointsBNDCHK.append( (resNumb-.5, zScore) )
                                                
                        NTdebug("%10s valueList: %-80s" % ( checkID, valueList))
                
        p = ResPlot( molecule=project.molecule, yRange=(-2, 10))
        p.drawResIcons()
        
        p.lines(pointsANGCHK, plusPoint)
        p.lines(pointsBNDCHK, circlePoint)
#        p.show() # uncomment to see something
        
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
        helixIconList = HelixIconList(seq=width, xy=(x,y),width=width,height=height)
        self.assertFalse(helixIconList.addPatches())
        for p in helixIconList.patchList:
            ax.add_patch(p)        
        ax.set_xlim(xmax=10)
        ax.set_ylim(ymax=10)
#        show()
        
    def testZaagtand(self):
        t = arange( 0.,360.,1.)
        s = triangularList( t )
        plot(t,s)
#        show()
        
    def testTo3StateUpper(self):
        self.assertEquals(     to3StateUpper(['h','H']), ['H','H'])
        self.assertNotEquals(  to3StateUpper([' ','H']), ['H','H'])
        self.assertEquals(     to3StateUpper(['X','H']), [' ','H'])
        
if __name__ == "__main__":
    cing.verbosity = verbosityError
#    cing.verbosity = verbosityDebug
    unittest.main()
