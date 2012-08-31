Trials with RECOORD entries

Lists on nmr in $D/NRG-CING/list

entry_list_recoord_current.csv          RECOORD entries still in PDB
entry_list_recoord_current.csv          RECOORD entries NRG-CING



Commands:
cd $D/NRG-CING/list
relate $WS/nmrrestrntsgrid/bmrb_pdb_match/results/recoord.csv intersection $D/NRG-CING/entry_list_pdb.csv      entry_list_recoord_current.csv
relate $WS/nmrrestrntsgrid/bmrb_pdb_match/results/recoord.csv intersection $D/NRG-CING/entry_list_nrgcing.csv  entry_list_recoord_nrgcing.csv


# Fast testing:
In $C/python/cing/Scripts/refineEntry.py    set fastestTest
In $C/python/Refine/NTxplor.py              set FAST_FOR_TESTING
This will give a turn over on 1brv in ~50 seconds on Sara with refineEntry.py 

# Test network on Sara VC
ping www.google.com
ssh i@nmr.cmbi.ru.nl
ssh i@131.174.88.36

# 
# Test transfer over ssh to nmr:
$CINGROOT/python/cing/Libs/test/test_network.py

# Test startVC startup/stop:
sudo $C/scripts/vcing/VCheadless stop    
sudo $C/scripts/vcing/VCheadless start

# Check settings for Topos pool id on master & golden slave. 
vi $C/python/cing/Scripts/vCing/localConstants.py

# Clean golden copy of data
cd /home/i/tmp/cingTmp
rm -rfi *

# From here on folow: http://code.google.com/p/cing/wiki/VirtualCingUsage

# Started with old RECOORD set
 534    entry_list_recoord_nrgcing_shuffled.csv
 
 Status R for recognized A for started work X for other S for solved
        E for entry
 Problems
        1aj3 entries not present in nrgcing were apparently not filtered out yet.
        1qbf ligand NH23 uncoded
A       1m94 anneal failed. Got no results back except for the overall log. Implemented a reporting on IP so it can be backtraced.
S       1uxc anneal failed on %CSTRAN-ERR: selection has to contain exactly one atom. Added exception to ignoreLineXplorList


Considering to overcommit processes by a factor of 8.
So a VM of 8 cores has 8 VCprocesses running that each will fork at some point 8 xplor calculations which occupy a single core each.
The load will be a maximum of 64.
Towards the end long running jobs will enjoy full cpu power.
It will not help me finish the first jobs sooner.
VMs with no load at the end can be shot.
Wilmar mentions it might be too much of an overcommit.

