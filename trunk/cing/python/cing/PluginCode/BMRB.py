"""
Adds init/import of BMRB format

Methods:
"""
from cing.Libs.AwkLike import AwkLike
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.core.constants import BMRBd
from cing.core.molecule import Molecule
from cing.core.molecule import Chain

class NMRrestraintsGrid:
    def __init__(self):
        self.bmrbUrl = "http://www.bmrb.wisc.edu"

#==============================================================================
def initBMRB( project, bmrbFile, moleculeName  = None ):
    """
        Initialize from edited BMRB file
        Return molecule instance
    """
    mol = Molecule( name=moleculeName )   
    project.appendMolecule( mol )

    error = False
    for f in AwkLike( bmrbFile, minNF = 8, commentString = '#' ):

        resName = f.dollar[3]
        resNum  = f.int(2)

        atomName = f.dollar[4]
#        shift   = f.float(6)
#        serror  = f.float(7)
#        ambig   = f.int(8)
        res = mol._addResidue( Chain.defaultChainId, resName, resNum, BMRBd )

        if (not res):
            NTerror( 'Error initBMRB: invalid residue %s %s line %d (%s)\n',
                    resName, atomName, f.NR, f.dollar[0]
                    )
            error = True
        #end if
    #end for

    error = error or (project.importBMRB( bmrbFile)    == None)
    if error:
        NTmessage( '==> initBMRB: completed with error(s)' )
    else:
        NTmessage( '==> initBMRB: successfully parsed %d lines from %s', f.NR, f.FILENAME )
    #end if
    NTmessage("%s", mol.format() )

    if error: 
        return None
    return mol
#end def

#==============================================================================
def importBMRB( project, bmrbFile =None ):
    """
        Import chemical shifts from edited BMRB file
        No reassigned Pseudo atoms yet;
        Return molecule instance or None on error
    """

    if not project.molecule:
        NTerror("Error importBMRB: no molecule defined\n" )
        return None
    #end if

    mol = project.molecule
    mol.newResonances()

    error = False
    for f in AwkLike( bmrbFile, minNF = 8, commentString = '#' ):

        resName = f.dollar[3]
        resNum  = f.int(2)

        atomName= f.dollar[4]
        shift   = f.float(6)
        serror  = f.float(7)
        _ambig   = f.int(8)

        atm = mol.decodeNameTuple( (BMRBd, Chain.defaultChainId, resNum, atomName) )

        if not atm:
            NTerror( 'Error initBMRB: invalid atom %s %s line %d (%s)\n',
                    resName, atomName, f.NR, f.dollar[0] )
            error = True
        else:
            atm.resonances().value = shift
            atm.resonances().error = serror
        #end if
    #end for

    if error:
        NTmessage( '==> importBMRB: completed with error(s)' )
    else:
        NTmessage( '==> importBMRB: successfully parsed %d lines from %s', f.NR, f.FILENAME )
    #end if
    NTmessage("%s", mol.format() )

    if error: 
        return None
    return mol
#end def

# register the functions
methods  = [(initBMRB, None),
            (importBMRB, None)
           ]
saves    = []
restores = []
exports  = []
