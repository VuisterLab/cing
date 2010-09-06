from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG import CASD_DB_NAME
from cing.NRG import CASD_DB_USER_NAME
from cing.NRG import PDBJ_DB_NAME
from cing.NRG import PDBJ_DB_USER_NAME
from cing.PluginCode.required.reqOther import *
import gc
import warnings

DB_TYPE_MYSQL = 'mysql'
DB_TYPE_PSQL = 'postgres'
DB_TYPE_DEFAULT = DB_TYPE_PSQL

if True: # for easy blocking of data, preventing the code to be resorted with imports above.
#    switchOutput(False)
    try:
        # All sql imports here and not above.
        import sqlalchemy
        from sqlalchemy import create_engine
        from sqlalchemy.orm.session import sessionmaker
        from sqlalchemy.schema import MetaData
        from sqlalchemy.schema import Table
        from sqlalchemy.sql.expression import func
        from sqlalchemy.exc import SAWarning

        versionTuple = sqlalchemy.__version__.split('.')
        if not (versionTuple[0] > '0' or versionTuple[1] >= '5'):
            switchOutput(True)
            NTerror("Need to have at least version 0.5.x of sqlalchemy installed")
            raise ImportWarning(SQL_STR)
    except:
        switchOutput(True)
        raise ImportWarning(SQL_STR)
    finally:
        switchOutput(True)
#    NTdebug('Using SqlAlchemy')

class cgenericSql(NTdict):
    "Class for connecting to any MySql database."
    def __init__(self, db_type=DB_TYPE_DEFAULT, host='localhost', user='nobody@noaddress.no', passwd='', unix_socket='/tmp/mysql.sock', db="", schema=None, echo=False):
        NTdebug("Initializing cgenericSql with user/db: %s/%s" % (user,db))
        self.host = host
        self.user = user
        self.passwd = passwd
        self.unix_socket = unix_socket
        self.db = db
        self.conn = None # set in connect()
        self.schema = schema
        self.db_type = db_type
        self.engine = None
        self.session = None
        self.Session = None

        "Connection object to database if connected it is None"
        self.version = None
        self.cursor = None
        "Cursor of connection"
        self.echo = echo
        self.metadata = MetaData()
        self.tableNameList = []

    def close(self, wait_time=1.0, force_gc = True):
        # close the connection
        self.session.close()
        self.Session.close_all()
        self.engine.dispose()
        del self.session
        del self.Session
        del self.engine
        if wait_time:
            time.sleep(wait_time)
        if force_gc:
            gc.collect()

    def connect(self):
        "Return True on error"
#        create_engine('oracle://PDBe:password@cmbiora/PDBE') for oracle driver call.
        # driver://username:password@host:port/database
#        connectionString = '%s://%s/%s?user=%s&unix_socket=%s&passwd=%s' % (
        connectionString = '%s://%s:%s@%s/%s' % (
             self.db_type,
             self.user,
             self.passwd,
             self.host,
             self.db
        )
        NTdebug("Using connectionString %s" % connectionString)
        self.engine = create_engine(connectionString, echo=self.echo)
        if True:
            self.conn = self.engine.connect()
        else:
            try:
                self.conn = self.engine.connect()
            except:
                if cing.verbosity >= verbosityWarning:
                    NTexception("Failed to connect to engine")
                    pass
                return True
        if not self.conn:
            NTerror("DB connection failed")
            return True

        self.metadata.bind = self.engine
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session() # instantiation.
        if not self.session:
            NTerror("DB connection failed because session was not retrieved.")
            return True

        self.dBversion = self.session.execute(func.version()).fetchone()[0]
        NTmessage("Now connected on %s to %s database %s by %s" % (self.host, self.db, self.dBversion, self.user))
        if self.db_type == DB_TYPE_MYSQL:
            dBversionTuple = self.dBversion.split('.')
            dBversionFloat = float(dBversionTuple[0] + '.' + dBversionTuple[1])
            if dBversionFloat < 5.1:
                NTerror("Need to have at least version 5.1.x of MySql installed")
                return True

    def loadTable(self, tableName):
        NTdebug("Loading table %s" % tableName)
        warnings.simplefilter('ignore', category=SAWarning)
        #warnings.filters.insert(0, ('ignore', None, SAWarning, None, 0))

        self[tableName] = Table(tableName, self.metadata, autoload=True, schema=self.schema)
        return self[tableName]

    def autoload(self):
        """Return True on error"""
        for tableName in self.tableNameList:
            NTdebug("Loading table %s" % tableName)
            self[tableName] = Table(tableName, self.metadata, autoload=True, schema=self.schema)
#            table = self[tableName]
#            columnNameList = [c.name for c in table.columns]
#            NTdebug("Loaded table %s with columns %s" % (tableName, columnNameList))
        #The MetaData object supports some handy methods, such as getting a list of Tables in the order (or reverse) of their dependency:
#        with warnings.catch_warnings(): # can't use the python 2.5 feature since it's not always enabled. Update when no longer supporting 2.5
        if True:
            warnings.simplefilter("ignore")
            for _t in self.metadata.table_iterator(reverse=False):
                pass
#                NTdebug("Table: %s" % t.name)
            warnings.simplefilter("default") # reset to default warning behavior.
#            warnings.warn("depreciated 123", DeprecationWarning)

class csqlAlchemy(cgenericSql):
    """AKA the Queen's English"""
    def __init__(self, db_type=DB_TYPE_DEFAULT, host='localhost', user='nrgcing1', passwd='4I4KMS', unix_socket='/tmp/mysql.sock', db="nrgcing", schema=None, echo=False):
        NTdebug("Initializing csqlAlchemy with user/db: %s/%s" % (user,db))
        cgenericSql.__init__(self, db_type=db_type, host=host, user=user, passwd=passwd, unix_socket=unix_socket, db=db, schema=schema, echo=echo)
        # be explicit here to take advantage of code analysis.
        self.tableNameList = ['cingentry', 'cingchain', 'cingresidue', 'cingatom']
#        self.tableNameList = [ 'casdcing.'+x for x in self.tableNameList]
#        self.entry = None
        self.cingentry = None
        self.cingchain = None
        self.cingresidue = None
        self.cingatom = None

        self.levelIdResidue = "residue"  # mirrors WI setup.
        self.levelIdAtom = "atom"

    def autoload(self):
        """Return True on error"""
        cgenericSql.autoload(self)
        if not self.cingentry:
            NTerror("Failed to retrieve the cingentry table")
            return True



def printResult(result):
    if result.rowcount < 1:
        return
    for row in result:
        NTmessage(str(row))

if __name__ == '__main__':
    cing.verbosity = verbosityDebug
    if True: # default: True
        db_name = PDBJ_DB_NAME
        user_name = PDBJ_DB_USER_NAME
        schema = CASD_DB_NAME
    else:
        db_name = CASD_DB_NAME
        user_name = CASD_DB_USER_NAME

    csql = csqlAlchemy(user=user_name, db=db_name,schema=schema)
    csql.connect()
    csql.autoload()
