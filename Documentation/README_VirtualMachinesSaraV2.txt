To be transfered to http://code.google.com/p/cing/wiki/VirtualCingUsageSaraV2 when ready.
This is file: $C/Documentation/README_VirtualMachinesSaraV2.txt 
Select:

Bus:    Virtio
Model:  Virtio

19 Nodes:
CPU Intel 2.13 GHz 32 cores (Xeon-E7 "Westmere-EX")
RAM 256 Gbyte
"Local disk" 10 Tbyte
Ethernet 4*10GE

On Sara's cloud use ctrl-[ to simulate ctrl-c.

TODO:
-- Check on how to get direct VNC access to VM.
-- Fix VM to internet trafic as ping and ssh from VM fail.
-- Changed passwords for users i and root so they differ from master copy.

DONE:
-- Empty out /etc/resolv.conf
-- follow FAQ at: https://www.cloud.sara.nl/projects/hpc-cloud-documentation/wiki/FAQ
    to adjust a line in /lib/udev/rules.d/75-persistent-net-generator.rules
    and remove          /etc/udev/rules.d/70-persistent-net.rules
-- Empty host name:
   vi /etc/hostname
-- Reset IP:
   vi /etc/network/interfaces
       Remove the address and the gateway lines just leaving four lines:
            # The loopback network interface
            auto lo
            iface lo inet loopback            
            # The primary network interface
            auto eth0
            iface eth0 inet dhcp
-- Stopping NetworkManager
    /etc/init.d/network-manager stop
    stop network-manager.            
    more /etc/resolv.conf # should show sara's dns's.    
-- Remove NetworkManager package (Better to start work with server version of ubuntu; next time.)
    dpkg --list | grep network          
    dpkg --remove network-manager # need to do deps first.          
-- Restart the networking
    /etc/init.d/networking restart
-- Check webserver status by browsing to: http://LVCa/icing/
-- Disable i's crontab
-- Remove the certificate for https protocol from server at 443 port.
-- Remove unwanted services:
    chkconfig -l
    chkconfig --del postgresql    
    chkconfig --del apache2
    chkconfig --del tomcat6
    chkconfig --del firewall
    chkconfig --del rsync
-- ssh in: 
    ssh i@145.100.57.243        
    
    
-- Install x2go; see http://www.x2go.org/doku.php/wiki:x2go-repository-ubuntu
    x2goserver x2goserver-compat x2goserver-xsession x2goserver-fmbindings x2goserver-pyhoca    
    
-- Copy a VM disk image by starting up from a non-persistent copy and use the save as option.
    It will only save on exit. then adjust the template to use the new image.    