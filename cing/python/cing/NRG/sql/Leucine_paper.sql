-- Count number of leu
-- Result 66,423
select count(*)
--select e.pdb_id as pdb, c.name as c, r.number as num, r.name
from "nrgcing"."cingresidue" r
inner join "nrgcing"."cingchain"   c on r.chain_id = c.chain_id
inner join "nrgcing"."cingentry"   e on c.entry_id = e.entry_id
inner join "nrgcing"."entry_list_selection" s1 on s1.pdb_id = e.pdb_id
where r.name = 'LEU' AND
e.pdb_id = '1hue'
order by e.pdb_id, c.name, r.number 
limit 100;

-- Ranges string for a particular entry
select e.pdb_id as pdb, e.ranges
from "nrgcing"."cingentry" e 
where
e.pdb_id IN ( '1brv','1hkt','1mo7','1mo8','1ozi','1p9j','1pd7','1qjt','1vj6','1y7n','2fws','2fwu','2jsx') 
order by e.pdb_id 
limit 100;

-- Residues in ranges for a particular entry
select e.pdb_id as pdb, c.name as c, r.number as num, r.name, r.sel_1
from "nrgcing"."cingresidue" r
inner join "nrgcing"."cingchain"   c on r.chain_id = c.chain_id
inner join "nrgcing"."cingentry"   e on c.entry_id = e.entry_id
inner join "nrgcing"."entry_list_selection" s1 on s1.pdb_id = e.pdb_id
where r.sel_1 = true AND
r.name = 'LEU'
--e.pdb_id IN ( '1brv','1hkt','1mo7','1mo8','1ozi','1p9j','1pd7','1qjt','1vj6','1y7n','2fws','2fwu','2jsx') 
order by e.pdb_id, c.name, r.number 
limit 100000;

-- SQL0102
-- Number of entries with 10+ models and 30+ aa.
select count(*)
from "nrgcing"."entry_list_selection" e;

-- SQL0103
-- Count number of leu in well-defined ranges with an existing chi average value.
-- There are 302 LEU for which the chi1 or 2 average value is a null. This might be a bug.   
-- Result 19,103 (was 52,888 without filtering on r.distance_count and chi1/2 cvs)
--  and 31,983 without filtering on  r.distance_count.
--select e.pdb_id as pdb, c.name as c, r.number as num, r.name, r.chi1_avg, r.chi2_avg
drop view if exists "nrgcing".leucine;
create view "nrgcing".leucine as select r.residue_id
FROM "nrgcing"."cingresidue" r
inner join "nrgcing"."cingchain"   c on r.chain_id = c.chain_id
inner join "nrgcing"."cingentry"   e on c.entry_id = e.entry_id
inner join "nrgcing"."entry_list_selection" s1 on s1.pdb_id = e.pdb_id
where 
r.sel_1 = true AND
r.name = 'LEU' AND
r.distance_count >= 10 AND
r.chi1_cv < 0.2 AND r.chi2_cv < 0.2 AND
NOT (r.chi1_avg IS NULL OR r.chi2_avg IS NULL);
--order by e.pdb_id, c.name, r.number 
select count(*) from "nrgcing".leucine;


-- SQL0101
-- Count number of bad leu chi2 in t/g- and g-/g-.
-- JFD checked that all leucine chi1 and 2's are in [0,360>
-- Result: 19,103
--In [1]: 100.*(767+952)/19103.
--Out[1]: 8.9985866094330742
--select e.pdb_id as pdb, c.name as c, r.number as num, r.name,
select count(*)
--to_char(r.chi1_avg,  'FM990.0') as chi1_avg,
--to_char(r.chi1_cv,   'FM0.000')  as chi1_cv,
--to_char(r.chi2_avg,  'FM990.0') as chi2_avg,
--to_char(r.chi2_cv,   'FM0.000')  as chi2_cv
FROM "nrgcing"."cingresidue" r
inner join "nrgcing"."leucine"   le on le.residue_id = r.residue_id
--inner join "nrgcing"."cingchain"   c on r.chain_id = c.chain_id
--inner join "nrgcing"."cingentry"   e on c.entry_id = e.entry_id
where
-- t/g- result: 767
--r.chi1_avg >= 120 AND r.chi1_avg <  240 AND r.chi2_avg >= 240 AND r.chi2_avg <  360
-- g-/g- result: 952
r.chi1_avg >= 240 AND r.chi1_avg <  360 AND r.chi2_avg >= 240 AND r.chi2_avg <  360

