#!/usr/bin/env python
"""
# One size fit all so the same code for VC and regular use.
# NB iCing uses the simple doValidateiCing.py script.
# Customized by arguments.

# -1- Regular use:

# Execute like:
# cd /Library/WebServer/Documents/NRG-CING/data/br/1brv
# python -u /Users/jd/workspace35/cing/python/cing/Scripts/validateEntry.py 1brv \
# file:///Library/WebServer/Documents/NRG-CING/recoordSync /Library/WebServer/Documents/NRG-CING . . BY_ENTRY CCPN True
# or:
# cd /Library/WebServer/Documents/CASD-NMR-CING/data/eR/NeR103ACheshire
# python -u /Users/jd/workspace35/cing/python/cing/Scripts/validateEntry.py NeR103ACheshire \
#     file:///Users/jd/CASD-NMR-CING/data /Library/WebServer/Documents/CASD-NMR-CING . . BY_CH23_BY_ENTRY CCPN
# or:
# cd /Library/WebServer/Documents/PDB-CING/data/as/2as0
# python -u /Users/jd/workspace35/cingStable/python/cing/Scripts/validateEntry.py 2as0  \
# file:///Users/jd/wattosTestingPlatform/pdb/data/structures/divided/pdb /Library/WebServer/Documents/PDB-CING . . BY_CH23 PDB

# -2- VC use:
9
$CINGROOT/python/cing/NRG/validateEntryForNrgByVC.py 1brv \
http://nmr.cmbi.ru.nl/NRG-CING/prep/C \
jd@localhost:/tmp \
. . BY_CH23_BY_ENTRY CCPN

Retrieves from http://nmr.cmbi.ru.nl/NRG-CING/prep/C/br/1brv/1brv.tgz
Scps to                 :     jd@localhost:/tmp/data/br/1brv/1brv.cing.tgz

For topos replace the first command by validateEntryNrg:
validateEntryNrg 1brv http://nmr.cmbi.umcn.nl/NRG-CING/input \
    jd@nmr.cmbi.umcn.nl:/Library/WebServer/Documents/NRG-CING . . BY_CH23_BY_ENTRY CCPN
"""
from cing import cingDirTmp
from cing import header
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.disk import copy
from cing.Libs.disk import rmdir
from cing.Libs.network import * #@UnusedWildImport
from cing.NRG import * #@UnusedWildImport
from cing.NRG.settings import * #@UnusedWildImport
from cing.NRG.storeCING2db import doStoreCING2db
from cing.core.classes import Project
from cing.core.constants import * #@UnusedWildImport
from cing.main import getStartMessage
from cing.main import getStopMessage
from shutil import rmtree
import shutil
import string
import urllib



ARCHIVE_TYPE_FLAT = 'FLAT'
ARCHIVE_TYPE_BY_ENTRY = 'BY_ENTRY'
ARCHIVE_TYPE_BY_CH23 = 'BY_CH23'
ARCHIVE_TYPE_BY_CH23_BY_ENTRY = 'BY_CH23_BY_ENTRY'

PROJECT_TYPE_CING = CING
PROJECT_TYPE_CCPN = CCPN
PROJECT_TYPE_CYANA = CYANA
PROJECT_TYPE_PDB = PDB
#PROJECT_TYPE_XPLOR = 3 # Not done yet.
PROJECT_TYPE_DEFAULT = PROJECT_TYPE_CING

IDX_VERBOSITY = 0
IDX_INPUT = 1
IDX_OUTPUT = 2
IDX_PDB = 3
IDX_RESTRAINTS = 4
IDX_ARCHIVE = 5
IDX_PROJECT_TYPE = 6
IDX_STORE_DB = 7
IDX_RANGES = 8
IDX_FILTER_TOP = 9
IDX_FILTER_VASCO = 10
IDX_SINGLE_CORE_OPERATION = 11


def main(entryId, *extraArgList):
    """inputDir may be a directory or a url. A url needs to start with http://.
    """

    fastestTest = False # default: False
    htmlOnly = False # default: False but enable it for faster runs without some actual data.
    doWhatif = True # disables whatif actual run
    doProcheck = True
    doWattos = True
    doQueeny = True
    doTalos = True
    tgzCing = True # default: True # Create a tgz for the cing project. In case of a CING project input it will be overwritten.
                    # NB leave this set to True or modify code below.
    removeCcpnDirectory = 1 # perhaps not so in the future.
    modelCount = None # default setting is None
