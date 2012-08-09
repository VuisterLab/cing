#!/bin/tcsh
# Add to startup scripts (in Ubuntu this is done in the Gnome GUI under 
#   Preferences/Startup Programs which gets put into:
#   ~i/.config/autostart/startVC.csh.desktop
# Alternatively, and prefered we can also go headless see VCheadless
# $CINGROOT/scripts/vcing/startVC.csh

# Author: Jurgen F. Doreleijers
# Thu Oct 14 23:56:36 CEST 2010

source $0:h/settings.csh

set doSvnUpdate = 1
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
set initialSleep = 600 # DEFAULT: 120 # was too slow on Sara.

set date_string = (`date "+%Y-%m-%d_%H-%M-%S"`) # gives only seconds.
# Get a precise date to distinguish between the many logs that different VCs might return to master.
set epoch_string = (`java Wattos.Utils.Programs.GetEpochTime`)
set time_string = $date_string"_"$epoch_string
set log_file = "startVC_$time_string.log"
#set tmp_dir = mktemp -d -t $0
#cd $tmp_dir
cd

# first time write to log do not append.
echo "Startup script version 1.6 for VC at: $date_string on host: $HOST"    |& tee $log_file
echo "DEBUG: the log of this script is in $log_file"                        |& tee -a $log_file
echo "DEBUG: the full log of this script might be in /tmp/startVC.log"      |& tee -a $log_file
#sleep 9999
#exit
if ( $isProduction ) then
    echo "Sleeping for $initialSleep seconds so system can come up with network etc." |& tee -a $log_file
    sleep $initialSleep # give 2 minutes for getting systems up. If the machine autoshuts this might have to be longer.
endif

# update log file on target of course this bites itself but it seems to be fine.
#scp -q $log_file $TARGET_SDIR

if ( $doSvnUpdate ) then
    # When svn updating this file will corrupt my fine little system here by biting it's own tail. Manual step needed.
    echo "DEBUG: running syncVCcode.csh"                                    |& tee -a $log_file
    $CINGROOT/scripts/vcing/syncVCcode.csh                                  |& tee -a $log_file
    cd
endif

# TEST routines
if ( $doTest ) then
    echo "First ls" | & tee -a $log_file
    ls -al >& ls.log
    touch abcdef
    echo "Second ls" | & tee -a $log_file
    ls -al >& ls2.log
    tar -cvzf ls2_$time_string.tgz ls2.log | & tee -a $log_file
    scp $TARGET_PORT ls2_$time_string.tgz $TARGET_SDIR/result/ | & tee -a $log_file
endif

if ( $doRun ) then
    echo "Doing run." | & tee -a $log_file
    $CINGROOT/python/cing/Scripts/vCing/vCing.py runSlave | & tee -a $log_file
    # update log file on target
#    scp -q $TARGET_PORT $log_file $TARGET_SDIR
endif

set date_string = (`date "+%Y-%m-%d_%H-%M-%S"`) # gives only seconds.
set epoch_string = (`java Wattos.Utils.Programs.GetEpochTime`)
set time_string = $date_string"_"$epoch_string
echo "DONE at:                  $time_string"  | & tee -a $log_file

scp -q $TARGET_PORT $log_file $TARGET_SDIR/log/
echo "DEBUG: DONE and this message will not show up anywhere I'm afraid."