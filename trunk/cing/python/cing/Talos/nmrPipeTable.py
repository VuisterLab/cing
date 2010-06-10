"""
nmrPipeTab.py

gv 21 March 2006

"""
from cing.Libs.AwkLike import AwkLike
from cing.Libs.NTutils import * #@UnusedWildImport

class nmrPipeTabRow( NTdict ):

    def __init__( self, table, id, **kwds ):
        NTdict.__init__( self, __CLASS__  = 'nmrPipeTabRow',
                                 table      = table,
                                 id         = id,
                                 name       = 'row'+str(id),
                                 __FORMAT__ = '%(name)s',
                                 **kwds
                          )
        # set defaults to None
        for c in self.keys():
            self.setdefault( c, None )
        #end for
    #end def

    def keys( self ):
        """overide keys method to define collums as 'active' items"""
        keys = []
        for c in self.table.columnDefs:
            keys.append( c.name )
        return keys
    #end def

    def __iter__( self ):
        for v in self.values():
            yield v
        #end for
    #end def

    def __str__( self ):
        r = ''
        for col in self.table.columnDefs:
            if not col.hide:
                if self[col.name] == None:
                    dot=col.fmt.find('.')
                    if dot < 0:
                        fmt = col.fmt[:-1] + 's'
                    else:
                        fmt = col.fmt[0:dot] + 's'
                    #endif

                    r = r + fmt % (self.table.noneIndicator) + ' '
                else:
                    r = r + sprintf(col.fmt, self[ col.name ] ) + ' '
                #end if
            #end if
        #end for
        return r
    #end def
#end class

