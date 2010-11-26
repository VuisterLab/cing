"""
Nomenclature database constants descriptors:
AQUA         AQUA nomenclature
CNS          CNS nomenclature; amounts to XPLOR
CYANA        CYANA 1.x nomenclature
CYANA2       CYANA 2.x nomenclature
DYANA        DYANA nomenclature; amounts to CYANA
INTERNAL     Current internal nomenclature (INTERNAL_0 or INTERNAL_1)
IUPAC        IUPAC Nomenclature
PDB          Old (PDB2) nomenclature
SPARKY       Sparky nomenclature, amounts to IUPAC
XEASY        Xeasy nomenclature; amounts to CYANA
XPLOR        XPLOR nomenclature

Axes descriptors:
X_AXIS, Y_AXIS, Z_AXIS, A_AXIS
"""
import cing
__version__    = cing.__version__
__date__       = cing.__date__
__author__     = cing.__author__
__copyright__  = cing.__copyright__
__credits__    = cing.__credits__

AQUA       = 'AQUA' # not uptodate with BMRB DG/G difference.
IUPAC      = 'IUPAC'
SPARKY     =  IUPAC
CYANA      = 'CYANA'
XEASY      = CYANA
DYANA      = CYANA
CYANA2     = 'CYANA2'
XPLOR      = 'XPLOR'
CNS        =  XPLOR
PDB        = 'PDB'
INTERNAL_0 = 'INTERNAL_0'   # INTERNAL_0 is the first convention used: was based upon DYANA/CYANA1.x convention (Gly has HA1/2)
INTERNAL_1 = 'INTERNAL_1'   # INTERNAL_1 is the second convention used: IUPAC for IUPAC defined atoms, CYANA2 for non-IUPAC atoms
INTERNAL   = INTERNAL_0

LOOSE      = 'LOOSE'

CCPN       = 'CCPN'
CING       = 'CING'
CING_STR   = CING
# No shift value for Xeasy.
NOSHIFT         =  999.000
NULL_STRING_DOT ='.'
EMPTY_RANGE_STR = NULL_STRING_DOT
CV_RANGE_STR = 'cv'
AUTO_RANGE_STR = 'auto'
ALL_RANGE_STR = 'all'
# PLUGINS
IS_INSTALLED_STR = 'isInstalled'

dots = '-----------'

X_AXIS = 0
Y_AXIS = 1
Z_AXIS = 2
A_AXIS = 3

CYANA_NON_RESIDUES = ['PL','LL2','link']

# Color labels for HTML/CSS output
COLOR_RED    = 'red'
COLOR_GREEN  = 'green'
COLOR_ORANGE = 'orange'

EPSILON_RESTRAINT_VALUE_FLOAT = 1.e-5

# For criteria implementation.
OPERATION_EQUALS                 = '=='
OPERATION_LESS_THAN_OR_EQUALS    = '<='
OPERATION_GREATER_THAN_OR_EQUALS = '>='
OPERATION_LESS_THAN              = '<'
OPERATION_GREATER_THAN           = '>'
OPERATION_IN                     = 'in'
OPERATION_OUT                    = 'out'

ATOM_LEVEL     = 'ATOM'
RES_LEVEL      = 'RESIDUE'
CHAIN_LEVEL    = 'CHAIN'
MOLECULE_LEVEL = 'MOLECULE'
PROJECT_LEVEL  = 'PROJECT'

ATOM_STR = 'atom'
RES_STR = 'res'
CHAIN_STR = 'chain'
MOLECULE_STR = 'molecule'
PROJECT_STR = 'project'
ATOMS_STR = 'atoms'

ANY_ENTITY_LEVEL = 'ANY_ENTITY'

DR_LEVEL       = 'DistanceRestraint'
DRL_LEVEL      = 'DistanceRestraintList'
HBR_LEVEL = 'HBondRestraint' # Alternative for hydrogen bond restraints where in CCPN another name is used.
HBRL_LEVEL = 'HBondRestraintList'
AC_LEVEL = 'DihedralRestraint'
ACL_LEVEL = 'DihedralRestraintList'
RDC_LEVEL = 'RDCRestraint'
RDCL_LEVEL = 'RDCRestraintList'
COPLANAR_LEVEL = 'Coplanar'
COPLANARL_LEVEL = 'CoplanarList'
DIHEDRAL_BY_PROJECT_LEVEL = 'DihedralByProject'
DIHEDRALL_BY_PROJECT_LEVEL = 'DihedralByProjectList' # unused?
DIHEDRAL_BY_RESIDUE_STR = 'DihedralByResidue'

SUMMARY_STR = 'summary'

DATA_STR = 'data' # mostly for NRG.

DR_STR = 'distanceRestraints' # used as in residue.distanceRestraints
AC_STR = 'dihedralRestraints' # used as in residue.dihedralRestraints
VIOL1_STR = 'violCount1'
VIOL3_STR = 'violCount3'
VIOL5_STR = 'violCount5'

# SQL stuff
PDB_ID_STR      = 'pdb_id'
ENTRY_ID_STR    = 'entry_id'
CHAIN_ID_STR    = 'chain_id'
RESIDUE_ID_STR  = 'residue_id'
ATOM_ID_STR     = 'atom_id'
RES_COUNT_STR   = 'res_count'
MODEL_COUNT_STR = 'model_count'
ROG_STR         = 'rog'

