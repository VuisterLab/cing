# JUST FOR INTERNAL USE FOR NOW, SORRY #

Use case scenario for creating validation reports for NRG-CING at CMBI's cloud

### Order of steps ###
  * Log in to supercomputer at cmbi with X forwarding for remote display.
> > `ssh -XY jurgend@fm.cmbi.ru.nl`
  * Ask Wilmar to install a copy of VC onto it and configure it with memory and number of cores set. Currently we use 8 cores and 16 Gb. Wilmar also creates multiple instances, currently 6.
  * Start up one VC:
> > `sudo virsh start VC1`
  * List any VC:
> > `sudo virsh list`
  * Find display number, number = port - 5900
> > `sudo virsh vncdisplay VC1`
  * Start VNC on fm with display locally. Change the display port according to previous line item.
> > vncviewer localhost:5900
  * Install and reconfigure as required. Then stop VC from within.
  * After changing VC1, sync to the others with
> > `sudo /mnt/data/vms/sync_images`
  * Now multiple VCs can be started and used as described at VirtualCingUsage. They can be used at the same time as the VCs at Sara or any other location for that matter.
  * Destroy (terminate the machine)
> > `sudo virsh destroy VC1`
  * Log into vc from fm by terminal like: ssh i@192.168.122.2 the local ip needs to be obtained from vncviewer or Wilmar...

### Pitfalls happened ###
  * Network gets messed up on VC when OS gets updated by Wilmar. It might run out of connectors (7 max).
  * Firewall preventing network access.