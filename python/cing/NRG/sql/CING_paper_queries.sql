-- Queries for analyses done for the CING paper.

-- This is file: $C/python/cing/NRG/sql/CING_paper_queries.sql
-- Code on next line refers to cited numbers in the manuscript.
-- They are sequential in this file but not sequential in the manuscript.

--[SQL001]
-- residue_list_selection is defined and created from nrgCingRdb.py:
-- and it is simply the residues for which sel1 is true. (Quite trivial).
-- Find residues in entry selection and residue selection.
-- On 2012-02-27 this was:
-- 111052 false
-- 587710 true
-- On 2012-03-05 this was:
--  92276 false
-- 606615 true
-- Put into ipython to  
select count(*), s2.sel_1
FROM nrgcing.residue_list_selection s2
group by s2.sel_1;


--[SQL002]
select count(*) 
FROM nrgcing.cingentry e;


-- [SQL003]
-- Find number of segments in range per entry
-- First create a quoted csv file.
COPY (
    SELECT e.pdb_id, e.ranges
    FROM 
    nrgcing.cingentry e,
    nrgcing.entry_list_selection s1
    WHERE
    e.pdb_id = s1.pdb_id
) TO '/tmp/nrgcing_ranges.csv' WITH CSV HEADER;
-- Copy to development machine.
--      cd /Users/jd/CMBI/Papers/CING/Data
--      scp i@nmr.cmbi.ru.nl:/tmp/nrgcing_ranges.csv .
-- On 2012-02-27 this was: 6461 rows/entries.
--      wc nrgcing_ranges.csv
-- Process with segmentAnalysisCingPaper.py and not the below sql because we do need a procedural language for this.
-- TODO: include only regular amino acids.


--[SQL004]
-- On 2012-03-16 this was:
-- 80041
SELECT count(*)
FROM "pdbj".BRIEF_SUMMARY AS S;

--[SQL005]
-- On 2012-03-16 this was:
-- X-RAY DIFFRACTION        70120
-- SOLUTION NMR              9299 <=====
-- ELECTRON MICROSCOPY        411
-- NEUTRON DIFFRACTION         55
-- SOLID-STATE NMR             54 <=====
-- SOLUTION SCATTERING         45
-- FIBER DIFFRACTION           37
-- ELECTRON CRYSTALLOGRAPHY    32
-- POWDER DIFFRACTION          18
-- THEORETICAL MODEL            7
-- EPR                          6
-- INFRARED SPECTROSCOPY        4
-- FLUORESCENCE TRANSFER        1
SELECT p1.val, count(p1.val)
FROM "pdbj".BRIEF_SUMMARY AS S
JOIN "//exptl/@method" p1 ON s.docid = p1.docid
--WHERE p1.val LIKE '%NMR' 
group by p1.val
order by count(p1.val) desc;

--[SQL006]
-- Number of entries with descent size protein ensembles.
-- First run: python -u $CINGROOT/python/cing/NRG/nrgCingRdb.py 
-- On 2012-03-16 this was:
select count(*) 
from nrgcing.entry_list_selection;

--[SQL007]
-- On 2012-03-16 this was:
-- 1a24                 189             0             0               0               0
-- 1a4d                   0             0            41               0               0
-- 1afp                  51             0             0               0               0
-- 1ai0                 306             0             0               4               8
-- 1b4y                   0            30             0               0               0
-- 1brv                  32             0             0               0               0
-- 1bus                   0             0             0               0              57
-- 1cjg                 124            44             0               0               0
-- 1d3z                  76             0             0               0               0
-- 1hkt                 106             0             0               0               0
-- 1hue                 180             0             0               0               0
-- 1ieh                 135             0             0               0               0
-- 1iv6                  70            26             0               0               0
-- 1jwe                 114             0             0               0               0
-- 1kr8                   0             7             0               0               0
-- 2hgh                  87             0            55               0               3
-- 2k0e                 148             0             0               0               4
SELECT e.pdb_id, e.res_protein_count, res_dna_count, res_rna_count, res_water_count, res_other_count
FROM nrgcing.CINGENTRY E
WHERE 
    E.MODEL_COUNT >= 1             -- At least 10 models
