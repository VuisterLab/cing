"""
Execute like:
python -u $CINGROOT/python/cing/NRG/runSqlForSchema.py devnrgcing    $CINGROOT/python/cing/NRG/sql/setup_Schema.sql  .
python -u $CINGROOT/python/cing/NRG/runSqlForSchema.py devnrgcing    $CINGROOT/python/cing/NRG/sql/createDB-CING_psql.sql  .

python -u $CINGROOT/python/cing/NRG/runSqlForSchema.py nrgcing    $CINGROOT/python/cing/NRG/sql/dumpNRG-CING.sql        $D/NRG-CING/pgsql
python -u $CINGROOT/python/cing/NRG/runSqlForSchema.py nrgcing    $CINGROOT/python/cing/NRG/sql/loadDB-CING_psql.sql    $D/NRG-CING/pgsql
python -u $CINGROOT/python/cing/NRG/runSqlForSchema.py nrgcing    $CINGROOT/python/cing/NRG/sql/loadBmrbPdbMatch.sql    \
            $CINGROOT/data/NRG/bmrbPdbMatch
"""


from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG import * #@UnusedWildImport

schemaIdOrg = CASD_DB_NAME # this should match the input SQL.
db_name = PDBJ_DB_NAME
user_name = PDBJ_DB_USER_NAME


def runSqlForSchema(sqlFile, schemaId = CASD_DB_NAME, rootPath=None):
    
    if schemaId == SCHEMA_ID_ALL_STR:
        for schemaIdSpecific in schemaIdList:
            if runSqlForSchema(sqlFile, schemaId = schemaIdSpecific, rootPath=rootPath):
                nTerror("Failed for schema: %s" % schemaIdSpecific)
            # end if
        # end for
        nTmessage("Done with overall runSqlForSchema")
        return
    # end if

    if rootPath:
        os.chdir(rootPath)
    txt = readTextFromFile(sqlFile)
    old = schemaIdOrg
    new = schemaId
    if old != new:
        txt = txt.replace(old, new)

    txt = txt.replace('$cwd', rootPath)
    sqlFileRoot = nTpath(sqlFile)[1]
    fn = 'tmpRunSqlForSchema_%s_%s.sql' % (sqlFileRoot, schemaId)
    if writeTextToFile(fn,txt):
        nTerror('Failed to write new sql file.')
        return True
    psqlProgram = ExecuteProgram( pathToProgram = 'psql', rootPath = rootPath,
                                   redirectOutput = False,
                                   redirectInputFromFile = fn
                                 )
    argumentListStr = '%s %s' % (db_name, user_name)
    nTmessage('==> Running psql on schema %s ... ' % schemaId)
    psqlProgram(argumentListStr)
    nTmessage('Done!')

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 3:
        nTerror("Failed to find expected 3 arguments")
        sys.exit(1)
    schemaId = args[0]
    sqlFile = args[1]
    rootPath = args[2]
    if (schemaId != SCHEMA_ID_ALL_STR) and (schemaId not in schemaIdList):
        nTerror("Need to be called with valid schema id from %s but got: [%s]" % (str(schemaIdList), schemaId))
        sys.exit(1)
    if not os.path.exists(rootPath):
        nTerror("rootPath does not exist")
        sys.exit(1)

    if runSqlForSchema(sqlFile, schemaId=schemaId, rootPath=rootPath):
        nTerror('Failed to createDb for schema: %s' % schemaId)
        sys.exit(1)