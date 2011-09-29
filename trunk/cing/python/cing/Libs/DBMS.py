'''
Created on Mar 25, 2010

This class thinks of a bunch of CSV files (such as created by Mac Numbers in iWork) as a database
much like the code in Wattos.Database.DBMS.
@author: jd
'''

from StringIO import StringIO
from cing.Libs.NTutils import * #@UnusedWildImport
import csv
import operator
import urllib

DEFAULT_COLUMN_LABEL = 'COLUMN_' # a number will be added.
ROW_WITHOUT_COLUMNS_STRING   = "No columns present"
NULL_STRING = '' # may be modified

class Relation():

    def __init__(self, name, dbms, columnList=None):
        # Name for the column. Only place where order of columns is defined and matters.*/
        self.columnOrder = []
        self.name = name
        # Other objects that should all be native arrays with using parallel indices as the above.
        self.attr = {}
        self.dbms = dbms
        self.dbms.tables[self.name] = self
        if columnList:
            for col in columnList:
                self.insertColumn(label=col)


    def insertColumn(self, index=-1, label=None, 
#                     foreignKeyConstr=None
                     ):
        """
        Insert a column for a certain variable type; before the given position. Or at the end when a -1 is given.
        label Column name; has to be unique.
        """
#        if ( hasColumn( label )  ) {
#            General.showWarning("in insertColumn label already present for label: [" +
#                label + "] and type: [" + dataTypeList[dataType] + "]. So didn't add another column with this label.");
#            return false;
#        }

#        if ( index > sizeColumns() ) {
#            General.showWarning("in insertColumn the given index for the new column ("+index+") is larger than the current size: [" +
#                sizeColumns() + "] that's impossible. No column added.");
#            return false;
#        }

        if index == -1:
            index = self.sizeColumns()
        if label == None: # label may be empty string or a zero of some sort except None
            label = DEFAULT_COLUMN_LABEL + repr(index)


        self.columnOrder.insert(index, label)
        self.attr[label] = []

    def sizeColumns(self):
        return len(self.columnOrder)

    def sizeRows(self):
        firstColumn = self.attr[ self.columnOrder[0] ]
        return len(firstColumn)

    def getColumnByIdx(self, idx):
        'Return None on error'
        if idx < 0:
            nTerror("Found negative idx %s in getColumnByIdx" % idx)
            return None
        if idx >= self.sizeColumns():
            nTerror("Found idx %s in getColumnByIdx which is equal or larger than self.sizeColumns(): %s" % (idx, self.sizeColumns()))
            return None
        label = self.columnOrder[idx]
        return self.attr[label]

    def setColumnToValue(self, idx, value):
        'Return True on error'
        column = self.getColumnByIdx(idx)
        if column == None:
            return True
        for i in range(self.sizeRows()):
            column[i] = value
    # end def

    def renameColumn(self, idx, label):
        oldLabel = self.columnOrder[idx]
#        nTdebug("Renaming column %s at idx %s to %s" % (oldLabel, idx, label))
        col = self.getColumn(oldLabel)
        del self.attr[oldLabel]
        self.attr[label] = col
        self.columnOrder[idx] = label


    def getColumn(self, label):
        if label not in self.columnOrder:
            nTerror("Requested column label is absent in table: %s" % self.name)
            return None
        return self.attr[label]

    def convertColumn(self, idx, func=int):
        """Returns None on error or column converted otherwise"""

        column = self.getColumnByIdx(idx)
        if column == None:
            return None
        for idx,v in enumerate(column):
            column[idx] = apply(func,(v,))
        return column

    def readCsvFile(self, file_name, containsHeaderRow, 
#                    dtd_file_name=None
                    ):
        """
     *If containsHeaderRow is false then the default labels will be used.
     *dtd file if not existing defaults to all elements being STRING.
     *If it does exist,  it should be formatted as a csv file with the first two
     *columns having the column name and the column data type as strings.
        """
#        //General.showDebug("Reading from file    : " + file_name);
#        //General.showDebug(" with header         : " + containsHeaderRow);
#        //General.showDebug(" and dtd             : " + dtd_file_name);

        url_links = 'file://' + file_name
