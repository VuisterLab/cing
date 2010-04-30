COPY (SELECT * FROM entry) TO '/Users/jd/CASD-NMR-CING/pgsql/entry.csv' WITH CSV HEADER;
COPY (SELECT * FROM chain) TO '/Users/jd/CASD-NMR-CING/pgsql/chain.csv' WITH CSV HEADER;
COPY (SELECT * FROM residue) TO '/Users/jd/CASD-NMR-CING/pgsql/residue.csv' WITH CSV HEADER;
COPY (SELECT * FROM atom) TO '/Users/jd/CASD-NMR-CING/pgsql/atom.csv' WITH CSV HEADER;
