# tcsh Queries for analyses done for the CING paper.

[TCSH001]
# For Ramachandran and Janin counts. 
cd $C/python/cing/Scripts/data
# Number of chains: 5135
wc PDB_WI_SELECT_Rfactor0.21_Res2.0_2009-02-28_noObs.LIS
# Number of entries: 4906
cut -c1-4 PDB_WI_SELECT_Rfactor0.21_Res2.0_2009-02-28_noObs.LIS | sort -u | wc
# Number of residues: 1044392
vi $C/data/PluginCode/WhatIf/README.txt



[TCSH002]
# For D1D2 counts.
cd $C/data/PluginCode/WhatIf
# Number of chains: 5133 
gunzip -c cb4ncb4c_wi_db.csv.gz | cut -c1-6 | sort -u |wc
# Number of entries: 4905 
gunzip -c cb4ncb4c_wi_db.csv.gz | cut -c1-4 | sort -u |wc
