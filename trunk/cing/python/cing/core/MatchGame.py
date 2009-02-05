"""
Play another matching game.

Code for matching external soup to CING's.
"""
from cing.Libs.NTutils import NTcodeerror
from cing.Libs.NTutils import NTerror
from cing.core.constants import CYANA
from cing.core.constants import CYANA_NON_RESIDUES
from cing.core.constants import IUPAC
from cing.core.database import NTdb


class MatchGame():
    def __init__(self, convention = IUPAC, patchAtomNames = True, skipWaters = False, allowNonStandardResidue = True):
        self.convention = convention
        self.patchAtomNames = patchAtomNames
        self.skipWaters = skipWaters
        self.allowNonStandardResidue = allowNonStandardResidue
        
    def matchResidue2Cing(self, res):
        """
        Match res to CING database using previously defined convention;
        Account for 'ill-defined' residues by examining crucial atom names.
        Use CYANA (==DIANA) Naming for conversion to INTERNAL (i.e. These names will not likely change)

        Return NTdb resDef object None on Error

        res is a NTtree object with the following attributes set after this routine:
            db
            skip   
            resName    and attributes for every atom it includes:
            HA2, CD1, ...     
        """
        
#        NTdebug("Now in _matchResidue2Cing: %s" % res)
        
        res.db = None
        res.skip = False

        # Residue names that are ambiguously defined by different PDB file formats
        if res.resName[0:3] == 'ARG':
            if 'HH1' in res:
                res.db = NTdb.getResidueDefByName('ARG', convention = CYANA)
            elif '1HH' in res: # Second set for CYANA 1.x, AMBER
                res.db = NTdb.getResidueDefByName('ARG', convention = CYANA)
            else:
                # Default protonated; this also assures most common for X-ray without protons
                res.db = NTdb.getResidueDefByName('ARG+', convention = CYANA)
            #end if
        #end if
        elif res.resName[0:3] == 'ASP':
            if 'HD2' in res:
                #print 'ASPH'
                res.db = NTdb.getResidueDefByName('ASP', convention = CYANA)
            else:
                # Default deprot; this also assures most common for X-ray without protons
                #print 'ASP'
                res.db = NTdb.getResidueDefByName('ASP-', convention = CYANA)
            #end if
        elif res.resName[0:3] == 'GLU':
            if 'HE2' in res:
                #print 'GLUH'
                res.db = NTdb.getResidueDefByName('GLU', convention = CYANA)
            else:
                # Default deprot; this also assures most common for X-ray without protons
                #print 'GLU'
                res.db = NTdb.getResidueDefByName('GLU-', convention = CYANA)
            #end if
        elif res.resName[0:3] == 'HIS':
            if 'HD1' in res and 'HE2' in res:
                #print 'HISH'
                res.db = NTdb.getResidueDefByName('HIS+', convention = CYANA)
            elif not 'HD1' in res and 'HE2' in res:
                # print HISE
                res.db = NTdb.getResidueDefByName('HIST', convention = CYANA)
            else:
                # Default HD1
                #print 'HIS'
                res.db = NTdb.getResidueDefByName('HIS', convention = CYANA)
            #end if
        elif res.resName[0:3] == 'LYS':
            if ('HZ1' in res and not 'HZ3' in res):
                res.db = NTdb.getResidueDefByName('LYS', convention = CYANA)
            elif ('1HZ' in res and not '3HZ' in res): # Second set for CYANA 1.x
                res.db = NTdb.getResidueDefByName('LYS', convention = CYANA)
            else:
                # Default prot; this also assures most common for X-ray without protons
                res.db = NTdb.getResidueDefByName('LYS+', convention = CYANA)
            #end if
        elif res.resName in CYANA_NON_RESIDUES:
            res.skip = True
        elif res.resName == 'HOH' and self.skipWaters:
            res.skip = True
        else:
            res.db = NTdb.getResidueDefByName(res.resName, convention = self.convention)
        #end if
        
        # Only continue the search if not found and non-standard residues are allowed.
        if res.db:
            return res.db
        
        if not self.allowNonStandardResidue:
            res.skip = True         
            return res.db            

        # Try to match the residue using INTERNAL convention.
        res.db = NTdb.getResidueDefByName(res.resName)
        if res.db:
            return res.db
                       