--e.name in ( '1brv','1hkt','1mo7','1mo8','1ozi','1p9j','1pd7','1qjt','1vj6','1y7n','2fws','2fwu','2jsx')
--AND (

--)
--order by e.pdb_id, c.name, r.number 
--limit 1000;



-- Count number of leu with CS for both Cdeltas (stereospecifically) and single conformer (low cv).
-- Result 11,132
select count(*)
FROM "nrgcing"."cingatom" a1
inner join "nrgcing"."cingatom"   a2 on  a1.residue_id = a2.residue_id
inner join "nrgcing"."cingresidue" r on a1.residue_id = r.residue_id
inner join "nrgcing"."cingchain"   c on r.chain_id = c.chain_id
inner join "nrgcing"."cingentry"   e on c.entry_id = e.entry_id
where
r.name = 'LEU' AND
a1.name = 'CD1' and a2.name = 'CD2' AND
a1.cs IS NOT NULL AND a2.cs IS NOT NULL AND
abs(a1.cs-a2.cs) > 0.01 AND
r.chi2_avg IS NOT NULL AND r.chi2_cv IS NOT NULL AND
r.chi2_cv < 0.2
;

-- Count number of bad leu chi2 range <240,360> with CS
-- Result 1506
--select count(*)
select e.pdb_id as pdb, c.name as c, r.number as num, r.name, a1.name, a2.name,
to_char(a1.cs-a2.cs, 'FM990.0') as csd,
to_char(r.chi2_avg,  'FM990.0') as chi2_avg,
to_char(r.chi2_cv,   'FM0.00') as chi2_cv
FROM "nrgcing"."cingatom" a1
inner join "nrgcing"."cingatom"   a2 on  a1.residue_id = a2.residue_id
inner join "nrgcing"."cingresidue" r on a1.residue_id = r.residue_id
inner join "nrgcing"."cingchain"   c on r.chain_id = c.chain_id
inner join "nrgcing"."cingentry"   e on c.entry_id = e.entry_id
where
e.name in ( '1brv','1hkt','1mo7','1mo8','1ozi','1p9j','1pd7','1qjt','1vj6','1y7n','2fws','2fwu','2jsx') AND
r.name = 'LEU' AND
a1.name = 'CD1' and a2.name = 'CD2' AND
a1.cs IS NOT NULL AND a2.cs IS NOT NULL AND
abs(a1.cs-a2.cs) > 0.01 AND
r.chi2_avg IS NOT NULL AND r.chi2_cv IS NOT NULL AND
r.chi2_cv < 0.2 AND ( r.chi2_avg > 240 AND r.chi2_avg < 360 )
;

-- Find Leu with conflict between CD chemical shifts and chi2
-- result 218 residue around +180
select e.pdb_id as pdb, c.name as c, r.number as num, r.name, a1.name, a2.name,
to_char(a1.cs-a2.cs, 'FM990.0') as csd,
to_char(r.chi2_avg,  'FM990.0') as chi2_avg,
to_char(r.chi2_cv,   'FM0.00') as chi2_cv
FROM "nrgcing"."cingatom" a1
inner join "nrgcing"."cingatom"   a2 on  a1.residue_id = a2.residue_id
inner join "nrgcing"."cingresidue" r on a1.residue_id = r.residue_id
inner join "nrgcing"."cingchain"   c on r.chain_id = c.chain_id
inner join "nrgcing"."cingentry"   e on c.entry_id = e.entry_id
where
r.name = 'LEU' AND
a1.name = 'CD1' and a2.name = 'CD2' AND
a1.cs IS NOT NULL AND a2.cs IS NOT NULL AND
abs(a1.cs-a2.cs) > 0.01 AND
r.chi2_avg IS NOT NULL AND r.chi2_cv IS NOT NULL AND
(r.chi2_avg > 120. and r.chi2_avg < 240.) AND -- around +180
(a1.cs-a2.cs) < -4 AND                       -- >4 ppm (indicates trans)
r.chi2_cv < 0.2 AND ( r.chi2_avg > 0 AND r.chi2_avg < 240 )
order by (a1.cs-a2.cs) ASC;

