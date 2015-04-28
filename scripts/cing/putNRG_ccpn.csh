#!/bin/csh -f
# Author: Jurgen F. Doreleijers
# $CINGROOT/scripts/cing/putNRG_ccpn.csh

#set SERVER=jurgend@www.cmbi.ru.nl
#set CLIENT=jd@nmr.cmbi.umcn.nl
set CLIENT=i@nmr.cmbi.ru.nl
# trailing slash is important.
#set SOURCEDIR=/grunt/raid/docr/ccpn_tmp/data/recoord/
set SOURCEDIR=/raid/docr/ccpn_tmp/data/recoord/
# your top level rsync directory needs to exist
#set MIRRORDIR=/Library/WebServer/Documents/NRG-CING/recoordSync
set MIRRORDIR=/mnt/data/D/NRG-CING/recoordSync

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
rsync -avz -f '+ */*.tgz' -f '- */*' \
    --max-delete=10 --delete --stats $SOURCEDIR \
    -e ssh $CLIENT":"$MIRRORDIR

echo "Finished"