#        nTdebug("Reading from %s" % (url_links))
        try:
            resource = urllib.urlopen(url_links)
            reader = csv.reader(resource)
        except IOError:
            nTtracebackError()
            nTerror("Couldn't open url for reader: " + url_links)
            return True

        ncols = -1
        try:
            if containsHeaderRow:
                row = reader.next()
#                nTdebug("read header: %s" % row)
                ncols = len(row)
                for c in range(ncols):
                    self.insertColumn(label=row[c])
            for row in reader:
                if ncols == -1: # Without a header the table columns will have default labels.
                    ncols = len(row)
                    for c in range(ncols):
                        self.insertColumn()
                if len(row) != ncols:
                    nTerror("Failed to read correct number of columns on line: %s" % row)
                    return True
                for c in range(ncols):
                    label = self.columnOrder[c]
                    myList = self.attr[label]
                    myList.append(row[c])
        # Never know when the connection is finally empty.
        except IOError:
            pass
#        nTdebug("Read %8d rows %2d cols to relation %s" % (self.sizeRows(), self.sizeColumns(), self.name))
    # end def


    def writeCsvFile(self, file_name=None, doHeader=True):
        """Returns True on error.
        File name will be derived from table name if omitted.
        """

        txt = ''
        if doHeader:
            txt += ','.join(self.columnOrder)
            txt += '\n'
        firstColumn = self.getColumnByIdx(0)
        nrows = len(firstColumn)
        ncols = len(self.columnOrder)
        dataAsMatrix = []
        for c in range(ncols):
            dataAsMatrix.append(self.getColumnByIdx(c))

        rowStrList = []
        for r in range(nrows):
            colStrList = []
            for c in range(ncols):
                colStrList.append( str(dataAsMatrix[c][r]) )
            # end for c
            rowStr = ','.join(colStrList)
#            nTdebug("Adding rowStr: %s" % rowStr)
            rowStrList.append( rowStr )
        # end for r
        resultStr = txt + '\n'.join(rowStrList)

        if not file_name:
            file_name = self.name + '.csv'
        nTmessage("Will write %s nrows and %s ncols to %s" % (nrows,ncols,file_name))
        if writeTextToFile(file_name, resultStr):
            nTerror("Failed to write string to file: %s" % file_name)
            return True

    def getHash(self, keyColumnLabel = None, ignoreDuplicateKey = False, useSingleValueOfColumn = -1):
        """Takes a DMBS table and turns it into a hash on the keyColumnLabel with
        values a list of all columns. If return useSingleValueOfColumn is set to a columnId >= 0 then the value will
        not be all columns as an array but simply a single value.

        If the keyColumnLabel is None then the first column will be used.
        One warning will be issued if the column contains multiple keys. The code
        will skip consecutive occurrences.

        Returns False on error.
        """

        dic = {}

        if keyColumnLabel == None:
            keyColumn = self.getColumnByIdx(0)
        else:
            keyColumn = self.getColumn(keyColumnLabel)
        if keyColumn == None:
            return
        columnList = [ self.getColumnByIdx(i) for i in range(self.sizeColumns())]

        duplicateKeyFound = False
        for idx, k in enumerate(keyColumn):
            if dic.has_key(k):
                duplicateKeyFound = 'Last duplicate key found was for row idx: %s with key: %s' % ( idx, k )
                continue
            if useSingleValueOfColumn >= 0:
                dic[k] = columnList[useSingleValueOfColumn][idx]
            else:
                columnValues = [ columnList[i][idx] for i in range(self.sizeColumns())]
                dic[k] = columnValues

        if duplicateKeyFound:
            if ignoreDuplicateKey:
                nTdebug(duplicateKeyFound)
            else:
                nTwarning(duplicateKeyFound)
        return dic

    def isValidColumnIdx( self, columnIdx ):
        'Just checking'
        if ( ( columnIdx < 0 ) or ( columnIdx > (self.sizeColumns()-1))):
            return False
        return True

    def getColumnLabel( self, index ):
        'Return False on error'
        if not self.isValidColumnIdx(index):
            nTerror("in getColumnLabel: given index is not valid for columns: %s" % index)
            return
        label = self.columnOrder[index]
        return label

    def __str__( self, show_header = True,
#         show_data_types= True,
#         show_fkcs= True,
#         show_indices= True,
         show_rows= True):
        """
        This will create a string representation. The code in here should not
        need to be optimized because it is never intended to use this for millions of
        rows in an efficient way.
        Returns None in case of error.
        """

        sizeColumns = self.sizeColumns()
        sizeRows = self.sizeRows()
        if sizeColumns < 1:
            return    "---  Relation        : " + self.name + " has NO columns ---\n"

        file_str = StringIO()
