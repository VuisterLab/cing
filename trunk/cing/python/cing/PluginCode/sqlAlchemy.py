'''
Generic class to connect to any db using sqlAlchemy
and specific class for cings RDB.
'''

from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG import * #@UnusedWildImport
from cing.PluginCode.required.reqOther import *
import gc
import numpy
import warnings

DB_TYPE_MYSQL = 'mysql'
#DB_TYPE_PSQL = 'postgres'
DB_TYPE_PSQL = 'postgresql' # changed in 
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
        from psycopg2.extensions import register_adapter, AsIs
        versionTuple = sqlalchemy.__version__.split('.')
        if not (versionTuple[0] > '0' or versionTuple[1] >= '5'):
            switchOutput(True)
            nTerror("Need to have at least version 0.5.x of sqlalchemy installed")
            raise ImportWarning(SQL_STR)
    except:
        switchOutput(True)
        raise ImportWarning(SQL_STR)
    finally:
        switchOutput(True)
#    nTdebug('Using SqlAlchemy')
# end if

# Hack from http://rehalcon.blogspot.com/2010/03/sqlalchemy-programmingerror-cant-adapt.html
def adapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)
register_adapter(numpy.float64, adapt_numpy_float64)

class CgenericSql(NTdict): # pylint: disable=R0902
    "Class for connecting to any MySql database."
    def __init__(self, db_type=DB_TYPE_DEFAULT, host='localhost', user='nobody@noaddress.no', passwd='', 
                 unix_socket='/tmp/mysql.sock', db="", schema=None, echo=False):
        NTdict.__init__(self)
#        nTdebug("Initializing CgenericSql with user/db: %s/%s" % (user,db))
        self.host = host
        self.user = user
        self.passwd = passwd
        self.unix_socket = unix_socket
        self.db = db
        self.dBversion = None # set in connect()
        self.conn = None # set in connect()
        self.schema = schema
        self.db_type = db_type
        self.engine = None
        self.session = None
        self.sessionUpperCase = None

        #: Connection object to database if connected it is None
        self.version = None
        self.cursor = None
        #: Cursor of connection
        self.echo = echo
        self.metadata = MetaData()
        self.tableNameList = []
    # end def

    def close(self, wait_time=1.0, force_gc = True):
        'close the connection'
        self.session.close()
        self.sessionUpperCase.close_all()
        self.engine.dispose()
        del self.session
        del self.sessionUpperCase
        del self.engine
        if wait_time:
            time.sleep(wait_time)
        if force_gc:
            gc.collect()
        # end if
    # end def

    def connect(self, maxTries = 2, retryInitialDelaySeconds = 5., retryDelayFactor = 1.2):
        """
        Return True on error
        
        Retry given number of times with given delay scheme for when RDB has not enough connections.
        """
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
#        nTdebug("Using connectionString %s" % connectionString)
        self.engine = create_engine(connectionString, echo=self.echo)
        
        ntries = 0
        while ntries < maxTries:
            ntries += 1
#            nTdebug("Trying to connect to DB")
            try:
                self.conn = self.engine.connect()
                if self.conn:
                    break
                # end if
            except:
                nTtracebackError()
                nTerror("Failed to connect to DB for try %s" % ntries)                
            # end try
            nTdebug("Now sleeping %s seconds.")
            time.sleep(retryInitialDelaySeconds)
            retryInitialDelaySeconds *= retryDelayFactor
        # end while

        if not self.conn:
            NTcodeerror("Failed to connect to DB")
            return True
        # end if

        self.metadata.bind = self.engine
        self.sessionUpperCase = sessionmaker(bind=self.engine)
        self.session = self.sessionUpperCase() # instantiation.
        if not self.session:
            nTerror("DB connection failed because session was not retrieved.")
            return True

        self.dBversion = self.session.execute(func.version()).fetchone()[0]
