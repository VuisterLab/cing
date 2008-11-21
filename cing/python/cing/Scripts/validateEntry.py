from cing import verbosityDebug
from cing import verbosityNothing
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTwarning
from cing.core.classes import Project
from cing.core.constants import CYANA
from cing.core.constants import IUPAC
from cing.core.constants import PDB
from cing.core.constants import XPLOR
from cing.Libs.NTutils import NTmessage
from cing.Libs.disk import rmdir
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
    """
    fnametgz = entryId + '.tgz' 
    unametgz = url + '/' + fnametgz 
    NTdebug("downloading file:" + unametgz)
    try:
        urllib.urlretrieve(unametgz, fnametgz)
    except:
        NTwarning("Failed to download; " + unametgz)
        return

def main(entryId, *extraArgList):
    """inputDir may be a directory or a url. A url needs to start with http://.     
    """
    
    fastestTest = False
    htmlOnly = False # default is False but enable it for faster runs without some actual data.
    doWhatif = True # disables whatif actual run
    doProcheck = True
    if fastestTest:
        htmlOnly = True 
        doWhatif = False
        doProcheck = False
    
    expectedNumberOfArguments = 4
    if len(extraArgList) != expectedNumberOfArguments:
        NTerror("Got arguments: %s" % extraArgList)
        NTerror("Failed to get expected number of arguments: %d got %d" % (
            expectedNumberOfArguments, len(extraArgList)))
        return True
        
    inputDir = os.path.join(extraArgList[0], entryId)
    outputDir = extraArgList[1]
    pdbConvention = extraArgList[2] #@UnusedVariable
    restraintsConvention = extraArgList[3]

    NTdebug("Using:")
    NTdebug("inputDir:             " + inputDir)
    NTdebug("outputDir:            " + outputDir)
    NTdebug("pdbConvention:        " + pdbConvention)
    NTdebug("restraintsConvention: " + restraintsConvention)
    # presume the directory still needs to be created.
    if not os.path.isdir(outputDir):
        os.mkdir(outputDir)
    os.chdir(outputDir)
    
    project = Project(entryId)
    if project.removeFromDisk():
        NTerror("Failed to remove existing project (if present)")
        return True
        
    project = Project.open(entryId, status='new')
                
    isCcpnProject = False # TODO: refine
    if inputDir.startswith("http"):
        retrieveTgzFromUrl(entryId, inputDir)
        isCcpnProject = True
        
    if isCcpnProject:
        fnametgz = entryId + '.tgz'         
        if not project.initCcpn(ccpnFolder=fnametgz):
            NTerror("Failed to init project from ccpn")
            return True     
        os.unlink(fnametgz) # temporary ccpn tgz
        rmdir(entryId) # temporary ccpn dir        
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
        

if __name__ == "__main__":
    cing.verbosity = verbosityNothing
    cing.verbosity = verbosityDebug
    if main(*sys.argv[1:]):
        sys.exit(1)
