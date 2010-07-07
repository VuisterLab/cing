"""
Original from Wim Vranken.
Used for eNMR/weNMR workshop data sets.
"""

from ccpnmr.format.converters.NmrStarFormat import NmrStarFormat
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.forkoff import do_cmd
from cing.Scripts.FC.constants import * #@UnusedWildImport
from glob import glob
from memops.api import Implementation
import Tkinter
import shutil


__author__ = cing.__author__ + "Wim Vranken <wim@ebi.ac.uk>"

def convertStar2Ccpn(projectName, rootDir, inputDir="XPLOR", outputDir="CCPN"):
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

    project = Implementation.MemopsRoot(name=projectName)

    guiRoot = Tkinter.Tk() #  headless possible?
    importStarChemicalShifts(project, inputDir, guiRoot, allowPopups=0, minimalPrompts=1, verbose=0)
    project.saveModified()
    tgzFileName = "../" + projectName + ".tgz"
    cmd = "tar -czf %s %s" % (tgzFileName, projectName)
    do_cmd(cmd)
    guiRoot.destroy()


def importStarChemicalShifts(ccpnProject, inputDir, guiRoot, allowPopups=1, minimalPrompts=0, verbose=1, **presets):
    print "JFD: now in importStarChemicalShifts"


#    formatCns = CnsFormat(ccpnProject, guiRoot, verbose=verbose, minimalPrompts=minimalPrompts, allowPopups=allowPopups, **presets)
    formatNmrStarFormat = NmrStarFormat(ccpnProject, guiRoot, verbose=verbose, minimalPrompts=minimalPrompts, allowPopups=allowPopups, **presets)
    ccpnShiftListOfList = []

    # Actually just one but this is less time to code;-)
    globPattern = inputDir + '/*_21.str'
    fileList = glob(globPattern)
    NTdebug("From %s will read files: %s" % (globPattern, fileList))

    for fn in fileList:
        fnBaseName = os.path.basename(fn).split('.')[0]
        shiftList = formatNmrStarFormat.readShifts(fn, minimalPrompts=minimalPrompts, verbose=verbose)
        if not shiftList:
            NTerror("Failed to read")
            return True
        shiftList.setName(fnBaseName)
        ccpnShiftListOfList.append(shiftList)
        # Find and print this shiftList in the CCPN data model. Just to check lookup.
        shiftList = ccpnProject.currentNmrProject.findFirstMeasurementList(className = 'ShiftList')
        print 'ShiftList: [%s]' % shiftList


    keywds = getDeepByKeysOrDefault(presets, {}, READ_SHIFTS, KEYWORDS)
    if keywds:
      NTmessage("In importStarChemicalShifts using keywds...")
      NTdebug(str(keywds))

    shiftList = getDeepByKeys(ccpnShiftListOfList, 0) # no need to repeat
    NTdebug("First shiftList: %s" % shiftList)
    if shiftList == None:
        NTerror("Failed to get shiftList again.")
        return True

#    nmrConstraintStore = shiftList.nmrConstraintStore
#    structureGeneration = nmrConstraintStore.findFirstStructureGeneration()
    formatNmrStarFormat.linkResonances(
                  forceDefaultChainMapping=1, # may be overwritten by using forceChainMappings.
                  globalStereoAssign=1,
                  setSingleProchiral=1,
                  setSinglePossEquiv=1,
#                  strucGen=structureGeneration,
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
            NTmessage("Removing original rootDir: %s" % rootDir)
            shutil.rmtree(rootDir)
        os.mkdir(rootDir)

        NTmessage("Copying input from %s to %s" % (testDataEntry, inputDir))
        shutil.copytree(testDataEntry, inputDir)
        convertStar2Ccpn(projectName, rootDir)
