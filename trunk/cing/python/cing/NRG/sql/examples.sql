-- Entry count 62635 on Thu Jan 21 10:41:06 CET 2010
SELECT count(*) FROM brief_summary;

-- entry count per experimentele technique
select count(*), exptl_method
from pdbj.brief_summary
group by exptl_method
order by count(*) desc;

SELECT S.PDBID, P.VAL AS "resolution"
  FROM
       "pdbj".BRIEF_SUMMARY AS S JOIN "pdbj"."//refine/ls_d_res_high" AS P ON S.DOCID = P.DOCID
  WHERE P.VAL <= 1.0


SELECT table_name FROM information_schema.tables
where table_schema = 'pdbj' AND table_name like '%exp%data%'
limit 200;

SELECT * FROM information_schema.tables
where table_schema = 'pdbj'
AND table_name like '%SG_project%'
limit 2;

SELECT s.pdbid, p2.val
FROM brief_summary s
JOIN "//exptl/@method" p1 ON s.docid = p1.docid
JOIN "//pdbx_SG_project/initial_of_center" p2 ON s.docid = p2.docid
WHERE p1.val LIKE '%NMR'
LIMIT 10;

SELECT pdbid
FROM brief_summary b
WHERE '{"Vriend, G."}' <@ citation_author_pri
limit  10;

-- Below query isn't specific to one but to all authors; not very useful.
SELECT count(*) as c, citation_author_pri
FROM brief_summary s
JOIN "//exptl/@method" p1 ON s.docid = p1.docid
WHERE p1.val LIKE '%NMR'
group by citation_author_pri
order by count(*) desc
LIMIT 10;

WITH slen(docid, entity_id, len) AS
(SELECT docid, p.val, COUNT(*)
 FROM "//entity_poly_seq/@entity_id" p
 GROUP BY docid,p.val)
SELECT b.pdbid, SUM(e.pdbx_number_of_molecules * s.len)
FROM brief_summary b
JOIN entity e ON e.docid = b.docid
JOIN slen s ON s.docid = e.docid AND s.entity_id = e.id
JOIN "//exptl/@method" p1 ON s.docid = p1.docid
WHERE p1.val LIKE '%NMR'
GROUP BY b.pdbid
LIMIT 100;

-- Find NMR entries that were only released after 4 years.
SELECT pdbid, deposition_date, release_date
FROM brief_summary b
JOIN "//exptl/@method" p1 ON b.docid = p1.docid
WHERE p1.val LIKE '%NMR'
AND release_date > deposition_date + interval '4 year'
ORDER BY deposition_date desc
LIMIT 10;

-- Get listing of non-SG PDB pdbid)
select s.docid FROM brief_summary s
JOIN "//exptl/@method" p1 ON s.docid = p1.docid
WHERE p1.val LIKE '%NMR'
--AND s.pdbid = '1brv'
AND s.docid NOT IN ( select docid from "//pdbx_SG_project/initial_of_center")
LIMIT 10;

-- Count number of residues per NMR entry since last year.
WITH slen(docid, entity_id, len) AS
(SELECT docid, p.val, COUNT(*)
 FROM "//entity_poly_seq/@entity_id" p
 GROUP BY docid,p.val)
SELECT SUM(e.pdbx_number_of_molecules * s.len) AS l, b.pdbid
FROM brief_summary b
JOIN entity e ON e.docid = b.docid
JOIN slen s ON s.docid = e.docid AND s.entity_id = e.id
JOIN "//exptl/@method" p1 ON s.docid = p1.docid
WHERE p1.val LIKE '%NMR'
AND b.release_date >= '1-1-2009'
GROUP BY b.pdbid
order by l desc;




-- Count number of residues per NMR entry since last year.
WITH slen(docid, entity_id, len) AS
(SELECT docid, p.val, COUNT(*)
 FROM "//entity_poly_seq/@entity_id" p
 GROUP BY docid,p.val)
SELECT SUM(e.pdbx_number_of_molecules * s.len) AS l, b.pdbid
FROM brief_summary b
JOIN entity e ON e.docid = b.docid
JOIN slen s ON s.docid = e.docid AND s.entity_id = e.id
JOIN "//exptl/@method" p1 ON s.docid = p1.docid
WHERE p1.val LIKE '%NMR'
AND b.release_date >= '1-1-2009'
order by l desc
limit 10;

-- E.g. //entity/formula_weight is documented at:
-- http://mmcif.pdb.org/dictionaries/mmcif_pdbx.dic/Items/_entity.formula_weight.html
SELECT p2.val AS number_of_molecules,p3.val AS formula_weight, p1.val as type
FROM brief_summary s
JOIN "E://entity" e                         ON e.docid = s.docid
JOIN "//entity/type" p1                     ON p1.docid = e.docid AND p1.pos BETWEEN e.pstart AND e.pend
JOIN "//entity/pdbx_number_of_molecules" p2 ON p2.docid = e.docid AND p2.pos BETWEEN e.pstart AND e.pend
JOIN "//entity/formula_weight" p3           ON p3.docid = e.docid AND p3.pos BETWEEN e.pstart AND e.pend
WHERE s.pdbid = '1ai0'


SELECT e.pdb_id, bs.deposition_date FROM "nrgcing"."cingentry" as e, brief_summary bs
where e.wi_ramchk > 4.0 AND
e.pdb_id = bs.pdbid;




