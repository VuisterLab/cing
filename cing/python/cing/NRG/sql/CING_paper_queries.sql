-- A temporary table to contain the percentages of residues r/o/g taking
-- into account the entry AND range selection.
drop TABLE IF EXISTS nrgcing.tmpentry; 
CREATE TABLE nrgcing.tmpentry as (
    select c.entry_id as entry_id, c.rog as rog,
    ((100.0*c.ccount)/e.res_count) as cperc
    from nrgcing.cingentry e,
    (
        select r2.entry_id as entry_id, r2.rog as rog, count(*) as ccount from
        nrgcing.cingresidue r2
        group by r2.entry_id, r2.rog
    ) as c
    where e.entry_id = c.entry_id    
    order by e.entry_id, c.rog asc
);


SELECT e.pdb_id, e.res_count,
to_char( extract( year from b.deposition_date), 'FM9999') as deposition_date, 
to_char( te.cperc, 'FM999.0') as rog_perc0,
e.distance_count, e.dihedral_count, e.cs_count
FROM nrgcing.cingentry e, brief_summary b, nrgcing.tmpentry te
WHERE
e.pdb_id = b.pdbid AND
e.entry_id = te.entry_id AND
te.rog = 0 AND
te.cperc < 20 AND
b.deposition_date > '2009-01-01' AND
e.protein_count > 0 AND
e.res_count > 100 AND
e.chain_count = 1 AND
e.distance_count > 100 AND
e.dihedral_count > 50 AND
e.cs_count > 1000
order by b.deposition_date desc limit 20;

-- Number of entries with descent size protein ensembles
select count(*) 
from nrgcing.entry_list_selection;




CREATE TABLE nrgcing.tmpentry as (
    select e.entry_id as entry_id,
    c.rog as rog,
    round( (100.0*c.ccount)/e.res_count, 2) as cperc
    from
    nrgcing.cingentry e,
    (
        select r2.entry_id as entry_id, r2.rog as rog, count(*) as ccount from
        nrgcing.cingresidue r2
        group by r2.entry_id, r2.rog
    ) as c
    where
    e.entry_id = c.entry_id
    group by e.entry_id, c.ccount 
    order by e.entry_id asc
);



select r.entry_id as entry_id, count(*) as cred from
nrgcing.cingresidue r
where r.rog = 2 group by r.entry_id;



-- residue_list_selection is defined and created from nrgCingRdb.py:
-- Find residues in entry selection and residue selection.
select count(*), s2.sel_1 
FROM nrgcing.residue_list_selection s2
group by s2.sel_1;

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
-- Gives 6383 rows/entries. Process with segmentAnalysisCingPaper.py

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
    SELECT e.pdb_id, c.name, count(*) as l
    FROM 
    nrgcing.cingentry e,
    nrgcing.cingchain c,
    nrgcing.cingresidue r,
    nrgcing.residue_list_selection s2
    WHERE
    e.entry_id = c.entry_id AND
    c.chain_id = r.chain_id AND
    r.residue_id = s2.residue_id AND
--	e.pdb_id = '2kwk' AND
    s2.sel_1 = true
    group by e.pdb_id, c.name
    having count(*) > 4
    order by e.pdb_id, c.name asc
) as temp

-- Three-residue streches in range:
 1cfa   B        3
 1dxw   B        3
 1jmq   B        3
 1jsp   B        3
 1k3n   B        3
 1k3q   B        3
 1k9r   B        3
 1m0v   B        3
 1mw4   B        3
 1ozs   B        3
 1wco   A        3
 2ain   B        3
 2aiz   B        3
 2bbu   B        3
 2dyf   B        3
 2g46   B        3
 2g46   D        3
 2h3s   A        3
 2ka9   C        3
 2khh   B        3
 2krb   B        3
 2kwk   A        3 Residues 1-3 have s2.sel_1 set but aren't in range string. this is a bug.

 
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








gawk -f 'BEGIN{n=0}{'
    limit 10;

