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
from ccpnmr.format.converters.PseudoPdbFormat import PseudoPdbFormat
from cing import cingDirTmp
from cing import verbosityDebug
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import readLinesFromFile
from cing.NRG import CASD_NMR_BASE_NAME
from cing.core.classes import Project
from glob import glob
from matplotlib.cbook import mkdirs
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

def getCASD_NMR_Overview1():
    startDir = '/Library/WebServer/Documents/' + CASD_NMR_BASE_NAME
    entryListFileName = os.path.join(startDir, 'list', 'entry_list_todo.csv')
    entryList = readLinesFromFile(entryListFileName) #@UnusedVariable

def replaceCoordinates():

    cityList = [ 'Cheshire', 'Frankfurt', 'Lyon', 'Paris', 'Piscataway', 'Seattle', 'Utrecht' ]
    maxCities = 1
    maxEntries = 1
    # Adjust the parameters below!
    removeOriginalStructureEnsemble = True
    addStructureEnsemble = True # From all *.pdb files in inputDir.

#    inputDir = os.path.join(cingDirTestsData, "ccpn")
    baseDir = '/Users/jd/CASD-NMR-CING'
    dataOrgDir = os.path.join(baseDir,'data')
    dataDividedDir = os.path.join(baseDir,'dataDivided')
    #        _scriptName = sys.argv[0]
    # parameters for doScriptOnEntryList
    startDir = '/Library/WebServer/Documents/' + CASD_NMR_BASE_NAME
    entryListFileName = os.path.join(startDir, 'list', 'entry_list_todo.csv')
    entryList = readLinesFromFile(entryListFileName) #@UnusedVariable
    entryList = ['ET109Aox']

    for entryCode in entryList[0:maxEntries]:
        ch23 = entryCode[1:3]
        dataOrgEntryDir = os.path.join( dataOrgDir, entryCode )
        ccpnFile = os.path.join(dataOrgEntryDir, entryCode+".tgz")
        for city in cityList[0:maxCities]:
            entryCodeNew = entryCode + city
            dataDividedXDir = os.path.join(dataDividedDir, ch23)
            inputAuthorDir = os.path.join(dataDividedXDir, entryCodeNew, 'Author')
            outputNijmegenDir = os.path.join(dataDividedXDir, entryCodeNew, 'Nijmegen')

            globPattern = inputAuthorDir + '/*.pdb'
            pdbFileList = glob(globPattern)
            if not pdbFileList:
                NTmessage("Skipping because there is no PDB file in: " + os.getcwd())
                continue

            if not os.path.exists(inputAuthorDir):
                mkdirs(inputAuthorDir)
            if not os.path.exists(outputNijmegenDir):
                mkdirs(outputNijmegenDir)

            os.chdir(outputNijmegenDir)
            if False:
                # By reading the ccpn tgz into cing it is also untarred/tested.
                project = Project.open(entryCode, status = 'new')
                project.initCcpn(ccpnFolder = ccpnFile, modelCount=1)
                project.removeFromDisk()
                project.close(save=False)

            if True:
                ccpnProject = loadProject(entryCode)
                nmrProject = ccpnProject.currentNmrProject
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
                    structureGeneration = nmrProject.newStructureGeneration()
                    fileList = None
                    NTdebug("From %s will read files: %s" % (globPattern,fileList))
                    guiRoot = Tkinter.Tk()
                    format = PseudoPdbFormat(ccpnProject, guiRoot, verbose = 1)
                    format.readCoordinates(fileList, strucGen = structureGeneration, minimalPrompts = 1, linkAtoms = 0)

                NTmessage(  'saving to new path if all checks are valid' )
                # the newPath basename will be taken according to ccpn code doc.
                saveProject(ccpnProject, checkValid=True, newPath=entryCodeNew, removeExisting=True)


def processInputAndRun(): # TODO fix this code if usable.

    projectName = "1brv"
#    projectName = "AR3436A"
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
#            if len(sys.argv) > 5:
#                outputDir = sys.argv[4]
    print "projectName: %s" % projectName
    print "projectNameNew: %s" % projectNameNew
    print "inputDir: %s" % inputDir
    print "outputDir: %s" % outputDir

    if False:
        convert(projectName, inputDir, projectNameNew )

if __name__ == '__main__':
    cing.verbosity = verbosityDebug
    replaceCoordinates()
