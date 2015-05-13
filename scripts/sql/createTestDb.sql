-- A situation where there are to tables with the same name in the same database but in a different schema

create role me LOGIN CREATEDB SUPERUSER;
create role you LOGIN CREATEDB SUPERUSER;

SET AUTOCOMMIT=1;

DROP TABLE IF EXISTS schema_yours.entry;
DROP TABLE IF EXISTS schema_mine.entry;

DROP SCHEMA IF EXISTS schema_yours;
DROP SCHEMA IF EXISTS schema_mine;

CREATE SCHEMA schema_yours AUTHORIZATION you;
CREATE SCHEMA schema_mine  AUTHORIZATION me;


-- entry
CREATE TABLE schema_yours.entry ( entry_id SERIAL UNIQUE, pdb_id VARCHAR(255) );
CREATE TABLE schema_mine.entry ( entry_id SERIAL UNIQUE, pdb_id VARCHAR(255) );

insert into schema_yours.entry(pdb_id) VALUES ( '1brv' );
insert into schema_mine.entry(pdb_id) VALUES ( '1brw' );
insert into schema_mine.entry(pdb_id) VALUES ( '1brx' );

select * from schema_yours.entry;
select * from schema_mine.entry;

