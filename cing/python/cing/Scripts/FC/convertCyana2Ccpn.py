"""
Original from Wim Vranken.
Used for eNMR workshop Lyon data sets.
"""

from ccpnmr.format.converters.CyanaFormat import CyanaFormat
from ccpnmr.format.converters.PseudoPdbFormat import PseudoPdbFormat
from cing import verbosityDebug
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTmessageNoEOL
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import getDeepByKeys
from cing.Libs.NTutils import getDeepByKeysOrDefault
from cing.Libs.forkoff import do_cmd
from cing.Scripts.FC.constants import KEYWORDS
from cing.Scripts.FC.constants import READ_COORDINATES
from cing.core.classes import Project
from cing.core.constants import IUPAC
from glob import glob
from memops.api import Implementation
import Tkinter
import cing
import os
import shutil

__author__ = cing.__author__ + "Wim Vranken <wim@ebi.ac.uk>"

defaultPrintChainCode = '.'

def convert(projectName, rootDir):
    guiRoot = Tkinter.Tk()
    datasetDir = os.path.join(rootDir, projectName)
    nijmegenDir = os.path.join(datasetDir, "Nijmegen")
    authorDir = os.path.join(datasetDir, "Authors")
    os.chdir(nijmegenDir)

    projectPath = os.path.join(nijmegenDir, projectName)
    if os.path.exists(projectPath):
        shutil.rmtree(projectPath)

    project = Implementation.MemopsRoot(name=projectName)

    importCyanaCoordinatesAndRestraints(project, authorDir, guiRoot)
    project.saveModified()
    tgzFileName = "../" + projectName + ".tgz"
    cmd = "tar -czf %s %s" % (tgzFileName, projectName)
    do_cmd(cmd)
    guiRoot.destroy()

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


def printSequenceFromPdbFile(fn):
    verbosityOriginal = cing.verbosity
    cing.verbosity = cing.verbosityError
    entryId = 'getSequenceFromPdbFile'
    project = Project(entryId)
    project.removeFromDisk()
    project = Project.open(entryId, status='new')
    project.initPDB(pdbFile=fn, convention=IUPAC)
    fastaString = ''
    for res in project.molecule.allResidues():
        # db doesn't always exist.
        fastaString += getDeepByKeysOrDefault(res, defaultPrintChainCode, 'db', 'shortName')
    NTmessage("Sequence from PDB file:")
    NTmessage(fastaString)
    for res in project.molecule.allResidues():
        NTmessageNoEOL(res.shortName)
    NTmessage('')
    project.removeFromDisk()
    del project
    cing.verbosity = verbosityOriginal


def importPseudoPdb(ccpnProject, inputDir, guiRoot, allowPopups=1, minimalPrompts=0, verbose=1, **presets):
    NTdebug("Using presets %s" % `presets`)
    formatPseudoPdb = PseudoPdbFormat(ccpnProject, guiRoot, verbose=verbose, minimalPrompts=minimalPrompts, allowPopups=allowPopups)
    nmrProject = ccpnProject.currentNmrProject
#        nmrProject = project.newNmrProject(name=project.name)
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
    NTdebug("From getDeepByKeysOrDefault keywds: %s" % `keywds`)
    reportDifference(ccpnProject, fileList[0])

    status = formatPseudoPdb.readCoordinates(fileList, strucGen=structureGeneration, linkAtoms=0, swapFirstNumberAtom=1,
        minimalPrompts=minimalPrompts, verbose=verbose, **keywds)
    if not status: # can return None or False on error
        NTerror("Failed to formatPseudoPdb.readCoordinates")
        return True # returns True on error
#TODO: is this needed?
#    status = formatPseudoPdb.linkResonances(
#                  forceDefaultChainMapping = 1,
#                  globalStereoAssign = 1,
#                  setSingleProchiral = 1,
#                  setSinglePossEquiv = 1,
#                  strucGen = structureGeneration,
#                  allowPopups=allowPopups, minimalPrompts=minimalPrompts, verbose=verbose, **keywds )
#    if not status: # can return None or False on error
#        NTerror("Failed to formatPseudoPdb.linkResonances")
#        return True # returns True on error