#    ranges = None

    if fastestTest:
        modelCount = 2 # if this is more and there is only one model present it leads to an error message.
        htmlOnly = True
        doWhatif = False
        doProcheck = False
        doWattos = False
        doQueeny = False
        doTalos = False
        
    forceRedo = True
    forceRetrieveInput = True

    nTmessage(header)
    nTmessage(getStartMessage())

    # Sync below code with nrgCing#createToposTokens
    expectedArgumentList = """
    verbosity         inputDir             outputDir
    pdbConvention     restraintsConvention archiveType         projectType
    storeCING2db      ranges               filterTopViolations filterVasco
    singleCoreOperation
    """.split()
    expectedNumberOfArguments = len(expectedArgumentList)
    if len(extraArgList) != expectedNumberOfArguments:
        nTmessage("consider updating code to include all sequential parameters: %s" % str(expectedArgumentList))
        if len(extraArgList) > expectedNumberOfArguments:
            nTerror("Got arguments: " + str(extraArgList))
            nTerror("Failed to get expected number of arguments: %d got %d" % (
                expectedNumberOfArguments, len(extraArgList)))
            nTerror("Expected arguments: %s" % expectedArgumentList)
            return True
        # end if
    # end if
    entryCodeChar2and3 = entryId[1:3]
    cing.verbosity = int( extraArgList[IDX_VERBOSITY] )
    inputDir = extraArgList[IDX_INPUT]
    outputDir = os.path.join(extraArgList[IDX_OUTPUT], DATA_STR, entryCodeChar2and3, entryId)
    pdbConvention = extraArgList[IDX_PDB] #@UnusedVariable
    restraintsConvention = extraArgList[IDX_RESTRAINTS]
    archiveType = extraArgList[IDX_ARCHIVE] # Only used for deriving the input location not the output.
    projectType = extraArgList[IDX_PROJECT_TYPE]
    storeCING2db = stringMeansBooleanTrue( getDeepByKeysOrAttributes(extraArgList, IDX_STORE_DB))
    ranges = getDeepByKeysOrAttributes(extraArgList, IDX_RANGES)
    filterTopViolations = getDeepByKeysOrAttributes(extraArgList, IDX_FILTER_TOP)
    if filterTopViolations:
        filterTopViolations = int(filterTopViolations) # change '0' to 0
    filterVasco = getDeepByKeysOrAttributes(extraArgList, IDX_FILTER_VASCO)
    if filterVasco:
        filterVasco = int(filterVasco)
    else:
        filterVasco = 1 # Default should be True
    singleCoreOperation = getDeepByKeysOrAttributes(extraArgList, IDX_SINGLE_CORE_OPERATION )

    if archiveType == ARCHIVE_TYPE_FLAT:
        pass # default
    elif archiveType == ARCHIVE_TYPE_BY_ENTRY:
        inputDir = os.path.join(inputDir, entryId)
    elif archiveType == ARCHIVE_TYPE_BY_CH23:
        inputDir = os.path.join(inputDir, entryCodeChar2and3)
    elif archiveType == ARCHIVE_TYPE_BY_CH23_BY_ENTRY:
        inputDir = os.path.join(inputDir, entryCodeChar2and3, entryId)

    isRemoteOutputDir = False
    if '@' in outputDir:
        isRemoteOutputDir = True
#    vc = vCing('.') # argument is a fake master_ssh_url not needed here.

    nTdebug("Using program arguments:")
    nTdebug("inputDir:             %s" % inputDir)
    nTdebug("outputDir:            %s" % outputDir)
    nTdebug("pdbConvention:        %s" % pdbConvention)
    nTdebug("restraintsConvention: %s" % restraintsConvention)
    nTdebug("archiveType:          %s" % archiveType)
    nTdebug("projectType:          %s" % projectType)
    nTdebug("storeCING2db:         %s" % storeCING2db)
    nTdebug("ranges:               %s" % ranges)
    nTdebug("filterTopViolations:  %s" % filterTopViolations)
    nTdebug("filterVasco:          %s" % filterVasco)
    nTdebug("singleCoreOperation:  %s" % singleCoreOperation)    
    nTdebug("")
    nTdebug("Using derived settings:")
    nTdebug("modelCount:           %s" % modelCount)
    nTdebug("isRemoteOutputDir:    %s" % isRemoteOutputDir)
    
    # For NMR_REDO required as most efficient.
    if singleCoreOperation: 
        setToSingleCoreOperation()
    
    # presume the directory still needs to be created.
    cingEntryDir = entryId + ".cing"

    if os.path.isdir(cingEntryDir):
        if forceRedo:
            nTmessage("Enforcing a redo")
            rmtree(cingEntryDir)
        else:
            mainIndexFile = os.path.join(cingEntryDir, "index.html")
            isDone = os.path.isfile(mainIndexFile)
            if isDone:
                nTmessage("SKIPPING ENTRY ALREADY DONE")
                return
            nTmessage("REDOING BECAUSE VALIDATION CONSIDERED NOT DONE.")
            rmtree(cingEntryDir)
        # end if.
    # end if.

    if isRemoteOutputDir:
        os.chdir(cingDirTmp)
    else:
        os.chdir(outputDir)

    project = Project(entryId)
    if project.removeFromDisk():
        nTerror("Failed to remove existing project (if present)")
        return True
    # end if.

    formatFileName = '%s.tgz'
    if projectType == PROJECT_TYPE_CING:
        formatFileName = '%s.cing.tgz'
    elif projectType == PROJECT_TYPE_PDB:
        formatFileName = 'pdb%s.ent.gz'
    fileNameTgz = formatFileName % entryId

