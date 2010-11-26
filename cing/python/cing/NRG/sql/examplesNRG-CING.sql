-- login by:
-- psql pdbmlplus pdbj

-- Entry count 62635 on Thu Jan 21 10:41:06 CET 2010
SELECT count(*) FROM entry;

-- different schema
select count(*) from rcsb_pdb.hasExpData;

-- put extra data in
insert into rcsb_pdb.hasExpData VALUES ( '1brv' );

-- join between schemas
SELECT e.pdb_id FROM entry e, rcsb_pdb.hasExpData exp
WHERE e.pdb_id = exp.pdb_id;

-- join between databases
SELECT e.pdb_id FROM entry e, pdbmlplus.pdbj.brief_summary b
WHERE e.pdb_id =b.pdbid
AND e.pdb_id = '1brv';

SELECT entry.name, entry.wi_nqachk FROM entry
ORDER BY entry.name ASC, entry.wi_nqachk ASC;


SELECT e.name, e.distance_count,e.dihedral_count FROM entry e
where
e.distance_count = 0
AND e.dihedral_count = 0
and e.name not like '%Org'
and e.name not like '%Utrecht%'
and e.name not like '%Seattle%'
and e.name not like '%Cheshire%'
ORDER BY e.name ASC;

SELECT e.name, e.distance_count,e.dihedral_count FROM entry e
where
e.name not like '%Org'
and e.name not like '%Utrecht%'
and e.name not like '%Seattle%'
and e.name not like '%Cheshire%'
ORDER BY e.name ASC;

e.distance_count = 0
AND e.dihedral_count = 0

e.name = 'AR3436APiscataway2'

SELECT count(*) FROM entry e;

SELECT * FROM atom a where a.rog != 0;
SELECT * FROM residue r where r.rog = 2;
SELECT * FROM chain c where c.rog = 2;
SELECT * FROM entry e where e.rog = 2;

SELECT e1.entry_id, e1.pdb_id, e1.distance_count
FROM nrgcing.cingentry AS e1
WHERE e1.distance_count IS NOT NULL AND e1.distance_count != 0.0
AND e1.pdb_id = '2vda'
ORDER BY e1.distance_count DESC
LIMIT 10

SELECT * FROM "nrgcing"."cingentry" where pdb_id='1brv';

SELECT * FROM "nrgcing"."cingentry" where
noe_compl4>0.0;

SELECT r.*
FROM nrgcing.cingresidue r, nrgcing.cingentry e
where
-- r.wi_bmpchk > 30.0
r.entry_id = e.entry_id
AND e.pdb_id='1brv';

SELECT a.*
FROM nrgcing.cingatom a, nrgcing.cingentry e
where
-- r.wi_bmpchk > 30.0
a.entry_id = e.entry_id
AND e.pdb_id='1brv';

-- Now the sequences need to be initialized too.
SELECT setval('nrgcing.cingentry_entry_id_seq',     max(entry_id))      FROM nrgcing.cingentry;
SELECT setval('nrgcing.cingchain_chain_id_seq',     max(chain_id))      FROM nrgcing.cingchain;
SELECT setval('nrgcing.cingresidue_residue_id_seq', max(residue_id))    FROM nrgcing.cingresidue;
SELECT setval('nrgcing.cingatom_atom_id_seq',       max(atom_id))       FROM nrgcing.cingatom;

ALTER TABLE nrgcing.cingentry ADD COLUMN dis_max_all FLOAT DEFAULT NULL;
ALTER TABLE nrgcing.cingentry ADD COLUMN dis_rms_all FLOAT DEFAULT NULL;
ALTER TABLE nrgcing.cingentry ADD COLUMN dis_av_all  FLOAT DEFAULT NULL;
ALTER TABLE nrgcing.cingentry ADD COLUMN dis_av_viol FLOAT DEFAULT NULL;
ALTER TABLE nrgcing.cingentry ADD COLUMN dis_c1_viol INT   DEFAULT NULL;
ALTER TABLE nrgcing.cingentry ADD COLUMN dis_c3_viol INT   DEFAULT NULL;
ALTER TABLE nrgcing.cingentry ADD COLUMN dis_c5_viol INT   DEFAULT NULL;

ALTER TABLE nrgcing.cingentry ADD COLUMN dih_max_all FLOAT DEFAULT NULL;
ALTER TABLE nrgcing.cingentry ADD COLUMN dih_rms_all FLOAT DEFAULT NULL;
ALTER TABLE nrgcing.cingentry ADD COLUMN dih_av_all  FLOAT DEFAULT NULL;
ALTER TABLE nrgcing.cingentry ADD COLUMN dih_av_viol FLOAT DEFAULT NULL;
ALTER TABLE nrgcing.cingentry ADD COLUMN dih_c1_viol INT   DEFAULT NULL;
ALTER TABLE nrgcing.cingentry ADD COLUMN dih_c3_viol INT   DEFAULT NULL;
ALTER TABLE nrgcing.cingentry ADD COLUMN dih_c5_viol INT   DEFAULT NULL;

