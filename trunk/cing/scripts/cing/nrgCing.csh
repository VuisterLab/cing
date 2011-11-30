#!/bin/tcsh
# Author: Jurgen F. Doreleijers
# $CINGROOT/scripts/cing/nrgCing.csh
# Should be run from cron without output to cron.
#

if ( -e $UJ/cingStableSetings.csh ) then
    source $UJ/cingStableSetings.csh
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

echo "Trying to begin nrgCing.csh with [$$] and [$0]" |& tee $log_file

# status on the final grep will be zero when it did grep something.
# $$ is the process number of current shell.
# Need to add the x flag to grep to catch the process without having a controlling terminal.
# a flag for all processes including cron's
# ww for extra wide display showing the full command and parameters.
ps axww | grep "$0" | grep -v grep | grep -v $$ >>& $log_file
if ( ! $status ) then
    echo "ERROR: Stopping this job for another hasn't finished; see above list" >>& $log_file
    exit 1
endif

echo "Starting nrgCing.csh with [$$] and [$0]" |& tee $log_file
# TODO: Remove next line when done.
#exit 1

python -u $CINGROOT/python/cing/NRG/nrgCing.py updateWeekly >>& $log_file
if ( $status ) then 
    echo "ERROR: failed nrgCing.csh" |& tee $log_file
endif

echo "Finished" >>& $log_file