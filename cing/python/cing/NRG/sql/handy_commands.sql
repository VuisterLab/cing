

-- select the vacuum settings on/off.
select * from pg_settings where name like 'autovacuum';
-- select all settings from a category within.
select * from pg_settings where category like 'Autovacuum';

-- max_locks_per_transaction needs to be 256 min by pdbj recommendations
select name, setting, unit  from pg_settings where category like 'Resource%';

set pg_settings.extra_float_digits = -10


select * from tmptable;

select * from entry;

UPDATE entry,tmpTable  SET entry.pdbx_SG_project_XXXinitial_of_center = tmpTable.par WHERE entry.pdb_id = tmpTable.pdb_id;

insert entry(pdb_id) values ('1brv'),('1sjg');

SELECT e.casd_id, AVG(R.CHK_D1D2), STDDEV(R.CHK_D1D2), count(*) as N, MIN(R.CHK_D1D2), MAX(R.CHK_D1D2)
  FROM casdcing.cingRESIDUE AS R, casdcing.cingENTRY AS E
  WHERE R.ENTRY_ID = E.ENTRY_ID
  AND R.CHK_D1D2 <> 'NaN' -- Yes, stupid but needs to be excluded manually.
  AND R.CHK_D1D2 < -0.8
  GROUP BY e.casd_id
  order by N asc;

  order by AVG(R.CHK_D1D2) desc;
  AND R.CHK_D1D2 < -0.5
  and (e.pdb_id = '3i40' or e.pdb_id = '2xdy')

SELECT e.pdb_id, AVG(R.CHK_D1D2), STDDEV(R.CHK_D1D2), count(*) as N, MIN(R.CHK_D1D2), MAX(R.CHK_D1D2)
  FROM nrgcing.cingRESIDUE AS R, nrgcing.cingENTRY AS E
  WHERE R.ENTRY_ID = E.ENTRY_ID
  AND R.CHK_D1D2 <> 'NaN' -- Yes, stupid but needs to be excluded manually.
  GROUP BY e.pdb_id
  order by AVG(R.CHK_D1D2) desc;

SELECT e.casd_id, R.CHK_D1D2
  FROM RESIDUE AS R, ENTRY AS E
  WHERE R.ENTRY_ID = E.ENTRY_ID
  AND E.casd_id = 'NeR103AOrg'
  AND R.number = 2


SELECT s.pdbid, p.val AS "resolution"
FROM brief_summary s
JOIN "//refine/ls_d_res_high" p ON s.docid = p.docid
WHERE s.pdbid in ( SELECT pdb_id from pdbcing.cingENTRY)

SELECT count(s.pdbid)
FROM brief_summary s
JOIN "//refine/ls_d_res_high" p ON s.docid = p.docid
WHERE s.pdbid in ( SELECT pdb_id from pdbcing.cingENTRY)


set pg_settings.extra_float_digits = -10; -- fails.
--  AND E.casd_id = 'AR3436AFrankfurt'

--SELECT s.pdbid , p.entity_id , p.pdbx_seq_one_letter_code_can
--FROM brief_summary s
--JOIN  entity_poly p ON p.docid = s.docid
--WHERE s.pdbid like '1br%'

WITH slen(docid, entity_id, len) AS
(SELECT docid, p.val, COUNT(*)
 FROM "//entity_poly_seq/@entity_id" p
 GROUP BY docid,p.val)
SELECT b.pdbid, SUM(e.pdbx_number_of_molecules * s.len)
FROM brief_summary b
JOIN entity e ON e.docid = b.docid
JOIN slen s ON s.docid = e.docid AND s.entity_id = e.id
GROUP BY b.pdbid

drop table if exists pdbcing.cingsummary;
CREATE VIEW pdbcing.cingsummary AS
SELECT s.pdbid AS pdb_id, SUM(p2.val * p3.val) AS weight
FROM brief_summary s
JOIN "E://entity" e ON e.docid = s.docid
JOIN "//entity/type" p1
        ON p1.docid = e.docid AND p1.pos BETWEEN e.pstart AND e.pend
JOIN "//entity/pdbx_number_of_molecules" p2
        ON p2.docid = e.docid AND p2.pos BETWEEN e.pstart AND e.pend
JOIN "//entity/formula_weight" p3
        ON p3.docid = e.docid AND p3.pos BETWEEN e.pstart AND e.pend
WHERE p1.val = 'polymer'
GROUP BY s.pdbid
;

drop table if exists nrgcing.entry_list_selection;
CREATE VIEW nrgcing.entry_list_selection AS
SELECT e.pdb_id
  FROM "nrgcing".CINGENTRY E,  brief_summary s, pdbcing.cingsummary cingsummary
  WHERE e.pdb_id = S.pdbid
  AND e.pdb_id = cingsummary.pdb_id
  AND E.MODEL_COUNT > 9
  and cingsummary.weight > 3500.0 -- about 30 residues
  AND '{2}' <@ S.chain_type -- contains at least one protein chain.
  order by e.model_count;

select count() from nrgcing.cingentry;

into nrgcing.entry_list_selection(pdb_id)

