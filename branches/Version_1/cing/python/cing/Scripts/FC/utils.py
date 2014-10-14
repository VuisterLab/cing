"""Utilities for working with CCPN/FC

Run example:

cd $D/NRG-CING/prep/F/br/1brv ; python $CINGROOT/python/cing/Scripts/FC/utils.py 1brv fcProcessEntry \
    $D/NRG-CING/prep/S/br/1brv/1brv.tgz 1brv_assign.tgz swapCheck
"""

from ccp.format.nmrStar.projectIO import NmrStarProjectFile
from ccpnmr.format.converters.PseudoPdbFormat import PseudoPdbFormat
from ccpnmr.format.process.stereoAssignmentSwap import StereoAssignmentCleanup
from cing import header
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.forkoff import do_cmd
from cing.Libs.helper import getStartMessage
from cing.Libs.helper import getStopMessage
from cing.Libs.pdb import defaultPrintChainCode
from cing.PluginCode.BMRB import bmrbAtomType2spinTypeCingMap
from cing.Scripts.FC.constants import * #@UnusedWildImport
from cing.Scripts.utils import printSequenceFromPdbFile
from cing.core.molecule import AssignmentCountMap
from glob import glob
from memops.general.Io import loadProject
from memops.general.Io import saveProject
from shutil import rmtree
import Tkinter
import tarfile

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
        nTmessageNoEOL('%s%s ' % (res.ccpCode, res.seqCode))
        if not (res.seqCode % 10):
            nTmessage('')
    nTmessage('')
    nTmessage("Sequence from CCPN project:")
    nTmessage(fastaString)

def importPseudoPdb(ccpnProject, inputDir, guiRoot, allowPopups=1, minimalPrompts=0, verbose=1, **presets):
    nTdebug("Using presets %s" % repr(presets))
    formatPseudoPdb = PseudoPdbFormat(ccpnProject, guiRoot, verbose=verbose, minimalPrompts=minimalPrompts, allowPopups=allowPopups)
    nmrProject = ccpnProject.currentNmrProject
#        nmrProject = project.newNmrProject(name=project.name)
    structureEnsembleList = ccpnProject.sortedStructureEnsembles()
    if len(structureEnsembleList) != 1:
        nTerror("Failed to find single structureEnsemble; instead found: %d" % len(structureEnsembleList) )
    structureEnsemble = ccpnProject.findFirstStructureEnsemble()
    if structureEnsemble:
        nTmessage("In importPseudoPdb, removing first found structureEnsemble")
        structureEnsemble.delete()
    else:
        nTwarning("No structureEnsemble found; can't remove it.")

    structureGenerationList = nmrProject.sortedStructureGenerations()
    if not structureGenerationList:
        nTdebug("No or empty structureGenerationList; creating a new one.")
        nmrProject.newStructureGeneration()
        structureGenerationList = nmrProject.sortedStructureGenerations()

    if len(structureGenerationList) != 1:
        nTerror("Failed to find single structureGeneration; instead found: %d" % len(structureGenerationList) )

    structureGeneration = structureGenerationList[0]
#        structureGeneration = nmrProject.findFirstStructureGeneration()
#        structureGeneration = nmrProject.newStructureGeneration()
    if not structureGeneration:
        nTerror("Failed to find or create structureGeneration")
        return True

    globPattern = inputDir + '/*.pdb'
    fileList = glob(globPattern)
    nTdebug("From %s will read files: %s" % (globPattern, fileList))
    if len(fileList) != 1:
        nTerror("Failed to find single PDB file; instead found list: %s" % repr(fileList))
        return True

    keywds = getDeepByKeysOrDefault(presets, {}, READ_COORDINATES, KEYWORDS)
    nTdebug("In importPseudoPdb: from getDeepByKeysOrDefault keywds: %s" % repr(keywds))
    reportDifference(ccpnProject, fileList[0])

    status = formatPseudoPdb.readCoordinates(fileList, strucGen=structureGeneration, linkAtoms=0, swapFirstNumberAtom=1,
        minimalPrompts=minimalPrompts, verbose=verbose, **keywds)
    if not status: # can return None or False on error
        nTerror("Failed to formatPseudoPdb.readCoordinates")
        return True # returns True on error