-- And similar part for other conformation:
-- 115 residues around +60
select e.pdb_id as pdb, c.name as c, r.number as num, r.name, a1.name, a2.name,
to_char(a1.cs-a2.cs, 'FM990.0') as csd,
to_char(r.chi2_avg,  'FM990.0') as chi2_avg,
to_char(r.chi2_cv,   'FM0.00') as chi2_cv
FROM "nrgcing"."cingatom" a1
inner join "nrgcing"."cingatom"   a2 on  a1.residue_id = a2.residue_id
inner join "nrgcing"."cingresidue" r on a1.residue_id = r.residue_id
inner join "nrgcing"."cingchain"   c on r.chain_id = c.chain_id
inner join "nrgcing"."cingentry"   e on c.entry_id = e.entry_id
where
r.name = 'LEU' AND
a1.name = 'CD1' and a2.name = 'CD2' AND
a1.cs IS NOT NULL AND a2.cs IS NOT NULL AND
abs(a1.cs-a2.cs) > 0.01 AND
r.chi2_avg IS NOT NULL AND r.chi2_cv IS NOT NULL AND
(r.chi2_avg > 0. and r.chi2_avg < 120.) AND -- around +60
(a1.cs-a2.cs) > 4 AND                       -- >4 ppm (indicates trans)
r.chi2_cv < 0.2 AND ( r.chi2_avg > 0 AND r.chi2_avg < 240 )
order by (a1.cs-a2.cs) DESC;

-- Values for Vuister lab entries
-- No conflicts with CS at all!
select e.pdb_id as pdb, c.name as c, r.number as num, r.name, a1.name, a2.name,
to_char(a1.cs-a2.cs, 'FM990.0') as csd,
to_char(r.chi2_avg,  'FM990.0') as chi2_avg,
to_char(r.chi2_cv,   'FM0.00') as chi2_cv
FROM "nrgcing"."cingatom" a1
inner join "nrgcing"."cingatom"   a2 on  a1.residue_id = a2.residue_id
inner join "nrgcing"."cingresidue" r on a1.residue_id = r.residue_id
inner join "nrgcing"."cingchain"   c on r.chain_id = c.chain_id
inner join "nrgcing"."cingentry"   e on c.entry_id = e.entry_id
where
e.name in ( '1brv','1hkt','1mo7','1mo8','1ozi','1p9j','1pd7','1qjt','1vj6','1y7n','2fws','2fwu','2jsx') AND
r.name = 'LEU' AND
a1.name = 'CD1' and a2.name = 'CD2' AND
a1.cs IS NOT NULL AND a2.cs IS NOT NULL AND
abs(a1.cs-a2.cs) > 0.01 AND
r.chi2_cv < 0.2
order by (a1.cs-a2.cs) ASC
;


-- result 144 residue around +60
 pdb  | c | num  | name | name | name | csd  | chi2_avg | chi2_cv