#        nTmessage("Now connected on host %s to database %s schema %s by user %s" % (self.host, self.db, self.schema, self.user))
        nTdebug("Connection CgenericSql: %20s %10s %10s %10s" % (self.host, self.db, self.schema, self.user))
        if self.db_type == DB_TYPE_MYSQL:
            dBversionTuple = self.dBversion.split('.')
            dBversionFloat = float(dBversionTuple[0] + '.' + dBversionTuple[1])
            if dBversionFloat < 5.1:
                nTerror("Need to have at least version 5.1.x of MySql installed")
                return True
            # end if
        # end if
    # end def

    def loadTable(self, tableName):
        'Loading table.'
        warnings.simplefilter('ignore', category=SAWarning) # keep log interesting.
        #warnings.filters.insert(0, ('ignore', None, SAWarning, None, 0))

        self[tableName] = Table(tableName, self.metadata, autoload=True, schema=self.schema)
        return self[tableName]

    def autoload(self):
        """Return True on error"""
        for tableName in self.tableNameList:
#            nTdebug("Loading table %s" % tableName)
            self[tableName] = Table(tableName, self.metadata, autoload=True, schema=self.schema)
#            table = self[tableName]
#            columnNameList = [c.name for c in table.columns]
#            nTdebug("Loaded table %s with columns %s" % (tableName, columnNameList))
        #The MetaData object supports some handy methods, such as getting a list of Tables in the order (or reverse) of their dependency:
#        with warnings.catch_warnings(): 
# can't use the python 2.5 feature since it's not always enabled. Update when no longer supporting 2.5
        if False: # DEFAULT: False
            warnings.simplefilter("ignore")
#            for _t in self.metadata.table_iterator(reverse=False): # obsoleted
            for t in self.metadata.sorted_tables:                
                nTdebug("Table: %s" % t.name)
            warnings.simplefilter("default") # reset to default warning behavior.
#            warnings.warn("depreciated 123", DeprecationWarning)
        # end if
    # end def
# end class

class CsqlAlchemy(CgenericSql): # pylint: disable=R0902
    """AKA the Queen's English"""
    def __init__(self, db_type=DB_TYPE_DEFAULT, host='localhost', user='nrgcing1', passwd='4I4KMS', 
                    unix_socket='/tmp/mysql.sock', db="nrgcing", schema=None, echo=False):
#        nTdebug("Initializing CsqlAlchemy with user/db: %s/%s" % (user,db))
        CgenericSql.__init__(self, db_type=db_type, host=host, user=user, passwd=passwd, 
                    unix_socket=unix_socket, db=db, schema=schema, echo=echo)
        # be explicit here to take advantage of code analysis.
        self.tableNameList = """
            cingentry cingchain cingresidue cingatom 
            drlist dr 
            cingresonancelist cingresonancelistperatomclass 
            cingsummary entry_list_selection residue_list_selection 
        """.split()
#        self.tableNameList = [ 'casdcing.'+x for x in self.tableNameList]
#        self.entry = None
        self.cingentry = None
        self.cingchain = None
        self.cingresidue = None
        self.cingatom = None
        self.cingresonancelist = None
        self.cingresonancelistperatomclass = None
        self.cdrlist = None
        self.cdr = None
        self.cingsummary = None
        self.entry_list_selection = None
        self.residue_list_selection = None

        self.levelIdResidue = "residue"  # mirrors WI setup.
        self.levelIdAtom = "atom"
    # end def

    def autoload(self):
        """Return True on error"""
        CgenericSql.autoload(self)
        if self.cingentry == None:
            nTerror("Failed to retrieve the cingentry table")
            return True
        # end if
        if self.entry_list_selection == None:
            nTerror("Failed to retrieve the entry_list_selection table")
            return True
        # end if
        if self.residue_list_selection == None:
            nTerror("Failed to retrieve the residue_list_selection table")
            return True
        # end if
    # end def
# end class

def printResult(result):
    'Convenience method.'
    if result.rowcount < 1:
        return
    for row in result:
        nTmessage(str(row))
    # end for
# end def

if __name__ == '__main__':
    cing.verbosity = verbosityDebug
    db_name = PDBJ_DB_NAME
    user_name = PDBJ_DB_USER_NAME
    s = NRG_DB_NAME
    if False:
        db_name = CASD_DB_NAME
        user_name = CASD_DB_USER_NAME        

    csql = CsqlAlchemy(user=user_name, db=db_name,schema=s)
    csql.connect()
    csql.autoload()
# end if