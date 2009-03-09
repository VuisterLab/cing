from cing.Libs.NTutils import NTlist
from cing.PluginCode.required.reqProcheck import CONSENSUS_SEC_STRUCT_FRACTION
from cing.PluginCode.required.reqProcheck import SECSTRUCT_STR

DSSP_STR = "dssp" # key to the entities (atoms, residues, etc under which the results will be stored

def to3StateUpper( strNTList ):
    """Personal communications JFD with Rob Hooft and Gert Vriend.

    3, H -> H
    B, E -> S
    space, S, G, T -> coil (represented by ' ')

    See namesake method in procheck class.
    """
    result = NTlist()
    for c in strNTList:
        n = ' '
        if c == '3' or c == 'H':
            n = 'H'
        elif c == 'B' or c == 'E':
            n = 'S'
        result.append( n )
    return result

def getDsspSecStructConsensus( res ):
    """ Returns None for error, or one of ['H', 'S', ' ' ]
    """
    secStructList = res.getDeepByKeys(DSSP_STR,SECSTRUCT_STR)
    result = None
    if secStructList:
        secStructList = to3StateUpper( secStructList )
        result = secStructList.getConsensus(CONSENSUS_SEC_STRUCT_FRACTION) # will set it if not present yet.
#    NTdebug('secStruct res: %s %s %s', res, secStructList, secStruct)
    return result
