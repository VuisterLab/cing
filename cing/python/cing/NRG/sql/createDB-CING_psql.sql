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
--
-- Or edit and execute:
-- python -u $CINGROOT/python/cing/NRG/runSqlForSchema.py devnrgcing    $CINGROOT/python/cing/NRG/sql/createDB-CING_psql.sql    .
-- python -u $CINGROOT/python/cing/NRG/runSqlForSchema.py casdcing      $CINGROOT/python/cing/NRG/sql/createDB-CING_psql.sql    .

-- Should be autocommiting by default but I saw it didn't once.
SET AUTOCOMMIT=1;

-- ===== Registers ======
-- Register 1 is reserved for ranges selection at the residue level only.

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
    entry_id                       SERIAL UNIQUE PRIMARY KEY,
    name                           VARCHAR(255),
    rev_first                      INT DEFAULT NULL, -- CING revision of first project initialization which must have the import of data
    rev_last                       INT DEFAULT NULL, -- CING revision of last project save.
    timestamp_first                timestamp DEFAULT NULL, -- Dates (seconds since epoch) of the above.
    timestamp_last                 timestamp DEFAULT NULL,
    sel_1                     BOOLEAN DEFAULT NULL, -- registers used for selections see comment section above.
    sel_2                     BOOLEAN DEFAULT NULL,
    sel_3                     BOOLEAN DEFAULT NULL,
    sel_4                     BOOLEAN DEFAULT NULL,
    sel_5                     BOOLEAN DEFAULT NULL,
    bmrb_id                        INT DEFAULT NULL,
    casd_id                        VARCHAR(255) UNIQUE,
    pdb_id                         VARCHAR(255), -- (10)
    is_solid                       BOOLEAN DEFAULT NULL, -- ssnmr
    is_paramagnetic                BOOLEAN DEFAULT NULL, -- paramagnetic.
    is_membrane                    BOOLEAN DEFAULT NULL, -- membrane
    is_multimeric                  BOOLEAN DEFAULT NULL, -- E.g. 1hue is a dimer and would be true. Doesn't necessarily need to be a symmetric multimer however.
    symmetry                       VARCHAR(255) DEFAULT NULL, -- E.g. D2 by SYMMETRY_D2_STR
    ncs_symmetry                    FLOAT DEFAULT NULL, 
    dr_symmetry                     FLOAT DEFAULT NULL,
    chothia_class                  INT DEFAULT NULL,     -- (10) alpha, beta, of a/b, a+b, or coil
    protein_count                  INT DEFAULT NULL,     -- Number of protein chains. Not necessarily unique so e.g. 1hue has 2 that are identical (homodimer). TODO: fill.
    dna_count                      INT DEFAULT NULL,
    rna_count                      INT DEFAULT NULL,
    dna_rna_hybrid_count           INT DEFAULT NULL,
    is_minimized                   BOOLEAN DEFAULT NULL, -- (20) (optimized) minimized structure only known for 1340 entries in PDB overall on Jan 2010.
    software_collection            VARCHAR(255) DEFAULT NULL, -- _pdbx_nmr_software.name etc. only 8,000 items estimated 1,000 entries available
    software_processing            VARCHAR(255) DEFAULT NULL,
    software_analysis              VARCHAR(255) DEFAULT NULL,
    software_struct_solution       VARCHAR(255) DEFAULT NULL,
    software_refinement            VARCHAR(255) DEFAULT NULL,
    in_recoord                     BOOLEAN DEFAULT NULL,
    in_casd                        BOOLEAN DEFAULT NULL,
    in_dress                       BOOLEAN DEFAULT NULL,
    ranges                         VARCHAR(512) DEFAULT NULL,
    res_count                      INT DEFAULT NULL,     -- (30) number of residues
    model_count                    INT DEFAULT NULL,
    distance_count                 INT DEFAULT NULL,
    distance_count_sequential      INT DEFAULT NULL,
    distance_count_intra_residual  INT DEFAULT NULL,
    distance_count_medium_range    INT DEFAULT NULL,
    distance_count_long_range      INT DEFAULT NULL,
    distance_count_ambiguous       INT DEFAULT NULL,
    dihedral_count                 INT DEFAULT NULL,
    rdc_count                      INT DEFAULT NULL,
    peak_count                     INT DEFAULT NULL,
    cs_count                       INT DEFAULT NULL,
    cs1h_count                     INT DEFAULT NULL,
    cs13c_count                    INT DEFAULT NULL,
    cs15n_count                    INT DEFAULT NULL,
    cs31p_count                    INT DEFAULT NULL,
    ssa_count                      INT DEFAULT NULL,
    ssa_swap_count                 INT DEFAULT NULL,
    ssa_deassign_count             INT DEFAULT NULL,
    omega_dev_av_all               FLOAT DEFAULT NULL, --   cing
    cv_backbone                    FLOAT DEFAULT NULL,
    cv_sidechain                   FLOAT DEFAULT NULL,
    rmsd_backbone                  FLOAT DEFAULT NULL,
    rmsd_sidechain                 FLOAT DEFAULT NULL,
    queen_information              FLOAT DEFAULT NULL, --   queen
    queen_uncertainty1             FLOAT DEFAULT NULL,
    queen_uncertainty2             FLOAT DEFAULT NULL,
    wi_angchk                      FLOAT DEFAULT NULL, --   whatif (averages over the ensemble of selected models)      
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
    pc_gf                           FLOAT DEFAULT NULL, --   procheck_nmr
    pc_gf_phipsi                    FLOAT DEFAULT NULL,
    pc_gf_chi12                     FLOAT DEFAULT NULL,
    pc_gf_chi1                      FLOAT DEFAULT NULL,
    pc_rama_core                    FLOAT DEFAULT NULL,
    pc_rama_allow                   FLOAT DEFAULT NULL,
    pc_rama_gener                   FLOAT DEFAULT NULL,
    pc_rama_disall                  FLOAT DEFAULT NULL,
    noe_compl4                     FLOAT DEFAULT NULL, -- wattos (there are other parameters at residue level but not filled in now).
    noe_compl_obs                  INT DEFAULT NULL,
    noe_compl_exp                  INT DEFAULT NULL,
    noe_compl_mat                  INT DEFAULT NULL,
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
    rog                            INT DEFAULT NULL
