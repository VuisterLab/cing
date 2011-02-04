"""Utilities for working with CCPN/FC"""

from ccp.format.nmrStar.projectIO import NmrStarProjectFile
from ccpnmr.format.converters.PseudoPdbFormat import PseudoPdbFormat
from ccpnmr.format.process.stereoAssignmentSwap import StereoAssignmentSwapCheck
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.pdb import defaultPrintChainCode
from cing.Scripts.FC.constants import * #@UnusedWildImport
from cing.Scripts.utils import printSequenceFromPdbFile
from cing.core.molecule import AssignmentCountMap
from glob import glob
from cing.PluginCode.BMRB import bmrbAtomType2spinTypeCingMap

def reportDifference(ccpnProject, fn):
    printSequenceFromCcpnProject(ccpnProject)
    printSequenceFromPdbFile(fn)

def printSequenceFromCcpnProject(ccpnProject):
    molSystem = ccpnProject.findFirstMolSystem()
    firstChain = molSystem.findFirstChain()
#    print 'Code [%s], name [%s]' % (firstChain.code, firstChain.molecule.name)

    fastaString = ''

    for res in firstChain.sortedResidues():
        code1Letter = res.molResidue.chemComp.code1Letter
        if not code1Letter:
          code1Letter = defaultPrintChainCode

        fastaString += code1Letter
        NTmessageNoEOL('%s%s ' % (res.ccpCode, res.seqCode))
        if not (res.seqCode % 10):
            NTmessage('')
    NTmessage('')
    NTmessage("Sequence from CCPN project:")
    NTmessage(fastaString)

def importPseudoPdb(ccpnProject, inputDir, guiRoot, allowPopups=1, minimalPrompts=0, verbose=1, **presets):
    NTdebug("Using presets %s" % `presets`)
    formatPseudoPdb = PseudoPdbFormat(ccpnProject, guiRoot, verbose=verbose, minimalPrompts=minimalPrompts, allowPopups=allowPopups)
    nmrProject = ccpnProject.currentNmrProject
#        nmrProject = project.newNmrProject(name=project.name)
    structureEnsembleList = ccpnProject.sortedStructureEnsembles()
    if len(structureEnsembleList) != 1:
        NTerror("Failed to find single structureEnsemble; instead found: %d" % len(structureEnsembleList) )
    structureEnsemble = ccpnProject.findFirstStructureEnsemble()
    if structureEnsemble:
        NTmessage("In importPseudoPdb, removing first found structureEnsemble")
        structureEnsemble.delete()
    else:
        NTwarning("No structureEnsemble found; can't remove it.")

    structureGenerationList = nmrProject.sortedStructureGenerations()
    if not structureGenerationList:
        NTdebug("No or empty structureGenerationList; creating a new one.")
        nmrProject.newStructureGeneration()
        structureGenerationList = nmrProject.sortedStructureGenerations()

    if len(structureGenerationList) != 1:
        NTerror("Failed to find single structureGeneration; instead found: %d" % len(structureGenerationList) )

    structureGeneration = structureGenerationList[0]
#        structureGeneration = nmrProject.findFirstStructureGeneration()
#        structureGeneration = nmrProject.newStructureGeneration()
    if not structureGeneration:
        NTerror("Failed to find or create structureGeneration")
        return True

    globPattern = inputDir + '/*.pdb'
    fileList = glob(globPattern)
    NTdebug("From %s will read files: %s" % (globPattern, fileList))
    if len(fileList) != 1:
        NTerror("Failed to find single PDB file; instead found list: %s" % `fileList`)
        return True

    keywds = getDeepByKeysOrDefault(presets, {}, READ_COORDINATES, KEYWORDS)
    NTdebug("In importPseudoPdb: from getDeepByKeysOrDefault keywds: %s" % `keywds`)
    reportDifference(ccpnProject, fileList[0])

    status = formatPseudoPdb.readCoordinates(fileList, strucGen=structureGeneration, linkAtoms=0, swapFirstNumberAtom=1,
        minimalPrompts=minimalPrompts, verbose=verbose, **keywds)
    if not status: # can return None or False on error
        NTerror("Failed to formatPseudoPdb.readCoordinates")
        return True # returns True on error

def swapCheck(nmrConstraintStore,structureEnsemble,numSwapCheckRuns):

    """
    Input:

    nmrConstraintStore
    structureEnsemble

    numSwapCheckRuns: number of times this swap check is performed. 2 should be enough

    """

    print "\n### Checking stereo swaps and deassignment ###"

    swapCheck = StereoAssignmentSwapCheck(nmrConstraintStore,structureEnsemble,verbose = True)

#    violationCodes = {'xl': {'violation': 1.0, 'fraction': 0.00001},
#                      'l': {'violation': 0.5, 'fraction': 0.5}}
    # Use more restrictive cutoffs than the above defaults.
    violationCodes = {'xl': {'violation': 0.5, 'fraction': 0.00001},
                      'l': {'violation': 0.3, 'fraction': 0.5}}

    for _swapCheckRun in range(0,numSwapCheckRuns):
      swapCheck.checkSwapsAndClean(violationCodes = violationCodes)

    print
    print


def getBmrbCsCountsFromFile(inputStarFile):
    """Return None on error or a map on success"""
    assignmentCountMap = AssignmentCountMap()

    nmrStarFile = NmrStarProjectFile(inputStarFile)
    nmrStarFile.read(verbose=0)

    fileType, measurementType = ('chemShiftFiles', 'chemShifts')

    reportedSpinType = []
    for valuesFile in getattr(nmrStarFile, fileType):
#        NTdebug("getBmrbCsCountsFromFile valuesFile: %s" % valuesFile)
        valueList = getattr(valuesFile, measurementType)
#        NTdebug("getBmrbCsCountsFromFile size valueList: %s" % len(valueList))
        for value in valueList:
            # value is a ccp.format.nmrStar.chemShiftsIO.NmrStarChemShift instance
#            NTdebug("in NmrStar.NmrStarHandler.readNmrStarFile value: %s" % value)
            csAtomType = getDeepByKeysOrAttributes( bmrbAtomType2spinTypeCingMap, value.atomType )
#            resTypeBMRB = getDeepByKeysOrAttributes(  value, 'resLabel'' )
#            atomName = getDeepByKeysOrAttributes(  value, 'atomName' )
            if not csAtomType:
                if csAtomType not in reportedSpinType:
#                    NTdebug("Skipping CS for less common atom type: %s" %  value.atomType )
                    reportedSpinType.append(csAtomType)
                continue
            if not hasattr( assignmentCountMap, csAtomType ):
                if csAtomType not in reportedSpinType:
#                    NTdebug("Skipping CS for atom type unfit for CS: %s" % value)
                    reportedSpinType.append(csAtomType)
                continue
            assignmentCountMap[ csAtomType] += 1
        # end for
    # end for
#    NTdebug("Read: %s" % str(assignmentCountMap))
    return assignmentCountMap
# end def