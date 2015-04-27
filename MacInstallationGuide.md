## Mac version ##
Steps taken on duvel.cmbi.ru.nl (4 core MacBook Pro 15-inch, Mid 2010): OSX 10.9.1
8 GB RAM with SSD
Order below can matter.

## Install Mac Ports ##

Start from a clean install from: From http://www.macports.org/. Make sure to uninstall previous installs including a total remove of /Applications/MacPorts if present.

## Turn off spotlight to speed processing up ##
```
sudo launchctl unload  /System/Library/LaunchDaemons/com.apple.metadata.mds.plist
```

## Install mandatory deps ##

### Optionally switch doing [multiple](https://trac.macports.org/wiki/howto/ParallelBuilding) make jobs ###
```
sudo vi /opt/local/etc/macports/macports.conf
```
Set to zero:
buildmakejobs           0

With top you can see the load on the machine increasing from 1 to a max of x cores during subsequent builds.

### Done in 1 minute gawk as a test ###
```
sudo port install gawk
```

### Done in 5 minutes, set python27 selected early on ###
```
sudo port install python27 python_select 
sudo port select --set python python27
```

### Now the matplotlib MONSTER ###
This is going to install gcc so it will take about 1 hour. It used to take 5 hours mostly being stuck on [atlas](http://x4350.blogspot.com/2011/06/building-atlas-on-macports-takes.html).
```
sudo port install py27-matplotlib +tkinter +gtk2
```

Note that I had to force the activation since there were already installs in /Applications/MacPorts. Starting on August 2012 with Lion, python26 failed to compile on objc or something so I switched to python27 everywhere here.

### Done in 10 minutes. Smaller python deps. ###
```
sudo port install py27-curl py27-mysql py27-sqlalchemy py27-psycopg2 py27-scipy py27-ipython
```

### Done in 15 minutes OPTIONAL ###
```
sudo port install pymol xeyes p7zip Pallet py27-readline szip unrar
```

### Jenkins related installs, pretty fast. OPTIONAL ###
```
sudo port install sloccount py27-pylint py27-nose py27-coverage
```
Set the variant to use.
```
port select --set pylint pylint27 
```
Rename to version aspecifics for easy of code maintenance.
```
    cd /opt/local/bin
    sudo ln -s coverage-2.7    coverage
    sudo ln -s nosetests-2.7   nosetests
    #sudo ln -s pylint-2.7      pylint # This one was present already?
```

### More installs for CING (provides convert and ps2pdf) ###
```
sudo port install povray ghostscript ImageMagick
```

From here you should follow the generalized [SetupCING](SetupCING.md)