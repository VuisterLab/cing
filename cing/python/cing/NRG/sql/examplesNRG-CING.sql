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

