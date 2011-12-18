#!/bin/tcsh

echo "tejst"
exit 1

# Author: Jurgen F. Doreleijers
# Execute like:
# $CINGROOT/scripts/cing/manualUpdatePdbjMine.csh >>& ~/Library/Logs/weeklyUpdatePdbjMine.log
# tail -f manualUpdatePdbjMine.log &
# Takes about 6 hours for restore and about one hour per small sized weekly.
# the 1.1G Jul  7 16:11 pdbmlplus_weekly.2010-02-09.gz is unknown for duration.
# Source data comes from: ftp://ftp.pdbj.org/mine

#set tmp_dir = /Users/jd/tmpPdbj
set tmp_dir = /home/i/tmpPdbj
###################################################################

cd $tmp_dir

set list = ( pdbmlplus_weekly.2010-07-21.gz )

# Takes about 77 Gb and 3 hrs.
if ( 1 ) then
    date
    echo "Starting initial restore"
    pg_restore -d pdbmlplus pdbmlplus.dump
    date
    echo "Finished initial restore"
endif

if ( 0 ) then
    date
    echo "Starting weekly updates"
    foreach fn ( $list )
        date
        echo "loading from $fn"
        gunzip < $fn | psql pdbmlplus pdbj
    end
    date
    echo "Ending weekly updates"
endif

date
echo 'DONE'
