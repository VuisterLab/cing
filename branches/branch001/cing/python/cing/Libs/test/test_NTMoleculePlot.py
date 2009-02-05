"""
Unit test execute as:
python $CINGROOT/python/cing/Libs/test/test_NTMoleculePlot.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityError
from cing.Libs.NTmoleculePlot import KEY_LIST_STR
from cing.Libs.NTmoleculePlot import MoleculePlotSet
from cing.Libs.NTmoleculePlot import YLABEL_STR
from cing.Libs.NTplot import ResPlot
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
from cing.PluginCode.Whatif import ROTCHK_STR
from cing.PluginCode.Whatif import VALUE_LIST_STR
from cing.PluginCode.Whatif import WHATIF_STR
from cing.PluginCode.Whatif import Whatif
from cing.PluginCode.Whatif import runWhatif
from cing.PluginCode.procheck import PROCHECK_STR
from cing.core.classes import Project
from cing.core.constants import CYANA
from cing.core.constants import IUPAC
from random import random
from unittest import TestCase
import cing
import os #@Reimport
import unittest
#from cing.Libs.NTmoleculePlot import USE_ZERO_FOR_MIN_VALUE_STR
#from pylab import * # preferred importing. Includes nx imports. #@UnusedWildImport

class AllChecks(TestCase):

    # important to switch to temp space before starting to generate files for the project.
    os.chdir(cingDirTmp)
    NTdebug("Using matplot (True) or biggles: %s", useMatPlotLib)

    def testMoleculePlot(self):

        actuallyRunWhatif   = True
        showValues          = True

        modelNum            = 2 # Only used when simulating data
        #entryId = "1ai0" # Most complex molecular system in any PDB NMR entry
#        entryId = "2hgh" # Small much studied PDB NMR entry; 48 models
#        entryId = "1bus" # Small much studied PDB NMR entry:  5 models of 57 AA.: 285 residues.
#        entryId = "2hgh_1model"
        entryId = "1brv_1model"
#        entryId = "1brv_1model"

        pdbConvention = IUPAC
        ranges = None
        if entryId.startswith("2hgh"):
            pdbConvention = CYANA
            # Compile a NTlist instance with residue objects.
#            ranges = "2-54,111-136,145-193"
            ranges = None
                # 1 and 55 are 5' and 3' terminii which are a little looser.
                # 12, and 34 are bases that are not basepaired.
                # 191-193 are bound ZN ions.
        elif entryId.startswith("1brv"):
            # Truncate from Val171-Glu189 to:
#            ranges = "175-188"
            ranges = None

        self.failIf( os.chdir(cingDirTmp), msg=
            "Failed to change to temp test directory for data: "+cingDirTmp)
        project = Project( entryId )
        project.removeFromDisk()
        project = Project.open( entryId, status='new' )
        cyanaDirectory = os.path.join(cingDirTestsData,"cyana", entryId)
        pdbFileName = entryId+".pdb"
        pdbFilePath = os.path.join( cyanaDirectory, pdbFileName)
        NTdebug("Reading files from directory: " + cyanaDirectory)
        # Fast
        project.initPDB( pdbFile=pdbFilePath, convention = pdbConvention )

        if actuallyRunWhatif:
            self.assertFalse(runWhatif(project))
        else:
            rangeList = project.molecule.getFixedRangeList(
                max_length_range = ResPlot.MAX_WIDTH_IN_RESIDUES, ranges=ranges )
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
                    rotList = NTlist()
                    bbcList = NTlist()
                    accList = NTlist()

                    for _modelID in range(modelNum):
                        if not actuallyRunWhatif:
                            angList.append(random()*10-0) # Simulate abs max of Z-scores.
                            bndList.append(random()*5+1)  # offset by 1 but still want to start from zero?
                            quaList.append(random()*5+1)
                            ramList.append(random()*5+1)
                            c12List.append(random()*5+1)
                            rotList.append(random()*5+1)
                            bbcList.append(random()*5+1)
                            accList.append(random()*4-2)

                    if not actuallyRunWhatif:
                        self.assertFalse (   whatifResDict.setDeepByKeys(angList,  ANGCHK_STR,VALUE_LIST_STR) )
                        self.assertFalse (   whatifResDict.setDeepByKeys(bndList,  BNDCHK_STR,VALUE_LIST_STR) )
                        self.assertFalse (   whatifResDict.setDeepByKeys(quaList,  QUACHK_STR,VALUE_LIST_STR) )
                        self.assertFalse (   whatifResDict.setDeepByKeys(ramList,  RAMCHK_STR,VALUE_LIST_STR) )
                        self.assertFalse (   whatifResDict.setDeepByKeys(c12List,  C12CHK_STR,VALUE_LIST_STR) )
                        self.assertFalse (   whatifResDict.setDeepByKeys(rotList,  ROTCHK_STR,VALUE_LIST_STR) )
                        self.assertFalse (   whatifResDict.setDeepByKeys(bbcList,  BBCCHK_STR,VALUE_LIST_STR) )
                        self.assertFalse (   whatifResDict.setDeepByKeys(accList,  INOCHK_STR,VALUE_LIST_STR) )

                    for d in [whatifResDict, procheckResDict]:
                        checkIDList = d.keys()
                        for checkID in checkIDList:
                            if d==whatifResDict:
                                valueList = d.getDeepByKeys(checkID,VALUE_LIST_STR)
                            else:
                                valueList = d.getDeepByKeys(checkID)
                            if showValues:
                                NTdebug("%10s valueList: %-80s" % ( checkID, valueList))
        #end if actuallyRunWhatif:

        # The following object will be responsible for creating a (png/pdf) file with
        # possibly multiple pages
        # Level 1: row
        # Level 2: against main or alternative y-axis
        # Level 3: plot parameters dictionary (extendable).
        keyLoLoL = []
        plotAttributesRowMain = NTdict()
        plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          QUACHK_STR,         VALUE_LIST_STR ]
        plotAttributesRowMain[ YLABEL_STR]   = Whatif.shortNameDict[  QUACHK_STR ]
        keyLoLoL.append( [ [plotAttributesRowMain] ] )

        plotAttributesRowMain = NTdict()
        plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          RAMCHK_STR,         VALUE_LIST_STR ]
        plotAttributesRowMain[ YLABEL_STR]   = Whatif.shortNameDict[  RAMCHK_STR ]
        keyLoLoL.append( [ [plotAttributesRowMain] ] )

        plotAttributesRowMain = NTdict()
        plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          BBCCHK_STR,         VALUE_LIST_STR ]
        plotAttributesRowMain[ YLABEL_STR]   = Whatif.shortNameDict[  BBCCHK_STR ]
        keyLoLoL.append( [ [plotAttributesRowMain] ] )

        plotAttributesRowMain = NTdict()
        plotAttributesRowAlte = NTdict()
        plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR,          C12CHK_STR,         VALUE_LIST_STR ]
        plotAttributesRowAlte[ KEY_LIST_STR] = [ WHATIF_STR,          ROTCHK_STR,         VALUE_LIST_STR ]
        plotAttributesRowMain[ YLABEL_STR]   = Whatif.shortNameDict[  C12CHK_STR ]
        plotAttributesRowAlte[ YLABEL_STR]   = Whatif.shortNameDict[  ROTCHK_STR ]
#        plotAttributesRowMain[ USE_ZERO_FOR_MIN_VALUE_STR]   = True
        keyLoLoL.append( [ [plotAttributesRowMain], [plotAttributesRowAlte] ] )



        moleculePlotSet = MoleculePlotSet(project=project, ranges=ranges, keyLoLoL=keyLoLoL )
        moleculePlotSet.renderMoleculePlotSet( 'residuePlotSetAll.pdf',
            createPngCopyToo=True  )

if __name__ == "__main__":
    cing.verbosity = verbosityError
    cing.verbosity = verbosityDebug
    unittest.main()
