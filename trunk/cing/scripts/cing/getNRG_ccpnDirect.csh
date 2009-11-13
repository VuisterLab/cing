#!/bin/csh -f
# Author: Jurgen F. Doreleijers
# $CINGROOT/scripts/cing/getNRG_ccpnDirect.csh

# You should CHANGE THE NEXT THREE LINES to suit your local setup
set MIRRORDIR=/Library/WebServer/Documents/NRG-CING/recoordSync        # your top level rsync directory needs to exist

# For local copy use e.g.:
# \cp -f $ccpn_tmp_dir/data/recoord/$x/$x.tgz $MIRRORDIR/$x/$x.tgz
###################################################################

## No changes below except user id and specific word such as azvv.
set SERVER=jurgen@tang.bmrb.wisc.edu:/raid/docr/ccpn_tmp/data/recoord/         # remote server name; trailing slash is important

# status on the final grep will be zero when it did grep something.
ps -ww | grep "$0" | grep -v grep | grep -v $$
if ( ! $status ) then
    echo "Stopping this job for another hasn't finished; see above list"
    exit 0
endif

rsync -av -f '+ */1brv.tgz' -f '- */*' \
    --delete --stats --progress  \
    $SERVER $MIRRORDIR

echo "Finished"
