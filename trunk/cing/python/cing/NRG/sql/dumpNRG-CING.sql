COPY (SELECT * FROM entry) TO '/Users/jd/tmp/pgsql/entry.csv' WITH CSV HEADER;
COPY (SELECT * FROM chain) TO '/Users/jd/tmp/pgsql/chain.csv' WITH CSV HEADER;
COPY (SELECT * FROM residue) TO '/Users/jd/tmp/pgsql/residue.csv' WITH CSV HEADER;
