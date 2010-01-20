SELECT s.pdbid , p.entity_id , p.pdbx_seq_one_letter_code_can
FROM brief_summary s
JOIN  entity_poly p ON p.docid = s.docid 
WHERE s.pdbid like '1br%'
