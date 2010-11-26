# python -u $CINGROOT/python/cing/Scripts/interactive/mouseBuffer3.py
from cing.Libs.DBMS import DBMS
import os

if True:
#    os.chdir('/Library/WebServer/Documents/NRG-CING/pgsql')
    os.chdir('/Volumes/tera4/NRG-CING/pgsql')
    dbms = DBMS()
    relationName = 'nrgcing.cingentry'
    dbms.readCsvRelationList([relationName], '.')
    table = dbms.tables[relationName]
    table.setColumnToValue(65,0)
    file_name_new = relationName +"_new.csv"
    table.writeCsvFile(file_name_new)