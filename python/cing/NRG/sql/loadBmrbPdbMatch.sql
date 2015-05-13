-- * Run by command like:
-- python -u $CINGROOT/python/cing/NRG/runSqlForSchema.py nrgcing    $CINGROOT/python/cing/NRG/sql/loadBmrbPdbMatch.sql    $CINGROOT/data/NRG/bmrbPdbMatch

DROP TABLE IF EXISTS nrgcing.matchbmrb;
CREATE TABLE nrgcing.matchbmrb
(
    pdb_id                         VARCHAR(255) UNIQUE,
    bmrb_id                        INT
);
COPY nrgcing.matchbmrb 		FROM '$cwd/newMany2OneTable.csv' CSV HEADER;

DROP TABLE IF EXISTS nrgcing.matchbmrbadit;
CREATE TABLE nrgcing.matchbmrbadit
(
    bmrb_id                        INT UNIQUE,
    pdb_id                         VARCHAR(255)
);
COPY nrgcing.matchbmrbadit 		FROM '$cwd//adit_nmr_matched_pdb_bmrb_entry_ids.csv' CSV HEADER;


DROP TABLE IF EXISTS nrgcing.bmrb;
CREATE TABLE nrgcing.bmrb
(
    bmrb_id                        INT UNIQUE
);
COPY nrgcing.bmrb 		FROM '$cwd/bmrb.csv' CSV HEADER;

--select pdb_id from nrgcing.matchbmrb
--where pdb_id not in (select pdbid from pdbj.brief_summary)
--order by pdb_id;
--
--select bmrb_id from nrgcing.matchbmrb
--where bmrb_id not in (select bmrb_id from nrgcing.bmrb)
--order by bmrb_id;
--
--
--select bmrb_id from nrgcing.matchbmrbadit
--where bmrb_id not in (select bmrb_id from nrgcing.bmrb)
--order by bmrb_id;
--
--select distinct pdb_id from nrgcing.matchbmrbadit
--where pdb_id not in (select pdbid from pdbj.brief_summary)
--order by pdb_id;

