select * from tmptable;

select * from entry;

UPDATE entry,tmpTable  SET entry.pdbx_SG_project_XXXinitial_of_center = tmpTable.par WHERE entry.pdb_id = tmpTable.pdb_id;

insert entry(pdb_id) values ('1brv'),('1sjg');


SELECT e.casd_id, to_char(AVG(R.CHK_D1D2), '0.99') as avg, to_char(STDDEV(R.CHK_D1D2), '0.99') as std, to_char(MIN(R.CHK_D1D2), '0.99') as min,
  to_char(MAX(R.CHK_D1D2), '0.99') as max
  FROM RESIDUE AS R, ENTRY AS E
  WHERE R.ENTRY_ID = E.ENTRY_ID
 AND R.CHK_D1D2 <> 'NaN' -- Yes, stupid but needs to be excluded manually.
  GROUP BY e.casd_id
  order by AVG(R.CHK_D1D2) desc

SELECT e.casd_id, R.CHK_D1D2
  FROM RESIDUE AS R, ENTRY AS E
  WHERE R.ENTRY_ID = E.ENTRY_ID
  AND E.casd_id = 'NeR103AOrg'
  AND R.number = 2

set pg_settings.extra_float_digits = -10; -- fails.
--  AND E.casd_id = 'AR3436AFrankfurt'
