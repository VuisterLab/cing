"""
Execute like:
python -u $CINGROOT/python/cing/NRG/createDB_CING.py
"""

from cing import cingDirTmp
from cing import cingPythonCingDir
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG import * #@UnusedWildImport
from cing.PluginCode.required.reqWhatif import * #@UnusedWildImport
from matplotlib.pylab import * #@UnusedWildImport for most imports

schemaIdOrg = CASD_DB_NAME
sqlDir = os.path.join(cingPythonCingDir,'NRG', 'sql')
createDB_FileName = os.path.join(sqlDir, 'createDB-CING_psql.sql')
loadDB_FileName = os.path.join(sqlDir, 'loadDB-CING_psql.sql')

if True: # default: True
    db_name = PDBJ_DB_NAME
    user_name = PDBJ_DB_USER_NAME
else:
    db_name = CASD_DB_NAME
    user_name = CASD_DB_USER_NAME

def runSqlForSchema(sqlFile = createDB_FileName, schemaId = CASD_DB_NAME):
    os.chdir(cingDirTmp)
    txt = readTextFromFile(createDB_FileName)
    old = schemaIdOrg
    new = schemaId
    if old != new:
        txt = txt.replace(old, new)
    fn = 'create%s-CING_psql.sql' % schemaId
    if writeTextToFile(fn,txt):
        NTerror('Failed to write new sql file.')
        return True
    psqlProgram = ExecuteProgram( pathToProgram = 'psql', rootPath = cingDirTmp,
                                   redirectOutput = False,
                                   redirectInputFromFile = fn
                                 )
    argumentListStr = '%s %s' % (db_name, user_name)
    NTmessage('==> Running psql ... ')
    psqlProgram(argumentListStr)
    NTmessage('Done!')

if __name__ == '__main__':
    schemaId = NRG_DB_NAME
    sqlFile = createDB_FileName
#    sqlFile = loadDB_FileName
    if runSqlForSchema(sqlFile, schemaId):
        NTerror('Failed to createDb for schema: %s' % schemaId)
        sys.exit(1)