--AND E.pdb_id = '1brv'
AND E.pdb_id in ( '1a4d', '1a24', '1afp', '1ai0', '1b4y', '1brv', '1bus', '1cjg', '1d3z', '1hkt', '1hue', '1ieh', '1iv6', '1jwe', '1kr8', '2hgh', '2k0e' )
order by e.pdb_id;

-- Amino acid count per entry.
select e.pdb_id, c.mol_type_idx, count(*) as res_count
from 
    nrgcing.CINGENTRY E, 
    nrgcing.cingchain c,
    nrgcing.CINGresidue r
where 
    e.entry_id = c.entry_id AND
    c.chain_id = r.chain_id
--    e.entry_id = r.entry_id and
--    e.pdb_id = '1hue'
--    c.mol_type_idx = 0 -- Protein
group by e.pdb_id, c.mol_type_idx
limit 10;


--[SQL008]
-- On 2012-06-05 this was:
-- 499
SELECT count(*)
FROM 
    nrgcing.CINGENTRY E
where 
    e.rdc_count > 0


-- Testing with: 1brv 1ai0 2kwk
select
e.name,
e.ranges,
e.sel_1 
from
nrgcing.cingentry e
where
e.name in ( '2kwk', '1brv', '1ai0')
order by
e.name ASC
limit 50;

-- And
select
e.name,
c.name,
r.number,
r.name,
r.rog,
r.sel_1 
from
nrgcing.cingentry e,
nrgcing.cingchain c,
nrgcing.cingresidue r
where
e.entry_id = c.entry_id AND
e.entry_id = r.entry_id AND
e.name = '2kwk'
--r.sel_1 = true
order by
e.name ASC,
c.name ASC,
r.number ASC
limit 50;

-- A derived table to contain the percentages of residues rog.
drop TABLE IF EXISTS nrgcing.tmpentry; 
CREATE TABLE nrgcing.tmpentry as (
    select e.entry_id as entry_id,
    e.name,
    c.rog as rog,
    c.ccount as count,
    e.res_count as total_count,
    round( (100.0*c.ccount)/e.res_count, 2) as cperc
    from
    nrgcing.cingentry e,
    (
        select r.entry_id as entry_id, r.rog as rog, count(*) as ccount from
        nrgcing.cingresidue r
        where r.sel_1 = true
        group by r.entry_id, r.rog
    ) as c
    where
    e.entry_id = c.entry_id AND
    e.name = '1brv'
--    group by e.entry_id, c.ccount -- optional? 
    order by e.entry_id asc
);


-- Select pdb entries of sufficient badness that are large enough but also have
-- enough data and all data types.
SELECT e.pdb_id, e.res_count,
    to_char( extract( year from b.deposition_date), 'FM9999') as deposition_date, 
    to_char( te.cperc, 'FM999.0') as rog_perc0,
    e.distance_count, e.dihedral_count, e.cs_count
FROM nrgcing.cingentry e, brief_summary b, nrgcing.tmpentry te
WHERE
e.pdb_id = b.pdbid AND
e.entry_id = te.entry_id AND
te.rog = 0 AND
te.cperc < 101. AND -- Was 20.
b.deposition_date > '2009-01-01' AND
e.protein_count > 0 AND
e.res_count > 100 AND
e.chain_count = 1 AND
e.distance_count > 100 AND
e.dihedral_count > 50 AND
e.cs_count > 1000
order by b.deposition_date desc limit 20000;


-- Check existence of a particular entry.
select *
FROM nrgcing.entry_list_selection es
where es.pdb_id = '1gac'

select e.pdb_id, e.res_count
FROM nrgcing.cingentry e
where e.pdb_id = '1gac'



-- Unused select
select r.entry_id as entry_id, count(*) as cred 
from nrgcing.cingresidue r
where r.rog = 2 
group by r.entry_id;






select * 
from nrgcing.cingsummary cs
where cs.pdb_id = '1gac'
order by cs.pdb_id asc;


