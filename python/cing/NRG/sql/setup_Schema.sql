-- Edit and execute:
-- python -u $CINGROOT/python/cing/NRG/runSqlForSchema.py devnrgcing    $CINGROOT/python/cing/NRG/sql/setup_Schema.sql    .

-- create it
CREATE SCHEMA casdcing;

-- creating the account
CREATE ROLE casdcing1 LOGIN CREATEDB SUPERUSER PASSWORD '4I4KMS';
-- not needed really...
ALTER ROLE casdcing1 WITH PASSWORD '4I4KMS';

-- Create a 'normal' user pbreader
CREATE ROLE pbreader WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD 'pass';

-- Grant CONNECT to pdbmlplus
GRANT CONNECT ON DATABASE pdbmlplus TO pbreader;

-- Grant USAGE of database
GRANT USAGE ON SCHEMA casdcing TO pbreader;

-- Grant SELECT of any column in all tables in schema nrgcing
CREATE FUNCTION execute(text) returns void AS $BODY$BEGIN EXECUTE $1; END;$BODY$ language plpgsql;
--SELECT execute('GRANT SELECT ON nrgcing.'  || tablename || ' TO pbreader;') FROM pg_tables WHERE schemaname = 'nrgcing';
  SELECT execute('GRANT SELECT ON casdcing.' || tablename || ' TO pbreader;') FROM pg_tables WHERE schemaname = 'casdcing';
  SELECT execute('GRANT SELECT ON casdcing.' || tablename || ' TO wim;')      FROM pg_tables WHERE schemaname = 'casdcing';
GRANT USAGE on SCHEMA casdcing TO wim;
