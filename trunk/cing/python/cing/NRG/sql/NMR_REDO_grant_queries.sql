DROP TABLE IF EXISTS nrgcing.normalResidue;
create table nrgcing.normalResidue (
    name                     VARCHAR(5) UNIQUE PRIMARY KEY
);
CREATE INDEX indexAaResidue ON nrgcing.normalResidue(name);
insert into nrgcing.normalResidue VALUES
('ALA'),('ARGx'),('ARG'),('ASN'),('ASPH'),('ASP'),('CYSS'),('CYS'),('GLN'),('GLUH'),('GLU'),('GLY'),('HISE'),('HISH'),('HIS'),('ILE'),('LEU'),('LYSx'),('LYS'),('MET'),('PHE'),('cPRO'),('PRO'),('SER'),('THR'),('TRP'),('TYR'),('VAL'),('LGLY'),
('DA'),('A'),('DC'),('C'),('DG'),('G'),('DT'),('U'),
('CA2P'),('ZN'),
('HOH'),
('SS')
;

SELECT 'Number of NRG-CING entries: ' || count(*) FROM nrgcing.cingentry;

SELECT 'Experiment available' ||
count(*) 
FROM nrgcing.cingentry e
WHERE
e.distance_count > 0 OR
e.dihedral_count > 0 OR
e.rdc_count > 0;

SELECT 'Number of entries with Haddock AIR restraints. Overestimate because of failing conversions.' ||
count(*) 
FROM nrgcing.cingentry e
WHERE
e.distance_count < 50 AND
e.distance_count >= 1;

SELECT 'Dihedrals available' ||
count(*)
FROM nrgcing.cingentry e
WHERE
e.dihedral_count > 0;

SELECT 'Residues available' ||
count(*)
FROM nrgcing.cingresidue r;


SELECT 'Distinct ligand count: ' || count( distinct r.name )
FROM nrgcing.cingresidue r
WHERE
r.name NOT IN ( select name from nrgcing.normalResidue );

COPY ( 
SELECT distinct r.name
FROM nrgcing.cingresidue r
WHERE
r.name NOT IN ( select name from nrgcing.normalResidue )
order by r.name
)              TO '/Users/jd/tmp/tmpSql/distinctLigands.csv' WITH CSV HEADER;

COPY ( 
SELECT e.name as entry, c.name as chain, r.number, r.name, r.distance_count
FROM 
nrgcing.cingentry e,
nrgcing.cingchain c,
nrgcing.cingresidue r
WHERE
c.entry_id = e.entry_id AND
r.entry_id = e.entry_id AND
r.distance_count > 0 AND
r.name NOT IN ( select name from nrgcing.normalResidue )
order by e.name, c.name, r.number, r.name, r.distance_count
)              TO '/Users/jd/tmp/tmpSql/ligandsWithDrs.csv' WITH CSV HEADER;

COPY ( 
SELECT distinct e.name
FROM 
nrgcing.cingentry e,
nrgcing.cingchain c,
nrgcing.cingresidue r
WHERE
c.entry_id = e.entry_id AND
r.entry_id = e.entry_id AND
r.distance_count > 0 AND
r.name NOT IN ( select name from nrgcing.normalResidue )
order by e.name
)              TO '/Users/jd/tmp/tmpSql/entriesWithLigandsWithDrs.csv' WITH CSV HEADER;

SELECT 'Distinct entries with ligand with DRs count: ' || count( distinct e.name )
FROM 
nrgcing.cingentry e,
nrgcing.cingchain c,
nrgcing.cingresidue r
WHERE
c.entry_id = e.entry_id AND
r.entry_id = e.entry_id AND
r.distance_count > 0 AND
r.name NOT IN ( select name from nrgcing.normalResidue )

-- PER ENTRY STATS
SELECT 'dep date avg/sd/min/max: ' || avg(t.v), stddev(t.v), min(t.v), max(t.v) 
FROM (
    SELECT extract( year from deposition_date) as v 
    FROM brief_summary b
    JOIN "//exptl/@method" p1 ON b.docid = p1.docid
    WHERE p1.val = 'SOLUTION NMR'
) AS t;


SELECT 'Residues per entry: ' || avg(t.v), stddev(t.v), min(t.v), max(t.v) 
FROM (
    SELECT res_count as v
    FROM nrgcing.cingentry
) AS t;
-- 2l8m      3638 lots of water residues not included in RDB but counted in entry.residue_count
-- 3rec         2 dinucleotide
-- 1dey is a larger molecule with 2 funky residues.
--
--SELECT name, res_count
--FROM nrgcing.cingentry
--where res_count < 10 or res_count > 3500
--order by res_count

SELECT 'CS per residue: ' || count(t), avg(t.v), stddev(t.v), min(t.v), max(t.v) 
FROM (
    SELECT e.name, c.name, r.number, r.name, COUNT(a.cs) as v
    FROM 
        nrgcing.cingentry e,
        nrgcing.cingchain c,
        nrgcing.cingresidue r,
        nrgcing.cingatom a
    WHERE 
        c.entry_id = e.entry_id AND
        r.chain_id = c.chain_id AND
        a.residue_id = r.residue_id AND
--        e.name = '1ahd' AND
--        r.number <= 20 AND
        a.cs is not NULL
    GROUP BY e.name, c.name, r.number, r.name
    ORDER BY e.name, c.name, r.number, r.name
) AS t;


SELECT e.name, c.name, r.number, r.name, a.name, a.cs
FROM 
    nrgcing.cingentry e,
    nrgcing.cingchain c,
    nrgcing.cingresidue r,
    nrgcing.cingatom a
WHERE 
    c.entry_id = e.entry_id AND
    r.chain_id = c.chain_id AND
    a.residue_id = r.residue_id AND
    e.name = '1ahd' AND
--    r.number <= 20 AND
    a.name = 'C6'
--    a.cs is not NULL    
ORDER BY e.name, c.name, r.number, r.name, a.name

-- Get the number of references in PDB headers to the different software packages used.
SELECT p.VAL AS "program", count(p.val)
  FROM
       "pdbj".BRIEF_SUMMARY AS S JOIN 
             "pdbj"."/datablock/pdbx_nmr_softwareCategory/pdbx_nmr_software/name" AS P ON S.DOCID = P.DOCID
  JOIN "//exptl/@method" p1 ON s.docid = p1.docid
    WHERE p1.val LIKE '%NMR' 
--    AND
--    s.pdbid = '1brv'
group by p.val
order by count(p.val) desc
LIMIT 100
