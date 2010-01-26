#!/bin/csh -f
# Author: Jurgen F. Doreleijers
# Fri Jun  2 14:37:52 CDT 2006

set tmp_dir = /tmp
###################################################################
## No changes below

cd $tmp_dir

set date_string = (`date "+%Y_%m_%d-%H_%M_%S"`)
set LOG         = weeklyUpdatePdbjMine_$date_string.log
set TMPFILE     = pdbmlplus_weekly.latest.gz

if ( -e $TMPFILE ) then
	rm $TMPFILE
endif

wget ftp://ftp.pdbj.org/mine/weekly/$TMPFILE >& $LOG
if ( $status ) then
	echo "ERROR: failed to download $TMPFILE"
	exit 1
endif

if ( ! -e $TMPFILE ) then
	echo "ERROR: $TMPFILE not found"
	exit 1
endif

gunzip < $TMPFILE | psql pdbmlplus pdbj >>& $LOG