SELECT e.pdb_id, e.model_count, S.chain_type
  FROM "nrgcing".CINGENTRY E,  brief_summary s, nrgcing.cingsummary cingsummary
  WHERE e.pdb_id = S.pdbid
  AND e.pdb_id = cingsummary.pdb_id
  AND E.MODEL_COUNT > 9
  and cingsummary.weight > 3500.0 -- about 30 residues
  AND '{2}' <@ S.chain_type -- contains at least one protein chain.
  order by e.model_count;


-- Selects a,b,a/b,a+b protein classes
select e.pdb_id, e.wi_bbcchk
from nrgcing.entry_list_selection es, nrgcing.cingentry e
where es.pdb_id = e.pdb_id
order by e.wi_bbcchk asc
limit 10
;

select count(*) from nrgcing.cingentry;
select count(*) from nrgcing.cingsummary;
select count(*) from nrgcing.entry_list_selection;
select * from nrgcing.cingentry where pdb_id='1brv';


drop table if exists nrgcing.cingsummary cascade;
CREATE table nrgcing.cingsummary AS
SELECT s.pdbid AS pdb_id, SUM(p2.val * p3.val) AS weight
FROM brief_summary s
JOIN "E://entity" e ON e.docid = s.docid
JOIN "//entity/type" p1
        ON p1.docid = e.docid AND p1.pos BETWEEN e.pstart AND e.pend
JOIN "//entity/pdbx_number_of_molecules" p2
        ON p2.docid = e.docid AND p2.pos BETWEEN e.pstart AND e.pend
JOIN "//entity/formula_weight" p3
        ON p3.docid = e.docid AND p3.pos BETWEEN e.pstart AND e.pend
WHERE p1.val = 'polymer'
GROUP BY s.pdbid;

drop table if exists nrgcing.entry_list_selection cascade;
CREATE table nrgcing.entry_list_selection AS
SELECT e.pdb_id
  FROM nrgcing.CINGENTRY E,  brief_summary s, nrgcing.cingsummary cingsummary
  WHERE e.pdb_id = S.pdbid
  AND e.pdb_id = cingsummary.pdb_id
  AND E.MODEL_COUNT > 9
  and cingsummary.weight > 3500.0 -- about 30 residues
  AND '{2}' <@ S.chain_type; -- contains at least one protein chain.



SELECT E.name,  R.name, R.number, queen_information, queen_uncertainty1, queen_uncertainty2

SELECT E.name,  avg( r.queen_information ), count(*), e.res_count
FROM casdcing.CINGENTRY E, "casdcing"."cingresidue" R
where E.entry_id = R.entry_id
and queen_information IS NOT NULL AND queen_information != 0.0
group by e.name, e.res_count
order by E.name;


SELECT E.name,  R.residue_id, R.name, R.number,R.rmsd_backbone, R.rmsd_sidechain
FROM casdcing.CINGENTRY E, "casdcing"."cingresidue" R
where E.entry_id = R.entry_id
AND E.name = 'CGR26APiscataway'
order by E.name, R.number;

# Select for Vincent the protein entries with RDCs (about 350 today)
COPY (
SELECT e.pdb_id, e.rdc_count
  FROM nrgcing.CINGENTRY E,  brief_summary s, nrgcing.cingsummary cingsummary
  WHERE e.pdb_id = S.pdbid
  AND e.pdb_id = cingsummary.pdb_id
  AND '{2}' <@ S.chain_type
  AND e.rdc_count > 0
) TO '/tmp/rdc_entries.csv' WITH CSV HEADER;

SELECT pdb_id, model_count
FROM nrgcing.CINGENTRY
WHERE model_count > 50
order by model_count

-- delete from nrgcing.cingentry;

select * from nrgcing.cingatom
where name = 'HA'

summaryHeaderList = 'name bmrb_id rog distance_count cs_count chothia_class chain_count res_count'.split()

delete from nrgcing.cingentry;
insert into nrgcing.cingentry(rev_first, name, bmrb_id, rog, distance_count, cs_count, chothia_class, chain_count, res_count) values 
(   3, '2lfh', 1234, 0, 263, 50, 0, 1,  32),
(   3, '9pcy', 9999, 1,   0,  0, 2, 2, 100),
(   3, '1cjg', 4020, 2, 263, 50, 0, 1,   9),
(   3, '1brv', 4020, 0, 263, 50, 0, 1,  32),
(   3, '9pcy', 9999, 1,   0,  0, 2, 2, 100),
(   3, '1cjg', 4020, 2, 263, 50, 0, 1,   9),
(   3, '1brv', 4020, 0, 263, 50, 0, 1,  32),
(   4, '9pcy', 9999, 1,   0,  0, 2, 2, 100),
(   3, '1cjg', 4020, 2, 263, 50, 0, 1,   9),
(   3, '1brv', 4020, 0, 263, 50, 0, 1,  32),
(   3, '9pcy', 9999, 1,   0,  0, 2, 2, 100),
(1234, '1cjg', 4020, 2, 263, 50, 0, 1,   9),
( 123, '1brv', 4020, 0, 263, 50, 0, 1,  32),
(  23, '9pcy', 9999, 1,   0,  0, 2, 2, 100),
(   3, '1cjg', 4020, 2, 263, 50, 0, 1,   9),
(9999, '2hue',    9, 3,   0,  0, 2, 2, 999);
