"""
Original from Wim Vranken.
Used for eNMR workshop Lyon data sets.
"""

from ccpnmr.format.converters.CyanaFormat import CyanaFormat
from ccpnmr.format.converters.PseudoPdbFormat import PseudoPdbFormat
from cing import verbosityDebug
from cing.Libs.NTutils import NTdebug
from cing.Libs.forkoff import do_cmd
from glob import glob
from memops.api import Implementation
import Tkinter
import cing
import os
import shutil

__author__ = cing.__author__ + "Wim Vranken <wim@ebi.ac.uk>"


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

    nmrProject = project.newNmrProject(name=project.name)
    structureGeneration = nmrProject.newStructureGeneration()
    format = PseudoPdbFormat(project, guiRoot, verbose=1)

    globPattern = authorDir + '/*.pdb'
    fileList = glob(globPattern)
    NTdebug("From %s will read files: %s" % (globPattern, fileList))
    format.readCoordinates(fileList, strucGen=structureGeneration, minimalPrompts=1,
                      allowPopups=0,
                           linkAtoms=0,
                           swapFirstNumberAtom=1)

    importCyanaRestraints()
    project.saveModified()
    tgzFileName = "../" + projectName + ".tgz"
    cmd = "tar -czf %s %s" % (tgzFileName, projectName)
    do_cmd(cmd)
    guiRoot.destroy()

def importCyanaRestraints(project, restraintsDir, guiRoot, allowPopups=0):
#    guiRoot = Tkinter.Tk()
    format = CyanaFormat(project, guiRoot, verbose=0, minimalPrompts=1, allowPopups=allowPopups)

    ccpnConstraintListOfList = []

    globPattern = restraintsDir + '/*.upl'
    fileList = glob(globPattern)
    NTdebug("From %s will read files: %s" % (globPattern, fileList))
    for file in fileList:
        ccpnConstraintList = format.readDistanceConstraints(fileList[0])
        ccpnConstraintListOfList.append(ccpnConstraintList)


    globPattern = restraintsDir + '/*.aco'
    fileList = glob(globPattern)
    NTdebug("From %s will read in total files: %s" % (globPattern, fileList))
    if fileList:
        ccpnConstraintList = format.readDihedralConstraints(fileList[0])
        ccpnConstraintListOfList.append(ccpnConstraintList)

  # Many options are available - see ccpnmr.format.process.linkResonances
  #
  # The current options are the 'safest' to maintain the original information,
  # although bear in mind that here all atoms in the original list are
  # considered to be stereospecifically assigned
  #
    for ccpnConstraintList in (ccpnConstraintListOfList):
        nmrConstraintStore = ccpnConstraintList.nmrConstraintStore
        structureGeneration = nmrConstraintStore.findFirstStructureGeneration()
        format.linkResonances(
                      forceDefaultChainMapping=1,
                      globalStereoAssign=1,
                      setSingleProchiral=1,
                      setSinglePossEquiv=1,
                      strucGen=structureGeneration,
                      verbose=0,
                      allowPopups=allowPopups,
                      minimalPrompts=1
                      )



    nmrConstraintStore = ccpnConstraintList.nmrConstraintStore
    structureGeneration = nmrConstraintStore.findFirstStructureGeneration()

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
