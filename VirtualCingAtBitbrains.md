DOCUMENT IN PROGRESS

### Log in ###
  * Go to: [vcloud](https://vcloud.bitbrains.net/cloud/org/CMBI). I had to use Windows 7/Firefox 3.6.19 (32 bit) for some functionality (opening console) although most everything seems to work fine on OSX/Chrome. A newer version of vcloud is going to support more browsers.

### Add user ###
  * Under Administration.

### Start up ###
  * Goto the tab My Cloud and select vApps.
  * Start the system admin machine called vApp\_SYS. The VM is called Hatch 1 which you  can find under VMs.
  * Do not start the machine set: vApp\_VC\_A. Oops, this is all the vcs. 12 4-core machines.
  * Create a new vApp from catalog. For larger machines Bitbrains has the preference to distribute over the two vDC's they have: TC3 and TC4. This will take several minutes.
  * In properties ensure to have internet connected. Set the network to CMBI external with IP mode DHCP.
  * Start up the new VM.
  * Select the right kernel if GRUB asks for.

### ssh access from cmbi from/to VC ###
  * Read the root password f or the hatch from the properties in the cloud director. Get the public IP from the hatch. This IP can be read from: Administration -> Cloud Resources -> Networks and then from context menu of CMBI External do a Configure Services.
`ssh root@94.143.209.108 `
  * Now log thru to your vc with the regular i account with publically known password ilovevc
`ssh i@192.168.0.113 `
  * Of course the process can be more efficient by first setting up a tunnel:
`ssh -L localhost-bb_vc1:39668:192.168.0.113:22   -XY root@94.143.209.108 `
  * Keep that alive and then logging in directly:
`ssh -p 39668 i@localhost-bb_vc1 `
  * Please note the VC setup is for tcsh so first start a tcsh shell: `tcsh`
  * Get your data into VC by pulling from VC using the same tunnel trick (NB the upper case P):
`scp -P 39668 t.txt i@localhost-bb_vc1:/home/i`