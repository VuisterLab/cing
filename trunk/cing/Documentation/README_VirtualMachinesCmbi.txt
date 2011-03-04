Running VC at CMBI

-*- Use 8 cores per VC
    For this the pae kernel extension allows VC to go to 4 Gb per process without limit like the 3Gb we saw before.
    sudo apt-get update
    sudo apt-cache search kernel | grep -i pae
    sudo apt-get


-*- For VNC ports start at 5900 e.g. VC2 is 5901 if started in sequence.
    Connection string: localhost:5900

Wilmar's notes

There are VC1 thru VC6

log in:
    ssh -XY jurgend@fm.cmbi.ru.nl

start/list/remove
    sudo virsh start VC1
    sudo virsh list
    sudo virsh destroy VC2

Find display number, number = port - 5900
    sudo virsh vncdisplay VC1

Start VNC on fm with display locally.
    vncviewer localhost:5900

After changing VC1 sync to the others with
    sudo /mnt/data/vms/sync_images