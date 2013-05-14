

DROP TABLE IF EXISTS nrgcing.normalResidue;
create table nrgcing.normalResidue (
    name                     VARCHAR(5) UNIQUE PRIMARY KEY,
    moltype                  INT
);
-- mapMoltypeToInt = {PROTEIN_STR: 0, DNA_STR : 1, RNA_STR : 2, WATER_STR : 3, OTHER_STR: 4}
CREATE INDEX indexAaResidue ON nrgcing.normalResidue(name);
insert into nrgcing.normalResidue VALUES
('ALA', 0), ('ARGx', 0), ('ARG', 0), ('ASN', 0), ('ASPH', 0), ('ASP', 0), ('CYSS', 0), ('CYS', 0), ('GLN', 0), ('GLUH', 0), ('GLU', 0), ('GLY', 0), ('HISE', 0), ('HISH', 0), ('HIS', 0), ('ILE', 0), ('LEU', 0), ('LYSx', 0), ('LYS', 0), ('MET', 0), ('PHE', 0), ('cPRO', 0), ('PRO', 0), ('SER', 0), ('THR', 0), ('TRP', 0), ('TYR', 0), ('VAL', 0), ('LGLY', 0), 
('DA', 1),('DC', 1),('DG', 1),('DT', 1),('DU', 1),
('A', 2),('C', 2),('G', 2),('U', 2),('T', 2),
('HOH', 3),
('CA2P',4),('ZN',4),('CA',4),('MN',4),('CU',4),('CU1',4),('MG',4),('CO',4),('ZNH',4),('FES',4), 
('SS', 4)
;


SELECT 'Number of NRG-CING entries: ' || count(*) FROM nrgcing.cingentry;

-- Experiment available: 5519
SELECT 'Experiment available: ' ||
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
)              TO '/tmp/distinctLigands.csv' WITH CSV HEADER;

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
)              TO '/tmp/ligandsWithDrs.csv' WITH CSV HEADER;

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
)              TO '/tmp/entriesWithLigandsWithDrs.csv' WITH CSV HEADER;

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
-- first dep
SELECT extract( year from deposition_date) as v, b.pdbid 
FROM brief_summary b
JOIN "//exptl/@method" p1 ON b.docid = p1.docid
WHERE p1.val = 'SOLUTION NMR'
order by extract( year from deposition_date) asc
limit 10


-- PER YEAR STATS
SELECT t.v, count(*)
FROM (
    SELECT extract( year from deposition_date) as v 
    FROM brief_summary b
    JOIN "//exptl/@method" p1 ON b.docid = p1.docid
    WHERE p1.val = 'SOLUTION NMR'
) AS t
group by t.v
order by t.v asc
;


SELECT 'Residues per entry: ' || avg(t.v), stddev(t.v), min(t.v), max(t.v) 
FROM (
    SELECT res_count as v
    FROM nrgcing.cingentry
    where res_count < 1000
) AS t;
-- 2l8m      3638 lots of water residues not included in RDB but counted in entry.residue_count
-- 3rec         2 dinucleotide
-- 1dey is a larger molecule with 2 funky residues.
-- 1l0r      2220 # water
-- 2ku1      1659 # Remco's
--                ?column?                 |       stddev        | min | max  
-------------------------------------------+---------------------+-----+------
-- Residues per entry: 91.5368645494332847 | 71.0640008407049349 |   1 | 1659
SELECT 'Residues per entry: ' || avg(t.v), stddev(t.v), min(t.v), max(t.v) 
FROM (
    SELECT count(*) as v, e.name as name
    FROM nrgcing.cingentry e,
    nrgcing.cingchain c,
    nrgcing.cingresidue r
    WHERE
    c.entry_id = e.entry_id AND
    r.entry_id = e.entry_id AND
    r.chain_id = c.chain_id AND
    r.name != 'HOH'
--    e.name = '2l8m'
    group by e.name
    order by count(*) desc
) AS t;


SELECT name, res_count
FROM nrgcing.cingentry
where res_count > 1000
order by res_count desc

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
--        e.name = '1cjg' AND
--        r.number <= 20 AND
        a.cs is not NULL
    GROUP BY e.name, c.name, r.number, r.name
--    ORDER BY e.name, c.name, r.number, r.name
    ORDER BY COUNT(a.cs) desc
) AS t;

--    ** CS per entry **
-- 2h25 3959
-- 1y8b 3354
-- 1l6n 2709
--      ?column?      |         avg          |      stddev      | min | max  
----------------------+----------------------+------------------+-----+------
-- CS per entry: 3626 | 779.9597352454495312 | 511.838572644997 |   1 | 3959

