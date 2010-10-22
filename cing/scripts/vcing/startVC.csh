#!/bin/tcsh
# Add to startup scripts:
# $CINGROOT/scripts/vcing/startVC.csh

# Author: Jurgen F. Doreleijers
# Thu Oct 14 23:56:36 CEST 2010

source $0:h/settings.csh

set doSvnUpdate = 0
set doTest      = 0
set doRun       = 1

##No changes required below this line
###############################################################################

# Requirements below (kept in sync manually with nrgCing.csh etc.)
#limit cputime   176000  # Maximum number of seconds the CPU can spend; needed to be upped for 2ku1 which took over 8 hrs clocktime. 24 hrs.
limit filesize   500m   # Maximum size of any one file
#limit datasize  1000m   # Maximum size of data (including stack)
limit coredumpsize 0    # Maximum size of core dump file
umask 2                 # The files created will be having special permissions.
set initialSleep = 60

set date_string = (`date "+%Y-%m-%d_%H-%M-%S"`) # gives only seconds.
set epoch_string = (`java Wattos.Utils.Programs.GetEpochTime`)
set time_string = $date_string"_"$epoch_string
set log_file = "startVC_$time_string.log"
set tmp_dir = mktemp -d -t $0
cd $tmp_dir

echo "Startup script for VC at: $time_string on host: $HOST" >& $log_file
echo "what?"
cat $log_file
# update log file on target of course this bits itself but it seems to be fine.
scp -q $TARGET_PORT $log_file $TARGET_SDIR

if ( $isProduction ) then
    echo "Sleeping for $initialSleep seconds so system can come up with network etc." >>& $log_file
    sleep $initialSleep # give 2 minutes for getting systems up. If the machine autoshuts this might have to be longer.
else
    if ( $doSvnUpdate ) then
        cd $CINGROOT
        svn update . >>& $log_file
    endif
endif


# TEST routines
if ( $doTest ) then
    echo "First ls" >>& $log_file
    ls -al >& ls.log
    touch abcdef
    echo "Second ls" >>& $log_file
    ls -al >& ls2.log
    tar -cvzf ls2_$time_string.tgz ls2.log >>& $log_file
    scp $TARGET_PORT ls2_$time_string.tgz $TARGET_SDIR >>& $log_file
    scp -q $TARGET_PORT $log_file $TARGET_SDIR
endif

if ( $doRun ) then
    $CINGROOT/python/cing/Scripts/vCing/vCingSlave.py runSlave >>& $log_file
    # update log file on target
    scp -q $TARGET_PORT $log_file $TARGET_SDIR
endif

set date_string = (`date "+%Y-%m-%d_%H-%M-%S"`) # gives only seconds.
set epoch_string = (`java Wattos.Utils.Programs.GetEpochTime`)
set time_string = $date_string"_"$epoch_string
echo "DONE at:                  $time_string"  >>& $log_file
scp -q $TARGET_PORT $log_file $TARGET_SDIR

#shutdown -h now NOT NEEDED BUT ALSO FAILS BECAUSE REQUIRES PASSWORD.