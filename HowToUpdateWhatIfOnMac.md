## Obsolete info below ##
Best to ask for copy from authors. Then update the paths in:
DO\_WHATIF.COM WHATIF.FIG for the main installation dir.

**Never do 'make all' it will screw up good files.**

## Check out ##

Add username to service by asking Maarten H.
```
svn co https://svn.cmbi.ru.nl/whatif/trunk/ whatif
```

## Update ##

**Cd to whatif dir and issue repeatedly:
```
svn update .
```
Note all conflicts and remove the conflicting files and iterate.... There must be a svn command line option for overriding this like there is in the GUI version in my Eclipse.**

  * Make sure the dummy-2.f is still present in src. It's available in this project's Downloads section. Add it to Makefile like this:
```
 walsrt.o walser.o masmp2.o whatis.o dummy-2.o
```
If you don't then you'll get a million compiler warnings about missing atomic blabla.

  * Remove the MESSAGE files in ./src and cleanup all revisions just to be anal.
```
rm MESSA*
rm ./dbdata/PARAMS.FIG.r6084 ./dbdata/PARAMS.FIG.r6684 ./dbdata/RAMA.LIN.r6084 ./dbdata/RAMA.LIN.r6684
```
etc... Or use 'find'.

  * DSSP failed to compile after doing a make all. Solution, get copy from CMBI. And remove it from Makefile#all target.
  * The getline compiles but gives a lot of noises so it must be bad. Get one from CMBI.
  * Note that the whatif/dbdata/RENATM.DAT file is currently missing from svn; get it from this project's Downloads.
  * Adjust the files: DO\_WHATIF.COM WHATIF.FIG for the main installation dir.

## Dependencies ##

### Install gfortran using MacPorts ###
  * Run .dmg installer from MacPorts web site.
```
port selfupdate
port install gcc42
```
After the last command you need to take a several hour break!

  * Put the What If Makefile from this projects download section in the whatif/src directory. It's specific to Mac in that different compiler options have been set. It is NOT included in the distribution as Makefile.mac. Between revisions there are changes to this Makefile; most importantly to the list of source files. It worked for [revision 6685](https://code.google.com/p/cing/source/detail?r=6685).

  * Change working directory to src and ype:
```
make
```

# Alternatively #
Perhaps the following also works but I haven't been able to wait for the long time it takes to compile:
```
fink selfupdate
fink install gfortran-shlibs (untested)
```