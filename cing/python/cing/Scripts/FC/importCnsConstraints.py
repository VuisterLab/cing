"""
##################
# Example script #
##################

Shows how to import a CNS constraint file into the data model
by directly using the FormatConverter Python layer.

Level: basic

Contact: Wim Vranken <wim@ebi.ac.uk>
"""

#
# Get the Implementation package to create a project
#

from memops.api import Implementation
from memops.universal import Io as uniIo
from ccp.api.nmr import Nmr

#
# Function to get resonances 'in order' for pairwise constraints,
# if this information was specified.
#

from ccp.general.Util import getResonancesFromPairwiseConstraintItem

#
# Import the CNS format class
#

from ccpnmr.format.converters.CnsFormat import CnsFormat

#
# Get Tkinter for popups
#

import Tkinter

#
# Standard Python stuff
#

import os, shutil

if __name__ == '__main__':

  #
  # Variables
  #
  
  dataDir = 'data/'
  coordinateFileName = 'cns_1.pdb' # Is used for getting the sequence only!
  distanceConstraintFileName = 'n15noesy.tbl'  

  currentDir = os.path.abspath('.')
  projectDir = os.path.join(currentDir,'local')
  projectName = 'testImportCnsConstraints'
  
  #
  # Make sure the projectDir exists and delete existing data
  #
  
  if not os.path.exists(projectDir):
    os.mkdir(projectDir)

  projectPath = os.path.join(projectDir,projectName)
  if os.path.exists(projectPath):
    shutil.rmtree(projectPath)
  
  #
  # Create a CCPN Data Model Project (this is the root object within the
  # Data Model)
  #
  
  ccpnProject = Implementation.MemopsRoot(name = projectName)
  nmrProject = Nmr.NmrProject(ccpnProject, name = ccpnProject.name)
  
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
      
      (oldUrlPath,baseName) = uniIo.splitPath(repository.url.path)
      newUrlPath = uniIo.joinPath(projectDir,baseName)
      
      repository.url = Implementation.Url(path = newUrlPath)
  
  #
  # Open a Tk window for handling the popups...
  #

  root = Tkinter.Tk()
  
  #
  # Create the FormatConverter CnsFormat object
  #

  cnsFormat = CnsFormat(ccpnProject,root)
  
  #
  # Read in a sequence - this will create the molecular system with
  # all the atom information.
  #
  # Note that a lot of the popups can be avoided when the right information
  # is passed in (see ccpnmr.format.converters.DataFormat, the readSequence
  # function in the DataFormat class)
  #

  coordinateFile = os.path.join(dataDir,coordinateFileName)
  ccpnChains = cnsFormat.readSequence(coordinateFile)
  
  #
  # Read in a distance constraint list
  #

  distanceConstraintFile = os.path.join(dataDir,distanceConstraintFileName)
  ccpnConstraintList = cnsFormat.readDistanceConstraints(distanceConstraintFile)
  
  #
  # Do some preliminary Data Model navigation to get input parameters for
  # linkResonances
  #
  # An nmrConstraintStore links a group of constraint files
  # A structureGeneration links an nmrConstraintStore with a set of structures
  #
  
  nmrConstraintStore = ccpnConstraintList.nmrConstraintStore
  structureGeneration = nmrConstraintStore.findFirstStructureGeneration()
  
  #
  # Run linkResonances (this will generate a lot of output to the shell)
  #
  # Many options are available - see ccpnmr.format.process.linkResonances
  #
  # The current options are the 'safest' to maintain the original information,
  # although bear in mind that here all atoms in the original list are
  # considered to be stereospecifically assigned
  #
  # Set forceDefaultChainMapping to 0 if you want to interactively link the
  # chains in the CCPN data model to the information from the constraint file
  #
 
  cnsFormat.linkResonances(
                      
                      forceDefaultChainMapping = 1,
                      globalStereoAssign = 1,
                      setSingleProchiral = 1,
                      setSinglePossEquiv = 1,
                      strucGen = structureGeneration
                      
                      )
  
  #
  # Save the CCPN project as XML files
  #

  ccpnProject.saveModified()
  
  #
  # Navigate the Data Model, get a list of atoms per constraint item
  #
    
  for distConstr in ccpnConstraintList.sortedConstraints():

    print "Constraint %d: %.1f-%.1f" % (distConstr.serial, distConstr.lowerLimit, distConstr.upperLimit)

    for constrItem in distConstr.sortedItems():
      
      #
      # Now list the atoms linked to each of the two resonances associated with
      # this item.
      #
      
      atomList = []
      
      resonanceList = getResonancesFromPairwiseConstraintItem(constrItem)
            
      for resonance in resonanceList:
        atomList.append([])
        if resonance.resonanceSet:
          for atomSet in resonance.resonanceSet.atomSets:
            for atom in atomSet.atoms:
              atomList[-1].append("%d.%s" % (atom.residue.seqCode,atom.name))
              
        atomList[-1].sort()
        atomList[-1] = ','.join(atomList[-1])
        
      print "   (%s) - (%s)" % (atomList[0],atomList[1])
  
    print
    
  #
  # Finally, note that you can read a CCPN project back in as well... use
  # the following as an example:
  #
  #
  # from memops.general.Io import loadProject
  #
  # ccpnProject = loadProject('MyProjectDirectory')
  #
  #
