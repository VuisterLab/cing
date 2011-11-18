This directory contains database dumps for PDBj Mine, the back-end relational
database for Protein Data Bank Japan.

The database dump files are only for the use with PostgreSQL
(version 8.4 or above) with some customization
(see below "2. INSTALLING PostgreSQL").

***** 0. PREREQUISITES *****
- A customized installation of PostgreSQL (see below).
- More than 150 GB of hard disk space (as of January, 2010) prepared
  for PostgreSQL. The required disk space will soon exceed 300GB or
  more as the number of PDB entries increases rapidly.

***** 1. DOWNLOADING THE DUMP FILES *****
The dump files are available at the FTP site:
ftp://ftp.pdbj.org/mine
The contents are the following:
-  pdbmlplus.dump
    The dump file of the whole PDBj Mine database.
-  split/pdbmlplus_split.{aa,ab,..}
    The "pdbmlplus.dump" file split into 100MB chunks.
-  weekly/pdbmlplus_weekly.yyyy-mm-dd.gz
    The weekly update of the week of yyyy-mm-dd (e.g., 2010-01-19).

- sql-scripts/ (directory)
    SQL scripts used for defining the PDBj Mine database. These files are
    not necessarily required for the casual user. But interested users can
    study the structure of the database by looking into these files.

All files are updated weekly (except for those under the sql directory).

When loaded, the database will require approximately 150 GB (gigabytes)
of disk space (as of January, 2010).

***** 2. INSTALLING PostgreSQL *****
*** 2-1. General instructions ***
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

*** 2-2. Configuration specific to PDBj Mine ***
The default database role for PDBj Mine is "pdbj" which can be created by
the following (postgresql) command:

% createuser -s pdbj

The default database name for PDBj Mine is "pdbmlplus" which can be created by
the following command:

% createdb pdbmlplus

Also install the PL/pgSQL language to the database pdbmlplus (if it was not yet
installed in the "template1" database):

% createlang plpgsql pdbmlplus

***** 3. POPULATING THE DATABASE FROM SCRATCH *****

You can populate the database by the "pg_restore" command.
If you have downloaded the whole database dump, this can be done as:

JFD: NB ===> The file may be a tar file. Even a tar.gz file I come to see.
% pg_restore -d pdbmlplus pdbmlplus.dump

Alternatively, if you have downloaded the split dump files, do as:

% cat pdbmlplus_split.* | pg_restore -d pdbmlplus

****** 4. POPULATING THE DATABASE FOR WEEKLY UPDATE *****
It is assumed that you have already populated the database from scratch
following the above prescription (POPULATING THE DATABASE FROM SCRATCH).
Use the psql command for updating the entries.

% gunzip < pdbmlplus_weekly.yyyy-mm-dd.gz | psql pdbmlplus pdbj

This dump file (an SQL script) only contains the data of updated and new
entries of the week.  It also deletes obsolete entries.

If you have any problems or questions, please ask us using the form at
http://www.pdbj.org/pdbj_contact.html

Protein Data Bank Japan
http://www.pdbj.org/
