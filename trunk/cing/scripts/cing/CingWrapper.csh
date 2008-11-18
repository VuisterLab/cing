#!/bin/tcsh -f

# DESCRIPTION: Script that executes cing with given parameters but only after setting up the right shell environment except cwd.
# EXAMPLE RUN: /Users/jd/workspace34/cing/scripts/cing/CingWrapper.csh --name 1a4d --initCcpn 1a4d.tgz -v 9 --script doValidateiCing.py

# INITIALIZATION
# Set all parameters in script: cing.csh
# Application: iCing. Basicially needed because it can't run under say jd's user account.


setenv UJ                 /Users/jd
setenv WS                 $UJ/workspace34
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



set script = CingWrapper.csh

##No changes required below this line
###############################################################################
# Requirements below:
limit cputime    6000   # Maximum number of seconds the CPU can spend
                        # on any single process spawned. 100 minutes seems to be top.
limit filesize   500m   # Maximum size of any one file
limit datasize  1000m   # Maximum size of data (including stack)
limit coredumpsize 0    # Maximum size of core dump file
umask 2                 # The files created will be having special permissions.

unsetenv PYTHONPATH

echo "DEBUG: Wrap for HOME / user           $HOME / $user"

echo "DEBUG: Initializing CING from         $CINGROOT"
source $CINGROOT/cing.csh

echo "DEBUG: Initializing CCPN from         $CCPNMR_TOP_DIR"
setenv PYTHONPATH   ${PYTHONPATH}:$CCPNMR_TOP_DIR/python

echo "DEBUG: Initializing Wattos from       $WATTOSROOT"
source $WATTOSROOT/scripts/wsetup

echo "DEBUG: Initializing Aqua from         $aquaroot"
source $aquaroot/aqsetup

echo "DEBUG: Initializing ProcheckNMR from  $procheckroot"
source $procheckroot/setup.scr

echo "DEBUG: Initializing MOLMOL from       $MOLMOLHOME"
if ( ! -e "/Users/jd/progs/molmolM/setup/PdbAtoms" ) then
    echo "ERROR: failed to find dep"
    exit 1
endif

echo "DEBUG: Initializing python from       $PYTHONPATH"

echo "DEBUG: Using CING arguments:          [$argv]"
echo "DEBUG: Starting script $script on `date`"

# short notation for $argv or even $argv[*] is $* but let's be verbose.
cing $argv

# Testing...
#python $CINGROOT/python/cing/Libs/test/test_NTMoleculePlot.py
#$MOLMOLHOME/molmol -t -f - < 1brv_1model_molmol_images.mac


echo "DEBUG: Stopped  script $script on `date`"
