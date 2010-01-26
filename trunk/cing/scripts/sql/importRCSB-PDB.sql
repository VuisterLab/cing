DROP TABLE IF EXISTS hasExpData;
CREATE table hasExpData
(
    pdb_id                        CHAR(4)
);

COPY hasExpData
FROM '/Users/jd/tmp/cingTmp/hasExpData.csv';
