#!/bin/csh -f
# Author: Jurgen F. Doreleijers
# $CINGROOT/scripts/cing/putNRG_ccpn.csh

set SERVER=jurgend@www.cmbi.ru.nl
set CLIENT=jd@nmr.cmbi.umcn.nl
# trailing slash is important.
set SOURCEDIR=/grunt/raid/docr/ccpn_tmp/data/recoord/
# your top level rsync directory needs to exist
set MIRRORDIR=/Library/WebServer/Documents/NRG-CING/recoordSync

###################################################################

## No changes below except user id and specific word such as azvv.

# status on the final grep will be zero when it did grep something.
ps -ww | grep "$0" | grep -v grep | grep -v $$
if ( ! $status ) then
    echo "Stopping this job for another hasn't finished; see above list"
    exit 0
endif

# leaving out options of verbosity so I get a smaller email.
# --progress -v

rsync --archive --filter '+ */*.tgz' -f '- */*' \
    --delete --stats \
    -e "ssh $SERVER ssh" \
    $SOURCEDIR $CLIENT':'$MIRRORDIR

echo "Finished"