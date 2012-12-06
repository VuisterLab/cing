---
-- FROM HERE execute as user pdbj
---

-- create a schema to play around with entry lists to be submitted to NMR_REDO
DROP SCHEMA IF EXISTS wt;
CREATE SCHEMA wt AUTHORIZATION pbreader;

-- allow user pbreader to use necessary schemas
GRANT USAGE ON SCHEMA wt TO pbreader;
GRANT USAGE ON SCHEMA pdbj TO pbreader;
GRANT USAGE ON SCHEMA nrgcing TO pbreader;
GRANT USAGE ON SCHEMA nmr_redo TO pbreader;

-- Grant SELECT of any column in all tables in necessary schemas
-- GRANT SELECT ON ALL TABLES IN SCHEMA wt TO pbreader; -- only possible from postgres version 9.x
CREATE FUNCTION execute(text) returns void AS $BODY$BEGIN EXECUTE $1; END;$BODY$ language plpgsql;
SELECT execute('GRANT SELECT ON wt.'  || tablename || ' TO pbreader;') FROM pg_tables WHERE schemaname = 'wt';
SELECT execute('GRANT SELECT ON "'  || tablename || '" TO pbreader;') FROM pg_tables WHERE schemaname = 'pdbj';
SELECT execute('GRANT SELECT ON nrgcing.'  || tablename || ' TO pbreader;') FROM pg_tables WHERE schemaname = 'nrgcing';
SELECT execute('GRANT SELECT ON nmr_redo.'  || tablename || ' TO pbreader;') FROM pg_tables WHERE schemaname = 'nmr_redo';
---
-- TO HERE execute as user pdbj
---

---
-- FROM HERE execute as user pbreader
---
-- info on expmethod table: \d pdbj."/datablock/exptlCategory/exptl/@method"
SELECT count(*) FROM pdbj."//exptl/@method" WHERE val = 'SOLUTION NMR';

-- tables having nmr in their name
SELECT * FROM pg_tables WHERE tablename LIKE '%nmr%';

-- tables having software in their name
SELECT * FROM pg_tables WHERE tablename LIKE '%software%'; 
SELECT * FROM pg_tables WHERE tablename LIKE '%nmr_software%';
SELECT * FROM pdbj."//pdbx_nmr_software/name" ORDER BY docid, pos LIMIT 10;
SELECT * FROM pdbj."//pdbx_nmr_software/classification" ORDER BY docid, pos LIMIT 10;

SELECT * FROM pdbj."//pdbx_nmr_software/name" ORDER BY docid, pos LIMIT 10;
SELECT * FROM pdbj."//pdbx_nmr_software/classification" ORDER BY docid, pos LIMIT 10;

-- create a table with NMR software used for each entry
SELECT s.pdbid AS pdb_id, n.val AS software_name, c.val AS software_class
  FROM pdbj.brief_summary s
  JOIN pdbj."E://pdbx_nmr_software" e ON e.docid = s.docid
  JOIN pdbj."//pdbx_nmr_software/name" n
        ON n.docid = e.docid AND n.pos BETWEEN e.pstart AND e.pend
  JOIN pdbj."//pdbx_nmr_software/classification" c
        ON c.docid = e.docid AND c.pos BETWEEN e.pstart AND e.pend
  GROUP BY s.pdbid, n.val, c.val;

--- 100 TEST STRUCTURES
-- only solution nmr
SELECT count(*) FROM pdbj."//exptl/@method" WHERE val = 'SOLUTION NMR';

-- not multiple chains (what if structures have ions in different chains? now exclude)
SELECT count(*) FROM nrgcing.cingentry e WHERE is_multimeric IS FALSE;

-- symmetry only monomer
SELECT count(*) FROM nrgcing.cingentry e WHERE e.symmetry = 'SYMMETRY_C1';

-- exclude HADDOCK entries
SELECT count(s.pdbid) FROM pdbj.brief_summary s JOIN (SELECT distinct docid FROM pdbj."//pdbx_nmr_software/name" n WHERE n.val LIKE '%HADDOCK%') as j USING (docid);

