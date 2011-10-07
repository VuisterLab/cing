"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_sqlAlchemy.py

Fails if MySql backends are absent.
"""
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG import CASD_DB_NAME
from cing.NRG import CASD_DB_USER_NAME
from cing.NRG import DEV_NRG_DB_SCHEMA
from cing.NRG import DEV_NRG_DB_USER_NAME
from cing.NRG import NRG_DB_SCHEMA
from cing.NRG import NRG_DB_USER_NAME
from cing.NRG import PDBJ_DB_NAME
from cing.PluginCode.sqlAlchemy import CsqlAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref
from sqlalchemy.orm import relation
from sqlalchemy.schema import Column
from sqlalchemy.schema import ForeignKey
from sqlalchemy.sql.expression import select
from sqlalchemy.types import Integer, String
from unittest import TestCase
import unittest

Base = declarative_base()

class User(Base): # pylint: disable=R0903
    'Simple class for testing.'
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)
#    in_recoord = Column(Integer)

#    def __init__(self, name, fullname, password, in_recoord=None):
    def __init__(self, name, fullname, password):
        self.name=name
        self.fullname=fullname
        self.password=password
#        self.in_recoord=in_recoord
    def __repr__(self):
#        return "<User('%s','%s', '%s', '%s')>" % (self.name, self.fullname, self.password, self.in_recoord)
        return "<User('%s','%s', '%s')>" % (self.name, self.fullname, self.password)

# pylint: disable=R0903
class Address(Base):
    'Test class for adding to db'
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relation(User, backref=backref('addresses', order_by=id))

    def __init__(self, email_address):
        self.email_address = email_address

    def __repr__(self):
        return "<Address('%s')>" % self.email_address

class AllChecks(TestCase):
    'Test case'
    
    def _test_SqlAlchemyWithPdbjCing(self):
        'Watch out with executing this test routine. It kills.'
        pdb_id = '1brv'

        if True: # default: True
            db_name = PDBJ_DB_NAME
            user_name = DEV_NRG_DB_USER_NAME
            schema = DEV_NRG_DB_SCHEMA
        else:
            db_name = CASD_DB_NAME
            user_name = CASD_DB_USER_NAME

        csql = CsqlAlchemy(user=user_name, db=db_name,schema=schema)

        if csql.connect():
            nTerror("Failed to connect to DB")
            return True
        csql.autoload()

        execute = csql.conn.execute
        centry = csql.cingentry

        # WATCH OUT WITH THE BELOW COMMANDS.
        #result = csql.conn.execute(centry.delete())
        result = execute(centry.delete().where(centry.c.pdb_id == pdb_id))
        if result.rowcount:
            nTdebug("Removed original entries numbering: %s" % result.rowcount)
        else:
            nTdebug("No original entry present yet.")

        result = csql.conn.execute(centry.insert().values(
            pdb_id=pdb_id,
            name=pdb_id,
            is_multimeric=False))

#        entry_id_list = result.last_inserted_ids() # fails for postgres version I have.
#        entry_id_list = result.inserted_primary_key() # wait for this new feature
#        nTdebug( "Last row id: " + str(result.lastrowid) ) # Always one
        entry_id_list = execute(select([centry.c.entry_id]).where(centry.c.pdb_id==pdb_id)).fetchall()
        self.assertNotEqual(entry_id_list,None,"Failed to get the id of the inserted entry but got: %s" % entry_id_list)
        self.assertEqual(len( entry_id_list ), 1,"Failed to get ONE id of the inserted entry but got: %s" % entry_id_list)
        entry_id = entry_id_list[0][0]
        nTdebug("Inserted entry id %s" % entry_id)


    def _test_SqlAlchemy(self):
        'Watch out with this method, it kills.'
        if True: # default: True
            db_name = PDBJ_DB_NAME
            user_name = NRG_DB_USER_NAME
            schema = NRG_DB_SCHEMA
        else:
            db_name = CASD_DB_NAME
            user_name = CASD_DB_USER_NAME

        csql = CsqlAlchemy(user=user_name, db=db_name,schema=schema)
        self.assertFalse(csql.connect())
        if not csql.conn:
            nTerror("Failed to connect in %s" % getCallerFileName())
            return
        nTmessage("Connected to RDB now.")
        if True:
            return # Just be sure to not continue here. 
    
#        users_table = Table('users', csql.metadata,
#            Column('id', Integer, primary_key = True),
#            Column('name', String(50)),
#            Column('fullname', String(50)),
#            Column('password', String(50))
#            )
#        csql.metadata.create_all(csql.engine)  # may be called multiple times.
#        mapper(User, users_table)
#        ed_user = User('ed', 'Ed Jones', 'edspassword')

#        _user_table = User.__table__
        metadata = Base.metadata

        ed_user = User('ed', 'Ed Jones', 'edspassword')
        csql.session.add(ed_user) # does NOT flush yet. Not autocommiting.

        our_user = csql.session.query(User).filter_by(name='ed').first()
        nTdebug( str(our_user) )
        nTdebug( "ed_user is our_user: %s" % (ed_user is our_user)) # Will be false only if it already existed?

        csql.session.add_all([
             User('wendy', 'Wendy Williams', 'foobar'),
             User('mary', 'Mary Contrary', 'xxg527'),
             User('fred', 'Fred Flinstone', 'blah')])

        ed_user.password = 'f8s7ccs'
        nTdebug(str(csql.session.dirty)) # shows bad data.je
        nTdebug(str(csql.session.new)) # shows unflushed data.
        csql.session.commit()
        nTdebug(str(ed_user)) # shows unflushed data.

#        column = Column('extraCol', String(50))
#        user_table.append_column(column) # fails to stick around. but can be done outside??
        metadata.create_all(csql.engine)
#        ed_user.extraCol = 'xyz'
#        csql.session.commit() # fails to make the append stick.
        nTdebug(str(ed_user))
#        nTdebug(ed_user.extraCol)

    def _test_SqlAlchemy_2(self):
        """Testing SqlAlchemy setup.
        Only enable when db is installed, configured and running"""
        pdb_id = '1brv'
        res_number = 171

        csql = CsqlAlchemy()
        self.assertFalse( csql.connect() )
        csql.autoload()

        execute = csql.conn.execute
        centry = csql.entry
        cchain = csql.chain
        cresidue = csql.residue
        #result = csql.conn.execute(centry.delete())
        result = execute(centry.delete().where(centry.c.pdb_id == pdb_id))
        if result.rowcount:
            nTdebug("Removed original entries numbering: %s" % result.rowcount)
        else:
            nTdebug("No original entry present yet.")

        #ins = centry.insert().values(entry_id=1,pdb_id='1brv')
        #nTdebug( ins )
        #ins.compile().params # show the set parameters/values.
        #result = csql.conn.execute(centry.insert().values(entry_id=1,pdb_id='1brv'))
        result = csql.conn.execute(centry.insert().values(pdb_id=pdb_id, name=pdb_id))
        entry_id = result.last_inserted_ids()[0]
        nTdebug("Inserted entry %s" % entry_id)

        result = csql.conn.execute(cchain.insert().values(entry_id=entry_id))
        chain_id = result.last_inserted_ids()[0]
        nTdebug("Inserted chain %s" % chain_id)

        #for j in range(1):
        #    for i in range(1):
        result = csql.conn.execute(cresidue.insert().values(entry_id=entry_id, chain_id=chain_id),
                    number=res_number)
        residue_id = result.last_inserted_ids()[0]
        nTdebug("Inserted residue %s" % residue_id)

        result = csql.conn.execute(cresidue.update().where(cresidue.c.residue_id == residue_id).values(number=res_number+999))
        nTdebug("Updated residues numbering %s" % result.rowcount)

        # Needed for the above hasn't been autocommitted.
        csql.session.commit()

        for residue in csql.session.query(cresidue):
            nTdebug("New residue number %s" % residue.number)

        for instance in csql.session.query(centry):
            nTdebug( "Retrieved entry instance: %s" % instance.pdb_id )


if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
