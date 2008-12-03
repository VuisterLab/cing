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
from shutil import rmtree
import cing
import os
import sys
import urllib

def usage():
    NTmessage("Use like eg:")
    NTmessage("python -u $CINGROOT/python/cing/Scripts/validateEntry.py entryId inputDir outputDir pdbConvention restraintsConvention")
    NTmessage("python -u $CINGROOT/python/cing/Scripts/validateEntry.py 1brv http://restraintsgrid.bmrb.wisc.edu/servlet_data/NRG_ccpn_tmp 1brv . .")

def retrieveTgzFromUrl(entryId, url):
    """Retrieves tgz file from url to current working dir assuming the
    source is named:      
    Will skip the download if it's already present.
    """
    fnametgz = entryId + '.tgz' 
    if os.path.exists(fnametgz):
        NTmessage("Tgz already present skip downloading")
        return
    unametgz = url + '/' + fnametgz 
    NTdebug("downloading url: " + unametgz)
    urllib.urlretrieve(unametgz, fnametgz) # consistently fails.

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
    FORCE_REDO = False
    
    expectedNumberOfArguments = 4
    if len(extraArgList) != expectedNumberOfArguments:
        NTerror("Got arguments: " + `extraArgList`)
        NTerror("Failed to get expected number of arguments: %d got %d" % (
            expectedNumberOfArguments, len(extraArgList)))
        return True
        
    entryCodeChar2and3 = entryId[1:3]        
    inputDir = os.path.join(extraArgList[0], entryId)
    outputDir = os.path.join( extraArgList[1], 'data', entryCodeChar2and3, entryId )
    pdbConvention = extraArgList[2] #@UnusedVariable
    restraintsConvention = extraArgList[3]

    NTdebug("Using:")
    NTdebug("inputDir:             " + inputDir)
    NTdebug("outputDir:            " + outputDir)
    NTdebug("pdbConvention:        " + pdbConvention)
    NTdebug("restraintsConvention: " + restraintsConvention)
    # presume the directory still needs to be created.
    cingEntryDir = entryId+".cing"
    
    if os.path.isdir(cingEntryDir):
        if FORCE_REDO:
            NTmessage("Enforcing a redo")
            rmtree(cingEntryDir)
        else:
            mainIndexFile = os.path.join( cingEntryDir, "index.html")
            isDone = os.path.isfile( mainIndexFile )
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
        
    project = Project.open(entryId, status='new')
                
    isCcpnProject = False # TODO: refine
    if inputDir.startswith("http"):
        fnametgz = entryId + '.tgz'
        stillToRetrieve = True
        if stillToRetrieve:
            if not os.path.exists(fnametgz):
                retrieveTgzFromUrl(entryId, inputDir)
        else:             
            if not os.path.exists(fnametgz):
                NTerror("Tgz should already have been present skipping entry")
                return        
#            retrieveTgzFromUrl(entryId, inputDir)
        isCcpnProject = True
        
    if isCcpnProject:
        fnametgz = entryId + '.tgz'         
        if not project.initCcpn(ccpnFolder=fnametgz):
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
        project.initPDB(pdbFile=pdbFilePath, convention=pdbConvention)
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
            project.cyana2cing(cyanaDirectory=inputDir,
                               convention=restraintsConvention,
                               copy2sources=True,
                               **kwds)
    project.save()
    if project.validate(htmlOnly=htmlOnly, doProcheck=doProcheck, doWhatif=doWhatif):
        NTerror("Failed to validate project read")
        return True
    project.save()
    if isCcpnProject:
#        fnametgz = entryId + '.tgz'         
#        os.unlink(fnametgz) # temporary ccpn tgz
        rmdir(entryId) # temporary ccpn dir        
    
        

if __name__ == "__main__":
    cing.verbosity = verbosityNothing
    cing.verbosity = verbosityDebug
    status = main(*sys.argv[1:])
#    return status
#        sys.exit(1) # can't be used in forkoff api