OMEGA_DEV_AV_ALL_STR    = 'omega_dev_av_all'
CV_BACKBONE_STR         = 'cv_backbone'
CV_SIDECHAIN_STR        = 'cv_sidechain'
CHK_RAMACH_STR          = 'chk_ramach'
CHK_JANIN_STR           = 'chk_janin'
CHK_D1D2_STR            = 'chk_d1d2'
PHI_AVG_STR             = 'phi_avg'
PSI_AVG_STR             = 'psi_avg'
CHI1_AVG_STR            = 'chi1_avg'
CHI2_AVG_STR            = 'chi2_avg'
PHI_CV_STR              = 'phi_cv'
PSI_CV_STR              = 'psi_cv'
CHI1_CV_STR             = 'chi1_cv'
CHI2_CV_STR             = 'chi2_cv'

DISTANCE_COUNT_STR    = 'distance_count'
DIHEDRAL_COUNT_STR    = 'dihedral_count'
RDC_COUNT_STR         = 'rdc_count'
PEAK_COUNT_STR        = 'peak_count'
CS_COUNT_STR          = 'cs_count'
CS1H_COUNT_STR        = 'cs1H_count'
CS13C_COUNT_STR       = 'cs13C_count'
CS15N_COUNT_STR       = 'cs15N_count'

POOR_PROP = 'POOR'
BAD_PROP  = 'BAD'

CHARS_PER_LINE_OF_PROGRESS = 100

PROTEIN_STR = 'protein'
PHI_STR = 'PHI'
PSI_STR = 'PSI'
CHI1_STR = 'CHI1'
CHI2_STR = 'CHI2'
OMEGA_STR = 'OMEGA'
CV_STR = 'cv'
CAV_STR = 'cav'
S2_STR = 'S2' # used in TalosPlus

DIHEDRAL_NAME_Cb4N = 'Cb4N'
DIHEDRAL_NAME_Cb4C = 'Cb4C'
GLY_HA3_NAME_CING = 'HA2'
range0_360 = [0.,360.]

VALUE_LIST_STR   = "valueList" # Originally in reqWhatif.py
# Used for keying of residue entity (and potentially others) with CING's own Z-score values.
CHK_STR = 'CHK'
RAMACHANDRAN_CHK_STR = 'RAMACHANDRAN_CHK'
CHI1CHI2_CHK_STR = 'CHI1CHI2_CHK'
D1D2_CHK_STR = 'D1D2_CHK'

AUTO_STR = 'auto'
RMSD_STR = 'rmsd'
RANGES_STR = 'ranges'
RESNUM_STR = 'resNum'
VALUE_STR = "value"
BACKBONE_AVERAGE_STR = 'backboneAverage'
HEAVY_ATOM_AVERAGE_STR = 'heavyAtomsAverage'
QSHIFT_STR = 'Qshift'
ALL_ATOMS_STR = 'allAtoms'
BACKBONE_STR = 'backbone'
HEAVY_ATOMS_STR = 'heavyAtoms'
PROTONS_STR = 'protons'

DIS_MAX_ALL_STR = 'dis_max_all'
DIS_RMS_ALL_STR = 'dis_rms_all'
DIS_AV_ALL_STR  = 'dis_av_all'
DIS_AV_VIOL_STR = 'dis_av_viol'
DIS_C1_VIOL_STR = 'dis_c1_viol'
DIS_C3_VIOL_STR = 'dis_c3_viol'
DIS_C5_VIOL_STR = 'dis_c5_viol'

DIH_MAX_ALL_STR = 'dih_max_all'
DIH_RMS_ALL_STR = 'dih_rms_all'
DIH_AV_ALL_STR  = 'dih_av_all'
DIH_AV_VIOL_STR = 'dih_av_viol'
DIH_C1_VIOL_STR = 'dih_c1_viol'
DIH_C3_VIOL_STR = 'dih_c3_viol'
DIH_C5_VIOL_STR = 'dih_c5_viol'

# in CING
VIOLMAXALL_STR = 'violMaxAll'
RMSD_STR       = 'rmsd' # see above.
VIOLAV_STR     = 'violAv'
VIOLAVALL_STR  = 'violAvAll'
VIOLCOUNT1_STR = 'violCount1'
VIOLCOUNT3_STR = 'violCount3'
VIOLCOUNT5_STR = 'violCount5'

# DB
QCS_ALL_STR = 'qcs_all'
QCS_BB_STR = 'qcs_bb'
QCS_HVY_STR = 'qcs_hvy'
QCS_PRT_STR = 'qcs_prt'

SCALE_BY_MAX = 'SCALE_BY_MAX' # Ramachandran
SCALE_BY_SUM = 'SCALE_BY_SUM' # D1D2
SCALE_BY_Z = 'SCALE_BY_Z' # D1D2 new
SCALE_BY_ONE = 'SCALE_BY_ONE' # NO scaling that is.
SCALE_BY_DEFAULT = SCALE_BY_MAX

MIN_PERCENTAGE_RAMA = 2.0  # This is a percentage of the MAX
MAX_PERCENTAGE_RAMA = 20.0
MIN_PERCENTAGE_D1D2 = 0.08 # This is a percentage of the SUM
MAX_PERCENTAGE_D1D2 = 0.2
MIN_Z_D1D2 = -1.0 # This is an absolute value of number of sigma's from average. NB, this is not a percentage
MAX_Z_D1D2 = 0.0

QshiftMinValue = 0.0
QshiftMaxValue = 0.05
QshiftReverseColorScheme = False

DS_STORE_STR = ".DS_Store" # A mac OSX file that should be ignored by CING.

VAL_SETS_CFG_DEFAULT_FILENAME = 'valSets.cfg'