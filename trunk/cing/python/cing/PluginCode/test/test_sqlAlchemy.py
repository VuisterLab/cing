"""
Unit test execute as:
python $CINGROOT/python/cing/Libs/test/test_sqlAlchemy.py

Fails if MySql backends are absent.
"""
from cing import verbosityDebug
from cing.Libs.NTutils import NTdebug
from cing.PluginCode.sqlAlchemy import csqlAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relation
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String
from unittest import TestCase
import cing
import unittest
"""
Unit test execute as:
python $CINGROOT/python/cing/Libs/test/test_cingSql.py
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

    def ttest_SqlAlchemy(self):
        """Only enable when db is installed, configured and running"""
        pdb_id = '1brv'
        res_number = 171

        csql = csqlAlchemy()
        self.assertFalse( csql.connect() )
        csql.autoload()

        execute = csql.conn.execute

        #result = csql.conn.execute(csql.entry.delete())
        result = execute(csql.entry.delete().where(csql.entry.c.pdb_id == pdb_id))
        if result.rowcount:
            NTdebug("Removed original entries numbering: %s" % result.rowcount)
        else:
            NTdebug("No original entry present yet.")

        #ins = csql.entry.insert().values(entry_id=1,pdb_id='1brv')
        #print ins
        #ins.compile().params # show the set parameters/values.
        #result = csql.conn.execute(csql.entry.insert().values(entry_id=1,pdb_id='1brv'))
        result = csql.conn.execute(csql.entry.insert().values(pdb_id=pdb_id, name=pdb_id))
        entry_id = result.last_inserted_ids()[0]
        NTdebug("Inserted entry %s" % entry_id)

        result = csql.conn.execute(csql.chain.insert().values(entry_id=entry_id))
        chain_id = result.last_inserted_ids()[0]
        NTdebug("Inserted chainZZ %s" % chain_id)

        #for j in range(1):
        #    for i in range(1):
        result = csql.conn.execute(csql.residue.insert().values(entry_id=entry_id, chain_id=chain_id),
                    number=res_number)
        residue_id = result.last_inserted_ids()[0]
        NTdebug("Inserted residue %s" % residue_id)

        result = csql.conn.execute(csql.residue.update().where(csql.residue.c.residue_id == residue_id).values(number=res_number+999))
        NTdebug("Updated residues numbering %s" % result.rowcount)

        # Needed for the above hasn't been autocommitted.
        csql.session.commit()

        for residue in csql.session.query(csql.residue):
            NTdebug("New residue number %s" % residue.number)

        for instance in csql.session.query(csql.entry):
            print instance.pdb_id


if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
