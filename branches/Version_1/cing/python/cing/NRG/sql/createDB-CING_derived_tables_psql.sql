--
-- SQL Definitions for creating tables that are normally derived but if full DB isn't loaded can be generated
-- here as dummy tables. Serves little purpose as most other code really assumes pdbj's pdbmlplus schema to exist.
--     Jurgen F. Doreleijers
--     CMBI, Radboud University Nijmegen, the Netherlands.
--
-- Notes:
-- * Run by command like:
-- python -u $CINGROOT/python/cing/NRG/runSqlForSchema.py nrgcing    $CINGROOT/python/cing/NRG/sql/createDB-CING_derived_tables_psql.sql .

-- Only now that the tables have been removed can the schema be removed.
DROP TABLE IF EXISTS casdcing.cingsummary            CASCADE;
DROP TABLE IF EXISTS casdcing.entry_list_selection   CASCADE;
DROP TABLE IF EXISTS casdcing.residue_list_selection CASCADE;

CREATE table casdcing.cingsummary
(
    pdb_id                         VARCHAR(255) UNIQUE PRIMARY KEY,
    weight                         FLOAT DEFAULT NULL
);

CREATE table casdcing.entry_list_selection
(
    pdb_id                         VARCHAR(255) UNIQUE PRIMARY KEY,
    selection                 bigint DEFAULT NULL
);

CREATE table casdcing.residue_list_selection
(
    residue_id                bigint DEFAULT NULL UNIQUE PRIMARY KEY,
    selection                 bigint DEFAULT NULL
);