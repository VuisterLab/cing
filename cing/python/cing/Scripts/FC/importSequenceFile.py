"""
##################
# Example script #
##################

Shows how to import a Fasta sequence file into the data model
by directly using the FormatConverter Python layer.

Level: basic

Contact: Wim Vranken <wim@ebi.ac.uk>
"""

#
# Get the Implementation package to create a project
#

from memops.api import Implementation

#
# Function to reset the paths for saving the project
#

#from memops.general.Io import setNewProjectPaths

#
# Get Tkinter for popups
#

import Tkinter

# 
# Get FastaFormat class for format conversion
# 
# If you'd want to read a Pdb file, this line would read:
#
# from ccpnmr.format.converters.PdbFormat import PdbFormat
#
# and so on for NmrView, ...
#

from ccpnmr.format.converters.FastaFormat import FastaFormat
from memops.universal import Io as uniIo

#
# These are standard Python libraries
#

import os, shutil

###################
# Main of program #
###################

if __name__ == "__main__":
  
  #
  # Variables...
  #
  
  dataDir = 'data/'
  sequenceFileName = 'fasta.seq'

  currentDir = os.path.abspath('.')
  projectDir = uniIo.joinPath((currentDir,'local'))
  projectName = 'testImportSequence'
  
  #
  # Make sure the projectDir exists and delete existing data
  #
  
  if not os.path.exists(projectDir):
    os.mkdir(projectDir)

  projectPath = os.path.join(projectDir,projectName)
  if os.path.exists(projectPath):
    shutil.rmtree(projectPath)

  #
  # Create a CCPN project. This sets default save locations in the
  # current directory (via the Url objects)
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
      newUrlPath = uniIo.joinPath((projectDir,baseName))
      
      repository.url = Implementation.Url(path=newUrlPath)
      
  #
  # Set up Tkinter so it's ready for use
  #

  guiRoot = Tkinter.Tk()
  
  #
  # Give the location of the sequence file
  #

  sequenceFile = os.path.join(dataDir,sequenceFileName)
  
  #
  # Create a FastaFormat instance
  #
  # Again, if this was PDB format, this would read:
  #
  # formatObject = PdbFormat(ccpnProject,guiRoot)
  #
  
  formatObject = FastaFormat(ccpnProject,guiRoot)
  
  #
  # Call the readSequence method from the fastaFormat instance
  # and pass in the name of the file to read
  #
  # This line would be the same for a PDB format - the read/write methods
  # are the same for all formats (except for some format-specific keywords
  # in some cases)
  #
  
  formatObject.readSequence(sequenceFile,minimalPrompts = 1)
  
  #
  # Testing to see if all is there...
  #
  
  print
  print "Project object:", ccpnProject
  print "List of MolSystem objects:", ccpnProject.sortedMolSystems()
  print "List of Molecule objects:", ccpnProject.sortedMolecules()
  
  # Select first available molecule
  mol = ccpnProject.findFirstMolecule()

  print "MolType of first molecule:", mol.molType
  print
  
  #
  # Save the project
  #
    
  ccpnProject.saveModified()
