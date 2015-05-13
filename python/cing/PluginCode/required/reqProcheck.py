'required items for this plugin for CING setup'
from cing.Libs.NTutils import * #@UnusedWildImport

PROCHECK_STR       = "procheck" # key to the entities (atoms, residues, etc under which the results will be stored
PC_STR             = "pc" # key to the entities (atoms, residues, etc under which the results will be stored
SECSTRUCT_STR      = 'secStruct'
#CONSENSUS_SEC_STRUCT_FRACTION = 0.6 # not used anymore; just taking the most common one.

gf_STR = 'gf'
gf_PHIPSI_STR = 'gfPHIPSI'
gf_CHI12_STR = 'gfCHI12'
gf_CHI1_STR = 'gfCHI1'

# Used in RDB
pc_gf_STR           = 'pc_gf'
pc_gf_PHIPSI_STR    = 'pc_gf_PHIPSI'
pc_gf_CHI12_STR     = 'pc_gf_CHI12'
pc_gf_CHI1_STR      = 'pc_gf_CHI1'

pc_rama_core_STR = 'pc_rama_core'
pc_rama_allow_STR = 'pc_rama_allow'
pc_rama_gener_STR = 'pc_rama_gener'
pc_rama_disall_STR = 'pc_rama_disall'

core_STR = 'core'
allowed_STR = 'allowed'
generous_STR = 'generous'
disallowed_STR = 'disallowed'

gf_LIST_STR = [ gf_STR, gf_PHIPSI_STR, gf_CHI12_STR, gf_CHI1_STR]
pc_rama_LIST_STR = [ pc_rama_core_STR, pc_rama_allow_STR, pc_rama_gener_STR, pc_rama_disall_STR]

#MXMODL Maximum number of models
#left at 60 in   viol2pdb because the same as MXFILE
MAX_PROCHECK_NMR_MODELS = 60
#MAX_PROCHECK_NMR_MODELS = 2

#C MXRES  - Maximum number of residues allowed for the protein structure
#C          being plotted
#was 20,000 in tplot.inc, set to 200,000
#5,000 to 50,000 in mplot.inc etc.
MAX_PROCHECK_TOTAL_RESIDUES = 50000
#MAX_PROCHECK_TOTAL_RESIDUES = 100

PCgFactorMinValue = - 3.0
PCgFactorMaxValue = 1.0
# Value above which the program PC was actually incorrect most likely
# See procheck.py code.
PCgFactorMaxErrorValue = 1.5
PCgFactorReverseColorScheme = True

def to3StatePC( strNTList ):
    """Exactly the same as Procheck postscript plots was attempted.

    S,B,h,e,t, ,None--> space character
    E               --> S
    H G             --> H

    Note that CING and Procheck_NMR does not draw an 'h' to a H and e to S.

    Procheck description: The secondary structure plot shows a schematic
    representation of the Kabsch & Sander (1983) secondary structure assignments.
    The key just below the picture shows which structure is which. Beta strands are
    taken to include all residues with a Kabsch & Sander assignment of E, helices
    corresponds to both H and G assignments, while everything else is taken to be
    random coil.

    PyMOL description: With PyMOL, heavy emphasis is placed on cartoon aesthetics,
    and so both hydrogen bonding patterns and backbone geometry are used in the
    assignment process. Depending upon the local context, helix and strand assignments
    are made based on geometry, hydrogen bonding, or both. This command will generate
    results which differ slightly from DSSP and other programs. Most deviations occur
    in borderline or transition regions. Generally speaking, PyMOL is more strict,
    thus assigning fewer helix/sheet residues, except for partially distorted helices,
    which PyMOL tends to tolerate.

    """
    result = NTlist()
    for c in strNTList:
        if c == 'E':
            n = 'S'
        elif c == 'H' or c == 'G':
            n = 'H'
        else:
            n = ' '
        result.append( n )
    return result

