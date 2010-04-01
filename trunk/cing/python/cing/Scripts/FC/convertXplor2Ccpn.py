"""
Original from Wim Vranken.
Used for eNMR workshop Lyon data sets.
"""

from ccpnmr.format.converters.CnsFormat import CnsFormat
from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDebug
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import getDeepByKeys
from cing.Libs.forkoff import do_cmd
from cing.Scripts.FC.convertCyana2Ccpn import importPseudoPdb
from glob import glob
from memops.api import Implementation
import Tkinter
import cing
import os
import shutil


__author__     = cing.__author__ + "Wim Vranken <wim@ebi.ac.uk>"

def convertXplor2Ccpn(projectName, rootDir, inputDir="XPLOR", outputDir="CCPN"):
    """The structure when done will be:

    rootDir -> -> inputDir -> xxxx.pdb etc.
               -> outputDir -> xxxx -> ccp etc.
               -> xxxx.tgz (the resulting CCPN data)

    E.g.
    taf3Piscataway -> Authors ->  all.pdb etc.
                   -> Nijmegen -> taf3Piscataway -> ccp etc.
                   -> taf3Piscataway.tgz

    Or in iCingSetup the rootDir is eg: /Library/WebServer/Documents/tmp/cing/ano/WjtXOz
    with project name gb1

    WjtXOz -> XPLOR  -> gb1.pdb etc.
           -> CCPN   -> gb1 -> ccpn etc.
           -> gb1.tgz


    The in and out paths are relative to the rootDir.
            """
    inputDir = os.path.join(rootDir, inputDir)
    outputDir = os.path.join(rootDir, outputDir)

    if not os.path.exists(inputDir):
        NTerror("Failed to find")
    if os.path.exists(outputDir):
        shutil.rmtree(outputDir)

    os.mkdir(outputDir)
    os.chdir(outputDir)

    ccpnProjectPath = os.path.join(outputDir, projectName)
    if os.path.exists(ccpnProjectPath):
        shutil.rmtree(ccpnProjectPath)

    project = Implementation.MemopsRoot(name = projectName)

    guiRoot = Tkinter.Tk() #  headless possible?
    importXplorCoordinatesAndRestraints(project, inputDir, guiRoot, allowPopups=0, minimalPrompts=1, verbose=0)
    project.saveModified()
    tgzFileName = "../"+projectName + ".tgz"
    cmd = "tar -czf %s %s" % (tgzFileName, projectName)
    do_cmd(cmd)
    guiRoot.destroy()


def importXplorCoordinatesAndRestraints(ccpnProject, inputDir, guiRoot, replaceCoordinates=1, replaceRestraints=1, allowPopups=1, minimalPrompts=0, verbose=1, **presets):
    NTdebug("Using presets %s" % `presets`)

    if replaceCoordinates:
        status = importPseudoPdb(ccpnProject, inputDir, guiRoot, allowPopups=allowPopups, minimalPrompts=minimalPrompts, verbose=verbose, **presets)
        if status:
            NTerror("Failed importCyanaCoordinatesAndRestraints")
            return True

    if not replaceRestraints:
        return

    formatCns = CnsFormat(ccpnProject, guiRoot, verbose=verbose, minimalPrompts=minimalPrompts, allowPopups=allowPopups)
    ccpnConstraintListOfList = []
    globPattern = inputDir + '/*_noe.tbl'
    fileList = glob(globPattern)
    NTdebug("From %s will read files: %s" % (globPattern,fileList))
    for fn in fileList:
        fnBaseName = os.path.basename(fn).split('.')[0]
        ccpnConstraintList = formatCns.readDistanceConstraints(fn, minimalPrompts=minimalPrompts, verbose=verbose)
        ccpnConstraintList.setName(fnBaseName)
        ccpnConstraintListOfList.append( ccpnConstraintList )

    globPattern = inputDir + '/*_hbond.tbl'
    fileList = glob(globPattern)
    NTdebug("From %s will read in files: %s" % (globPattern,fileList))
    for fn in fileList:
        fnBaseName = os.path.basename(fn).split('.')[0]
        ccpnConstraintList = formatCns.readDistanceConstraints(fn, minimalPrompts=minimalPrompts, verbose=verbose)
        ccpnConstraintList.setName(fnBaseName)
        ccpnConstraintListOfList.append( ccpnConstraintList )

    globPattern = inputDir + '/*_dihe.tbl'
    fileList = glob(globPattern)
    NTdebug("From %s will read in total files: %s" % (globPattern,fileList))
    for fn in fileList:
        fnBaseName = os.path.basename(fn).split('.')[0]
        ccpnConstraintList = formatCns.readDihedralConstraints(fn, minimalPrompts=minimalPrompts, verbose=verbose)
        ccpnConstraintList.setName(fnBaseName)
        ccpnConstraintListOfList.append( ccpnConstraintList )


    ccpnConstraintList = getDeepByKeys( ccpnConstraintListOfList, 0) # no need to repeat
    NTdebug("First ccpnConstraintList: %s" % ccpnConstraintList)
    if ccpnConstraintList != None:
#    for i, ccpnConstraintList in enumerate(ccpnConstraintListOfList):
        NTdebug("ccpnConstraintList: %s" % ccpnConstraintList)
        nmrConstraintStore = ccpnConstraintList.nmrConstraintStore
        structureGeneration = nmrConstraintStore.findFirstStructureGeneration()
        formatCns.linkResonances(
                      forceDefaultChainMapping = 1,
                      globalStereoAssign = 1,
                      setSingleProchiral = 1,
                      setSinglePossEquiv = 1,
                      strucGen = structureGeneration,
                      allowPopups=allowPopups, minimalPrompts=minimalPrompts, verbose=verbose )

if __name__ == '__main__':
    cing.verbosity = verbosityDebug

#    xplorDir = os.path.join(cingDirTestsData, "xplor")
    xplorDir = os.path.join(cingDirTestsData, "eNMR")
#    projectName = sys.argv[0]
#    done: BASPLyon CuTTHAcisLyon
#    projectList = """  BASPLyon CuTTHAcisLyon CuTTHAtransLyon ParvulustatLyon
#    TTScoLyon VpR247Lyon apoTTHAcisLyon apoTTHAtransLyon mia40Lyon taf3Lyon wln34Lyon""".split()
#    projectList = """gb1""".split()
#    projectList = """1tgq""".split()
    projectList = [ "HR5537AUtrecht" ]
    # failed for
    # BASPLyon

    for projectName in projectList:
#        testDataEntry = os.path.join(xplorDir, projectName)
        testDataEntry = os.path.join(xplorDir, projectName, 'Authors')
        rootDir = os.path.join(cingDirTmp,projectName)
        inputDirRel="XPLOR"
        inputDir = os.path.join(rootDir, inputDirRel)
        if os.path.exists(rootDir):
            NTmessage("Removing original rootDir: %s" % rootDir)
            shutil.rmtree(rootDir)
        os.mkdir(rootDir)

        NTmessage("Copying input from %s to %s" % (testDataEntry, inputDir))
        shutil.copytree( testDataEntry, inputDir)
        convertXplor2Ccpn(projectName, rootDir)
