#!/bin/csh -f
# Author: Jurgen F. Doreleijers
# Fri Jun  2 14:37:52 CDT 2006

set tmp_dir = /Users/jd/tmpPdbj
###################################################################
## No changes below

cd $tmp_dir

set today     = (`date       "+%Y-%m-%d"`)
set yesterday = (`date -v-1d "+%Y-%m-%d"`)

foreach d ( $today $yesterday )
	set fn = pdbmlplus_weekly.$d.gz
	if ( -e $fn ) then
		echo "$fn already existed. Skipping update now."
		exit 0
	endif
	wget --no-verbose ftp://ftp.pdbj.org/mine/weekly/$fn
	if ( $status ) then
		if ( $d == $today ) then
			echo "Failed to download today's file $fn"
		else
			echo "WARNING: Failed to download yesterdays file $fn"
			exit 1
		endif
	else
		if ( ! -e $fn ) then
			echo "ERROR: Downloaded file $fn not found"
			exit 1
		endif
		if ( -z $fn ) then
			echo "ERROR: Downloaded empty file $fn"
			exit 1
		endif
		echo "Downloaded $fn"
		# break out off for loop.
		continue
	endif
end

gunzip < $fn | psql pdbmlplus pdbj