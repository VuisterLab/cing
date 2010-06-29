select * from tmptable;

select * from entry;

UPDATE entry,tmpTable  SET entry.pdbx_SG_project_XXXinitial_of_center = tmpTable.par WHERE entry.pdb_id = tmpTable.pdb_id;

insert entry(pdb_id) values ('1brv'),('1sjg');

SELECT e.pdb_id, AVG(R.CHK_D1D2), STDDEV(R.CHK_D1D2), count(*) as N, MIN(R.CHK_D1D2), MAX(R.CHK_D1D2)
  FROM RESIDUE AS R, ENTRY AS E
  WHERE R.ENTRY_ID = E.ENTRY_ID
--  AND E.pdb_id = '1brv'
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
WHERE p.val <= 2.0


set pg_settings.extra_float_digits = -10; -- fails.
--  AND E.casd_id = 'AR3436AFrankfurt'