def importCyanaCoordinatesAndRestraints(ccpnProject, inputDir, guiRoot, replaceCoordinates=1, replaceRestraints=1, allowPopups=1, minimalPrompts=0, verbose=1, **presets):

    if replaceCoordinates:
        status = importPseudoPdb(ccpnProject, inputDir, guiRoot, allowPopups=allowPopups, minimalPrompts=minimalPrompts, verbose=verbose, **presets)
        if status:
            NTerror("Failed importCyanaCoordinatesAndRestraints")
            return True
    if not replaceRestraints:
        return
    formatCyana = CyanaFormat(ccpnProject, guiRoot, verbose=verbose, minimalPrompts=minimalPrompts, allowPopups=allowPopups)

    ccpnConstraintListOfList = []

    globPattern = inputDir + '/*.upl'
    fileList = glob(globPattern)
    NTdebug("From %s will read files: %s" % (globPattern, fileList))
    for fn in fileList:
        fnBaseName = os.path.basename(fn).split('.')[0]
        ccpnConstraintList = formatCyana.readDistanceConstraints(fn, minimalPrompts=minimalPrompts, verbose=verbose)
        ccpnConstraintList.setName(fnBaseName)
        ccpnConstraintListOfList.append(ccpnConstraintList)


    globPattern = inputDir + '/*.aco'
    fileList = glob(globPattern)
    NTdebug("From %s will read in total files: %s" % (globPattern, fileList))
    for fn in fileList:
        fnBaseName = os.path.basename(fn).split('.')[0]
        ccpnConstraintList = formatCyana.readDihedralConstraints(fn, minimalPrompts=minimalPrompts, allowPopups=allowPopups, verbose=verbose)
        ccpnConstraintList.setName(fnBaseName)
        ccpnConstraintListOfList.append(ccpnConstraintList)


    ccpnConstraintList = getDeepByKeys(ccpnConstraintListOfList, 0) # no need to repeat
    NTdebug("ccpnConstraintList: %s" % ccpnConstraintList)
    if ccpnConstraintList:
        nmrConstraintStore = ccpnConstraintList.nmrConstraintStore
        structureGeneration = nmrConstraintStore.findFirstStructureGeneration()
        formatCyana.linkResonances(
                      forceDefaultChainMapping=1,
                      globalStereoAssign=1,
                      setSingleProchiral=1,
                      setSinglePossEquiv=1,
                      strucGen=structureGeneration,
                      allowPopups=allowPopups, minimalPrompts=minimalPrompts, verbose=verbose)


#    nmrConstraintStore = ccpnConstraintList.nmrConstraintStore
#    structureGeneration = nmrConstraintStore.findFirstStructureGeneration()

  # Many options are available - see ccpnmr.format.process.linkResonances
  #
  # The current options are the 'safest' to maintain the original information,
  # although bear in mind that here all atoms in the original list are
  # considered to be stereospecifically assigned
  #
  # Not needed or is it?
#    format2.linkResonances(
#                      forceDefaultChainMapping = 1,
#                      globalStereoAssign = 1,
#                      setSingleProchiral = 1,
#                      setSinglePossEquiv = 1,
##                      allowPopups = 0,
#                      strucGen = structureGeneration
#                      )

if __name__ == '__main__':

    cing.verbosity = verbosityDebug
    rootDir = "/Users/jd/eNMR"
#    projectName = sys.argv[0]
#    done: BASPLyon CuTTHAcisLyon
#    projectList = """  BASPLyon CuTTHAcisLyon CuTTHAtransLyon ParvulustatLyon
#    TTScoLyon VpR247Lyon apoTTHAcisLyon apoTTHAtransLyon mia40Lyon taf3Lyon wln34Lyon""".split()
#    projectList = """   CuTTHAtransFrankfurt ParvulustatFrankfurt TTScoFrankfurt apoTTHAcisFrankfurt apoTTHAtransFrankfurt mia40Frankfurt wln34Frankfurt """.split()
    projectList = [ "VpR247Lyon" ]
    # failed for
    # BASPLyon

    for projectName in projectList:
        convert(projectName, rootDir)
