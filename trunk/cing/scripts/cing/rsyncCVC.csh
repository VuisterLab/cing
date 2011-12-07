#!/bin/tcsh
# Author: Jurgen F. Doreleijers
# $CINGROOT/scripts/cing/rsyncCVC.csh
# Can be run from cron as root.
#
set domainId        = CVCa
set base_url        = 'jurgenfd@cmbi21.cmbi.ru.nl:/var/lib/libvirt/images/' # NB slash is important.
set target_dir      = /Volumes/tria3/backup/CVC/images

echo "Starting rsyncCVC.csh with [$$] and [$0]"
echo "DEBUG: domainId           $domainId"
echo "DEBUG: base_url           $base_url"
echo "DEBUG: target_dir         $target_dir"

echo "Syncing ALL CVC raw files"
cd $target_dir
rsync -avvvz --stats --include='CVCa**.raw' --exclude='*' -e ssh $base_url .
echo "Done syncing."
