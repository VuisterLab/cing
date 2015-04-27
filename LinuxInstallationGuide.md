## Linux version ##

Consider taking the latest Ubuntu release which was 10.04 LTS at the time of writing. The 9.10 series works fine except for [issue 239](https://code.google.com/p/cing/issues/detail?id=239) and the 8.x series has a matplotlib version that is too old. Patching can be done manually of matplotlib but hasn't been tried. JFD tested the 32 and 64 bit version of 9.10 both but we'll show the 64 bit for conciseness.
```
Linux version 2.6.32-22-generic (buildd@yellow) (gcc version 4.4.3 (Ubuntu 4.4.3-4ubuntu5) ) #36-Ubuntu SMP Thu Jun 3 19:31:57 UTC 2010
In the 9.10 series this was:
Linux version 2.6.27-14-server (buildd@rothera) (gcc version 4.3.2 (Ubuntu 4.3.2-1ubuntu12) ) #1 SMP Mon Aug 31 13:57:10 UTC 2009
```

## Install matplotlib ##

Look for version 0.99.1.1 or higher.
This installs the minimum versions of everything.
```
sudo aptitude install python-matplotlib
```

Configure matplotlib by putting the configuration file from the download section:
```
http://cing.googlecode.com/files/matplotlibrc
```
in a directory that might already be created:
```
~/..matplotlib/matplotlibrc
```

## Install other deps ##
```
python-matplotlib
python-dev
cython
ipython (only needed when doing interactive work)
imagemagick
python-scipy

# Optional (but you might have them any way)
gawk
subversion
konsole
tcsh
csh
povray
```

## Configure CING ##

First setup CING proper as described in $CINGROOT/README.txt using a Makefile.

If you don't have access to '/tmp/cing' then configure a local tmp path by doing something like:
```
echo "cingDirTmp             = '/home/jurgen/tmp/cingTmp/'" > $CINGROOT/python/cing/localConstants.py
```

## Test installation ##
```
cing --test -v 0
```
or when you need the highest debug verbosity use 9 instead of 0. Normal is 3.

## Problems with dependencies ##
If you have these it might be nice to check the installation without them. If you want to temporarily disable them then do something like:
```
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

setenv PYTHONPATH $CINGROOT/python:${CYTHON}                 
                  
unsetenv CLASSPATH
```

For more permanent changes adjust the generated $CINGROOT/cing.csh

From here you should follow the generalized [SetupCING](SetupCING.md)