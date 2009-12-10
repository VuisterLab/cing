#!/bin/tcsh -f

# DESCRIPTION: Script that executes cing with given parameters but only after setting up the right shell environment except cwd.
# EXAMPLE RUN: $CINGROOT/scripts/cing/CingWrapper.csh --name 1a4d --initCcpn 1a4d.tgz -v 9 --script doValidateiCing.py

# INITIALIZATION
# Set all parameters in script: cing.csh
# Application: iCing. Basicially needed because it can't run under say jd's user account.


setenv UJ                 /Users/jd
setenv WS                 $UJ/workspace35
setenv CCPNMR_TOP_DIR     $WS/ccpn
setenv CINGROOT           $WS/cing
setenv WATTOSROOT         $WS/wattos
setenv aquaroot           $WS/aquad
setenv procheckroot       $UJ/progs/procheck
# contains a single par file with references to single hard-code path $UJ/progs/molmolM.
# TODO: move this dep into CING.
setenv MOLMOLHOME         $UJ/progs/molmolM

# A home directory is needed for .matplotlib, .ccpn and perhaps others' settings?
setenv HOME               /Library/WebServer/Documents/servlet-cing-home
#setenv HOME               $UJ

# Possible improvement could be to have the debug flag below here be defined from
# the iCing interface.
set verbosityDebug = 1


set script = CingWrapper.csh

##No changes required below this line
###############################################################################

# Requirements below:
limit cputime   24000   # Maximum number of seconds the CPU can spend
                        # on any single process spawned. 100 minutes seems to be top.
                        # Nop, Entry 2vda (Haddock 1,000 aa) was not even halfway with 100 minutes.
limit filesize   500m   # Maximum size of any one file
limit datasize  1000m   # Maximum size of data (including stack)
limit coredumpsize 0    # Maximum size of core dump file
umask 2                 # The files created will be having special permissions.

# PYTHONPATH  will be completely set by cing.csh.
unsetenv PYTHONPATH

# fink or macports
set useFink = 0
if ( $useFink ) then
    source /sw/bin/init.csh
else
    set path = ( /opt/local/bin /opt/local/sbin $path )
endif

if ( $verbosityDebug) then
    echo "DEBUG: Wrap for HOME / user           $HOME / $user"
endif

if ( $verbosityDebug) then
    echo    "DEBUG: Path:                          $PATH"
    echo -n "DEBUG: python:                        "
    which python
endif

if ( $verbosityDebug) then
    echo "DEBUG: Initializing CING from         $CINGROOT"
endif
source $CINGROOT/cing.csh

if ( $verbosityDebug) then
    echo "DEBUG: Initializing CCPN from         $CCPNMR_TOP_DIR"
endif
setenv PYTHONPATH   ${PYTHONPATH}:$CCPNMR_TOP_DIR/python

if ( $verbosityDebug) then
    echo "DEBUG: Initializing Wattos from       $WATTOSROOT"
endif
source $WATTOSROOT/scripts/wsetup

if ( $verbosityDebug) then
    echo "DEBUG: Initializing Aqua from         $aquaroot"
endif
source $aquaroot/aqsetup

if ( $verbosityDebug) then
    echo "DEBUG: Initializing ProcheckNMR from  $procheckroot"
endif
source $procheckroot/setup.scr

if ( $verbosityDebug) then
    echo "DEBUG: Initializing MOLMOL from       $MOLMOLHOME"
endif

if ( ! -e "/Users/jd/progs/molmolM/setup/PdbAtoms" ) then
    echo "ERROR: failed to find dep"
    exit 1
endif

if ( $verbosityDebug) then
    echo "DEBUG: Initializing python from       $PYTHONPATH"
    echo "DEBUG: Using CING arguments:          [$argv]"
    echo "DEBUG: Starting script $script on `date`"
endif

# short notation for $argv or even $argv[*] is $* but let's be verbose.
cing $argv

# Testing...
#python $CINGROOT/python/cing/Libs/test/test_NTMoleculePlot.py
#$MOLMOLHOME/molmol -t -f - < 1brv_1model_molmol_images.mac
#pwd;ls;date

if ( $verbosityDebug) then
    echo "DEBUG: Stopped  script $script on `date`"
endif