#        // Header
        if show_header:
#            boolean containsForeignKeyConstraints = false;
#            boolean containsindices               = false;
            file_str.write("---  Relation        : " + self.name + " ---\n")
            file_str.write("---  Column Labels   : ")
            for i in range(sizeColumns):
                label = self.getColumnLabel(i)
                file_str.write( label )
#                ForeignKeyConstr fkc = dbms.foreignKeyConstrSet.getForeignKeyConstrFrom(name,label);
#                if ( fkc != null ) {
#                    containsForeignKeyConstraints = true;
#                }
#                if ( indices.containsKey( label ) ) {
#                    containsindices = true;
#                }
                if i < ( sizeColumns - 1 ):
                    file_str.write(",")
                else:
                    file_str.write(" ---\n")

#            // Datatypes
#            if (show_data_types) {
#                file_str.write("---  Data Types      : ");
#                for (int i=0;i<sizeColumns;i++) {
#                    String label = getColumnLabel(i);
#                    int dataType = getColumnDataType(label);
#                    file_str.write(dataTypeList[dataType]);
#                    //file_str.write("("+dataType+")");
#                    if ( i < ( sizeColumns - 1 ) )
#                        file_str.write(",");
#                    else
#                        file_str.write(" ---\n");
#                }
#            }
#            // Foreign Key Constraints
#            if ( containsForeignKeyConstraints && show_fkcs ) {
#                file_str.write("---  Foreign Key Constraints   :\n");
#                for (int i=0;i<sizeColumns;i++) {
#                    String label = getColumnLabel(i);
#                    ForeignKeyConstr fkc = dbms.foreignKeyConstrSet.getForeignKeyConstrFrom(name,label);
#                    if ( fkc != null ) {
#                        file_str.write( "\t" );
#                        file_str.write( fkc.toString() );
#                        file_str.write( General.eol );
#                    }
#                }
#            }
#            // indices
#            if ( containsindices && show_indices ) {
#                file_str.write("---  indices                   :\n");
#                for (int i=0;i<sizeColumns;i++) {
#                    String label = getColumnLabel(i);
#                    if ( indices.containsKey( label )) {
#                        // Check all elements in array to see if there is such an index
#                        Index[] al = (Index[]) indices.get( label );
#                        for (int j=0;j<Index.INDEX_TYPE_COUNT;j++) {
#                            Index index = al[j];
#                            if ( index == null ) { // will skip zero-th element
#                                continue;
#                            }
#                            file_str.write( "\tColumn " );
#                            file_str.write( label );
#                            file_str.write( " has index. " );
#                            file_str.write( index.toString() );
#                            file_str.write( General.eol );
#                        }
#                    }
#                }
#            }
#        }

        if show_rows:
            if sizeRows < 1 :
                file_str.write("---  Empty Relation (%s columns but no rows) ---\n" % sizeColumns)
                return file_str.getvalue()
            # end if
            for r in range(sizeRows):
                rowString = self.toStringRow( r )
                if rowString == None:
                    nTerror("Failed to get row as a string for row %s from relation %s" % (r,self.name))
                    return None
                file_str.write( rowString ) # Get the row representation.
                file_str.write('\n')
            # end
        else:
            file_str.write("---  Relation contains %s rows ---\n" % sizeRows)
        # end if


        return file_str.getvalue()


    def toStringRow(self, row, showColumnLabels=False):
        """Still need to program correct quote styles for csv format if that becomes important.
         Returns ROW_WITHOUT_COLUMNS_STRING
         if there are no columns in the table.
         Return None on error.
         """
        if self.sizeColumns() == 0:
            return ROW_WITHOUT_COLUMNS_STRING

        file_str = StringIO()
        sizeColumns = self.sizeColumns()
        sizeColumnsMinusOne = sizeColumns - 1
        if showColumnLabels:
            file_str.write( "[Header] " )
            for c in range(sizeColumns):
                file_str.write( self.getColumnLabel(c) )
                if c < sizeColumnsMinusOne:
                    file_str.write(',')
            file_str.write('\n')
        file_str.write( "[%s] " % row )
        for c in range(sizeColumns):
            valueString = self.getValueString(row,c)
            if valueString == None:
                nTerror("Failed to get value as a string for row %s, column %s from relation %s" % (row,c,self.name))
                return None
            file_str.write( self.getValueString(row,c) )
            if c < sizeColumnsMinusOne:
                file_str.write(',')
        return file_str.getvalue()

    def toTable(self):
