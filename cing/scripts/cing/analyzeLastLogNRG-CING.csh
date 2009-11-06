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



exit 0

# hand commands follow:
# scan for the maximum time taken.
grep '\[' ~/analyzeLastLogNRG-CING_2009-11-04.log | sed -e 's/\[//' | sed -e 's/\]//' | gawk '{print $2}' | sort -n | head

set listToRemove = ( 1f8h 2k77 2px9 1j6t 1jtw 2con 2new 1vrc 2exg 1dx1 1his 1hit 1r2n )
cd /Library/WebServer/Documents/NRG-CING/data
foreach x ( $listToRemove )
    set ch23 = ( `echo $x | cut -c2-3` )
    set entryDir = $ch23/$x
    \rm -rf $entryDir >& /dev/null
end


set list = ( 1bn0 1chv 1ont 1x5b 1xv3 1y8f 2ff0 2k0j 2k1n 2k3m 2k61 )
set list = ( 1xv3 2ff0 2k0j 2k1n 2k3m 2k61 )
cd /Library/WebServer/Documents/NRG-CING/data
set logFileList = ()
foreach x ( $list )
    set ch23 = ( `echo $x | cut -c2-3` )
    set logFile = (`find $ch23/$x -depth 1 -name "$x*.log" | sort | tail -1`)
    set logFileList = ($logFileList $logFile)
end
vi $logFileList


