--
-- Protein Biophysics Analysis of the NRG-CING results
-- SQL Definitions for creating tables
--     written: Wed Nov 11 14:14:07 CET 2009
-- Copyright 2009
--     Jurgen F. Doreleijers
--     Protein Biophysics, Radboud University Nijmegen, the Netherlands.
--
-- Notes:
-- * Setup commands are specific for database type: MySQL
-- * Run by command like:
-- * mysql -u nrgcing1 -p4I4KMS nrgcing < $CINGROOT/scripts/sql/createNRG-CING.sql
-- no output means no errors.
-- Should be autocommiting by default but I saw it didn't once.
SET AUTOCOMMIT=1;

-- Remove previous copies in bottom up order.
-- This will automatically drop the index created too.
DROP TABLE IF EXISTS residue;
DROP TABLE IF EXISTS chain;
DROP TABLE IF EXISTS entry;

-- Remove unique sequence ids
DROP TABLE IF EXISTS residue_id;
DROP TABLE IF EXISTS chain_id;
DROP TABLE IF EXISTS entry_id;
CREATE TABLE entry_id   (id INT NOT NULL); INSERT INTO entry_id     VALUES (1000);
CREATE TABLE chain_id  (id INT NOT NULL); INSERT INTO chain_id    VALUES (1000);
CREATE TABLE residue_id (id INT NOT NULL); INSERT INTO residue_id   VALUES (1000);
-- entry
CREATE TABLE entry
(
    entry_id                       INT              NOT NULL PRIMARY KEY,
    bmrb_id                        INT,
    pdb_id                         CHAR(4),
    is_solid                       BOOLEAN DEFAULT NULL,
    is_paramagnetic                BOOLEAN DEFAULT NULL,
    is_membrane                    BOOLEAN DEFAULT NULL,
    is_multimeric                  BOOLEAN DEFAULT NULL,
    in_recoord                     BOOLEAN DEFAULT NULL,
    in_dress                       BOOLEAN DEFAULT NULL,
    rog                            INT DEFAULT NULL
) TYPE = INNODB;
CREATE INDEX entry_001 ON entry (bmrb_id);
CREATE INDEX entry_002 ON entry (pdb_id);

-- mrfile
-- MySQL doesn't accept the SYSDATE default for date_modified so always present date on insert.
-- From MySQL manual:
-- For storage engines other than InnoDB, MySQL Server parses the FOREIGN KEY
-- syntax in CREATE TABLE statements, but does not use or store it.
-- The solution is to define the innodb tables as below.
CREATE TABLE chain
(
    chain_id                        INT             NOT NULL PRIMARY KEY,
    entry_id                        INT             NOT NULL,
    detail                          VARCHAR(255)    DEFAULT 'A',
    pdb_id                          CHAR(4),
    rog                            INT DEFAULT NULL,
    FOREIGN KEY (entry_id)          REFERENCES entry (entry_id) ON DELETE CASCADE
) TYPE = INNODB;
-- Some common queries are helped by these indexes..
CREATE INDEX chain_001 ON chain (entry_id);
CREATE INDEX chain_002 ON chain (pdb_id);

-- residue
CREATE TABLE residue
(
    residue_id                     INT              NOT NULL PRIMARY KEY,
    chain_id                       INT              NOT NULL,
    entry_id                       INT              NOT NULL,
    number                         INT              NOT NULL,
    author_id                      VARCHAR(255)     NOT NULL,
    is_common                      BOOLEAN DEFAULT 1,
    is_termin                      BOOLEAN DEFAULT 0,
    rog                            INT DEFAULT NULL,
    FOREIGN KEY (chain_id)          REFERENCES chain (chain_id) ON DELETE CASCADE,
    FOREIGN KEY (entry_id)          REFERENCES entry (entry_id) ON DELETE CASCADE
) TYPE = INNODB;
CREATE INDEX residue_001 ON residue (chain_id);
CREATE INDEX residue_002 ON residue (number);


