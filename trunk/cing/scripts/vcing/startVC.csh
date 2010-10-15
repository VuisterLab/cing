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

set date_string = (`date "+%Y-%m-%d_%H-%M-%S"`) # gives only seconds.
set epoch_string = (`java Wattos.Utils.Programs.GetEpochTime`)
set time_string = $date_string"_"$epoch_string
echo "Startup script for VC at: $time_string"

set isProduction = 0 # causes sleep and no svn update.

if ( $isProduction ) then
    sleep 600
else
    if ( $doSvnUpdate ) then
        cd $CINGROOT
        svn update .
    endif
endif


# TEST routines
if ( $doTest ) then
    cd
    cd tmp/cingTmp
    echo "First ls"
    ls -al >& ls.log
    touch abcdef
    echo "Second ls"
    ls -al >& ls2.log
    tar -cvzf ls2_$time_string.tgz ls2.log
    scp ls2_$time_string.tgz $TARGET_SDIR
endif

if ( $doRun ) then
    python -u $CINGROOT/python/cing/Scripts/vCing/vCingSlave.py >& vCingSlave_$time_string.log
    scp vCingSlave_$time_string.log $TARGET_SDIR
endif

set date_string = (`date "+%Y-%m-%d_%H-%M-%S"`) # gives only seconds.
set epoch_string = (`java Wattos.Utils.Programs.GetEpochTime`)
set time_string = $date_string"_"$epoch_string
echo "DONE at:                  $time_string"

#shutdown -h now NOT NEEDED BUT ALSO FAILS BECAUSE REQUIRES PASSWORD.