#@PydevCodeAnalysisIgnore # pylint: disable-all
# TODO: Necessary or can get from stats?
#from pdbe.analysis.shifts.reref import make_selection, make_sel3

import os, random
import sys #@UnusedImport

from memops.general.Io import getTopDirectory
from memops.general.Io import loadProject
from memops.universal.Util import drawBox

from ccpnmr.format.general.Conversion import FormatConversion

from ccpnmr.format.general.Util import createSelection

from pdbe2.analysis.Util import getPickledDict
from pdbe2.analysis.Constants import protonToHeavyAtom
from pdbe2.analysis.shifts.reref.estimateReferences import estimate_reference_single, make_selection, make_sel3, select_entries

# User interaction classes
from ccpnmr.format.general.userInteraction import setupDataEntry
from ccpnmr.format.general.userInteraction import setupMessageReporter
from ccpnmr.format.general.userInteraction import setupMultiDialog

class VascoReferenceCheck:
 
  tempPath = 'tmp'
  ccpnDir = None
  
  vascoRefDataPath = os.path.join(getTopDirectory(),'python','pdbe','analysis','shifts','reref','data')

  # TODO: Make executable command line script?
  class VascoReferenceCheckError(StandardError):
    
    pass

  def __init__(self,guiParent=None,dataEntry=None,messageReporter=None,multiDialog=None, showMessages=True):
  
    self.guiParent = guiParent
    self.showMessages = showMessages
    
    if not dataEntry:
      dataEntry = setupDataEntry(guiParent)
    self.dataEntry = dataEntry
      
    if not messageReporter:
      messageReporter = setupMessageReporter(guiParent)
    self.messageReporter = messageReporter
    
    if not multiDialog:
      multiDialog = setupMultiDialog(guiParent)
    self.multiDialog = multiDialog
    
  def checkProject(self,ccpnProject=None,ccpnDir=None,structureEnsembleId=None,shiftListSerial=None):

    if self.showMessages:
        print drawBox(" VASCO: calculating rereferencing...")

    #
    # Get info from CCPN project
    #
    
    if ccpnProject:
      self.ccpnProject = ccpnProject
    elif ccpnDir:
      self.ccpnProject = loadProject(ccpnDir)
    elif self.ccpnDir:
      self.ccpnProject = loadProject(self.ccpnDir)
    else:
      from memops.editor.OpenProjectPopup import OpenProjectPopup
      _popup = OpenProjectPopup(self.guiParent, callback = self.initProject, modal=True)
    
    #
    # Get the relevant structureEnsemble
    #
    
    self.selectStructureEnsemble(structureEnsembleId=structureEnsembleId)
      
    #
    # Get the right shift list
    #
    
    self.selectShiftList(shiftListSerial=shiftListSerial)
          
    #
    # Prep the data
    #
    
    self.prepareData()
    
    #
    # Create a dictionary to run VASCO on
    #

    self.createEntryDict()
    
    #
    # Get VASCO reref data
    #
    
    self.getVascoRerefInfo()    
    
    
  def initProject(self,project=None):
  
    self.ccpnProject = project
    
  def selectStructureEnsemble(self, structureEnsembleId=None):
    
    self.structureEnsemble = None
    
    if self.ccpnProject.structureEnsembles:
      if len(self.ccpnProject.structureEnsembles) == 1:
        self.structureEnsemble = self.ccpnProject.findFirstStructureEnsemble()
      elif structureEnsembleId != None:
        self.structureEnsemble = self.ccpnProject.findFirstStructureEnsemble(ensembleId=structureEnsembleId)
      
      if not self.structureEnsemble:

        (selectionList,selectionDict) = createSelection(self.ccpnProject.sortedStructureEnsembles())

        interaction = self.multiDialog.SelectionList(

                           self.guiParent,
                           selectionList,
                           selectionDict = selectionDict,
                           title = "Project '%s': " % self.ccpnProject.name + 'Select structure ensemble for coordinates',
                           text = "Existing structure ensembles:"
                           )

        if interaction.isSelected:
          self.structureEnsemble = interaction.selection
        
      
    if not self.structureEnsemble:
      raise self.VascoReferenceCheckError("No structures available in, or selected from, project - cannot run VASCO without coordinates.")

  def selectShiftList(self, shiftListSerial=None):
  
    self.shiftList = None
    
    shiftLists = list(self.ccpnProject.currentNmrProject.findAllMeasurementLists(className='ShiftList'))
    
    if shiftLists:
      if len(shiftLists) == 1:
        self.shiftList = shiftLists[0]
      elif shiftListSerial != None:
        self.shiftList = self.ccpnProject.currentNmrProject.findFirstMeasurementList(className='ShiftList',serial=shiftListSerial)
      
      if not self.shiftList:

        (selectionList,selectionDict) = createSelection(shiftLists)

        interaction = self.multiDialog.SelectionList(

                           self.guiParent,
                           selectionList,
                           selectionDict = selectionDict,
                           title = "Project '%s': " % self.ccpnProject.name + 'Select shift list',
                           text = "Existing shift lists:"
                           )

        if interaction.isSelected:
          self.shiftList = interaction.selection
        
    if not self.shiftList:
      raise self.VascoReferenceCheckError("No shift list available in, or selected from, project - cannot run VASCO without chemical shifts.")
    
  def prepareData(self):

    self.createResMapping()
    
    self.writePdbFile()
    
    self.createSsInfo()
    
    self.createAsaInfo()
    
  def createSsInfo(self):

    from pdbe.analysis.external.stride.Util import StrideInfo #@UnresolvedImport

    if self.showMessages:
        print "Calculating STRIDE secondary structure info..."
    strideInfo = StrideInfo(self.tmpFilePath)
    self.ssInfo = strideInfo.getSsInfo()
    #print self.ssInfo

  def createAsaInfo(self):

    from pdbe.adatah.WhatIf import getWhatIfInfo #@UnresolvedImport

    if self.showMessages:
        print "Fetching WHATIF data..."
    self.whatIfInfo = getWhatIfInfo(None,inputFile=self.tmpFilePath,outputWhatIfFile="tmp/%s.pp" % self.tmpFileName)
    #print self.whatIfInfo
    
  def createResMapping(self):

    """

    Function that maps resonances to residues and actual atom names (not sets)

    """
    
    self.nmrProject = self.ccpnProject.currentNmrProject
    nmrResonances = self.nmrProject.sortedResonances()    

    resMapping = {}

    #
    # First make quick link for resonance -> atom
    #

    for resonance in nmrResonances:

      #
      # Only a link from the resonance to an atom if there is a resonanceSet...
      #

      if resonance.resonanceSet:

        atomSets = resonance.resonanceSet.sortedAtomSets()
        residue = atomSets[0].findFirstAtom().residue

        #
        # Go over the atomSets and atoms...
        #

        atomNameList = []

        for atomSet in atomSets:

          refAtom = atomSet.findFirstAtom()
          curResidue = refAtom.residue

          #
          # Check if all is OK (no mapping to different residues)
          #

          if curResidue != residue:
            if self.showMessages:
              print "  ERROR two residues to same resonance!"
            atomNameList = []
            break

          for atom in atomSet.atoms:
            atomNameList.append(atom.name)


        #
        # Do some sorting...
        #

        atomNameList.sort()
        atomNameList = tuple(atomNameList)

        resMapping[resonance] = [residue,atomNameList]

    self.resMapping = resMapping
  
  def writePdbFile(self):
 
    self.tmpFileName = "tmp.%d.pdb" % random.randint(0,10000000)
    self.tmpFilePath = os.path.join(self.tempPath,self.tmpFileName)
    
    if not os.path.exists(self.tempPath):
      os.mkdir(self.tempPath)

    fc = FormatConversion(ccpnProject=self.ccpnProject)

    addKeywords = {'structures': [self.structureEnsemble.sortedModels()[0]], 'version': '3.2' }
    fc.exportFile('coordinates','pdb',self.tmpFilePath,addKeywords = addKeywords)

  def createEntryDict(self):

    #
    # Put all into entry dictionary
    #

    self.entry = {}

    for chainCode in self.whatIfInfo['chains'].keys():

      chain = self.ccpnProject.currentMolSystem.findFirstChain(code=chainCode)
      if not chain:
        if self.showMessages:
          print "No info for chain %s" % (chainCode)
        continue

      molType = 'protein'
      protonToHeavyAtomDict = protonToHeavyAtom[molType]

      for seqKey in self.whatIfInfo['chains'][chainCode].keys():
        #  {'hasBadAtoms': False, 'resLabel': 'TRP', 'atoms': {'C': [0.0], 'CB': [0.0], 'CA': [0.0], 'CG': [0.0], 'O': [0.0], 'N': [0.0]}
        whatIfResInfo = self.whatIfInfo['chains'][chainCode][seqKey]

        ssCode = 'C'
        if self.ssInfo.has_key(chainCode) and self.ssInfo[chainCode].has_key(seqKey):
          ssCode = self.ssInfo[chainCode][seqKey]

        residue = self.findResidue(chain,seqKey)
        ccpCode = residue.ccpCode

        if not residue:
          if self.showMessages:
            print "No info for chain %s, residue %s" % (chainCode,str(seqKey))
          continue

        for resonance in self.resMapping.keys():
          if residue == self.resMapping[resonance][0]:
            atomNameTuple = self.resMapping[resonance][1]
            #print chainCode, seqKey
            #print atomNameTuple
            #print whatIfResInfo['atoms']

            #
            # Get shift value(s)
            #

            #shiftValues = []
            # JFD: Wim added extra selection to not get all shifts which 
            # would lead to errors.
            shift = resonance.findFirstShift(parentList=self.shiftList)

            """
            if shift:
              shiftValues.append(shift.value)

            allResonances = resonance.resonanceSet.sortedResonances()

            if len(allResonances) == 2:
              otherResonance = allResonances[not allResonances.index(resonance)]

              otherShift = otherResonance.findFirstShift()

              if otherShift and otherShift.value != shiftValues[0]:
                shiftValues.append(otherShift.value)

            """          
            #
            # Get atom name for getting exposure value
            #      

            if atomNameTuple[0][0] == 'H':
              if protonToHeavyAtomDict[ccpCode].has_key(atomNameTuple):
                heavyAtomNameKey = protonToHeavyAtomDict[ccpCode][atomNameTuple]
              elif  protonToHeavyAtomDict[ccpCode].has_key(atomNameTuple[0]):
                heavyAtomNameKey = protonToHeavyAtomDict[ccpCode][atomNameTuple[0]]
              elif atomNameTuple[0] == 'H1':
                heavyAtomNameKey = protonToHeavyAtomDict[ccpCode]['H']
              else:
                atomSetKey = "%s*" % atomNameTuple[0][:-1]
                try:           
                  heavyAtomNameKey = protonToHeavyAtomDict[ccpCode][atomSetKey]
                except:
                  print protonToHeavyAtomDict[ccpCode].keys()
                  raise
            else:
              heavyAtomNameKey = atomNameTuple[0]

            #print '  HEAVY', heavyAtomNameKey
            #print

            # Now get exposure (watch out if CD1,CD2 type info!)
            exposure = whatIfResInfo['atoms'][heavyAtomNameKey][0]

            if not self.entry.has_key(ccpCode):
              self.entry[ccpCode] = {}

            # Will this work for all? Confusing mix of names/tuples in code!!
            if not self.entry[ccpCode].has_key(atomNameTuple):
              self.entry[ccpCode][atomNameTuple] = ([],[],[])

            # Create entry dictionary information for rereferencing...
            if shift and exposure != None:

              correctedShiftValue = shift.value # Might want to add correction!
              shortSecStruc = ssCode

              insert = False
              insertIndex = 0 #@UnusedVariable
              for i in range(len(self.entry[ccpCode][atomNameTuple][0])-1,-1,-1):
                if exposure > self.entry[ccpCode][atomNameTuple][1][i]:
                  self.entry[ccpCode][atomNameTuple][0].insert(i+1,correctedShiftValue)
                  self.entry[ccpCode][atomNameTuple][1].insert(i+1,exposure)
                  self.entry[ccpCode][atomNameTuple][2].insert(i+1,shortSecStruc)
                  insertIndex = i+1 #@UnusedVariable
                  insert = True
                  break

              if not insert:
                self.entry[ccpCode][atomNameTuple][0].insert(0,correctedShiftValue)
                self.entry[ccpCode][atomNameTuple][1].insert(0,exposure)
                self.entry[ccpCode][atomNameTuple][2].insert(0,shortSecStruc)
  
  def findResidue(self,chain,seqKey):
  
    return chain.findFirstResidue(seqId=seqKey[0],seqInsertCode=seqKey[1])
  
  def getVascoRerefInfo(self):

    #
    # Get VASCO reference info
    #

    dateStamp = "20100225"

    stats = getPickledDict(os.path.join(self.vascoRefDataPath,"stats_%s.pp" % dateStamp))
    bounds = getPickledDict(os.path.join(self.vascoRefDataPath,"bounds_%s.pp" % dateStamp))
    
    self.rerefInfo = {}

    for molType in ('protein',):#'RNA'):

      if molType == 'protein':
        group0 = {'arg': ('cz',), #@UnusedVariable
                  'asn': ('cg',),
                  'asp': ('cg',),
                  'gln': ('cd',),
                  'glu': ('cd',),
                  'phe': ('cg',),
                  'trp': ('cd2','ce2'),
                  'tyr': ('cg', 'cz')}

        group1 = {'arg': ('cz',),
                  'asn': ('cg',),
                  'asp': ('cg',),
                  'gln': ('cd',),
                  'glu': ('cd',),
                  'phe': ('cg',),
                  'trp': ('cd2','ce2'),
                  'tyr': ('cg', 'cz'),
                  '*': ('c',)}

        group2 = {'his': ('cd2', 'ce1'),
                  'phe': ('cd1', 'cd2', 'ce1', 'ce2', 'cz'),
                  'trp': ('cd1', 'ce3', 'ch2', 'cz2', 'cz3'),
                  'tyr': ('cd1', 'cd2', 'ce1', 'ce2')}

        group4 = {'*': ('c',)}

      if molType == 'protein':
        n_points = 200 #@UnusedVariable
      else:
        # Less critical for DNA, RNA, ...
        n_points = 100 #@UnusedVariable

      for atom_type in ('H','C','N'):

        """
        #atom_type = 'H'
        ref_cutoff = None
        normalise = True
        exclude_outliers = 4.
        n_iterations = 1

        print 'Reading raw data...'
        full_set = getPickledDict(os.path.join("../originalData/results/",database))

        for entry in full_set.keys():
          if full_set[entry].has_key(molType):
            full_set[entry] = full_set[entry][molType]
          else:
            del(full_set[entry])

        print 'Running estimation for full set...'     
        full_ref, full_stats, full_bounds, full_processed = run_estimation(full_set, n=1, n_points=n_points,
                                                                               ref_cutoff=ref_cutoff,
                                                                               atom_type=atom_type,
                                                                               molType = molType)
        """

        if atom_type == 'C' and molType == 'protein':

          #sel0 = make_selection(group0)
          sel1 = make_selection(group1)
          sel2 = make_selection(group2)
          # TODO Fix this one!
          sel3 = make_sel3(stats[atom_type][3], sel1+sel2)
          sel4 = make_selection(group4)

          tmpEntry = {'tmpEntry': self.entry}

          #set_group0 = select_entries(tmpEntry, sel0)
          set_group1 = select_entries(tmpEntry, sel1)
          set_group2 = select_entries(tmpEntry, sel2)
          set_group3 = select_entries(tmpEntry, sel3)
          set_group4 = select_entries(tmpEntry, sel4)

          groups = {1: set_group1, 2: set_group2, 3: set_group3, 4: set_group4}

        else:
          groups = {None: self.entry}

        for i, group in groups.items():
        
          if atom_type == 'C' and molType == 'protein':
            useBounds = bounds[atom_type][i]
            useStats = stats[atom_type][i]
          else:
            useBounds = bounds[atom_type]
            useStats = stats[atom_type]

          if group.has_key('tmpEntry'):
            group = group['tmpEntry']

          (rerefValue,rerefError,_void) =  estimate_reference_single(group, useStats, useBounds, entry_name='temp', atom_type=atom_type,
                                          exclude_outliers=False,molType=molType,verbose=False)
                                          
          #print atom_type, i
          if rerefValue != None:
              rerefValue = -rerefValue
          self.rerefInfo[(atom_type,i)] = (rerefValue,rerefError)
    
    #
    # Print out info
    #
    
    atomKeys = self.rerefInfo.keys()
    atomKeys.sort()
    
    if self.showMessages:
        for atomKey in atomKeys:
          print atomKey,
          print self.rerefInfo[atomKey]
      
if __name__ == '__main__':

  import Tkinter

  root = Tkinter.Tk()

  vascoReferenceCheck = VascoReferenceCheck(guiParent=root)
  vascoReferenceCheck.checkProject()


