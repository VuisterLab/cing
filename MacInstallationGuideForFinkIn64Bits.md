## Mac Version ##
```
Mac OS X 10.5.7 (9J3050) - Leopard
```

## Mac Hardware ##
```
Macs with Intel Processors Core 2 Duo (64bits)
```

## Intall Fink Bootstraped for x86\_64 ##

Follow the general recommendations at http://www.finkproject.org/download

Open Terminal, choose a folder and:
```
cvs -z3 -d:pserver:anonymous@fink.cvs.sourceforge.net:/cvsroot/fink co -P fink
cd fink; ./bootstrap /sw
# when asked opt for 64bits/x86_64
/sw/bin/pathsetup.sh
```

## Install mandatory deps ##

Start a new Terminal session and:
```
sudo perl -pi.bak -e 's| stable/main | stable/main unstable/main unstable/crypto |g' /sw/etc/fink.conf
fink selfupdate-rsync
fink scanpackages
fink -y selfupdate ; fink update-all; fink cleanup
```

Now let’s install the packages necessaries for CING. Bear in mind that may be a long operation since some packages, if not all, need to be compiled:
```
fink -b install python ipython-py26 python26 # ‘-b’ option means that Fink will try to download a binary version if it exists
fink -b install numpy-py26 molmol povray pymol-py26 matplotlib-py26 pdfsync pil-py26 ghostscript imagemagick
```

To setup CING, you can follow [SetupCING](SetupCING.md), with a difference re cython. You’ll need to do this:

```
cd $CINGROOT/python/cing/Libs/cython
gcc -m64 -fno-strict-aliasing -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes -I/sw/include/python2.6 -c superpose.c -o build/temp.macosx-10.3-i386-2.6/superpose.o
gcc -m64 -L/sw/lib -bundle -L/sw/lib/python2.6/config -lpython2.6 build/temp.macosx-10.3-i386-2.6/superpose.o -o superpose.so
```