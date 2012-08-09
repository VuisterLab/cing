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
This will give a turn over on 1brv of less than 114 seconds on Duvel with refineEntry.py 

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

# Check settings for Topos pool id.
$C/python/cing/Scripts/vCing/localConstants.py
