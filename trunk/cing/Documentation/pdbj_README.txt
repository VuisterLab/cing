*** This is document is NOT complete yet. ***

This directory contains database dumps for PDBj Mine, the backend relational
database for Protein Data Bank Japan.

1. INSTALLING PostgreSQL

To use the dump files, you need to install PostgreSQL (version 8.4 or above).
http://www.postgresql.org/

When installing PostgreSQL, you need to modify a line in the header file 
src/include/pg_config_manual.h under the PostgreSQL source file directory. 
That is, change the line

#define NAMEDATALEN 64

to

#define NAMEDATALEN 256

In addition, you need to configure with libxml enabled.
This can be done as

% ./configure --with-libxml

when you configure PostgreSQL.

Then, follow the PostgreSQL manual for installation and server configuration.
After installation, edit the configuration file of PostgreSQL 
(${PGDATA}/postgresql.conf) appropriately. 
In particular, you might need to increase the parameter
"max_locks_per_transaction" to a large value (say, 256).

2. POPULATING THE DATABASE FROM SCRATCH

The default database role for PDBj Mine is "pdbj" which can be created by
the following (postgresql) command:

% createuser -s pdbj

The default database name for PDBj Mine is "pdbmlplus" which can be created by
the following command:

% createdb pdbmlplus

Also install the PL/pgSQL language to the database pdbmlplus (if it was not yet
installed in the "template1" database):

% createlang plpgsql pdbmlplus

Then, you can populate the database by the "pg_restore" command.

% pg_restore -d pdbmlplus pdbmlplus.dump