-- exclude entries refined with rdc_restraints
SELECT count(*) FROM nrgcing.cingentry e WHERE e.rdc_count = 0;

-- what to do with SAXS restraints?

-- only entries with > 50 distance restraints (5970 @ 16-11-2012)
-- also exclude many entries with HADDOCK AIR restraints?
SELECT count(*) FROM nrgcing.cingentry e WHERE e.distance_count > 50;
--SELECT avg(e.distance_count), stddev(e.distance_count), min(e.distance_count), max(e.distance_count) FROM nrgcing.cingentry e;

-- only entries with > 10 dihedral restraints (3743 @ 16-11-2012)
SELECT count(*) FROM nrgcing.cingentry e WHERE e.dihedral_count > 10;
--SELECT avg(e.dihedral_count), stddev(e.dihedral_count), min(e.dihedral_count), max(e.dihedral_count) FROM nrgcing.cingentry e;

-- entries deposited less than 5 years ago
SELECT extract(year FROM s.deposition_date) AS year FROM pdbj.brief_summary s WHERE s.deposition_date > (current_date - interval '5 years') ORDER BY year LIMIT 10;

-- entries can have both common and uncommon residues
-- a view with entries containing uncommon residues:
CREATE VIEW wt.enWiUnComRes AS 
SELECT distinct e.name AS name 
FROM nrgcing.cingentry e, nrgcing.cingchain c, nrgcing.cingresidue r 
WHERE c.entry_id = e.entry_id AND r.entry_id = e.entry_id AND r.name NOT IN ( SELECT name FROM nrgcing.normalResidue )
ORDER BY e.name;

-- create table with weight
DROP TABLE IF EXISTS wt.polweight CASCADE;
CREATE TABLE wt.polweight AS
SELECT s.pdbid AS pdbid, SUM(p2.val * p3.val) AS weight
  FROM pdbj.brief_summary s
  JOIN pdbj."E://entity" e ON e.docid = s.docid
  JOIN pdbj."//entity/type" p1
        ON p1.docid = e.docid AND p1.pos BETWEEN e.pstart AND e.pend
  JOIN pdbj."//entity/pdbx_number_of_molecules" p2
        ON p2.docid = e.docid AND p2.pos BETWEEN e.pstart AND e.pend
  JOIN pdbj."//entity/formula_weight" p3
        ON p3.docid = e.docid AND p3.pos BETWEEN e.pstart AND e.pend
  WHERE p1.val = 'polymer'
  GROUP BY s.pdbid;
  
  -- create table entry_list_selection again
DROP TABLE IF EXISTS wt.entry_list_selection CASCADE;
CREATE TABLE wt.entry_list_selection AS
SELECT e.pdb_id
  FROM nrgcing.cingentry e, pdbj.brief_summary s, wt.polweight pw
  WHERE e.pdb_id = s.pdbid
    AND e.pdb_id = pw.pdbid
    AND e.model_count > 9
    AND pw.weight > 3500.0 -- about 30 residues
    AND '{2}' <@ s.chain_type -- contains at least one protein chain.
    AND e.is_multimeric IS FALSE -- no multiple chains (what if structures have ions in different chains? now exclude)
    AND e.symmetry = 'SYMMETRY_C1' -- only monomers
    AND e.name NOT IN (SELECT name FROM wt.enWiUnComRes) -- no entries that have uncommon residues
    AND s.docid NOT IN (SELECT distinct docid FROM pdbj."//pdbx_nmr_software/name" n WHERE n.val LIKE '%HADDOCK%') -- exclude haddock entries
    AND s.deposition_date > (current_date - interval '3 years')
    AND e.distance_count between 500 and 4000
    AND e.dihedral_count between 60 and 300
    AND e.rdc_count = 0
