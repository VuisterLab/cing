#!/bin/tcsh
# Author: Jurgen F. Doreleijers
# $CINGROOT/scripts/cing/pdbCing.csh
# Should be run from cron without output to cron.
#
if ( -e /Users/jd/cingStableSetings.csh ) then
    source /Users/jd/cingStableSetings.csh
endif

###################################################################
# Requirements below:
limit cputime   24000   # Maximum number of seconds the CPU can spend
limit filesize   500m   # Maximum size of any one file
limit datasize  1000m   # Maximum size of data (including stack)
limit coredumpsize 0    # Maximum size of core dump file

#set date_string = (`date | sed -e 's/ /_/g'`)
set date_string = (`date "+%Y_%m_%d-%H_%M_%S"`)

set prog_string = $0:t:r
#set log_dir     = $tmp_dir/$prog_string
set log_dir     = /Library/WebServer/Documents/PDB-CING/log
set log_file    = $log_dir/$prog_string"_$date_string".log

mkdir -p $log_dir

if ( -e $log_file ) then
    echo "ERROR: failed $CINGROOT/scripts/cing/pdbCing.csh because log file already exists: $log_file"
    exit 1
endif

# status on the final grep will be zero when it did grep something.
# $$ is the process number of current shell.
# Need to add the x flag to grep to catch the process without having a controlling terminal.
# a flag for all processes including cron's
# ww for extra wide display showing the full command and parameters.
# ps -axww | grep "$0" | grep -v grep | grep -v $$ >>& $log_file
# if ( ! $status ) then
#     echo "ERROR: Stopping this job for another hasn't finished; see above list" >>& $log_file
#     exit 1
# endif

echo "Starting pdbCing.csh with [$$] and [$0]" >>& $log_file
# TODO: Remove next line when done.
#exit 1

python -u $CINGROOT/python/cing/NRG/pdbCing.py >>& $log_file

echo "Finished" >>& $log_file