#!/bin/tcsh -f
# MOVED INTO nrgCing.py AFTER PROTOTYPING.
# Finds the last log for each NRG-CING run and does something to it.
# Watch out when modifying this command
# Execute like:
# $CINGROOT/scripts/cing/analyzeLastLogNRG-CING.csh

cd /Library/WebServer/Documents/NRG-CING/data
set logFileListName = '../logFileList.csv'

set list = ( `find . -depth 2 -name "[0-9]*" | cut -c6- | sort` )
set listTodo = ()
set listCrashed = ()
set listStopped = ()
set listOk = ()
echo "Found number of entries:         $#list"

set logFileList = ()
set listTimeTaken = ()


foreach x ( $list )
    #echo "Doing $x"
    set ch23 = ( `echo $x | cut -c2-3` )
    set logFile = (`find $ch23/$x -depth 1 -name "$x*.log" | sort | tail -1`)
    if ( $?logFile ) then
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