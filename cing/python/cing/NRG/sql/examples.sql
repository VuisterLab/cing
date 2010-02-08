-- Entry count 62635 on Thu Jan 21 10:41:06 CET 2010
SELECT count(*) FROM brief_summary;

-- entry count per experimentele technique
select count(*), exptl_method
from pdbj.brief_summary
group by exptl_method
order by count(*) desc;


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

SELECT pdbid, summary
FROM brief_summary b
WHERE '{"Vriend, G."}' <@ citation_author_pri

SELECT count(*) as c, citation_author_pri
FROM brief_summary s
JOIN "//exptl/@method" p1 ON s.docid = p1.docid
WHERE p1.val LIKE '%NMR'
group by citation_author_pri
order by count(*) desc
LIMIT 100;

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

-- Get listing of non-SG PDB ids by primary citation author.
SELECT count(s.pdbid), p2.val AS primary_citation_author_name
FROM brief_summary s
JOIN "E://citation_author" e1 ON e1.docid = s.docid
JOIN "//citation_author/@citation_id" p1
    ON p1.docid = e1.docid AND p1.pos BETWEEN e1.pstart AND e1.pend
JOIN "//citation_author/@name" p2
    ON p2.docid = e1.docid AND p2.pos BETWEEN e1.pstart AND e1.pend
JOIN "//exptl/@method" p3 ON s.docid = p3.docid
WHERE p3.val LIKE '%NMR'
AND p1.val = 'primary'
--AND p2.val = 'Doreleijers, J.F.'
AND s.docid NOT IN ( select docid from "//pdbx_SG_project/initial_of_center")
group by primary_citation_author_name
--order by p2.val asc
order by count(s.pdbid) desc
limit 100;


-- Get NMR entries NOT from SG projects
SELECT count(s.pdbid)
FROM brief_summary s
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




