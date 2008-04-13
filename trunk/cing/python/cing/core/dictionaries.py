from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTwarning
from cing.core.constants import INTERNAL
from cing.core.constants import LOOSE
from cing.core.database import NTdb

NTdebug("==> Creating translation dictionaries ... ")

#
#==============================================================================
# Create the residueDict and atomDict settings from the nameDict's
#
# This allows checking and conversion of names
# Note that it generates cycles in the referencing, so printing of
# these dicts generates a recursion error.
#
#
# NTdb.residueDict[INTERNAL] is a dictionary of all internal residue names. Each
# entry points to the relevant residueDef instance.
# Ex. NTdb.residueDict[INTERNAL]['GLU-'] points to the GLU- residueDef instance
#
# NTdb.residueDict[CYANA2] is a dictionary of all CYANA2 residue names. Each
# entry points to the relevant residueDef instance
#
# idem for all other conventions
#
# NTdb.residueDict[LOOSE] is a dictionary of all Losely defined residue names. Each
# entry points to the relevant residueDef instance
#
# The atomDict dictionaries of each residue function analogously for the atom names
#
#==============================================================================
for res in NTdb:
    # loose definitions
    NTdb.residueDict.setdefault( LOOSE, {} )
    for n in [res.shortName, res.name, res.name.capitalize(), res.name.lower()]:
        NTdb.residueDict[LOOSE][n] = res
    #end for
    #different convention definitions
    for convR, nameR in res.nameDict.iteritems():
        NTdb.residueDict.setdefault( convR, {} )
        if (nameR != None):
            NTdb.residueDict[convR][nameR] = res
        #end if
    # end for
    for atm in res:
        for convA, nameA in atm.nameDict.iteritems():
            res.atomDict.setdefault( convA, {} )
            if (nameA != None):
                # XPLOR definitions have possibly multiple entries
                # separated by ','
                for n in nameA.split(','):
                    res.atomDict[convA][n] = atm
                #end for
            #end if
        #end for
    #end for
#end for
#print NTdb.residueDict[LOOSE]['F']
#print NTdb.residueDict[LOOSE]['Phe']
#
#==============================================================================
#
def isValidResidueName( resName, convention = INTERNAL ):
    """return 1 if resName is a valid for convention"""
#  print '>>', resName, atomName

    rn = resName.strip()
    if rn in NTdb.residueDict[convention]:
        return 1
    return


def isValidAtomName( resName, atomName, convention = INTERNAL):
    """Only return 1 if resName,atomName is a valid for convention
       Otherwise the default return of zero on invalid.
    """
#  print '>>', resName, atomName

    rn = resName.strip()
    an = atomName.strip()
    if not isValidResidueName( rn, convention ):
        NTwarning("Residue name is not valid in cing.core.dictionaries#isValidAtomName for: ["+rn+"]")
        return None
    res = NTdb.residueDict[convention][rn]
    if an in res.atomDict[convention]:
        return 1
#  NTwarning("Atom name is not valid in cing.core.dictionaries#isValidAtomName for: ["+an+"]")

#print isValidAtomName( 'Y', 'HN', 'BMRB')
#print isValidResidueName('Y',LOOSE)
#print isValidResidueName( 'ARG+', 'CYANA2')
#print isValidResidueName( 'ARG', 'CYANA2')



#
#==============================================================================
#
def translateResidueName( convention, resName, newConvention=INTERNAL ):
    """ Translate resName from convention to newConvention
        return None on error/no-translation
    """
    res =  NTdbGetResidue( resName, convention=convention )
    if res != None:
        return res.translate( newConvention )
    #endif
    return None
#end def
#
#==============================================================================
#
def translateAtomName( convention, resName, atmName, newConvention=INTERNAL ):
    """ Translate resName,atomName from convention to newConvention
        return None on error/no-translation
    """
    atm =  NTdbGetAtom( resName, atmName, convention=convention )
    if atm != None:
        return atm.translate( newConvention )
    #endif
    return None
#end def
#
#==============================================================================
#
def NTdbGetResidue( resName, convention = INTERNAL ):
    """return NTdb entry for resName if resName is a valid for convention
       or None otherwise
    """
    rn = resName.strip()
    if isValidResidueName( rn , convention=convention ):
        return NTdb.residueDict[convention][rn]
    #endif
    return None
#end def
#
#==============================================================================
#
def NTdbGetAtom( resName, atmName, convention = INTERNAL ):
    """return NTdb entry for resName,atmName if resName,atmName is a valid
       for convention
       or None otherwise
    """
    if not resName:
        NTerror("in dictionaries.NTdbGetAtom resName was None")
        return None
    if not atmName:
        NTerror("in dictionaries.NTdbGetAtom atmName was None")
        return None
    rn = resName.strip()
    an = atmName.strip()

    if isValidAtomName( rn , an, convention=convention ):
        return NTdb.residueDict[convention][rn].atomDict[convention][an]
    #endif
    return None
#end def

