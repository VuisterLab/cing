#@PydevCodeAnalysisIgnore # pylint: disable-all
"""
Use akin linkNmrStarData.py, so e.g.:

python -u $CINGROOT/python/cing/Scripts/FC/mergeNrgBmrbShifts.py 1ieh -bmrbCodes bmr4969 -raise -force
"""

import os, sys, shutil

#from cing.NRG.shiftPresetDict import presetDict
presetDict = {}

import zipfile
import tarfile

from memops.general.Io import loadProject, saveProject
from pdbe.adatah.Generic import DataHandler
from pdbe.adatah.NmrRestrGrid import nmrGridDataDir #@UnusedImport
from pdbe.adatah.NmrStar import NmrStarHandler
from pdbe.adatah.Util import runConversionJobs #@UnusedImport

"""
What I changed:

Took out all CING references, except presetDict, should be reused
All error/warnings for CING are now print statements in below
Had to modify XML files, were refs to a tjragan directory for molecular stuff

General info:

Error/log file written to original CCPN project directory, also DONE file if completed. Can put SKIP file in there if no conversion required.


Set up:

All variables below MergeNrgBmrbShifts directory

Run as:

python mergeNrgBmrbShifts.py 1ieh -bmrbCodes bmr4969

"""

#####################################
# Generic dataHandling code/classes #
#####################################

class MergeNrgBmrbShifts(DataHandler, NmrStarHandler):

    BASE_DIRECTORY = "/Users/tjr22/Desktop/testing/data"

    projectDirectory = os.path.join(BASE_DIRECTORY, 'origCcpnProjects')

    # Directory where BMRB files live
    bmrbDir = os.path.join(BASE_DIRECTORY, 'bmrb')
    
    # Directory where final project is written
    finalProjectMainDir = os.path.join(BASE_DIRECTORY, 'jointCcpnProjects')
    
    # List of formats used
    formatList = ['NmrStar']
    bmrbFileFormat = "%s_2.1.str.txt" # Used indirectly as well perhaps.

    # This is a file with custom mappings, should be kept
    presetDict = presetDict

    def setBaseName(self):
        self.baseName = self.idCode

    def loadProject(self):

        # This is the directory where the original CCPN project lives
        origCcpnProjectDir = os.path.join(self.projectDirectory, self.idCode)
        
        # This is the zipped CCPN project location
        zippedCcpnProject = os.path.join(origCcpnProjectDir, 'linkNmrStarData.zip')
        
        # Unzip into the original CCPN project directory
        try:
            curTarFile = tarfile.open(zippedCcpnProject, 'r:gz')
            curTarFile.extractall(origCcpnProjectDir)
        except Exception:
            curZipFile = zipfile.ZipFile(zippedCcpnProject)
            curZipFile.extractall(origCcpnProjectDir)

        
        self.ccpnProjectDir =  os.path.join(origCcpnProjectDir, 'linkNmrStarData')
        
        assert os.path.exists(self.ccpnProjectDir), 'Project did not unzip correctly'
        
        self.ccpnProject = loadProject(self.ccpnProjectDir)

    def runSpecific(self):
        """ Returns True on error """

        # Read the existing CCPN project, set up format object dict
        self.loadProject()
        self.createFormatObjects()

        self.entry = self.ccpnProject.findFirstNmrEntryStore().findFirstEntry()
        self.molSystem = self.ccpnProject.findFirstMolSystem()
        self.nmrProject = self.ccpnProject.findFirstNmrProject()
        self.strucGen = self.nmrProject.findFirstStructureGeneration()

        bmrbCodesLength = len(self.bmrbCodes)
        if not bmrbCodesLength:
            print("Not a single BMRB entry presented.")
            return
        if bmrbCodesLength > 1:
            print("Currently NRG-CING only loads a single BMRB entry's CS. Skipping others.")

        # Read the BMRB NMR-STAR file (only chem shift data)
        bmrbCode = self.bmrbCodes[0]
        self.initShiftPresets(bmrbCode)

        inputStarDir = os.path.join(self.bmrbDir, bmrbCode)
        if not os.path.exists(inputStarDir):
            print("Input star dir not found: %s" % inputStarDir)
            return True
            
        inputStarFile = os.path.join(inputStarDir, self.bmrbFileFormat % bmrbCode[3:])
        if not os.path.exists(inputStarFile):
            print("inputStarFile not found: %s" % inputStarFile)
            return True
        print("Start readNmrStarFile")
        self.readNmrStarFile(inputStarFile, components=['measurements'])
        # Try to autoset mapping...
        print("Start setBmrbNmrStarMapping")
        self.setBmrbNmrStarMapping(inputStarFile)
        # Run linkResonances, using custom keywds set above
        print("Start runLinkResonances")
        self.runLinkResonances(resonanceType='nmr')
        # Save project in new location
        
        
        finalProjectDirectory = os.path.join(self.finalProjectMainDir,self.idCode)
        if not os.path.exists(finalProjectDirectory):
          os.mkdir(finalProjectDirectory)

        print('Saving to new path: %s in cwd: %s' % (finalProjectDirectory, os.getcwd()))
        saveProject(self.ccpnProject, removeExisting=True, newPath=finalProjectDirectory, newProjectName=self.baseName)
                
        # Create .tgz of new project - can do this a bit nicer, quick hack
        curDir = os.getcwd()
        os.chdir(self.finalProjectMainDir)
        tar = tarfile.open("{}.tgz".format(self.baseName),'w:gz')
        print self.baseName
        tar.add(self.baseName)
        tar.close()
        os.chdir(curDir)
        
        # Clean up non-archived CCPN projects to save disk space        
        shutil.rmtree(self.ccpnProjectDir)
        shutil.rmtree(finalProjectDirectory)

    def initShiftPresets(self, bmrbCode):
        if not self.presetDict.has_key(bmrbCode):
            return
        sys.__stdout__.write("  Using shift preset values...\n")
        self.presets = self.presetDict[bmrbCode]
        # Print out comment if available
        if 1:
            sys.__stdout__.write("    > %s\n" % self.presets)
        else: # Just comments
            if self.presets.has_key('comment'):
                commentLines = self.presets['comment'].split("\n")
                for commentLine in commentLines:
                    sys.__stdout__.write("    > %s\n" % commentLine)

    def handleSpecificArguments(self, sysArgs):
        self.bmrbCodes = []
        if '-bmrbCodes' in sysArgs:
            for sysArgIndex in range(sysArgs.index("-bmrbCodes") + 1, len(sysArgs)):
                sysArgValue = sysArgs[sysArgIndex]
                if sysArgValue[0] == '-':
                    break
                self.bmrbCodes.append(sysArgValue)
        if not self.bmrbCodes:
            raise self.DataHandlerError, "Need to pass in at least one BMRB code with -bmrbCodes flag for this script to work!"


if __name__ == "__main__":

    MergeNrgBmrbShifts(sys.argv)