------+---+------+------+------+------+------+----------+---------
 1sr3 | A |  102 | LEU  | CD1  | CD2  | 21.2 | 95.2     | 0.00
 1doq | A |  254 | LEU  | CD1  | CD2  | 7.8  | 100.4    | 0.00
 2kou | A |  100 | LEU  | CD1  | CD2  | 7.3  | 105.4    | 0.15
 1vyn | A |  111 | LEU  | CD1  | CD2  | 7.2  | 113.2    | 0.15
 1hko | A |   50 | LEU  | CD1  | CD2  | 7.1  | 107.8    | 0.00
 1ihq | B |    7 | LEU  | CD1  | CD2  | 6.7  | 103.2    | 0.11
 2b1w | A |   22 | LEU  | CD1  | CD2  | 6.6  | 78.3     | 0.00
 2k9q | B |   58 | LEU  | CD1  | CD2  | 6.0  | 66.9     | 0.01
 1j6y | A |   14 | LEU  | CD1  | CD2  | 6.0  | 98.6     | 0.01
 2hfd | A |   62 | LEU  | CD1  | CD2  | 6.0  | 55.8     | 0.00
 2kj4 | A |   52 | LEU  | CD1  | CD2  | 5.9  | 66.7     | 0.00
 2l1s | A |   63 | LEU  | CD1  | CD2  | 5.9  | 59.2     | 0.00
 1jfn | A |   69 | LEU  | CD1  | CD2  | 5.9  | 85.7     | 0.12
 2e9k | A |   43 | LEU  | CD1  | CD2  | 5.8  | 52.9     | 0.00
 1bj8 | A |   73 | LEU  | CD1  | CD2  | 5.7  | 80.9     | 0.00
 2kno | A |  110 | LEU  | CD1  | CD2  | 5.7  | 75.1     | 0.00
 1r8u | B |  357 | LEU  | CD1  | CD2  | 5.7  | 76.6     | 0.00
 1ckv | A |   42 | LEU  | CD1  | CD2  | 5.7  | 75.5     | 0.02
 2kbm | D |   33 | LEU  | CD1  | CD2  | 5.6  | 90.6     | 0.00

 -- result 213 residue around 180
 pdb  | c | num  | name | name | name |  csd  | chi2_avg | chi2_cv
------+---+------+------+------+------+-------+----------+---------
 1pux | A |   52 | LEU  | CD1  | CD2  | -11.4 | 148.3    | 0.00
 2tmp | A |  100 | LEU  | CD1  | CD2  | -7.4  | 151.9    | 0.01
 2joq | A |   37 | LEU  | CD1  | CD2  | -6.7  | 173.5    | 0.00
 2ro5 | B |   46 | LEU  | CD1  | CD2  | -6.7  | 161.7    | 0.00
 2mfn | A |   62 | LEU  | CD1  | CD2  | -6.5  | 174.7    | 0.00
 1mfn | A |   62 | LEU  | CD1  | CD2  | -6.5  | 168.1    | 0.00
 1wjj | A |   22 | LEU  | CD1  | CD2  | -6.5  | 171.1    | 0.00
 2kiv | A |   87 | LEU  | CD1  | CD2  | -6.5  | 169.9    | 0.01
 2g3q | B |   50 | LEU  | CD1  | CD2  | -6.4  | 177.4    | 0.00
 1jw3 | A |   66 | LEU  | CD1  | CD2  | -6.4  | 176.3    | 0.01
 2kdi | A |   59 | LEU  | CD1  | CD2  | -6.3  | 158.8    | 0.01
 1x1f | A |  130 | LEU  | CD1  | CD2  | -6.2  | 184.5    | 0.00
 2e9k | A |   60 | LEU  | CD1  | CD2  | -6.1  | 178.1    | 0.00
 2ksv | A |  204 | LEU  | CD1  | CD2  | -6.1  | 195.2    | 0.00
 1bld | A |  127 | LEU  | CD1  | CD2  | -6.0  | 184.5    | 0.00
 1wk0 | A |   89 | LEU  | CD1  | CD2  | -6.0  | 187.9    | 0.00
 3eza | B |   77 | LEU  | CD1  | CD2  | -6.0  | 171.0    | 0.00

-- Result Vuister lab: bad rotamer
 pdb  | c | num | name | name | name | csd  | chi2_avg | chi2_cv
