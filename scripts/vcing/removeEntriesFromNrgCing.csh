#!/bin/tcsh
#
# USAGE: $CINGROOT/scripts/vcing/removeEntriesFromNrgCing.csh
#

#set D = /home/jurgenfd/D

set inputDir = $D/NRG-CING/data
cd $inputDir
echo "Working from $cwd"
#set list = ( `find . -maxdepth 3 -name "*.tgz"`)
set list = ( `cat ~/toRemove.csv`)
set list = ( 1b0q )
echo "Working on $#list entries"

foreach x ( $list )
    echo "$x"
    set ch23 = ( `echo $x | cut -c2-3` )
    /bin/rm -rf $ch23/$x
    if ( $status ) then
        echo "ERROR: $x"
    endif
end

echo "Done with removing"