'''
Created on Jul 20, 2010

This script will put some output in the persisting log file ~/Library/Logs/weeklyUpdatePdbjMine.log

Execute from cron like:
05 15 * * wed  (/opt/local/bin/python /Users/jd/workspace35/cingStable/python/cing/NRG/weeklyUpdatePdbjMine.py 2>&1)|mail -s weeklyUpdatePdbjMine.log jd
/Users/jd/workspace35/cing/scripts/cing/CingWrapper.csh  --noProject --script /Users/jd/workspace35/cing/python/cing/NRG/weeklyUpdatePdbjMine.py

@author: jd
'''
from cing.Libs.DBMS import DBMS
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG import * #@UnusedWildImport

#stream = open(logFile, 'a')
#kwds = {'stream':stream, 'useDate':True, 'useProcessId':True, 'doubleToStandardStreams': True}
#log_message = PrintWrap(verbose=verbosityOutput, **kwds)
#log_error = PrintWrap(verbose=verbosityError, prefix=prefixError, **kwds)
#log_debug = PrintWrap(verbose=verbosityDebug, prefix=prefixDebug, **kwds)
#cing.verbosity = cing.verbosityDebug
#NTerrorT('Hello error')
#NTdebugT('Hello buggie')
#NTmessageT("Hello new teed message")
#sys.exit(0)


def run():
    '''returns True on error'''

    tmp_dir = '/Users/jd/tmpPdbj'
    psqlLogFile = 'psqlUpdate.latest.log'
    psqlTmpCsvFile = 'psqlCmd.csv'

    os.chdir(tmp_dir)
    logFile = '/Users/jd/Library/Logs/weeklyUpdatePdbjMine.log'
    if teeToFile(logFile):
        NTerror("Failed to start tea party to: %s" % logFile)
        sys.exit(1)

    NTmessageT("Starting $CINGROOT/python/cing/NRG/weeklyUpdatePdbjMine.py")

    fn = os.path.join('pdbmlplus_weekly.latest.gz')
    if False:
        if os.path.exists(fn):
            NTmessageT('Removing previous copy of %s' % fn)
            os.unlink(fn)
        NTmessageT("Starting downloading weekly update")
#        wgetProgram = ExecuteProgram('wget --no-verbose %s' % fnUrl, redirectOutput=False)
        fnUrl = os.path.join('ftp://ftp.pdbj.org/mine/weekly', fn)
        # if this is still too verbose try: --quiet
        wgetProgram = ExecuteProgram('wget --no-verbose %s' % fnUrl, redirectOutput=False)
        exitCode = wgetProgram()
        if exitCode:
            NTerrorT("Failed to download file %s" % fnUrl)
            return True

        if not os.path.exists(fn):
            NTerrorT('Downloaded file %s not found' % fn)
            return True

        if not os.path.getsize(fn):
            NTerrorT('Downloaded empty file %s' % fn)
            return True
        NTmessage("Downloaded %s" % fn)

    if False:
        # Absolutely needed to redirect to separate log file as these get very verbose when there are errors..
        command = 'gunzip < %s | psql pdbmlplus pdbj' % fn
        NTmessageT("Starting weekly update with [%s] and logging to: %s" % ( command, psqlLogFile ))
        psqlProgram = ExecuteProgram(command, redirectOutputToFile=psqlLogFile)
        exitCode = psqlProgram()
        if exitCode:
            NTerrorT("Failed to run psql program with command: [%s]" % command)
            return True
    if True:
        NTmessage("Getting overall number of entry count")

        if os.path.exists(psqlTmpCsvFile):
            NTdebug('Removing previous copy of %s' % psqlTmpCsvFile)
            os.unlink(psqlTmpCsvFile)

        # without semi-colon
        sqlSelectCmd = "select count(*) from pdbj.brief_summary"
        # without semi-colon
        sqlCopyCmd = "COPY (%s) TO STDOUT WITH CSV HEADER" % sqlSelectCmd
        command = "psql -h %s --command='%s' pdbmlplus pdbj" % ( PDBJ_DB_HOST, sqlCopyCmd)
        NTdebug("command: [%s]" % command)
        psqlProgram = ExecuteProgram(command, redirectOutputToFile=psqlTmpCsvFile)
        exitCode = psqlProgram()
        if exitCode:
            NTerrorT("Failed to run psql program with command: [%s]" % command)
            return True
        if not os.path.exists( psqlTmpCsvFile ):
            NTerror('Csv file %s not found' % psqlTmpCsvFile)
            return True
        if not os.path.getsize(psqlTmpCsvFile):
            NTerror('Csv file %s is empty' % psqlTmpCsvFile)
            return True
        relationNames = [ psqlTmpCsvFile ]
        # Truncate the .csv extensions
        relationNames = [ relationName[:-4] for relationName in relationNames]
        dbms = DBMS()
        if dbms.readCsvRelationList(relationNames):
            NTerror("Failed to read relation: %s" % str(relationNames))
            return True
        entryCountTable = dbms.tables[relationNames[0]]
#        NTdebug('\n'+str(entryCountTable))
        entryCountColumnName = entryCountTable.columnOrder[0]
        if entryCountColumnName != 'count':
            NTerrorT("Failed to find count column name from DB")
            return True
        entryCountList = entryCountTable.getColumnByIdx(0)
        entryCount = entryCountList[0]
        NTmessage("Currently found %s number of entries in pdbmlplus" % entryCount)

if __name__ == '__main__':
#    cing.verbosity = cing.verbosityDebug
    if run():
        NTerrorT("Failed to run weeklyUpdatePdbjMine")
        sys.exit(1)
    NTmessageT("Ending weeklyUpdatePdbjMine")

#sys.exit(1)
#from cing.Libs.DBMS import DBMS
#from cing.Libs.NTutils import * #@UnusedWildImport
#from cing.NRG import * #@UnusedWildImport
#cing.verbosity = cing.verbosityDebug
#
#tmp_dir = '/Users/jd/tmpPdbj'
#psqlTmpCsvFile = 'psqlCmd.csv'
#
#os.chdir(tmp_dir)
#
#dbms = DBMS()
#relationNames = [ psqlTmpCsvFile ]
#relationNames = [ relationName[:-4] for relationName in relationNames]
