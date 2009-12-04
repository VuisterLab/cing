from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTzap
from cing.PluginCode.Whatif import Whatif
from cing.PluginCode.required.reqOther import SQL_STR
from cing.PluginCode.required.reqProcheck import PROCHECK_STR
from cing.PluginCode.required.reqProcheck import gf_CHI12_STR
from cing.PluginCode.required.reqProcheck import gf_CHI1_STR
from cing.PluginCode.required.reqProcheck import gf_PHIPSI_STR
from cing.PluginCode.required.reqProcheck import gf_STR
from cing.PluginCode.required.reqWhatif import OMECHK_STR
from cing.PluginCode.required.reqWhatif import VALUE_LIST_STR
from cing.PluginCode.required.reqWhatif import WHATIF_STR
from cing.core.ROGscore import rogScoreStr
from cing.core.constants import DR_STR
from cing.core.constants import VIOL1_STR
from cing.core.constants import VIOL3_STR
from cing.core.constants import VIOL5_STR
import warnings

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
    def __init__(self, host = 'localhost', user = 'nobody@noaddress.no', passwd = '', unix_socket = '/tmp/mysql.sock', db = "", echo = False):
        NTdebug("Initializing cgenericSql")
        self.host = host
        self.user = user
        self.passwd = passwd
        self.unix_socket = unix_socket
        self.db = db
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
        self.engine = create_engine('mysql://%s/%s?user=%s&unix_socket=%s&passwd=%s' % (self.host,
             self.db,
             self.user,
             self.unix_socket,
             self.passwd
            ), echo = self.echo)
        self.conn = self.engine.connect()
        if not self.conn:
            NTerror("Mysql connection failed")
            return True

        self.metadata.bind = self.engine
        self.Session = sessionmaker(bind = self.engine)
        self.session = self.Session() # instantiation.
        if not self.session:
            NTerror("Mysql connection failed because session was not retrieved.")
            return True

        self.dBversion = self.session.execute(func.version()).fetchone()[0]
        dBversionTuple = self.dBversion.split('.')
        dBversionFloat = float(dBversionTuple[0]+'.'+dBversionTuple[1])
        NTmessage("Now connected to Mysql %s database %s by %s" % (self.db, self.dBversion, self.user))
        if dBversionFloat < 5.1:
            NTerror("Need to have at least version 5.1.x of MySql installed")
            return True

    def autoload(self):
        """Return True on error"""
        for tableName in self.tableNameList:
            NTdebug("Loading table %s" % tableName)
            self[tableName] = Table(tableName, self.metadata, autoload = True)
            table = self[tableName]
            columnNameList = [c.name for c in table.columns]
            NTdebug("Loaded table %s with columns %s" % (tableName, columnNameList))
        #The MetaData object supports some handy methods, such as getting a list of Tables in the order (or reverse) of their dependency:
#        with warnings.catch_warnings(): # can't use the python 2.5 feature since it's not always enabled. TODO: update when no longer supporting 2.5
        if True:
            warnings.simplefilter("ignore")
            for t in self.metadata.table_iterator(reverse=False):
                NTdebug("Table: %s" % t.name)
            warnings.simplefilter("default") # reset to default warning behaviour.
#            warnings.warn("deprecated 123", DeprecationWarning)


class csqlAlchemy(cgenericSql):
    """AKA the Queen's English"""
    def __init__(self, host = 'localhost', user = 'nrgcing1', passwd = '4I4KMS', unix_socket = '/tmp/mysql.sock', db = "nrgcing", echo=False):
        cgenericSql.__init__(self, host = host, user = user, passwd = passwd, unix_socket = unix_socket, db = db,echo=False)
        NTdebug("Initialized csqlAlchemy")
        # be explicit here to take advantage of code analysis.
        self.tableNameList = ['entry', 'chain', 'residue' ]
        self.entry = None
        self.chain = None
        self.residue = None

        self.levelIdResidue     = "residue"  # mirrors WI setup.
        self.levelIdAtom        = "atom"

        self.mapCing = NTdict()
        """Maps a CING tuple (level_id, key1,,,keyN) to a SQL tuple (table_name, column_name)"""
        # CING
        self.mapCing[ ( self.levelIdResidue, rogScoreStr, OMECHK_STR ) ] = ( self.levelIdResidue, 'omega_dev_av_all' )
        self.mapCing[ ( self.levelIdResidue, DR_STR, VIOL1_STR ) ] = ( self.levelIdResidue, 'dis_c1_viol' )
        self.mapCing[ ( self.levelIdResidue, DR_STR, VIOL3_STR ) ] = ( self.levelIdResidue, 'dis_c3_viol' )
        self.mapCing[ ( self.levelIdResidue, DR_STR, VIOL5_STR ) ] = ( self.levelIdResidue, 'dis_c5_viol' )

        # WHAT IF
        wiChkIdList = NTzap(Whatif.nameDefs,0)
        for checkId in wiChkIdList:
            columnName = 'wi_' + checkId
            self.mapCing[ ( self.levelIdResidue, WHATIF_STR, checkId, VALUE_LIST_STR ) ] = ( self.levelIdResidue, columnName )

        # PROCHECK
        pcChkIdList = ( gf_STR, gf_PHIPSI_STR, gf_CHI12_STR, gf_CHI1_STR )
        for checkId in pcChkIdList:
            columnName = 'pc_' + checkId
            self.mapCing[ ( self.levelIdResidue, PROCHECK_STR, checkId, VALUE_LIST_STR ) ] = ( self.levelIdResidue, columnName )
        NTdebug("mapCing: %s" % self.mapCing)
    def autoload(self):
        """Return True on error"""
        cgenericSql.autoload(self)
        if not self.entry:
            NTerror("Failed to retrieve the entry table")
            return True