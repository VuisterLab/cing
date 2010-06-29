-- Use by loading this function set in by:
-- \i /Users/jd/workspace35/cing/python/cing/NRG/sql/learningPgSql.sql


-- returns zero for succes and one for error.
CREATE OR REPLACE FUNCTION createDb(schemaName varchar) RETURNS integer AS $$
DECLARE
--    schemaName varchar := 'testje';
    result integer := 0;
BEGIN
	RAISE NOTICE 'schemaName here is %', schemaName;

	DROP TABLE IF EXISTS schemaName.entry;
	DROP SCHEMA IF EXISTS schemaName;

--	CREATE SCHEMA schemaName AUTHORIZATION schemaName;


	-- entry
--	CREATE TABLE schemaName.entry ( entry_id SERIAL UNIQUE, pdb_id VARCHAR(255) );

--	insert into schemaName.entry(pdb_id) VALUES ( '1brv' );

--	select * from schemaName.entry;

    RETURN result;
END;
$$ LANGUAGE plpgsql;

select createDb('testSchema');
