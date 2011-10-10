#!/bin/tcsh -f

# Remove entry from archive in order for not to be considered wrong for an old problem.
# Watch out when modifying this command
# Execute like:
# $CINGROOT/scripts/cing/cleanArchive.csh

set maxToDelete = 2
set archiveId = "NRG-CING"
set A = $D/$archiveId
cat \
    $A/entry_list_prep_crashed.csv      $A/entry_list_prep_failed.csv  \
    $A/entry_list_crashed.csv           $A/entry_list_stopped.csv      \
    $A/entry_list_store_crashed.csv     $A/entry_list_store_failed.csv \
    $A/entry_list_store_not_in_db.csv \
    > $A/entry_list_tobewhippedout.csv
set list = ( 1brv 2hgh 9pcy )
#set list = ( `cat $A/entry_list_tobewhippedout.csv` )
    
####################################################################################
# No changes below.
####################################################################################

set deleteCount = 0
echo "Starting removing max of $#list entries from list: [$list]"
cd $D/$archiveId
foreach x ( $list )
    if ( $deleteCount >= $maxToDelete ) then
        echo "Stopping because already removed max $maxToDelete"
        break
    endif
    @ deleteCount = $deleteCount + 1
    echo "Doing $x for $deleteCount total."  
    set ch23 = ( `echo $x | cut -c2-3` )
    foreach sD ( data prep/C prep/F prep/S )
        if ( -d $sD/$ch23/$x ) then
            echo "Removing $sD/$ch23/$x"
            \rm -rf $sD/$ch23/$x
        else
            echo "DEBUG: no directory $sD/$ch23/$x"
        endif
    end
    if ( -e input/$ch23/$x/$x.tgz ) then
        echo "Removing input/$ch23/$x/$x.tgz"
        \rm input/$ch23/$x/$x.tgz
    endif
end

echo "Done removing"