#    nTdebug("fileNameTgz: %s" % fileNameTgz)
    allowedInputProtocolList = 'http file ssh'.split()
    inputProtocal = string.split( inputDir, ':' )[0]
    if inputProtocal in allowedInputProtocolList:
        stillToRetrieve = False
        if os.path.exists(fileNameTgz):
            if forceRetrieveInput:
                os.unlink(fileNameTgz)
                stillToRetrieve = True
            # end if
        else:
            stillToRetrieve = True
        # end if
        if stillToRetrieve:
            retrieveTgzFromUrl(entryId, inputDir, archiveType=archiveType, formatFileName=formatFileName)
        # end if
        if not os.path.exists(fileNameTgz):
            nTerror("Tgz should already have been present skipping entry")
            return
        # end if
    else:
        nTdebug("Entry not retrieved which might be normal in some situations.")
    # end if.

    if projectType == PROJECT_TYPE_CING:
        # Needs to be copied because the open method doesn't take a directory argument..
        fullFileNameTgz = os.path.join(inputDir, fileNameTgz)
        shutil.copy(fullFileNameTgz, '.')
        project = Project.open(entryId, status='old')
        if not project:
            nTerror("Failed to init old project")
            return True
    elif projectType == PROJECT_TYPE_CCPN:
        project = Project.open(entryId, status='new')
        if not project.initCcpn(ccpnFolder=fileNameTgz, modelCount=modelCount):
            nTerror("Failed to init project from ccpn")
            return True
    elif projectType == PROJECT_TYPE_PDB:
        project = Project.open(entryId, status='new')
        pdbFilePath = entryId + ".pdb"
        gunzip(fileNameTgz, outputFileName=pdbFilePath, removeOriginal=True)
        project.initPDB(pdbFile=pdbFilePath, convention=IUPAC, nmodels=modelCount)
#        if tmpPdbFile:
        if True:
            nTdebug("Removing tmp: %s" % pdbFilePath)
            os.unlink(pdbFilePath)
    elif projectType == PROJECT_TYPE_CYANA:
        project = Project.open(entryId, status='new')
        pdbFileName = entryId + ".pdb"
        pdbFilePath = os.path.join(inputDir, pdbFileName)
        project.initPDB(pdbFile=pdbFilePath, convention=IUPAC, nmodels=modelCount)
        nTdebug("Reading files from directory: " + inputDir)
        kwds = {'uplFiles': [ entryId ], 'acoFiles': [ entryId ] }
        if os.path.exists(os.path.join(inputDir, entryId + ".prot")):
            if os.path.exists(os.path.join(inputDir, entryId + ".seq")):
                kwds['protFile'] = entryId
                kwds['seqFile'] = entryId
            else:
                nTerror("Failed to find the .seq file whereas there was a .prot file.")
        # Skip restraints if absent.
        if os.path.exists(os.path.join(inputDir, entryId + ".upl")):
            project.cyana2cing(cyanaDirectory=inputDir,
                               convention=restraintsConvention,
                               copy2sources=True,
                               nmodels=modelCount,
                               **kwds)
        # end if
    # end if
    if ranges != None:
        project.molecule.setRanges(ranges)
    project.molecule.superpose(ranges=ranges)
    if filterTopViolations and not project.filterHighRestraintViol():
        nTerror("Failed to filterHighRestraintViol")    
####> MAIN UTILITY HERE
    if 0: # DEFAULT 0
        project.save()
    if project.validate(htmlOnly=htmlOnly, ranges=ranges, doProcheck=doProcheck, doWhatif=doWhatif,
            doWattos=doWattos, doQueeny = doQueeny, doTalos=doTalos, filterVasco = filterVasco ):
        nTerror("Failed to validate project read")
        return True
    # end if filterVasco

    project.save()

    if storeCING2db:
        # Does require:
        #from cing.PluginCode.sqlAlchemy import csqlAlchemy
        # and should never crash  run.
        archive_id = ARCHIVE_DEV_NRG_ID
        if isProduction:
            archive_id = ARCHIVE_NRG_ID
        try:
            if doStoreCING2db( entryId, archive_id, project=project):
                nTerror("Failed to store CING project's data to DB but continuing.")
        except:
            nTtracebackError()
            nTerror("Failed to store CING project's data due to above traceback error.")

    if projectType == PROJECT_TYPE_CCPN:
