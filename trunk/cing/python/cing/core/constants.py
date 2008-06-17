
AQUA       = 'AQUA' # not uptodate with BMRB DG/G difference.
BMRB       = 'BMRB'
SPARKY     = BMRB
IUPAC      = BMRB
BMRBd      = 'BMRBd'
CYANA      = 'CYANA'
XEASY      = CYANA
CYANA2     = 'CYANA2'
XPLOR      = 'XPLOR'
PDB        = 'PDB'
INTERNAL   = 'INTERNAL'
LOOSE      = 'LOOSE'

# Wim added
CCPN       = 'CCPN'

# No shift value for Xeasy.
NOSHIFT         =  999.000

#http://www.python.org/dev/peps/pep-0754/
#try:
#    from matplotlib.numerix import nan as NAN_FLOAT # is in python 2.6 ?
#except ImportError:
#    NAN_FLOAT = 'nan'
#end try
#try:
#    from matplotlib.numerix._na_imports import isnan as ISNAN
#except ImportError:
#    from cing.Libs.fpconst import isNaN as ISNAN #@UnusedImport
    # should be math.isnan when we switch to python 2.6
#end try

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


