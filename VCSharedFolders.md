# Introduction #

Shared folders allow the guest OS (Ubuntu in VirtualCING) to use directories of the host OS. Enabling 'shared folders' in VMware Player is however not enough to properly configure this feature. The installation of Vmware Tools in VC is also required. Follow the steps below and host directories will be visible in /mnt/hgfs/ of VC.

# Details #

Startup VC
  * in VC click Virtual Machine > (RE)install VMware Tools
  * click on the mounted dvd icon on the Desktop.
  * untar the vmware-tools package and cd to the extracted folder
  * run 'sudo ./vmware-config-tools.pl' (sudo password: ilovevc)
  * follow instructions. if neccessary, first install the proper linux headers.
    1. google "ubuntu linux-headers-" + output of 'uname -r' (e.g. 2.6.32-33-generic)
    1. download .deb package for machine type equal to output of 'uname -m'
    1. install package: e.g. 'sudo dpkg -i package.deb'
    1. now rerun 'sudo ./vmware-config-tools.pl'
  * if everything has worked so far, run 'vmware-toolbox &' to start VMware tools
  * add the command /usr/bin/vmware-toolbox to system > preferences > startup applications in VC
  * setup and enable shared folders in your vmplayer/vmware fusion
Shared folders appear in /mnt/hgfs/