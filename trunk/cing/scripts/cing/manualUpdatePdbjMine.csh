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

set tmp_dir = /Users/jd/tmpPdbj
#set tmp_dir = /home/i/tmpPdbj
#set tmp_dir = /mnt/data/tmpPdbj
###################################################################

cd $tmp_dir
set date_string = (`date "+%Y_%m_%d-%H_%M_%S"`)
set log_dir     = $tmp_dir/logs
set list = ( pdbmlplus_weekly.2010-07-21.gz )

# Takes about 77 Gb and 3 hrs.
if ( 1 ) then
    date
    \rm -rf ftp.pdbj.org
    echo "Starting download of split archive; takes about 8 G."
    echo "From before: Downloaded: 86 files, 8.3G in 8h 38m 25s (281 KB/s)"    
    set prog_string = wgetSplit
    set log_file    = $log_dir/$prog_string"_$date_string".log
    wget -r ftp://ftp.pdbj.org/mine/split >& $log_file

    date
    echo "Dropping pdbj schema (Expect that this will take xx minutes)"
    set prog_string = pg_restore
    set log_file    = $log_dir/$prog_string"_$date_string".log
    echo "DROP SCHEMA IF EXISTS pdbj CASCADE;" | psql pdbmlplus pdbj
    echo "Starting restore from split dump files."
    (cat ftp.pdbj.org/mine/split/pdbmlplus_split.* | pg_restore -d pdbmlplus -U pdbj) >& $log_file
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