--    pdbx_SG_project_XXXinitial_of_center  VARCHAR(25) DEFAULT NULL, -- pdbx_SG_project_Initial_of_center E.g. RSGI; NULL means not from any SG.
);

CREATE INDEX entry_001 ON casdcing.cingentry (bmrb_id);
CREATE INDEX entry_002 ON casdcing.cingentry (pdb_id);
CREATE INDEX entry_se1 ON casdcing.cingentry (sel_1);
CREATE INDEX entry_se2 ON casdcing.cingentry (sel_2);
CREATE INDEX entry_se3 ON casdcing.cingentry (sel_3);
CREATE INDEX entry_se4 ON casdcing.cingentry (sel_4);
CREATE INDEX entry_se5 ON casdcing.cingentry (sel_5);

-- mrfile
-- MySQL doesn't accept the SYSDATE default for date_modified so always present date on insert.
-- From MySQL manual:
-- For storage engines other than InnoDB, MySQL Server parses the FOREIGN KEY
-- syntax in CREATE TABLE statements, but does not use or store it.
-- The solution is to define the innodb tables as below.


--    mol_type
CREATE TABLE casdcing.cingchain
(
    chain_id                        SERIAL UNIQUE PRIMARY KEY,
    entry_id                        INT NOT NULL,
    name                            VARCHAR(255)    DEFAULT 'A',
    sel_1                     BOOLEAN DEFAULT NULL,
    sel_2                     BOOLEAN DEFAULT NULL,
    sel_3                     BOOLEAN DEFAULT NULL,
    sel_4                     BOOLEAN DEFAULT NULL,
    sel_5                     BOOLEAN DEFAULT NULL,
    chothia_class                   INT DEFAULT NULL,
    rog                             INT DEFAULT NULL,
    FOREIGN KEY (entry_id)          REFERENCES casdcing.cingentry (entry_id) ON DELETE CASCADE
);
-- Some common queries are helped by these indexes..
CREATE INDEX chain_001 ON casdcing.cingchain (entry_id);
CREATE INDEX chain_se1 ON casdcing.cingchain (sel_1);
CREATE INDEX chain_se2 ON casdcing.cingchain (sel_2);
CREATE INDEX chain_se3 ON casdcing.cingchain (sel_3);
CREATE INDEX chain_se4 ON casdcing.cingchain (sel_4);
CREATE INDEX chain_se5 ON casdcing.cingchain (sel_5);