#        return [self.attr[label] for label in self.columnOrder ] Too easy.
        result = []
        sizeColumns = self.sizeColumns()
        sizeRows = self.sizeRows()
        if sizeColumns == 0:
            return result
        if sizeRows == 0:
            return result
        for r in range(sizeRows):
            row = []
            result.append(row)
            for c in range(sizeColumns):
                value = self.getValue(r, c)
                row.append(value)
        return result

    def getValue( self, rowIdx, columnIdx):
        """
        Returns None on error.
        Returns module variable NULL_STRING for None values. Modify if needed.
        """
        label = self.getColumnLabel(columnIdx)
#        // Sanity checks
        if label == False:
            nTerror("Failed to Relation.getValue for columnIdx idx %s. Existing columnIdx labels: %s" % (
                columnIdx, str(self.columnOrder)))
            return None
        columnIdx = self.getColumnByIdx(columnIdx)
        sizeRows = self.sizeRows()
        if rowIdx < 0 or rowIdx >= self.sizeRows():
            nTerror("Failed to Relation.getValue for rowIdx idx %s is not in range of (0,%s) for columnIdx %s." % (
                rowIdx, label, sizeRows))
            return None

        return columnIdx[rowIdx]
    # end def

    def getValueString( self, rowIdx, columnIdx):
        """
        Returns None on error.
        Returns module variable NULL_STRING for None values. Modify if needed.
        """
        value = self.getValue( rowIdx, columnIdx)
        if value == None:
            return NULL_STRING
        return str(value)
    # end def

    def toLol( self ):
        """
        Creates a standard list of lists.
        """
        sizeRows = self.sizeRows()
        sizeColumns = self.sizeColumns()
        result = []
        for _i in range(sizeRows):
            result.append([None] * sizeColumns)
#        nTdebug("result:\n%s" % result)
        for colIdx in range(sizeColumns):
            column = self.getColumnByIdx(colIdx)
            for rowIdx in range(sizeRows):
                result[rowIdx][colIdx] =  column[rowIdx]
            # end for
        # end for
        return result
    # end def

    def fromLol( self, lol ):
        """
        Moves data from standard list of lists in.
        Relation will grow extra rows if size is too small.
        Input needs to be at least as big as Relation.
        """
        sizeColumns = self.sizeColumns()
        inputSizeColumns = len(lol[0])
        if inputSizeColumns > sizeColumns:
            nTdebug("Growing relation columns from %s to %s" % (sizeColumns, inputSizeColumns))
            for _i in range(inputSizeColumns - sizeColumns):
                label = "column_%d" % self.sizeColumns()
#                nTdebug("Adding column %s" % label)
                self.insertColumn(-1, label)
            # end for
            sizeColumns = self.sizeColumns()
        # end if

        sizeRows = self.sizeRows()
        inputSizeRows = len(lol)
        if inputSizeRows > sizeRows:
            nTdebug("Growing relation rows from %s to %s" % (sizeRows, inputSizeRows))
            rowCountToAdd = inputSizeRows - sizeRows
            for colIdx in range(sizeColumns):
                column = self.getColumnByIdx(colIdx)
                for rowIdx in range(rowCountToAdd):
                    column.append( None )
                # end for
            # end for
            sizeRows = self.sizeRows()
        # end if

        for colIdx in range(sizeColumns):
            column = self.getColumnByIdx(colIdx)
            for rowIdx in range(sizeRows):
                column[rowIdx] = lol[rowIdx][colIdx]
            # end for
        # end for
    # end def


    def sortRelationByColumnIdx( self, columnList):
        """
        First rewrites the relation to a normal LoL for which standard techniques are used."
        return True on error
        """
        table = self.toLol()
