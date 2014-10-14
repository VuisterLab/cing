#!/bin/tcsh
# Author: Jurgen F. Doreleijers
# $CINGROOT/scripts/cing/nrgCing.csh
# Should be run from cron without output to cron.
#

if ( -e $UJ/cingStableSettings.csh ) then
    source $UJ/cingStableSettings.csh
endif

###################################################################
# Requirements below:
limit cputime   176000   # Maximum number of seconds the CPU can spend (2 days); needed to be upped for 2ku1 which took 19 hrs clocktime.
limit filesize   500m   # Maximum size of any one file
limit datasize  1000m   # Maximum size of data (including stack)
limit coredumpsize 0    # Maximum size of core dump file

#set date_string = (`date | sed -e 's/ /_/g'`)
set date_string = (`date "+%Y_%m_%d-%H_%M_%S"`)

set prog_string = $0:t:r
#set log_dir     = $tmp_dir/$prog_string
set log_dir     = $D/NRG-CING/log
set log_file    = $log_dir/$prog_string"_$date_string".log

mkdir -p $log_dir

if ( -e $log_file ) then
    echo "ERROR: failed $CINGROOT/scripts/cing/nrgCing.csh because log file already exists: $log_file"
    exit 1
endif

# duplication of code TODO: check
#if ( -e $UJ/cingStableSettings.csh ) then
#    echo "Sourced $UJ/cingStableSettings.csh"                                                   |& tee -a $log_file
#endif

echo "Trying to begin nrgCing.csh with [$$] and [$0]"                                           |& tee -a $log_file

# Status on the final grep will be zero when it did grep something.
# The x flag is to catch processes without having a controlling terminal.
# -a flag for all processes including cron's
# -ww for extra wide display showing the full command and parameters.
# By crontab there is one more process in between. Luckily it is a different parent for each invocation
# and not the (same) crontab process. 
set myProces    = $0:t
set myPid       = $$
set pPid        = `ps o ppid= -p $$`
echo "Checking for running processes given:"                                                    |& tee -a $log_file                                                
echo " myProces         : $myProces"                                                            |& tee -a $log_file    
echo " myPid            : $myPid"                                                               |& tee -a $log_file    
echo " pPid             : $pPid"                                                                |& tee -a $log_file    
#echo "## 2"                                                                                   
#ps axww -o pid,ppid,stat,user,command| grep "$myProces"                                                                    
#echo "## 3"                                                                                   
#ps axww -o pid,ppid,stat,user,command| grep "$myProces" | grep -v grep | grep -v ps                                        
#echo "## 4"                                                                                   
ps axww -o pid,ppid,stat,user,command| grep "$myProces" | grep -v grep | grep -v ps | grep -v $myPid | grep -v $pPid |& tee -a $log_file   
if ( ! $status ) then	                                                                      
    echo "ERROR: Stopping this job for another hasn't finished; see above list"                 |& tee -a $log_file    
    exit 1                                                                                    
endif                                       
#echo "DEBUG: sleeping 9999 before exiting."                                                       
#sleep 9999                                                  
#echo "DEBUG: good stopping any way now"                                                       
#exit 0                                                                                        
#echo "## 5"                                                                                   


echo "Starting nrgCing.csh with [$$] and [$0]"                                                  |& tee -a $log_file
python -u $CINGROOT/python/cing/NRG/nrgCing.py updateWeekly                                     >>& $log_file
if ( $status ) then 
    echo "ERROR: failed nrgCing.csh"                                                            |& tee -a $log_file
endif

echo "Finished"                                                                                 |& tee -a  $log_file