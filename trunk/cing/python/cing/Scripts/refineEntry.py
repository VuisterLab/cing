#!/usr/bin/env python
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.network import * #@UnusedWildImport
from cing.NRG import * #@UnusedWildImport
from cing.NRG.settings import * #@UnusedWildImport
from cing.Scripts.validateEntry import * #@UnusedWildImport
from cing.core.constants import * #@UnusedWildImport


# -1- Regular use: from nmr_redo.

# Execute like:
# cd /Library/WebServer/Documents/NMR_REDO/data/br/1brv
# python -u /Users/jd/workspace35/cing/python/cing/Scripts/refineEntry.py 1brv 9 \
# file:///Library/WebServer/Documents/NRG-CING/data \
#        /Library/WebServer/Documents/NMR_REDO \
# . . BY_CH23_BY_ENTRY CING 1 auto 0 0

#x = ARCHIVE_TYPE_BY_CH23_BY_ENTRY

def main(entryId, *extraArgList):
    """inputDir may be a directory or a url. A url needs to start with http://.
    """

    fastestTest = 0 # default: 0
    
    modelCountAnneal, bestAnneal, best = 200, 50, 25    
    htmlOnly = False # default: False but enable it for faster runs without some actual data.
    doWhatif = True # disables whatif actual run
    doProcheck = True
    doWattos = True
    doQueeny = True
    doTalos = True
    tgzCing = True # default: True # Create a tgz for the cing project. In case of a CING project input it will be overwritten.
                    # NB leave this set to True or modify code below.
#    modelCount = None # default setting is None
#    ranges = None

    if fastestTest:
        modelCountAnneal, bestAnneal, best = 4, 3, 2        
#        modelCount = 2 # if this is more and there is only one model present it leads to an error message.
        htmlOnly = True
        doWhatif = False
        doProcheck = False
        doWattos = False
        doQueeny = False
        doTalos = False
    FORCE_REDO = True
    FORCE_RETRIEVE_INPUT = True


    NTmessage(header)
    NTmessage(getStartMessage())

    # Sync below code with nrgCing#createToposTokens
    expectedArgumentList = """
    verbosity         inputDir             outputDir
    pdbConvention     restraintsConvention archiveType         projectType
    storeCING2db      ranges               filterTopViolations filterVasco
    singleCoreOperation
    """.split()
    expectedNumberOfArguments = len(expectedArgumentList)
    if len(extraArgList) != expectedNumberOfArguments:
        NTmessage("consider updating code to include all sequential parameters: %s" % str(expectedArgumentList))
        if len(extraArgList) > expectedNumberOfArguments:
            NTerror("Got arguments: " + `extraArgList`)
            NTerror("Failed to get expected number of arguments: %d got %d" % (
                expectedNumberOfArguments, len(extraArgList)))
            NTerror("Expected arguments: %s" % expectedArgumentList)
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

    NTdebug("Using program arguments:")
    NTdebug("inputDir:             %s" % inputDir)
    NTdebug("outputDir:            %s" % outputDir)
    NTdebug("pdbConvention:        %s" % pdbConvention)
    NTdebug("restraintsConvention: %s" % restraintsConvention)
    NTdebug("archiveType:          %s" % archiveType)
    NTdebug("projectType:          %s" % projectType)
    NTdebug("storeCING2db:         %s" % storeCING2db)
    NTdebug("ranges:               %s" % ranges)
    NTdebug("filterTopViolations:  %s" % filterTopViolations)
    NTdebug("filterVasco:          %s" % filterVasco)
    NTdebug("singleCoreOperation:  %s" % singleCoreOperation)
    NTdebug("")
    NTdebug("Using derived settings:")
    NTdebug("modelCountAnneal:     %s" % modelCountAnneal)
    NTdebug("bestAnneal:           %s" % bestAnneal)
    NTdebug("best:                 %s" % best)
    NTdebug("isRemoteOutputDir:    %s" % isRemoteOutputDir)
    
    # For NMR_REDO required as most efficient.
    if singleCoreOperation: 
        setToSingleCoreOperation()

    
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

    if isRemoteOutputDir:
        os.chdir(cingDirTmp)
    else:
        mkdirs(outputDir)
        os.chdir(outputDir)

    project = Project(entryId)
    if project.removeFromDisk():
        NTerror("Failed to remove existing project (if present)")
        return True
    # end if.

    formatFileName = '%s.tgz'
    if projectType == PROJECT_TYPE_CING:
        formatFileName = '%s.cing.tgz'
    elif projectType == PROJECT_TYPE_PDB:
        formatFileName = 'pdb%s.ent.gz'
    fileNameTgz = formatFileName % entryId

