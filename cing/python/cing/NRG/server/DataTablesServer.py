#!/opt/local/bin/python -u

# Script:    DataTables server-side script for Python and Python
# Copyright: 2010 - Allan Jardine
# License:   GPL v2 or BSD (3-point)
# No big modules here please.
from psycopg2.extras import DictCursor
from traceback import format_exc
import cgi
import psycopg2
import re
import string
import sys
import time
# CGI header
log = sys.stderr.write
#log('Hello CGI\n')
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# Array of database columns which should be read and sent back to DataTables
PDB_ID_IDX = 2 # Keep in sync with settings.py where it serves no purpose but to remind us of order importance.
# Indexed column (used for fast and accurate table cardinality)
#_indexColumn = "pdb_id"
_columns = 'is_solid name pdb_id bmrb_id rog_str distance_count cs_count chothia_class_str chain_count res_count'.split()
_boolean_columns = 'is_solid'.split() # can be simply filtered for.
_string_columns = 'name pdb_id rog_str chothia_class_str'.split() # can be simply filtered for.
# DB table to use
_sTable = "nrgcing.cingentry"
#schema= NRG_DB_SCHEMA  
conn_string = "host='localhost' dbname='pdbmlplus' user='nrgcing1' password='4I4KMS'"
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# If you just want to use the basic configuration for DataTables with PHP server-side, there is
# no need to edit below this line
#
def toCsv(inObject):
    'Return None on empty or invalid inObject.'
    if not inObject:
        return None
    result = ','.join(_columns[2:]) + '\n' # Header row
    for r in range(len(inObject)):
        rowStr = ''
        row = inObject[r]
        for c in range(2,len(row)):            
            v = row[c]
            if isinstance(v, str): # Strings are usually quoted.
                v = '"%s"' % v
            # end if                      
            if v == None: # Nulls are empty unquoted values.
                v = ''
            # end if
            rowStr += str(v) + ','
        # end for        
        result += "%s\n" % rowStr[:-1]
    return result
# end def


def is_pdb_code( chk_string ):
    """
    This function checks to see if the string is a reasonable candidate for a pdb entry code.
    """
    pattern = re.compile( '^\d\w\w\w$' )
    return pattern.match( chk_string )
# end def

htmlHead = """
<head>
<meta name="Author" content="Jurgen F. Doreleijers, CMBI">
<title>NRG-CING</title>
<link media="screen" href="../../NRG-CING/HTML/cing.css" type="text/css" rel="stylesheet"/>
<!-- INSERT ADDITIONAL HEAD STRING HERE -->
</head>
"""

htmlBody = """<body>
<div id="container">
<div id="header">
    <H1>NRG-CING</H1>
    <a href="../NRG-CING/HTML/index.html#_top" title="goto home page">Home</a>
    <A HREF="../NRG-CING/HTML/about.html" title="goto page with help about the NRG-CING front page">About</A>
    <A HREF="../NRG-CING/HTML/credits.html" title="goto page with credits">Credits</A>
    <A HREF="../NRG-CING/HTML/more.html" title="goto page with more resources">More</A>
    <a href="../NRG-CING/HTML/contact.html" title="goto page with contact information">Contact</a>
    <A HREF="../NRG-CING/HTML/help.html" title="goto page with help">Help</A>    
<!-- end header --> </div>        
<div id="main">        
<!-- INSERT MAIN HERE -->
<!-- end main --></div>
<br style="clear: both;"/>
<div id="footer">
<p>Generated on:&nbsp;<!-- INSERT NEW DATE HERE --></p>
<!-- end footer --></div>
<!-- end container --></div>
<!-- INSERT GOOGLE ANALYTICS TEMPLATE HERE -->
</body>
</html>        
        """        

# It's inserted only into the top level index.html; one per cing report.
GOOGLE_ANALYTICS_TEMPLATE = """
<!-- The script below will anonymously report usage data to Google Analytics by any javascript enabled browser. -->
<script type="text/javascript">
var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
</script>
<script type="text/javascript">
try {
var pageTracker = _gat._getTracker("UA-4413187-1");
pageTracker._trackPageview();
} catch(err) {}</script>
"""
old_string = r"<!-- INSERT GOOGLE ANALYTICS TEMPLATE HERE -->"
htmlBody = string.replace(htmlBody, old_string, GOOGLE_ANALYTICS_TEMPLATE)                        
old_string = r"<!-- INSERT NEW DATE HERE -->"
new_string = time.asctime()
htmlBody = string.replace(htmlBody, old_string, new_string)                        


