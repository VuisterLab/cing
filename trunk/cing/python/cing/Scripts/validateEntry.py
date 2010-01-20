# python -u $CINGROOT/python/cing/Scripts/validateEntry.py
from cing import header
from cing import verbosityDebug
from cing import verbosityNothing
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTwarning
from cing.Libs.disk import rmdir
from cing.Libs.forkoff import do_cmd
from cing.core.classes import Project
from cing.core.constants import CCPN
from cing.core.constants import CING
from cing.core.constants import CYANA
from cing.core.constants import IUPAC
from cing.core.constants import PDB
from cing.core.constants import XPLOR
from cing.main import getStartMessage
from cing.main import getStopMessage
from shutil import rmtree
import cing
import os
import shutil
import sys
import urllib

ARCHIVE_TYPE_FLAT = 'FLAT'
ARCHIVE_TYPE_BY_ENTRY = 'BY_ENTRY'
ARCHIVE_TYPE_BY_CH23_BY_ENTRY = 'BY_CH23_BY_ENTRY'

PROJECT_TYPE_CING = CING
PROJECT_TYPE_CCPN = CCPN
PROJECT_TYPE_CYANA = CYANA
#PROJECT_TYPE_XPLOR = 3 # Not done yet.
PROJECT_TYPE_DEFAULT = PROJECT_TYPE_CING

def usage():
    NTmessage("Call from validateNRG.py -> doScriptOnEntryList.py")


def main(entryId, *extraArgList):
    """inputDir may be a directory or a url. A url needs to start with http://.
    """

    fastestTest = False # default: False
    htmlOnly = False # default: False but enable it for faster runs without some actual data.
    doWhatif = True # disables whatif actual run
    doProcheck = True
    doWattos = True
    tgzCing = True # default: True # Create a tgz for the cing project. In case of a CING project input it will be overwritten.
#    modelCount=2
    modelCount=None # default setting is None
    if fastestTest:
        modelCount=2
        htmlOnly = True
        doWhatif = False
        doProcheck = False
        doWattos = False
    FORCE_REDO = True
    FORCE_RETRIEVE_INPUT = True


    NTmessage(header)
    NTmessage(getStartMessage())

    expectedArgumentList = [ 'inputDir', 'outputDir', 'pdbConvention', 'restraintsConvention', 'archiveType', 'projectType' ]
    expectedNumberOfArguments = len(expectedArgumentList)
    if len(extraArgList) != expectedNumberOfArguments:
        NTerror("Got arguments: " + `extraArgList`)
        NTerror("Failed to get expected number of arguments: %d got %d" % (
            expectedNumberOfArguments, len(extraArgList)))
        NTerror("Expected arguments: %s" % expectedArgumentList)
        return True

    entryCodeChar2and3 = entryId[1:3]

    inputDir = extraArgList[0]
    outputDir = os.path.join(extraArgList[1], 'data', entryCodeChar2and3, entryId)
    pdbConvention = extraArgList[2] #@UnusedVariable
    restraintsConvention = extraArgList[3]
    archiveType = extraArgList[4]
    projectType = extraArgList[5]

    if archiveType == ARCHIVE_TYPE_FLAT:
        pass
        # default
    elif archiveType == ARCHIVE_TYPE_BY_ENTRY:
        inputDir = os.path.join(inputDir, entryId)
    elif archiveType == ARCHIVE_TYPE_BY_CH23_BY_ENTRY:
        inputDir = os.path.join(inputDir, entryCodeChar2and3, entryId)

    NTdebug("Using:")
    NTdebug("inputDir:             " + inputDir)
    NTdebug("outputDir:            " + outputDir)
    NTdebug("pdbConvention:        " + pdbConvention)
    NTdebug("restraintsConvention: " + restraintsConvention)
    NTdebug("archiveType:          " + archiveType)
    NTdebug("projectType:          " + projectType)
    NTdebug("modelCount:           " + modelCount)
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
        # end if.
    # end if.

    os.chdir(outputDir)

    project = Project(entryId)
    if project.removeFromDisk():
        NTerror("Failed to remove existing project (if present)")
        return True
    # end if.

    fileNameTgz = entryId + '.tgz'
    if projectType == PROJECT_TYPE_CING:
        fileNameTgz = entryId + '.cing.tgz'
    # if true will do retrieveTgzFromUrl.
    if inputDir.startswith("http") or inputDir.startswith("file"):
        stillToRetrieve = False
        if os.path.exists(fileNameTgz):
            if FORCE_RETRIEVE_INPUT:
                os.unlink(fileNameTgz)
                stillToRetrieve = True
            # end if
        else:
            stillToRetrieve = True
        # end if
        if stillToRetrieve:
             retrieveTgzFromUrl(entryId, inputDir, archiveType = archiveType)
        # end if
        if not os.path.exists(fileNameTgz):
            NTerror("Tgz should already have been present skipping entry")
            return
        # end if
    # end if.
