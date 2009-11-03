from cing import cingDirData
#from pprint import pprint
import cPickle
import os

WHATIF_STR       = "Whatif" # key to the entities (atoms, residues, etc under which the results will be stored

CHECK_ID_STR     = "checkID"
LOC_ID_STR       = "locID"
LEVEL_STR        = "level"
TEXT_STR         = "text"
TYPE_STR         = "type"
VALUE_LIST_STR   = "valueList"
QUAL_LIST_STR    = "qualList"

INOCHK_STR       = 'INOCHK'
BNDCHK_STR       = 'BNDCHK'
ANGCHK_STR       = 'ANGCHK'
OMECHK_STR       = 'OMECHK'
HNDCHK_STR       = 'HNDCHK'
INOCHK_STR       = 'INOCHK'

QUACHK_STR       = 'QUACHK'
RAMCHK_STR       = 'RAMCHK'
C12CHK_STR       = 'C12CHK'
BBCCHK_STR       = 'BBCCHK'
ROTCHK_STR       = 'ROTCHK'

NQACHK_STR       = 'NQACHK'
PLNCHK_STR       = 'PLNCHK'
PL2CHK_STR       = 'PL2CHK'
PL3CHK_STR       = 'PL3CHK'

CHICHK_STR       = 'CHICHK'
FLPCHK_STR       = 'FLPCHK'
ACCLST_STR       = 'ACCLST'
BMPCHK_STR       = 'BMPCHK'

if True:
    dbase_file_abs_name =  os.path.join( cingDirData, 'PluginCode', 'WhatIf', 'phipsi_wi_db.dat' )
    #dbaseTemp = shelve.open( dbase_file_abs_name )
    dbase_file = open(dbase_file_abs_name, 'rb') # read binary
    dbaseTemp = cPickle.load(dbase_file)
#    pprint.pprint(dbaseTemp)
    histRamaCombined                = dbaseTemp[ 'histRamaCombined' ]
    histRamaBySsAndResType          = dbaseTemp[ 'histRamaBySsAndResType' ]
    histRamaBySsAndCombinedResType  = dbaseTemp[ 'histRamaBySsAndCombinedResType' ]
#    pprint(histRamaCombined)
    dbase_file.close()
    #dbaseTemp.close()

    dbase_file_abs_name = os.path.join( cingDirData, 'PluginCode', 'WhatIf', 'chi1chi2_wi_db.dat' )
    dbase_file = open(dbase_file_abs_name, 'rb') # read binary
    dbaseTemp = cPickle.load(dbase_file)
    histJaninBySsAndResType         = dbaseTemp[ 'histJaninBySsAndResType' ]
    histJaninBySsAndCombinedResType = dbaseTemp[ 'histJaninBySsAndCombinedResType' ]
    dbase_file.close()

# Disable when debugged:
if False:
    histRamaCombined         = None
    histRamaBySsAndResType = None
    histRamaBySsAndCombinedResType = None
    histJaninBySsAndResType         = None
    histJaninBySsAndCombinedResType = None


wiPlotList = []
# GV: moved to outer level to not always call createHtmlWhatif
wiPlotList.append( ('_01_backbone_chi','QUA/RAM/BBC/C12') )
wiPlotList.append( ('_02_bond_angle','BND/ANG/NQA/PLNCHK') )
wiPlotList.append( ('_03_steric_acc_flip','BMP/ACC/FLP/CHI') )

#WI_SUMMARY_STR = 'wiSummary'