def swapCheck(nmrConstraintStore,structureEnsemble,numSwapCheckRuns=1):

    """
    Input:

    nmrConstraintStore
    structureEnsemble

    numSwapCheckRuns: number of times this swap check is performed. 1 should be enough

    """

    nTmessage("\n### Checking stereo swaps and deassignment ###")

#    swapCheck = StereoAssignmentSwapCheck(nmrConstraintStore,structureEnsemble,verbose = True)
    swapCheck = StereoAssignmentCleanup(nmrConstraintStore,structureEnsemble,verbose = True)

#    violationCodes = {'xl':                                             {'violation': 1.0,  'fraction': 0.00001},
#                       'l':                                             {'violation': 0.5,  'fraction': 0.5},
#                       StereoAssignmentCleanup.VIOLATION_CODE_S_STR:    {'violation': 0.001,'fraction': -999.9} 
# required for reporting smaller violations.
#                       }

    for _swapCheckRun in range(0,numSwapCheckRuns):
#      swapCheck.checkSwapsAndClean(violationCodes = violationCodes)
        swapCheck.checkSwapsAndClean()

    nTmessage("\n")
# end def

def fcProcessEntry( entry_code, ccpnTgzFile, outputCcpnTgzFile, functionToRun='swapCheck'):
    """
    E.g.

    entry_code          1brv
    ccpnTgzFile         /NRG-CING/prep/S/br/1brv/1brv.tgz Full path
    outputCcpnTgzFile   1brv_assign.tgz but inside the project will still be keyed and named 1brv.

    Return True on error
    Can be extended later on to run a different function.
    Will run in cwd.
    """

    # Adjust the parameters below
    isInteractive = False
    doSwapCheck = True
    doSaveProject = True
    doExport = True

    minimalPrompts = True
    verbose = True
    allowPopups = False

    if isInteractive:
        allowPopups = True
        minimalPrompts = False

    print 'entry_code                                                                                    ', entry_code
#    print 'bmrb_id                                                                                       ', bmrb_id
    print 'allowPopups                                                                                   ', allowPopups
    print 'isInteractive                                                                                 ', isInteractive
    print 'minimalPrompts                                                                                ', minimalPrompts
    print 'verbose                                                                                       ', verbose
    print 'doSwapCheck                                                                                   ', doSwapCheck
    print 'doSaveProject                                                                                 ', doSaveProject
    print 'doExport                                                                                      ', doExport

    guiRoot = None
    if allowPopups:
        guiRoot = Tkinter.Tk()

    if not os.path.exists(ccpnTgzFile):
        nTerror("Input file not found: %s" % ccpnTgzFile)
        return True
    nTdebug("Looking at %s" % entry_code)

    if os.path.exists(entry_code):
        nTmessage("Removing previous directory: %s" % entry_code)
        rmtree(entry_code)
    do_cmd("tar -xzf " + ccpnTgzFile) # will unpack to cwd.
    if os.path.exists('linkNmrStarData'):
        nTmessage("Renaming standard directory linkNmrStarData to entry: %s" % entry_code)
        os.rename('linkNmrStarData', entry_code)

    ccpnProject = loadProject(entry_code)
    if not ccpnProject:
        nTerror("Failed to read project: %s" % entry_code)
        return True

    if doSwapCheck:
#        constraintsHandler = ConstraintsHandler()
        nmrConstraintStore = ccpnProject.findFirstNmrConstraintStore()
        structureEnsemble = ccpnProject.findFirstStructureEnsemble()
        if nmrConstraintStore:
            if structureEnsemble:
                swapCheck(nmrConstraintStore, structureEnsemble)
            else:
                nTmessage("Failed to find structureEnsemble; skipping swapCheck")
        else:
            nTmessage("Failed to find nmrConstraintStore; skipping swapCheck")
