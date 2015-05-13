-- STEP BY STEP PROCEDURE FOR SETTING UP NEW DB

-- psql
-- Todo: When the db is available anywhere but on the host itself this is a security problem.

-- Notes:
    --  # no escapes for any char but the first.
    -- no backslash escape '\' needed when using double quotes in windows.
-- Getting started help:
--\? from the psql monitor
--\l list db
--\dt' list tables
--\d atom list a table

--create role nrgcing1 LOGIN CREATEDB SUPERUSER;
--alter database nrgcing owner to nrgcing1;

-- create it
create database nrgcing;
create database pdbcing;
create database pdbmlplus;

-- now from command line:
createlang plpgsql nrgcing
createlang plpgsql pdbcing
createlang plpgsql pdbmlplus

-- creating the account
create role nrgcing1 LOGIN CREATEDB SUPERUSER PASSWORD '4I4KMS';
create role pdbcing1 LOGIN CREATEDB SUPERUSER PASSWORD '4I4KMS';

create role nrgcing_reader LOGIN PASSWORD '4I4KMS';
grant select to nrgcing_reader

create role pdbj LOGIN CREATEDB SUPERUSER;
DROP ROLE pdbj_reader;

create role pdbj_reader WITH PASSWORD '4I4KMS' LOGIN CREATEDB SUPERUSER;

alter role nrgcing1 WITH PASSWORD '4I4KMS'
alter role casdcing1 WITH PASSWORD '4I4KMS'

REVOKE ALL ON database pdbmlplus FROM pdbj_reader;
GRANT ALL ON database pdbmlplus TO pdbj_reader;

GRANT ALL ON pdbmlplus.pdbj.brief_summary TO nrgcing1;

REVOKE ALL ON brief_summary FROM pdbj_reader;

-- GRANT REPLICATION SLAVE ON *.* TO 'repl'@'localhost.localdomain' IDENTIFIED BY 'slavepass';

-- create the tables within
mysql -u nrgcing1 -p4I4KMS  nrgcing < $CINGROOT/scripts/sql/createNRG-CING.sql


-- OR load very fast! Dump from 1 database to the next.
mysqldump --opt -u root -p'\!Ecj%Y&R' wattos1 > $SJ/filetosaveto.sql
-- add if speed is needed to begining of file: SET FOREIGN_KEY_CHECKS=0;
-- takes only 4 seconds without optimalization though.
mysql -u wattos1 -p4I4KMS wattos1 < $SJ/filetosaveto.sql
and then copy the mrgrid data itself too
cd /big/jurgen/DB/mrgrid/bfiles
cp -rvfup wattos1/* wattos1

-- just a comment to end the previous command interpreted by jedit as a comment **/

-- More config
set global query_cache_size=16000000;
SHOW STATUS LIKE 'Qcache%';
SHOW VARIABLES LIKE 'have_query_cache';
SHOW VARIABLES LIKE 'query_cache%';




-- JUNK BELOW

# Setttings within Eclips db browser.C:\Documents and Settings\jurgen.WHELK.000\workspace\Wattos\lib\mysql-connector-java-5.0.3-bin.jar
jdbc:mysql://localhost:3306/wattos1
com.mysql.jdbc.Driver

SELECT * FROM entry
ORDER BY entry.name ASC;