class DataTablesServer:
    def __init__( self ):
        self.cgi = cgi.FieldStorage()
        try:
            self.dbh = psycopg2.connect(conn_string)            
            if 0: # Default: False
                print "Content-Type: text/plain\n"
                # conn.cursor will return a cursor object, you can use this query to perform queries
                # note that in this example we pass a cursor_factory argument that will
                # dictionary cursor so COLUMNS will be returned as a dictionary so we
                # can access columns by their name instead of index.
                cursor = self.dbh.cursor(cursor_factory=DictCursor)                
                # Then we get the work memory we just set -> we know we only want the
                # first ROW so we call fetchone.
                # then we use bracket access to get the FIRST value.
                # Note that even though we've returned the columns by name we can still
                # access columns by numeric index as well - which is really nice.
                cursor.execute('SHOW work_mem')
                # Call fetchone - which will fetch the first row returned from the database.
                memory = cursor.fetchone()
                # access the column by numeric index:
                # even though we enabled columns by name I'm showing you this to
                # show that you can still access columns by index and iterate over them.
                print "Value: ", memory[0]
#    #             print the entire row 
                print "Row:    ", memory
#                return
            # end if            
        except:
            traceBackString = format_exc()
            if traceBackString == None:
                traceBackString = 'No traceback error string available.'
            print traceBackString
            return
        # end try
        self.resultData = None
        self.cadinalityFiltered = 0
        self.cadinality = 0
        # Who's calling
        if self.cgi.has_key('database'):
            log( "Processing textbox query.\n" )
            self.processSimpleTextBoxQuery()
            return
        # end if         
#        log( "cgi: %s\n" % str(self.cgi) )
                                          
        
        if self.cgi.has_key('query_type') and self.cgi['query_type'].value == "normal":
            print "Content-Type: text/plain\n"
            log( "Processing normal query.\n" )
            self.runQueries(usePaging=True)
            self.outputResult()
        else:
            print "Content-Disposition: attachment; filename=NRG-CING_summary_selection.csv;\n"
            log( "Processing download query.\n" )
#            self.cgi['iDisplayLength'] = -1 # All filtered rows please
            self.runQueries(usePaging=False)
#            log( "self.resultData: %s\n" % str(self.resultData) )
            print toCsv( self.resultData )            
            return
        # end def            
    # end def
    
    def processSimpleTextBoxQuery( self ):
        '''
        Redirect any which way the input.
        '''
        print "Content-Type: text/html\n"
        basicRedirectHtml = """<html><META HTTP-EQUIV="Refresh"
              CONTENT="0; URL=%s">
              </html>
        """
        invalidPdbHtmlMain = """    
        <H3>Invalid PDB entry code?</H3>
        <p>You provided for the PDB identifier the string value: [<font color="red">%s</font>]. </p>
        <p>
        This seems to be an invalid PDB entry code. A valid PDB identifier consist of four characters with the
        first character being a digit and the remaining three character any alphanumeric character.
        Case is not important for this matter. E.g. 9pcy is a valid PDB identifier.
        </P>
        <p>Please go back and try again.</P>
        """   
        absentPdbHtmlMain = """    
        <H3>Missing NRG-CING entry</H3>
        <p>This entry [<font color="red">%(pdb_id)s</font>] is not in NRG-CING.</p>
        <p>
        Consider checking the WHY_NOT site for this PDB identifier:
        <A HREF="http://www.cmbi.ru.nl/WHY_NOT2/search/pdbid/%(pdb_id)s"> %(pdb_id)s</a>
        to find out why it is not (yet) present in NRG-CING and other databases perhaps.
        </p>
        <p>        
        Or look at the 
        PDBREPORT validation report for:
        <A HREF="http://www.cmbi.ru.nl/pdbreport/cgi-bin/nonotes?PDBID=%(pdb_id)s">%(pdb_id)s</a>
        which will exist even if this is a valid PDB identifier of an entry solved by X-ray crystallography.        
        </P>
        <p>Alternatively, you may go back and try again.</P>
        """   
             
