#!/bin/csh -f
# Author: Jurgen F. Doreleijers
# $CINGROOT/scripts/cing/getNRG_ccpn.csh

# You should CHANGE THE NEXT THREE LINES to suit your local setup
set MIRRORDIR=/Library/WebServer/Documents/NRG-CING/recoordSync        # your top level rsync directory needs to exist

# For local copy use e.g.:
# \cp -f $ccpn_tmp_dir/data/recoord/$x/$x.tgz $MIRRORDIR/$x/$x.tgz
###################################################################

## No changes below except user id and specific word such as azvv.
set SERVER=grunt.bmrb.wisc.edu:/raid/docr/ccpn_tmp/data/recoord/         # remote server name; trailing slash is important

#set SERVER=grunt.bmrb.wisc.edu:/raid/mr_anno_progress/

# status on the final grep will be zero when it did grep something.
ps -elf | grep rsync | grep -v grep
if ( ! $status ) then
    echo "Stopping this cron job for another rsync hasn't finished; see above list"
    exit 0
endif

rsync -av -f '+ */1brv.tgz' -f '- */*' \
    --delete --stats --progress  \
    -e "ssh jurgen@tang.bmrb.wisc.edu ssh" \
    $SERVER $MIRRORDIR

echo "Finished"
