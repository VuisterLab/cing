-- * Run by command like:
-- * psql --quiet pdbmlplus pdbj < $CINGROOT/python/cing/NRG/sql/dumpCASP-NMR-CING.sql
-- Then follow up by doing from Stella:
-- scp -r -P 39676 localhost-nmr:/Users/jd/NRG-CING/pgsql .

COPY (SELECT * FROM caspcing.cingentry) 			TO '/Library/WebServer/Documents/CASP-NMR-CING/pgsql/caspcing.cingentry.csv' WITH CSV HEADER;
COPY (SELECT * FROM caspcing.cingchain) 			TO '/Library/WebServer/Documents/CASP-NMR-CING/pgsql/caspcing.cingchain.csv' WITH CSV HEADER;
COPY (SELECT * FROM caspcing.cingresidue) 			TO '/Library/WebServer/Documents/CASP-NMR-CING/pgsql/caspcing.cingresidue.csv' WITH CSV HEADER;
COPY (SELECT * FROM caspcing.cingatom) 				TO '/Library/WebServer/Documents/CASP-NMR-CING/pgsql/caspcing.cingatom.csv' WITH CSV HEADER;
-- derived tables
COPY (SELECT * FROM caspcing.cingsummary) 			TO '/Library/WebServer/Documents/CASP-NMR-CING/pgsql/caspcing.cingsummary.csv' WITH CSV HEADER;
COPY (SELECT * FROM caspcing.entry_list_selection) 	TO '/Library/WebServer/Documents/CASP-NMR-CING/pgsql/caspcing.entry_list_selection.csv' WITH CSV HEADER;