#        print 'DEBUG: now in processSimpleTextBoxQuery'
        # Sanity check.        
        dbValue = self.cgi['database'].value
        if dbValue != 'pdb':
            log("ERROR: got a cgi database parameter but the value was not pdb but: %s\n" % str(dbValue))
            print basicRedirectHtml % '../../NRG-CING/HTML/index.html'
            return
        # end def
        pdb_id = ''
        if self.cgi.has_key('id'): # the id might not even exist if the submitted value was empty.            
            pdb_id = self.cgi['id'].value
        if not is_pdb_code(pdb_id):
            file_content = htmlHead + '\n' + htmlBody
            old_string = r"<!-- INSERT MAIN HERE -->"
            new_string = invalidPdbHtmlMain % pdb_id
            file_content = string.replace(file_content, old_string, new_string )
            print file_content
            return
        # end def
        pdb_id = pdb_id.lower()
        if not self.isPresentInDb(pdb_id):
            file_content = htmlHead + '\n' + htmlBody
            old_string = r"<!-- INSERT MAIN HERE -->"
            new_string = absentPdbHtmlMain % { "pdb_id": pdb_id }
            file_content = string.replace(file_content, old_string, new_string )
            print file_content
            return
        # end def
        # All well here.
        ch23 = pdb_id[1:3]
        # Superfast redirect without inbetween page.
        refTag = "../../NRG-CING/data/" + ch23 + "/"+pdb_id+"/"+pdb_id+".cing/" + pdb_id + "/HTML/index.html"
        print basicRedirectHtml % refTag
        return
    # end def
        
    
    def outputResult( self ):
        'Output the JSON required for DataTables'
        output = '{'
        output += '"sEcho": '+str(int(self.cgi['sEcho'].value))+', '
        output += '"iTotalRecords": '+str(self.cardinality)+', '
        output += '"iTotalDisplayRecords": '+str(self.cadinalityFiltered)+', '
        output += '"aaData": [ '
        
        mapRog = {'green':  '<font color=#000000>green</font>', 
                  'orange': '<font color=#FFA500>orange</font>', 
                  'red':    '<font color=#FF0000>red</font>',
                  '': 'n.d.'
                  }
        refEndTag = "</a>"                    
        for r,row in enumerate(self.resultData): #@UnusedVariable # pylint: disable=W0612
#            log("Looking at row: %s.\n" % str(row))
            output += '['
            for i in range( len(_columns) ):
                columnName = _columns[i]
                v = str( row[ _columns[i] ] )
                if v == 'None':
#                    log("Resetting None string to empty string\n")
                    v = ''
                # end if                    
                if columnName == "name" or columnName == "pdb_id" or i == 0:
                    if len(v) != 4: # for when we are at row 0: is_solid. We need to actually look in column 1.
#                        log("DEBUG: getting thru PDB id from different column number 1.\n")
#                        log("WARNING: Strange got bad length for expected pdb id: [%s]\n" % str(dbId))
                        v = str( row[ _columns[PDB_ID_IDX] ] ) # 1 is pdb_id
#                        log("DEBUG: XXXX.\n")
                        if v == None:
                            log("ERROR: got actual None for value.\n")
                            output += '"%s",' % '.'
                            continue
                        # end if                         
                        if len(v) != 4:
                            log("ERROR: Strange got no pdb_id string in column: [%s] but [%s]\n" % (columnName,str(v)))
                            output += '"%s",' % ''
                            continue
                        # end if                                                 
                    # end if                         
                    dbId = v
                    ch23 = dbId[1:3]
                    refTag = "<a href='" + "../data/" + ch23 + "/"+dbId+"/"+dbId+".cing" + "'>" 
                    if columnName == "name":
#                        http://localhost/NRG-CING/data/br/1brv/1brv.cing/1brv/HTML/mol.gif
                        imgTag = "<img src='" + "../data/" + ch23 + "/"+dbId+"/"+dbId+".cing/"+dbId+\
                                    "/HTML/mol_pin.gif' width=57 height=40 border=0>"
                        v = refTag + imgTag + refEndTag
                    elif columnName == "pdb_id":
#                        http://www.rcsb.org/pdb/explore/explore.do?structureId=1brv
                        refTag = "<a href='" + "http://www.rcsb.org/pdb/explore/explore.do?structureId=" + dbId + "'>"
                        v = refTag + dbId + refEndTag
                    elif i ==0: # is_solid, an alias for download url.
#                        http://nmr.cmbi.ru.nl/NRG-CING/data/br/1brv/1brv.cing.tgz                    
                        refTag = "<a href='" + "../data/" + ch23 + "/"+dbId+"/"+dbId+".cing.tgz" + "'>" 
#                        http://localhost/NRG-CING/data/br/1brv/1brv.cing/1brv/HTML/mol.gif
                        imgTag = "<img src='icon_download.gif' width=34 height=34 border=0>"
                        v = refTag + imgTag + refEndTag
                    else: # is_solid, an alias for download url.
                        log("ERROR: code bug. Please revise loop here.\n")
                    # end def
                    output += '"%s",' % v
                    continue
                # end def
                if columnName == "bmrb_id":
                    dbId = v
#                    http://www.bmrb.wisc.edu/data_library/generate_summary.php?bmrbId=4020           
                    refTag = "<a href='" + "http://www.bmrb.wisc.edu/data_library/generate_summary.php?bmrbId=" + dbId + "'>"
                    v = refTag + dbId + refEndTag
                elif _columns[i] == "rog_str":
                    v = mapRog[ v ]
                # end if
                output += '"%s",' % v
