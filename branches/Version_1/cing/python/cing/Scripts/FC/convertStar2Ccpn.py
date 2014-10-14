"""
Original from Wim Vranken.
Used for eNMR/weNMR workshop data sets.
"""

from ccpnmr.format.converters.NmrStarFormat import NmrStarFormat
from cing import issueListUrl
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.forkoff import do_cmd
from cing.Scripts.FC.constants import * #@UnusedWildImport
from glob import glob
from memops.api import Implementation
from memops.api.Implementation import ApiError
import shutil

try:
    import Tkinter
except:
    if cing.verbosity == cing.verbosityDebug:
        if False:
            nTtracebackError()
# end try

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

    nTerror("This routine is untested and shouldn't be used without.")
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
    importStarChemicalShifts(project, inputDir, guiRoot, allowPopups=0, minimalPrompts=1, verbose=0)
    project.saveModified()
    tgzFileName = "../" + projectName + ".tgz"
    cmd = "tar -czf %s %s" % (tgzFileName, projectName)
    do_cmd(cmd)
    guiRoot.destroy()

def importFullStarProjects(starFileName, projectName, inputDir='.', outputDir='.', guiRoot=None, allowPopups=0,minimalPrompts=1,verbose=1):
    '''Returns a full CCPN project rooted in inputDir/projectName that will be created and saved.
    Input will be from inputDir/starFileName

    Returns False for error.
    '''

    if not os.path.exists(inputDir):
        nTerror("Failed to find inputDir: %s" % inputDir)
        return False
    starFileNameFull = os.path.join(inputDir, starFileName)
    if not os.path.exists(starFileNameFull):
        nTerror("Failed to find starFileNameFull: %s" % starFileNameFull)
        return False
    if not os.path.exists(outputDir):
        os.mkdir(outputDir)
    os.chdir(outputDir)

    ccpnProjectPath = os.path.join(outputDir, projectName)
    if os.path.exists(ccpnProjectPath):
        shutil.rmtree(ccpnProjectPath)

    ccpnProject = Implementation.MemopsRoot(name=projectName)

#    'linkAtoms':                (True,False,'If set to False (off), unrecognized coordinate atoms will not be linked.'),
    keywds = {'minimalPrompts': minimalPrompts, 'allowPopups': allowPopups, 'linkAtoms':0}
    formatNmrStarFormat = NmrStarFormat(ccpnProject, guiRoot, verbose=verbose, **keywds)
    formatNmrStarFormat.version = '3.1'
    entryTitle = 'Project from NMR-STAR for %s' % projectName
    entryDetails = "Created by Wim Vranken's FormatConverter embedded in CING"
    formatNmrStarFormat.getFullProject( starFileNameFull, title = entryTitle, details = entryDetails, **keywds)
#    nmrConstraintStore = shiftList.nmrConstraintStore
#    structureGeneration = nmrConstraintStore.findFirstStructureGeneration()
#    formatNmrStarFormat.linkResonances(
#                  forceDefaultChainMapping=1, # may be overwritten by using forceChainMappings.
#                  globalStereoAssign=1,
#                  setSingleProchiral=1,
#                  setSinglePossEquiv=1,
##                  strucGen=structureGeneration,
#                  allowPopups=allowPopups, minimalPrompts=minimalPrompts, verbose=verbose, **keywds)
    # Catch entries like mentioned in issue

    try:
        ccpnProject.checkAllValid()
    except ApiError:
        nTtracebackError()
        nTerror("Failed ccpnProject.checkAllValid")
        nTerror("See issue: %s%d" % (issueListUrl, 266))
        return False

    ccpnProject.saveModified()

    if not os.path.exists(ccpnProjectPath):
        nTerror("Failed to find new CCPN project directory: %s" % ccpnProjectPath)
        return False
    tgzFileName = projectName + ".tgz"
    cmd = "tar -czf %s %s" % (tgzFileName, projectName)
    do_cmd(cmd)

    return ccpnProject


def importStarChemicalShifts(ccpnProject, inputDir, guiRoot, allowPopups=1, minimalPrompts=0, verbose=1, **presets):
    print "JFD: now in importStarChemicalShifts"


#    formatCns = CnsFormat(ccpnProject, guiRoot, verbose=verbose, minimalPrompts=minimalPrompts, allowPopups=allowPopups, **presets)
    formatNmrStarFormat = NmrStarFormat(ccpnProject, guiRoot, verbose=verbose, minimalPrompts=minimalPrompts, 
                                        allowPopups=allowPopups, **presets)
    ccpnShiftListOfList = []

    # Actually just one but this is less time to code;-)
    globPattern = inputDir + '/*_21.str'
    fileList = glob(globPattern)
    nTdebug("From %s will read files: %s" % (globPattern, fileList))

    for fn in fileList:
        fnBaseName = os.path.basename(fn).split('.')[0]
        shiftList = formatNmrStarFormat.readShifts(fn, minimalPrompts=minimalPrompts, verbose=verbose)
        if not shiftList:
            nTerror("Failed to read")
            return True
        shiftList.setName(fnBaseName)
        ccpnShiftListOfList.append(shiftList)
        # Find and print this shiftList in the CCPN data model. Just to check lookup.
        shiftList = ccpnProject.currentNmrProject.findFirstMeasurementList(className = 'ShiftList')
        print 'ShiftList: [%s]' % shiftList


    keywds = getDeepByKeysOrDefault(presets, {}, READ_SHIFTS, KEYWORDS)
    if keywds:
        nTmessage("In importStarChemicalShifts using keywds...")
        nTdebug(str(keywds))

    shiftList = getDeepByKeys(ccpnShiftListOfList, 0) # no need to repeat
    nTdebug("First shiftList: %s" % shiftList)
    if shiftList == None:
        nTerror("Failed to get shiftList again.")
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
    starFileName, projectName, inputDir = sys.argv[1:]
    status = True
    try:
        status = not importFullStarProjects(starFileName, projectName, inputDir)
    except:
        nTtracebackError()
        status = True

    if status:
        nTerror("Failed to importFullStarProjects")
        sys.exit(1)

