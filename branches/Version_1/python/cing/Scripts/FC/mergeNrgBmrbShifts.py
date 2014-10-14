#@PydevCodeAnalysisIgnore # pylint: disable-all
"""
Use akin linkNmrStarData.py, so e.g.:

python -u $CINGROOT/python/cing/Scripts/FC/mergeNrgBmrbShifts.py 1ieh -bmrbCodes bmr4969 -raise -force
"""

from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.forkoff import do_cmd
from cing.NRG.doAnnotateNrgCing import bmrbDir
from cing.NRG.settings import dir_S
from cing.NRG.shiftPresetDict import presetDict
from cing.core.classes import Project
from memops.general.Io import saveProject
from pdbe.adatah.Generic import DataHandler
from pdbe.adatah.NmrRestrGrid import nmrGridDataDir #@UnusedImport
from pdbe.adatah.NmrStar import NmrStarHandler
from pdbe.adatah.Util import runConversionJobs #@UnusedImport
#from recoord2.pdbe.Constants import projectDirectory as loadDir
#from pdbe.adatah.Bmrb    import bmrbArchiveDataDir #@UnresolvedImport

#####################################
# Generic dataHandling code/classes #
#####################################

class MergeNrgBmrbShifts(DataHandler, NmrStarHandler):

    baseName = 'nrgBmrbMerge' # default for ccpn top directory

    # List of formats used
    formatList = ['NmrStar']
    bmrbFileFormat = "%s_21.str" # Used indirectly as well perhaps.
    # These can be reset if necessary... not part of main class
#    loadDir = cingDirTmp
#    projectDirectory = os.path.join(archivesCcpnDataDir, 'nrgBmrbMerge')
    projectDirectory = cingDirTmp
    presetDict = presetDict

    def setBaseName(self):
        self.baseName = self.idCode

    def loadProject(self):
        modelCount = 1
        ccpnFile = os.path.join("%s_input.tgz" % self.idCode)
        project = Project.open(self.idCode, status='new')
        # Can read tgz files.
        if project.initCcpn(ccpnFolder=ccpnFile, modelCount=modelCount) == None:
            nTerror("Failed to read: %s" % ccpnFile)
            return True
#        self.ccpnProject = loadCcpnTgzProject(os.path.join(self.loadDir, self.idCode, 'linkNmrStarData'))
        self.ccpnProject = project.ccpn

    def runSpecific(self):
        """ Returns True on error """
        entryCodeChar2and3 = self.idCode[1:3]
        projectDirectory = os.path.join(dir_S, entryCodeChar2and3, self.idCode)
        os.chdir(projectDirectory)
        curDir = os.getcwd() #@UnusedVariable
        nTdebug("curDir: %s" % curDir)
#        ccpnDir = self.baseName #@UnusedVariable

        # Read the existing CCPN project, set up format object dict
        self.loadProject()
        self.createFormatObjects()

        self.entry = self.ccpnProject.findFirstNmrEntryStore().findFirstEntry()
        self.molSystem = self.ccpnProject.findFirstMolSystem()
        self.nmrProject = self.ccpnProject.findFirstNmrProject()
        self.strucGen = self.nmrProject.findFirstStructureGeneration()

        bmrbCodesLength = len(self.bmrbCodes)
        if not bmrbCodesLength:
            nTerror("Not a single BMRB entry presented.")
            return
        if bmrbCodesLength > 1:
            nTwarning("Currently NRG-CING only loads a single BMRB entry's CS. Skipping others.")

        # Read the BMRB NMR-STAR file (only chem shift data)
#        for bmrbCode in self.bmrbCodes:
        bmrbCode = self.bmrbCodes[0]
        self.initShiftPresets(bmrbCode)
    #          bmrbNmrStarFile = os.path.join(bmrbArchiveDataDir, self.bmrbFileFormat % bmrbCode)
#        bmrb_id = int(bmrbCode[3:])
#        digits12 = "%02d" % (bmrb_id % 100)
#        inputStarDir = os.path.join(bmrbDir, digits12)
        inputStarDir = os.path.join(bmrbDir, bmrbCode)
        if not os.path.exists(inputStarDir):
            nTerror("Input star dir not found: %s" % inputStarDir)
            return True
        inputStarFile = os.path.join(inputStarDir, self.bmrbFileFormat % bmrbCode)
        if not os.path.exists(inputStarFile):
            nTerror("inputStarFile not found: %s" % inputStarFile)
            return True
        nTdebug("Start readNmrStarFile")
        self.readNmrStarFile(inputStarFile, components=['measurements'])
        # Try to autoset mapping...
        nTdebug("Start setBmrbNmrStarMapping")
        self.setBmrbNmrStarMapping(inputStarFile)
        # Run linkResonances, using custom keywds set above
        nTdebug("Start runLinkResonances")
        self.runLinkResonances(resonanceType='nmr')
        # Save project in new location
        newPath = self.baseName
        nTmessage('Saving to new path: %s in cwd: %s' % (newPath, os.getcwd()))
        saveProject(self.ccpnProject, removeExisting=True, newPath=newPath, newProjectName=self.baseName)
        ccpnTgzFile = "%s.tgz" % self.idCode
        cmd = "tar -czf %s %s" % (ccpnTgzFile, newPath)
        if do_cmd(cmd):
            nTerror("Failed tar")
            return None
        nTmessage("Saved ccpn project to tgz: %s" % ccpnTgzFile)

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
    cing.verbosity = cing.verbosityDebug
    MergeNrgBmrbShifts(sys.argv)

