""" 

Script to copy files from one or more source repositories to a single 
target repository. Can synchronize entire repository or a subbranch of it.

Customize by changing skipBeginnings and skipEndings at the top
and sourceRepDirs and targetRepDir near the bottom

Run by python updateExtendNmr.py mode target_dir verbose.
Try python updateExtendNmr.py for usage instructions
Try with mode==test first time

Currently set up for copying from ccpn repositories to extendNmr repository
"""


import filecmp
import os
import shutil
import sys

__author__ = 'Rasmus Fogh'

# Do not copy files and directories beginning with these strings:
skipBeginnings = ('.', 'CVS', 
                  # For CING added:
                  '.svn', )

# Do not copy files and diorectories if the full path ends tieh these strings.
skipEndings = ('.pyc', '.pyo', '$py.class', '~odp', '~odm', '.so', '.o', 
               '/all/python/ccpnmr/api', '/all/python/ccpnmr/xml', 
               '/all/python/memops/api', '/all/python/memops/xml', 
               '/all/python/ccp/api', '/all/python/ccp/xml',
               # For CING added:
               '.class',
               )

def compareTrees(destDir, origDir, localPath=None, compareFiles=True, 
                 verbose=False):
  
  origOnly = {}
  different = {}
  
  # normalize directories and check
  destDir = os.path.abspath(destDir)
  origDir = os.path.abspath(origDir)
  if localPath:
    dirPath = os.path.join(origDir, localPath)
  else:
    dirPath = origDir
    
  for dd in (destDir, origDir, dirPath):
    if not os.path.isdir(dd):
      raise ("Error, %s is not a directory" % dd)
  
  # depth-first loop over directories:
  dirPaths = [dirPath]
  while dirPaths:
    dirPath = dirPaths.pop()
    newDirPath = dirPath.replace(origDir, destDir)
  
    # loop over files to copy
    for fileName in os.listdir(dirPath):
 
      if [x for x in skipBeginnings if fileName.startswith(x)]:
        # ignore files with these beginnings
        continue
 
      filePath = os.path.join(dirPath, fileName)
      newFilePath = os.path.join(newDirPath, fileName)
      
      if [x for x in skipEndings if fileName.endswith(x)]:
        # ignore files with these endings
        continue
 
      elif os.path.isdir(filePath):
        ll = os.listdir(filePath)
        if 'CVS' in ll or '.svn' in ll:
          # If this directory has a CVS or .svn subdirectory, 
          # include it in the copy...
 
          if os.path.exists(newFilePath):
            if not os.path.isdir(newFilePath):
              raise("Error, %s is a directory but %s is not"
                    % (filePath, newFilePath))
          else:
            origOnly[newFilePath] = filePath
            
          dirPaths.append(filePath)
          continue
      
      elif verbose and os.path.islink(filePath) or not os.path.isfile(filePath):
        print ("Warning:%s in source neither directory nor normal file. Skipping ..." % filePath)      
      else:
        # source is normal file
        
        if os.path.exists(newFilePath):
          if compareFiles:
            if os.path.isfile(newFilePath):
              if not filecmp.cmp(filePath, newFilePath):
                different[newFilePath] =  filePath
            else:
              if verbose:
                print ("Warning: different type for files %s and %s. Skipping ..."
                       % (filePath, newFilePath))
        else:
          origOnly[newFilePath] =  filePath
  #
  return (origOnly, different)


def processRepositories(destDir, origDirs, localPath=None, mode='test',
                        verbose=False):
  
  lenDestDir = len(destDir)
  origOnly = {}
  different = {}
  destOnly = None
  for origDir in origDirs:
    orig, diff = compareTrees(destDir, origDir, localPath=localPath,
                              verbose=verbose)
    
    for key,val in orig.items():
      if key in origOnly:
        raise Exception("New file %s matches both %s and %s" 
                        % (key, val, origOnly[key]))
      else:
        origOnly[key] = val
    
    for key,val in diff.items():
      if key in different:
        raise Exception("Existing file %s matches both %s and %s" 
                        % (key, val, different[key]))
      else:
        different[key] = val
        
    dest, _junk = compareTrees(origDir, destDir, localPath=localPath,
                              compareFiles=False, verbose=verbose)
    
    if not destOnly:
      destOnly = set(dest.values())
    else:
      destOnly = destOnly.intersection(dest.values())
  
  for target, source in sorted(different.items()):
    localPath = target[lenDestDir+1:]
    print 'Files differ: ', source[:-len(localPath)], localPath
    if mode == 'copy':
      shutil.copy2(source, target)
    
  for target, source in sorted(origOnly.items()):
    print 'New file: ', source
    if mode == 'copy':
      shutil.copy2(source, target)
    
  for target in sorted(destOnly):
    print 'Remove file: ', target
    if mode == 'copy':
      os.remove(target)
  
  
  if mode == 'copy':
    print "File operations finished"
    print "NB Remember to 'svn delete' removed files and svn add new files!"
  
  elif mode == 'test':
    print "Done testing."
    print "If you want to apply above changes, repeat with mode == 'copy'"
  

if __name__ == '__main__':
  
  # Source repository directories, to copy from
  sourceRepDirs = ('/home/rhf22/CCPN/cvsroots/stable_2_0_7/ccpn',
                   '/home/rhf22/CCPN/cvsroots/stable_2_0_7/ccpnint',)

  # Target repository directory, to copy to
  targetRepDir = '/home/rhf22/CCPN/extend-nmr/ccpn'
  
  args = sys.argv[1:]
  
  if not args:
    print "Usage: python updateExtendNmr.py mode target_dir verbose"
    print "       mode in ('test','copy')"
    print "       target_dir is svn dir to update (optional)"
    print "       If arguments include string 'verbose' output will be verbose"
    sys.exit(1)
     
    # Test mode?
    if 'test' == args[0]:
      mode = 'test'
    elif 'copy' == args[0]:
      mode = 'copy'
    else:
      print "Aborting - no valid mode..."
      sys.exit()
 
    if 'verbose' in args:
      verbose=True
    else:
      verbose=False
 
    # target dir
    if len(args) > 2 or (len(args) > 1 and not verbose):
      targetDir = os.path.abspath(args[1])
      if not targetDir.startswith(targetRepDir):
        raise Exception(" Target dir %s must be within target repository %s" % (targetDir, targetRepDir))
      localPath = targetDir[len(targetRepDir):]
    else:
      targetDir = targetRepDir
      localPath = None
 
    #
    #
    processRepositories(targetRepDir, sourceRepDirs, localPath=localPath, mode=mode, verbose=verbose)
  
  
