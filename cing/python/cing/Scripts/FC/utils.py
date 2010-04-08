"""Utilities for working with CCPN/FC"""

from ccpnmr.format.converters.PseudoPdbFormat import PseudoPdbFormat
from ccpnmr.format.process.stereoAssignmentSwap import StereoAssignmentSwapCheck
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTmessageNoEOL
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import getDeepByKeysOrDefault
from cing.Libs.pdb import defaultPrintChainCode
from cing.Scripts.FC.constants import KEYWORDS
from cing.Scripts.FC.constants import READ_COORDINATES
from cing.Scripts.utils import printSequenceFromPdbFile
from glob import glob

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
        NTmessageNoEOL('%s%s' % (res.ccpCode, res.seqCode))
        if not (res.seqCode % 50):
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
        NTmessage("Removing first found structureEnsemble")
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
#    NTdebug("From getDeepByKeysOrDefault keywds: %s" % `keywds`)
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
