

-- select the vacuum settings on/off.
select * from pg_settings where name like 'autovacuum';
-- select all settings from a category within.
select * from pg_settings where category like 'Autovacuum';

-- max_locks_per_transaction needs to be 256 min by pdbj recommendations
select * from pg_settings where category like 'Resource%';