class nmrPipeTable( NTdict ):
    """
    nmrPipeTable class
    implemented as NTdict of NTdict's, i.e.

    element (row-0, INDEX) indexed as
        tab[0].INDEX   or tab[0]['INDEX']

    tab = nmrPipeTable()                # Empty table
    tab = nmrPipeTable( 'tabFile' )     # table from tabFile

    METHODS:

    addColumn( name, fmt = "%s", default=None ):
        Add column 'name' to table; set values to 'default'

    hideColumn( *cNames )
        Hide column(s) cNames

    showColumn( *cNames )
        Show columns cNames

    addRow( **kwds ):
        Add row to table, optional kwds can be used to set values

    readFile( tabFile  ):
        Read table from tabFile

    write( stream=sys.stdout ):
        Write table to stream

    writeFile( tabFile)   :
        Open tabFile, write table and close tabFile

    """

    def __init__( self, tabFile=None, **kwds ):
        NTdict.__init__( self, __CLASS__ = 'nmrPipeTab', **kwds )
        self.__FORMAT__ = '=== nmrPipeTab ===\n' +\
                          '... tabFile:     %(tabFile)s \n' +\
                          '... columnDefs:  %(columnDefs)s\n' +\
                          '... nrows:       %(nrows)d\n'

        self.setdefault('noneIndicator', '-') # character to identify the None value

        self.columnDefs = NTlist()          # list of column definitions, implemented
                                            # as NTdict
        self.rows       = NTlist()
        self.nrows      = 0
        self.remarks    = NTlist()
        self.data       = NTdict()
        self.tabFile    = tabFile

        if (tabFile):
            self.readFile( tabFile  )
        #end if
    #end def

    def addRow( self, **kwds ):
        """
        Add ro to table, optional kwds can be used to set values
        """
        row = nmrPipeTabRow( table=self, id=self.nrows, **kwds )
        self[ self.nrows ] = row
        self.rows.append( row )
        self.nrows += 1
        return row
    #end def

    def addColumn( self, name, fmt = "%s", default=None ):
        """
        Add column 'name' to table; set values to 'default'
        return columnDef, or None on error
        """
        if name in self:
            NTerror('nmrPipeTable.addColumn: column "%s" already exists\n', name )
            return None
        #end if

        col = NTdict( name=name,
                        fmt=fmt,
                        id=len(self.columnDefs),
                        hide=False,
                        __FORMAT__ = '%(name)s'
                      )
        self.columnDefs.append( col )
        self[name] = col
        for row in self:
            row[name] = default
        #end for

        return col
    #end def

    def column( self, cName ):
        """Return list of values of column cName or None on error
        """
        if cName not in self: return None

        col = NTlist()
        for row in self:
            col.append( row[cName] )
        #end for
        return col
    #end def

    def hideColumn( self, *cNames ):
        """
        Hide column(s) cNames
        """
        for c in cNames:
            if not c in self:
                NTerror('nmrPipeTable.hideColumn: column "%s" not defined\n', c)
            else:
                self[c].hide = True
            #end if
        #end for
    #end def

    def showColumn( self, *cNames ):
        """
        Show column(s) cNames
        """
        for c in cNames:
            if not c in self:
                NTerror('nmrPipeTable.showColumn: column "%s" not defined\n', c)
            else:
                self[c].hide = False
            #end if
        #end for
    #end def

    def readFile( self, tabFile  ):
        """
        Read table from tabFile
        """
        NTmessage('==> Reading nmrPipe table file ... ' )

        #end if

        for line in AwkLike( tabFile, minNF = 1, commentString = '#' ):
            if ( line.dollar[1] == 'REMARK' and line.NF > 1 ):
                self.remarks.append( line.dollar[2:] )

            elif ( line.dollar[1] == 'VARS' ):
                for v in line.dollar[2:]:
                    self.addColumn( name=v )
                #end for
            elif ( line.dollar[1] == 'FORMAT' ):
                i = 0
                for f in line.dollar[2:]:
                    self.columnDefs[i].fmt=f
                    i += 1
                #end for
            elif ( line.dollar[1] == 'DATA' and line.NF > 3 ):
                self.data[line.dollar[2]] = line.dollar[3:]

            elif ( line.NF == len( self.columnDefs ) ):
                row = self.addRow()
                for i in range( 0, line.NF ):
                    col = self.columnDefs[i]

                    if (line.dollar[i+1] == self.noneIndicator):
                        row[col.name] = None
                    else:
                        # derive conversion function from fmt field
                        if (col.fmt[-1:] in ['f','e','E','g','G']):
                            func = float
                        elif (col.fmt[-1:] in ['d','o','x','X']):
                            func = int
                        else:
                            func = str
                        #end if
                        row[ col.name ] = func( line.dollar[i+1] )
                    #endif
                #end for
            else:
                pass
            #end if
        #end for
        self.tabFile = tabFile
    #end def

    def write( self, stream=sys.stdout):
        """
        Write tab to stream
        """
        for r in self.remarks:
            fprintf( stream, 'REMARK  %s\n', r )
        #end for

        fprintf(     stream, 'VARS    ' )
        for c in self.columnDefs:
            if not c.hide: fprintf( stream, '%s ', c.name )
        #end for
        fprintf( stream, '\n' )

        fprintf(     stream, 'FORMAT  ' )
        for c in self.columnDefs:
            if not c.hide: fprintf( stream, '%s ', c.fmt )
        #end for
        fprintf( stream, '\n' )

        for d,v in self.data.iteritems():
            fprintf( stream, 'DATA     %s %s\n', d, v )
        #end for

        fprintf( stream, '\n' )
        for row in self:
            fprintf( stream, '%s\n', row )
        #end for

    #end def

    def writeFile( self, tabFile)   :
        """
        Write table to tabFile
        """
        file = open( tabFile, 'w' )
        self.write( file )
        file.close()
        NTmessage('==> Written nmrPipe table file "%s"', tabFile )
        #end if
    #end def

    #iteration overrides: loop over row indices or rows
    def keys( self ):
        return range( 0, self.nrows )
    #end def

    def __iter__( self ):
        for row in self.rows:
            yield row
        #end for
    #end def
#end def

#==============================================================================
# Testing from here-on
#==============================================================================
#
if __name__ == '__main__':

    tab = nmrPipeTable( 'test.tab' )
    print tab[0]
    print tab[0].get('PSI')
    print tab[0].keys()
    print tab[0].values()
#    for c in tab[0]:
#        print c
    tab.addRow( PHI=10, PSI=13)
    tab.write()