------+---+-----+------+------+------+------+----------+---------
 1mo7 | A | 559 | LEU  | CD1  | CD2  | 0.9  | 330.7    | 0.01
 1mo7 | A | 456 | LEU  | CD1  | CD2  | 2.3  | 305.4    | 0.00
 1mo7 | A | 443 | LEU  | CD1  | CD2  | 1.8  | 257.5    | 0.00
 1mo8 | A | 523 | LEU  | CD1  | CD2  | 1.3  | 277.2    | 0.00
 1mo8 | A | 440 | LEU  | CD1  | CD2  | 2.6  | 310.7    | 0.00
 1pd7 | A |  73 | LEU  | CD1  | CD2  | -0.5 | 304.4    | 0.00
 1qjt | A |  94 | LEU  | CD1  | CD2  | 3.8  | 295.3    | 0.00
 1qjt | A |  59 | LEU  | CD1  | CD2  | 3.2  | 279.2    | 0.00
 1qjt | A |  37 | LEU  | CD1  | CD2  | -0.8 | 291.1    | 0.00
 1qjt | A |  12 | LEU  | CD1  | CD2  | 2.2  | 296.6    | 0.00
 2fws | A | 486 | LEU  | CD1  | CD2  | 3.2  | 302.3    | 0.02
 2fws | A | 483 | LEU  | CD1  | CD2  | 2.5  | 294.1    | 0.00
 2fws | A | 401 | LEU  | CD1  | CD2  | 1.4  | 302.2    | 0.01
 2fws | A | 384 | LEU  | CD1  | CD2  | 0.7  | 288.2    | 0.00
 2fwu | A | 636 | LEU  | CD1  | CD2  | 2.9  | 314.0    | 0.00
 2fwu | A | 618 | LEU  | CD1  | CD2  | 1.5  | 313.5    | 0.00
 2fwu | A | 596 | LEU  | CD1  | CD2  | -0.5 | 315.8    | 0.00
 2fwu | A | 589 | LEU  | CD1  | CD2  | -1.1 | 301.9    | 0.00
 2fwu | A | 526 | LEU  | CD1  | CD2  | 2.2  | 304.8    | 0.00
(19 rows)

-- Result Vuister lab: all values fixed rotameric state. Sorted by csd.
 pdb  | c | num | name | name | name | csd  | chi2_avg | chi2_cv
