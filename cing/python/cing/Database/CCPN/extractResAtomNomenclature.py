

from memops.api import Implementation

memopsRoot = Implementation.MemopsRoot(name='TestOnly')

names = ['CING','CYANA2.1','DIANA','IUPAC','CIF']

resData = []

atomData = {}

for chemComp in memopsRoot.chemComps:
  
  if chemComp.molType == 'other':
    
    chemCompVars = chemComp.findAllChemCompVars()
  
  else:
    chemCompVars = chemComp.findAllChemCompVars(linking='middle')
    
  for chemCompVar in chemCompVars:
  
    resText = 'RESIDUE '
    atomDict = {}
    chemAtoms = []
    chemAtomSets = []
    for chemAtom in chemCompVar.chemAtoms:
      if chemAtom.className == 'ChemAtom':
        atomDict[chemAtom.name] = {}
        chemAtoms.append(chemAtom)

    for chemAtomSet in chemCompVar.chemAtomSets:
      atomDict[chemAtomSet.name] = {}
      chemAtomSets.append(chemAtomSet)
    
    for name in names:

      namingSystem = chemComp.findFirstNamingSystem(name=name)
             
      resCode = '-' # chemComp.code3Letter # Default for unspecified info
 
      if namingSystem:
        sysName = chemCompVar.findFirstSpecificSysName(namingSystem=namingSystem) \
                  or chemCompVar.findFirstChemCompSysName(namingSystem=namingSystem) \
                  or namingSystem.mainChemCompSysName \
                  or namingSystem.findFirstChemCompSysName()
 
        if sysName:
          resCode = sysName.sysName
        else:
          resCode = chemComp.code3Letter
 
        atomReference = namingSystem.atomReference
        atomSetReference = namingSystem.atomSetReference
 
        for chemAtom in chemAtoms:
          atomSysName = namingSystem.findFirstAtomSysName(atomName=chemAtom.name,
                                                          atomSubType=chemAtom.subType)

          if atomReference and  not atomSysName:
            atomSysName = atomReference.findFirstAtomSysName(atomName=chemAtom.name,
                                                             atomSubType=chemAtom.subType)
 
          if atomSysName:
            atomDict[chemAtom.name][name] = atomSysName.sysName

        for chemAtomSet in chemAtomSets:
          atomSysName = namingSystem.findFirstAtomSysName(atomName=chemAtomSet.name,
                                                         atomSubType=chemAtomSet.subType)

          if atomSetReference and not atomSysName:
            atomSysName = atomSetReference.findFirstAtomSysName(atomName=chemAtomSet.name,
                                                         atomSubType=chemAtomSet.subType)

          if atomSysName:
            atomDict[chemAtomSet.name][name] = atomSysName.sysName
       

      resText += ' %s %-4s' % (name, resCode)
  
    ccpId = '%s %s' % (chemComp.ccpCode,
                       chemCompVar.descriptor)
  
    resText += '  CCPN %s %-4s' % (chemComp.molType, ccpId)
    
    atomTexts = []
    chemAtomNames = atomDict.keys()
    chemAtomNames.sort()
    
    for chemAtomName in chemAtomNames:
      atomText = 'ATOM '
      for name in names:
        sysName = atomDict[chemAtomName].get(name, '-')
        atomText += ' %5s %-7s' % (name, sysName)
      
      atomText += '  CCPN %s' % chemAtomName
      atomTexts.append(atomText)

    atomData[chemCompVar] = atomTexts 

    resData.append( (resText, chemCompVar) )
 
resData.sort()

for t, chemCompVar in resData:
  atomTexts = atomData.get(chemCompVar, [])
  print t
  
  for a in atomTexts:
    print a

  print 'ENDRES'
      