-- Find number of chains in selected entries and selected residues
-- Skipping chains that don't have selected residues anyway (such as water).
-- Skipping chains that contain only 1 residue such as ions and simplest ligands
-- Depending on cutoff we get total number of chains:
-- 1 7426
-- 2 7414
-- 3 7392 
-- 4 7363 TAKEN.
-- Gives average length:   7363 75.6176830096428086
SELECT count(*), avg(temp.l) 
from (
    SELECT e.pdb_id, e.timestamp_last, c.name, count(*) as size
    FROM 
    nrgcing.cingentry e,
    nrgcing.cingchain c,
    nrgcing.cingresidue r
--    nrgcing.residue_list_selection s2
    WHERE
    e.entry_id = c.entry_id AND
    e.entry_id = r.entry_id AND
--    r.residue_id = s2.residue_id AND
    e.timestamp_last > '2012-02-26' AND
--	e.pdb_id = '2kwk' AND
    r.sel_1 = true
    group by e.pdb_id, e.timestamp_last, c.name
    having count(*) > -1
    order by count(*) asc, e.pdb_id, c.name asc
    limit 50
) as temp

-- Three-residue streches in range: (shouldn't exist per auto range selection).
-- 1cfa   B        3
-- 1dxw   B        3
-- 1jmq   B        3
-- 1jsp   B        3
-- 1k3n   B        3
-- 1k3q   B        3
-- 1k9r   B        3
-- 1m0v   B        3
-- 1mw4   B        3
-- 1ozs   B        3
-- 1wco   A        3
-- 2ain   B        3
-- 2aiz   B        3
-- 2bbu   B        3
-- 2dyf   B        3
-- 2g46   B        3
-- 2g46   D        3
-- 2h3s   A        3
-- 2ka9   C        3
-- 2khh   B        3
-- 2krb   B        3
-- 2kwk   A        3 Residues 1-3 have s2.sel_1 set but aren't in range string. this is a bug.

 
SELECT e.pdb_id, c.name, r.number
FROM 
nrgcing.cingentry e,
nrgcing.cingchain c,
nrgcing.cingresidue r,
nrgcing.residue_list_selection s2
WHERE
e.entry_id = c.entry_id AND
c.chain_id = r.chain_id AND
r.residue_id = s2.residue_id AND
e.pdb_id = '2kwk' AND
s2.sel_1 = true
order by e.pdb_id, c.name, r.number asc

limit 200;

-- Reviewer 1 point 3; new figure 5
-- residues with coordinates and within cv range.
-- r.sel_1 denotes it is in range.
-- r.is_present checks for coordinates
-- A derived table to contain the percentages of residues rog.
drop TABLE IF EXISTS nrgcing.tmpentry2; 
drop TABLE IF EXISTS nrgcing.tmpentry3; 
CREATE TABLE nrgcing.tmpentry2 as (
    select r1.entry_id as entry_id, r1.rog as rog, count(*) as ccount from
    nrgcing.cingresidue r1
    where r1.sel_1 = true AND r1.is_present = true
    group by r1.entry_id, r1.rog
)
CREATE TABLE nrgcing.tmpentry3 as (
    select r2.entry_id, count(*) as ccount from
    nrgcing.cingresidue r2
    where r2.sel_1 = true AND r2.is_present = true
    group by r2.entry_id
)

drop TABLE IF EXISTS nrgcing.tmpentry4; 
CREATE TABLE nrgcing.tmpentry4 as (
select e.entry_id as entry_id,
e.name,
c1.rog as rog,
c2.ccount as ccount,
e.res_count as total_count,
round( (100.0*c1.ccount)/c2.ccount, 1) as cperc
from
nrgcing.cingentry e,
nrgcing.tmpentry2 c1,
nrgcing.tmpentry3 c2
where
e.entry_id = c1.entry_id AND
e.entry_id = c2.entry_id
--(e.name = '1cl4' or e.name = '1m9o')
order by e.entry_id asc, rog asc
);

select * from nrgcing.tmpentry4
where (name = '1cl4' or name = '1m9o' or name = '2kq3') and
rog = 0;

--# Nice example for Sid
SELECT e.pdb_id, e.timestamp_last
FROM nrgcing.cingentry e
WHERE
e.timestamp_last = '2012-09-01'
limit 50;


