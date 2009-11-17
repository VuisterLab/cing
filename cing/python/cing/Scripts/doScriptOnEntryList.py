"""
Run script on set of entries given their input/output locations
and a file with a list of their names.
"""
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import getDateTimeStampForFileName
from cing.Libs.forkoff import ForkOff
from cing.Libs.forkoff import do_cmd
from cing.Libs.NTutils import NTpath
import os

"""
NB
- Doing procheck on MacOSX.5.3/MacBook Pro best performance is
for when using 3 processes.
"""
START_ENTRY_ID                 = 0 # default 0
MAX_ENTRIES_TODO               = 999 # default a ridiculously large number like 999999

def mkSubDirStructure(startDir, entryCodeList, pythonScriptFileNameRoot):
    for entry_code in entryCodeList:
        entryCodeChar2and3 = entry_code[1:3]
        dataDir = os.path.join( startDir, 'data' )
        if not os.path.exists(dataDir):
            NTmessage("Creating dir: " + dataDir)
            os.mkdir(dataDir)
        subDir = os.path.join( dataDir, entryCodeChar2and3 )
        if not os.path.exists(subDir):
            NTmessage("Creating dir: " + subDir)
            os.mkdir(subDir)
        entryDir = os.path.join( subDir, entry_code )
        if not os.path.exists(entryDir):
            NTmessage("Creating dir: " + entryDir)
            os.mkdir(entryDir)
        logDir = os.path.join( entryDir, 'log_'+pythonScriptFileNameRoot )
        if not os.path.exists(logDir):
            NTmessage("Creating dir: " + logDir)
            os.mkdir(logDir)

def doScriptOnEntryList(pythonScriptFileName,
          entryListFileName,
          startDir                       ='.',
          processes_max                  = 3,   # default 3
          max_time_to_wait               = 600,
          delay_between_submitting_jobs  = 1,
          extraArgList                   = None,
          START_ENTRY_ID                 = START_ENTRY_ID,
          MAX_ENTRIES_TODO               = MAX_ENTRIES_TODO,
          expectPdbEntryList             = True
          ):
    """Return True on error"""
#    if os.chdir(cingDirTmp):
#        raise SetupError("Failed to change to directory for temporary test files: "+cingDirTmp)

    # Empty list means no filtering done.
    entryCodeListFilter = []
#    entryCodeListFilter = string.split("1n62")

    entryListFile = file(entryListFileName, 'r')
    entryCodeList = []
    chainCodeList = []
    entryCountTotal = 0
    for line in entryListFile.readlines():
        line = line.strip()
        entryCountTotal += 1
        if expectPdbEntryList:
            entryCode = line[0:4].lower()
        else:
            entryCode = line
        if entryCode in entryCodeListFilter:
            continue
        entryCodeList.append( entryCode )
        # get it only when present or ignore it. Watch for number of arguments changes.
        # the python script will only see entry_code and extraArgListStr
        chainCode = ''
        if expectPdbEntryList:
            if len(line) > 4:
                chainCode = line[4].upper()
#        NTdebug('Using chainCode: [%s]' % chainCode )
        chainCodeList.append(chainCode)
    entryListFile.close()

    entryCountSelected = len( entryCodeList )
    # lastEntryId is id of last entry excluding the entry itself.
    lastEntryId = min(len(entryCodeList), START_ENTRY_ID+MAX_ENTRIES_TODO)
    entryCodeList = entryCodeList[START_ENTRY_ID:lastEntryId]
    chainCodeList = chainCodeList[START_ENTRY_ID:lastEntryId]

    NTmessage('Read      %04d entries    ' % entryCountTotal)
    NTmessage('Selected  %04d entries    ' % entryCountSelected)
    NTmessage('Sliced    %04d entries: %s' % (len(entryCodeList), entryCodeList ))


    (_directory, pythonScriptFileNameRoot, _ext) = NTpath(pythonScriptFileName)
    mkSubDirStructure( startDir, entryCodeList, pythonScriptFileNameRoot )
    logScriptFileNameRoot = 'log_'+pythonScriptFileNameRoot
    job_list = []
    i = 0
    for entry_code in entryCodeList:
        extraArgListStr = ''
        if extraArgList:
            extraArgListStr = ' '.join( extraArgList )
        chain_code = chainCodeList[i]

        entryCodeChar2and3 = entry_code[1:3]
        entryDir = os.path.join( startDir, 'data', entryCodeChar2and3, entry_code )

        date_stamp = getDateTimeStampForFileName()
        cmd = 'cd %s; python -u %s %s %s %s > %s/%s_%s%s.log 2>&1 ' % (
            entryDir,
            pythonScriptFileName,
            entry_code,
            chain_code,
            extraArgListStr,
            logScriptFileNameRoot,
            entry_code,
            chain_code,
            date_stamp
             )
        job = ( do_cmd, (cmd,) )
        job_list.append( job )
        i += 1

    f = ForkOff( processes_max       = processes_max,
            max_time_to_wait    = max_time_to_wait)
    done_entry_list = f.forkoff_start( job_list, delay_between_submitting_jobs )
    done_entry_list.sort()
    not_done_entry_list = range(len(job_list))
    for id in done_entry_list:
        idx = not_done_entry_list.index(id)
        if idx >= 0:
            del(not_done_entry_list[idx])
    NTmessage("Finished list  : %s" % done_entry_list)
    NTmessage("Unfinished list: %s" % not_done_entry_list)
    for id in not_done_entry_list:
        job = job_list[id]
        _do_cmd, cmdTuple = job
        cmd = cmdTuple[0]
        NTerror("Failed forked: %s" % cmd)