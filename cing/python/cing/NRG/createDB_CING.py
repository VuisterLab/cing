from cing import cingDirTmp
from cing import cingPythonCingDir
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG import CASD_DB_NAME
from cing.NRG import PDB_DB_NAME
from cing.NRG import PDBJ_DB_NAME
from cing.NRG import CASD_DB_USER_NAME
from cing.NRG import PDBJ_DB_USER_NAME

schemaIdOrg = CASD_DB_NAME
createDB_FileName = os.path.join(cingPythonCingDir,'NRG', 'sql', 'createDB-CING_psql.sql')

if True: # default: True
    db_name = PDBJ_DB_NAME
    user_name = PDBJ_DB_USER_NAME
else:
    db_name = CASD_DB_NAME
    user_name = CASD_DB_USER_NAME

def createDb(schemaId = CASD_DB_NAME):
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
    schemaId = PDB_DB_NAME
    if createDb(schemaId):
        NTerror('Failed to createDb for schema: %s' % schemaId)
        sys.exit(1)

