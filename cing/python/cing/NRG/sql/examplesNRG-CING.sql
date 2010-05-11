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
