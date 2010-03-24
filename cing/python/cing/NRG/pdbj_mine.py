'''
Run like:
python $CINGROOT/python/cing/NRG/pdbj_mine.py $CINGROOT/python/cing/NRG/sql/tmp.sql
'''
from cing.Libs.NTutils import writeTextToFile
import csv
import sys
import urllib

STACKTRACE_LENGHT_MIN = 1000
'Number of characters to constitute a stacktrace'
STACKTRACE_COMPONENT = 'at mine.SqlServlet.doPost'
'Mandatory part of stacktrace used to id it.'


def postQuery(sql_query, saveCsvFile = None, base_url='http://service.pdbj.org/mine/sql'):
    """Return a table or None on error."""
    post_parameter = urllib.urlencode({'format':'csv' , 'q':sql_query})
    # generate access query
    connection = urllib.urlopen(base_url, post_parameter)
    if not connection:
        print "ERROR: Failed to connect to PDBj Mine"
        return
    resultTxt = connection.read()
    if not resultTxt:
        print "ERROR: Failed to get any result back from PDBj Mine"
        return
    if len(resultTxt) > STACKTRACE_LENGHT_MIN:
        # cheap scan.
        if resultTxt.count(STACKTRACE_COMPONENT, 0, STACKTRACE_LENGHT_MIN):
            print "ERROR: Found stack trace:"
            print resultTxt
            return
    if saveCsvFile:
        writeTextToFile( saveCsvFile, resultTxt)
    # parse as CSV
    result = []
#    print "Found resultTxt: %s" % resultTxt
    # Use a trick to read from txt now. Trick is to offer an array of lines that will be split.
    resultTxtList = resultTxt.splitlines()
    csvReader = csv.reader(resultTxtList, delimiter=',', quotechar='"')
    total = 0
    isHeader = True
    for row in csvReader:
        result.append(row)
        if not isHeader:
            total += int(row[1])
        isHeader = False
    # show result
    print "DEBUG: Found result: %s" % result
    print "DEBUG: Found total: %s" % total
    return result

if __name__ == '__main__':
    sql_query = open(sys.argv[1], 'r').read()
#    print 'sql_query: %s' % sql_query
    postQuery(sql_query,saveCsvFile='result.csv')
