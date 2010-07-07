
drop table if exists casdcing.cingsummary;
CREATE table casdcing.cingsummary AS
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

drop table if exists casdcing.entry_list_selection;
CREATE table casdcing.entry_list_selection AS
SELECT e.pdb_id
  FROM casdcing.CINGENTRY E,  brief_summary s, casdcing.cingsummary cingsummary
  WHERE e.pdb_id = S.pdbid
  AND e.pdb_id = cingsummary.pdb_id
  AND E.MODEL_COUNT > 9
  and cingsummary.weight > 3500.0 -- about 30 residues
  AND '{2}' <@ S.chain_type -- contains at least one protein chain.
  ;


select count(*) from casdcing.cingentry;
--select * from casdcing.cingentry where pdb_id='1brv';

drop table if exists casdcing.cingsummary cascade;
CREATE table casdcing.cingsummary AS
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

drop table if exists casdcing.entry_list_selection cascade;
CREATE table casdcing.entry_list_selection AS
SELECT e.pdb_id
  FROM casdcing.CINGENTRY E,  brief_summary s, casdcing.cingsummary cingsummary
  WHERE e.pdb_id = S.pdbid
  AND e.pdb_id = cingsummary.pdb_id
  AND E.MODEL_COUNT > 9
  and cingsummary.weight > 3500.0 -- about 30 residues
  AND '{2}' <@ S.chain_type; -- contains at least one protein chain.



select count(*) from casdcing.cingsummary;
select count(*) from casdcing.entry_list_selection;
