'''
Created on Jan 15, 2010\
From: http://www.tylerlesmann.com/2009/apr/27/copying-databases-across-platforms-sqlalchemy/
@author: Tyler Lesmann

Usage: python $CINGROOT/cing/python/Libs/RDBpuller.py -f source_server -t destination_server table [table ...]
    -f, -t = driver://user[:password]@host[:port]/database
'''
import getopt
import sys
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

def make_session(connection_string):
    engine = create_engine(connection_string, echo=False, convert_unicode=True)
    sessionUpperCaseStart = sessionmaker(bind=engine)
    return sessionUpperCaseStart(), engine

def pull_data(from_db, to_db, tables):
    source, sengine = make_session(from_db)
    smeta = MetaData(bind=sengine)
    destination, dengine = make_session(to_db)

    for table_name in tables:
        print 'Processing', table_name
        print 'Pulling schema from source server'
        table = Table(table_name, smeta, autoload=True)
        print 'Creating table on destination server'
        table.metadata.create_all(dengine)
        newRecord = quick_mapper(table)
        columns = table.columns.keys()
        print 'Transferring records'
        for record in source.query(table).all():
            data = dict(
                [(str(column), getattr(record, column)) for column in columns]
            )
            destination.merge(newRecord(**data))
    print 'Committing changes'
    destination.commit()

def print_usage():
    myName = sys.argv[0]
    print """
Usage: %s -f source_server -t destination_server table [table ...]
    -f, -t = driver://user[:password]@host[:port]/database

Example: %s -f oracle://someuser:PaSsWd@db1/TSH1 \\
    -t mysql://root@db2:3307/reporting table_one table_two

Example: %s -f oracle://someuser:PaSsWd@db1/TSH1 \\
    -t mysql://root@db2:3307/reporting table_one table_two
    """ % (myName, myName, myName)

def quick_mapper(table):
    base = declarative_base()
    # pylint: disable=W0232
    # pylint: disable=R0903
    class GenericMapper(base):
        __table__ = table
    return GenericMapper

if __name__ == '__main__':
    optlist, tables = getopt.getopt(sys.argv[1:], 'f:t:')

    options = dict(optlist)
    if '-f' not in options or '-t' not in options or not tables:
        print_usage()
        raise SystemExit, 1

    pull_data(
        options['-f'],
        options['-t'],
        tables,
    )