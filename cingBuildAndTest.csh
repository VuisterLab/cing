#!/bin/tcsh
# Run with absolut path e.g.:
#
#        $CINGROOT/cingBuildAndTest.csh
#
# Used by Jenkins to build and test CING installation automatically on various platforms. 
# Important to use shell setup from user; hence the above no -f option.
# In OSX Lion a -e option fails the script right away so it's omitted.
 
echo "Starting cingBuildAndTest.csh"

cd $0:h
#ulimit -a -H

if ( ! $?PYTHONPATH ) then
    echo "DEBUG: initializing non-existing PYTHONPATH to ."
    setenv PYTHONPATH .
endif

if ( ! $?CLASSPATH ) then
    echo "DEBUG: initializing non-existing CLASSPATH to ."
    setenv CLASSPATH .
endif

echo "DEBUG: PATH       1: $PATH"
echo "DEBUG: PYTHONPATH 1: $PYTHONPATH"
echo "DEBUG: CLASSPATH  1: $CLASSPATH"

setenv CINGROOT $cwd

# Unset inherited environment
# Alternatively we could use env for this as in:
# env -i PATH=$PATH HOME=$HOME USER=$USER /Users/jd/workspace/xplor-nih-2.27/bin/xplor  
#unsetenv PYTHONPATH
unsetenv CYTHON
unsetenv PYMOL_PATH
unsetenv YASARA_PATH
unsetenv CING_VARS

if ( $?WATTOSROOT ) then
    echo "DEBUG: WATTOSROOT 1: $WATTOSROOT"
else
    echo "DEBUG: WATTOSROOT 1: undefined (optional)"
endif

if ( $?CCPNMR_TOP_DIR ) then
    echo "DEBUG: CCPNMR_TOP_DIR 1: $CCPNMR_TOP_DIR"
else
    echo "DEBUG: CCPNMR_TOP_DIR 1: undefined (optional)"
endif

echo "DEBUG: PYTHONPATH 2: $PYTHONPATH"

make clean
make install
source cing.csh
make cython

echo "DEBUG: PATH       3  : $PATH"
echo "DEBUG: PYTHONPATH 3  : $PYTHONPATH"
echo "DEBUG: CINGROOT   3  : $CINGROOT"
echo
echo

# Comment out the next line after done testing for it's a security issue.
#setenv | sort

echo "Counting Source Lines Of Code."
echo
make sloccount
echo

# Still fails 
echo 
echo 
make pylint
echo

# Still fails on some deps. So listing last in line.
echo "Unit testing with the nose framework"
echo "NB this step might produce some problems that may safely be ignored."
echo "The final test at the bottom is the only test that needs to be succesful."
echo
make nose
echo

echo "Starting cing up and testing for zero status for exit code"
echo
cing --noProject
echo

echo "Full regular cing test that needs to be successful (single core)"
echo
make test
set overallStatus = $status
echo
if ( $overallStatus ) then
    echo "ERROR overall test status from 'make test' failed."
else
    echo "Overall test status: OK"
endif



echo "Done"
