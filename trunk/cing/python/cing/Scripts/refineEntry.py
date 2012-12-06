#!/usr/bin/env python

"""
Regular use: from nmr_redo.

    verbosity         
    inputDir             outputDir
    pdbConvention     restraintsConvention archiveType         projectType
    storeCING2db      ranges               filterTopViolations filterVasco
    singleCoreOperation

Execute like:

#set x = 2kq3
set x = 1brv
set ch23 = ( `echo $x | cut -c2-3` )
mkdir -p $D/NMR_REDO/data/$ch23/$x
cd !$
$C/python/cing/Scripts/refineEntry.py $x 9 file://$D/NRG-CING/data $D/NMR_REDO . . BY_CH23_BY_ENTRY CING 0 auto 0 0 0 >& $x"_ref".log &

or as remote slave. NB the 
    input directory name will be postfixed with  (          entryCodeChar2and3, entryId)
    output directory name will be postfixed with (DATA_STR, entryCodeChar2and3, entryId)

cd /home/i/tmp/cingTmp 
$C/python/cing/Scripts/refineEntry.py $x 9 \
    http://nmr.cmbi.ru.nl/NRG-CING/data i@nmr.cmbi.ru.nl:/mnt/data/D/NMR_REDO \
    . . BY_CH23_BY_ENTRY CING 0 auto 0 0 1 >& $x"_ref".log &

"""

from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.network import * #@UnusedWildImport
from cing.NRG import * #@UnusedWildImport
from cing.NRG.settings import * #@UnusedWildImport
from cing.Scripts.validateEntry import * #@UnusedWildImport
from cing.core.constants import * #@UnusedWildImport


def mainRefineEntry(entryId, *extraArgList):
    """inputDir may be a directory or a url. A url needs to start with http://.
    """

    fastestTest = 0 # DEFAULT: False
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
    force_redo = True
    force_retrieve_input = True


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
            nTerror("Got arguments: " + repr(extraArgList))
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
    # end if
    singleCoreOperation = getDeepByKeysOrAttributes(extraArgList, IDX_SINGLE_CORE_OPERATION )
    if singleCoreOperation:
        singleCoreOperation = int(singleCoreOperation)
    else:
        singleCoreOperation = 0 # Default should be True
    # end if
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
    nTdebug("modelCountAnneal:     %s" % modelCountAnneal)
    nTdebug("bestAnneal:           %s" % bestAnneal)
    nTdebug("best:                 %s" % best)
    nTdebug("isRemoteOutputDir:    %s" % isRemoteOutputDir)
    
    # For NMR_REDO required as most efficient.
    if singleCoreOperation: 
        setToSingleCoreOperation()
    # end if
    ip = get_local_ip_address()
    if ip:
        nTmessage('Found active IP address: %s' % ip)
    else:
        nTwarning('No IP address could be derived.')
    # end if

    # presume the directory still needs to be created.
    cingEntryDir = entryId + ".cing"

    if os.path.isdir(cingEntryDir):
        if force_redo:
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
        mkdirs(outputDir)
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
            if force_retrieve_input:
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
#        fullFileNameTgz = os.path.join(inputDir, fileNameTgz)
#        shutil.copy(fullFileNameTgz, '.')
        project = Project.open(entryId, status='old')
        if not project:
            nTerror("Failed to init old project")
            return True
    else:
        nTerror("Expected a CING project.")
        return True
        # end if
    # end if

####> MAIN UTILITY HERE
    if project.fullRedo(modelCountAnneal = modelCountAnneal, bestAnneal = bestAnneal, best = best):  
        nTerror("Failed fullAnnealAndRefine.")
        
        # Store the unfinished results
        # We don't need a time stamp because we are interested 
        # in the most recent unfinished (failed) run
        directoryNameCing = entryId + ".cing"
        startFileNameCing = directoryNameCing + ".tgz"
        unfTgzFileNameCing = directoryNameCing + ".unf.tgz"
        if not createTgz(unfTgzFileNameCing, directoryNameCing):
            # If the new tgz file was created, delete the old tgz and dir
            cleanCingTgzAndDir(startFileNameCing, directoryNameCing)
            # We send the new tgz file from a higher level (constants) # TODO: change?
        else: # do NOT remove old tgz nor dir
            pass
        # end if/else
        return True
          
    
    if ranges != None:
        project.molecule.setRanges(ranges)
    project.molecule.superpose(ranges=ranges)

    if 1: # DEFAULT 1?
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
        archive_id = ARCHIVE_NMR_REDO_ID
#        if isProduction:
#            archive_id = ARCHIVE_NRG_ID
        try:
            if doStoreCING2db( entryId, archive_id, project=project):
                nTerror("Failed to store CING project's data to DB but continuing.")
        except:
            nTtracebackError()
            nTerror("Failed to store CING project's data due to above traceback error.")

    if tgzCing:
        directoryNameCing = entryId + ".cing"
        tgzFileNameCing = directoryNameCing + ".tgz"
        if not createTgz(tgzFileNameCing, directoryNameCing):
            # If the tgz file was created, send it
            if isRemoteOutputDir:
                sendTgzAndClean(tgzFileNameCing, directoryNameCing, outputDir)
            else: # do NOT remove local copy
                pass
            # end if/else
        # end if
    # end if tgzCing
# end def

def createTgz(tgzName, dirName):
    if os.path.exists(tgzName):
        nTwarning("Overwriting: " + tgzName)
    # end if
    cmd = "tar -czf %s %s" % (tgzName, dirName)
    nTdebug("cmd: %s" % cmd)
#        do_cmd(cmd)
    status, result = commands.getstatusoutput(cmd)
    if status:
        nTerror("Failed to tar status: %s with result %s" % (status, result))
        return True
    # end if
#end def

def sendTgzAndClean(tgzName, dirName, sendDir):
    if putFileBySsh(tgzName, sendDir, ntriesMax = 2):
        nTerror("Failed to send File By Scp. Maintaining results")
        return True
    # end if
    cleanCingTgzAndDir(tgzName, dirName)
# end def

def cleanCingTgzAndDir(tgzName, dirName):
    nTmessage("Removing tgz result: %s" % tgzName)
    os.remove(tgzName)
    nTmessage("Removing cing dir itself: %s" % dirName)
    rmdir(dirName)
# end def

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
#        sys.exit(1) # can't be used in forkoff api
    try:
        status = mainRefineEntry(*sys.argv[1:])
    finally:
        nTmessage(getStopMessage(cing.starttime))
