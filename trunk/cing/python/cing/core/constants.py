"""
Nomenclature database constants descriptors:
AQUA         AQUA nomenclature
CNS          CNS nomenclature; amounts to XPLOR
CYANA        CYANA 1.x nomenclature
CYANA2       CYANA 2.x nomenclature
DYANA        DYANA nomenclature; amounts to CYANA
INTERNAL     Internal nomenclature
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
INTERNAL   = 'INTERNAL_1'   # INTERNAL_0 is the first convention used: was based upon DYANA/CYANA1.x convention
                            # JFD adds: TODO: why not take IUPAC for internal work? 
                            # INTERNAL_1 is the second convention used: IUPAC for IUPAC defined atoms, CYANA2 for non-IUPAC atoms
LOOSE      = 'LOOSE'

# Wim added
CCPN       = 'CCPN'

# No shift value for Xeasy.
NOSHIFT         =  999.000


X_AXIS = 0
Y_AXIS = 1
Z_AXIS = 2
A_AXIS = 3

CYANA_NON_RESIDUES = ['PL','LL2','link']

# Color labels for HTML/CSS output
COLOR_RED    = 'red'
COLOR_GREEN  = 'green'
COLOR_ORANGE = 'orange'


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

ANY_ENTITY_LEVEL = 'ANY_ENTITY'

DR_LEVEL       = 'DistanceRestraint'
DRL_LEVEL      = 'DistanceRestraintList'

POOR_PROP = 'POOR'
BAD_PROP  = 'BAD'

CHARS_PER_LINE_OF_PROGRESS = 100

VAL_SETS_CFG_DEFAULT_FILENAME = 'valSets.cfg'
