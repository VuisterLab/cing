#!/bin/tcsh -f
# Used by Jenkins to build and test CING installation automatically on various platforms. 
# Important not to use shell setup from user; hence the above -f option.

cd $0:h

# Unset inherited environment  
unsetenv PYTHONPATH
unsetenv CYTHON
unsetenv PYMOL_PATH
unsetenv YASARA_PATH
unsetenv CING_VARS

echo "PATH       1: $PATH"
#echo "PYTHONPATH 1: $PYTHONPATH"
#echo "CINGROOT   1: $CINGROOT"

# Note that Jenkins is checking out a couple of levels extra.
#cd $CINGROOT

make -j -f Makefile install
echo "PATH       2  : $PATH"

source cing.csh
make -j -f Makefile build_cython
echo "PATH       3  : $PATH"
echo "PYTHONPATH 3  : $PYTHONPATH"


echo "PATH 4        : $PATH"
echo "PYTHONPATH 4  : $PYTHONPATH"

make -j -f Makefile test
if ( $status ) then
    echo "Failed test"
    exit 1
endif
echo "Done"