#            retrieveTgzFromUrl(entryId, inputDir)

    if projectType == PROJECT_TYPE_CING:
        # Needs to be copied because the open method doesn't take a directory argument..
        fullFileNameTgz = os.path.join(inputDir, fileNameTgz)
        shutil.copy(fullFileNameTgz, '.')
        project = Project.open(entryId, status = 'old')
        if not project:
            NTerror("Failed to init old project")
            return True
    elif projectType == PROJECT_TYPE_CCPN:
        project = Project.open(entryId, status = 'new')
        if not project.initCcpn(ccpnFolder = fileNameTgz, modelCount=modelCount):
            NTerror("Failed to init project from ccpn")
            return True
    elif projectType == PROJECT_TYPE_CYANA:
        project = Project.open(entryId, status = 'new')
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
        project.initPDB(pdbFile = pdbFilePath, convention = pdbConvention, nmodels=modelCount)
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
                               nmodels = modelCount,
                               **kwds)

    project.save()
    if project.validate(htmlOnly = htmlOnly, doProcheck = doProcheck, doWhatif = doWhatif, doWattos=doWattos):
        NTerror("Failed to validate project read")
        return True
    project.save()
    if projectType == PROJECT_TYPE_CCPN:
#        fileNameTgz = entryId + '.tgz'
#        os.unlink(fileNameTgz) # temporary ccpn tgz
        rmdir(entryId) # temporary ccpn dir

    if tgzCing:
        directoryNameCing = entryId + ".cing"
        tgzFileNameCing = directoryNameCing + ".tgz"
        if os.path.exists(tgzFileNameCing):
            NTwarning("Overwriting: " + tgzFileNameCing)
        cmd = "tar -czf %s %s" % (tgzFileNameCing, directoryNameCing)
        do_cmd(cmd)


def retrieveTgzFromUrl(entryId, url, archiveType = ARCHIVE_TYPE_FLAT):
    """Retrieves tgz file from url to current working dir assuming the
    source is named:      $url/$x/$x.tgz
    Will skip the download if it's already present.

    Returns True on failure or None on success.
    """
    fileNameTgz = entryId + '.tgz'
    if os.path.exists(fileNameTgz):
        NTmessage("Tgz already present, skipping download")
        return

    pathInsert = ''
    # TODO: check
    # Commented out the next lines for NRG-CING but not certain this will work for all uses of this script.
#    if archiveType == ARCHIVE_TYPE_BY_ENTRY:
#        pathInsert = '/%s' % entryId
    if archiveType == ARCHIVE_TYPE_BY_CH23_BY_ENTRY:
        entryCodeChar2and3 = entryId[1:3]
        pathInsert = '/%s/%s' % (entryCodeChar2and3, entryId)

    if url.startswith('file:/'):
        pathSource = url.replace('file:/', '')
        fullPathSource = "%s%s/%s" % (pathSource, pathInsert, fileNameTgz)
        NTmessage("copying file: %s to: %s" % (fullPathSource, fileNameTgz))
        if not os.path.exists(fullPathSource):
            NTerror("%s does not exist." % (fullPathSource))
            return True
        if not os.path.isfile(fullPathSource):
            NTerror("%s is not a file" % (fullPathSource))
            return True
        os.symlink(fullPathSource, fileNameTgz)
    elif url.startswith('http:/'):
        urlNameTgz = "%s%s/%s" % (url, pathInsert, fileNameTgz)
        NTmessage("downloading url: %s to: %s" % (urlNameTgz, fileNameTgz))
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
