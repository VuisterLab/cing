#!/bin/tcsh
# Run as: $C/scripts/vcing/publishVClocalConstants.csh

echo "Starting $C/scripts/vcing/publishVClocalConstants.csh"
#set slaveM = "vc"
set slaveM = "145.100.57.240"
echo "slaveM: $slaveM"

# master
if ( 0 ) then
    scp $C/python/cing/Scripts/vCing/localConstants.py i@nmr.cmbi.ru.nl:/home/i/workspace/cingStable/python/cing/Scripts/vCing/
    scp $C/scripts/vcing/localConstants.csh            i@nmr.cmbi.ru.nl:/home/i/workspace/cingStable/scripts/vcing/
endif

# slave
if ( 1 ) then
#    scp $C/scripts/tcsh/shootall                       "i@$slaveM":"/home/i/workspace/cing/scripts/tcsh/"
    scp $C/python/cing/Scripts/vCing/localConstants.py "i@$slaveM":"/home/i/workspace/cing/python/cing/Scripts/vCing/"
    scp $C/scripts/vcing/localConstants.csh            "i@$slaveM":"/home/i/workspace/cing/scripts/vcing/"
    scp $C/scripts/vcing/startVC.csh                   "i@$slaveM":"/home/i/workspace/cing/scripts/vcing/"
    scp $C/scripts/vcing/VCheadless                    "i@$slaveM":"/home/i/workspace/cing/scripts/vcing/"
    scp $C/scripts/vcing/topos/topos                   "i@$slaveM":"/home/i/workspace/cing/scripts/vcing/topos/"
    scp $C/python/cing/Scripts/vCing/vCing.py          "i@$slaveM":"/home/i/workspace/cing/python/cing/Scripts/vCing/"
endif