#        insert new residue.
        res.db = NTdb.appendResidueDef(name = res.resName, shortName = '_')
        if not res.db:
            NTcodeerror("Adding a non-standard residue should have been possible.")
            return None
        # Just a check, disable for speed.
        _x = NTdb.getResidueDefByName(res.resName)
        if not _x:
            NTcodeerror("Added residue but failed to find it again in pdbParser#_matchResidue2Cing")
            
        return res.db
    #end def

    def matchAtom2Cing(self, atm):
        """
        Match atm.name to CING database using previously defined convention;
        Account for 'ill-defined' atoms, such as CYANA definitions in PDB file

        If self.patchAtomNames=True (defined on __init__), several patches are tried (NOT advised to use by GV but
        recommended by JD).

        Return NTdb AtomDef object or None on Error

        atm is a NTtree object with the following attributes set after this routine:
            db
            skip
            _parent
            name
        """
        
#        NTdebug("Now in _matchAtom2Cing: %s" % atm)
        
        if not atm:
            NTerror('pdbParser._matchAtom: undefined atom')
            return None
        #end if

        atm.db = None
        atm.skip = False
        res = atm._parent

        if not res:
            NTerror('pdbParser._matchAtom: undefined parent residue, atom %s, convention %s, not matched',
                    atm.name, self.convention)
            return None
        #end if
        #print '>',atm,res

        if res.skip:
            atm.skip = True
            return None # JFD: this is not an error but contract of method signature requests an AtomDef object
        # which can not be created here.
        #end if

        if not res.db:
            NTerror('_matchAtom2Cing: undefined parent residue DB'),
            return None
        #end if

        # Now try to match the name of the atom
#        if self.convention == CYANA or self.convention == CYANA2:
            # the residue names are in Cyana1.x convention (i.e. for GLU-)
            # atm names of the Cyana1.x PDB files are in messed-up Cyana format
            # So: 1HD2 becomes HD21 where needed:
            # JFD adds: Not just in CYANA
        # JFD adds: new rule; CING always reworks atom names that start with a digit.
        aName = moveFirstDigitToEnd(atm.name)
#        else:
#            aName = atm.name
        #end if

        # For the atom name conversion step, we use the res.db object. This points to the proper ResidueDef that we just
        # mapped in the _matchResidue2Cing routine.
        atm.db = res.db.getAtomDefByName(aName, convention = self.convention)
        if atm.db:
            return atm.db

        # JFD adds hacks these debilitating simple variations if nothing is found so far
        # GWV does not like this at all and therefore hides it behind an option
        if self.patchAtomNames:        
#            if not atm.db: # some besides CYANA have this too; just too easy to hack here
#                aName = moveFirstDigitToEnd(atm.name)
#                atm.db = res.db.getAtomDefByName( aName, convention = self.convention )
            #end if
#            if not atm.db:
            bName = None # Don't save the variable name beyond patch attempt.
            if atm.name == 'H': # happens for 1y4o_1model reading as cyana but in cyana we have hn for INTERNAL_0
                bName = 'HN' 
            elif atm.name == 'HN': # for future examples.
                bName = 'H'
            if bName:
                atm.db = res.db.getAtomDefByName(bName, convention = self.convention)
            #end if
#            if atm.db:
#                NTdebug('pdbParser._matchAtom: patched atom %s, residue %s %s, convention %s',
#                           atm.name, res.resName, res.resNum, self.convention                     )                
        #end if
        if atm.db:
            return atm.db

        # Try internal one for those just added to non-standard residues/atoms.
        atm.db = res.db.getAtomDefByName(aName)                
#        if atm.db:
#            return atm.db        
        return atm.db
    #end def

        
def moveFirstDigitToEnd(a):
    if a[0].isdigit():
        a = a[1:] + a[0]
    return a