#        constraintsHandler.swapCheck(nmrConstraintStore, structureEnsemble, numSwapCheckRuns)
    # end if doSwapCheck

    if doSaveProject:
        nTmessage('Saving to new path: %s' % entry_code)
        saveProject(ccpnProject, newPath=entry_code, removeExisting=True)
    if doExport:
        if os.path.exists(outputCcpnTgzFile):
            nTmessage("Overwriting: " + outputCcpnTgzFile)
        myTar = tarfile.open(outputCcpnTgzFile, mode='w:gz') # overwrites
        myTar.add(entry_code)
        myTar.close()
    if guiRoot:
        guiRoot.destroy()
# end def


def getBmrbCsCountsFromFile(inputStarFile):
    """Return None on error or a map on success"""
    assignmentCountMap = AssignmentCountMap()

    nmrStarFile = NmrStarProjectFile(inputStarFile)
    nmrStarFile.read(verbose=0)

    fileType, measurementType = ('chemShiftFiles', 'chemShifts')

    reportedSpinType = []
    for valuesFile in getattr(nmrStarFile, fileType):
#        nTdebug("getBmrbCsCountsFromFile valuesFile: %s" % valuesFile)
        valueList = getattr(valuesFile, measurementType)
#        nTdebug("getBmrbCsCountsFromFile size valueList: %s" % len(valueList))
        for value in valueList:
            # value is a ccp.format.nmrStar.chemShiftsIO.NmrStarChemShift instance
#            nTdebug("in NmrStar.NmrStarHandler.readNmrStarFile value: %s" % value)
            csAtomType = getDeepByKeysOrAttributes( bmrbAtomType2spinTypeCingMap, value.atomType )
#            resTypeBMRB = getDeepByKeysOrAttributes(  value, 'resLabel'' )
#            atomName = getDeepByKeysOrAttributes(  value, 'atomName' )
            if not csAtomType:
                if csAtomType not in reportedSpinType:
#                    nTdebug("Skipping CS for less common atom type: %s" %  value.atomType )
                    reportedSpinType.append(csAtomType)
                continue
            if not hasattr( assignmentCountMap, csAtomType ):
                if csAtomType not in reportedSpinType:
#                    nTdebug("Skipping CS for atom type unfit for CS: %s" % value)
                    reportedSpinType.append(csAtomType)
                continue
            assignmentCountMap[ csAtomType] += 1
        # end for
    # end for
#    nTdebug("Read: %s" % str(assignmentCountMap))
    return assignmentCountMap
# end def

if __name__ == '__main__':
    cing.verbosity = verbosityDebug

    nTmessage(header)
    nTmessage(getStartMessage())

    destination = sys.argv[1]
    hasPdbId = False
    entry_code = '.'
    if is_pdb_code(destination): # needs to be first argument if this main is to be used by doScriptOnEntryList.
        entry_code = destination
        hasPdbId = True
        destination = sys.argv[2]
    # end if

    startArgListOther = 2
    if hasPdbId:
        startArgListOther = 3
    argListOther = []
    if len(sys.argv) > startArgListOther:
        argListOther = sys.argv[startArgListOther:]
    nTmessage('\nGoing to destination: %s with(out) on entry_code %s with extra arguments %s' % (
                destination, entry_code, str(argListOther)))

    try:
        if destination == 'fcProcessEntry':
            ccpnTgzFile = argListOther[0]
            outputCcpnTgzFile = argListOther[1]
            functionToRun = argListOther[2]
            if fcProcessEntry( entry_code, ccpnTgzFile, outputCcpnTgzFile, functionToRun ):
                nTerror("Failed to fcProcessEntry")
        else:
            nTerror("Unknown destination: %s" % destination)
    except:
        nTtracebackError()
    finally:
        nTmessage(getStopMessage(cing.starttime))

