#!/bin/tcsh

# Find all invalid Tgz in dir and further process with handyCommands.csh
# USAGE: $CINGROOT/scripts/vcing/checkCingTgz.csh

cd $D/NRG-CING/data
set list = ( `cat $D/NRG-CING/entry_list_nmr_random_3.csv`)
#set list = ( 1brv )
echo "Looking for $#list entries"
#set x = 1brv
foreach x ( $list )
#    sleep 1 # chance to quit.
#    echo "$x"
    set ch23 = ( `echo $x | cut -c2-3` )
    set inputFile = $ch23/$x/$x.cing.tgz
    if ( ! -e $inputFile ) then
        echo "ERROR: $x missing $inputFile in $cwd"
        continue
    endif
    ls -l $inputFile
end
