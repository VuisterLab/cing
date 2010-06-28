"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_sqlAlchemy.py

Fails if MySql backends are absent.
"""
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.sqlAlchemy import csqlAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref
from sqlalchemy.orm import relation
from sqlalchemy.schema import Column
from sqlalchemy.schema import ForeignKey
from sqlalchemy.sql.expression import select
from sqlalchemy.types import Integer, String
from unittest import TestCase
import unittest
"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_sqlAlchemy.py
"""


Base = declarative_base()

class User(Base):
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
        return "<User('%s','%s', '%s', '%s')>" % (self.name, self.fullname, self.password)

class Address(Base):
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

    def tttest_SqlAlchemyWithNrgCing(self):
        pdb_id = '1brv'

        csql = csqlAlchemy()
        if csql.connect():
            NTerror("Failed to connect to DB")
            return True
        csql.autoload()

        execute = csql.conn.execute
        centry = csql.entry

        # WATCH OUT WITH THE BELOW COMMANDS.
        #result = csql.conn.execute(centry.delete())
        result = execute(centry.delete().where(centry.c.pdb_id == pdb_id))
        if result.rowcount:
            NTdebug("Removed original entries numbering: %s" % result.rowcount)
        else:
            NTdebug("No original entry present yet.")

        result = csql.conn.execute(centry.insert().values(
            pdb_id=pdb_id,
            name=pdb_id,
            is_multimeric=False))

#        entry_id_list = result.last_inserted_ids() # fails for postgres version I have.
#        entry_id_list = result.inserted_primary_key() # wait for this new feature
#        NTdebug( "Last row id: " + str(result.lastrowid) ) # Always one
        entry_id_list = execute(select([centry.c.entry_id]).where(centry.c.pdb_id==pdb_id)).fetchall()
        self.assertNotEqual(entry_id_list,None,"Failed to get the id of the inserted entry but got: %s" % entry_id_list)
        self.assertEqual(len( entry_id_list ), 1,"Failed to get ONE id of the inserted entry but got: %s" % entry_id_list)
        entry_id = entry_id_list[0][0]
        NTdebug("Inserted entry id %s" % entry_id)


    def tttest_SqlAlchemy(self):
        csql = csqlAlchemy()
        self.assertFalse(csql.connect())
#        users_table = Table('users', csql.metadata,
#            Column('id', Integer, primary_key = True),
#            Column('name', String(50)),
#            Column('fullname', String(50)),
#            Column('password', String(50))
#            )
#        csql.metadata.create_all(csql.engine)  # may be called multiple times.
#        mapper(User, users_table)
#        ed_user = User('ed', 'Ed Jones', 'edspassword')

        _user_table = User.__table__
        metadata = Base.metadata

        ed_user = User('ed', 'Ed Jones', 'edspassword')
        csql.session.add(ed_user) # does NOT flush yet. Not autocommiting.

        our_user = csql.session.query(User).filter_by(name='ed').first()
        NTdebug( str(our_user) )
        NTdebug( "ed_user is our_user: %s" % (ed_user is our_user)) # Will be false only if it already existed?

        csql.session.add_all([
             User('wendy', 'Wendy Williams', 'foobar'),
             User('mary', 'Mary Contrary', 'xxg527'),
             User('fred', 'Fred Flinstone', 'blah')])

        ed_user.password = 'f8s7ccs'
        NTdebug(str(csql.session.dirty)) # shows bad data.je
        NTdebug(str(csql.session.new)) # shows unflushed data.
        csql.session.commit()
        NTdebug(str(ed_user)) # shows unflushed data.

#        column = Column('extraCol', String(50))
#        user_table.append_column(column) # fails to stick around. but can be done outside??
        metadata.create_all(csql.engine)
#        ed_user.extraCol = 'xyz'
#        csql.session.commit() # fails to make the append stick.
        NTdebug(str(ed_user))
#        NTdebug(ed_user.extraCol)

    def tttttest_SqlAlchemy(self):
        """Testing SqlAlchemy setup.
        Only enable when db is installed, configured and running"""
        pdb_id = '1brv'
        res_number = 171

        csql = csqlAlchemy()
        self.assertFalse( csql.connect() )
        csql.autoload()

        execute = csql.conn.execute
        centry = csql.entry
        cchain = csql.chain
        cresidue = csql.residue
        #result = csql.conn.execute(centry.delete())
        result = execute(centry.delete().where(centry.c.pdb_id == pdb_id))
        if result.rowcount:
            NTdebug("Removed original entries numbering: %s" % result.rowcount)
        else:
            NTdebug("No original entry present yet.")

        #ins = centry.insert().values(entry_id=1,pdb_id='1brv')
        #NTdebug( ins )
        #ins.compile().params # show the set parameters/values.
        #result = csql.conn.execute(centry.insert().values(entry_id=1,pdb_id='1brv'))
        result = csql.conn.execute(centry.insert().values(pdb_id=pdb_id, name=pdb_id))
        entry_id = result.last_inserted_ids()[0]
        NTdebug("Inserted entry %s" % entry_id)

        result = csql.conn.execute(cchain.insert().values(entry_id=entry_id))
        chain_id = result.last_inserted_ids()[0]
        NTdebug("Inserted chain %s" % chain_id)

        #for j in range(1):
        #    for i in range(1):
        result = csql.conn.execute(cresidue.insert().values(entry_id=entry_id, chain_id=chain_id),
                    number=res_number)
        residue_id = result.last_inserted_ids()[0]
        NTdebug("Inserted residue %s" % residue_id)

        result = csql.conn.execute(cresidue.update().where(cresidue.c.residue_id == residue_id).values(number=res_number+999))
        NTdebug("Updated residues numbering %s" % result.rowcount)

        # Needed for the above hasn't been autocommitted.
        csql.session.commit()

        for residue in csql.session.query(cresidue):
            NTdebug("New residue number %s" % residue.number)

        for instance in csql.session.query(centry):
            NTdebug( "Retrieved entry instance: %s" % instance.pdb_id )


if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
