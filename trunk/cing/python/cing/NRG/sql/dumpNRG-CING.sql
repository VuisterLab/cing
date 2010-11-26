-- * Run by command like:
-- * psql --quiet pdbmlplus pdbj < $CINGROOT/python/cing/NRG/sql/dumpNRG-CING.sql
-- Then follow up by doing from Stella:
-- scp -r -P 39676 localhost-nmr:$cwd .

COPY (SELECT * FROM nrgcing.cingentry) 				TO '$cwd/nrgcing.cingentry.csv' WITH CSV HEADER;
COPY (SELECT * FROM nrgcing.cingchain) 				TO '$cwd/nrgcing.cingchain.csv' WITH CSV HEADER;
COPY (SELECT * FROM nrgcing.cingresidue) 			TO '$cwd/nrgcing.cingresidue.csv' WITH CSV HEADER;
COPY (SELECT * FROM nrgcing.cingatom) 				TO '$cwd/nrgcing.cingatom.csv' WITH CSV HEADER;
-- derived tables
COPY (SELECT * FROM nrgcing.cingsummary) 			TO '$cwd/nrgcing.cingsummary.csv' WITH CSV HEADER;
COPY (SELECT * FROM nrgcing.entry_list_selection) 	TO '$cwd/nrgcing.entry_list_selection.csv' WITH CSV HEADER;

-- usefull tables DEFAULT is to have these commented out.
-- No header!
--COPY (SELECT pdb_id FROM nrgcing.cingentry order by pdb_id limit 9999 )         TO '$cwd/nrgcing.pdb_ids.csv' WITH CSV;
