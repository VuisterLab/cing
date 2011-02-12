'''
Execute like:

python -u $CINGROOT/python/cing/NRG/doAnnotateNrgCing.py $x $y
'''

from cing import header
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.disk import mkdirs
from cing.Libs.forkoff import do_cmd
from cing.NRG.PDBEntryLists import getBmrbLinks
from cing.NRG.nrgCing import nrgCing
from cing.NRG.settings import bmrbDir
from cing.NRG.shiftPresetDict import presetDict
from cing.Scripts.FC.convertStar2Ccpn import importStarChemicalShifts
from cing.Scripts.FC.utils import swapCheck
from cing.core.classes import Project
from cing.core.constants import * #@UnusedWildImport
from cing.main import getStartMessage
from cing.main import getStopMessage
from memops.general.Io import loadProject
from memops.general.Io import saveProject
from shutil import rmtree
import Tkinter
import tarfile


n = nrgCing()
if False:
    getBmrbLinks()

dataDir = n.data_dir
results_dir = n.results_dir
nrgPlusDir = os.path.join(results_dir, 'nrgPlus')

def annotateEntry(entry_code, bmrb_id, *extraArgList):
    'Return True on error'
    NTmessage(header)
    NTmessage(getStartMessage())

    expectedArgumentList = []
    expectedNumberOfArguments = len(expectedArgumentList)
    if len(extraArgList) != expectedNumberOfArguments:
        NTerror("Got arguments: " + `extraArgList`)
        NTerror("Failed to get expected number of arguments: %d got %d" % (
            expectedNumberOfArguments, len(extraArgList)))
        NTerror("Expected arguments: %s" % expectedArgumentList)
        return True
#    entry_code, city = entryCodePlusCity.split('_')

    # Adjust the parameters below
    isInteractive = False
    checkOrgProject = False
    doSwapCheck = False
    doSaveProject = True
    doExport = True

    minimalPrompts = True
    verbose = True
    allowPopups = False

    if isInteractive:
        allowPopups = True
        minimalPrompts = False
#        verbose = True
    else:
        pass
#        minimalPrompts = True
#        verbose = False

    print 'entry_code                                                                                    ', entry_code
    print 'bmrb_id                                                                                       ', bmrb_id
    print 'allowPopups                                                                                   ', allowPopups
    print 'isInteractive                                                                                 ', isInteractive
    print 'minimalPrompts                                                                                ', minimalPrompts
    print 'verbose                                                                                       ', verbose
    print 'checkOrgProject                                                                               ', checkOrgProject
    print 'doSwapCheck                                                                                   ', doSwapCheck
    print 'doSaveProject                                                                                 ', doSaveProject
    print 'doExport                                                                                      ', doExport

    guiRoot = None
    if allowPopups:
        guiRoot = Tkinter.Tk()

    ch23 = entry_code[1:3]
    dataOrgEntryDir = os.path.join(results_dir, 'recoordSync', entry_code)
    ccpnFile = os.path.join(dataOrgEntryDir, entry_code + ".tgz")
    if not os.path.exists(ccpnFile):
        NTerror("Input file not found: %s" % ccpnFile)
        return True
    NTdebug("Looking at %s" % entry_code)
#                continue # TODO disable premature stop.

    bmrb_code = 'bmr'+bmrb_id

    digits12 ="%02d" % ( bmrb_id % 100 )
    inputStarDir = os.path.join(bmrbDir, digits12)
    if not os.path.exists(inputStarDir):
        NTerror("Input star dir not found: %s" % inputStarDir)
        return True
    inputStarFile = os.path.join(inputStarDir, '%s.str'%bmrb_code)
    if not os.path.exists(inputStarFile):
        NTerror("inputStarFile not found: %s" % inputStarFile)
        return True

    dataDividedXDir = os.path.join(nrgPlusDir, ch23)
    entryDir = os.path.join(dataDividedXDir, entry_code)
    outputNijmegenDir = os.path.join(entryDir, 'Nijmegen')
    if not os.path.exists(outputNijmegenDir):
        mkdirs(outputNijmegenDir)
    os.chdir(outputNijmegenDir)

    presets = getDeepByKeysOrDefault(presetDict, {}, bmrb_code)
    if presets:
      NTmessage("In annotateLoop using preset values...")
      NTdebug(str(presets))

    if os.path.exists(entry_code):
        NTmessage("Removing previous directory: %s" % entry_code)
        rmtree(entry_code)
    do_cmd("tar -xzf " + ccpnFile)
    if os.path.exists('linkNmrStarData'):
        NTmessage("Renaming standard directory linkNmrStarData to entry: %s" % entry_code)
        os.rename('linkNmrStarData', entry_code)

    if checkOrgProject:
        # By reading the ccpn tgz into cing it is also untarred/tested.
        project = Project.open(entry_code, status='new')
        if not project.initCcpn(ccpnFolder=ccpnFile, modelCount=1):
            NTerror("Failed check of original project")
            return True
        project.removeFromDisk()
        project.close(save=False)

    ccpnProject = loadProject(entry_code)
    if not ccpnProject:
        NTerror("Failed to read project: %s" % entry_code)
        return True

