#!/bin/csh -f
# Author: Jurgen F. Doreleijers
# $CINGROOT/scripts/cing/unpack_nmr_redo.csh

if ( -e $UJ/cingStableSettings.csh ) then
    source $UJ/cingStableSettings.csh
endif


set MIRRORDIR = $D/NMR_REDO
cd $MIRRORDIR/data
find . -maxdepth 3 -name "*.cing.tgz" -mtime -5 | cut -c11-14 | sort > ../entry_list_good-tries.csv

###################################################################

## No changes below except user id and specific word such as azvv.
set subl = ( 1brv )
#set subl = ( `cat $D/NMR_REDO/entry_list_good-tries.csv` )
#Untar and store to db (Create schema first and dep tables).

# Get argument pdb code if it exists.
if ( $1 != "" ) then
#    set subl = (  $1  )
    set subl = (  `echo $1 | sed 's/,/ /'g`  )
endif


echo "Doing" $#subl "pdb entries"
foreach x ( $subl )
    echo "Doing $x"
    set ch23 = ( `echo $x | cut -c2-3` )
    set subdirLoc = $MIRRORDIR/data/$ch23/$x
    cd $subdirLoc
    if ( -e $x.cing ) then
        echo "Removing previous cing unpacked project"
        \rm -rf $x.cing
    endif
    $C/python/cing/NRG/nmr_redo.py $x storeCING2db
end

echo "Finished"