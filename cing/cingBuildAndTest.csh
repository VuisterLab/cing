#!/bin/tcsh -e
# Run with absolut path e.g.:
#
#        /Users/i/workspace/cing/cingBuildAndTest.csh
#
# Used by Jenkins to build and test CING installation automatically on various platforms. 
# Important to use shell setup from user; hence the above no -f option.

cd $0:h
echo "DEBUG: Now in cwd: $cwd"
echo "DEBUG: PATH       1: $PATH"

# Unset inherited environment
# Alternatively we could use env for this as in:
# env -i PATH=$PATH HOME=$HOME USER=$USER /Users/jd/workspace/xplor-nih-2.27/bin/xplor  
#unsetenv PYTHONPATH
unsetenv CYTHON
unsetenv PYMOL_PATH
unsetenv YASARA_PATH
unsetenv CING_VARS

if ( $?CCPNMR_TOP_DIR ) then
    echo "DEBUG: CCPNMR_TOP_DIR 1: $CCPNMR_TOP_DIR"
else
    echo "DEBUG: CCPNMR_TOP_DIR 1: undefined"
endif

echo "DEBUG: PYTHONPATH 1: $PYTHONPATH"

make -j -f Makefile install
echo "DEBUG: PATH       2  : $PATH"

source cing.csh
make -j -f Makefile build_cython
# echo "DEBUG: PATH       3  : $PATH"
# echo "DEBUG: PYTHONPATH 3  : $PYTHONPATH"
# echo "DEBUG: CINGROOT   3  : $CINGROOT"
setenv

make -j -f Makefile test

# Disabled for now because it will burn too many cycles.
#make -j -f Makefile nose
#if ( $status ) then
#    echo "Failed nose"
#    exit 1
#endif

echo "Done"
