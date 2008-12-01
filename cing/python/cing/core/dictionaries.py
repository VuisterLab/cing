from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTwarning
from cing.core.constants import INTERNAL
from cing.core.constants import LOOSE
from cing.core.database import NTdb

#NTdebug("==> Creating translation dictionaries ... ")
#
##
##==============================================================================
## Create the residueDict and atomDict settings from the nameDict's
##
## This allows checking and conversion of names
## Note that it generates cycles in the referencing, so printing of
## these dicts generates a recursion error.
##
##
## NTdb.residueDict[INTERNAL] is a dictionary of all internal residue names. Each
## entry points to the relevant residueDef instance.
## Ex. NTdb.residueDict[INTERNAL]['GLU-'] points to the GLU- residueDef instance
##
## NTdb.residueDict[CYANA2] is a dictionary of all CYANA2 residue names. Each
## entry points to the relevant residueDef instance
##
## idem for all other conventions
##
## NTdb.residueDict[LOOSE] is a dictionary of all Losely defined residue names. Each
## entry points to the relevant residueDef instance
##
## The atomDict dictionaries of each residue function analogously for the atom names
##
##==============================================================================
#for res in NTdb:
#    # loose definitions
#    NTdb.residueDict.setdefault( LOOSE, {} )
#    for n in [res.shortName, res.name, res.name.capitalize(), res.name.lower()]:
#        NTdb.residueDict[LOOSE][n] = res
#    #end for
#    #different convention definitions
#    for convR, nameR in res.nameDict.iteritems():
#        NTdb.residueDict.setdefault( convR, {} )
#        if (nameR != None):
#            NTdb.residueDict[convR][nameR] = res
#        #end if
#    # end for
#    for atm in res:
#        for convA, nameA in atm.nameDict.iteritems():
#            res.atomDict.setdefault( convA, {} )
#            if (nameA != None):
#                # XPLOR definitions have possibly multiple entries
#                # separated by ','
#                for n in nameA.split(','):
#                    res.atomDict[convA][n] = atm
#                #end for
#            #end if
#        #end for
#    #end for
##end for

#def isValidResidueName( resName, convention = INTERNAL ):
#    """Compatibility dummy"""
#    return NTdb.isValidResidueName( resName, convention = convention )
##end def
#
#def isValidAtomName( resName, atomName, convention = INTERNAL):
#    """Compatibility dummy"""
#    return NTdb.isValidAtomName( resName, atomName, convention = convention )
##end def

#
#==============================================================================
#
#def translateResidueName( convention, resName, newConvention=INTERNAL ):
#    """ Translate resName from convention to newConvention
#        return None on error/no-translation
#    """
#    res =  NTdb.getResidueDefByName( resName, convention=convention )
#    if res != None:
#        return res.translate( newConvention )
#    #endif
#    return None
##end def
##
##==============================================================================
##
#def translateAtomName( convention, resName, atmName, newConvention=INTERNAL ):
#    """ Translate resName,atomName from convention to newConvention
#        return None on error/no-translation
#    """
#    atm =  NTdb.getAtomDefByName( resName, atmName, convention=convention )
#    if atm != None:
#        return atm.translate( newConvention )
#    #endif
#    return None
##end def
#
#==============================================================================
#
#def NTdbGetResidue( resName, convention = INTERNAL ):
#    """Compatibility dummy"""
#    return NTdb.getResidueDefByName( resName, convention = convention )
##end def
##
#==============================================================================
#
#def NTdbGetAtom( resName, atmName, convention = INTERNAL ):
#    """Compatibility dummy"""
#    return NTdb.getAtomDefByName( resName, atomName, convention = convention )
##end def

