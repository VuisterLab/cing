#!/bin/csh 
#  A simple script to restart the iCing server.

#  Since it isn't possible to determine if the server is in an ok state. Just plainly kill it.
#
# verbosity argument can be set to:
#   terse   (no output and no logging)
#   silent  (no output but to log file)
#   verbose (output to email even if the check was a success, 
#                including all logged from last verbose run.)
#   nomail  (for direct output of to screen)

# Run from cron as jd
# Remove per directory.
set script = iCingRestartServer

# Executables, might need full-path depending on the environs:
set mail_exe = mail

set verbosity = "$1"

# Whom to send the report to when it is done:
set mailto = jurgenfd@gmail.com

# Where to put the report for a bit before it gets mailed:
set tmpdir = /tmp
set logfile = $tmpdir/$script.log

## maximum number of bytes when all is successful
set maxtmpoutsize = 150

set sleepTimeCing = 5

#No admin changes below this line (I hope): - - - - - -
###################################################################

# tmp file has PID encoded inside to ensure uniqueness
# during the run:
set tmpout = $tmpdir/"$script"_$$.txt
set tmphead = $tmpdir/"$script"_head_$$.txt

set procList1 = (`ps -x | grep "python/cing/main.py --server" | grep -v grep | gawk '{print $1}'`) >& $tmpout
set procList2 = (`ps -x | grep "iCingByCgi.py"                | grep -v grep | gawk '{print $1}'`) >& $tmpout
set procList = ( $procList1 $procList2 )
echo "Found $#procList server processes: $procList to kill." >>& $tmpout

foreach procId ( $procList )
	kill -9 $procId  >>& $tmpout
end

sleep $sleepTimeCing

# Add to the tmpout if anything there...
ps -x | grep server | grep python | grep -i cing | grep -v grep  >>& $tmpout

#/usr/sbin/httpd -k restart
#sleep $sleepTimeApache

cing --server -v 9 >>& ~jd/cingServer.log &


#if ( $status ) then
#	echo "Failed to startup a new cing server:" >>& $tmpout
#	tail -100 ~/cingServer.log  >>& $tmpout
#end

@ tmpoutsize = 0
if ( ! -z $tmpout ) then
    if ( -e $tmpout ) then
        set tmpoutinfo = (`ls -l $tmpout`)
        @ tmpoutsize = $tmpoutinfo[5]
    endif
endif
set stat_failure = ( $tmpoutsize > $maxtmpoutsize )

if ( ! -e $logfile ) then
    touch $logfile
endif

if ( $stat_failure || ($verbosity != "terse") ) then
    if ( $stat_failure ) then
        set subject = "$script reporting ERROR"     > $tmphead
        gawk '{printf("%s %s\n", strftime(), $0)}' $tmpout >> $logfile
    else
        set subject = "$script reporting SUCCESS"   > $tmphead
    endif
    if ( $verbosity == "nomail" ) then
        cat $tmphead $tmpout
        echo $subject
    else if ( $verbosity != "silent" ) then
                if ( $verbosity == "verbose" ) then
                    cat $tmphead $tmpout $logfile | $mail_exe -s "$subject" $mailto
                    \rm -f $logfile
                else
                    cat $tmphead $tmpout | $mail_exe -s "$subject" $mailto
                endif
            endif
    endif
#    cat $tmphead $tmpout 
endif

# In either case, now that we are done, get rid of the old message
\rm -f $tmpout $tmphead >& /dev/null
