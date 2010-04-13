from cing import verbosityDebug
from cing import verbosityWarning
from cing.Libs.NTutils import NTdebug, NTdict, NTerror, NTmessage
from cing.Libs.NTutils import NTexception
from cing.NRG import CASD_DB_NAME
from cing.NRG import CASD_DB_USER_NAME
from cing.PluginCode.required.reqOther import SQL_STR
import cing
import warnings

DB_TYPE_MYSQL = 'mysql'
DB_TYPE_PSQL = 'postgres'
DB_TYPE_DEFAULT = DB_TYPE_PSQL

if True: # for easy blocking of data, preventing the code to be resorted with imports above.
    from cing.Libs.NTutils import ImportWarning
    from cing.Libs.NTutils import switchOutput
#    switchOutput(False)
    try:
        # All sql imports here and not above.
        import sqlalchemy
        from sqlalchemy import create_engine
        from sqlalchemy.orm.session import sessionmaker
        from sqlalchemy.schema import MetaData
        from sqlalchemy.schema import Table
        from sqlalchemy.sql.expression import func
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
    def __init__(self, db_type=DB_TYPE_DEFAULT, host='localhost', user='nobody@noaddress.no', passwd='', unix_socket='/tmp/mysql.sock', db="", echo=False):
        NTdebug("Initializing cgenericSql")
        self.host = host
        self.user = user
        self.passwd = passwd
        self.unix_socket = unix_socket
        self.db = db
        self.db_type = db_type
        self.engine = None
        "Connection object to database if connected it is None"
        self.version = None
        self.cursor = None
        "Cursor of connection"
        self.echo = echo
        self.metadata = MetaData()
        self.tableNameList = []

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
                    NTexception("Failed to connect to MySql engine")
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
        NTmessage("Now connected to %s database %s by %s" % (self.db, self.dBversion, self.user))
        if self.db_type == DB_TYPE_MYSQL:
            dBversionTuple = self.dBversion.split('.')
            dBversionFloat = float(dBversionTuple[0] + '.' + dBversionTuple[1])
            if dBversionFloat < 5.1:
                NTerror("Need to have at least version 5.1.x of MySql installed")
                return True

    def autoload(self):
        """Return True on error"""
        for tableName in self.tableNameList:
            NTdebug("Loading table %s" % tableName)
            self[tableName] = Table(tableName, self.metadata, autoload=True)
            table = self[tableName]
            columnNameList = [c.name for c in table.columns]
            NTdebug("Loaded table %s with columns %s" % (tableName, columnNameList))
        #The MetaData object supports some handy methods, such as getting a list of Tables in the order (or reverse) of their dependency:
#        with warnings.catch_warnings(): # can't use the python 2.5 feature since it's not always enabled. Update when no longer supporting 2.5
        if True:
            warnings.simplefilter("ignore")
            for t in self.metadata.table_iterator(reverse=False):
                NTdebug("Table: %s" % t.name)
            warnings.simplefilter("default") # reset to default warning behaviour.
#            warnings.warn("deprecated 123", DeprecationWarning)

class csqlAlchemy(cgenericSql):
    """AKA the Queen's English"""
    def __init__(self, db_type=DB_TYPE_DEFAULT, host='localhost', user='nrgcing1', passwd='4I4KMS', unix_socket='/tmp/mysql.sock', db="nrgcing", echo=False):
        cgenericSql.__init__(self, db_type=db_type, host=host, user=user, passwd=passwd, unix_socket=unix_socket, db=db, echo=echo)
        NTdebug("Initialized csqlAlchemy")
        # be explicit here to take advantage of code analysis.
        self.tableNameList = ['entry', 'chain', 'residue', 'atom']
#        self.tableNameList = [ 'casdcing.'+x for x in self.tableNameList]
        self.entry = None
        self.chain = None
        self.residue = None
        self.atom = None
        self.author = None
        self.author_list = None

        self.levelIdResidue = "residue"  # mirrors WI setup.
        self.levelIdAtom = "atom"

    def autoload(self):
        """Return True on error"""
        cgenericSql.autoload(self)
        if not self.entry:
            NTerror("Failed to retrieve the entry table")
            return True

if __name__ == '__main__':
    cing.verbosity = verbosityDebug

    csql = csqlAlchemy(user=CASD_DB_USER_NAME, db=CASD_DB_NAME)
    csql.connect()
    csql.autoload()
