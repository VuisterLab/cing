#!/bin/tcsh
# Author: Jurgen F. Doreleijers
# $CINGROOT/scripts/vcing/syncVCcode.csh
# Should be run from other script that will deal with this output.
# NB do not run this code on machines other than VC.


###################################################################
# Requirements below:
###################################################################

#limit cputime      6    # Maximum number of seconds the CPU can spend (10 minutes). Fails because hanging processes aren't on the cpu.
limit filesize   500m   # Maximum size of any one file
limit datasize  1000m   # Maximum size of data (including stack)
limit coredumpsize 0    # Maximum size of core dump file

#set date_string = (`date | sed -e 's/ /_/g'`)
set date_string = (`date "+%Y_%m_%d-%H_%M_%S"`)

set prog_string = $0:t:r
set log_file    = $prog_string"_$date_string".log

if ( -e $log_file ) then
    echo "ERROR: failed $prog_string because log file already exists: $log_file"
    exit 1
endif

# For vCloud the machines will be numbered but still start with the vc prefix
set hostStart = ( `echo $HOST | gawk '{print tolower($0)}' | cut -c1-2` ) 
if ( $hostStart != 'vc' ) then
    echo "ERROR: tried to run $prog_string on a non VC machine: $HOST"
    echo "ERROR: this is not recommended since it might do svn/cvs updates"
    echo "DEBUG: The host string should have started with vc regardless of capitablization but was found to be: $hostStart"
    exit 1
endif

if ( -e $CINGROOT ) then
    cd $CINGROOT
    echo "Doing CING svn update." | & tee -a $log_file
    svn --force --non-interactive --accept theirs-full update . | & tee -a $log_file
endif

if ( -e $CCPNMR_TOP_DIR ) then
    cd $CCPNMR_TOP_DIR
    echo "Doing CCPN csv update." | & tee -a $log_file
    # ignore the unknown files existing only locally.
    cvs -q -z3 -d:pserver:anonymous@ccpn.cvs.sourceforge.net:/cvsroot/ccpn update -r stable | grep -v '^?' | & tee -a $log_file
endif

if ( -e $WATTOSROOT ) then
    cd $WATTOSROOT
    echo "Doing Wattos svn update." | & tee -a $log_file
    svn --force --non-interactive --accept theirs-full update . | & tee -a $log_file
endif

echo "Finished"