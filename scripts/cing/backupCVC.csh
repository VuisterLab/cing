#!/bin/tcsh
# Author: Jurgen F. Doreleijers
# $CINGROOT/scripts/cing/backupCVC.csh
# Can be run from cron as root.
#
# Sequence of events:
# -1- Shutdown (3 minutes)
# -2- Copy raw file (6)
# -3- Startup (1)
# All events are checked for completion
#
# Takes about 10 minutes total.
# Each exit status has a different cause. Zero is for overall success.
#
set domainId = CVCa
set ntries = 20
set waitTime = 60
set date_string = (`date "+%Y_%m_%d-%H_%M_%S"`)
set vmCvcDirectory = /var/lib/libvirt/images
set statusShutOff = "shut off"
set statusRunning = "running"

echo "Starting backupCVC.csh with [$$] and [$0]"
#echo "DEBUG: starting timer at: "`date`
#echo "DEBUG: domainId         $domainId"
#echo "DEBUG: ntries           $ntries"
#echo "DEBUG: waitTime         $waitTime"
#echo "DEBUG: date_string      $date_string"
#echo "DEBUG: vmCvcDirectory   $vmCvcDirectory"

cd $vmCvcDirectory

echo "Listing all VM raw files (including data) with ls -alsth *.raw"
ls -alsth *.raw
echo "Listing all VMs in preparation for graceful shutdown."
virsh list --all 
echo "Finding our domain"
virsh list --all | grep $domainId
echo "Grepping our domain for being '$statusRunning'."
virsh list --all | grep $domainId | grep "$statusRunning"
if ( ! $status ) then
    echo "Found domain '$statusRunning'."
else
    echo "ERROR: Found domain NOT '$statusRunning'."
    exit 3
endif

echo "Shutting down gracefully our domain: $domainId"
virsh shutdown $domainId

echo "Trying $ntries times every $waitTime seconds to see if shutdown is complete."
@ count = 1
set isShutOff = 0
while ( $count <= $ntries )
    if ( $count < 2 ) then
        echo "Listing our VM while waiting for graceful shutdown."
    endif
    virsh list --all | grep $domainId
#    echo "DEBUG: Grepping our domain for being '$statusShutOff'."
    virsh list --all | grep $domainId | grep "$statusShutOff"
    if ( ! $status ) then
        echo "Found domain '$statusShutOff'."
        set isShutOff = 1
        break    	
    endif
#    echo "DEBUG: Found domain NOT '$statusShutOff' yet, sleeping $waitTime seconds."
    sleep $waitTime
    @ count = $count + 1
end

if ( $isShutOff ) then
    echo "Found domain '$statusShutOff'."
else
    echo "ERROR: failed to shutdown domain."
    echo "Trying again for a gracefull shutdown but if that fails it will be destroyed."
    virsh shutdown $domainId
    echo "Sleeping 10 seconds."
    sleep 10
    echo "Listing all VMs while waiting for graceful shutdown."
    virsh list --all
    echo "Sleeping $waitTime seconds."
    sleep $waitTime
    echo "Presumed the above failed as well and going in for the kill using a destroy."
    virsh destroy $domainId
    echo "Sleeping $waitTime seconds to give the manager time to recover."
    sleep $waitTime
endif

virsh list --all | grep $domainId | grep "$statusShutOff"
if ( ! $status ) then
    echo "Found domain '$statusShutOff'."
else
    echo "ERROR: failed to shutdown/destroy domain completely."
    echo "Please check status and recover manually."
    exit 1
endif

echo "Copying domain raw file"
echo "DEBUG: starting timer at: "`date`
echo "DEBUG: on 2011-12-05 this took 6 minutes"
set dstRaw = $domainId"_"$date_string.raw
cp $domainId.raw $dstRaw
echo "DEBUG: stopping timer at: "`date`

if ( -e $dstRaw ) then
    echo "Copied raw file to: $dstRaw"
    ls -alsth $dstRaw
else
    echo "ERROR: failed to copy raw file to: $dstRaw"
    exit 2
endif
    
echo "Listing all VMs in preparation to start again."
virsh list --all

echo "Restarting: $domainId"
virsh start $domainId
echo "Sleeping $waitTime seconds."
sleep $waitTime

echo "Listing our VMs again (starting domain is listed as running)."
virsh list --all | grep $domainId

echo "Grepping our domain for being '$statusRunning'."
virsh list --all | grep $domainId | grep "$statusRunning"
if ( ! $status ) then
    echo "Found domain '$statusRunning'."
else
    echo "ERROR: Found domain NOT '$statusRunning'."
    exit 4
endif

echo "DEBUG: stopping timer at: "`date`
echo "Finished"