#        fileNameTgz = entryId + '.tgz'
        os.unlink(fileNameTgz) # temporary ccpn tgz
        if removeCcpnDirectory:
            rmdir(entryId) # ccpn dir may contain vasco info.

    if tgzCing:
        directoryNameCing = entryId + ".cing"
        tgzFileNameCing = directoryNameCing + ".tgz"
        if os.path.exists(tgzFileNameCing):
            nTwarning("Overwriting: " + tgzFileNameCing)
        cmd = "tar -czf %s %s" % (tgzFileNameCing, directoryNameCing)
        nTdebug("cmd: %s" % cmd)
#        do_cmd(cmd)
        status, result = commands.getstatusoutput(cmd)
        if status:
            nTerror("Failed to tar status: %s with result %s" % (status, result))
            return True
        if isRemoteOutputDir:
            if putFileBySsh(tgzFileNameCing, outputDir, ntriesMax = 2):
                nTerror("Failed to send File By Scp status: %s with result %s" % (status, result))
                nTerror("Maintaining results.")
                return True
            # end if
            nTmessage("Removing tgz result: %s" % tgzFileNameCing)
            os.remove(tgzFileNameCing)
            nTmessage("Removing cing dir itself: %s" % directoryNameCing)
            rmdir(directoryNameCing)
        else: # do NOT remove local copy
            pass
        # end if/else
    # end if tgzCing
# end def


def retrieveTgzFromUrl(entryId, url, archiveType=ARCHIVE_TYPE_FLAT, formatFileName='%s.tgz'): # pylint: disable=W0613
    """Retrieves tgz file from url to current working dir assuming the
    source is named:      $url/$x/$x.tgz
    Will skip the download if it's already present.

    Returns True on failure or None on success.
    """
#    fileNameTgz = entryId + extension
    fileNameTgz = formatFileName % entryId
    if os.path.exists(fileNameTgz):
        nTmessage("Tgz already present, skipping download")
        return
#    nTdebug("fileNameTgz: %s" % fileNameTgz)

    pathInsert = ''
    # TODO: check
    # Commented out the next lines for NRG-CING but not certain this will work for all uses of this script.
#    if archiveType == ARCHIVE_TYPE_BY_ENTRY:
#        pathInsert = '/%s' % entryId
#    if archiveType == ARCHIVE_TYPE_BY_CH23_BY_ENTRY:
##        entryCodeChar2and3 = entryId[1:3]
#        pathInsert = '/%s/%s' % (entryCodeChar2and3, entryId)

    if url.startswith('file://'):
        pathSource = url.replace('file://', '')
        fullPathSource = "%s%s/%s" % (pathSource, pathInsert, fileNameTgz)
        nTmessage("copying file: %s to: %s" % (fullPathSource, fileNameTgz))
        if not os.path.exists(fullPathSource):
            nTerror("%s does not exist." % (fullPathSource))
            return True
        if not os.path.isfile(fullPathSource):
            nTerror("%s is not a file" % (fullPathSource))
            return True
        if os.path.exists(fileNameTgz):
            nTmessage('Removing old copy: %s' % fileNameTgz)
            os.unlink(fileNameTgz)
        copy(fullPathSource, fileNameTgz)
    elif url.startswith('http://'):
        urlNameTgz = "%s%s/%s" % (url, pathInsert, fileNameTgz)
        nTmessage("downloading url: %s to: %s" % (urlNameTgz, fileNameTgz))
        urllib.urlretrieve(urlNameTgz, fileNameTgz)
    elif url.startswith('ssh://'):
        urlNameTgz = "%s%s/%s" % (url, pathInsert, fileNameTgz)
        nTmessage("Retrieving by ssh: %s to: %s" % (urlNameTgz, fileNameTgz))
        if getFileBySsh(urlNameTgz, fileNameTgz, ntriesMax = 2):
            nTerror( "Giving up ")
    else:
        nTerror("url has to start with http:/ or file:/ but was: %s" % (url))
        return True

    if os.path.exists(fileNameTgz):
        return

    nTerror("Failed to download: " + urlNameTgz)
    return True


if __name__ == "__main__":
    cing.verbosity = verbosityDebug
#        sys.exit(1) # can't be used in forkoff api
    try:
        _status = main(*sys.argv[1:])
    finally:
        nTmessage(getStopMessage(cing.starttime))