------+---+-----+------+------+------+------+----------+---------
 2fwu | A | 642 | LEU  | CD1  | CD2  | -4.1 | 71.3     | 0.00
 1mo7 | A | 421 | LEU  | CD1  | CD2  | -3.8 | 54.4     | 0.00
 1mo8 | A | 522 | LEU  | CD1  | CD2  | -3.7 | 71.6     | 0.01
 1mo7 | A | 522 | LEU  | CD1  | CD2  | -3.7 | 54.1     | 0.00
 1mo8 | A | 421 | LEU  | CD1  | CD2  | -3.6 | 64.6     | 0.01
 2fws | A | 392 | LEU  | CD1  | CD2  | -3.5 | 74.2     | 0.00
 1mo7 | A | 558 | LEU  | CD1  | CD2  | -3.3 | 42.1     | 0.00
 1mo7 | A | 504 | LEU  | CD1  | CD2  | -3.1 | 67.5     | 0.00
 1mo8 | A | 457 | LEU  | CD1  | CD2  | -2.7 | 98.0     | 0.01
 1mo7 | A | 457 | LEU  | CD1  | CD2  | -2.5 | 88.0     | 0.01
 1mo7 | A | 515 | LEU  | CD1  | CD2  | -2.1 | 54.8     | 0.00
 1mo8 | A | 515 | LEU  | CD1  | CD2  | -2.1 | 82.1     | 0.00
 2jsx | A |  56 | LEU  | CD1  | CD2  | -1.9 | 65.8     | 0.00
 1mo7 | A | 490 | LEU  | CD1  | CD2  | -1.7 | 102.7    | 0.01
 2fwu | A | 589 | LEU  | CD1  | CD2  | -1.1 | 301.9    | 0.00
 1ozi | A |  32 | LEU  | CD1  | CD2  | -0.9 | 185.3    | 0.00
 1qjt | A |  37 | LEU  | CD1  | CD2  | -0.8 | 291.1    | 0.00
 1mo8 | A | 490 | LEU  | CD1  | CD2  | -0.8 | 162.2    | 0.00
 1mo8 | A | 530 | LEU  | CD1  | CD2  | -0.8 | 76.8     | 0.00
 1mo7 | A | 530 | LEU  | CD1  | CD2  | -0.6 | 78.8     | 0.00
 2fwu | A | 596 | LEU  | CD1  | CD2  | -0.5 | 315.8    | 0.00
 1pd7 | A |  73 | LEU  | CD1  | CD2  | -0.5 | 304.4    | 0.00
 2jsx | A |  74 | LEU  | CD1  | CD2  | -0.5 | 180.5    | 0.00
 1ozi | A | 101 | LEU  | CD1  | CD2  | -0.1 | 72.2     | 0.01
 1mo7 | A | 588 | LEU  | CD1  | CD2  | 0.2  | 83.3     | 0.00
 1mo8 | A | 588 | LEU  | CD1  | CD2  | 0.2  | 172.1    | 0.00
 1pd7 | A |  22 | LEU  | CD1  | CD2  | 0.3  | 171.0    | 0.00
 1brv | A | 185 | LEU  | CD1  | CD2  | 0.4  | 175.1    | 0.00
 1y7n | A |  16 | LEU  | CD1  | CD2  | 0.4  | 71.5     | 0.00
 2jsx | A |  44 | LEU  | CD1  | CD2  | 0.5  | 170.0    | 0.00
 1mo8 | A | 559 | LEU  | CD1  | CD2  | 0.6  | 173.5    | 0.02
 2fws | A | 384 | LEU  | CD1  | CD2  | 0.7  | 288.2    | 0.00
 2fws | A | 457 | LEU  | CD1  | CD2  | 0.8  | 175.2    | 0.00
 1mo7 | A | 559 | LEU  | CD1  | CD2  | 0.9  | 330.7    | 0.01
 2fws | A | 475 | LEU  | CD1  | CD2  | 1.3  | 178.7    | 0.00
 1mo8 | A | 523 | LEU  | CD1  | CD2  | 1.3  | 277.2    | 0.00
 1mo7 | A | 523 | LEU  | CD1  | CD2  | 1.3  | 173.8    | 0.00
 1mo8 | A | 553 | LEU  | CD1  | CD2  | 1.4  | 132.7    | 0.07
 2fws | A | 401 | LEU  | CD1  | CD2  | 1.4  | 302.2    | 0.01
 2fwu | A | 618 | LEU  | CD1  | CD2  | 1.5  | 313.5    | 0.00
 2jsx | A |  10 | LEU  | CD1  | CD2  | 1.6  | 174.3    | 0.00
 1mo8 | A | 427 | LEU  | CD1  | CD2  | 1.7  | 163.0    | 0.00
 1mo7 | A | 427 | LEU  | CD1  | CD2  | 1.7  | 173.3    | 0.00
 1mo8 | A | 443 | LEU  | CD1  | CD2  | 1.8  | 147.6    | 0.05
 1mo7 | A | 443 | LEU  | CD1  | CD2  | 1.8  | 257.5    | 0.00
 2fwu | A | 560 | LEU  | CD1  | CD2  | 1.8  | 174.6    | 0.00
 1mo8 | A | 560 | LEU  | CD1  | CD2  | 1.8  | 171.1    | 0.00
 1pd7 | A |  43 | LEU  | CD1  | CD2  | 1.9  | 176.4    | 0.00
 1qjt | A |  35 | LEU  | CD1  | CD2  | 1.9  | 168.2    | 0.00
 1qjt | A |  43 | LEU  | CD1  | CD2  | 2.0  | 162.8    | 0.01
 1mo7 | A | 560 | LEU  | CD1  | CD2  | 2.0  | 171.0    | 0.00
 1mo7 | A | 543 | LEU  | CD1  | CD2  | 2.1  | 197.6    | 0.00
 1mo8 | A | 543 | LEU  | CD1  | CD2  | 2.1  | 166.7    | 0.00
 1y7n | A |  22 | LEU  | CD1  | CD2  | 2.1  | 187.0    | 0.00
 1mo7 | A | 545 | LEU  | CD1  | CD2  | 2.1  | 178.2    | 0.00
 2fwu | A | 526 | LEU  | CD1  | CD2  | 2.2  | 304.8    | 0.00
 1qjt | A |  12 | LEU  | CD1  | CD2  | 2.2  | 296.6    | 0.00
 1brv | A | 183 | LEU  | CD1  | CD2  | 2.3  | 180.0    | 0.00
 1mo7 | A | 456 | LEU  | CD1  | CD2  | 2.3  | 305.4    | 0.00
 1mo8 | A | 545 | LEU  | CD1  | CD2  | 2.3  | 167.0    | 0.00
 1mo7 | A | 440 | LEU  | CD1  | CD2  | 2.4  | 169.1    | 0.00
 2jsx | A |  26 | LEU  | CD1  | CD2  | 2.4  | 181.0    | 0.00
 1pd7 | A |  80 | LEU  | CD1  | CD2  | 2.4  | 182.2    | 0.00
 1mo8 | A | 456 | LEU  | CD1  | CD2  | 2.5  | 143.2    | 0.08
 2fws | A | 483 | LEU  | CD1  | CD2  | 2.5  | 294.1    | 0.00
 1mo8 | A | 440 | LEU  | CD1  | CD2  | 2.6  | 310.7    | 0.00
 1qjt | A |  91 | LEU  | CD1  | CD2  | 2.8  | 162.7    | 0.00
 1mo7 | A | 553 | LEU  | CD1  | CD2  | 2.8  | 175.2    | 0.00
 2jsx | A |  70 | LEU  | CD1  | CD2  | 2.9  | 178.8    | 0.00
 1mo7 | A | 583 | LEU  | CD1  | CD2  | 2.9  | 175.3    | 0.00
 2fwu | A | 636 | LEU  | CD1  | CD2  | 2.9  | 314.0    | 0.00
 1ozi | A |  78 | LEU  | CD1  | CD2  | 2.9  | 171.1    | 0.00
 1qjt | A |  87 | LEU  | CD1  | CD2  | 3.1  | 171.3    | 0.00
 1qjt | A |   7 | LEU  | CD1  | CD2  | 3.1  | 149.7    | 0.08
 2fws | A | 486 | LEU  | CD1  | CD2  | 3.2  | 302.3    | 0.02
 1qjt | A |  59 | LEU  | CD1  | CD2  | 3.2  | 279.2    | 0.00
 1qjt | A |  53 | LEU  | CD1  | CD2  | 3.2  | 178.6    | 0.00
 1ozi | A |  71 | LEU  | CD1  | CD2  | 3.3  | 181.8    | 0.00
 1mo8 | A | 583 | LEU  | CD1  | CD2  | 3.3  | 178.5    | 0.00
 2fws | A | 460 | LEU  | CD1  | CD2  | 3.4  | 181.2    | 0.00
 1mo7 | A | 548 | LEU  | CD1  | CD2  | 3.4  | 137.3    | 0.10
 1mo8 | A | 548 | LEU  | CD1  | CD2  | 3.4  | 180.1    | 0.00
 1mo8 | A | 534 | LEU  | CD1  | CD2  | 3.5  | 238.5    | 0.03
 1mo7 | A | 534 | LEU  | CD1  | CD2  | 3.5  | 200.5    | 0.01
 1qjt | A |  68 | LEU  | CD1  | CD2  | 3.5  | 183.6    | 0.01
 1qjt | A |  96 | LEU  | CD1  | CD2  | 3.6  | 157.8    | 0.00
 1mo8 | A | 505 | LEU  | CD1  | CD2  | 3.7  | 169.0    | 0.00
 1mo7 | A | 505 | LEU  | CD1  | CD2  | 3.7  | 162.7    | 0.00
 1qjt | A |  94 | LEU  | CD1  | CD2  | 3.8  | 295.3    | 0.00
 1pd7 | A |  32 | LEU  | CD1  | CD2  | 4.0  | 153.9    | 0.00
 1qjt | A |  77 | LEU  | CD1  | CD2  | 4.0  | 185.2    | 0.00
 1qjt | A |   9 | LEU  | CD1  | CD2  | 4.1  | 191.1    | 0.00
 1pd7 | A |  72 | LEU  | CD1  | CD2  | 4.1  | 179.7    | 0.00
 1pd7 | A |  35 | LEU  | CD1  | CD2  | 4.3  | 202.4    | 0.00
 1qjt | A |  48 | LEU  | CD1  | CD2  | 4.4  | 156.5    | 0.00
 1qjt | A |  79 | LEU  | CD1  | CD2  | 5.7  | 172.8    | 0.00
