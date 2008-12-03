#!/bin/csh

# DESCRIPTION: Script that executes python script
# EXAMPLE RUN: molgrap.csh

# INITIALIZATION
# Set all parameters in python script: molgrap.py
# Directory with initial data.
#set base_dir        = /share/jurgen/BMRB/Molgrap
set base_dir        = /Users/jd/workspace/Molgrap

##No changes required below this line
###############################################################################
# Very loose requirements below:
limit cputime   60000   # Maximum number of seconds the CPU can spend
                        # on any single process spawned.
limit filesize   500m   # Maximum size of any one file
limit datasize   500m   # Maximum size of data (including stack)
limit coredumpsize 0    # Maximum size of core dump file

echo "Starting script molgrap.csh on `date`"
## Instantiate AQUA 
## Change this in the future to a stable version
## in stead of the developmental version
aquad

umask 2

cd $base_dir

foreach doCESGArchive ( 0 1 )     
    # Do the timed execution
    time python molgrap.py $doCESGArchive
end

echo "Ending script molgrap.csh"