SELECT 'CS per entry: ' || count(t), avg(t.v), stddev(t.v), min(t.v), max(t.v) 
FROM (
    SELECT e.name, COUNT(a.cs) as v
    FROM 
        nrgcing.cingentry e,
        nrgcing.cingchain c,
        nrgcing.cingresidue r,
        nrgcing.cingatom a
    WHERE 
        c.entry_id = e.entry_id AND
        r.chain_id = c.chain_id AND
        a.residue_id = r.residue_id AND
--        e.name = '1cjg' AND
--        r.number <= 20 AND
        a.cs is not NULL
    GROUP BY e.name
    ORDER BY COUNT(a.cs) asc
--    limit 100
) AS t;

--    distance_count                 INT DEFAULT NULL,
--    dihedral_count                 INT DEFAULT NULL,
--    rdc_count                      INT DEFAULT NULL,
--    peak_count                     INT DEFAULT NULL,
--    cs_count                       INT DEFAULT NULL,

SELECT 'Restraints per entry: ' || count(t.v), avg(t.v), stddev(t.v), min(t.v), max(t.v) 
FROM (
    SELECT e.name, (e.distance_count + e.dihedral_count + e.rdc_count) as v
    FROM
        nrgcing.cingentry e
    WHERE 
        (e.distance_count + e.dihedral_count + e.rdc_count)  > 0    
) AS t;

-- Outliers max.
-- name |   v   
--------+-------
-- 2l0q | 11972
-- 2kby | 11044
SELECT e.name, (e.distance_count + e.dihedral_count + e.rdc_count) as v
FROM
    nrgcing.cingentry e
WHERE 
    (e.distance_count + e.dihedral_count + e.rdc_count)  > 10000
order by  (e.distance_count + e.dihedral_count + e.rdc_count) desc;

-- Outliers min.
-- name | v 
--------+---
-- 2kjh | 1 Contains additional unparsed HADDOCK DRs.
-- 1evd | 3 Many discover DRs unprocessed.
-- 2odd | 5 Many in DOCR not in NRG-CING
-- 2kqg | 5 Many Amber unparsed.
-- 2kqh | 6 See 2kqg
-- 2kaw | 6 Many ambi xplor unparsed.
-- 2k9f | 6 11 AIRs unparsed.
-- 2k4a | 8 18 AIRs unparsed.
-- 1d7q | 8 Many xplor unparsed.
-- 1p9f | 9 Really just 9 dihedral restraints. Entry from 2004. Don't know the group. XXXXXXXXXXXXXXXXXXXXXXXXXXXXX
-- 1gjx | 10 Dihedrals only.
-- 1evb | 10 Many discover DRs unprocessed.
-- 1kyj | 11 Many xplor unparsed.
-- 1soc | 11 Really 14 NOEs in Discover format. XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
-- 2ih0 | 11 Many discover DRs unprocessed.
-- 2i18 | 12 Many in DOCR not in NRG-CING
-- 1jzp | 12 Dihedrals only
-- 2alb | 12 Many CYANA DRs unprocessed.
-- 2oru | 13 Dihedrals only
-- 2kda | 13 Many xplor unparsed.
-- 2jnr | 16 That more than 1soc.
SELECT e.name, (e.distance_count + e.dihedral_count + e.rdc_count) as v
FROM
    nrgcing.cingentry e
WHERE 
    (e.distance_count + e.dihedral_count + e.rdc_count)  > 0
order by  (e.distance_count + e.dihedral_count + e.rdc_count) asc
limit 30;

--      ?column?      |          avg          |      stddev       | min |  max  
----------------------+-----------------------+-------------------+-----+-------
-- DR per entry: 5423 | 1324.8089618292458049 | 1107.413404708204 |   1 | 11972
SELECT 'DR per entry: ' || count(t.v), avg(t.v), stddev(t.v), min(t.v), max(t.v) 
FROM (
    SELECT e.name, e.distance_count as v
    FROM
        nrgcing.cingentry e
    WHERE 
        e.distance_count > 0    
) AS t;

-- Outliers:
-- 2kby | 10112 # Symmetric tetramer. Good as far as I can see.
-- 2l0q | 11972 # Many DRs because of duplication on individual methyl protons.
SELECT e.name, e.distance_count as v
FROM
    nrgcing.cingentry e
WHERE 
    e.distance_count > 10000;   

SELECT 'AIRs per entry: ' || count(t.v), avg(t.v), stddev(t.v), min(t.v), max(t.v) 
FROM (
    SELECT e.name, e.distance_count as v
    FROM
        nrgcing.cingentry e
    WHERE 
        e.distance_count < 50 AND
        e.distance_count >= 1
) AS t;

SELECT 'Dih per entry: ' || count(t.v), avg(t.v), stddev(t.v), min(t.v), max(t.v) 
FROM (
    SELECT e.name, e.dihedral_count as v
    FROM
        nrgcing.cingentry e
    WHERE 
        e.dihedral_count > 0    
) AS t;

