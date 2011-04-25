#!/bin/tcsh
# Find all invalid Tgz in dir and further process with handyCommands.csh
# USAGE: $CINGROOT/scripts/vcing/listInvalidTgz.csh >& ~/listInvalidTgz.log &
#

#set D = /home/jurgenfd/D
#set D = /Volumes/tetra/D
set D = /Volumes/terad/D

set inputDir = $D/NRG-CING/data
cd $inputDir
echo "Working from $cwd"
set list = ( `find . -maxdepth 3 -name "*.tgz"`)
#set list = ( "br/1brv/1brv.cing.tgz" )
echo "Working on $#list tgz"

foreach f ( $list )
    echo $f
    tar -tzf $f >& /dev/null
    if ( $status ) then
        echo "ERROR: $f"
    endif
end

echo "Done with listing"