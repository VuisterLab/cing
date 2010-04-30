"""
Unit test execute as:
python $CINGROOT/python/cing/Libs/test/test_NTMoleculePlotCorrelation.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityError
from cing.Libs.NTmoleculePlot import KEY_LIST2_STR
from cing.Libs.NTmoleculePlot import KEY_LIST_STR
from cing.Libs.NTmoleculePlot import MoleculePlotSet
from cing.Libs.NTmoleculePlot import USE_ROG_FOR_COLOR_STR
from cing.Libs.NTmoleculePlot import XLABEL_STR
from cing.Libs.NTmoleculePlot import YLABEL_STR
from cing.Libs.NTplot import ResPlot
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
from cing.PluginCode.Whatif import WHATIF_STR
from cing.PluginCode.Whatif import Whatif
from cing.PluginCode.procheck import PROCHECK_STR
from cing.core.classes import Project
from cing.core.constants import * #@UnusedWildImport
from random import random
from unittest import TestCase
import os #@Reimport
import shutil
import unittest

class AllChecks(TestCase):

    # important to switch to temp space before starting to generate files for the project.
    os.chdir(cingDirTmp)

    def test_NTMoleculePlotCorrelation(self):

        showValues = False
        fastestTest = False

        htmlOnly = True # default is False but enable it for faster runs without some actual data.
        doWhatif = False # disables whatif actual run
        doProcheck = False
        doWattos = False
        useNrgArchive = False
        if fastestTest:
            htmlOnly = True
            doWhatif = False
            doProcheck = False
            doWattos = False


        modelNum = 1 # Only used when simulating data
        #entryId = "1ai0" # Most complex molecular system in any PDB NMR entry
#        entryId = "2hgh" # Small much studied PDB NMR entry; 48 models
#        entryId = "1bus" # Small much studied PDB NMR entry:  5 models of 57 AA.: 285 residues.
#        entryId = "2hgh_1model"
        entryId = "1hue"

        self.failIf(os.chdir(cingDirTmp), msg =
            "Failed to change to temp test directory for data: " + cingDirTmp)
        project = Project.open(entryId, status = 'new')
        self.assertTrue(project, 'Failed opening project: ' + entryId)
        if useNrgArchive: # default is False
            inputArchiveDir = os.path.join('/Library/WebServer/Documents/NRG-CING/recoordSync', entryId)
        else:
            inputArchiveDir = os.path.join(cingDirTestsData, "ccpn")

        ccpnFile = os.path.join(inputArchiveDir, entryId + ".tgz")
        self.assertTrue(project.initCcpn(ccpnFolder = ccpnFile))
        # Do not leave the old CCPN directory laying around since it might get added to by another test.
        if os.path.exists(entryId):
            self.assertFalse(shutil.rmtree(entryId))

        if doWhatif:
            self.assertFalse(project.validate(htmlOnly=htmlOnly,
                                              doProcheck = doProcheck,
                                              doWhatif=doWhatif,
                                              doWattos=doWattos ))

        else:
            rangeList = project.molecule.getFixedRangeList(
                max_length_range = ResPlot.MAX_WIDTH_IN_RESIDUES, ranges = None)
            resNumb = 0
            for resList in rangeList:
                for res in resList:
                    resNumb += 1

        #            NTdebug(`res`)
                    if resNumb % 2:
                        res.rogScore.setMaxColor(COLOR_RED, "just testing ROG color.")
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
                        if not doWhatif:
                            angList.append(random()*10 - 0) # Simulate abs max of Z-scores.
                            bndList.append(random()*5 + 1)  # offset by 1 but still want to start from zero?
                            quaList.append(random()*5 - 3 )
                            ramList.append(random()*5 + 0)
                            c12List.append(random()*5 -3 )
                            rotList.append(random()*5 + 0)
                            bbcList.append(random()*5 -3)
                            accList.append(random()*4 - 2)

                    if not doWhatif:
                        self.assertFalse (whatifResDict.setDeepByKeys(angList, ANGCHK_STR, VALUE_LIST_STR))
                        self.assertFalse (whatifResDict.setDeepByKeys(bndList, BNDCHK_STR, VALUE_LIST_STR))
                        self.assertFalse (whatifResDict.setDeepByKeys(quaList, QUACHK_STR, VALUE_LIST_STR))
                        self.assertFalse (whatifResDict.setDeepByKeys(ramList, RAMCHK_STR, VALUE_LIST_STR))
                        self.assertFalse (whatifResDict.setDeepByKeys(c12List, C12CHK_STR, VALUE_LIST_STR))
                        self.assertFalse (whatifResDict.setDeepByKeys(rotList, ROTCHK_STR, VALUE_LIST_STR))
                        self.assertFalse (whatifResDict.setDeepByKeys(bbcList, BBCCHK_STR, VALUE_LIST_STR))
                        self.assertFalse (whatifResDict.setDeepByKeys(accList, INOCHK_STR, VALUE_LIST_STR))

                    for d in [whatifResDict, procheckResDict]:
                        checkIDList = d.keys()
                        for checkID in checkIDList:
                            if d == whatifResDict:
                                valueList = d.getDeepByKeys(checkID, VALUE_LIST_STR)
                            else:
                                valueList = d.getDeepByKeys(checkID)
                            if showValues:
                                NTdebug("%10s valueList: %-80s" % (checkID, valueList))
        #end if actuallyRunWhatif:

        # The following object will be responsible for creating a (png/pdf) file with
        # possibly multiple pages
        # Level 1: row
        # Level 2: against main or alternative y-axis
        # Level 3: plot parameters dictionary (extendable).
        keyLoLoL = []
        plotAttributesRowMain = NTdict()
        # Now for a correlation specify the x, y series as consequetive
        # KEY_LIST_STR, KEY_LIST2_STR and subsequent correlations as:
        # KEY_LIST_STR3, KEY_LIST4_STR etc.
        plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR, QUACHK_STR, VALUE_LIST_STR ]
        plotAttributesRowMain[ KEY_LIST2_STR] = [ WHATIF_STR, RAMCHK_STR, VALUE_LIST_STR ]
        plotAttributesRowMain[ XLABEL_STR] = Whatif.shortNameDict[  QUACHK_STR ]
        plotAttributesRowMain[ YLABEL_STR] = Whatif.shortNameDict[  RAMCHK_STR ]
        plotAttributesRowMain[ USE_ROG_FOR_COLOR_STR] = True
        keyLoLoL.append([ [plotAttributesRowMain] ])
        #keyLoLoL.append( [ [plotAttributesRowMain], [plotAttributesRowAlte] ] ) future extension.
        plotAttributesRowMain = NTdict()
        plotAttributesRowMain[ KEY_LIST_STR] =  [ WHATIF_STR,          QUACHK_STR,         VALUE_LIST_STR ]
        plotAttributesRowMain[ KEY_LIST2_STR] = [ WHATIF_STR,          C12CHK_STR,         VALUE_LIST_STR ]
        plotAttributesRowMain[ XLABEL_STR]   = Whatif.shortNameDict[  QUACHK_STR ]
        plotAttributesRowMain[ YLABEL_STR]   = Whatif.shortNameDict[  C12CHK_STR ]
        plotAttributesRowMain[ USE_ROG_FOR_COLOR_STR] = True
        keyLoLoL.append( [ [plotAttributesRowMain] ] )

        # Next line also works when makeCorrelationPlot=True
        moleculePlotSet = MoleculePlotSet(project = project, ranges = None, keyLoLoL = keyLoLoL, makeCorrelationPlot = True)
        moleculePlotSet.renderMoleculePlotSet('residuePlotSetAll.pdf',
            createPngCopyToo = True)

if __name__ == "__main__":
    cing.verbosity = verbosityError
    cing.verbosity = verbosityDebug
    unittest.main()
