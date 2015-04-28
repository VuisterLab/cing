#!/bin/csh -f

#  A simple script to remove temporary data.
#
#  As this is meant to be run by cron, avoid any output to STDOUT or STDERR.
#  else it sends e-mail.  I want to control the e-mail and send it myself:
#
# verbosity argument can be set to:
#   terse   (no output and no logging)
#   silent  (no output but to log file)
#   verbose (output to email even if the check was a success, 
#                including all logged from last verbose run.)
#   nomail  (for direct output of to screen)

# Run from cron as root
# Remove per directory.
set script = iCingRemoveOldFiles

# Executables, might need full-path depending on the environs:
set mail_exe = mail

set verbosity = "$1"

# Whom to send the report to when it is done:
set mailto = jurgenfd@gmail.com

# Find options.
set dirToClean = /Library/WebServer/Documents/tmp/cing
@ maxMinutes = 24 * 60 * 7
#set maxMinutes = 1
# Where to put the report for a bit before it gets mailed:
set tmpdir = /tmp
set logfile = $tmpdir/$script.log

## maximum number of bytes when all is successful
set maxtmpoutsize = 0

#No admin changes below this line (I hope): - - - - - -
###################################################################

# tmp file has PID encoded inside to ensure uniqueness
# during the run:
set tmpout = $tmpdir/"$script"_$$.txt
set tmphead = $tmpdir/"$script"_head_$$.txt

find $dirToClean -mmin +$maxMinutes -type d -mindepth 1 -maxdepth 1 -exec \rm -rf {} \; >& $tmpout
#find $dirToClean -mmin +$maxMinutes -type d -mindepth 1 -maxdepth 1 >& $tmpout

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