#                log("DEBUG: Logging value: [%s]\n" % v)                
            # end for            
#            log("DEBUG: Logged row: %s\n" % r)                
            # Optional Configuration:
            # If you need to add any extra columns (add/edit/delete etc) to the table, that aren't in the
            # database - you can do it here
            output = output[:-1]
            output += '],'
        # end for
        output = output[:-1]
        output += '] }'        
        print output
    # end def
        
    def isPresentInDb( self, dbValue ):
        'Check for existence in RDB.'
        dataCursor = self.dbh.cursor(cursor_factory=DictCursor)
        query = """SELECT count(*) FROM %s where pdb_id='%s'""" % (
                _sTable, dbValue )
#        print 'query: %s' % query
        dataCursor.execute( query )
        count = dataCursor.fetchone()[0]
        return count > 0
    # end def
    
    def runQueries( self, usePaging = True ):
        'Generate the SQL needed and run the queries'
        dataCursor = self.dbh.cursor(cursor_factory=DictCursor)
        where=self.filtering()
        order=self.ordering()
        limit = ''
        if usePaging:
#            log("Paging\n")
            limit=self.paging()
#        print 'where: %s' % where
#        print 'order: %s' % order
#        print 'limit: %s' % limit
#        SELECT SQL_CALC_FOUND_ROWS %(columns)s
        query = """
            SELECT %(columns)s
            FROM   %(table)s %(where)s %(order)s %(limit)s""" % dict(
                columns=', '.join(_columns), table=_sTable, 
                where=where, order=order, limit=limit
            )
#        print 'query: %s' % query
        dataCursor.execute( query )
        self.resultData = dataCursor.fetchall()
#        print 'Debug: resultData length: %s' % len(self.resultData)
        
        cadinalityFilteredCursor = self.dbh.cursor() # Extra real query needed in pgsql w.r.t. postgresql.
        cadinalityFilteredCursor.execute( """
            SELECT count(*)
            FROM   %(table)s %(where)s""" % dict(
                columns=', '.join(_columns), table=_sTable, 
                where=where
        ) )
        self.cadinalityFiltered = cadinalityFilteredCursor.fetchone()[0]
#        print 'Debug: cadinalityFiltered length: %s' % self.cadinalityFiltered
        
        cadinalityCursor = self.dbh.cursor()
        query = "SELECT COUNT(*) FROM %s"  %  _sTable         
#        print 'query: %s' % query
        cadinalityCursor.execute( query )
        self.cardinality = cadinalityCursor.fetchone()[0]
#        print 'Debug: cardinality length: %s' % self.cardinality
    # end def
        
    def filtering( self ):
        "Create the 'WHERE' part of the SQL string"
        filter = ""
        if self.cgi.has_key('sSearch') and self.cgi['sSearch'].value != "":
            filter = "WHERE "
            for i in range( len(_columns) ):
                s = "to_char(%s,'999999')" % _columns[i]  
                if _columns[i] in _string_columns:
                    s = _columns[i]
                elif _columns[i] in _boolean_columns:
                    continue # skip booleans for now.
                # end if
#                log('Doing matching with: %s\n' % s)
                filter += "%s LIKE '%%%s%%' OR " % (s, self.cgi['sSearch'].value)
            filter = filter[:-3]
        return filter
    # end def
        
    def ordering( self ):
        "Create the 'ORDER BY' part of the SQL string"
        order = ""
        if ( self.cgi['iSortCol_0'].value != "" ) and ( self.cgi['iSortingCols'].value > 0 ):
            order = "ORDER BY  "
            for i in range( int(self.cgi['iSortingCols'].value) ):
                order += "%s %s, " % (_columns[ int(self.cgi['iSortCol_'+str(i)].value) ], \
                    self.cgi['sSortDir_'+str(i)].value)
        return order[:-2]
    # end def
        
    def paging( self ):
        "Create the 'LIMIT' part of the SQL string"
        limit = ""
        if ( self.cgi['iDisplayStart'] != "" ) and ( self.cgi['iDisplayLength'] != -1 ):
#            limit = "LIMIT %s, %s" % (self.cgi['iDisplayStart'].value, self.cgi['iDisplayLength'].value )
            limit = "LIMIT %s OFFSET %s" % (self.cgi['iDisplayLength'].value, self.cgi['iDisplayStart'].value )
        # end if
        return limit
    # end def
# end class

# Perform the server-side actions for DataTables
dtserver=DataTablesServer()