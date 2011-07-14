#@PydevCodeAnalysisIgnore # pylint: disable-all
import os

#
# Code to run executable on file per model (if available), and return results
#

def runExecPerModel(fileName,reader,tempFile):
  
  fin = open(fileName)
  pdbLines = fin.readlines()
  fin.close()
  
  models = {}
  
  for line in pdbLines:
    
    cols = line.split()
    
    if cols[0] == 'MODEL':
      modelNum = int(cols[1])
      models[modelNum] = []
    
    elif cols[0] == 'ATOM' and not models:
      # Use original file directly
      break
    
    # Only do ATOM lines, forget about HETATM stuff
    if cols[0] == 'ATOM':
      models[modelNum].append(line)
  
  #
  # Make sure temporary dir exists
  #
  
  (tempPathName,_tempFileName) = os.path.split(tempFile)
  if not os.path.exists(tempPathName):
    os.makedirs(tempPathName)
  
  #
  # Now run executable, per model if necessary, and get info
  #
  
  readInfo = []
  
  if not models:
  
    readInfo.append(reader.read(fileName))
    
  else:

    modelList = models.keys()
    modelList.sort()

    for modelNum in modelList:

      fout = open(tempFile,'w')

      for line in models[modelNum]:
        fout.write(line)

      fout.close()

      readInfo.append(reader.read(tempFile))
    
    # Clean up
    os.remove(tempFile)
    
  return readInfo

from ccp.general.Util import getOtherAtom

def createResidueProtonToHeavyAtom(residue):
  
  ccpCode = residue.ccpCode
  chemComp = residue.chemCompVar.chemComp

  protonToHeavyAtom = {ccpCode: {}}

  for heavyAtom in chemComp.sortedChemAtoms():

    if heavyAtom.elementSymbol == 'H':
      continue

    atomName = heavyAtom.name

    if atomName == 'OXT':
      continue

    bondedProtons = []

    for bond in heavyAtom.chemBonds:

      otherAtom = getOtherAtom(heavyAtom,bond)

      if otherAtom.elementSymbol == 'H':
        if atomName == 'N' and otherAtom.name != 'H':
          continue
        bondedProtons.append(otherAtom)

    if bondedProtons:
      chemAtomSet = bondedProtons[0].chemAtomSet
      if chemAtomSet:
        if chemAtomSet.isEquivalent or chemAtomSet.isProchiral == True:
          protonKey = [bp.name for bp in bondedProtons]
          protonKey.sort()
          protonKey = tuple(protonKey)
          protonToHeavyAtom[ccpCode][protonKey] = atomName

          if chemAtomSet.isEquivalent:
            continue

      for bp in bondedProtons:
        protonToHeavyAtom[ccpCode][bp.name] = atomName

  return protonToHeavyAtom

#
# Code to handle pickled dictionaries
#

def getPickledDict(fileName):

  import pickle

  dictionary = {}

  if os.path.exists(fileName):
    pickleFile = open(fileName)
    dictionary = pickle.load(pickleFile)
    pickleFile.close()

  return dictionary

def createPickledDict(fileName,dictionary):

  import pickle
  
  # Avoid trampling file on CTRL-C
  try:
    pickleFile = open(fileName,'w')
    pickle.dump(dictionary,pickleFile)
    pickleFile.close()
  except:
    print "  Warning: dictionary creation misfired!"
  
#
# Code to handle saving of reference dictionaries
#

def saveReferencePickledDict(fileName,dictionary,forceWrite = False):

  origDict = getPickledDict(fileName)
  
  # TODO: warning this only works if dictionary one level deep!
  origKeys = origDict.keys()
  origKeys.sort()
  
  newKeys = dictionary.keys()
  newKeys.sort()
  
  if origKeys != newKeys or forceWrite:
    createPickledDict(fileName,dictionary)

