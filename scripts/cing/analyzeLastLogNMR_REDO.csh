#!/bin/tcsh -f
# MOVED INTO nrgCing.py AFTER PROTOTYPING.
# Finds the last log for each NRG-CING run and does something to it.
# Watch out when modifying this command
# Execute like:
# $CINGROOT/scripts/cing/analyzeLastLogNMR_REDO.csh

set projectId = NMR_REDO

cd /Library/WebServer/Documents/$projectId/data
set logFileListName = '../logFileList.csv'

zcat $D/RDB/pgsql/backup_2011-09-29/nmr_redo.cingentry.csv.gz | gawk -F , '{m=$38;if((NR>1) && (m=25))print $2}' | sort > ~/nmr_redo_entries.csv
set list = ( `cat ~/nmr_redo_entries.csv`)
echo "Found number of entries:         $#list"
set listTodo = ()
set listCrashed = ()
set listStopped = ()
set listOk = ()

set logFileList = ()
set listTimeTaken = ()
foreach x ( $list )
    echo "Doing $x"
    set ch23 = ( `echo $x | cut -c2-3` )
    set logFile = (`find $ch23/$x/log_refineEntry -depth 1 -name "$x*.log" | sort | tail -1`)
    if ( $?logFile ) then
        echo "Checking $logFile"
        set logFileList = ($logFileList $logFile)
        set timeTaken = (` grep 'CING took       :' $logFile | gawk '{print $(NF-1)}' `)
        if ( $timeTaken != "" ) then
            echo "$x [$timeTaken]"
            set listTimeTaken = ( $listTimeTaken $timeTaken )
            # Next grep gives a zero status if any match is found.
            grep --silent 'Traceback (most recent call last)' $logFile
            if ( $status ) then
                echo "$x all good"
                set listOk = ($listOk $x)
            else
                echo "ERROR $x traceback found"
                set listCrashed = ($listCrashed $x)
            endif
        else
            echo "ERROR $x failed to finish"
            set listStopped = ($listStopped $x)
        endif
    else
        echo "ERROR $x not started"
        set listTodo = ($listTodo $x)
    endif
end

echo "listTimeTaken: $listTimeTaken"
echo $listTimeTaken | gawk '{for (i=1; i<=NF; i++) sum += $(i);print "NF,av is:", NF, sum/NF}'
echo "Again, found number of entries:  $#list"
echo "Found number of entries todo:    $#listTodo"
echo "Found number of entries crashed: $#listCrashed"
echo "Found number of entries stopped: $#listStopped"
echo "Found number of entries ok:      $#listOk"

\rm -f $logFileListName >& /dev/null
foreach x ( $logFileList )
    echo $x >> $logFileListName
end



echo "\nFound number of log files: $#logFileList"

exit 0

### junk
