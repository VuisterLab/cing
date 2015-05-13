-- Execute like:
-- psql nrgcing nrgcing1 < /Users/jd/workspace35/cing/scripts/sql/importRCSB-PDB.sql

DROP TABLE IF EXISTS rcsb_pdb.hasExpData;
CREATE table nrgcing.rcsb_pdb.hasExpData
(
    pdb_id                        CHAR(4)
);

COPY rcsb_pdb.hasExpData
FROM '/Users/jd/tmp/cingTmp/hasExpData.csv';
