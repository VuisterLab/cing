#!/bin/csh -f
# Author: Jurgen F. Doreleijers
# $CINGROOT/scripts/cing/getNRG_ccpn.csh

echo "Routine fails due to network problems between Madison and Nijmegen"
echo "Use the putNRG_CCPN.csh script instead"
exit 0

# You should CHANGE THE NEXT THREE LINES to suit your local setup
set MIRRORDIR=/Library/WebServer/Documents/NRG-CING/recoordSync        # your top level rsync directory needs to exist

# For local copy use e.g.:
# \cp -f $ccpn_tmp_dir/data/recoord/$x/$x.tgz $MIRRORDIR/$x/$x.tgz
###################################################################

## No changes below except user id and specific word such as azvv.
set SERVER=grunt.bmrb.wisc.edu:/raid/docr/ccpn_tmp/data/recoord/         # remote server name; trailing slash is important

#set SERVER=grunt.bmrb.wisc.edu:/raid/mr_anno_progress/

# status on the final grep will be zero when it did grep something.
ps -ww | grep "$0" | grep -v grep | grep -v $$
if ( ! $status ) then
    echo "Stopping this job for another hasn't finished; see above list"
    exit 0
endif

rsync -av -f '+ */*.tgz' -f '- */*' \
    --delete --stats --progress  \
#    --bwlimit=80 \
    -e "ssh jurgen@lionfish.bmrb.wisc.edu ssh" \
    $SERVER $MIRRORDIR

echo "Finished"
exit 0
