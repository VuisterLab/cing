"""
Run script on set of entries given their input/output locations
and a file with a list of their names.
"""
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.forkoff import ForkOff
from cing.Libs.forkoff import do_cmd
from random import shuffle

# Doing procheck on MacOSX.5.3/MacBook Pro best performance is
# for when using 3 processes.

start_entry_id                 = 0 # default 0
max_entries_todo               = 999 # default a ridiculously large number like 999999

def mkSubDirStructure(startDir, entryCodeList, pythonScriptFileNameRoot):
    for entry_code in entryCodeList:
        entryCodeChar2and3 = entry_code[1:3]
        dataDir = os.path.join( startDir, DATA_STR )
        if not os.path.exists(dataDir):
#            nTmessage("Creating dir: " + dataDir)
            os.mkdir(dataDir)
        subDir = os.path.join( dataDir, entryCodeChar2and3 )
        if not os.path.exists(subDir):
#            nTmessage("Creating dir: " + subDir)
            os.mkdir(subDir)
        entryDir = os.path.join( subDir, entry_code )
        if not os.path.exists(entryDir):
#            nTmessage("Creating dir: " + entryDir)
            os.mkdir(entryDir)
        logDir = os.path.join( entryDir, 'log_'+pythonScriptFileNameRoot )
        if not os.path.exists(logDir):
#            nTmessage("Creating dir: " + logDir)
            os.mkdir(logDir)

def doScriptOnEntryList(pythonScriptFileName,
          entryListFileName,
          startDir                       ='.',
          processes_max                  = 3,   # default 3
          max_time_to_wait               = 600,
          delay_between_submitting_jobs  = 1,
          extraArgList                   = None,
          start_entry_id                 = start_entry_id,
          max_entries_todo               = max_entries_todo,
          expectPdbEntryList             = True,
          shuffleBeforeSelecting         = False # fails for chain ids when included.
          ):
    """Return True on error"""
    
    if 1: # DEFAULT: False
        nTdebug("entryListFileName            : %s" % entryListFileName)        
        nTdebug("startDir                     : %s" % startDir                     )        
        nTdebug("processes_max                : %s" % processes_max                )        
        nTdebug("max_time_to_wait             : %s" % max_time_to_wait             )        
        nTdebug("delay_between_submitting_jobs: %s" % delay_between_submitting_jobs)        
        nTdebug("extraArgList                 : %s" % str(extraArgList            ))        
        nTdebug("start_entry_id               : %s" % start_entry_id               )        
        nTdebug("max_entries_todo             : %s" % max_entries_todo             )        
        nTdebug("expectPdbEntryList           : %s" % expectPdbEntryList           )        
        nTdebug("shuffleBeforeSelecting       : %s" % shuffleBeforeSelecting       )
    # end if        
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
        if line == '': # skip empty lines.
            continue
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
#        nTdebug('Using chainCode: [%s]' % chainCode )
        chainCodeList.append(chainCode)
    entryListFile.close()

    entryCountSelected = len( entryCodeList )
    # lastEntryId is id of last entry excluding the entry itself.
    lastEntryId = min(len(entryCodeList), start_entry_id+max_entries_todo)    
    if shuffleBeforeSelecting:
        nTmessage("Shuffling entry list before selecting entries.")
        entryCodeListCopy = entryCodeList[:]
        shuffle(entryCodeListCopy)
        entryCodeList = entryCodeListCopy[start_entry_id:lastEntryId] # no sense in starting at zero here; they're random.
    else:
        entryCodeList = entryCodeList[start_entry_id:lastEntryId] # no sense in starting at zero here; they're random.
    entryCodeList.sort()
    chainCodeList = chainCodeList[start_entry_id:lastEntryId]

    nTmessage('Read      %05d entries    ' % entryCountTotal)
    nTmessage('Selected  %05d entries    ' % entryCountSelected)
    nTmessage('Sliced    %05d entries: %s' % (len(entryCodeList), entryCodeList ))
#    nTmessage('Sliced    %05d chains:  %s' % (len(chainCodeList), chainCodeList ))


    useAnyCmd = False
    if pythonScriptFileName.endswith('.py'):
        (_directory, pythonScriptFileNameRoot, _ext) = nTpath(pythonScriptFileName)
    else:
        useAnyCmd = True
        pythonScriptFileNameRoot = pythonScriptFileName.split()[0] # get first word of eg.
        if pythonScriptFileNameRoot.count('/'):
            pythonScriptFileNameRoot = pythonScriptFileNameRoot.split('/')[-1]
        if pythonScriptFileNameRoot.count('.'):
            pythonScriptFileNameRoot = pythonScriptFileNameRoot.split('.')[0]
        # 'cing -v 9 -n $x --initPDB $PDB/pdb$x.ent.gz --validateFastest --ranges cv')
    mkSubDirStructure( startDir, entryCodeList, pythonScriptFileNameRoot )
    logScriptFileNameRoot = 'log_'+pythonScriptFileNameRoot
    job_list = []
    for i, entry_code in enumerate(entryCodeList):
        extraArgListStr = ''
        if extraArgList:
            extraArgListStr = ' '.join( extraArgList )
        chain_code = chainCodeList[i]

        entryCodeChar2and3 = entry_code[1:3]
        entryDir = os.path.join( startDir, DATA_STR, entryCodeChar2and3, entry_code )

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
        if useAnyCmd:
            cmdBase = pythonScriptFileName
            cmdBase = cmdBase.replace("$x", entry_code)
            cmdBase = cmdBase.replace("$c", chain_code)
            cmd = 'cd %s; %s %s %s > %s/%s_%s%s.log 2>&1 ' % (
                entryDir,
                cmdBase,
                entry_code,
                chain_code,
                logScriptFileNameRoot,
                entry_code,
                chain_code,
                date_stamp
                 )
        job = ( do_cmd, (cmd,) )
#        nTdebug("Will schedule job cmd: %s" % cmd)
        job_list.append( job )

    f = ForkOff( processes_max       = processes_max, max_time_to_wait    = max_time_to_wait)
    done_entry_list = f.forkoff_start( job_list, delay_between_submitting_jobs )
    done_entry_list.sort()
    not_done_entry_list = range(len(job_list))
    for id in done_entry_list:
        idx = not_done_entry_list.index(id)
        if idx >= 0:
            del(not_done_entry_list[idx])
    nTmessage("In doScriptOnEntryList Finished list  : %s" % done_entry_list)
    nTmessage("In doScriptOnEntryList Unfinished list: %s" % not_done_entry_list)
    for id in not_done_entry_list:
        job = job_list[id]
        _do_cmd, cmdTuple = job
        cmd = cmdTuple[0]
        nTerror("In doScriptOnEntryList failed forked: %s" % cmd)

if __name__ == '__main__':
    entryCodeList = '1brv 1bus'.split()