--    AND (s.citation_author::text LIKE '%Vuister, G.W.%'
--    	OR s.citation_author::text LIKE '%Herrmann, T%'
--    	OR s.citation_author::text LIKE '%Guentert, P%'
--    	OR s.citation_author::text LIKE '%Tjandra, N%'
--    	OR s.citation_author::text LIKE '%Clore, M.G.%'
--    	OR s.citation_author::text LIKE '%Grzesiek, S.%'
--    	OR s.citation_author::text LIKE '%Griesinger, C.%'
--    	)
ORDER BY e.pdb_id;

DROP TABLE IF EXISTS wt.entry_list_selection_info CASCADE;
CREATE TABLE wt.entry_list_selection_info AS
SELECT e.pdb_id, e.distance_count, e.dihedral_count
  FROM nrgcing.cingentry e, pdbj.brief_summary s, wt.polweight pw
  WHERE e.pdb_id = s.pdbid
    AND e.pdb_id = pw.pdbid
    AND e.model_count > 9
    AND pw.weight > 3500.0 -- about 30 residues
    AND '{2}' <@ s.chain_type -- contains at least one protein chain.
    AND e.is_multimeric IS FALSE -- no multiple chains (what if structures have ions in different chains? now exclude)
    AND e.symmetry = 'SYMMETRY_C1' -- only monomers
    AND e.name NOT IN (SELECT name FROM wt.enWiUnComRes) -- no entries that have uncommon residues
    AND s.docid NOT IN (SELECT distinct docid FROM pdbj."//pdbx_nmr_software/name" n WHERE n.val LIKE '%HADDOCK%') -- exclude haddock entries
    AND s.deposition_date > (current_date - interval '3 years')
    AND e.distance_count > 50
    AND e.dihedral_count > 50
    AND e.rdc_count = 0
;

DROP TABLE IF EXISTS wt.first_set_comp CASCADE;
CREATE TABLE wt.first_set_comp AS
SELECT re.pdb_id,
		ce.rog AS o_rog, re.rog AS re_rog,
		ce.wi_quachk AS o_wi_quachk, re.wi_quachk AS re_wi_quachk, -- 1 st generation packing quality
		ce.wi_nqachk AS o_wi_nqachk, re.wi_nqachk AS re_wi_nqachk, -- 2 nd generation packing quality
		ce.wi_ramchk AS o_wi_ramchk, re.wi_ramchk AS re_wi_ramchk, -- ramachandran plot appearance
		ce.wi_c12chk AS o_wi_c12chk, re.wi_c12chk AS re_wi_c12chk, -- chi-1/chi-2 rotamer normality
		--ce.wi_rotchk AS o_wi_rotchk, re.wi_rotchk AS re_wi_rotchk, -- rotamer normality
		ce.wi_bbcchk AS o_wi_bbcchk, re.wi_bbcchk AS re_wi_bbcchk, -- backbone normality
		ce.dis_rms_all AS o_dis_rms_all, re.dis_rms_all AS re_dis_rms_all,
		--ce.dis_av_all AS o_dis_av_all, re.dis_av_all AS re_dis_av_all,
		--ce.dis_av_viol AS o_dis_av_viol, re.dis_av_viol AS re_dis_av_viol,
		ce.dis_c5_viol AS o_dis_c5_viol, re.dis_c5_viol AS re_dis_c5_viol,
		ce.dih_rms_all AS o_dih_rms_all, re.dih_rms_all AS re_dih_rms_all,
		--ce.dih_av_all AS o_dih_av_all, re.dih_av_all AS re_dih_av_all,
		--ce.dih_av_viol AS o_dih_av_viol, re.dih_av_viol AS re_dih_av_viol,
		ce.dih_c5_viol AS o_dih_c5_viol, re.dih_c5_viol AS re_dih_c5_viol
	FROM nrgcing.cingentry ce, nmr_redo.cingentry re
	WHERE ce.pdb_id = re.pdb_id
	ORDER BY re.name;
--\copy wt.first_set_comp to '282_BB_comp.tab' csv header