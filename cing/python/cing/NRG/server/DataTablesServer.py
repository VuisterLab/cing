#!/opt/local/bin/python -u

# Script:    DataTables server-side script for Python and Python
# Copyright: 2010 - Allan Jardine
# License:   GPL v2 or BSD (3-point)

# Modules
#from cing.Libs.NTutils import * #@UnusedWildImport
#from cing.NRG import * #@UnusedWildImport
#from cing.NRG.settings import summaryHeaderList
from psycopg2.extras import DictCursor
from traceback import format_exc
import cgi
import psycopg2
import sys
# CGI header
print "Content-Type: text/plain\n\n"
log = sys.stderr.write
#log('Hello CGI\n')
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Easy set varaibles
#
# Array of database columns which should be read and sent back to DataTables
_columns = 'name rog_str distance_count cs_count chothia_class_str chain_count res_count'.split()
_string_columns = 'name rog_str chothia_class_str'.split() # can be simply filtered for.
# Indexed column (used for fast and accurate table cardinality)
_indexColumn = "name"
# DB table to use
_sTable = "nrgcing.cingentry"
#schema= NRG_DB_SCHEMA  
conn_string = "host='localhost' dbname='pdbmlplus' user='nrgcing1' password='4I4KMS'"
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# If you just want to use the basic configuration for DataTables with PHP server-side, there is
# no need to edit below this line
#
class DataTablesServer:
    def __init__( self ):
        self.cgi = cgi.FieldStorage()
        try:
            self.dbh = psycopg2.connect(conn_string)            
            if 0: # Default: False
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
    #             print the entire row 
                print "Row:    ", memory
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
        
        self.runQueries()
        self.outputResult()
    # end def
    
    #
    # outputResult
    # Output the JSON required for DataTables
    #
    def outputResult( self ):
        output = '{'
        output += '"sEcho": '+str(int(self.cgi['sEcho'].value))+', '
        output += '"iTotalRecords": '+str(self.cardinality)+', '
        output += '"iTotalDisplayRecords": '+str(self.cadinalityFiltered)+', '
        output += '"aaData": [ '
        
        mapRog = {'green':  '<font color=#000000>green</font>', 
                  'orange': '<font color=#FFA500>orange</font>', 
                  'red':    '<font color=#FF0000>red</font>'}
#        mapCho = {0:'alpha', 
#                  1:'beta', 
#                  2:'a/b',
#                  3:'coil',
#                  None:'other',
#                  }
        for row in self.resultData:
            output += '['
            for i in range( len(_columns) ):
                v = row[ _columns[i] ]
                if _columns[i] == "rog_str" :
                    v = mapRog[ v ]
#                elif _columns[i] == "chothia_class" :
#                    v = mapCho[ v ]
                # end if
                output += '"%s",' % v
            # end for            
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
    def runQueries( self ):
        'Generate the SQL needed and run the queries'
        dataCursor = self.dbh.cursor(cursor_factory=DictCursor)
        where=self.filtering()
        order=self.ordering()
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