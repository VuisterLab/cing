from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.PluginCode.required.reqOther import SQL_STR

if True: # for easy blocking of data, preventing the code to be resorted with imports above.
    from cing.Libs.NTutils import ImportWarning
    from cing.Libs.NTutils import switchOutput
    switchOutput(False)
    try:
        import MySQLdb
    except:
        switchOutput(True)
        raise ImportWarning(SQL_STR)
    finally:
        switchOutput(True)
    NTmessage('Using MySQLdb')

class genericSql():
    "Class for connecting to any MySql database."
    def __init__(self, host = 'localhost', user = 'anonymous', passwd = 'nobody@gmail.com', unix_socket = '/tmp/mysql.sock', db = "mydb"):
        NTdebug("Initializing genericSql")
        self.host = host
        self.user = user
        self.passwd = passwd
        self.unix_socket = unix_socket
        self.db = db
        self.conn = None
        "Connection object to database if connected it is None"
        self.cursor = None
        "Cursor of connection"

    def connect(self):
        "Return True on error"
        try:
            self.conn = MySQLdb.connect(
                             host = self.host,
                             user = self.user,
                             passwd = self.passwd,
                             unix_socket = self.unix_socket,
                             db = self.db)
            self.cursor = self.conn.cursor ()
        except MySQLdb.Error, e:
            self.conn = None
            NTerror("Mysql connection failed: %d: %s" % (e.args[0], e.args[1]))
            return True

        self.cursor.execute("SELECT VERSION()")
        row = self.cursor.fetchone()
        version = row[0]
        NTmessage("Now connected to Mysql %s database %s by %s" % (version, self.db, self.user))

class cingSql(genericSql):
    """AKA the Queen's English"""
    def __init__(self, host = 'localhost', user = 'nrgcing1', passwd = '4I4KMS', unix_socket = '/tmp/mysql.sock', db = "nrgcing"):
        genericSql.__init__(self, host = host, user = user, passwd = passwd, unix_socket = unix_socket, db = db)
        NTdebug("Initialized cingSql")

    def getNextSequenceId(self, table_name = 'entry'):
        """Reserve a new id in the sequence generator table. Get unique sequence id from db.
     Watch out this will only work up to the number of times that int can handle for
     int(32) that is: 2 billion (2,147,483,648). Using proprietary Oracle method.
     * @return The next id which is kept in the database and incremented on each call.

     Return None on error.
     On error the transactions are not committed.
     """

        if not self.conn:
            NTerror("Failed getNextSequenceId because not connected")
            return

        id = None
        try:
            self.cursor.execute("UPDATE " + table_name + "_id SET id=LAST_INSERT_ID(id+1)")
            NTdebug("Number of rows updated: %d" % self.cursor.rowcount)
            if self.cursor.rowcount != 1:
                NTerror("Failed getNextSequenceId because failed to increment id for table: %s" % table_name)
                return None

            self.cursor.execute("SELECT LAST_INSERT_ID()")
            NTdebug("Number of rows retrieved: %d" % self.cursor.rowcount)
            if self.cursor.rowcount != 1:
                NTerror("Failed getNextSequenceId because failed to select last id for table: %s" % table_name)
                return None
            row = self.cursor.fetchone()
            id = int(row[0])
            self.conn.commit() # Since autocommit is off.
        except MySQLdb.Error, e:
            NTerror("Mysql connection failed: %d: %s" % (e.args[0], e.args[1]))
            return
        return id

    def insertEntry(self, pdb_id, bmrb_id):
        """Reserve a new id in the sequence generator table. Get unique sequence id from db.
     Watch out this will only work up to the number of times that int can handle for
     int(32) that is: 2 billion (2,147,483,648). Using proprietary Oracle method.
     * @return The next id which is kept in the database and incremented on each call.

     Return None on error.
     On error the transactions are not committed.
     """

        if not self.conn:
            NTerror("Failed insertEntry because not connected")
            return

        id = self.getNextSequenceId()
        if not id:
            NTerror("Failed insertEntry because failed getNextSequenceId")
            return

#        try:
#            self.cursor.execute("UPDATE " + table_name + "_id SET id=LAST_INSERT_ID(id+1)")
#            NTdebug("Number of rows updated: %d" % self.cursor.rowcount)
#            if self.cursor.rowcount != 1:
#                NTerror("Failed getNextSequenceId because failed to increment id for table: %s" % table_name)
#                return None
#
#            self.cursor.execute("SELECT LAST_INSERT_ID()")
#            NTdebug("Number of rows retrieved: %d" % self.cursor.rowcount)
#            if self.cursor.rowcount != 1:
#                NTerror("Failed getNextSequenceId because failed to select last id for table: %s" % table_name)
#                return None
#            row = self.cursor.fetchone()
#            id = int(row[0])
#            self.conn.commit() # Since autocommit is off.
#        except MySQLdb.Error, e:
#            NTerror("Mysql connection failed: %d: %s" % (e.args[0], e.args[1]))
#            return
#        return id

class cEntry():
    """cing type of entry for MySql database"""
    def __init__(self, ):
#        self.entry_id                       INT              NOT NULL PRIMARY KEY,
#        self.bmrb_id                        INT,
#        self.pdb_id                         CHAR(4),
#        self.is_solid                       BOOLEAN DEFAULT NULL,
#        self.is_paramagnetic                BOOLEAN DEFAULT NULL,
#        self.is_membrane                    BOOLEAN DEFAULT NULL,
#        self.is_multimeric                  BOOLEAN DEFAULT NULL,
#        self.in_recoord                     BOOLEAN DEFAULT NULL,
#        self.in_dress                       BOOLEAN DEFAULT NULL,
#        self.rog                            INT DEFAULT NULL
        pass


class cSql(genericSql):
    """AKA the Queen's English"""
    def __init__(self, host = 'localhost', user = 'nrgcing1', passwd = '4I4KMS', unix_socket = '/tmp/mysql.sock', db = "nrgcing"):
        genericSql.__init__(self, host = host, user = user, passwd = passwd, unix_socket = unix_socket, db = db)
        NTdebug("Initialized cingSql")
