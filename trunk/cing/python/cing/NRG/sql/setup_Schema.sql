-- Edit and execute:
-- python -u $CINGROOT/python/cing/NRG/runSqlForSchema.py devnrgcing    $CINGROOT/python/cing/NRG/sql/setup_Schema.sql    .

-- create it
create schema casdcing;

-- creating the account
create role casdcing1 LOGIN CREATEDB SUPERUSER PASSWORD '4I4KMS';
-- not needed really...
alter role casdcing1 WITH PASSWORD '4I4KMS'