--      ?column?      |         avg          |      stddev      | min | max 
----------------------+----------------------+------------------+-----+-----
 RDC per entry: 426 | 138.6455399061032864 | 148.033775768559 |   9 | 970
SELECT 'RDC per entry: ' || count(t.v), avg(t.v), stddev(t.v), min(t.v), max(t.v) 
FROM (
    SELECT e.name, e.rdc_count as v
    FROM
        nrgcing.cingentry e
    WHERE 
        e.rdc_count > 0    
) AS t;

-- Outliers min:
-- 1qwb | 9 OK with 6 of original 15 commented out.
SELECT e.name, e.rdc_count as v
FROM
    nrgcing.cingentry e
WHERE 
    e.rdc_count < 10    
order by e.rdc_count desc
limit 10;

-- Outliers max:
-- 1ezp | 970 OK Lewis Kay entry with 370 AA. Bad Rama's.
SELECT e.name, e.rdc_count as v
FROM
    nrgcing.cingentry e
WHERE 
    e.rdc_count > 500    
order by e.rdc_count desc
limit 10;



WHERE 
    e.distance_count > 0;

SELECT 'CS containing entry: ' || count(t), avg(t.v), stddev(t.v), min(t.v), max(t.v) 
FROM (
    SELECT e.name, e.cs_count as v
    FROM 
        nrgcing.cingentry e
    WHERE 
        e.cs_count > 0    
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

-- Dimers is 413 (assuming another 40 have more than dimeric /multimerisity/)
-- NULL            2
-- SYMMETRY_C1  8496
-- SYMMETRY_C2   413 -> 453.
SELECT e.symmetry, count(*)
FROM 
    nrgcing.cingentry e
group by e.symmetry

-- Number of chains. Multiple chains indicate complexes or water or ion?
-- 2812 - 413 = 2399.
-- false          6099
-- true           2812
SELECT e.is_multimeric, count(*)
FROM 
    nrgcing.cingentry e
group by e.is_multimeric

-- Last revision of CING code.
--     1057  8124
--     1060   787
SELECT e.rev_last, count(*)
FROM 
    nrgcing.cingentry e
group by e.rev_last

-- See documentation in Documentation/multimers_and_complexes.txt
-- complexes that are not dimeric
-- ename | chaincount 
---------+------------
-- 1c17  |         13 complex
-- 3aiy  |         12 insulin hexamer
-- 1aiy  |         12
-- 1ai0  |         12
-- 4aiy  |         12 insulin hexamer
-- 5aiy  |         12
-- 2aiy  |         12
-- 2kib  |          8
-- 2ku1  |          7
-- 1rcs  |          6
-- 2k1n  |          6
-- 2ki6  |          6
-- 1co0  |          6
-- 2jz7  |          5
-- 2beg  |          5
-- 1eq8  |          5
-- 2a9h  |          5
-- 2kwd  |          5
-- 2hyn  |          5
-- 2rnm  |          5
-- 1zll  |          5
-- 2h35  |          4
-- 1mq1  |          4
-- 1f6g  |          4
-- 1rso  |          4
-- 2kkk  |          4
-- 1rme  |          4
-- 1ybl  |          4
-- 1pes  |          4
-- 1ybr  |          4
-- 2j0z  |          4
-- 2jo5  |          4
-- 2kn7  |          4
-- 2bjc  |          4
-- 1qey  |          4
-----
-- 2djy  |          2 real
-- 2pon  |          2 real
-- 2ihx  |          2 real
-- 2fci  |          2 real
-- 2k1v  |          2 real
-- 2kju  |          2 real
-- 1kup  |          2 real
-- 1l4w  |          2 real
--(1236 rows)

-- false positive example:  1jo1           2 # symmetric dimeric rna with 2 ligands.
-- There are 142 that have 3 chains. Spot check shows almost none trimers.
-- 1rfo  |          3 trimer.
-- 2rr9  |          3 real

SELECT t.ename, count(*) as chaincount
FROM (
    SELECT e.name as ename, c.name as cname, count(*) as polychain_rescount
    FROM 
        nrgcing.cingentry e,
        nrgcing.cingchain c,
        nrgcing.cingresidue r
    WHERE 
        c.entry_id = e.entry_id AND
        r.chain_id = c.chain_id AND
        e.symmetry != 'SYMMETRY_C2' AND
--	    e.name = '1brv' AND
        r.name IN ( select n.name from nrgcing.normalResidue n where n.moltype <= 2)    
    group by ename, cname
    ORDER BY count(*)
) as t
group by t.ename
having count(*) = 3
order by count(*) desc;



-- Number of protein containing entries
-- 2812 - 413 = 2399.
-- false          6099
-- true           2812
SELECT e.chothia_class, count(*)
FROM 
    nrgcing.cingentry e
    where e.chothia_class is not null
group by e.chothia_class
order by e.chothia_class asc
