"""
Original from Wim Vranken.
Used for eNMR/weNMR workshop data sets.
"""

from ccpnmr.format.converters.CnsFormat import CnsFormat
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.forkoff import do_cmd
from cing.Scripts.FC.constants import * #@UnusedWildImport
from cing.Scripts.FC.utils import importPseudoPdb
from glob import glob
from memops.api import Implementation
import Tkinter
import shutil


__author__ = cing.__author__ + "Wim Vranken <wim@ebi.ac.uk>"

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
        nTerror("Failed to find")
    if os.path.exists(outputDir):
        shutil.rmtree(outputDir)

    os.mkdir(outputDir)
    os.chdir(outputDir)

    ccpnProjectPath = os.path.join(outputDir, projectName)
    if os.path.exists(ccpnProjectPath):
        shutil.rmtree(ccpnProjectPath)

    project = Implementation.MemopsRoot(name=projectName)

    guiRoot = Tkinter.Tk() #  headless possible?
    importXplorCoorAndRes(project, inputDir, guiRoot, allowPopups=0, minimalPrompts=1, verbose=0)
    project.saveModified()
    tgzFileName = "../" + projectName + ".tgz"
    cmd = "tar -czf %s %s" % (tgzFileName, projectName)
    do_cmd(cmd)
    guiRoot.destroy()


def importXplorCoorAndRes(ccpnProject, inputDir, guiRoot, replaceCoordinates=1, replaceRestraints=1, 
                          allowPopups=1, minimalPrompts=0, verbose=1, **presets):

    if replaceCoordinates:
        status = importPseudoPdb(ccpnProject, inputDir, guiRoot, allowPopups=allowPopups, minimalPrompts=minimalPrompts, 
                                 verbose=verbose, **presets)
        if status:
            nTerror("Failed importXplorCoorAndRes")
            return True

    if not replaceRestraints:
        return

    formatCns = CnsFormat(ccpnProject, guiRoot, verbose=verbose, minimalPrompts=minimalPrompts, allowPopups=allowPopups)
    ccpnConstraintListOfList = []

    # Will overwrite the settings given to formatCns.linkResonances(  below
    globPattern = inputDir + '/*_noe.tbl'
    fileList = glob(globPattern)
    nTdebug("From %s will read files: %s" % (globPattern, fileList))

#    for fn in fileList[0:1]: # TODO:
    for fn in fileList:
        fnBaseName = os.path.basename(fn).split('.')[0]
        ccpnConstraintList = formatCns.readDistanceConstraints(fn, minimalPrompts=minimalPrompts, verbose=verbose)
        ccpnConstraintList.setName(fnBaseName)
        ccpnConstraintListOfList.append(ccpnConstraintList)
        if not ccpnConstraintList:
            nTerror("Failed to read")
            return True

#    globPattern = inputDir + '/*_hbond.tblXXXX' # TODO:
    globPattern = inputDir + '/*_hbond.tbl'
    fileList = glob(globPattern)
    nTdebug("From %s will read in files: %s" % (globPattern, fileList))
    for fn in fileList:
        fnBaseName = os.path.basename(fn).split('.')[0]
        ccpnConstraintList = formatCns.readDistanceConstraints(fn, minimalPrompts=minimalPrompts, verbose=verbose)
        ccpnConstraintList.setName(fnBaseName)
        ccpnConstraintListOfList.append(ccpnConstraintList)

#    globPattern = inputDir + '/*_dihe.tblXXXX' # TODO:
    globPattern = inputDir + '/*_dihe.tbl'
    fileList = glob(globPattern)
    nTdebug("From %s will read in total files: %s" % (globPattern, fileList))
    for fn in fileList:
        fnBaseName = os.path.basename(fn).split('.')[0]
        ccpnConstraintList = formatCns.readDihedralConstraints(fn, minimalPrompts=minimalPrompts, verbose=verbose)
        ccpnConstraintList.setName(fnBaseName)
        ccpnConstraintListOfList.append(ccpnConstraintList)

    keywds = getDeepByKeysOrDefault(presets, {}, LINK_RESONANCES, KEYWORDS)
    nTdebug("From getDeepByKeysOrDefault keywds: %s" % repr(keywds))

    ccpnConstraintList = getDeepByKeys(ccpnConstraintListOfList, 0) # no need to repeat
    nTdebug("First ccpnConstraintList: %s" % ccpnConstraintList)
    if ccpnConstraintList != None:
#    for i, ccpnConstraintList in enumerate(ccpnConstraintListOfList):
        keywds = getDeepByKeysOrDefault(presets, {}, LINK_RESONANCES, KEYWORDS)
        nTdebug("From getDeepByKeysOrDefault keywds: %s" % repr(keywds))
        nTdebug("ccpnConstraintList: %s" % ccpnConstraintList)
        nmrConstraintStore = ccpnConstraintList.nmrConstraintStore
        structureGeneration = nmrConstraintStore.findFirstStructureGeneration()
        formatCns.linkResonances(
                      forceDefaultChainMapping=1, # may be overwritten by using forceChainMappings.
                      globalStereoAssign=1,
                      setSingleProchiral=1,
                      setSinglePossEquiv=1,
                      strucGen=structureGeneration,
                      allowPopups=allowPopups, minimalPrompts=minimalPrompts, verbose=verbose, **keywds)

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
        rootDir = os.path.join(cingDirTmp, projectName)
        inputDirRel = "XPLOR"
        inputDir = os.path.join(rootDir, inputDirRel)
        if os.path.exists(rootDir):
            nTmessage("Removing original rootDir: %s" % rootDir)
            shutil.rmtree(rootDir)
        os.mkdir(rootDir)

        nTmessage("Copying input from %s to %s" % (testDataEntry, inputDir))
        shutil.copytree(testDataEntry, inputDir)
        convertXplor2Ccpn(projectName, rootDir)
