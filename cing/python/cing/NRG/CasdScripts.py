'''
Created on May 13, 2013

@author: rhf
'''

import os

# Set default locations
# NBNB should be moved to Constants file later
casdNmrDir = os.environ.get('CASD_HOME')
if not casdNmrDir:
  raise Exception("Environment variable CASD_HOME not set")
allDataDir = os.path.join(casdNmrDir, 'data')
topTmpDir = os.path.join(casdNmrDir, 'tmpdata')
if not os.path.exists(topTmpDir):
  os.makedirs(topTmpDir)

def dirToCasdTree(path=None, trialRun=False):
  """ Runner function: execute casdFileToTree for all files in dir
  printing warning where not possible.
  """
  
  if path is None:
    path = os.path.join(casdNmrDir, 'import')
  
  files = os.listdir(path)
  for ff in files:
    dest = None
    ll = ff.split('.',1)
    if len(ll) == 2:
      dest = casdFileDir(ll[0])
    if dest is None:
      print 'WARNING, file name %s does not start with CASD EntryName' % ff
    
    elif os.path.exists(dest):
      print 'MOVing:', ff, dest
      if not trialRun:
        os.rename(os.path.join(path,ff), os.path.join(dest,ff))
    else:
      print 'WARNING, destination directory %s does not exist' % dest
      

def casdFileDir(entryName):
  """ Determint CASD tree directory from entry name, which must start
   with pdbcode_Groupname_anint. or pdbcode_Org.
  """
  
  ll = entryName.split('_')
  if (len(ll) ==3 or (len(ll) == 2 and ll[1] == 'Org')) and len(ll[0]) > 3:
    # name fits naming pattern
    return os.path.join(allDataDir, entryName[1:3], entryName)
  else:
    return None
    
  
def getEntryName(info, isOriginal=False):
  """ Get entry name from info dictionary. 
  if isOriginal get name of CASD input (...._Org)
  
  NBNB copy of function in ccpn/python/nijmegen/CASD/Util.py
  NBNB must be consolidated
  """
  mainId = info.get('PDBcode')
  if mainId:
    mainId = mainId.lower()
  else:
    mainId = info['Target']
  
  if isOriginal or 'Program' not in info:
    #Original data - put in Org
    return mainId + '_Org'
  
  else:
    entryID = info.get('EntryID', '???')
    group = info.get('Group', '????')
    return '%s_%s_%s' % (mainId, group, entryID, )
  


if __name__ == '__main__':
  
  pass
  # move files from import directory to CASD tree
  #dirToCasdTree(trialRun=True)
  dirToCasdTree()
  
