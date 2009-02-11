from cing import header
from cing import verbosityDebug
from cing import verbosityNothing
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.Libs.disk import rmdir
from cing.core.classes import Project
from cing.core.constants import CYANA
from cing.core.constants import IUPAC
from cing.core.constants import PDB
from cing.core.constants import XPLOR
from cing.main import getStartMessage
from cing.main import getStopMessage
from shutil import rmtree
import cing
import os
import sys
import urllib

def usage():
    NTmessage("Call from validateNRG.py -> doScriptOnEntryList.py")


def main(entryId, *extraArgList):
    """inputDir may be a directory or a url. A url needs to start with http://.     
    """
        
    fastestTest = True
    htmlOnly = False # default is False but enable it for faster runs without some actual data.
    doWhatif = True # disables whatif actual run
    doProcheck = True
    if fastestTest:
        htmlOnly = True 
        doWhatif = False
        doProcheck = False
    FORCE_REDO = True
    FORCE_RETRIEVE_INPUT = True
    
    
    NTmessage(header)
    NTmessage(getStartMessage())
    
    expectedNumberOfArguments = 5
    if len(extraArgList) != expectedNumberOfArguments:
        NTerror("Got arguments: " + `extraArgList`)
        NTerror("Failed to get expected number of arguments: %d got %d" % (
            expectedNumberOfArguments, len(extraArgList)))
        return True
        
    entryCodeChar2and3 = entryId[1:3]        
    inputDir = os.path.join(extraArgList[0], entryId)
    outputDir = os.path.join(extraArgList[1], 'data', entryCodeChar2and3, entryId)
    pdbConvention = extraArgList[2] #@UnusedVariable
    restraintsConvention = extraArgList[3]
    archiveType = extraArgList[4]

    NTdebug("Using:")
    NTdebug("inputDir:             " + inputDir)
    NTdebug("outputDir:            " + outputDir)
    NTdebug("pdbConvention:        " + pdbConvention)
    NTdebug("restraintsConvention: " + restraintsConvention)
    # presume the directory still needs to be created.
    cingEntryDir = entryId + ".cing"
    
    if os.path.isdir(cingEntryDir):
        if FORCE_REDO:
            NTmessage("Enforcing a redo")
            rmtree(cingEntryDir)
        else:
            mainIndexFile = os.path.join(cingEntryDir, "index.html")
            isDone = os.path.isfile(mainIndexFile)
            if isDone:
                NTmessage("SKIPPING ENTRY ALREADY DONE")
                return
            NTmessage("REDOING BECAUSE VALIDATION CONSIDERED NOT DONE.")
            rmtree(cingEntryDir)
                
        
    os.chdir(outputDir)
    
    project = Project(entryId)
    if project.removeFromDisk():
        NTerror("Failed to remove existing project (if present)")
        return True
        
    project = Project.open(entryId, status = 'new')
                
    isCcpnProject = False 
    # if true will do retrieveTgzFromUrl.
    if inputDir.startswith("http") or inputDir.startswith("file"):
        fileNameTgz = entryId + '.tgz'
        stillToRetrieve = False
        if os.path.exists(fileNameTgz):
            if FORCE_RETRIEVE_INPUT:
                os.unlink(fileNameTgz)
                stillToRetrieve = True
        else:
            stillToRetrieve = True           
            
        if stillToRetrieve:
             retrieveTgzFromUrl(entryId, inputDir, archiveType = archiveType)
             
        if not os.path.exists(fileNameTgz):
            NTerror("Tgz should already have been present skipping entry")
            return        
