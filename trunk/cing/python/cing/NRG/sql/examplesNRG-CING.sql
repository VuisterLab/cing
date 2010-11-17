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

