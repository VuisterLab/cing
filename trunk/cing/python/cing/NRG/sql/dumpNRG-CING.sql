-- * Run by command like:
-- * psql --quiet pdbmlplus pdbj < $CINGROOT/python/cing/NRG/sql/dumpNRG-CING.sql
-- Then follow up by doing from Stella:
-- scp -r -P 39676 localhost-nmr:$cwd .

-- Or edit and execute:
-- python -u $CINGROOT/python/cing/NRG/runSqlForSchema.py casdcing    $CINGROOT/python/cing/NRG/sql/dumpNRG-CING.sql    ~/CASD-NMR-CING/pgsql

COPY (SELECT * FROM casdcing.cingentry) 			TO '$cwd/casdcing.cingentry.csv' WITH CSV HEADER;
COPY (SELECT * FROM casdcing.cingchain) 			TO '$cwd/casdcing.cingchain.csv' WITH CSV HEADER;
COPY (SELECT * FROM casdcing.cingresidue) 			TO '$cwd/casdcing.cingresidue.csv' WITH CSV HEADER;
COPY (SELECT * FROM casdcing.cingatom) 				TO '$cwd/casdcing.cingatom.csv' WITH CSV HEADER;
-- derived tables
COPY (SELECT * FROM casdcing.cingsummary) 			TO '$cwd/casdcing.cingsummary.csv' WITH CSV HEADER;
COPY (SELECT * FROM casdcing.entry_list_selection) 	TO '$cwd/casdcing.entry_list_selection.csv' WITH CSV HEADER;

-- usefull tables DEFAULT is to have these commented out.
-- No header!
--COPY (SELECT pdb_id FROM casdcing.cingentry order by pdb_id limit 9999 )         TO '$cwd/casdcing.pdb_ids.csv' WITH CSV;
