

-- select the vacuum settings on/off.
select * from pg_settings where name like 'autovacuum';
-- select all settings from a category within.
select * from pg_settings where category like 'Autovacuum';

-- max_locks_per_transaction needs to be 256 min by pdbj recommendations
select * from pg_settings where category like 'Resource%';

set pg_settings.extra_float_digits = -10


select * from tmptable;

select * from entry;

UPDATE entry,tmpTable  SET entry.pdbx_SG_project_XXXinitial_of_center = tmpTable.par WHERE entry.pdb_id = tmpTable.pdb_id;

insert entry(pdb_id) values ('1brv'),('1sjg');

SELECT e.pdb_id, AVG(R.CHK_D1D2), STDDEV(R.CHK_D1D2), count(*) as N, MIN(R.CHK_D1D2), MAX(R.CHK_D1D2)
  FROM pdbcing.cingRESIDUE AS R, pdbcing.cingENTRY AS E
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