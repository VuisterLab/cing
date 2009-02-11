#!/bin/csh -f
# Author: Jurgen F. Doreleijers 
# Put in cron like:
# /Users/jd/workspace34/cing/scripts/cing/getNRG_ccpn.csh

# You should CHANGE THE NEXT THREE LINES to suit your local setup
set MIRRORDIR=/Library/WebServer/Documents/NRG-CING/recoordSync        # your top level rsync directory needs to exist
#set USER_ID = jurgen

###################################################################
## No changes below except user id and specific word such as azvv.
set SERVER=tang.bmrb.wisc.edu:/big/docr/ccpn_tmp/data/recoord/         # remote server name; trailing slash is important

# replace azvv by another specific word if process doesn't start up.
# status on the final grep will be zero when it did grep something.
ps -elf | grep azvv | grep rsync | grep -v grep
if ( ! $status ) then
	echo "Stopping this cron job for another hasn't finished; see above list"
	exit 0
endif

# Watch out for not changing the azvv option below without changing it above.
rsync -azvv \
    -f '+ */*.tgz' -f '- */*' \
    --delete --stats --progress  \
    -e 'ssh -l jurgen' $SERVER $MIRRORDIR

echo "Finished"
