-- Login by:
--      psql pdbmlplus pdbj
-- Or use:
--      echo "SELECT count(*) FROM recoord.cingentry;" | psql pdbmlplus pdbj

SELECT count(*) FROM nmr_redo.cingentry;
SELECT name, residue_count FROM nmr_redo.cingentry;

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

-- sel_2 means that the entry has 25 models in nmr_redo and 
-- sel_2 is set everywhere in recoord.
update recoord.cingresidue set sel_2 = TRUE;

update nmr_redo.cingresidue set sel_2 = TRUE where residue_id IN
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
select count(*) from recoord.cingresidue WHERE sel_2 = TRUE;


update recoord.cingresidue set sel_2 = TRUE;
-- NRG issue 278 Bounds badly interpreted or specified
update recoord.cingresidue set sel_2 = FALSE where name IN ( '1omt' );
-- NRG issue 279 XPLOR atom name HG1# for Thr should be mapped to methyl i.s.o. hydroxyl proton
update recoord.cingresidue set sel_2 = FALSE where name IN ( '1u2f' );

select count(*)
from recoord.cingresidue r2
where r2.sel_2 = TRUE;

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
select e1.name, r1.name, r1.number, r1.wi_plnchk
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
r1.wi_plnchk > 4;

