-- * Run by command like:
-- python -u $CINGROOT/python/cing/NRG/runSqlForSchema.py nrgcing    $CINGROOT/python/cing/NRG/sql/loadDB-CING_psql.sql    $D/NRG-CING/pgsql

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

COPY nrgcing.tmppc 		FROM 'nrgcing.tmppc.csv' CSV HEADER;