ALTER TABLE nrgcing.cingresidue ADD COLUMN phi_avg  FLOAT  DEFAULT NULL;
ALTER TABLE nrgcing.cingresidue ADD COLUMN phi_cv   FLOAT  DEFAULT NULL;
ALTER TABLE nrgcing.cingresidue ADD COLUMN psi_avg  FLOAT  DEFAULT NULL;
ALTER TABLE nrgcing.cingresidue ADD COLUMN psi_cv   FLOAT  DEFAULT NULL;
ALTER TABLE nrgcing.cingresidue ADD COLUMN chi1_avg FLOAT  DEFAULT NULL;
ALTER TABLE nrgcing.cingresidue ADD COLUMN chi1_cv  FLOAT  DEFAULT NULL;
ALTER TABLE nrgcing.cingresidue ADD COLUMN chi2_avg FLOAT  DEFAULT NULL;
ALTER TABLE nrgcing.cingresidue ADD COLUMN chi2_cv  FLOAT  DEFAULT NULL;

SELECT distinct e.pdb_id FROM "nrgcing"."cingresidue" r,  "nrgcing"."cingentry" e where
r.entry_id = e.entry_id AND
r.number < -10 AND
e.res_count < 40 AND
e.model_count <= 10 AND
e.pc_gf > -99
order by e.pdb_id;

SELECT count( FROM "nrgcing"."cingentry";

-- Can't be done in one blow.
ALTER TABLE nrgcing.cingatom ALTER COLUMN wi_mo2chk TYPE VARCHAR(255);
ALTER TABLE nrgcing.cingatom ALTER COLUMN wi_mo2chk SET DEFAULT NULL;
ALTER TABLE nrgcing.cingatom ALTER COLUMN atom_id  PRIMARY KEY;
ALTER TABLE nrgcing.cingatom ADD PRIMARY KEY (atom_id);

COPY nrgcing.cingentry     FROM 'nrgcing.cingentry.csv'   CSV HEADER;
COPY nrgcing.cingentry ( entry_id,name,bmrb_id,casd_id,pdb_id,is_solid,is_paramagnetic,is_membrane,is_multimeric,chothia_class,protein_count,dna_count,rna_count,dna_rna_hybrid_count,is_minimized,software_collection,software_processing,software_analysis,software_struct_solution,software_refinement,in_recoord,in_casd,in_dress,ranges,res_count,model_count,distance_count,dihedral_count,rdc_count,peak_count,cs_count,cs1h_count,cs13c_count,cs15n_count,wi_angchk,wi_bbcchk,wi_bmpchk,wi_bndchk,wi_c12chk,wi_chichk,wi_flpchk,wi_hndchk,wi_inochk,wi_nqachk,wi_omechk,wi_pl2chk,wi_pl3chk,wi_plnchk,wi_quachk,wi_ramchk,wi_rotchk,pc_gf,pc_gf_phipsi,pc_gf_chi12,pc_gf_chi1,noe_compl4,rog )
FROM '$cwd/casdcing.cingentry.csv'    CSV HEADER;

entry_id,name,bmrb_id,casd_id,pdb_id,is_solid,is_paramagnetic,is_membrane,is_multimeric,chothia_class,protein_count,dna_count,rna_count,dna_rna_hybrid_count,is_minimized,software_collection,software_processing,software_analysis,software_struct_solution,software_refinement,in_recoord,in_casd,in_dress,ranges,res_count,model_count,distance_count,dihedral_count,rdc_count,peak_count,cs_count,cs1h_count,cs13c_count,cs15n_count,wi_angchk,wi_bbcchk,wi_bmpchk,wi_bndchk,wi_c12chk,wi_chichk,wi_flpchk,wi_hndchk,wi_inochk,wi_nqachk,wi_omechk,wi_pl2chk,wi_pl3chk,wi_plnchk,wi_quachk,wi_ramchk,wi_rotchk,pc_gf,pc_gf_phipsi,pc_gf_chi12,pc_gf_chi1,pc_rama_core,pc_rama_allow,pc_rama_gener,pc_rama_disall,noe_compl4,rog,dis_max_all,dis_rms_all,dis_av_all,dis_av_viol,dis_c1_viol,dis_c3_viol,dis_c5_viol,dih_max_all,dih_rms_all,dih_av_all,dih_av_viol,dih_c1_viol,dih_c3_viol,dih_c5_viol
