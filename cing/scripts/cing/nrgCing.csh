#!/bin/tcsh
# Author: Jurgen F. Doreleijers
# $CINGROOT/scripts/cing/nrgCing.csh

#source /Users/jd/cingStableSetings.csh

###################################################################
# Requirements below:
limit cputime   24000   # Maximum number of seconds the CPU can spend
limit filesize   500m   # Maximum size of any one file
limit datasize  1000m   # Maximum size of data (including stack)
limit coredumpsize 0    # Maximum size of core dump file

# status on the final grep will be zero when it did grep something.
ps -ww | grep "$0" | grep -v grep | grep -v $$
if ( ! $status ) then
    echo "Stopping this job for another hasn't finished; see above list"
    exit 0
endif

echo "Starting nrgCing.csh"

python -u $CINGROOT/python/cing/NRG/nrgCing.py

echo "Finished"