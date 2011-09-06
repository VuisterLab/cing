'''
Created on Jul 20, 2010

This script will put some output in the persisting log file ~/Library/Logs/weeklyUpdatePdbjMine.log

Execute from cron like (pay attention to correct CINGROOT translation on nmr it is cingStable when testing):
05 15 * * wed  (/Users/jd/workspace35/cing/scripts/cing/CingWrapper.csh  --noProject --script 
    /Users/jd/workspace35/cing/python/cing/NRG/weeklyUpdatePdbjMine.py 2>&1)|mail -s weeklyUpdatePdbjMine.log jd

Or from command line like:
$CINGROOT/scripts/cing/CingWrapper.csh  --noProject --script $CINGROOT/python/cing/NRG/weeklyUpdatePdbjMine.py

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
#nTerrorT('Hello error')
#nTdebugT('Hello buggie')
#nTmessageT("Hello new teed message")
#sys.exit(0)


def run():
    '''returns True on error'''

    tmp_dir = '/Users/jd/tmpPdbj'
    psqlLogFile = 'psqlUpdate.latest.log'
    psqlTmpCsvFile = 'psqlCmd.csv'

    os.chdir(tmp_dir)
    logFile = '/Users/jd/Library/Logs/weeklyUpdatePdbjMine.log'
    if teeToFile(logFile):
        nTerror("Failed to start tea party to: %s" % logFile)
        sys.exit(1)

    nTmessageT("Starting $CINGROOT/python/cing/NRG/weeklyUpdatePdbjMine.py")

    fn = 'pdbmlplus_weekly.latest.gz'
    if True:
        if os.path.exists(fn):
            nTmessageT('Removing previous copy of %s' % fn)
            os.unlink(fn)
        nTmessageT("Starting downloading weekly update")
#        wgetProgram = ExecuteProgram('wget --no-verbose %s' % fnUrl, redirectOutput=False)
        fnUrl = os.path.join('ftp://ftp.pdbj.org/mine/weekly', fn)
        # if this is still too verbose try: --quiet
        wgetProgram = ExecuteProgram('wget --no-verbose %s' % fnUrl, redirectOutput=False)
        exitCode = wgetProgram()
        if exitCode:
            nTerrorT("Failed to download file %s" % fnUrl)
            return True

        if not os.path.exists(fn):
            nTerrorT('Downloaded file %s not found' % fn)
            return True

        if not os.path.getsize(fn):
            nTerrorT('Downloaded empty file %s' % fn)
            return True
        nTmessage("Downloaded %s" % fn)

    if True:
        # Absolutely needed to redirect to separate log file as these get very verbose when there are errors..
        command = 'gunzip < %s | psql pdbmlplus pdbj' % fn
        nTmessageT("Starting weekly update with [%s] and logging to: %s" % ( command, psqlLogFile ))
        psqlProgram = ExecuteProgram(command, redirectOutputToFile=psqlLogFile)
        exitCode = psqlProgram()
        if exitCode:
            nTerrorT("Failed to run psql program with command: [%s]" % command)
            return True
    if True:
        nTmessage("Getting overall number of entry count")

        if os.path.exists(psqlTmpCsvFile):
            nTdebug('Removing previous copy of %s' % psqlTmpCsvFile)
            os.unlink(psqlTmpCsvFile)

        # without semi-colon
        sqlSelectCmd = "select count(*) from pdbj.brief_summary"
        # without semi-colon
        sqlCopyCmd = "COPY (%s) TO STDOUT WITH CSV HEADER" % sqlSelectCmd
        command = "psql -h %s --command='%s' pdbmlplus pdbj" % ( PDBJ_DB_HOST, sqlCopyCmd)
        nTdebug("command: [%s]" % command)
        psqlProgram = ExecuteProgram(command, redirectOutputToFile=psqlTmpCsvFile)
        exitCode = psqlProgram()
        if exitCode:
            nTerrorT("Failed to run psql program with command: [%s]" % command)
            return True
        if not os.path.exists( psqlTmpCsvFile ):
            nTerror('Csv file %s not found' % psqlTmpCsvFile)
            return True
        if not os.path.getsize(psqlTmpCsvFile):
            nTerror('Csv file %s is empty' % psqlTmpCsvFile)
            return True
        relationNames = [ psqlTmpCsvFile ]
        # Truncate the .csv extensions
        relationNames = [ relationName[:-4] for relationName in relationNames]
        dbms = DBMS()
        if dbms.readCsvRelationList(relationNames):
            nTerror("Failed to read relation: %s" % str(relationNames))
            return True
        entryCountTable = dbms.tables[relationNames[0]]
#        nTdebug('\n'+str(entryCountTable))
        entryCountColumnName = entryCountTable.columnOrder[0]
        if entryCountColumnName != 'count':
            nTerrorT("Failed to find count column name from DB")
            return True
        entryCountList = entryCountTable.getColumnByIdx(0)
        entryCount = entryCountList[0]
        nTmessage("Currently found %s number of entries in pdbmlplus" % entryCount)

if __name__ == '__main__':
#    cing.verbosity = cing.verbosityDebug
    if run():
        nTerrorT("Failed to run weeklyUpdatePdbjMine")
        sys.exit(1)
    nTmessageT("Ending weeklyUpdatePdbjMine")

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
