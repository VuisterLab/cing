# These archive ids will be used to switch beteen the different setups/rdbs/projects. E.g. look at the use of nrgCing.archive_id
# Use the below map from archive to schema for switching.
from cing.NRG.settings import results_base
from cing.NRG.settings import results_base_recoord
from cing.NRG.settings import results_base_redo

ARCHIVE_NRG_ID      =  'ARCHIVE_NRG'
ARCHIVE_DEV_NRG_ID  =  'ARCHIVE_DEV_NRG'
ARCHIVE_CASD_ID     =  'ARCHIVE_CASD'
ARCHIVE_CASP_ID     =  'ARCHIVE_CASP'
ARCHIVE_PDB_ID      =  'ARCHIVE_PDB'
ARCHIVE_NMR_REDO_ID =  'ARCHIVE_NMR_REDO'
ARCHIVE_NMR_REDOA_ID=  'ARCHIVE_NMR_REDOA'
ARCHIVE_RECOORD_ID  =  'ARCHIVE_RECOORD'
ARCHIVE_RECOORDA_ID =  'ARCHIVE_RECOORDA'

CASD_DB_USER_NAME = 'casdcing1'
CASD_DB_NAME = 'casdcing'

CASP_DB_USER_NAME = 'caspcing1'
CASP_DB_NAME = 'caspcing'

NRG_DB_USER_NAME = 'nrgcing1'
NRG_DB_NAME = 'nrgcing'
NRG_DB_SCHEMA = NRG_DB_NAME

NMR_REDO_DB_USER_NAME = 'nmr_redo1'
NMR_REDO_DB_NAME = 'nmr_redo'
NMR_REDO_DB_SCHEMA = NMR_REDO_DB_NAME

NMR_REDOA_DB_USER_NAME = 'nmr_redoa1'    # the annealed version.
NMR_REDOA_DB_NAME = 'nmr_redoa'
NMR_REDOA_DB_SCHEMA = NMR_REDO_DB_NAME

RECOORD_DB_USER_NAME = 'recoord1'
RECOORD_DB_NAME = 'recoord'
RECOORD_DB_SCHEMA = RECOORD_DB_NAME

RECOORDA_DB_USER_NAME = 'recoorda1' # the annealed version.
RECOORDA_DB_NAME = 'recoorda'
RECOORDA_DB_SCHEMA = RECOORDA_DB_NAME

DEV_NRG_DB_USER_NAME = 'devnrgcing1'
DEV_NRG_DB_NAME = 'devnrgcing'
DEV_NRG_DB_SCHEMA = DEV_NRG_DB_NAME

PDB_DB_USER_NAME = 'pdbcing1'
PDB_DB_NAME = 'pdbcing'

PDBJ_DB_USER_NAME = 'pdbj'
PDBJ_DB_NAME = 'pdbmlplus'
PDBJ_DB_HOST = 'localhost'
PDBJ_DB_SCHEMA = PDBJ_DB_USER_NAME

CASD_NMR_BASE_NAME = 'CASD-NMR-CING'
inputDirCASD_NMR = 'file:///Users/jd/%s/data' + CASD_NMR_BASE_NAME

CASP_NMR_BASE_NAME = 'CASP-NMR-CING'
inputDirCASP_NMR = 'file:///Users/jd/%s/data' + CASP_NMR_BASE_NAME

SCHEMA_ID_ALL_STR = 'SCHEMA_ID_ALL' # Used as a wild card for all below ids.
schemaIdList  = [ CASD_DB_NAME,    PDB_DB_NAME,    NRG_DB_NAME,    DEV_NRG_DB_SCHEMA,    CASP_DB_NAME,    
                 NMR_REDO_DB_SCHEMA,    NMR_REDOA_DB_SCHEMA,    RECOORD_DB_SCHEMA, RECOORDA_DB_SCHEMA   ]
archiveIdList = [ ARCHIVE_CASD_ID, ARCHIVE_PDB_ID, ARCHIVE_NRG_ID, ARCHIVE_DEV_NRG_ID,   ARCHIVE_CASP_ID, 
                 ARCHIVE_NMR_REDO_ID,   ARCHIVE_NMR_REDOA_ID,   ARCHIVE_RECOORD_ID, ARCHIVE_RECOORDA_ID   ]

archiveIdPdbBased = archiveIdList[:] # Requires PDB ID can be derived.

mapArchive2Schema = {}
for _idxArchiveId,archive_id in enumerate( archiveIdList ):
    mapArchive2Schema[ archive_id ] = schemaIdList[_idxArchiveId]
# end for
mapBase2Archive = {}
mapBase2Archive[ results_base ]         = ARCHIVE_NRG_ID
mapBase2Archive[ results_base_recoord ] = ARCHIVE_RECOORD_ID
mapBase2Archive[ results_base_redo ]    = ARCHIVE_NMR_REDO_ID
mapArchive2Base = {}
mapArchive2Base[ ARCHIVE_NRG_ID         ] = results_base
mapArchive2Base[ ARCHIVE_RECOORD_ID     ] = results_base_recoord
mapArchive2Base[ ARCHIVE_NMR_REDO_ID    ] = results_base_redo
