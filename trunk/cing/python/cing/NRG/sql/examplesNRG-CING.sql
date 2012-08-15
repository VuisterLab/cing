-- this is file: $C/python/cing/NRG/sql/examplesNRG-CING.sql 
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

ALTER TABLE nrgcing.cingentry ADD COLUMN res_protein_count INT   DEFAULT NULL;
ALTER TABLE nrgcing.cingentry ADD COLUMN res_dna_count     INT   DEFAULT NULL;
ALTER TABLE nrgcing.cingentry ADD COLUMN res_rna_count     INT   DEFAULT NULL;
ALTER TABLE nrgcing.cingentry ADD COLUMN res_water_count   INT   DEFAULT NULL;
ALTER TABLE nrgcing.cingentry ADD COLUMN res_other_count   INT   DEFAULT NULL;

ALTER TABLE nrgcing.cingresidue ADD COLUMN phi_avg  FLOAT  DEFAULT NULL;
ALTER TABLE nrgcing.cingresidue ADD COLUMN phi_cv   FLOAT  DEFAULT NULL;
ALTER TABLE nrgcing.cingresidue ADD COLUMN psi_avg  FLOAT  DEFAULT NULL;
ALTER TABLE nrgcing.cingresidue ADD COLUMN psi_cv   FLOAT  DEFAULT NULL;
ALTER TABLE nrgcing.cingresidue ADD COLUMN chi1_avg FLOAT  DEFAULT NULL;
ALTER TABLE nrgcing.cingresidue ADD COLUMN chi1_cv  FLOAT  DEFAULT NULL;
ALTER TABLE nrgcing.cingresidue ADD COLUMN chi2_avg FLOAT  DEFAULT NULL;
ALTER TABLE nrgcing.cingresidue ADD COLUMN chi2_cv  FLOAT  DEFAULT NULL;
-- See:
--DSSP_H = 'H'
--DSSP_S = 'S'
--DSSP_C = ' '
ALTER TABLE nrgcing.cingresidue ADD COLUMN dssp_h_percent  FLOAT  DEFAULT NULL;
ALTER TABLE nrgcing.cingresidue ADD COLUMN dssp_s_percent  FLOAT  DEFAULT NULL;
ALTER TABLE nrgcing.cingresidue ADD COLUMN dssp_c_percent  FLOAT  DEFAULT NULL;

select avg(dssp_h_percent) as h, avg(dssp_s_percent) as s, avg(dssp_c_percent) as c from nrgcing.cingresidue where
dssp_h_percent is not null 
;

SELECT distinct e.pdb_id FROM "nrgcing"."cingresidue" r,  "nrgcing"."cingentry" e where
r.entry_id = e.entry_id AND
r.number < -10 AND
e.res_count < 40 AND
e.model_count <= 10 AND
e.pc_gf > -99
order by e.pdb_id;


-- find the cs differences for the Leu Cdeltas
SELECT count(*) FROM "devnrgcing"."cingentry";
SELECT e.pdb_id as pdb, c.name as c, r.number as num, a.name, a.cs

SELECT count(*) /2 as leu_ssa_cds
FROM
"devnrgcing"."cingentry" e,
"devnrgcing"."cingresidue" r,
"devnrgcing"."cingchain" c,
"devnrgcing"."cingatom" a
 where
r.entry_id = e.entry_id AND
c.entry_id = e.entry_id AND
a.residue_id = r.residue_id AND
e.res_count >= 30 AND -- Includes not too small peptides
e.model_count > 1 AND -- Dismiss entries without true ensemble
r.name = 'LEU' AND
a.cs_ssa = 1 AND -- only ssa according to BMRB (stereoAssigned flag in CING)
a.name LIKE 'CD%';
order by e.pdb_id, c.name, r.number, a.name;





