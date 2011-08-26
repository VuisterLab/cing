-- Login by:
--      psql pdbmlplus pdbj
-- Or use:
--      echo "SELECT count(*) FROM recoord.cingentry;" | psql pdbmlplus pdbj

SELECT count(*) FROM recoord.cingentry;

CREATE TABLE nmr_redo.tmpentrylist
(    pdb_id                       VARCHAR(255) UNIQUE PRIMARY KEY );
COPY nmr_redo.tmpentrylist     FROM '/Library/WebServer/Documents/NMR_REDO/list/tmpentrylist.csv'   CSV HEADER;

SELECT count(*) 
FROM nmr_redo.cingentry e1
WHERE e1.name in ( select pdb_id from nmr_redo.tmpentrylist )

WHERE e1.name in ( '1brv', '1dum', '1mmc' )

e1.name in ( select pdb_id from nmr_redo.tmpentrylist )


select e1.name as pdb_id,
e1.dis_max_all, 
e2.dis_max_all,
e1.dis_rms_all as e1dis_rms_all,
e2.dis_rms_all as e2dis_rms_all, 
e2.dis_rms_all - e1.dis_rms_all as ddis_rms_all, 
e1.rev_last,
e2.rev_last
from
recoord.cingentry  e1,
nmr_redo.cingentry e2
where e1.name = e2.name
order by e1.name;
