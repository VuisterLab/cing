"""
Execute like:
python -u $CINGROOT/python/cing/NRG/runSqlForSchema.py nrgcing
"""

from cing import cingDirTmp
from cing import cingPythonCingDir
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG import * #@UnusedWildImport

schemaIdOrg = CASD_DB_NAME
sqlDir = os.path.join(cingPythonCingDir,'NRG', 'sql')

if True: # default: True
    db_name = PDBJ_DB_NAME
    user_name = PDBJ_DB_USER_NAME
else:
    db_name = CASD_DB_NAME
    user_name = CASD_DB_USER_NAME

def runSqlForSchema(sqlFile, schemaId = CASD_DB_NAME):
    os.chdir(cingDirTmp)
    txt = readTextFromFile(sqlFile)
    old = schemaIdOrg
    new = schemaId
    if old != new:
        txt = txt.replace(old, new)
    sqlFileRoot = NTpath(sqlFile)[1]
    fn = 'tmpRunSqlForSchema_%s_%s.sql' % (sqlFileRoot, schemaId)
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
    args = sys.argv[1:]
    schemaId = args[0]
    if schemaId not in schemaIdList:
        NTerror("Need to be called with valid schema id from %s but got: [%s]" % (str(schemaIdList), schemaId))
        sys.exit(1)

#    sqlFile = os.path.join(sqlDir, 'createDB-CING_psql.sql')
#    sqlFile = os.path.join(sqlDir, 'loadDB-CING_psql.sql')
    sqlFile = os.path.join(sqlDir, 'createDepTables.sql')
    if runSqlForSchema(sqlFile, schemaId=schemaId):
        NTerror('Failed to createDb for schema: %s' % schemaId)
        sys.exit(1)

