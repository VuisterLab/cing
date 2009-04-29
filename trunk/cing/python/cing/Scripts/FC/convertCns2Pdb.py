"""
##################
# Example script #
##################

Shows how to convert CNS-type coordinate files to PDB-like coordinate files with
the correct PDB atom naming. Also resets the path names.

Level: intermediate

Contact: Wim Vranken <wim@ebi.ac.uk>
"""

#
# These are standard Python libraries
#

import os, re, shutil

#
# Get the Implementation package to create a project
#

from memops.api import Implementation

# 
# Get Pdb and CnsFormat classes for format conversion
# 

from ccpnmr.format.converters.PdbFormat import PdbFormat
from ccpnmr.format.converters.CnsFormat import CnsFormat

#
# Get Tkinter for popups
#

import Tkinter

if __name__ == '__main__':

  #
  # Variables...
  #
  
  dataDir = 'data/'
  cnsFileMatchRegExp = "cns_(\d+)\.pdb$"

  currentDir = os.path.abspath('.')
  projectDir = os.path.join(currentDir,'local')
  projectName = 'testCns2PdbConversion'
  
  outputDir = os.path.join(currentDir,'local')
  outputPdbFileName = 'test.pdb'
  
  #
  # Make sure the projectDir exists and delete existing data
  #
  
  if not os.path.exists(projectDir):
    os.mkdir(projectDir)

  projectPath = os.path.join(projectDir,projectName)
  if os.path.exists(projectPath):
    shutil.rmtree(projectPath)

  #
  # Open a CCPN project and make an NMR structure generation to link the structures to
  #
  
  #
  # Easiest way to make sure project is saved in a particular directory is to make it
  # the active one. Otherwise have to change repository paths.
  #
  
  curDir = os.getcwd()
  os.chdir(projectDir)
  project = Implementation.MemopsRoot(name = projectName)    
  os.chdir(curDir)
  
  nmrProject = project.newNmrProject(name = project.name)
  structureGeneration = nmrProject.newStructureGeneration()
  
  #
  # Start Tkinter for user interaction
  #

  guiRoot = Tkinter.Tk()

  #
  # Get the CNS files from the data directory and sort them
  #

  files = os.listdir(dataDir)
  fileDict = {}
  strucNumList = []

  cnsMultipleFileMatch = re.compile(cnsFileMatchRegExp)

  for file in files:

    searchObj = cnsMultipleFileMatch.search(file)

    if searchObj:

      strucNum = int(searchObj.group(1))

      fileDict[strucNum] = file
      strucNumList.append(strucNum)

  strucNumList.sort()

  fileList = []

  for strucNum in strucNumList:

    fileList.append(os.path.join(dataDir,fileDict[strucNum]))

  #
  # Create the format converter CNS format
  #

  cnsFormat = CnsFormat(project,guiRoot,verbose = 1)

  #
  # Now read in the structures... this will also create the Molecules and Molecular system via readSequence()
  #

  cnsFormat.readCoordinates(fileList,strucGen = structureGeneration, minimalPrompts = 1, linkAtoms = 0)

  #
  # Create the format converter PDB format
  #

  pdbFormat = PdbFormat(project,guiRoot,verbose = 1)

  #
  # Make sure the outputDir exists...
  #
  
  if not os.path.exists(outputDir):
    os.mkdir(outputDir)

  #
  # Now write the structures...
  #

  structureList = list(structureGeneration.structureEnsemble.models)

  outputPdbFile = os.path.join(outputDir,outputPdbFileName)

  pdbFormat.writeCoordinates(outputPdbFile,structures = structureList, minimalPrompts = 1)

  #
  # Save the CCPN project...
  #
  
  project.saveModified()
