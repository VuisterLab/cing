--
-- SQL Definitions for creating tables.
--     Jurgen F. Doreleijers
--     Protein Biophysics, Radboud University Nijmegen, the Netherlands.
--     written: Wed Jun 30 12:27:14 CEST 2010
--
-- Notes:
-- * Setup commands are specific for database type: PostgreSQL
-- * Run by command like:
-- * psql --quiet casdcing casdcing1 < $CINGROOT/scripts/sql/createDB-CING_psql.sql
-- * psql --quiet pdbmlplus pdbj < $CINGROOT/scripts/sql/createDB-CING_psql.sql
-- Or from  cing.NRG.createDB_CING.py

-- Should be autocommiting by default but I saw it didn't once.
SET AUTOCOMMIT=1;

-- Only now that the tables have been removed can the schema be removed.
DROP SCHEMA IF EXISTS casdcing CASCADE;
CREATE SCHEMA casdcing AUTHORIZATION casdcing1;

--CREATE TABLE entry
--(
--    entry_id                       SERIAL UNIQUE,
--    name                           VARCHAR(255)
--)

-- entry
CREATE TABLE casdcing.cingentry
(
    entry_id                       SERIAL UNIQUE,
    name                           VARCHAR(255),
    bmrb_id                        INT,
    casd_id                        VARCHAR(255) UNIQUE,
    pdb_id                         VARCHAR(255),
    is_solid                       BOOLEAN DEFAULT NULL, -- ssnmr
    is_paramagnetic                BOOLEAN DEFAULT NULL, -- paramagnetic.
    is_membrane                    BOOLEAN DEFAULT NULL, -- membrane
    is_multimeric                  BOOLEAN DEFAULT NULL, --
    chothia_class                  INT DEFAULT NULL,     -- alpha, beta, of a/b, a+b, or coil
    protein_count                  INT DEFAULT NULL,
    dna_count                      INT DEFAULT NULL,
    rna_count                      INT DEFAULT NULL,
    dna_rna_hybrid_count           INT DEFAULT NULL,
    is_minimized                   BOOLEAN DEFAULT NULL, -- (optimized) minimized structure only known for 1340 entries in PDB overall on Jan 2010.
    software_collection            VARCHAR(255) DEFAULT NULL, -- _pdbx_nmr_software.name etc. only 8,000 items estimated 1,000 entries available
    software_processing            VARCHAR(255) DEFAULT NULL,
    software_analysis              VARCHAR(255) DEFAULT NULL,
    software_struct_solution       VARCHAR(255) DEFAULT NULL,
    software_refinement            VARCHAR(255) DEFAULT NULL,
    in_recoord                     BOOLEAN DEFAULT NULL,
    in_casd                        BOOLEAN DEFAULT NULL,
    in_dress                       BOOLEAN DEFAULT NULL,
    ranges                         VARCHAR(512) DEFAULT NULL,
    res_count                      INT DEFAULT NULL,     -- number of residues
    model_count                    INT DEFAULT NULL,     --
    distance_count                 INT DEFAULT NULL,
    dihedral_count                 INT DEFAULT NULL,
    rdc_count                      INT DEFAULT NULL,
    peak_count                     INT DEFAULT NULL,
    cs_count                       INT DEFAULT NULL,
    cs1H_count                     INT DEFAULT NULL,
    cs13C_count                    INT DEFAULT NULL,
    cs15N_count                    INT DEFAULT NULL,
--   whatif (averages over the ensemble of selected models)
    wi_angchk                      FLOAT DEFAULT NULL,
    wi_bbcchk                      FLOAT DEFAULT NULL,
    wi_bmpchk                      FLOAT DEFAULT NULL,
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
--   procheck_nmr
    pc_gf                           FLOAT DEFAULT NULL,
    pc_gf_phipsi                    FLOAT DEFAULT NULL,
    pc_gf_chi12                     FLOAT DEFAULT NULL,
    pc_gf_chi1                      FLOAT DEFAULT NULL,
    pc_rama_core                    FLOAT DEFAULT NULL,
    pc_rama_allow                   FLOAT DEFAULT NULL,
    pc_rama_gener                   FLOAT DEFAULT NULL,
    pc_rama_disall                  FLOAT DEFAULT NULL,
--   wattos (there are other parameters at residue level but not filled in now).
    noe_compl4                     FLOAT DEFAULT NULL,

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

--    pdbx_SG_project_XXXinitial_of_center  VARCHAR(25) DEFAULT NULL, -- pdbx_SG_project_Initial_of_center E.g. RSGI; NULL means not from any SG.
    rog                            INT DEFAULT NULL
);

CREATE INDEX entry_001 ON casdcing.cingentry (bmrb_id);
CREATE INDEX entry_002 ON casdcing.cingentry (pdb_id);

-- mrfile
-- MySQL doesn't accept the SYSDATE default for date_modified so always present date on insert.
-- From MySQL manual:
-- For storage engines other than InnoDB, MySQL Server parses the FOREIGN KEY
-- syntax in CREATE TABLE statements, but does not use or store it.
-- The solution is to define the innodb tables as below.


