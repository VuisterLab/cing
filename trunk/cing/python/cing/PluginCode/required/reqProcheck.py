from cing.Libs.NTutils import NTlist

PROCHECK_STR       = "procheck" # key to the entities (atoms, residues, etc under which the results will be stored
SECSTRUCT_STR      = 'secStruct'
CONSENSUS_SEC_STRUCT_FRACTION = 0.6

#MXMODL Maximum number of models
#left at 60 in   viol2pdb because the same as MXFILE
MAX_PROCHECK_NMR_MODELS = 60
#MAX_PROCHECK_NMR_MODELS = 2

def to3StateUpper( strNTList ):
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