-- Can't be done in one blow.
ALTER TABLE nrgcing.cingatom ALTER COLUMN wi_mo2chk TYPE VARCHAR(255);
ALTER TABLE nrgcing.cingatom ALTER COLUMN wi_mo2chk SET DEFAULT NULL;
ALTER TABLE nrgcing.cingatom ALTER COLUMN atom_id  PRIMARY KEY;
ALTER TABLE nrgcing.cingatom ADD PRIMARY KEY (atom_id);

COPY nrgcing.cingentry     FROM 'nrgcing.cingentry.csv'   CSV HEADER;
COPY nrgcing.cingentry ( entry_id,name,bmrb_id,casd_id,pdb_id,is_solid,is_paramagnetic,is_membrane,is_multimeric,chothia_class,protein_count,dna_count,rna_count,dna_rna_hybrid_count,is_minimized,software_collection,software_processing,software_analysis,software_struct_solution,software_refinement,in_recoord,in_casd,in_dress,ranges,res_count,model_count,distance_count,dihedral_count,rdc_count,peak_count,cs_count,cs1h_count,cs13c_count,cs15n_count,wi_angchk,wi_bbcchk,wi_bmpchk,wi_bndchk,wi_c12chk,wi_chichk,wi_flpchk,wi_hndchk,wi_inochk,wi_nqachk,wi_omechk,wi_pl2chk,wi_pl3chk,wi_plnchk,wi_quachk,wi_ramchk,wi_rotchk,pc_gf,pc_gf_phipsi,pc_gf_chi12,pc_gf_chi1,noe_compl4,rog )
FROM '$cwd/casdcing.cingentry.csv'    CSV HEADER;

entry_id,name,bmrb_id,casd_id,pdb_id,is_solid,is_paramagnetic,is_membrane,is_multimeric,chothia_class,protein_count,dna_count,rna_count,dna_rna_hybrid_count,is_minimized,software_collection,software_processing,software_analysis,software_struct_solution,software_refinement,in_recoord,in_casd,in_dress,ranges,res_count,model_count,distance_count,dihedral_count,rdc_count,peak_count,cs_count,cs1h_count,cs13c_count,cs15n_count,wi_angchk,wi_bbcchk,wi_bmpchk,wi_bndchk,wi_c12chk,wi_chichk,wi_flpchk,wi_hndchk,wi_inochk,wi_nqachk,wi_omechk,wi_pl2chk,wi_pl3chk,wi_plnchk,wi_quachk,wi_ramchk,wi_rotchk,pc_gf,pc_gf_phipsi,pc_gf_chi12,pc_gf_chi1,pc_rama_core,pc_rama_allow,pc_rama_gener,pc_rama_disall,noe_compl4,rog,dis_max_all,dis_rms_all,dis_av_all,dis_av_viol,dis_c1_viol,dis_c3_viol,dis_c5_viol,dih_max_all,dih_rms_all,dih_av_all,dih_av_viol,dih_c1_viol,dih_c3_viol,dih_c5_viol

-- A couple of new items
SELECT name, rdc_count+distance_count+dihedral_count as restr_count,
rdc_count, dihedral_count, distance_count
-- distance_count, distance_count_sequential, distance_count_intra_residual, distance_count_medium_range, distance_count_long_range, distance_count_ambiguous
FROM "nrgcing"."cingentry" e
order by name;

SELECT name, distance_count, cs_count
FROM "nrgcing"."cingentry" e
where
distance_count = 0 AND
cs_count > 0
order by name;

SELECT name,
    ssa_count         ,
    ssa_swap_count    ,
    ssa_deassign_count
FROM "nrgcing"."cingentry" e
where ssa_count IS NOT NULL
order by name;

-- for H_None, N_None, C_3 and 
SELECT name, resonancelist_id, atomclass,
to_char(csd, '0.99') as csds,
to_char(csd_err, '0.99') as csd_errs
FROM "nrgcing"."cingentry" e, nrgcing.cingresonancelistperatomclass pa
where e.entry_id = pa.entry_id AND
atomclass = 'C_3'
order by csd, resonancelist_id;



