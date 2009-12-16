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

-- entry
CREATE TABLE entry
(
    entry_id                       INT              NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name                           VARCHAR(255) NOT NULL,
    bmrb_id                        INT,
    pdb_id                         CHAR(4),
    is_solid                       BOOLEAN DEFAULT NULL,
    is_paramagnetic                BOOLEAN DEFAULT NULL,
    is_membrane                    BOOLEAN DEFAULT NULL,
    is_multimeric                  BOOLEAN DEFAULT NULL,
    in_recoord                     BOOLEAN DEFAULT NULL,
    in_dress                       BOOLEAN DEFAULT NULL,
    model_count                    INT DEFAULT NULL,
    res_count                      INT DEFAULT NULL,
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
    chain_id                        INT             NOT NULL AUTO_INCREMENT PRIMARY KEY,
    entry_id                        INT             NOT NULL,
    name                            VARCHAR(255)    DEFAULT 'A',
    rog                             INT DEFAULT NULL,
    FOREIGN KEY (entry_id)          REFERENCES entry (entry_id) ON DELETE CASCADE
) TYPE = INNODB;
-- Some common queries are helped by these indexes..
CREATE INDEX chain_001 ON chain (entry_id);

-- residue
CREATE TABLE residue
(
    residue_id                     INT              NOT NULL AUTO_INCREMENT PRIMARY KEY,
    chain_id                       INT              NOT NULL,
    entry_id                       INT              NOT NULL,
    number                         INT              NOT NULL,
    name                           VARCHAR(255)     DEFAULT NULL,
    is_common                      BOOLEAN DEFAULT NULL,
    is_termin                      BOOLEAN DEFAULT NULL,
--   whatif (averages over the ensemble of selected models)
    wi_acclst                      FLOAT DEFAULT NULL,
    wi_angchk                      FLOAT DEFAULT NULL,
    wi_bbcchk                      FLOAT DEFAULT NULL,
    wi_bmpchk                      FLOAT DEFAULT 0.0,
    wi_bndchk                      FLOAT DEFAULT NULL,
    wi_c12chk                      FLOAT DEFAULT NULL,
    wi_chichk                      FLOAT DEFAULT NULL,
    wi_flpchk                      FLOAT DEFAULT NULL,
    wi_hndchk                      FLOAT DEFAULT NULL,
    wi_inochk                      FLOAT DEFAULT NULL,
    wi_nqachk                      FLOAT DEFAULT NULL,
    wi_omechk                      FLOAT DEFAULT NULL,
    wi_pl2chk                      FLOAT DEFAULT NULL,
    wi_pl3chk                      FLOAT DEFAULT NULL,
    wi_plnchk                      FLOAT DEFAULT NULL,
    wi_quachk                      FLOAT DEFAULT NULL,
    wi_ramchk                      FLOAT DEFAULT NULL,
    wi_rotchk                      FLOAT DEFAULT NULL,
--   dssp
    dssp_id                        INT DEFAULT NULL,
--   procheck_nmr
    pc_gf                          FLOAT DEFAULT NULL,
    pc_gfphipsi                    FLOAT DEFAULT NULL,
    pc_gfchi12                     FLOAT DEFAULT NULL,
    pc_gfchi1                      FLOAT DEFAULT NULL,
--   wattos
    noe_compl4                     FLOAT DEFAULT NULL,
    noe_compl_obs                  INT DEFAULT NULL,
    noe_compl_exp                  INT DEFAULT NULL,
    noe_compl_mat                  INT DEFAULT NULL,
--   cing
    rog                            INT DEFAULT NULL,
    omega_dev_av_all               FLOAT DEFAULT NULL,

    dis_max_all                    FLOAT DEFAULT NULL,
    dis_rms_all                    FLOAT DEFAULT NULL,
    dis_av_all                     FLOAT DEFAULT NULL,
    dis_av_viol                    FLOAT DEFAULT NULL,
    dis_c1_viol                    INT DEFAULT NULL,
    dis_c3_viol                    INT DEFAULT NULL,
    dis_c5_viol                    INT DEFAULT NULL,

    dih_max_all                    FLOAT DEFAULT NULL,
    dih_rms_all                    FLOAT DEFAULT NULL,
    dih_av_all                     FLOAT DEFAULT NULL,
    dih_av_viol                    FLOAT DEFAULT NULL,
    dih_c1_viol                    INT DEFAULT NULL,
    dih_c3_viol                    INT DEFAULT NULL,
    dih_c5_viol                    INT DEFAULT NULL,

    FOREIGN KEY (chain_id)          REFERENCES chain (chain_id) ON DELETE CASCADE,
    FOREIGN KEY (entry_id)          REFERENCES entry (entry_id) ON DELETE CASCADE
) TYPE = INNODB;
CREATE INDEX residue_001 ON residue (chain_id);
CREATE INDEX residue_002 ON residue (number);
CREATE INDEX residue_003 ON residue (dssp_id);
CREATE INDEX residue_004 ON residue (rog);
CREATE INDEX residue_005 ON residue (dis_c5_viol);