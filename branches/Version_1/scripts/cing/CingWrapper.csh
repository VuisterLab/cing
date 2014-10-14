#!/bin/tcsh -f

# DESCRIPTION: Script that executes cing with given parameters but only after setting up the right shell environment except cwd.
# EXAMPLE RUN: 
# $CINGROOT/scripts/cing/CingWrapper.csh --name 1a4d --initCcpn 1a4d.tgz -v 9 --script doValidateiCing.py
# $C/scripts/cing/CingWrapper.csh -v 9 --noProject --script $C/python/cing/Scripts/doNothing.py

# INITIALIZATION
# Set all parameters in script: cing.csh
# Application: iCing. Basically needed because it can't run under say jd's user account.


setenv UJ                 /local/
setenv WS                 $UJ/workspace
# A home directory is needed for .matplotlib, .ccpn and perhaps others' settings?
# E.g. the below would be appropriate for a tomcat6 user's home. 
setenv HOME               /tmp/servlet-cing-home

setenv cingScriptDir $0:h
if ( -e $cingScriptDir/localConstants.csh ) then
    source $cingScriptDir/localConstants.csh
endif

setenv CCPNMR_TOP_DIR     $WS/ccpn
setenv CINGROOT           $WS/cing
setenv WATTOSROOT         $WS/wattos
setenv aquaroot           $WS/aquad
setenv talosPath          $WS/talosplus/talos+
setenv procheckroot       $WS/procheck
# contains a par file with references to hard-code paths
setenv MOLMOLHOME         $WS/molmol

# Possible improvement could be to have the debug flag below here be defined from
# the iCing interface.
set verbosityDebug = 0

set script = CingWrapper.csh

##No changes required below this line
###############################################################################

# Requirements below (kept in sync manually with nrgCing.csh etc.)
#limit cputime   24000  # Maximum number of seconds the CPU can spend
                        # on any single process spawned. 100 minutes seems to be top.
                        # Nop, Entry 2vda (Haddock 1,000 aa) was not even halfway with 100 minutes.
limit cputime   176000  # Maximum number of seconds the CPU can spend; needed to be upped for 2ku1 which took over 8 hrs clocktime. 24 hrs.

limit filesize   500m   # Maximum size of any one file
limit datasize  1000m   # Maximum size of data (including stack)
limit coredumpsize 0    # Maximum size of core dump file
umask 2                 # The files created will be having special permissions.

# PYTHONPATH  will be completely set by cing.csh.
unsetenv PYTHONPATH

# The  /usr/local/pgsql/bin OR /Users/jd/opt/bin is just for psql dep.
set path = ( \
/opt/local/bin \
/opt/local/sbin \
/usr/local/pgsql/bin \
/Users/jd/opt/bin \
$path )

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
    echo "DEBUG: Initializing Talos+ from       $talosPath"
endif

if ( $verbosityDebug) then
    echo "DEBUG: Initializing MOLMOL from       $MOLMOLHOME"
endif

if ( ! -e "$MOLMOLHOME/setup/PdbAtoms" ) then
    echo "ERROR: failed to find MolMol dep on PdbAtoms"
    exit 1
endif

if ( $verbosityDebug) then
    echo "DEBUG: Initializing python from       $PYTHONPATH"
    echo "DEBUG: Using CING arguments:          [$argv]"
    echo "DEBUG: Starting script $script on `date`"
endif

# short notation for $argv or even $argv[*] is $* but let's be verbose.
cing $argv

if ( $verbosityDebug) then
    echo "DEBUG: Stopped  script $script on `date`"
endif
