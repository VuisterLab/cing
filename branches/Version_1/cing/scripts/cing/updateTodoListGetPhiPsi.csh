#!/bin/tcsh

# count check:
# 5160 overall
# 5135 excluding 25 obsoletes
# 5135 *_hyd.pdb
# 5135 logs
# 5131 csv

set tmpDirCing = cingTmp
if ( -e /Users/jd/cingStableSettings.csh ) then
    source /Users/jd/cingStableSettings.csh
    set tmpDirCing = cingTmpStable
endif

set dataDir = $CINGROOT/python/cing/Scripts/data
set d1d2Dir = /Users/jd/tmp/$tmpDirCing/d1d2_wi_db/data

cd $d1d2Dir

# check how many were started overall (multiple runs)
find . -name "*.log" | wc

# check for errors:
find . -name "*.log" | xargs grep ERROR
# check for dumps (maar 1 bij 414 gedaan)
find . -name "*.log" | xargs grep -i Trace
# check as done
find . -name "*.csv" | wc
# check as done
find ../pdb_hyd -name "*_hyd.pdb" | wc
# check csv files for size (2k is reasonable)
find . -name "*.csv" -ls | sort -n -k7 | head
# mark as done
find . -name "*.csv" | gawk '{print toupper($0)}' | cut -c26-30 | sort > $dataDir/PDB_done.txt

# calculate list todo
relate $dataDir/PDB_WI_SELECT_Rfactor_2.1_Res2.0_2009-02-28.LIS difference $dataDir/PDB_done.txt $dataDir/PDB_done_tmp.txt
gawk '{print toupper($0)}' $dataDir/PDB_done_tmp.txt > $dataDir/PDB_todo.txt
rm $dataDir/PDB_done_tmp.txt


foreach x ( $obsoleteList )
    echo "Doing $x"
    set ch23 = ( `echo $x | cut -c2-3` )
    set dirToDelete = $d1d2Dir/$ch23/$x
    \rm -rf $dirToDelete
end