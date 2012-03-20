#!/bin/tcsh
#
#  A simple script to run the webchatpp perl program and check the result.
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
# Put into crontab like:
#01          0 * * fri   /Users/jd/workspace35/cing/scripts/webchatpp/servers_check_wrapper.csh verbose
#*/12        * * * *     /Users/jd/workspace35/cing/scripts/webchatpp/servers_check_wrapper.csh silent

# Executables, might need full-path depending on the environs:
set mail_exe = mail
set perl_exe = perl
set webchat_exe = /opt/local/bin/webchatpp
set webchat_dir = /Users/jd/workspace35/webchatpp/servers_check

setenv cingScriptDir $0:h
if ( -e $cingScriptDir/localConstants.csh ) then
    source $cingScriptDir/localConstants.csh
endif

set verbosity = "$1"
## maximum number of bytes when all is successful
set maxtmpoutsize = 400

# Whom to send the report to when it is done:
#set mailto = jurgen@bmrb.wisc.edu
set mailto = jurgenfd@gmail.com

# Where to put the report for a bit before it gets mailed:
set tmpdir = /tmp
set logfile = $tmpdir/servers_check_wrap.log

# regexp to match spurious error messages we want to throw away:
#set grepout_irrelevant = "^Checking"


#No admin changes below this line (I hope): - - - - - -
###################################################################

# tmp file has PID encoded inside to ensure uniqueness
# during the run:
set tmpout=$tmpdir/servers_check_$$.txt
set tmphead=$tmpdir/servers_check_head_$$.txt
set tmpfoot=$tmpdir/servers_check_foot_$$.txt
set tmpscript=$tmpdir/servers_check_script_$$.txt
set tmpperl=$tmpdir/servers_check_perl_$$.txt

# This command will produce no output when everything works fine:
    # This is one long piped command:
    cat  \
        $webchat_dir/cing_check.wcpl    \
        $webchat_dir/dodo_check.wcpl    \
        $webchat_dir/iCing_check.wcpl    \
        $webchat_dir/mrgrid_check.wcpl    \
        $webchat_dir/nmr_cmbi_home_check.wcpl    \
        $webchat_dir/proteins_home_check.wcpl    \
        $webchat_dir/wattos_home_check.wcpl    \
    > $tmpscript
    cat $tmpscript |& $webchat_exe  > $tmpperl
    cat $tmpperl   |& $perl_exe     |& grep -v "Parsing of undecoded UTF-8 will give garbage" >& $tmpout

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
        set subject = "servers_check reporting ERROR"     > $tmphead
        gawk '{printf("%s %s\n", strftime(), $0)}' $tmpout >> $logfile
    else 
        set subject = "servers_check reporting SUCCESS"   > $tmphead
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
\rm -f $tmpscript $tmpperl $tmpout $tmphead $tmpfoot >& /dev/null 
