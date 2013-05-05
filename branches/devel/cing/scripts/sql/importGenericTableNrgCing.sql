-- NOT USED AT THE MOMENT

-- live results from filesystem.
-- TABLE_NAME will be replaced by type
-- TABLE_KEY_COLUMN (like pdb_id)
-- TABLE_KEY_TYPE (like CHAR(4))
-- DATA_TYPE
-- COLUMN_NAME too.
DROP TABLE IF EXISTS tmpTable;
CREATE table tmpTable
(
    TABLE_KEY_COLUMN              TABLE_KEY_TYPE,
    par                           DATA_TYPE
);


LOAD DATA INFILE
    '/Users/jd/tmp/cingTmp/tmpTable.csv'
    INTO TABLE tmpTable
    FIELDS TERMINATED BY ','
    OPTIONALLY ENCLOSED BY '\"'
    LINES  TERMINATED BY '\n';

UPDATE TABLE_NAME,tmpTable
SET TABLE_NAME.COLUMN_NAME = tmpTable.par
WHERE TABLE_NAME.TABLE_KEY_COLUMN = tmpTable.TABLE_KEY;

