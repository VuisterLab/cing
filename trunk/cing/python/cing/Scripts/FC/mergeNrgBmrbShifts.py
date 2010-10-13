import sys, os

from memops.general.Io import loadProject, saveProject

#####################################
# Generic dataHandling code/classes #
#####################################

from pdbe.adatah.Util import runConversionJobs #@UnusedImport
from pdbe.adatah.Generic import DataHandler
from pdbe.adatah.NmrStar import NmrStarHandler
from pdbe.adatah.Constants import archivesCcpnDataDir

from pdbe.adatah.NmrRestrGrid import nmrGridDataDir #@UnusedImport
from pdbe.adatah.Bmrb    import bmrbArchiveDataDir #@UnresolvedImport
from recoord2.pdbe.Constants import projectDirectory as loadDir #@UnresolvedImport

# Import presets
from shiftPresetDict import presetDict #@UnresolvedImport

class MergeNrgBmrbShifts(DataHandler,NmrStarHandler):

  #################
  # REQUIRED HERE #
  #################

  baseName = 'nrgBmrbMerge'

  # List of formats used
  formatList = ['NmrStar']

  bmrbFileFormat = "%s.str"

  #################
  # SPECIFIC HERE #
  #################

  # These can be reset if necessary... not part of main class
  loadDir = loadDir
  projectDirectory = os.path.join(archivesCcpnDataDir,'nrgBmrbMerge')
  presetDict = presetDict

  def setBaseName(self):

    self.baseName = self.baseName

  def loadProject(self):

    self.ccpnProject = loadProject(os.path.join(self.loadDir,self.idCode,'linkNmrStarData'))

  def runSpecific(self):

    curDir = os.getcwd() #@UnusedVariable
    ccpnDir = self.baseName #@UnusedVariable

    #
    # Read the existing CCPN project, set up format object dict
    #

    self.loadProject()
    self.createFormatObjects()

    self.entry = self.ccpnProject.findFirstNmrEntryStore().findFirstEntry()
    self.molSystem = self.ccpnProject.findFirstMolSystem()
    self.nmrProject = self.ccpnProject.findFirstNmrProject()
    self.strucGen = self.nmrProject.findFirstStructureGeneration()

    #
    # Read the BMRB NMR-STAR files (only chem shift data)
    #

    for bmrbCode in self.bmrbCodes:

      self.initShiftPresets(bmrbCode)

      bmrbNmrStarFile = os.path.join(bmrbArchiveDataDir,self.bmrbFileFormat % bmrbCode)
      self.readNmrStarFile(bmrbNmrStarFile, components = ['measurements'])

      #
      # Try to autoset mapping...
      #

      self.setBmrbNmrStarMapping(bmrbNmrStarFile)

      #
      # Run linkResonances, using custom keywds set above
      #

      self.runLinkResonances(resonanceType = 'nmr')

    #
    # Save project in new location
    #

    saveProject(self.ccpnProject,removeExisting=True,newPath = os.path.join(self.entryDir,self.baseName), newProjectName = self.baseName)

  def initShiftPresets(self,bmrbCode):

    if self.presetDict.has_key(bmrbCode):
      sys.__stdout__.write("  Using shift preset values...\n")
      self.presets = self.presetDict[bmrbCode]

      #
      # Print out comment if available
      #

      if self.presetDict[bmrbCode].has_key('comment'):
        commentLines = self.presetDict[bmrbCode]['comment'].split("\n")
        for commentLine in commentLines:
          sys.__stdout__.write("    > %s\n" % commentLine)


  def handleSpecificArguments(self,sysArgs):

    self.bmrbCodes = []

    if '-bmrbCodes' in sysArgs:

      for sysArgIndex in range(sysArgs.index("-bmrbCodes") + 1,len(sysArgs)):
        sysArgValue = sysArgs[sysArgIndex]
        if not sysArgValue[0] == '-':
          self.bmrbCodes.append(sysArgValue)
        else:
          break

    if not self.bmrbCodes:

      raise self.DataHandlerError, "Need to pass in at least one BMRB code with -bmrbCodes flag for this script to work!"

if __name__ == "__main__":

  # Class auto-runs
  MergeNrgBmrbShifts(sys.argv)
