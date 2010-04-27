"""
Unit test execute as:
python $CINGROOT/python/cing/Libs/test/test_NTMoleculePlot.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityError
from cing.Libs.NTmoleculePlot import KEY_LIST2_STR
from cing.Libs.NTmoleculePlot import KEY_LIST3_STR
from cing.Libs.NTmoleculePlot import KEY_LIST4_STR
from cing.Libs.NTmoleculePlot import KEY_LIST_STR
from cing.Libs.NTmoleculePlot import MoleculePlotSet
from cing.Libs.NTmoleculePlot import USE_MAX_VALUE_STR
from cing.Libs.NTmoleculePlot import USE_ZERO_FOR_MIN_VALUE_STR
from cing.Libs.NTmoleculePlot import YLABEL_STR
from cing.Libs.NTplot import ResPlot
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTlist
from cing.PluginCode.required.reqProcheck import PROCHECK_STR
from cing.PluginCode.required.reqWhatif import * #@UnusedWildImport
from cing.core.classes import Project
from cing.core.constants import * #@UnusedWildImport
from random import random
from unittest import TestCase
import os #@Reimport
import unittest
#from cing.Libs.NTmoleculePlot import USE_ZERO_FOR_MIN_VALUE_STR
#from pylab import * # preferred importing. Includes nx imports. #@UnusedWildImport

class AllChecks(TestCase):

    # important to switch to temp space before starting to generate files for the project.
    os.chdir(cingDirTmp)

    def testMoleculePlot(self):

        actuallyRunWhatif = False
        showValues = False

        modelNum = 2 # Only used when simulating data
        #entryId = "1ai0" # Most complex molecular system in any PDB NMR entry
#        entryId = "2hgh" # Small much studied PDB NMR entry; 48 models
#        entryId = "1bus" # Small much studied PDB NMR entry:  5 models of 57 AA.: 285 residues.
#        entryId = "2hgh_1model"
#        entryId = "1brv_1model"
        entryId = "1brv"

        pdbConvention = CYANA
        restraintsConvention = CYANA

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

        self.failIf(os.chdir(cingDirTmp), msg=
            "Failed to change to temp test directory for data: " + cingDirTmp)
        project = Project(entryId)
        project.removeFromDisk()
        project = Project.open(entryId, status='new')
        cyanaDirectory = os.path.join(cingDirTestsData, "cyana", entryId)
#        pdbFileName = entryId + ".pdb"
#        pdbFilePath = os.path.join(cyanaDirectory, pdbFileName)
        NTdebug("Reading files from directory: " + cyanaDirectory)

        kwds = {}
        kwds['pdbFile'] = entryId
        kwds['nmodels'] = modelNum


        # Skip restraints if absent.
        if os.path.exists(os.path.join(cyanaDirectory, entryId + ".upl")):
            kwds['uplFiles'] = [entryId]
        if os.path.exists(os.path.join(cyanaDirectory, entryId + ".aco")) and not entryId.startswith("1YWUcdGMP"):
            kwds['acoFiles'] = [ entryId ]

        if os.path.exists(os.path.join(cyanaDirectory, entryId + ".seq")):
            kwds['seqFile'] = entryId

        if os.path.exists(os.path.join(cyanaDirectory, entryId + ".seq")):
            kwds['seqFile'] = entryId

        if os.path.exists(os.path.join(cyanaDirectory, entryId + ".prot")):
            self.assertTrue(os.path.exists(os.path.join(cyanaDirectory, entryId + ".seq")),
                "Converter for cyana also needs a seq file before a prot file can be imported")
            kwds['protFile'] = entryId
            kwds['seqFile'] = entryId
        project.cyana2cing(cyanaDirectory = cyanaDirectory,
                           convention = restraintsConvention,
                           coordinateConvention = pdbConvention,
                           copy2sources = True,
                           **kwds)

        project.validate(parseOnly=False, htmlOnly=True, doProcheck=False, doWhatif=False, doWattos=False, doTalos=False)
#        project.runDssp()
        if actuallyRunWhatif:
            from cing.PluginCode.Whatif import runWhatif
            self.assertFalse(runWhatif(project))
        else:
            rangeList = project.molecule.getFixedRangeList(
                max_length_range=ResPlot.MAX_WIDTH_IN_RESIDUES, ranges=ranges)
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
                            angList.append(random()*10 - 0) # Simulate abs max of Z-scores.
                            bndList.append(random()*5 + 1)  # offset by 1 but still want to start from zero?
                            quaList.append(random()*100 + 1)
                            ramList.append(random()*5 + 1)
                            c12List.append(random()*5 + 1)
                            rotList.append(random()*5 + 1)
                            bbcList.append(random()*5 + 1)
                            accList.append(random()*4 - 2)

                    if not actuallyRunWhatif:
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
        plotAttributesRowAlte = NTdict()
        plotAttributesRowMain[ KEY_LIST_STR] = [ PHI_STR, CV_STR ]
        plotAttributesRowMain[ KEY_LIST2_STR] = [ PSI_STR, CV_STR ]
        plotAttributesRowAlte[ KEY_LIST_STR] = [ 'cv_backbone' ]
        plotAttributesRowMain[ YLABEL_STR] = 'cv phi/psi'
        plotAttributesRowAlte[ YLABEL_STR] = 'cv backbone'
        plotAttributesRowMain[ USE_ZERO_FOR_MIN_VALUE_STR] = True
#        plotAttributesRowMain[ USE_MAX_VALUE_STR] = 0.2
        keyLoLoL.append([ [plotAttributesRowMain], [plotAttributesRowAlte] ])

        plotAttributesRowMain = NTdict()
        plotAttributesRowAlte = NTdict()
        plotAttributesRowMain[ KEY_LIST_STR] = [ CHI1_STR, CV_STR ]
        plotAttributesRowMain[ KEY_LIST2_STR] = [ CHI2_STR, CV_STR ]
        plotAttributesRowAlte[ KEY_LIST_STR] = [ 'cv_sidechain' ]
        plotAttributesRowMain[ YLABEL_STR] = 'cv chi1/2'
        plotAttributesRowAlte[ YLABEL_STR] = 'cv sidechain'
        plotAttributesRowMain[ USE_ZERO_FOR_MIN_VALUE_STR] = True
#        plotAttributesRowMain[ USE_MAX_VALUE_STR]   = 1.0
        keyLoLoL.append([ [plotAttributesRowMain], [plotAttributesRowAlte] ])

        plotAttributesRowMain = NTdict()
        plotAttributesRowAlte = NTdict()
        plotAttributesRowMain[ KEY_LIST_STR] = [ RMSD_STR, BACKBONE_AVERAGE_STR, VALUE_STR ]
        plotAttributesRowAlte[ KEY_LIST_STR] = [ RMSD_STR, HEAVY_ATOM_AVERAGE_STR, VALUE_STR ]
        plotAttributesRowMain[ YLABEL_STR] = BACKBONE_AVERAGE_STR
        plotAttributesRowAlte[ YLABEL_STR] = HEAVY_ATOM_AVERAGE_STR
        plotAttributesRowMain[ USE_ZERO_FOR_MIN_VALUE_STR] = True
        keyLoLoL.append([ [plotAttributesRowMain], [plotAttributesRowAlte] ])

        plotAttributesRowMain = NTdict()
        plotAttributesRowAlte = NTdict()
        plotAttributesRowMain[ KEY_LIST_STR] = [ WHATIF_STR, C12CHK_STR, VALUE_LIST_STR ]
        plotAttributesRowAlte[ KEY_LIST_STR] = [ WHATIF_STR, ROTCHK_STR, VALUE_LIST_STR ]
        plotAttributesRowAlte[ KEY_LIST2_STR] = [ WHATIF_STR, RAMCHK_STR, VALUE_LIST_STR ]
        plotAttributesRowMain[ YLABEL_STR] = C12CHK_STR
        plotAttributesRowAlte[ YLABEL_STR] = ROTCHK_STR
        plotAttributesRowMain[ USE_ZERO_FOR_MIN_VALUE_STR] = True
#        plotAttributesRowMain[ USE_MAX_VALUE_STR] = 10.0
        keyLoLoL.append([ [plotAttributesRowMain], [plotAttributesRowAlte] ])

        plotAttributesRowMain = NTdict()
        plotAttributesRowMain[ KEY_LIST_STR] = [ QSHIFT_STR, ALL_ATOMS_STR]
        plotAttributesRowMain[ KEY_LIST2_STR] = [ QSHIFT_STR, BACKBONE_STR]
        plotAttributesRowMain[ KEY_LIST3_STR] = [ QSHIFT_STR, HEAVY_ATOMS_STR]
        plotAttributesRowMain[ KEY_LIST4_STR] = [ QSHIFT_STR, PROTONS_STR]
        plotAttributesRowMain[ YLABEL_STR] = 'QCS all/bb/hvy/prt'
        plotAttributesRowMain[ USE_ZERO_FOR_MIN_VALUE_STR] = True
#        plotAttributesRowMain[ USE_VERBOSE_Y_LOCATOR_STR ] = True
        plotAttributesRowMain[ USE_MAX_VALUE_STR] = 0.5
        keyLoLoL.append([ [plotAttributesRowMain] ])


#BACKBONE_STR = 'backbone'
#HEAVY_ATOMS_STR = 'heavyAtoms'
#PROTONS_STR = 'protons'


        moleculePlotSet = MoleculePlotSet(project=project, ranges=ranges, keyLoLoL=keyLoLoL)
        moleculePlotSet.renderMoleculePlotSet('test_NTMoleculePlot.pdf',
            createPngCopyToo=True)

if __name__ == "__main__":
    cing.verbosity = verbosityError
    cing.verbosity = verbosityDebug
    unittest.main()
