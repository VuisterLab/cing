-- Login by:
--      psql pdbmlplus pdbj
-- Or use:
--      echo "SELECT count(*) FROM recoord.cingentry;" | psql pdbmlplus pdbj

SELECT count(*) FROM nmr_redo.cingentry;
SELECT name, residue_count FROM nmr_redo.cingentry;

select * from nrgcing.cingentry where name = '2lfh';

SELECT e.name, c.name, r.number, a.name 
FROM 
nrgcing.cingentry    e,
nrgcing.cingchain    c,
nrgcing.cingresidue  r,
nrgcing.cingatom     a
where
e.entry_id = c.entry_id AND
c.chain_id = r.chain_id AND
r.residue_id = a.residue_id AND
e.name = '2lfh' AND
c.name = 'A' AND
r.number = 68 AND
a.name like 'O%'


CREATE TABLE nmr_redo.tmpentrylist
(    pdb_id                       VARCHAR(255) UNIQUE PRIMARY KEY );
COPY nmr_redo.tmpentrylist     FROM '/Library/WebServer/Documents/NMR_REDO/list/tmpentrylist.csv'   CSV HEADER;

SELECT count(*) 
FROM nmr_redo.cingentry e1
WHERE e1.name in ( select pdb_id from nmr_redo.tmpentrylist )

WHERE e1.name in ( '1brv', '1dum', '1mmc' )

e1.name in ( select pdb_id from nmr_redo.tmpentrylist )


select e1.name as pdb_id,
e2.dis_rms_all - e1.dis_rms_all as delta_dis_rms_all
from
recoord.cingentry  e1,
nmr_redo.cingentry e2
where e1.name = e2.name AND
e1.name = '1brv' AND
e2.model_count = 25 -- selects just those that are done with large number of models.
order by e1.res_count desc, e1.name
limit 10
;

-- e1.name = '1brv' AND
-- select e1.name, r1.number, r1.sel_1, r2.sel_1, r2.wi_ramchk - r1.wi_ramchk
select e1.name, e2.model_count, avg( r2.wi_ramchk - r1.wi_ramchk )
from
recoord.cingresidue   r1,
nmr_redo.cingresidue  r2,
recoord.cingentry  e1,
nmr_redo.cingentry e2
where
e1.name = e2.name AND
e2.model_count > 2 AND
r1.entry_id = e1.entry_id AND
r2.entry_id = e2.entry_id AND
r1.number = r2.number AND
r1.cv_backbone IS NOT NULL -- select only residues with coordinates
group by e1.name, e2.model_count
order by avg( r2.wi_ramchk - r1.wi_ramchk )
order by e1.name asc, r1.number asc
;

DROP TABLE IF EXISTS nmr_redo.testResidue;
create table nmr_redo.testResidue (
    residue_id                     SERIAL UNIQUE PRIMARY KEY,
    sel_2                     BOOLEAN DEFAULT NULL
)
insert into nmr_redo.testResidue VALUES ( 1, NULL );
insert into nmr_redo.testResidue VALUES ( 2, NULL );
insert into nmr_redo.testResidue VALUES ( 3, NULL );



select count(*) from  recoord.cingresidue WHERE sel_1 = TRUE AND sel_2 = TRUE;
select count(*) from nmr_redo.cingresidue WHERE sel_1 = TRUE AND sel_2 = TRUE;
select count(*) from nmr_redo.cingentry e2 where e2.model_count < 25;

-- RECOORD manipulations
-- sel_2 means that the entry has 25 models in nmr_redo and 
-- See problemEntryListNMR_REDO.csv
update recoord.cingresidue set sel_2 = TRUE;
update recoord.cingresidue set sel_2 = FALSE where name IN ( '1omt' ); -- NRG issue 278 Bounds badly interpreted or specified
update recoord.cingresidue set sel_2 = FALSE where name IN ( '1u2f' ); -- NRG issue 279 XPLOR atom name HG1# for Thr should be mapped to methyl i.s.o. hydroxyl proton


-- NMR_REDO manipulations
-- sel_2 is set everywhere in recoord.
update nmr_redo.cingresidue set sel_2 = FALSE;
update nmr_redo.cingresidue set sel_2 = TRUE where residue_id IN
( 
select r2.residue_id
    from
    nmr_redo.cingresidue  r2,
    nmr_redo.cingentry e2
    where
    r2.entry_id = e2.entry_id AND
    e2.model_count = 25
);

--     e2.name = '1brv'    

select residue_id, r0.distance_count 
from  
    nrgcing.cingresidue  r0,
    nrgcing.cingentry e0
WHERE 
    r0.entry_id = e0.entry_id AND
e0.name = '1brv' AND
r0.name = 'PRO' AND
r0.number = 172
;
-- OTHER
( 
select r2.residue_id
    from
    nmr_redo.cingresidue  r2,
    nmr_redo.cingentry e2
    where
    r2.entry_id = e2.entry_id AND
    e2.model_count = 25 
)
;

select name, sel_2 from recoord.cingentry;

-- Get outliers from selections.
select e1.name, r1.name, r1.number, r1.pc_gf_PHIPSI, r2.pc_gf_PHIPSI
from 
    recoord.cingresidue  r1,
    recoord.cingentry e1,
    nmr_redo.cingresidue  r2,
    nmr_redo.cingentry e2
where 
e1.name = e2.name AND
r1.entry_id = e1.entry_id AND
r2.entry_id = e2.entry_id AND
r1.number = r2.number AND
r1.sel_1 = TRUE AND
r2.sel_1 = TRUE AND
r2.sel_2 = TRUE AND
(
r1.pc_gf_PHIPSI > 8 or
r2.pc_gf_PHIPSI > 8
);


-- Get outliers from selections.
select e1.name, r1.name, r1.number, r1.pc_gf_PHIPSI, r2.pc_gf_PHIPSI
from 
    nrgcing.cingresidue  r1,
    nrgcing.cingentry e1,
    nmr_redo.cingresidue  r2,
    nmr_redo.cingentry e2
where 
e1.name = e2.name AND
r1.entry_id = e1.entry_id AND
r2.entry_id = e2.entry_id AND
r1.number = r2.number AND
r1.sel_1 = TRUE AND
r2.sel_1 = TRUE AND
r2.sel_2 = TRUE AND
(
r1.pc_gf_PHIPSI > 1.5 or
r2.pc_gf_PHIPSI > 1.5
);


select e1.name, e1.distance_count
from 
nrgcing.cingresidue  r1,
nrgcing.cingentry e1
where 
r1.entry_id = e1.entry_id AND
e1.distance_count > 0 AND
e1.protein_count        > 0 AND 
e1.dna_count            = 0 AND 
e1.rna_count            = 0 AND 
e1.dna_rna_hybrid_count = 0 
group by e1.name, e1.distance_count





