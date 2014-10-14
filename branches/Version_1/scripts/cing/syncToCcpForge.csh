#!/bin/tcsh -f

############################################################################
#
# Script for updating slaved mirror on CCPForge
#
############################################################################


set MIRRORDIR=$pdbbase_dir                         # your top level rsync directory

# You should NOT CHANGE THE NEXT TWO LINES
set SERVER=http://ccpforge.cse.rl.ac.uk/svn/extend-nmr/
set USER_ID=jurgenfd
set PASSWORD_FILE=~/Private/passwordFiles/passwordFileCcpForge.txt


UNTESTED UNFINISHED
# CING source code with extensive test data sets take ~300 Mb. 
# We should probably create a version without the large test data later. Or is upsetting us?
# Which reminds me where do you want the whatcheck mac install? It's 1.2 Gb compiled with databases.

cd cing

# I expect the current svn info might clobber.

find . -name ".svn" -ok rm {} \;

svn import -m "new import CING" cing/ http://ccpforge.cse.rl.ac.uk/svn/extend-nmr/cing/trunk



rsync -rlpt -z --delete --port=$PORT \
    --password-file=$PASSWORD_FILE \
    $USER_ID@$SERVER/data/structures/divided/mmCIF/$ch23/$x.cif.gz \
    $subdirLoc/$x.cif.gz

echo "Done with syncing "
exit 0


#rsync -rlpt -z --delete --port=$PORT \
    --password-file=$PASSWORD_FILE \
    $USER_ID@$SERVER/data/structures/divided/mmCIF/$ch23/$x.cif.gz \
    $subdirLoc/$x.cif.gz