#            retrieveTgzFromUrl(entryId, inputDir)
        isCcpnProject = True
        
    if isCcpnProject:
        fileNameTgz = entryId + '.tgz'         
        if not project.initCcpn(ccpnFolder = fileNameTgz):
            NTerror("Failed to init project from ccpn")
            return True     
    else:
        pdbFileName = entryId + ".pdb"
    #    pdbFilePath = os.path.join( inputDir, pdbFileName)
        pdbFilePath = os.path.join(inputDir, pdbFileName)
        
        if True:
            pdbConvention = IUPAC
            if entryId.startswith("1YWUcdGMP"):
                pdbConvention = XPLOR
            if entryId.startswith("2hgh"):
                pdbConvention = CYANA
            if entryId.startswith("1tgq"):
                pdbConvention = PDB
        project.initPDB(pdbFile = pdbFilePath, convention = pdbConvention)
        NTdebug("Reading files from directory: " + inputDir)
        kwds = {'uplFiles': [ entryId ],
                'acoFiles': [ entryId ]              
                  }
        
        if entryId.startswith("1YWUcdGMP"):
            del(kwds['acoFiles'])
            
        if os.path.exists(os.path.join(inputDir, entryId + ".prot")):
            if os.path.exists(os.path.join(inputDir, entryId + ".seq")):
                kwds['protFile'] = entryId
                kwds['seqFile'] = entryId
            else:
                NTerror("Failed to find the .seq file whereas there was a .prot file.")
    
        # Skip restraints if absent.
        if os.path.exists(os.path.join(inputDir, entryId + ".upl")):
            project.cyana2cing(cyanaDirectory = inputDir,
                               convention = restraintsConvention,
                               copy2sources = True,
                               **kwds)
    project.save()
    if project.validate(htmlOnly = htmlOnly, doProcheck = doProcheck, doWhatif = doWhatif):
        NTerror("Failed to validate project read")
        return True
    project.save()
    if isCcpnProject:
#        fileNameTgz = entryId + '.tgz'         
#        os.unlink(fileNameTgz) # temporary ccpn tgz
        rmdir(entryId) # temporary ccpn dir        
    
        
ARCHIVE_TYPE_FLAT = 0
ARCHIVE_TYPE_BY_ENTRY = 1
ARCHIVE_TYPE_BY_CH23_BY_ENTRY = 2

def retrieveTgzFromUrl(entryId, url, archiveType = ARCHIVE_TYPE_FLAT):
    """Retrieves tgz file from url to current working dir assuming the
    source is named:      $url/$x/$x.tgz
    Will skip the download if it's already present.
    
    Returns True on failure or None on success.
    """
    fileNameTgz = entryId + '.tgz' 
    if os.path.exists(fileNameTgz):
        NTmessage("Tgz already present skip downloading")
        return
    
    pathInsert = ''
    if archiveType == ARCHIVE_TYPE_BY_ENTRY:
        pathInsert = '/%s' % entryId
    if archiveType == ARCHIVE_TYPE_BY_CH23_BY_ENTRY:
        entryCodeChar2and3 = entryId[1:3]
        pathInsert = '/%s/%s' % (entryCodeChar2and3, entryId)
        
    if url.startswith('file:/'):
        pathSource = url.replace('file:/', '')
        fullPathSource = "%s%s/%s" % (pathSource, pathInsert, fileNameTgz) 
        NTdebug("copying file: %s to: %s" % (fullPathSource, fileNameTgz))
        if not os.path.exists(fullPathSource):
            NTerror("%s does not exist." % (fullPathSource))
            return True            
        if not os.path.isfile(fullPathSource):
            NTerror("%s is not a file" % (fullPathSource))
            return True            
        os.link(fullPathSource, fileNameTgz)
    elif url.startswith('http:/'):
        urlNameTgz = "%s%s/%s" % (url, pathInsert, fileNameTgz) 
        NTdebug("downloading url: %s to: %s" % (urlNameTgz, fileNameTgz))        
        urllib.urlretrieve(urlNameTgz, fileNameTgz)        
    else:
        NTerror("url has to start with http:/ or file:/ but was: %s" % (url))
        return True
        
    if os.path.exists(fileNameTgz):
        return
    
    NTerror("Failed to download: " + urlNameTgz)
    return True
    

if __name__ == "__main__":
    cing.verbosity = verbosityNothing
    cing.verbosity = verbosityDebug
    
#        sys.exit(1) # can't be used in forkoff api
    try:
        status = main(*sys.argv[1:])
    finally:
        NTmessage(getStopMessage())
