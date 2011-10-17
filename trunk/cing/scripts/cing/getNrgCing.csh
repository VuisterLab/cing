#!/bin/csh -f
# Author: Jurgen F. Doreleijers
# $CINGROOT/scripts/cing/getNrgCing.csh 1brv
set SERVER=localhost-nmr
# trailing slash is important.
#set SOURCEDIR=/Library/WebServer/Documents/NRG-CING/
set SOURCEDIR=/Library/WebServer/Documents/NRG-CING
set MIRRORDIR=/Library/WebServer/Documents/NRG-CING

###################################################################

## No changes below except user id and specific word such as azvv.

#set subl = ( 1brv )
set subl = (`cat /Users/jd/entry_list_of_interest.csv`)
#set subl = (`cat $list_dir/bmrbPdbEntryList.csv`)

# Get argument pdb code if it exists.
if ( $1 != "" ) then
#    set subl = (  $1  )
    set subl = (  `echo $1 | sed 's/,/ /'g`  )
endif


echo "Doing" $#subl "pdb entries"
foreach x ( $subl )
    echo "Doing $x"
    cd
    set ch23 = ( `echo $x | cut -c2-3` )
    set subdirSrcLoc = $SOURCEDIR/data/$ch23/$x
    set subdirLoc = $MIRRORDIR/data/$ch23/$x
    if ( -e $subdirLoc ) then
        echo "Removing dir: " $subdirLoc
        \rm -rf $subdirLoc
    endif
    mkdir -p $subdirLoc    
    scp -r -P 39676 $SERVER':'$subdirSrcLoc/$x.cing.tgz $subdirLoc
    cd $subdirLoc
    tar -xzf $x.cing.tgz
end

echo "Finished"