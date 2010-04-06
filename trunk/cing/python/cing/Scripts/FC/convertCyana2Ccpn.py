"""
See doc in convertXplor2Ccpn.py
"""

from ccpnmr.format.converters.CyanaFormat import CyanaFormat
from cing import verbosityDebug
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import getDeepByKeys
from cing.Libs.forkoff import do_cmd
from cing.Scripts.FC.utils import importPseudoPdb
from glob import glob
from memops.api import Implementation
import Tkinter
import cing
import os
import shutil

__author__ = cing.__author__ + "Wim Vranken <wim@ebi.ac.uk>"


def convertCyana2Ccpn(projectName, rootDir):
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
        convertCyana2Ccpn(projectName, rootDir)