--    mol_type
CREATE TABLE casdcing.cingchain
(
    chain_id                        SERIAL UNIQUE,
    entry_id                        INT NOT NULL,
    name                            VARCHAR(255)    DEFAULT 'A',
    chothia_class                   INT DEFAULT NULL,
    rog                             INT DEFAULT NULL,
    FOREIGN KEY (entry_id)          REFERENCES casdcing.cingentry (entry_id) ON DELETE CASCADE
);
-- Some common queries are helped by these indexes..
CREATE INDEX chain_001 ON casdcing.cingchain (entry_id);

-- residue
CREATE TABLE casdcing.cingresidue
(
    residue_id                     SERIAL UNIQUE,
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
    wi_bmpchk                      FLOAT DEFAULT NULL,
    wi_bndchk                      FLOAT DEFAULT NULL,
    wi_c12chk                      FLOAT DEFAULT NULL,
    wi_flpchk                      FLOAT DEFAULT NULL,
    wi_inochk                      FLOAT DEFAULT NULL,
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
    pc_gf                           FLOAT DEFAULT NULL,
    pc_gf_phipsi                    FLOAT DEFAULT NULL,
    pc_gf_chi12                     FLOAT DEFAULT NULL,
    pc_gf_chi1                      FLOAT DEFAULT NULL,
--   wattos
    noe_compl4                     FLOAT DEFAULT NULL,
    noe_compl_obs                  INT DEFAULT NULL,
    noe_compl_exp                  INT DEFAULT NULL,
    noe_compl_mat                  INT DEFAULT NULL,
--   cing
    rog                            INT DEFAULT NULL,
    omega_dev_av_all               FLOAT DEFAULT NULL,
    cv_backbone                    FLOAT DEFAULT NULL,
    cv_sidechain                   FLOAT DEFAULT NULL,

    phi_avg                    FLOAT DEFAULT NULL,
    phi_cv                     FLOAT DEFAULT NULL,
    psi_avg                    FLOAT DEFAULT NULL,
    psi_cv                     FLOAT DEFAULT NULL,
    chi1_avg                   FLOAT DEFAULT NULL,
    chi1_cv                    FLOAT DEFAULT NULL,
    chi2_avg                   FLOAT DEFAULT NULL,
    chi2_cv                    FLOAT DEFAULT NULL,

    chk_ramach                     FLOAT DEFAULT NULL,
    chk_janin                      FLOAT DEFAULT NULL,
    chk_d1d2                       FLOAT DEFAULT NULL,
    distance_count                 INT DEFAULT NULL,
    dihedral_count                 INT DEFAULT NULL,
    rdc_count                      INT DEFAULT NULL,
    peak_count                     INT DEFAULT NULL,
    cs_count                       INT DEFAULT NULL,
    cs1H_count                     INT DEFAULT NULL,
    cs13C_count                    INT DEFAULT NULL,
    cs15N_count                    INT DEFAULT NULL,

    qcs_all                        FLOAT DEFAULT NULL,
    qcs_bb                         FLOAT DEFAULT NULL,
    qcs_hvy                        FLOAT DEFAULT NULL,
    qcs_prt                        FLOAT DEFAULT NULL,

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

    FOREIGN KEY (chain_id)          REFERENCES casdcing.cingchain (chain_id) ON DELETE CASCADE,
    FOREIGN KEY (entry_id)          REFERENCES casdcing.cingentry (entry_id) ON DELETE CASCADE
);
CREATE INDEX residue_001 ON casdcing.cingresidue (chain_id);
CREATE INDEX residue_002 ON casdcing.cingresidue (entry_id);
CREATE INDEX residue_003 ON casdcing.cingresidue (number);
CREATE INDEX residue_004 ON casdcing.cingresidue (dssp_id);
CREATE INDEX residue_005 ON casdcing.cingresidue (rog);
CREATE INDEX residue_006 ON casdcing.cingresidue (dis_c5_viol);


-- atom
CREATE TABLE casdcing.cingatom
(
    atom_id                        SERIAL UNIQUE,
    residue_id                     INT              NOT NULL,
    chain_id                       INT              NOT NULL,
    entry_id                       INT              NOT NULL,
    name                           VARCHAR(255)     DEFAULT NULL,
--   whatif
    wi_ba2chk                      FLOAT DEFAULT NULL,
    wi_bh2chk                      VARCHAR(255) DEFAULT NULL,
    wi_chichk                      FLOAT DEFAULT NULL,
    wi_dunchk                      FLOAT DEFAULT NULL,
    wi_hndchk                      FLOAT DEFAULT NULL,
    wi_mischk                      VARCHAR(255) DEFAULT NULL,
    wi_mo2chk                      VARCHAR(255) DEFAULT NULL,
    wi_pl2chk                      FLOAT DEFAULT NULL,
    wi_wgtchk                      FLOAT DEFAULT NULL,
--   cing
    rog                            INT DEFAULT NULL,
    FOREIGN KEY (residue_id)        REFERENCES casdcing.cingresidue (residue_id) ON DELETE CASCADE,
    FOREIGN KEY (chain_id)          REFERENCES casdcing.cingchain (chain_id) ON DELETE CASCADE,
    FOREIGN KEY (entry_id)          REFERENCES casdcing.cingentry (entry_id) ON DELETE CASCADE
);
CREATE INDEX atom_001 ON casdcing.cingatom (residue_id);
CREATE INDEX atom_002 ON casdcing.cingatom (chain_id);
CREATE INDEX atom_003 ON casdcing.cingatom (entry_id);
CREATE INDEX atom_004 ON casdcing.cingatom (name);

