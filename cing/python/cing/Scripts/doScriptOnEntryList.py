"""
Validate set of entries given their input/output locations
and a file with a list of their names. 
"""
from cing.Libs.NTutils import NTmessage
from cing.Libs.forkoff import ForkOff
from cing.Libs.forkoff import do_cmd
import string

START_ENTRY_ID                 = 0 # default 0
MAX_ENTRIES_TODO               = 999999 # default a ridiculously large number like 999999

def doScriptOnEntryList(pythonScriptFileName, 
          entryListFileName, 
          startDir='.', 
          processes_max                  = 3,
          max_time_to_wait               = 600, 
          delay_between_submitting_jobs  = 1,
          extraArgList = None
          ):
#    if os.chdir(cingDirTestsTmp):
#        raise SetupError("Failed to change to directory for temporary test files: "+cingDirTestsTmp)

    # Empty list means no filtering done.
    entryCodeListFilter = []
#    entryCodeListFilter = string.split("1n62")
    
    entryListFile = file(entryListFileName, 'r')
    entryCodeList = []
    for line in entryListFile.readlines():
        entryCode = string.lower( line[0:4] )
        if entryCode in entryCodeListFilter:
            continue
        entryCodeList.append( entryCode )
    lastEntry = min(len(entryCodeList), START_ENTRY_ID+MAX_ENTRIES_TODO)
    entryCodeList = entryCodeList[START_ENTRY_ID:lastEntry]

    NTmessage('doing max %04d entries: %s' % (len(entryCodeList), entryCodeList ))  
    NTmessage('sub selection: max %04d entries: %s' % (len(entryCodeListFilter), entryCodeListFilter ))  
    
    job_list = []
    for entry_code in entryCodeList:
        extraArgListStr = string.join( extraArgList, ' ')
        cmd = 'cd %s; python -u %s %s %s > %s.log 2>&1 ' % ( startDir,
            pythonScriptFileName, 
            entry_code, 
            extraArgListStr,
            entry_code )
        job = ( do_cmd, (cmd,) )
        job_list.append( job )

    f = ForkOff( processes_max       = processes_max,
            max_time_to_wait    = max_time_to_wait) 
    done_entry_list = f.forkoff_start( job_list, delay_between_submitting_jobs )
    NTmessage("Finished following list: %s" % done_entry_list)
    