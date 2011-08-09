"""
Unit test execute as:
python $CINGROOT/python/cing/Libs/test/test_NTMoleculePlot.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.html import image2DdihedralWidth
from cing.Libs.html import image2Ddihedralheight
from cing.PluginCode.matplib import * #@UnusedWildImport
from cing.PluginCode.required.reqWhatif import * #@UnusedWildImport
from cing.PluginCode.dssp import Dssp #@UnusedImport needed to throw a ImportWarning so that the test is handled properly.
from cing.PluginCode.Whatif import Whatif #@UnusedImport needed to throw a ImportWarning so that the test is handled properly.
from cing.core.classes import Project
from cing.core.constants import * #@UnusedWildImport
from unittest import TestCase
import unittest
#from pylab import * # preferred importing. Includes nx imports. #@UnusedWildImport

class AllChecks(TestCase):

    # important to switch to temp space before starting to generate files for the project.
    cingDirTmpTest = os.path.join( cingDirTmp, 'test_NTMoleculePlot' )
    mkdirs( cingDirTmpTest )
    os.chdir(cingDirTmpTest)

    def testMoleculePlot(self):

        actuallyRunWhatif = False
        showValues = False

        modelNum = 1 # Only used when simulating data
        #entryId = "1ai0" # Most complex molecular system in any PDB NMR entry
#        entryId = "2hgh" # Small much studied PDB NMR entry; 48 models
        entryId = "1bus" # Small much studied PDB NMR entry:  5 models of 57 AA.: 285 residues.
#        entryId = "2hgh_1model"
#        entryId = "1brv_1model"

        pdbConvention = CYANA
        restraintsConvention = CYANA

#        ranges = None
        ranges = 'cv'
        if entryId.startswith("2hgh"):
            pdbConvention = CYANA
            # Compile a NTlist instance with residue objects.
            ranges = "2-54,111-136,145-193"
            ranges = None
                # 1 and 55 are 5' and 3' terminii which are a little looser.
                # 12, and 34 are bases that are not basepaired.
                # 191-193 are bound ZN ions.
        elif entryId.startswith("1brv"):
            # Truncate from Val171-Glu189 to:
            ranges = "175-188"
#            ranges = None
        elif entryId.startswith("1bus"):
            ranges = "6-13,29-45"

        project = Project(entryId)
        project.removeFromDisk()
        project = Project.open(entryId, status='new')
        cyanaDirectory = os.path.join(cingDirTestsData, "cyana", entryId)
#        pdbFileName = entryId + ".pdb"
#        pdbFilePath = os.path.join(cyanaDirectory, pdbFileName)
        nTdebug("Reading files from directory: " + cyanaDirectory)

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
        self.assertTrue(project.cyana2cing(cyanaDirectory = cyanaDirectory,
                           convention = restraintsConvention,
                           coordinateConvention = pdbConvention,
                           copy2sources = True,
                           **kwds))

#        project.validate(parseOnly=False, htmlOnly=True, doProcheck=False, doWhatif=False, doWattos=False, doTalos=False) # needed?

        self.assertFalse( project.molecule.setRanges(ranges) )
        from cing.PluginCode.dssp import runDssp # Triggers checks. @UnusedImport

        project.runDssp()
        if actuallyRunWhatif:
            from cing.PluginCode.Whatif import runWhatif # Triggers checks.
            self.assertFalse(runWhatif(project))
        else:
            rangeList = project.molecule.getFixedRangeList(
                max_length_range=ResPlot.MAX_WIDTH_IN_RESIDUES)
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
                                nTdebug("%10s valueList: %-80s" % (checkID, valueList))
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
        plotAttributesRowMain[ KEY_LIST_STR] = [ CHK_STR, RAMACHANDRAN_CHK_STR, VALUE_STR ]
        plotAttributesRowMain[ YLABEL_STR] = 'Z phi/psi'
        keyLoLoL.append([ [plotAttributesRowMain]])

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

        nTdebug("Instantiating moleculePlotSet")
        moleculePlotSet = MoleculePlotSet(project=project, keyLoLoL=keyLoLoL)
        pdfPath = '%s/test_NTMoleculePlot.pdf' % self.cingDirTmpTest
        moleculePlotSet.renderMoleculePlotSet(pdfPath, createPngCopyToo=True)

    def _testDihedralComboPlot(self):
        ps = NTplotSet() # closes any previous plots
        ps.hardcopySize = (image2DdihedralWidth, image2Ddihedralheight)
        dihedralName1 = 'PHI'
        dihedralName2 = 'PSI'
        projectName = 'testDihedralComboPlot'
        project     = Project(projectName)
        plotparams1 = project.plotParameters.getdefault(dihedralName1,'dihedralDefault')
        plotparams2 = project.plotParameters.getdefault(dihedralName1,'dihedralDefault')

        plot = NTplot(title=projectName,
          xRange=(plotparams1.min, plotparams1.max),
          xTicks=range(int(plotparams1.min), int(plotparams1.max + 1), plotparams1.ticksize),
          xLabel=dihedralName1,
          yRange=(plotparams2.min, plotparams2.max),
          yTicks=range(int(plotparams2.min), int(plotparams2.max + 1), plotparams2.ticksize),
          yLabel=dihedralName2)

        ps.addPlot(plot)
        ps.hardcopy(projectName, 'png')

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
