#!/bin/tcsh

# One liners

set list = (`cat $D/NRG-CING/entry_list_prep_todo_2011-04-18b.csv`)
echo "Working on $#list entries"
#set list = ( 1brv )

foreach x ( $list )
    echo "Doing $x"
    set ch23 = ( `echo $x | cut -c2-3` )
    set inputFile = $D/NRG-CING/input/$ch23/$x.tgz
    if ( ! -e $inputFile ) then
        echo "ERROR: missing $inputFile"
        continue
    endif
    set targetUrl = /Library/WebServer/Documents/NRG-CING/input/$ch23
    set targetMachine = jd@dodos.dyndns.org
#    echo "Creating dir if not present"
    ssh $targetMachine mkdir -p $targetUrl
#    echo "Copying file"
    scp $D/NRG-CING/input/$ch23/$x.tgz $targetMachine\:$targetUrl
#    echo "Done with $x"
    sleep 1
end
