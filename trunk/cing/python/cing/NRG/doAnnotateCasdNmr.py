from cing import header
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.forkoff import do_cmd
from cing.NRG.CasdNmrMassageCcpnProject import dataDir
from cing.NRG.CasdNmrMassageCcpnProject import mapEntrycodeNew2EntrycodeAndCity
from cing.NRG.CasdNmrMassageCcpnProject import programHoH
from cing.NRG.casdNmrPresetDict import presetDict
from cing.Scripts.FC.convertCyana2Ccpn import importCyanaCoordinatesAndRestraints
from cing.Scripts.FC.convertXplor2Ccpn import importXplorCoordinatesAndRestraints
from cing.Scripts.FC.utils import importPseudoPdb
from cing.Scripts.FC.utils import swapCheck
from cing.core.classes import Project
from cing.core.constants import * #@UnusedWildImport
from cing.main import getStartMessage
from cing.main import getStopMessage
from memops.general.Io import loadProject
from memops.general.Io import saveProject
from shutil import copytree
from shutil import rmtree
import Tkinter
import tarfile


def annotateEntry(entryCodeNew, *extraArgList):
    nTmessage(header)
    nTmessage(getStartMessage())

    expectedArgumentList = []
    expectedNumberOfArguments = len(expectedArgumentList)
    if len(extraArgList) != expectedNumberOfArguments:
        nTerror("Got arguments: " + `extraArgList`)
        nTerror("Failed to get expected number of arguments: %d got %d" % (
            expectedNumberOfArguments, len(extraArgList)))
        nTerror("Expected arguments: %s" % expectedArgumentList)
        return True
#    entryCode, city = entryCodePlusCity.split('_')

    # Adjust the parameters below
    isInteractive = False
    sourceIsOrgProject = True
    checkOrgProject = False
    replaceCoordinates = True # From all *.pdb files in inputDir.
    replaceRestraints = True
    doSwapCheck = True
    doSaveProject = True
    doExport = True

    minimalPrompts = True
    verbose = True

    if isInteractive:
        allowPopups = True
        minimalPrompts = False
#        verbose = True
    else:
        allowPopups = False
#        minimalPrompts = True
#        verbose = False

    print 'allowPopups                                                                                   ', allowPopups
    print 'isInteractive                                                                                 ', isInteractive
    print 'minimalPrompts                                                                                ', minimalPrompts
    print 'verbose                                                                                       ', verbose
    print 'sourceIsOrgProject                      (or new CCPN file)                                    ', sourceIsOrgProject
    print 'checkOrgProject                                                                               ', checkOrgProject
    print 'replaceCoordinates                                                                            ', replaceCoordinates
    print 'replaceRestraints                                                                             ', replaceRestraints
    print 'doSwapCheck                                                                                   ', doSwapCheck
    print 'doSaveProject                                                                                 ', doSaveProject
    print 'doExport                                                                                      ', doExport

    guiRoot = None
    if allowPopups:
        guiRoot = Tkinter.Tk()

    entryCode,city = mapEntrycodeNew2EntrycodeAndCity[entryCodeNew]
    ch23 = entryCode[1:3]
    entryCodeOrg = entryCode + 'Org'
    dataOrgEntryDir = os.path.join(dataDir, ch23, entryCodeOrg)
    ccpnFile = os.path.join(dataOrgEntryDir, entryCodeOrg + ".tgz")
#    entryCodeNew = entryCode + city
    programId = getDeepByKeys(programHoH, entryCode, city)
    if not (city == 'Test' or programId):
#                nTdebug("Skipping %s" % entryCodeNew)
        nTerror("Neither City is 'Test' or programId given")
        return
    else:
        nTdebug("Looking at %s" % entryCodeNew)