delete FROM "nrgcing"."cingentry" e;

SELECT name, res_count FROM "nrgcing"."cingentry" e
where res_count > 9
order by res_count asc
limit 10;

DROP TABLE IF EXISTS nrgcing.aa;
CREATE table nrgcing.aa
(
    name                           VARCHAR(25)
);
COPY nrgcing.aa      FROM '/Users/jd/workspace35/cing/Tests/data/cing/aa.csv'    CSV HEADER;

-- find unique residue names
SELECT r.name, e.name, count( r.name )
FROM
"nrgcing"."cingentry" e,
"nrgcing"."cingresidue" r,
"nrgcing"."cingchain" c
 where
r.entry_id = e.entry_id AND
c.entry_id = e.entry_id AND
r.name  in ( 'ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'GLY', 'HIS', 'ILE', 'LEU', 'LYS', 'MET', 'PHE', 'PRO', 'SER', 'THR', 'TRP', 'TYR', 'VAL',  'CYSS', 'HISH', 'HISE', 'GLUH', 'ASPH', 'cPRO')
group by r.name, e.name
order by count(r.name) desc;

SELECT r.name, e.name, e.distance_count_long_range, count( r.name )
FROM
"nrgcing"."cingentry" e,
"nrgcing"."cingresidue" r,
"nrgcing"."cingchain" c
 where
r.entry_id = e.entry_id AND
c.entry_id = e.entry_id AND
e.is_multimeric = false AND e.res_count > 30 AND
e.distance_count_long_range > 30 AND r.distance_count > 1 AND
e.rdc_count = 0 AND
r.name  not in like 'LYSx'
group by r.name, e.name, e.distance_count_long_range
order by count(r.name) asc;


SELECT e.name, e.distance_count_long_range, e.res_count 
FROM
"nrgcing"."cingentry" e
where
e.name = '1brv'


SELECT count(*) 
SELECT *
SELECT e.name, e.distance_count_long_range, e.res_count 
FROM
"nrgcing"."cingentry" e
where
e.is_multimeric = true AND e.res_count < 50 AND
e.distance_count_long_range > 30 AND
e.rdc_count = 0 AND e.chothia_class IS NOT NULL


order by e.distance_count_long_range asc;


-- Get small dimers
SELECT *
FROM
"nrgcing"."cingentry" e
where
e.is_multimeric = true AND e.res_count < 50 AND
e.distance_count_long_range > 30 AND
e.rdc_count = 0 AND 
e.chothia_class IS NOT NULL AND e.chothia_class !=3


-- 
SELECT name, queen_information, queen_uncertainty1, queen_uncertainty2
FROM "casdcing"."cingentry" e
where queen_information IS NOT NULL
order by name
;

SELECT name
FROM "casdcing"."cingentry" e
where queen_information IS NULL
order by name
;

SELECT s.pdbid AS pdb_id, SUM(p2.val * p3.val) AS weight
FROM pdbj.brief_summary s
JOIN pdbj."E://entity" e ON e.docid = s.docid
JOIN "//entity/pdbx_number_of_molecules" p2    ON p2.docid = e.docid AND p2.pos BETWEEN e.pstart AND e.pend
JOIN "//entity/formula_weight" p3              ON p3.docid = e.docid AND p3.pos BETWEEN e.pstart AND e.pend
GROUP BY s.pdbid
INTO TABLE nrgcing.cingsummary

create table nrgcing.cingsummary as
SELECT s.pdbid AS pdb_id, SUM(p2.val * p3.val) AS weight
FROM pdbj.brief_summary s
JOIN pdbj."E://entity" e ON e.docid = s.docid
JOIN "//entity/pdbx_number_of_molecules" p2    ON p2.docid = e.docid AND p2.pos BETWEEN e.pstart AND e.pend
JOIN "//entity/formula_weight" p3              ON p3.docid = e.docid AND p3.pos BETWEEN e.pstart AND e.pend
GROUP BY s.pdbid

SELECT count(*) from nrgcing.drlist;
SELECT count(*) from nrgcing.dr;
SELECT count(*) from nrgcing.cingatom;

-- Get the non-ambi dr pairs for leucine HG using only 3 relations.
SELECT e.name, dl.number as dl_number, d.dr_id, d.member_id, d.upper, d.chain_name_1, d.residue_name_1, d.residue_num_1, d.atom_name_1
FROM
nrgcing.cingentry e,
nrgcing.drlist dl,
nrgcing.dr d
 where
d.entry_id = e.entry_id AND
d.drlist_id = dl.drlist_id AND (
    (d.atom_name_1  = 'HG' AND d.residue_name_1 = 'LEU' ) 
OR  (d.atom_name_2  = 'HG' AND d.residue_name_2 = 'LEU' )
) AND
d.item_logic_code IS NULL
order by e.name, dl.number, d.dr_id, d.member_id asc;

-- Then the similar thing using 6 relations
-- Get the non-ambi dr pairs for where the first atom is a leucine HG
SELECT count(*) FROM nrgcing.cingentry;
SELECT e.name, dl.number as dl_number, d.dr_id, d.member_id, d.upper, 
        a.name as a_name, r.name as r_name, r.number as r_number, c.name as c_name
FROM
nrgcing.cingentry e,
nrgcing.cingchain c,
nrgcing.cingresidue r,
nrgcing.cingatom a,
nrgcing.drlist dl,
nrgcing.dr d
 where
d.entry_id = e.entry_id AND
d.drlist_id = dl.drlist_id AND
a.atom_id  = d.atom_id_1 AND 
a.residue_id  = r.residue_id AND 
a.chain_id  = c.chain_id AND 
a.name = 'HG' AND 
r.name = 'LEU' AND 
d.item_logic_code IS NULL
order by e.name, dl.number, d.dr_id, d.member_id asc;

SELECT e.name, r.cs_count,
       r.name as r_name, r.number as r_number, c.name as c_name
FROM
nrgcing.cingentry e,
nrgcing.cingchain c,
nrgcing.cingresidue r
 where
r.entry_id = e.entry_id AND
c.entry_id = e.entry_id AND
r.name = 'ALA' AND
r.cs_count > 13
order by r.cs_count desc
limit 100
;

SELECT r.residue_id, count(*) as r_cs_count
FROM
nrgcing.cingresidue r,
nrgcing.cingatom a
 where
a.residue_id = r.residue_id AND
a.cs IS NOT NULL
group by r.residue_id
order by r_cs_count desc
limit 100
;

SELECT e.name, r.name as r_name, r.number as r_number, c.name as c_name,
    r.cs_count
FROM
nrgcing.cingentry e,
nrgcing.cingchain c,
nrgcing.cingresidue r
 where
r.entry_id = e.entry_id AND
c.entry_id = e.entry_id AND
r.residue_id = 615999
;

ALTER TABLE nrgcing.cingentry ADD COLUMN rog_str VARCHAR(255) DEFAULT NULL;
ALTER TABLE nrgcing.cingentry ADD COLUMN chothia_class_str VARCHAR(255) DEFAULT NULL;

update nrgcing.cingentry set rog_str='green' where rog = 0; 
update nrgcing.cingentry set rog_str='orange' where rog = 1; 
update nrgcing.cingentry set rog_str='red' where rog = 2; 

update nrgcing.cingentry set chothia_class_str='alpha' where chothia_class = 0; 
update nrgcing.cingentry set chothia_class_str='beta' where chothia_class = 1; 
update nrgcing.cingentry set chothia_class_str='a/b' where chothia_class = 2; 
update nrgcing.cingentry set chothia_class_str='coil' where chothia_class = 3; 

update nrgcing.cingentry set bmrb_id=NULL where bmrb_id = 9; 

ALTER TABLE nrgcing.cingresidue ADD COLUMN is_present BOOLEAN DEFAULT NULL;