-- residue
CREATE TABLE casdcing.cingresidue
(
    residue_id                     SERIAL UNIQUE PRIMARY KEY,
    chain_id                       INT              NOT NULL,
    entry_id                       INT              NOT NULL,
    number                         INT              NOT NULL,
    name                           VARCHAR(255)     DEFAULT NULL,
    sel_1                     BOOLEAN DEFAULT NULL,
    sel_2                     BOOLEAN DEFAULT NULL,
    sel_3                     BOOLEAN DEFAULT NULL,
    sel_4                     BOOLEAN DEFAULT NULL,
    sel_5                     BOOLEAN DEFAULT NULL,
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

--   queen
    queen_information      FLOAT DEFAULT NULL,
    queen_uncertainty1     FLOAT DEFAULT NULL,
    queen_uncertainty2     FLOAT DEFAULT NULL, -- column 39

--   cing
    rog                            INT DEFAULT NULL,
    omega_dev_av_all               FLOAT DEFAULT NULL,
    cv_backbone                    FLOAT DEFAULT NULL,
    cv_sidechain                   FLOAT DEFAULT NULL,
    rmsd_backbone                  FLOAT DEFAULT NULL,
    rmsd_sidechain                 FLOAT DEFAULT NULL,

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
    cs1h_count                     INT DEFAULT NULL,
    cs13c_count                    INT DEFAULT NULL,
    cs15n_count                    INT DEFAULT NULL,
    cs31p_count                    INT DEFAULT NULL,

    qcs_all                        FLOAT DEFAULT NULL,
    qcs_bb                         FLOAT DEFAULT NULL,
    qcs_hvy                        FLOAT DEFAULT NULL,
    qcs_prt                        FLOAT DEFAULT NULL,
    qcs_s2                         FLOAT DEFAULT NULL,

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
CREATE INDEX residue_se1 ON casdcing.cingresidue (sel_1);
CREATE INDEX residue_se2 ON casdcing.cingresidue (sel_2);
CREATE INDEX residue_se3 ON casdcing.cingresidue (sel_3);
CREATE INDEX residue_se4 ON casdcing.cingresidue (sel_4);
CREATE INDEX residue_se5 ON casdcing.cingresidue (sel_5);


-- atom
CREATE TABLE casdcing.cingatom
(
    atom_id                        SERIAL UNIQUE PRIMARY KEY,
    residue_id                     INT              NOT NULL,
    chain_id                       INT              NOT NULL,
    entry_id                       INT              NOT NULL,
    name                           VARCHAR(255)     DEFAULT NULL,
    spin_type                      VARCHAR(255)     DEFAULT NULL,
    sel_1                     BOOLEAN DEFAULT NULL,
    sel_2                     BOOLEAN DEFAULT NULL,
    sel_3                     BOOLEAN DEFAULT NULL,
    sel_4                     BOOLEAN DEFAULT NULL,
    sel_5                     BOOLEAN DEFAULT NULL,
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
    cs                             FLOAT DEFAULT NULL,
    cs_err                         FLOAT DEFAULT NULL,
    cs_ssa                         INT DEFAULT NULL, -- atom.stereoAssigned flag in CING data model.

    rog                            INT DEFAULT NULL,
    FOREIGN KEY (residue_id)        REFERENCES casdcing.cingresidue (residue_id) ON DELETE CASCADE,
    FOREIGN KEY (chain_id)          REFERENCES casdcing.cingchain (chain_id) ON DELETE CASCADE,
    FOREIGN KEY (entry_id)          REFERENCES casdcing.cingentry (entry_id) ON DELETE CASCADE
);
CREATE INDEX atom_001 ON casdcing.cingatom (residue_id);
CREATE INDEX atom_002 ON casdcing.cingatom (chain_id);
CREATE INDEX atom_003 ON casdcing.cingatom (entry_id);
CREATE INDEX atom_004 ON casdcing.cingatom (name);
CREATE INDEX atom_005 ON casdcing.cingatom (spin_type);
CREATE INDEX atom_se1 ON casdcing.cingatom (sel_1);
CREATE INDEX atom_se2 ON casdcing.cingatom (sel_2);
CREATE INDEX atom_se3 ON casdcing.cingatom (sel_3);
CREATE INDEX atom_se4 ON casdcing.cingatom (sel_4);
CREATE INDEX atom_se5 ON casdcing.cingatom (sel_5);


CREATE TABLE casdcing.cingresonancelist
(
    resonancelist_id               SERIAL UNIQUE PRIMARY KEY,
    entry_id                       INT              NOT NULL,
    name                           VARCHAR(255),
    applied                        BOOLEAN DEFAULT FALSE, -- only when applicable
    rog                            INT DEFAULT NULL,
    FOREIGN KEY (entry_id)         REFERENCES casdcing.cingentry (entry_id) ON DELETE CASCADE
);
CREATE INDEX cingresonancelist_001 ON casdcing.cingresonancelist (entry_id);
CREATE INDEX cingresonancelist_002 ON casdcing.cingresonancelist (applied);
CREATE INDEX cingresonancelist_003 ON casdcing.cingresonancelist (rog);

CREATE TABLE casdcing.cingresonancelistperatomclass
(
    resonancelistperatomclass_id   SERIAL UNIQUE PRIMARY KEY,
    resonancelist_id               INT              NOT NULL,
    entry_id                       INT              NOT NULL,
    atomclass                      VARCHAR(255),          -- atom clas
    csd                            FLOAT DEFAULT NULL,
    csd_err                        FLOAT DEFAULT NULL,
    rog                            INT DEFAULT NULL,
    FOREIGN KEY (resonancelist_id) REFERENCES casdcing.cingresonancelist (resonancelist_id) ON DELETE CASCADE,
    FOREIGN KEY (entry_id)         REFERENCES casdcing.cingentry (entry_id) ON DELETE CASCADE
);

CREATE INDEX cingresonancelistperatomclass_001 ON casdcing.cingresonancelistperatomclass (resonancelist_id);
CREATE INDEX cingresonancelistperatomclass_002 ON casdcing.cingresonancelistperatomclass (entry_id);
CREATE INDEX cingresonancelistperatomclass_003 ON casdcing.cingresonancelistperatomclass (atomclass);
CREATE INDEX cingresonancelistperatomclass_004 ON casdcing.cingresonancelistperatomclass (rog);

CREATE table casdcing.cingsummary
(
    pdb_id                         VARCHAR(255) UNIQUE PRIMARY KEY,
    weight                         FLOAT DEFAULT NULL
);

CREATE table casdcing.entry_list_selection
(
    pdb_id                         VARCHAR(255) UNIQUE PRIMARY KEY
);

