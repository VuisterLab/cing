#!/usr/bin/env python
# Run like (replace 1brv with any PDB entry)
# $CINGROOT/python/cing/Scripts/FC/vascoCingRefCheck.py 1brv

from cing.Libs.NTutils import * #@UnusedWildImport
from memops.api import Implementation
from memops.general.Io import loadProject
from memops.universal.Util import returnInt, returnFloat
from pdbe.software.vascoReferenceCheck import VascoReferenceCheck
import glob




"""
Additional install:

vascoRefData/ files, for statistical info.
vascoReferenceCheck.py, in pdbe.software (now part of SF CVS)

"""

class VascoCingReferenceCheck(VascoReferenceCheck):

  cingDataDir = "."
  dsspDataDirName = "dssp"
  whatIfDataDirName = "Whatif"

  vascoRefDataPath = 'vascoRefData'

  def setupDirectories(self,pdbCode):

    self.dsspDataDir = os.path.join(self.cingDataDir,pdbCode,self.dsspDataDirName)
    self.whatIfDataDir = os.path.join(self.cingDataDir,pdbCode,self.whatIfDataDirName)

    self.ccpnDir = "%s/%s" % (pdbCode,pdbCode)

  def writePdbFile(self):

    pass

  def createSsInfo(self):

    print "Fetching DSSP secondary structure info..."

    fileNames = glob.glob(os.path.join(self.dsspDataDir,"model_*.dssp"))

    self.allSsInfo = {}
    for fileName in fileNames:
      self.readDsspInfoFile(fileName)

    #
    # Now determine the most common SS element for each
    #

    self.ssInfo = {}

    for chainCode in self.allSsInfo.keys():
      self.ssInfo[chainCode] = {}
      for residueKey in self.allSsInfo[chainCode].keys():

        ssCodeDict = {}

        for ssCode in self.allSsInfo[chainCode][residueKey]:
          if not ssCodeDict.has_key(ssCode):
            ssCodeDict[ssCode] = 0
          ssCodeDict[ssCode] += 1

        ssCodeMax = 0
        ssCode = None
        for ssCodeTemp in ssCodeDict.keys():
          if ssCodeDict[ssCodeTemp] > ssCodeMax:
            ssCodeMax = ssCodeDict[ssCodeTemp]
            ssCode = ssCodeTemp

        # Convert...
        if ssCode in (' ',):
          ssCode = 'C'

        self.ssInfo[chainCode][residueKey] = ssCode

  def readDsspInfoFile(self,fileName):

    fin = open(fileName)
    lines = fin.readlines()
    fin.close()

    dataLine = False
    for line in lines:
      cols = line.split()

      if cols[0] == '#' and cols[1] == 'RESIDUE':
        dataLine = True

      elif dataLine:
        # Note; No insertion code?
        seqCode=returnInt(line[5:10])
        chainCode=line[11:12]
        secStruc=line[16:17]

        if not self.allSsInfo.has_key(chainCode):
          self.allSsInfo[chainCode]={}

        seqKey = (seqCode,' ')

        if not self.allSsInfo[chainCode].has_key(seqKey):
          self.allSsInfo[chainCode][seqKey] = []

        self.allSsInfo[chainCode][seqKey].append(secStruc)

  def createAsaInfo(self):

    print "Fetching WHATIF per-atom surface accessibility info..."

    fileNames = glob.glob(os.path.join(self.whatIfDataDir,"wsvacc*.log"))

    self.allWhatIfInfo = {'chains': {}}
    for fileName in fileNames:
      self.readWhatIfAsaInfoFile(fileName)

    #
    # Now determine the median ASA for each
    #

    self.whatIfInfo = self.allWhatIfInfo
    medianIndex = None

    for chainCode in self.whatIfInfo['chains'].keys():
      for seqKey in self.whatIfInfo['chains'][chainCode].keys():
        for atomName in self.whatIfInfo['chains'][chainCode][seqKey]['atoms'].keys():
          asaList = self.whatIfInfo['chains'][chainCode][seqKey]['atoms'][atomName]
          asaList.sort()

          if not medianIndex:
            medianIndex = int((len(asaList) / 2.0) + 0.5)

          self.whatIfInfo['chains'][chainCode][seqKey]['atoms'][atomName] = [asaList[medianIndex]]

  def readWhatIfAsaInfoFile(self,fileName):

    fin = open(fileName)
    lines = fin.readlines()
    fin.close()

    dataLine = False #@UnusedVariable
    for line in lines:

      line = line.strip()

      if line[0] == '*' or not line:
        continue

      fields = line.split(';')

      chainCode = fields[4]

      insertionCode = fields[3]
      if not insertionCode:
        insertionCode = ' '
      seqKey = (returnInt(fields[2]),insertionCode)

      atomName = fields[6]
      # TODO: any problems with | at beginning and end?
      accessibility = returnFloat(fields[7][1:-1])

      if not self.allWhatIfInfo['chains'].has_key(chainCode):
        self.allWhatIfInfo['chains'][chainCode]={}

      if not self.allWhatIfInfo['chains'][chainCode].has_key(seqKey):
        resLabel = fields[1]
        self.allWhatIfInfo['chains'][chainCode][seqKey] = {'hasBadAtoms': False, 'resLabel': resLabel, 'atoms': {}}

      if not self.allWhatIfInfo['chains'][chainCode][seqKey]['atoms'].has_key(atomName):
        self.allWhatIfInfo['chains'][chainCode][seqKey]['atoms'][atomName] = []

      self.allWhatIfInfo['chains'][chainCode][seqKey]['atoms'][atomName].append(accessibility)

  def findResidue(self,chain,seqKey):

    return chain.findFirstResidue(seqCode=seqKey[0],seqInsertCode=seqKey[1])

  def checkAllShiftLists(self):

    ccpnProject = loadProject(self.ccpnDir)

    for shiftList in ccpnProject.currentNmrProject.findAllMeasurementLists(className='ShiftList'):

      self.checkProject(ccpnProject=ccpnProject,shiftListSerial=shiftList.serial)
      self.tagProject()

  def tagProject(self):

    atomInfo = (('H',('H',None)),
                ('N',('N',None)),
                ('C_aliphatic',('C',3)))

    for (atomType,atomKey) in atomInfo:
      (rerefValue,rerefError) = self.rerefInfo[atomKey]
      if rerefValue != None:
        appData1 = Implementation.AppDataFloat(value=-rerefValue,application='VASCO',keyword='correction_%s' % atomType)
        appData2 = Implementation.AppDataFloat(value=rerefError,application='VASCO',keyword='correctionError_%s' % atomType)

        self.shiftList.addApplicationData(appData1)
        self.shiftList.addApplicationData(appData2)

    print self.shiftList.findAllApplicationData(application='VASCO')

if __name__ == '__main__':

  pdbCode = '1brv'

  import Tkinter

  root = Tkinter.Tk()

  # Try traditional for comparison
  #vascoReferenceCheck = VascoReferenceCheck(guiParent=root)
  #vascoReferenceCheck.checkProject(ccpnDir=ccpnDir)

  # Try the CING based check
  vascoReferenceCheck = VascoCingReferenceCheck(guiParent=root)
  vascoReferenceCheck.setupDirectories(pdbCode)
  vascoReferenceCheck.checkAllShiftLists()

  #vascoReferenceCheck.ccpnProject.saveModified()