#        nTdebug("Table setup:\n%s" % table)
        tableNew = sort_table(table, columnList)
#        nTdebug("tableNew:\n%s" % tableNew)
        if self.fromLol(tableNew):
            nTerror("Failed " + getCallerName())
            return True
    # end def
# end class


class DBMS():
    def __init__(self):
        self.tables = {}

    def readCsvRelationList(self, relationNames, csvFileDir='.',
#            csvDtdFileDir=None, checkConsistency=False, showChecks=False, 
            containsHeaderRow=True):
        'return True on error'
        csvFilesRead = len(relationNames)
        for i in range(csvFilesRead):
            if self.readCsvRelation( relationNames[i], csvFileDir=csvFileDir, 
#                                     csvDtdFileDir=csvDtdFileDir, checkConsistency=checkConsistency, showChecks=showChecks, 
                                     containsHeaderRow=containsHeaderRow):
                nTerror("Failed to read relation: " + relationNames[i])
                return True

    def readCsvRelation(self, relationName, csvFileDir='.',
#            csvDtdFileDir=None, checkConsistency=False, showChecks=False, 
            containsHeaderRow=True, showMessages=0):
        'return True on error'
        relation = Relation(relationName, self)
        if showMessages:
            nTmessage("Reading relation : " + relation.name)
        csvFileDir = os.path.abspath(csvFileDir)
        csv_fileName = os.path.join(csvFileDir, relation.name + ".csv")
        if relation.readCsvFile(csv_fileName, containsHeaderRow):
            nTerror("Failed to read csv file: " + csv_fileName)
            return True
    # end def

# Convenience method
def getRelationFromCsvFile( csvPath, containsHeaderRow=True):
    'Return None on error'
    dbms = DBMS()
    (directory, relationName, _extension) = nTpath(csvPath)
    if dbms.readCsvRelation( relationName, csvFileDir=directory, containsHeaderRow=containsHeaderRow ):
        nTerror("Failed to getRelationFromCsvFile")
        return
    return dbms.tables[relationName]
# end def

def addColumnHeaderRowToCsvFile( csvPath, columnOrder ):
    'Return True on error.'
    relation = getRelationFromCsvFile(csvPath, False)
    if not relation:
        nTerror("Failed to read file in " + getCallerName())
        return True
    lread = relation.sizeColumns()
    lnew = len(columnOrder)
    if lread != lnew:
        nTerror("Read %s columns but got number of names for them: %s" % (lread, lnew))
        return True
#    nTdebug("Read %s" % r)
    for idx in range(lnew):
        relation.renameColumn(idx, columnOrder[idx])
    relation.writeCsvFile()
# end def

def sortRelationByColFromCsvFile( csvPath, columnList=None, containsHeaderRow=True):
    'Return True on error'
    dbms = DBMS()
    (directory, relationName, _extension) = nTpath(csvPath)
    if dbms.readCsvRelation( relationName, csvFileDir=directory, containsHeaderRow=containsHeaderRow ):
        nTerror("Failed to readCsvRelation")
        return True
    r = dbms.tables[relationName]
    if columnList == None:
        columnList = [0]
#    nTdebug("Relation read:\n%s" % r)
    if r.sortRelationByColumnIdx(columnList):
        nTerror("Failed to sortRelationByColumnIdx")
        return True
#    nTdebug("Relation sorted:\n%s" % r)
    if r.writeCsvFile():
        nTerror("Failed to writeCsvFile")
        return True
# end def

# Stolen from http://www.saltycrane.com/blog/2007/12/how-to-sort-table-by-columns-in-python/
# by:
def sort_table(table, cols):
    """ sort a table by multiple columns
        table: a list of lists (or tuple of tuples) where each inner list
               represents a row
        cols:  a list (or tuple) specifying the column numbers to sort by
               e.g. (1,0) would sort by column 1, then by column 0
    """
    for col in reversed(cols):
        table = sorted(table, key=operator.itemgetter(col))
    return table

