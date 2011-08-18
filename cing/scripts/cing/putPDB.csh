#!/bin/tcsh
# Author: Jurgen F. Doreleijers
# $CINGROOT/scripts/cing/putPDB.csh
#source $0:h/settings.csh

# Loop thru www to nmr.
set SERVER=jurgend@www.cmbi.ru.nl
set CLIENT=jd@nmr.cmbi.umcn.nl
# Trailing slash is important.
#set SOURCEDIR=$pdbbase_dir/data/structures/divided/mmCIF/br/
set SOURCEDIR=$pdbbase_dir/
# top level rsync directory needs to exist. No slash needed.
#set MIRRORDIR=/Users/jd/wattosTestingPlatform/pdb/data/structures/divided/mmCIF/br
set MIRRORDIR=/Users/jd/wattosTestingPlatform/pdb
set LOGFILE=/tmp/putPDB.log

set specificFlagsForThisJob = "rlptv --max-delete=41 --delete --stats --progress"
###################################################################
# status on the final grep will be zero when it did grep something.

echo "Using following from settings.csh and perhaps overwritten in localSettings.csh" 
echo "SOURCEDIR:   $SOURCEDIR"
echo "MIRRORDIR:   $MIRRORDIR"

ps -ww | grep "$0" | grep -v grep | grep -v $$
if ( ! $status ) then
    echo "Stopping this job for another hasn't finished; see above list"
    exit 0
endif

if ( -f $LOGFILE ) then
    \rm -f $LOGFILE
endif

echo "Syncing PDB archive to NMR with putPDB.csh from Sara"

rsync -$specificFlagsForThisJob -e "ssh $SERVER ssh" $SOURCEDIR $CLIENT':'$MIRRORDIR |& tee $LOGFILE

echo "Finished"