#            nmrProject = ccpnProject.currentNmrProject
#            ccpnMolSystem = ccpnProject.findFirstMolSystem()
#            NTmessage('found ccpnMolSystem: %s' % ccpnMolSystem)
#    print 'status: %s' % ccpnMolSystem.setCode(projectName) # impossible; reported to ccpn team.

    importStarChemicalShifts(ccpnProject, inputStarDir, guiRoot, allowPopups=allowPopups, minimalPrompts=minimalPrompts, verbose=verbose, **presets)

    if doSwapCheck:
#        constraintsHandler = ConstraintsHandler()
        nmrConstraintStore = ccpnProject.findFirstNmrConstraintStore()
        structureEnsemble = ccpnProject.findFirstStructureEnsemble()
        numSwapCheckRuns = 3
        if nmrConstraintStore:
            if structureEnsemble:
                swapCheck(nmrConstraintStore, structureEnsemble, numSwapCheckRuns)
            else:
                NTmessage("Failed to find structureEnsemble; skipping swapCheck")
        else:
            NTmessage("Failed to find nmrConstraintStore; skipping swapCheck")
#        constraintsHandler.swapCheck(nmrConstraintStore, structureEnsemble, numSwapCheckRuns)

    if doSaveProject:
#        NTmessage('Checking validity and saving to new path')
        NTmessage('Saving to new path')
#        checkValid=True,
        saveProject(ccpnProject, newPath=entry_code, removeExisting=True)
    if doExport:
        tarPath = os.path.join(entryDir, entry_code + ".tgz")
        if os.path.exists(tarPath):
            NTmessage("Overwriting: " + tarPath)
        myTar = tarfile.open(tarPath, mode='w:gz') # overwrites
        myTar.add(entry_code)
        myTar.close()
    if guiRoot:
        guiRoot.destroy()
# end def

def runAbunch():
#1hkt  4046 not in NRG
#2rop many errors; what remained?

#Good: 1brv 1cjg 1d3z 1ieh
# OK (only 1 chain done) 1cjg 1hue 2jmx 1iv6 2kib

# cp $CINGROOT/Tests/data/ccpn/$x.tgz .
# scp    nmr:/Library/WebServer/Documents/NRG-CING/recoordSync/$x/$x.tgz .
# scp -r nmr:/Users/jd/wattosTestingPlatform/bmrb/ftp.bmrb.wisc.edu/pub/bmrb/entry_directories/bmr$y .

    _comboList =    '''
1brv  4020
1cjg  4813
1d3z  6457
1hue  4047
1ieh  4969
1iv6  5317
2rop  11041
2jmx  15072
2kz0  16995
2kib  20074
'''.split()

    comboList = '''
2kib  20074
'''.split()
    comboListCount = len(comboList)/2
    for i in range(comboListCount):
        idxX = i*2
        idxY = idxX + 1
        x = comboList[idxX]
        y = comboList[idxY]
        try:
            status = annotateEntry(x,y)
        except:
            NTtracebackError()
            status = True
        finally:
            NTmessage(getStopMessage(cing.starttime))
            if status:
                NTerror("Failed to annotateEntry for arguments: %s" % str( sys.argv))

if __name__ == "__main__":
    cing.verbosity = cing.verbosityDebug
#    status = False
#    try:
#        status = annotateEntry(*sys.argv[1:])
#    except:
#        NTtracebackError()
#        status = True
#    finally:
#        NTmessage(getStopMessage(cing.starttime))
#        if status:
#            NTerror("Failed to annotateEntry for arguments: %s" % str( sys.argv))
#            sys.exit(1)
    runAbunch()
