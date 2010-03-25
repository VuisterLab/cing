'''
Created on Mar 25, 2010

This class thinks of a bunch of CSV files (such as created by Mac Numbers in iWork) as a database
much like the code in Wattos.Database.DBMS.
@author: jd
'''
from cing.Libs.NTutils import NTerror
import csv
import os
import urllib

DEFAULT_COLUMN_LABEL = 'COLUMN_' # a number will be added.

class Relation():

    def __init__(self, name, dbms):
        # Name for the column. Only place where order of columns is defined and matters.*/
        self.columnOrder = []
        self.name = name
        # Other objects that should all be native arrays with using parallel indices as the above.
        self.attr = {}
        self.dbms = dbms

    def insertColumn(self, index=-1, label=None, foreignKeyConstr=None):
        """Insert a column for a certain variable type; before the given position.
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
            label = DEFAULT_COLUMN_LABEL + `index`


        self.columnOrder.insert(index, label)
        self.attr[label] = []

    def sizeColumns(self):
        return len(self.columnOrder)

    def sizeRows(self):
        firstColumn = self.attr[ self.columnOrder[0] ]
        return len(firstColumn)

    def getColumnByIdx(self, idx):
        label = self.columnOrder[idx]
        return self.attr[label]

    def readCsvFile(self, file_name, containsHeaderRow, dtd_file_name=None):
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
#        NTdebug("Reading from %s" % (url_links))
        try:
            resource = urllib.urlopen(url_links)
            reader = csv.reader(resource)
        except IOError:
            NTerror("Couldn't open url for reader: " + url_links)
            return True

        ncols = -1
        try:
            if containsHeaderRow:
                row = reader.next()
#                NTdebug("read header: %s" % row)
                ncols = len(row)
                for c in range(ncols):
                    self.insertColumn(label=row[c])
            for row in reader:
                if ncols == -1: # Without a header the table columns will have default labels.
                    ncols = len(row)
                    for c in range(ncols):
                        self.insertColumn()
                if len(row) != ncols:
                    NTerror("Failed to read correct number of columns on line: %s" % row)
                    return True
                for c in range(ncols):
                    label = self.columnOrder[c]
                    l = self.attr[label]
                    l.append(row[c])
        # Never know when the connection is finally empty.
        except IOError:
            pass
#        NTdebug("Read number of rows: %d" % self.sizeRows())
        self.dbms.tables[self.name] = self

class DBMS():
    def __init__(self):
        self.tables = {}

    def readCsvRelationList(self, relationNames, csvFileDir,
            csvDtdFileDir=None, checkConsistency=False, showChecks=False, containsHeaderRow=True):
        csvFilesRead = len(relationNames)
        for i in range(csvFilesRead):
            relation = Relation(relationNames[i], self)
#            NTmessage("Reading relation : " + relation.name)
            csv_fileName = os.path.join(csvFileDir, relation.name + ".csv")
            if relation.readCsvFile(csv_fileName, containsHeaderRow):
                NTerror("Failed to read csv file: " + csv_fileName)
                return True

