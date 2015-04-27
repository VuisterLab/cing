# **JUST FOR INTERNAL USE FOR NOW, SORRY** #

# Introduction #

Installing CING with can be a hassle because it can use a lot of components.
Using VirtualCing (VC) you get all required -and many optional- plugins in one go.

# Installation #

  * Install VMware 3.1 (or later) (VMware Fusion on Mac, or the free VMware Player for Windows or Linux).
Your computer (host) must be pretty high end, specifically your processor must support virtualization of VirtualCing (guest)
  * Ask Geerten or Jurgen for the local download URL. Probably something like http://nmr.cmbi.ru.nl/xxx/yyy/VC.tgz
  * Unzip the archive.
  * Open VC with VMware.
  * In VirtualCing (inside VMware) you will be logged in as super user 'i'. You shouldn't need the password: 'ilovevc'. Yes, you are a super user and it's your machine now!
  * The desktop will contain an open browser to this Wiki for your reference.
  * A terminal program called Konsole is also open. It's icon looks like an old CRT screen showing a greater than sign.
  * If you like to run all of CING's unit tests you can type in that terminal: `cing --test -v 0`. The results are in /home/i/tmp/cingTmp. There is a link to that directory on your desktop. It should now contain all kind of files including images like: test\_NTMoleculePlot.png.
  * It is recommended to store your data on a shared folder on your host OS so that you will not loose it when you loose VC. You can mount the drive using e.g. MacFusion over ssh because in VC a ssh daemon is active.
  * For access inside VC to the host you will need to enable a shared folder in /mnt/hgfs by editing the network settings in VMware for VC. Reboot the VM to activate.
  * In order to update to the latest version of cing type (acknowledge questions with tf i.e. theirs-fully):
```
cd $CINGROOT/
svn update .
```
  * VC can run with as little as 1 Gb but is really happy with 2. Make sure you leave your host OS plenty of memory. Our experience is to run on 2 but preferably 4 Gb. Adjust the memory in the VMware settings for VC.
  * You may want to reset the password from 'ilovevc' to something like 'melovevc' for security reasons. The machine will really be available on your local network so be aware of the usual security issues. Changing the user name is really involved as a lot of customization was done. Adding a user is trivial.

# Batteries included #
  * Ubuntu 9.10 32 bit server with:
    * convert
    * ghostscript
    * ps2pdf
    * povray
  * Python 2.6 with packages:
    * pymol
    * matplotlib
    * cython
  * Optional plugins:
| aqua  | molmol           | wattos  |
|:------|:-----------------|:--------|
| ccpn  | procheck\_nmr     | what if   |
| dssp  | talos            | xplor        |

# To add #
  * pyRoseta (in progress)
  * Mars

# Notes #
  * Have a look at CING's wiki pages LinuxInstallationGuide and VirtualCingTheMakingOf to see the fun you missed ;-)
