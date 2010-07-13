#!/bin/csh
# Author: Jurgen F. Doreleijers
# Execute like:
# $CINGROOT/scripts/cing/manualUpdatePdbjMine.csh >& manualUpdatePdbjMine.log &
# tail -f manualUpdatePdbjMine.log &
set tmp_dir = /Users/jd/tmpPdbj
###################################################################

cd $tmp_dir

set list = ( pdbmlplus_weekly.2010-03-09.gz pdbmlplus_weekly.2010-03-16.gz pdbmlplus_weekly.2010-03-23.gz pdbmlplus_weekly.2010-03-31.gz pdbmlplus_weekly.2010-04-07.gz pdbmlplus_weekly.2010-04-14.gz pdbmlplus_weekly.2010-04-21.gz pdbmlplus_weekly.2010-04-28.gz pdbmlplus_weekly.2010-05-05.gz pdbmlplus_weekly.2010-05-12.gz pdbmlplus_weekly.2010-05-19.gz pdbmlplus_weekly.2010-05-26.gz pdbmlplus_weekly.2010-06-02.gz pdbmlplus_weekly.2010-06-09.gz pdbmlplus_weekly.2010-06-16.gz pdbmlplus_weekly.2010-06-23.gz pdbmlplus_weekly.2010-06-30.gz pdbmlplus_weekly.2010-07-07.gz )

pg_restore -d pdbmlplus pdbmlplus.dump

foreach fn ( $list )
        echo 'loading from $fn'
        gunzip < $fn | psql pdbmlplus pdbj
end

echo 'DONE'
