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