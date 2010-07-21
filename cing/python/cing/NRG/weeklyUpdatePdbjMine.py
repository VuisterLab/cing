'''
Created on Jul 20, 2010

Should put all output in log file and not on sys.stdout/err.

Execute from cron like:
05 15 * * wed  (/opt/local/bin/python /Users/jd/workspace35/cingStable/python/cing/NRG/weeklyUpdatePdbjMine.py 2>&1)|mail -s rsyncPDB.log jd
python $CINGROOT/python/cing/NRG/weeklyUpdatePdbjMine.py

@author: jd
'''
from cing.Libs.DBMS import DBMS
from cing.Libs.NTutils import * #@UnusedWildImport

tmp_dir = '/Users/jd/tmpPdbj'

logFile = '/Users/jd/Library/Logs/weeklyUpdatePdbjMine.log'
psqlLogFile = 'psqlUpdate.latest.log'
psqlTmpCsvFile = 'psqlCmd.csv'
stream = open(logFile, 'a')
kwds = {'stream':stream, 'useDate':True, 'useProcessId':True}
log_message = PrintWrap(verbose=verbosityOutput, **kwds)
log_error = PrintWrap(verbose=verbosityError, prefix=prefixError, **kwds)
log_debug = PrintWrap(verbose=verbosityDebug, prefix=prefixDebug, **kwds)
log_message('Hello msg')
log_error('Hello error')
log_debug('Hello buggie')
NTmessage("Message to mail")
NTerror("Message to mail")
sys.exit(0)


def run():
    '''returns True on error'''

    os.chdir(tmp_dir)

    fn = os.path.join('pdbmlplus_weekly.latest.gz')
    if False:
        if os.path.exists(fn):
            log_message('Removing previous copy of %s' % fn)
            os.unlink(fn)
        fnUrl = os.path.join('ftp://ftp.pdbj.org/mine/weekly', fn)
    if False:
        log_message("Starting downloading weekly update")
#        wgetProgram = ExecuteProgram('wget --no-verbose %s' % fnUrl, redirectOutput=False)
        wgetProgram = ExecuteProgram('wget %s' % fnUrl, redirectOutput=False)
        exitCode = wgetProgram()
        if exitCode:
            log_error("Failed to download file %s" % fnUrl)
            return True

        if not os.path.exists(fn):
            log_error('Downloaded file %s not found' % fn)
            return True

        if not os.path.getsize(fn):
            log_error('Downloaded empty file %s' % fn)
            return True
        log_message("Downloaded %s" % fn)

    if False:
        log_message("Starting weekly update")
        command = 'gunzip < %s | psql pdbmlplus pdbj' % fn
        psqlProgram = ExecuteProgram(command, redirectOutputToFile=psqlLogFile)
        exitCode = psqlProgram()
        if exitCode:
            log_error("Failed to run psql program with command: [%s]" % command)
            return True
    if True:
        log_message("Getting overall number of entry count")
        if os.path.exists(psqlTmpCsvFile):
            log_debug('Removing previous copy of %s' % psqlTmpCsvFile)
            os.unlink(fn)

        # without semi-colon
        sqlSelectCmd = "select count(*) from pdbj.brief_summary"
        # without semi-colon
        sqlCopyCmd = "COPY (%s) TO STDOUT WITH CSV" % sqlSelectCmd
        command = "psql -h nmr --command='%s' pdbmlplus pdbj" % sqlCopyCmd
        log_debug("command: [%s]" % command)
        psqlProgram = ExecuteProgram(command, redirectOutputToFile=psqlTmpCsvFile)
        exitCode = psqlProgram()
        if exitCode:
            log_error("Failed to run psql program with command: [%s]" % command)
            return True
        if not os.path.exists( psqlTmpCsvFile ):
            log_error('Csv file %s not found' % psqlTmpCsvFile)
            return True
        if not os.path.getsize(psqlTmpCsvFile):
            log_error('Csv file %s is empty' % psqlTmpCsvFile)
            return True
        relationNames = [ psqlTmpCsvFile ]
        # Truncate the extensions
        relationNames = [ relationName[:-4] for relationName in relationNames]
        dbms = DBMS()
        if dbms.readCsvRelationList(relationNames):
            log_error("Failed to read relation: %s" % str(relationNames))
            return True
        entryCountTable = dbms.tables[relationNames[0]]
        entryCountList = entryCountTable.columnOrder[0]
        entryCount = entryCountList[0]
        NTmessage("Currently found %s number of entries in pdbmlplus" % entryCount)






    log_message("Ending weekly updates")

if __name__ == '__main__':
    if run():
        log_error("Failed to run weeklyUpdatePdbjMine")
        sys.exit(1)
