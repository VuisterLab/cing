#!/bin/tcsh

# Find all invalid Tgz in dir

set inputDir = $D/NRG-CING/data
cd $inputDir
set list = ( `find . -name "*.tgz" -maxdepth 3 `)
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