#                continue # TODO disable premature stop.


    dataDividedXDir = os.path.join(dataDir, ch23)
    entryDir = os.path.join(dataDividedXDir, entryCodeNew)
    inputAuthorDir = os.path.join(entryDir, 'Author')
    outputNijmegenDir = os.path.join(entryDir, 'Nijmegen')

    if not os.path.exists(inputAuthorDir):
        mkdirs(inputAuthorDir)
    if not os.path.exists(outputNijmegenDir):
        mkdirs(outputNijmegenDir)

    os.chdir(outputNijmegenDir)

    presets = getDeepByKeysOrDefault(presetDict, {}, entryCodeNew)
    if presets:
      nTmessage("In annotateLoop using preset values...")

    if sourceIsOrgProject:
        if os.path.exists(entryCodeOrg):
            nTmessage("Removing previous Org directory: %s" % entryCodeOrg)
            rmtree(entryCodeOrg)
        do_cmd("tar -xzf " + ccpnFile)
        if os.path.exists(entryCodeNew):
            nTmessage("Removing previous directory: %s" % entryCodeNew)
            rmtree(entryCodeNew)
        copytree(entryCodeOrg, entryCodeNew)

    if checkOrgProject:
        # By reading the ccpn tgz into cing it is also untarred/tested.
        project = Project.open(entryCodeOrg, status='new')
        if not project.initCcpn(ccpnFolder=ccpnFile, modelCount=1):
            nTerror("Failed check of original project")
            return
        project.removeFromDisk()
        project.close(save=False)

    ccpnProject = loadProject(entryCodeNew)
    if not ccpnProject:
        nTerror("Failed to read project: %s" % entryCodeNew)
        return

#            nmrProject = ccpnProject.currentNmrProject
#            ccpnMolSystem = ccpnProject.findFirstMolSystem()
#            nTmessage('found ccpnMolSystem: %s' % ccpnMolSystem)
#    print 'status: %s' % ccpnMolSystem.setCode(projectName) # impossible; reported to ccpn team.

    if replaceCoordinates or replaceRestraints:
        if programId == CYANA:
            importCyanaCoordinatesAndRestraints(ccpnProject, inputAuthorDir, guiRoot,
                replaceCoordinates=replaceCoordinates, replaceRestraints=replaceRestraints, allowPopups=allowPopups, minimalPrompts=minimalPrompts, verbose=verbose, **presets)
        elif programId == XPLOR:
            importXplorCoordinatesAndRestraints(ccpnProject, inputAuthorDir, guiRoot,
                replaceCoordinates=replaceCoordinates, replaceRestraints=replaceRestraints, allowPopups=allowPopups, minimalPrompts=minimalPrompts, verbose=verbose, **presets)
        elif programId == PDB:
            importPseudoPdb(ccpnProject, inputAuthorDir, guiRoot,
                allowPopups=allowPopups, minimalPrompts=minimalPrompts, verbose=verbose, **presets)
        else:
            nTerror("Failed to doImportCoordinatesAndRestraints because action for program Id not coded for: %s" % programId)
            nTerror("Skipping entry")
            return

    if doSwapCheck:
#        constraintsHandler = ConstraintsHandler()
        nmrConstraintStore = ccpnProject.findFirstNmrConstraintStore()
        structureEnsemble = ccpnProject.findFirstStructureEnsemble()
        numSwapCheckRuns = 3
        if nmrConstraintStore:
            if structureEnsemble:
                swapCheck(nmrConstraintStore, structureEnsemble, numSwapCheckRuns)
            else:
                nTmessage("Failed to find structureEnsemble; skipping swapCheck")
        else:
            nTmessage("Failed to find nmrConstraintStore; skipping swapCheck")
#        constraintsHandler.swapCheck(nmrConstraintStore, structureEnsemble, numSwapCheckRuns)

    if doSaveProject:
#        nTmessage('Checking validity and saving to new path')
        nTmessage('Saving to new path: %s' % entryCodeNew)
#        checkValid=True,
        saveProject(ccpnProject, newPath=entryCodeNew, removeExisting=True)
    if doExport:
        tarPath = os.path.join(entryDir, entryCodeNew + ".tgz")
        if os.path.exists(tarPath):
            nTmessage("Overwriting: " + tarPath)
        myTar = tarfile.open(tarPath, mode='w:gz') # overwrites
        myTar.add(entryCodeNew)
        myTar.close()
    if guiRoot:
        guiRoot.destroy()
# end def

if __name__ == "__main__":
    cing.verbosity = cing.verbosityDebug
    try:
        status = annotateEntry(*sys.argv[1:])
    except:
        NTtracebackError()
    finally:
        nTmessage(getStopMessage(cing.starttime))
