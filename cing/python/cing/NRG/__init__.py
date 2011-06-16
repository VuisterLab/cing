# These archive ids will be used to switch beteen the different setups/rdbs/projects. E.g. look at the use of nrgCing.archive_id
# Use the below map from archive to schema for switching.
ARCHIVE_NRG_ID      =  'ARCHIVE_NRG'
ARCHIVE_DEV_NRG_ID  =  'ARCHIVE_DEV_NRG'
ARCHIVE_CASD_ID     =  'ARCHIVE_CASD'
ARCHIVE_CASP_ID     =  'ARCHIVE_CASP'
ARCHIVE_PDB_ID      =  'ARCHIVE_PDB'
ARCHIVE_NMR_REDO_ID =  'ARCHIVE_NMR_REDO'

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

schemaIdList  = [ CASD_DB_NAME,    PDB_DB_NAME,    NRG_DB_NAME,    DEV_NRG_DB_SCHEMA,    CASP_DB_NAME,    NMR_REDO_DB_SCHEMA    ]
archiveIdList = [ ARCHIVE_CASD_ID, ARCHIVE_PDB_ID, ARCHIVE_NRG_ID, ARCHIVE_DEV_NRG_ID,   ARCHIVE_CASP_ID, ARCHIVE_NMR_REDO_ID   ]

mapArchive2Schema = {}
for i,archiveId in enumerate( archiveIdList ):
    mapArchive2Schema[ archiveId ] = schemaIdList[i]

