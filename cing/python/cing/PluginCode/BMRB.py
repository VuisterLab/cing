"""
Adds init/import of BMRB format

Methods:
"""
from cing.Libs.AwkLike import AwkLike
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.constants import * #@UnusedWildImport
from cing.core.molecule import Chain
from cing.core.molecule import Molecule
#from cing.Libs.fpconst import NaN

bmrbAtomType2spinTypeCingMap = { 'H': '1H', 'C': '13C', 'N': '15N', 'P': '31P' }
bmrbResType2CingMap = { 'H': '1H', 'C': '13C', 'N': '15N', 'P': '31P' }

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
        res = mol._addResidue( Chain.defaultChainId, resName, resNum, IUPAC )

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
def importFromBMRB( project, bmrbFile ):
    """
        Import chemical shifts from edited BMRB file
        No reassigned Pseudo atoms yet;
        Return molecule instance or None on error
    """

    if not project.molecule:
        NTerror("Error importBMRB: no molecule defined" )
        return None
    #end if

    mol = project.molecule
    mol.newResonances(source=bmrbFile)

    error = False
#    for f in AwkLike( bmrbFile, minNF = 8, commentString = '#' ):
#
#        resName = f.dollar[3]
#        resNum  = f.int(2)
#
#        atomName= f.dollar[4]
#        shift   = f.float(6)
#        serror  = f.float(7)
#        _ambig   = f.int(8)

    for f in AwkLike( bmrbFile, minNF = 9, commentString = '#' ):

        resName = f.dollar[4]
        resNum  = f.int(2)

        atomName= f.dollar[5]
        shift   = f.float(7)
        serror  = f.float(8)
        _ambig   = f.int(9)

        atm = mol.decodeNameTuple( (IUPAC, Chain.defaultChainId, resNum, atomName) )

        if not atm:
            NTerror( 'Error initBMRB: invalid atom %s %s line %d (%s)',
                    resName, atomName, f.NR, f.dollar[0] )
            error = True
        else:
            atm.resonances().value = shift
            atm.resonances().error = serror
            if _ambig == 1 and atm.isProChiral():
                atm.stereoAssigned = True
        #end if
    #end for

    # now fix the assignments;
    for atm in mol.allAtoms():
        # Check if all realAtoms are assigned in case there is a pseudo atom
        if atm.isAssigned() and not atm.isStereoAssigned() and atm.hasPseudoAtom():
            fix = False
            pseudo = atm.pseudoAtom()
            for a in pseudo.realAtoms():
                if not a.isAssigned():
                    fix = True
                    break
                #end if
            #end for
            if fix:
                pseudo.resonances().value = atm.resonances().value
                pseudo.resonances().error = atm.resonances().error
                atm.resonances().value = NaN
                atm.resonances().value = NaN
                NTmessage('Deassigned %s, assigned %s', atm, pseudo)
            #end if
        #end if
    #end for

    if error:
        NTerror( '==> importFromBMRB: completed with error(s)' )
    else:
        NTmessage( '==> importFromBMRB: successfully parsed %d lines from %s', f.NR, f.FILENAME )
    #end if

    if error:
        return None
    return mol
#end def

# register the functions
methods  = [(initBMRB, None),
            (importFromBMRB, None)
           ]
saves    = []
restores = []
exports  = []
