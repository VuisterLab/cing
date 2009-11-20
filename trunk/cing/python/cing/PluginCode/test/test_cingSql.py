"""
Unit test execute as:
python $CINGROOT/python/cing/Libs/test/test_cingSql.py
"""

from cing import verbosityDebug
from cing.Libs.NTutils import NTdebug
from cing.PluginCode.cingSql import cingSql
from cing.PluginCode.sqlAlchemy import csqlAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer
from sqlalchemy.types import String
from unittest import TestCase
import cing
import unittest

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)
    in_recoord = Column(Integer)

    def __init__(self, name, fullname, password, in_recoord=None):
#    def __init__(self, name, fullname, password):
        self.name=name
        self.fullname=fullname
        self.password=password
        self.in_recoord=in_recoord
    def __repr__(self):
        return "<User('%s','%s', '%s', '%s')>" % (self.name, self.fullname, self.password, self.in_recoord)

#class Address(Base):
#    __tablename__ = 'addresses'
#    id = Column(Integer, primary_key=True)
#    email_address = Column(String, nullable=False)
#    user_id = Column(Integer, ForeignKey('users.id'))
#
#    user = relation(User, backref=backref('addresses', order_by=id))
#
#    def __init__(self, email_address):
#        self.email_address = email_address
#
#    def __repr__(self):
#        return "<Address('%s')>" % self.email_address

class AllChecks(TestCase):

    def tttest_CingSql(self):
        cSql = cingSql()
        self.assertFalse(cSql.connect())
        nextId = cSql.getNextSequenceId()
        NTdebug("Got nextId: %d" % nextId)
        self.assertTrue(nextId)

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

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()


