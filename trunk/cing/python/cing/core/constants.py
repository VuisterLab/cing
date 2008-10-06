
AQUA       = 'AQUA' # not uptodate with BMRB DG/G difference.
IUPAC      = 'IUPAC'
BMRB       =  IUPAC # since IUPAC is set to be equivalent to BMRB; remove one of them. IUPAC is used in dbTable.
SPARKY     =  IUPAC
BMRBd      = 'BMRBd'
CYANA      = 'CYANA'
XEASY      = CYANA
CYANA2     = 'CYANA2'
XPLOR      = 'XPLOR'
PDB        = 'PDB'
INTERNAL   = 'INTERNAL_0'   # INTERNAL_0 is the first convention used: was based upon DYANA/CYANA1.x convention
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


