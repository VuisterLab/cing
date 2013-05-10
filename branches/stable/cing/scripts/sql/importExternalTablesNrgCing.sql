-- NOT USED AT THE MOMENT

-- live results from filesystem.
-- DATA_TYPE will be replaced by type
-- COLUMN_NAME too.
DROP TABLE IF EXISTS tmpTable;
CREATE table tmpTable
(
    pdb_id                        CHAR(4),
    par                           VARCHAR(25)
);


LOAD DATA INFILE
    '/Users/jd/tmp/cingTmp/tmpTable.csv'
    INTO TABLE tmpTable
    FIELDS TERMINATED BY ','
    OPTIONALLY ENCLOSED BY '\"'
    LINES  TERMINATED BY '\n';

UPDATE entry,tmpTable
SET entry.pdbx_SG_project_XXXinitial_of_center = tmpTable.par
WHERE entry.pdb_id = tmpTable.pdb_id;


