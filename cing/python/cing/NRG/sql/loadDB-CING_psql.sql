-- * Run by command like:
--   Change to correct sql file in python executable and then:
-- * python -u $CINGROOT/python/cing/NRG/runSqlForSchema.py casdcing

delete from casdcing.cingentry;

COPY casdcing.cingentry 	FROM '/Users/jd/CASD-NMR-CING/pgsql/casdcing.cingentry.csv' CSV HEADER;
COPY casdcing.cingchain 	FROM '/Users/jd/CASD-NMR-CING/pgsql/casdcing.cingchain.csv' CSV HEADER;
COPY casdcing.cingresidue 	FROM '/Users/jd/CASD-NMR-CING/pgsql/casdcing.cingresidue.csv' CSV HEADER;
COPY casdcing.cingatom 		FROM '/Users/jd/CASD-NMR-CING/pgsql/casdcing.cingatom.csv' CSV HEADER;
---- derived tables from createDepTables.sql

-- Should be from db but right now hacked in with:
-- cat ~/pc.grep | gawk '{print substr($0,9,4), $4, $6, $8, $10}' | sed -e 's/%//g' | sed -e 's/ /,/g' >\
--   $D/NRG-CING/pgsql/nrgcing.tmppc.csv
-- Plus the header:
-- pdb_id,pc_rama_core,pc_rama_allow,pc_rama_gener,pc_rama_disall

CREATE TABLE nrgcing.tmppc
(
    pdb_id                         VARCHAR(255) UNIQUE,
    pc_rama_core                      FLOAT DEFAULT NULL,
    pc_rama_allow                      FLOAT DEFAULT NULL,
    pc_rama_gener                      FLOAT DEFAULT NULL,
    pc_rama_disall                      FLOAT DEFAULT NULL
);

COPY nrgcing.tmppc 		FROM '/Library/WebServer/Documents/NRG-CING/pgsql/nrgcing.tmppc.csv' CSV HEADER;

DROP TABLE IF EXISTS nrgcing.matchbmrb;
CREATE TABLE nrgcing.matchbmrb
(
    bmrb_id                        INT,
    pdb_id                         VARCHAR(255) UNIQUE,
    overall_score                  INT DEFAULT NULL
);
COPY nrgcing.matchbmrb 		FROM '/Users/jd/workspace35/cing/data/NRG/score_many2one_new.csv' CSV HEADER;

DROP TABLE IF EXISTS nrgcing.matchbmrbadit;
CREATE TABLE nrgcing.matchbmrbadit
(
    bmrb_id                        INT UNIQUE,
    pdb_id                         VARCHAR(255)
);
COPY nrgcing.matchbmrbadit 		FROM '/Users/jd/workspace35/cing/data/NRG/adit_nmr_matched_pdb_bmrb_entry_ids.csv' CSV HEADER;


DROP TABLE IF EXISTS nrgcing.bmrb;
CREATE TABLE nrgcing.bmrb
(
    bmrb_id                        INT UNIQUE
);
COPY nrgcing.bmrb 		FROM '/Users/jd/workspace35/cing/data/NRG/bmrb.csv' CSV HEADER;

select pdb_id from nrgcing.matchbmrb
where pdb_id not in (select pdbid from pdbj.brief_summary)
order by pdb_id
;

select bmrb_id from nrgcing.matchbmrb
where bmrb_id not in (select bmrb_id from nrgcing.bmrb)
order by bmrb_id
;


select bmrb_id from nrgcing.matchbmrbadit
where bmrb_id not in (select bmrb_id from nrgcing.bmrb)
order by bmrb_id
;
select distinct pdb_id from nrgcing.matchbmrbadit
where pdb_id not in (select pdbid from pdbj.brief_summary)
order by pdb_id
;

