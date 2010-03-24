#@PydevCodeAnalysisIgnore
"""
With help from Wim Vranken.
For example:
    - changing the MS name from 2kkx to ET109AredOrg
    - swap checks/changes

# Execute like e.g.:
# python -u $CINGROOT/python/cing/Scripts/FC/massageCcpnProject.py ET109AredOrg ET109AredUtrecht
if the input project is in cwd.

Most functionality is hard-coded here so be careful reading the actual code.
"""
from ccpnmr.format.converters import PseudoPdbFormat
from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDebug
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import readLinesFromFile
from cing.Libs.NTutils import readTextFromFile
from cing.NRG import CASD_NMR_BASE_NAME
from glob import glob
from memops.general.Io import loadProject
from memops.general.Io import saveProject
import Tkinter
import cing
import os
import sys

__author__ = "Wim Vranken <wim@ebi.ac.uk> Jurgen Doreleijers <jurgenfd@gmail.com>"

def convert(projectName, inputDir, projectNameNew):
    # Adjust the parameters below!
    removeOriginalStructureEnsemble = True
    addStructureEnsemble = True # From all *.pdb files in inputDir.

    ccpnPath = os.path.join(inputDir, projectName)
    ccpnProject = loadProject(ccpnPath)

    ccpnMolSystem = ccpnProject.findFirstMolSystem()
    NTmessage( 'found ccpnMolSystem: %s' % ccpnMolSystem )
#    print 'status: %s' % ccpnMolSystem.setCode(projectName) # impossible; reported to ccpn team.

    if removeOriginalStructureEnsemble:
        structureEnsemble = ccpnProject.findFirstStructureEnsemble()
        if structureEnsemble:
            NTmessage("Removing first found structureEnsemble")
            structureEnsemble.delete()
        else:
            NTwarning("No structureEnsemble found; can't remove it.")

    if addStructureEnsemble:
        structureGeneration = ccpnProject.newStructureGeneration()
        guiRoot = Tkinter.Tk()
        format = PseudoPdbFormat(ccpnProject, guiRoot, verbose = 1)

        globPattern = inputDir + '/*.pdb'
        fileList = glob(globPattern)
        NTdebug("From %s will read files: %s" % (globPattern,fileList))
        format.readCoordinates(fileList, strucGen = structureGeneration, minimalPrompts = 1, linkAtoms = 0)

    NTmessage(  'saving to new path if all checks are valid' )
    # the newPath basename will be taken according to ccpn code doc.
    ccpnPathNew = os.path.join(inputDir, projectNameNew)
    saveProject(ccpnProject, checkValid=True, newPath=ccpnPathNew, removeExisting=True)

def replaceCoordinates(projectName, inputDir, projectNameNew, outputDir ):
    """Replace the coordinates in the structure ensemble with those from the PDB files in the inputDir"""

    if not os.path.exists(outputDir):
        os.mkdir(outputDir)

    # Adjust the parameters below!
    removeOriginalStructureEnsemble = True
    addStructureEnsemble = False # From all *.pdb files in inputDir.

    ccpnPath = os.path.join(inputDir, projectName)
    ccpnProject = loadProject(ccpnPath)

    ccpnMolSystem = ccpnProject.findFirstMolSystem()
    NTmessage( 'found ccpnMolSystem: %s' % ccpnMolSystem )
#    print 'status: %s' % ccpnMolSystem.setCode(projectName) # impossible; reported to ccpn team.

    if removeOriginalStructureEnsemble:
        structureEnsemble = ccpnProject.findFirstStructureEnsemble()
        if structureEnsemble:
            NTmessage("Removing first found structureEnsemble")
            structureEnsemble.delete()
        else:
            NTwarning("No structureEnsemble found; can't remove it.")

    if addStructureEnsemble:
        structureGeneration = ccpnProject.newStructureGeneration()
        guiRoot = Tkinter.Tk()
        format = PseudoPdbFormat(ccpnProject, guiRoot, verbose = 1)

        globPattern = inputDir + '/*.pdb'
        fileList = glob(globPattern)
        NTdebug("From %s will read files: %s" % (globPattern,fileList))
        format.readCoordinates(fileList, strucGen = structureGeneration, minimalPrompts = 1, linkAtoms = 0)

    NTmessage(  'saving to new path if all checks are valid' )
    # the newPath basename will be taken according to ccpn code doc.
    ccpnPathNew = os.path.join(inputDir, projectNameNew)
    saveProject(ccpnProject, checkValid=True, newPath=ccpnPathNew, removeExisting=True)

def swapCheck(projectName, inputDir, projectNameNew ):

    ccpnPath = os.path.join(inputDir, projectName)
    ccpnProject = loadProject(ccpnPath)

    ccpnMolSystem = ccpnProject.findFirstMolSystem()
    NTmessage(  'found ccpnMolSystem: %s' % ccpnMolSystem )

    if False:
        from pdbe.adatah.Constraints import ConstraintsHandler
        ch = ConstraintsHandler()
        ncs = ccpnProject.findFirstNmrConstraintStore()
        se = ccpnProject.findFirstStructureEnsemble()
        ch.swapCheck(ncs,se,2)


    NTmessage( 'saving to new path if all checks are valid' )
    # the newPath basename will be taken according to ccpn code doc.
    ccpnPathNew = os.path.join(inputDir, projectNameNew)
    saveProject(ccpnProject, checkValid=True, newPath=ccpnPathNew, removeExisting=True)

def replaceCoordinatesWrapper():
#    inputDir = os.path.join(cingDirTestsData, "ccpn")
    dataOrgDir = os.path.join('/Users/jd/CASD-NMR-CING/data', projectName)
    #        _scriptName = sys.argv[0]
    # parameters for doScriptOnEntryList
    startDir = '/Library/WebServer/Documents/' + CASD_NMR_BASE_NAME
    dataDir = startDir + 'data'

    entryListFileName = os.path.join(startDir, 'list', 'entry_list_todo.csv')
    entryList = readLinesFromFile(entryListFileName)
    cityList = [ 'Frankfurt', 'Lyon' ]

    for entryCode in entryList[0:1]:
        ch23 = entryCode[1:3]
        dataOrgEntryDir = xx
        for city in cityList:
            entryCodeNew = entryCode + city
            os.path.join()


if __name__ == '__main__':
    cing.verbosity = verbosityDebug

    if True:
        replaceCoordinatesWrapper()
        sys.exit(0)

    projectName = "1brv"
#    projectName = "AR3436A"
    projectNameNew = projectName + 'New'
#    inputDir = os.path.join(cingDirTestsData, "ccpn")
    inputDir = os.path.join('/Users/jd/CASD-NMR-CING/data', projectName)
    outputDir = cingDirTmp
#        _scriptName = sys.argv[0]
    if False:
        projectName = sys.argv[1]
        inputDir = sys.argv[2]
        projectNameNew = None
        if len(sys.argv) > 4:
            projectNameNew = sys.argv[3]
            if len(sys.argv) > 5:
                outputDir = sys.argv[4]
    print "projectName: %s" % projectName
    print "projectNameNew: %s" % projectNameNew
    print "inputDir: %s" % inputDir
    print "outputDir: %s" % outputDir

    if False:
        swapCheck(projectName, inputDir)
    if False:
        convert(projectName, inputDir, projectNameNew )
