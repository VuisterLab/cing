# Use as:

# source $CINGROOT/unsetEnv.csh

# to test the cing installation without external deps

# test with doing:
# echo $PYTHONPATH
# etc.
# Then do:
# cing --test -v 0

unsetenv  xplorPath
unsetenv  procheckPath
unsetenv  aqpcPath   
unsetenv  whatifPath 
unsetenv  dsspPath   
unsetenv  molmolPath
unsetenv  povrayPath

unsetenv  convertPath
unsetenv  ghostscriptPath 
unsetenv  ps2pdfPath
                  
unsetenv CLASSPATH
setenv PYTHONPATH $CINGROOT/python:${CYTHON}                 