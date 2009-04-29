"""
##################
# Example script #
##################

Shows how to convert NmrView to XEasy files via the data model using the
FormatConverter Python layer.

Level: intermediate

Contact: Wim Vranken <wim@ebi.ac.uk>
"""

#
# Get the top level data model package
#

from memops.universal import Io as uniIo
from memops.api import Implementation

#
# Get the format converter classes for NmrView and XEasy
#

from ccpnmr.format.converters.NmrViewFormat import NmrViewFormat
from ccpnmr.format.converters.XEasyFormat import XEasyFormat

#
# Read in a function to help create an NMR experiment and datasource
#

from ccpnmr.format.general.Util import createExperiment, getRefExpFromOldExpType
from ccpnmr.format.general.Util import createPpmFreqDataSource

#
# Get Tkinter for popups
#

import Tkinter

#
# General python stuff
#

import os, shutil

if __name__ == "__main__":

  #
  # Variables
  #
  
  dataDir = 'data/'
  inputSequenceFileName = 'nmrView.seq'
  inputChemShiftFileName = 'ppm.out'  
  expTypeName = 'noesy_hsqc_HNH.hhn' # This is the 'old' experiment type name
  expName = 'test_experiment'
  inputPeakListFileName = 'nmrView.xpk'

  currentDir = os.path.abspath('.')
  projectDir = os.path.join(currentDir,'local')
  projectName = 'testNmrView2XEasy'
  
  outputDir = os.path.join(currentDir,'local')
  outputSequenceFileName = 'xeasy.seq'
  outputPeakListFileName = 'xeasy.xpk'
  outputChemShiftFileName = 'xeasy.prot'  
  
  #
  # Make sure the projectDir exists and delete existing data
  #
  
  if not os.path.exists(projectDir):
    os.mkdir(projectDir)

  projectPath = os.path.join(projectDir,projectName)
  if os.path.exists(projectPath):
    shutil.rmtree(projectPath)

  #
  # Create a project
  #
  
  ccpnProject = Implementation.MemopsRoot(name = projectName)
  nmrProject = ccpnProject.newNmrProject(name = ccpnProject.name)
  
  #
  # Make sure it saves the information in the projectDir
  # To do this on the Python level you have to reset the path
  # for the urls that indicate the directory locations for the
  # saved files...
  #
  # Alternatively create the project in the right directory to
  # start with - see convertCns2Pdb
  #
  
  for repository in ccpnProject.repositories:
    
    if repository.name in ('userData','backup'):
      
      (oldUrlPath,baseName) = uniIo.splitPath((repository.url.path))
      newUrlPath = uniIo.joinPath(projectDir,baseName)
      
      repository.url = Implementation.Url(path = newUrlPath)

  #
  # Create main Tk window for popups
  #

  gui = Tkinter.Tk()

  #
  # Create an NmrView class and read in the files... create an experiment
  # for the peak list beforehand and pass in the parameters.
  #
  
  nmrViewFormat = NmrViewFormat(ccpnProject,gui)
  
  #
  # Read in the sequence (set minimalPrompts = 0 for more user interaction during this process)
  #
  
  sequenceFile = os.path.join(dataDir,inputSequenceFileName)
  nmrViewFormat.readSequence(sequenceFile, minimalPrompts = 1)
  
  #
  # Read in the chemical shifts (set minimalPrompts = 0 for more user interaction during this process)
  #
  
  chemShiftFile = os.path.join(dataDir,inputChemShiftFileName)
  nmrViewFormat.readShifts(chemShiftFile, minimalPrompts = 1)
  
  #
  # Create an NMR experiment. This is based on the NmrExpPrototype setup.
  #
  
  refExp = getRefExpFromOldExpType(ccpnProject,expTypeName)
  nmrExp = createExperiment(ccpnProject,expName,refExp)
  nmrDataSource = createPpmFreqDataSource(nmrExp,'test','processed',nmrExp.numDim)
  
  #
  # Read in a peak list (connected to the experiment that was just created)
  #
  
  peakListFile = os.path.join(dataDir,inputPeakListFileName)
  nmrViewFormat.readPeaks(peakListFile, dataSource = nmrDataSource,minimalPrompts = 1)
  
  #
  # Run linkresonances... before running this there is on the one hand the NMR
  # information (peaks, shifts) linked to the 'Resonance' objects, and on the
  # other hand the sequence information (molecules, chains, residues, atoms), but
  # they are not linked to each other.
  #
  # LinkResonances links up the NMR information to the atom information - so basically
  # assigns the NMR information. Many options are possible - see python/ccpnmr/format/process/linkResonances.py
  #

  nmrViewFormat.linkResonances(setSingleProchiral = 0,
                               setSinglePossEquiv = 0,
                               minimalPrompts = 1)

  #
  # Note that at this stage everything is inside the data model, and code that
  # works with the Data Model can be run at this stage (e.g. creating achemical
  # shift list from a set of peak assignments, ...).
  #
  # Some examples of data model navigation are at the end of the script...
  #

  #
  # Make sure the outputDir exists...
  #
  
  if not os.path.exists(outputDir):
    os.mkdir(outputDir)

  #
  # Export XEasy files... the right CCPN object(s) has to be selected first.
  #
  
  xeasyFormat = XEasyFormat(ccpnProject,gui)

  chains = list(ccpnProject.sortedMolSystems()[0].chains)
  sequenceFile = os.path.join(outputDir,outputSequenceFileName)
  xeasyFormat.writeSequence(sequenceFile,chains = chains,minimalPrompts = 1)
  
  shiftList = ccpnProject.currentNmrProject.findFirstMeasurementList(className = 'ShiftList')
  chemShiftFile = os.path.join(outputDir,outputChemShiftFileName)
  xeasyFormat.writeShifts(chemShiftFile,measurementList = shiftList,minimalPrompts = 1)
  
  peakLists = list(nmrDataSource.peakLists)
  peakListFile = os.path.join(outputDir,outputPeakListFileName)
  xeasyFormat.writePeaks(peakListFile,peakLists = peakLists,minimalPrompts = 1)

  #
  # Save the project - note that this will only work if all the paths
  # specified by the Urls already exist!
  #
    
  ccpnProject.saveModified()

  #
  # Some data model navigation examples...
  #
    
  print "Number of resonances: %d" % len(ccpnProject.currentNmrProject.resonances)
  
  for nmrExp in ccpnProject.currentNmrProject.sortedExperiments():
    print "Experiment %d: %s (%s) %d dims" % (nmrExp.serial, nmrExp.name, nmrExp.experimentType, nmrExp.numDim)
    print "  Reference pathway: %s" % nmrExp.refExperiment.nmrExpPrototype.name
  
  #
  # Get all the sequence codes associated with resonances...
  #
  
  seqCodes = []

  for resonance in ccpnProject.currentNmrProject.sortedResonances():
    if resonance.resonanceSet:
      resonanceSet = resonance.resonanceSet
      for atomSet in resonanceSet.atomSets:
        seqCode = atomSet.findFirstAtom().residue.seqCode
        if seqCode not in seqCodes:
          seqCodes.append(seqCode)

  seqCodes.sort()
  print "Residue sequence codes connected to resonances:\n"
  print seqCodes
