#!/bin/tcsh

if ( -e /Users/jd/cingStableSetings.csh ) then
    source /Users/jd/cingStableSetings.csh
endif

set dataDir = $CINGROOT/python/cing/Scripts/data
set d1d2Dir = /Users/jd/tmp/cingTmpStable/d1d2_wi_db/data

cd $d1d2Dir

# check how many were started overall (multiple runs)
find . -name "*.log" | wc

# check for errors:
find . -name "*.log" | xargs grep ERROR
# check for dumps
find . -name "*.log" | xargs grep -i Trace
# check csv files for size (2k is reasonable)
find . -name "*.csv" -ls | sort -n -k7 | head
# mark as done
find . -name "*.csv" | gawk '{print toupper($0)}' | cut -c26-30 | sort > $dataDir/PDB_done.txt

# calculate list todo
relate $dataDir/PDB_WI_SELECT_Rfactor_2.1_Res2.0_2009-02-28.LIS difference $dataDir/PDB_done.txt $dataDir/PDB_todo.LIS