#    NTdebug("fileNameTgz: %s" % fileNameTgz)
    allowedInputProtocolList = 'http file ssh'.split()
    inputProtocal = string.split( inputDir, ':' )[0]
    if inputProtocal in allowedInputProtocolList:
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
             retrieveTgzFromUrl(entryId, inputDir, archiveType=archiveType, formatFileName=formatFileName)
        # end if
        if not os.path.exists(fileNameTgz):
            NTerror("Tgz should already have been present skipping entry")
            return
        # end if
    else:
        NTdebug("Entry not retrieved which might be normal in some situations.")
    # end if.

    if projectType == PROJECT_TYPE_CING:
        # Needs to be copied because the open method doesn't take a directory argument..
#        fullFileNameTgz = os.path.join(inputDir, fileNameTgz)
#        shutil.copy(fullFileNameTgz, '.')
        project = Project.open(entryId, status='old')
        if not project:
            NTerror("Failed to init old project")
            return True
    else:
        NTerror("Expected a CING project.")
        return True
        # end if
    # end if

####> MAIN UTILITY HERE
    if project.fullRedo(modelCountAnneal = modelCountAnneal, bestAnneal = bestAnneal, best = best):  
        NTerror("Failed fullAnnealAndRefine.")
        return True
    
          
    
    if ranges != None:
        project.molecule.setRanges(ranges)
    project.molecule.superpose(ranges=ranges)

    if 1: # DEFAULT 1?
        project.save()
    if project.validate(htmlOnly=htmlOnly, ranges=ranges, doProcheck=doProcheck, doWhatif=doWhatif,
            doWattos=doWattos, doQueeny = doQueeny, doTalos=doTalos, filterVasco = filterVasco ):
        NTerror("Failed to validate project read")
        return True
    # end if filterVasco

    project.save()

    if storeCING2db:
        # Does require:
        #from cing.PluginCode.sqlAlchemy import csqlAlchemy
        # and should never crash  run.
        archive_id = ARCHIVE_NMR_REDO_ID
#        if isProduction:
#            archive_id = ARCHIVE_NRG_ID
        try:
            if doStoreCING2db( entryId, archive_id, project=project):
                NTerror("Failed to store CING project's data to DB but continuing.")
        except:
            NTtracebackError()
            NTerror("Failed to store CING project's data due to above traceback error.")

    if tgzCing:
        directoryNameCing = entryId + ".cing"
        tgzFileNameCing = directoryNameCing + ".tgz"
        if os.path.exists(tgzFileNameCing):
            NTwarning("Overwriting: " + tgzFileNameCing)
        cmd = "tar -czf %s %s" % (tgzFileNameCing, directoryNameCing)
        NTdebug("cmd: %s" % cmd)
#        do_cmd(cmd)
        status, result = commands.getstatusoutput(cmd)
        if status:
            NTerror("Failed to tar status: %s with result %s" % (status, result))
            return True
        if isRemoteOutputDir:
            if putFileBySsh(tgzFileNameCing, outputDir, ntriesMax = 2):
                NTerror("Failed to send File By Scp status: %s with result %s" % (status, result))
                NTerror("Maintaining results.")
                return True
            # end if
            NTmessage("Removing tgz result: %s" % tgzFileNameCing)
            os.remove(tgzFileNameCing)
            NTmessage("Removing cing dir itself: %s" % directoryNameCing)
            rmdir(directoryNameCing)
        else: # do NOT remove local copy
            pass
        # end if/else
    # end if tgzCing
# end def

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
#        sys.exit(1) # can't be used in forkoff api
    try:
        status = main(*sys.argv[1:])
    finally:
        NTmessage(getStopMessage(cing.starttime))
