from cing.core.constants import INTERNAL
from cing.Libs.AwkLike import AwkLike
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTpath
from cing.Libs.NTutils import NTdict # Used by obj[r.dollar[1]] = eval( " ".join( r.dollar[3:] ) ) @UnusedImport
from cing.Libs.NTutils import NTtree
from cing.Libs.NTutils import fprintf
from cing import cingPythonCingDir
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import NTerror
import os
import sys


patches = True

"""
NTdb: database of topology, nomenclature and NMR properties

20-25 Sep 2005
Restructuring using NTtree and saving to different file format.
1. Read residueDefs and converted to 'keyword format': dbTable.py
2. Redefined the MolDef, ResidueDef, AtomDef and DihedralDef classes; based on
   NTtree,
   used nameDict attribute to store the different names
3. File 'NTdb.py': contains classes and parser of dbTable.
   Yields NTdb as root of database
4. Conversion dictionaries initialized from nameDict entries of NTdb

Note that updating dict and list types requires first initialisation of the
NTdb-tree and then updating it. Otherwise, the changes are discarded as parsing
the dbTable involves blunt assignment of the corresponding attributes.

28 Nov 2005:
* dbTable now contains dbTable entry: update programs that write this table.
* Using dbTableNew, added spin system SS

30 Jan 2006.
Included shifts info from BMRB using the addSHIFTS.py routine.
Residues CYSS, HIS+, HIST, and DNA/RNA are not yet included.

22 March 2006:
Slightly changed the way the database is loaded: now a plain textfile; path is
taken from NTmolPath, which is set on init

19 Feb 2007:
Simplified code for parsing dbTable file
Removed \n from all __FORMAT__ defs

29 Sep 2008:
Removed XML saves; patch the properties for duplicates

"""


class MolDef( NTtree ):
    def __init__( self, name, *args, **kwds ):
        NTtree.__init__( self,
                         __CLASS__   = 'MolDef',
                         convention  = INTERNAL,
                         name        = name,
                         residueDict = {},    # contains definitions of residues, sorted by convention
                       )
        self.residues = self._children
        for arg in args:
            self.update( arg )
        #end for
        self.update( kwds )

        self.__FORMAT__ = '=== MolDef %(name)s (%(convention)r) ===\n' + \
                          'residues:   %(residues)s\n'

#        self.saveXML('name')
    #end def

    def appendResidue( self, name, shortName, **kwds ):
        res = ResidueDef( name, shortName, **kwds )
        self._addChild( res )
        res.molDef = self
        return res
    #end def

    def residuesWithProperties(self, *properties ):
        """
        Return a NTlist instance with residueDefs that have properties
        """
        result = NTlist()

        if len(properties) == 0: return result
        for res in self.residues:
            if res.hasProperties(*properties):
                result.append(res)
            #end if
        #end for
        return result
    #end def

    def atomsWithProperties(self, *properties ):
        """
        Return a NTlist instance with atomDefs that have properties
        """
        result = NTlist()

        if len(properties) == 0: return result
        for atm in self.subNodes(depth=2):
            if atm.hasProperties(*properties):
                result.append(atm)
            #end if
        #end for
        return result
    #end def

    def exportDef( self, fileName=None, stream = sys.stdout ):
        "export name definitions to fileName/stream"
        if fileName != None:
            stream = open( fileName, 'w')
        #end if

#        fprintf( stream, 'dbTable = """\n')
        for res in self:
            res.exportDef( stream=stream )
        #end for
#        fprintf( stream, '"""\n' )
    #end def
#end class

class ResidueDef( NTtree ):
    def __init__( self, name, shortName, **kwds ):
        NTtree.__init__(   self,
                           __CLASS__   = 'ResidueDef',
                           convention  = INTERNAL,
                           name        = name,
                           shortName   = shortName,
                           comment     = None,
                           nameDict    = {},
                           atomDict    = {}, # contains definition of atoms, sorted by convention, dynamically created on initialisation
                           dihedrals   = NTlist(),
                           properties  = [] # list of properties for residue
                       )
        self.atoms = self._children
        self.update( kwds )

        self.__FORMAT__ = '=== ResidueDef %(name)s (%(convention)r) ===\n' +\
                          'shortName:  %(shortName)s\n' +\
                          'comment:    %(comment)s\n' +\
                          'atoms:      %(atoms)s\n' +\
                          'dihedrals:  %(dihedrals)s\n' +\
                          'properties: %(properties)s'

#        self.saveXML('name', 'shortName', 'comment', 'nameDict','dihedrals', 'properties')
        #NB atoms is a derived attribute (from _children), no need to save it explicitly

    def appendAtom( self, name, **kwds ):
        atm = AtomDef( name, **kwds )
        self._addChild( atm )
        atm.residueDef = self
        return atm
    #end def

    def appendDihedral( self, name, **kwds ):
        dh = DihedralDef( name, **kwds )
        self[name] = dh
        self.dihedrals.append( dh )
        dh._parent = self
        dh.residueDef = self
        return dh
    #end def

    def residuesWithProperties(self, *properties ):
        """
        Return a NTlist instance with residueDefs that have properties
        """
        result = NTlist()

        if self.hasProperties(*properties):
            result.append(self)
        #end if
        return result
    #end def

    def atomsWithProperties(self, *properties ):
        """
        Return a NTlist instance with atomDefs that have All properties
        """
        result = NTlist()

        if not len(properties):
            return result
        for atm in self.subNodes(depth=1):
            if atm.hasProperties(*properties):
                result.append(atm)
            #end if
        #end for
        return result
    #end def

    def hasProperties(self, *properties):
        """
        Returns True if ResidueDef has All properties, False otherwise
        """
        if not len(properties):
            return False

        for p in properties:
            if not p in self.properties:
                return False
            #end if
        #end for
        return True
    #end def

    def translate( self, convention ):
        if convention in self.nameDict:
            return self.nameDict[convention]
        #end if
        return None
    #end def

    def exportDef( self, stream = sys.stdout ):
        "export definitions to stream"
        fprintf( stream, '\n#=======================================================================\n')
        fprintf( stream,   '#\t%-8s %-8s\n','internal', 'short')
        fprintf( stream,   'RESIDUE\t%-8s %-8s\n',self.name, self.shortName )
        fprintf( stream,   '#=======================================================================\n')

        # saving different residue attributes
        for attr in ['nameDict', 'comment','properties']:
            fprintf( stream, "\t%s = %s\n", attr, repr(self[attr]) )
        #end for

        for dh in self.dihedrals:
            dh.exportDef( stream )
        #end for

        for atm in self.atoms:
            atm.exportDef( stream )
        #end for

        fprintf( stream,   'END_RESIDUE\n')
        fprintf( stream,   '#=======================================================================\n')
    #end def
#end class

class AtomDef( NTtree ):
    def __init__( self, name, **kwds ):
        #print '>>', args, kwds
        NTtree.__init__( self,
                           __CLASS__   = 'AtomDef' ,
                           convention  = INTERNAL,
                           name        = name,     # Internal name
                           nameDict    = {},
                           aliases     = [],       # list of aliases

                           topology    = [],       # List of bound atoms: (i, name) tuple
                                                   # i:  -1=previous residue; 0=current residue; 1=next residue
                           pseudo      = None,     # Corresponding pseudo atom (for real atoms)
                           real        = [],       # List of corresponding real atoms (for pseudo atoms)

                           type        = None,     # Cyana type of atom
                           spinType    = None,     # NMR spin type; i.e. 1H, 13C ...
                           shift       = None,      # NTdict with average and sd

                           hetatm      = False,    # PDB HETATM type

                           properties  = []        # List with properties
                         )
        self.update( kwds )

        self.__FORMAT__ = '=== AtomDef %(residueDef)s.%(name)s (%(convention)r) ===\n' +\
                          'topology:   %(topology)s\n' +\
                          'pseudo:     %(pseudo)s\n' +\
                          'real:       %(real)s\n' +\
                          'spinType:   %(spinType)s\n' +\
                          'hetatm:     %(hetatm)s\n' +\
                          'properties: %(properties)s'

#        self.saveXML('name', 'nameDict'
#                     'topology','pseudo','real',
#                     'type','spinType','shift', 'hetatm','properties'
#                    )

    def translate( self, convention ):
#        if convention in self.nameDict:
# speed
        if self.nameDict.has_key(convention):
            # XPLOR definitions potentially have multiple
            # entries, separated by ','. Take the first.
            if self.nameDict[convention] != None:
                return self.nameDict[convention].split(',')[0]
            #end if
        #end if
        return None
    #end def

#    def _changeConvention(self, newConvention):
#        """Change convention for this atom.
#        Not to be used without proper knowledge of the effects; i.e. only for updating dbTable
#
#        return True on error
#        """
#        newName = self.translate(newConvention)
#        if not newName:
#            NTerror('AtomDef.changeConvention: not defined for %r', newConvention)
#            return True
#        oldName = self.name
#        if newName == oldName:
#            # do nothing except changing convention
#            self.convention = newConvention
#            return False
#
#        if self.residueDef.renameChild(self, newName) != self:
#            NTerror('AtomDef.changeConvention: changing %s to %s', self, newName)
#            return True
#
#        # changing topology fields
#        # of course this gives problems for sequential connectivities; so we will
#        # simply only put a warning for those
#        for resId, atmName in self.topology:
#            if resId != 0:
#                NTwarning('AtomDef.changeConvention: checking %s topology (%d,%s) skipped', self, resId,atmName)
#            else:
#                if not atmName in self.residueDef:
#                    NTerror('AtomDef.changeConvention: checking %s topology (%d,%s)', self, resId,atmName)
#                    return True
#                #end if
#                NTdebug('AtomDef.changeConvention: changing %s topology (%d,%s)', self, resId,atmName)
#                atm = self.residueDef[atmName]
#                for i, top in enumerate(atm.topology):
#                    if top[1] == oldName:
#                        atm.topology[i] = (top[0],newName)
#                        break
#                    #end if
#                #end for
#            #end if
#        #end for
#
#        # changing dihedral fields
#        # of course this gives problems for sequential connectivities; so we will
#        # simply only put a warning for those
#        for dihed in self.residue.dihedrals:
#            for resId, atmName in dihed.atoms:
#                if resId != 0:
#                    NTwarning('AtomDef.changeConvention: checking %s topology (%d,%s) skipped', dihed, resId,atmName)
#                else:
#                    if not atmName in self.residueDef:
#                        NTerror('AtomDef.changeConvention: checking %s topology (%d,%s)', self, resId,atmName)
#                        return True
#                    #end if
#                    NTdebug('AtomDef.changeConvention: changing %s topology (%d,%s)', self, resId,atmName)
#                    atm = self.residueDef[atmName]
#                    for i, top in enumerate(atm.topology):
#                        if top[1] == oldName:
#                            atm.topology[i] = (top[0],newName)
#                            break
#                        #end if
#                    #end for
#                #end if
#        #end for
#
#        # change properties
#        changeProperty( self, oldName, newName)
#
#        self.convention = newConvention
#    #end def

    def atomsWithProperties(self, *properties ):
        """
        Return a NTlist instance with self if it has properties
        """
        result = NTlist()

        if len(properties) == 0: return result
        if self.hasProperties(*properties):
            result.append(self)
        #end if
        return result
    #end def

    def hasProperties(self, *properties):
        """
        Returns True if AtomDef has properties, False otherwise
        """
        if len(properties) == 0: return False

        for p in properties:
            if not p in self.properties:
                return False
            #end if
        #end for
        return True
    #end def

    def exportDef( self, stream = sys.stdout, convention=INTERNAL ):
        "export definitions to stream"
        fprintf( stream, '\t#---------------------------------------------------------------\n')
        fprintf( stream, '\tATOM %-8s\n',self.translate(convention))
        fprintf( stream, '\t#---------------------------------------------------------------\n')

        if convention == INTERNAL:
            top2 = self.topology
        else:
            # convert topology
            top2 = []
            for resId,atmName in self.topology:
                if resId != 0:
                    NTwarning('AtomDef.exportDef: %s topology (%d,%s) skipped translation', self, resId, atmName)
                    top2.append( (resId,atmName) )
                elif not atmName in self.residueDef:
                    NTerror('AtomDef.exportDef: %s topology (%d,%s) not decoded', self, resId, atmName)
                    top2.append( (resId,atmName) )
                else:
                    atm = self.residueDef[atmName]
                    top2.append( (resId,atm.translate(convention)) )
                #end if
            #end for
            #print 'top2', top2

            #convert properties
            prop
        #end if
        fprintf( stream, "\t\t%s = %s\n", 'topology', repr(top2) )

        for attr in ['nameDict','aliases','pseudo','real','type','spinType','shift','hetatm','properties']:
            if self.has_key(attr):
                fprintf( stream, "\t\t%s = %s\n", attr, repr(self[attr]) )
        #end for

        fprintf( stream, '\tEND_ATOM\n')
#        fprintf( stream, '\t#---------------------------------------------------------------\n')
    #end def
#end class

class DihedralDef( NTtree ):
    def __init__( self, name, **kwds ):
        NTtree.__init__(   self,
                           __CLASS__   = 'DihedralDef',
                           convention  = INTERNAL,
                           name        = name,
                           residueDef  = None,
                           atoms       = [],    # List of atoms: (i, name) tuple
                                                # i:  -1=previous residue
                                                #      0=current residue
                                                #      1=next residue
                           karplus     = None   # Karplus parameters: (A,B,C,teta) tuple
                          )
        self.update( kwds )

        self.__FORMAT__ = '=== DihedralDef %(residueDef)s.%(name)s (%(convention)r) ===\n' +\
                          'atoms:   %(atoms)s\n' +\
                          'karplus: %(karplus)s'

#        self.saveXML( 'name', 'atoms', 'karplus' )
    #end def

    def exportDef( self, stream = sys.stdout, convention=INTERNAL ):
        "export definitions to stream"
        fprintf( stream, '\t#---------------------------------------------------------------\n')
        fprintf( stream, '\tDIHEDRAL %-8s\n',self.name)
        fprintf( stream, '\t#---------------------------------------------------------------\n')

        if convention == INTERNAL:
            atms = self.atoms
        else:
            # convert atoms
            atms = []
            for resId,atmName in self.atoms:
                if resId != 0:
                    NTwarning('DihedralDef.exportDef: %s topology (%d,%s) skipped translation', self, resId, atmName)
                    atms.append( (resId,atmName) )
                elif not atmName in self.residueDef:
                    NTerror('DihedralDef.exportDef: %s topology (%d,%s) not decoded', self, resId, atmName)
                    atms.append( (resId,atmName) )
                else:
                    atm = self.residueDef[atmName]
                    atms.append( (resId,atm.translate(convention)) )
                #end if
            #end for
            #print 'atms', atms
        #end if
        fprintf( stream, "\t\t%s = %s\n", 'atoms', repr(atms) )

        for attr in ['karplus']:
            fprintf( stream, "\t\t%s = %s\n", attr, repr(self[attr]) )
        #end for

        fprintf( stream, '\tEND_DIHEDRAL\n')
#        fprintf( stream, '\t#---------------------------------------------------------------\n')
    #end for
#end class

def changeProperty( obj, oldProperty, newProperty):
    """
    Change oldProperty in obj.properties list to newProperty
    """
    if not obj.has_key('properties'):
        return
    props = obj['properties']
    i = props.index(oldProperty)
    if i>=0:
        props[i] = newProperty
#end def


def importNameDefs( tableFile, name)   :
    "Import residue and atoms name defs from tableFile"

    NTdebug('==> Importing database file '+ tableFile )

    mol = MolDef( name = 'mol' )
    obj = mol # object point to 'active' object, mol, residue, dihedral or atom attributes get appended to obj.
    for r in AwkLike( tableFile ):
#            print '>',r.dollar[0]
        if r.isComment() or r.isEmpty():
            pass
        elif r.dollar[1] == 'RESIDUE':
            res = mol.appendResidue( name=r.dollar[2], shortName =r.dollar[3] )
            obj = res
        elif r.dollar[1] == 'END_RESIDUE':
            obj = mol
        elif r.dollar[1] == 'DIHEDRAL':
            dh = res.appendDihedral( name=r.dollar[2] )
            obj = dh
        elif r.dollar[1] == 'END_DIHEDRAL':
            obj = res
        elif r.dollar[1] == 'ATOM':
            atm = res.appendAtom( name=r.dollar[2] )
            obj = atm
        elif r.dollar[1] == 'END_ATOM':
            obj = res
        elif r.NF > 2:
#            NTmessage( '=> %s',repr(obj))
#             # Get a mol representing constructor
#              cname = obj._Cname( -1 ).split(".")
#              result= cname[0]
#              for a in cname[1:]:
#                  result = result +'[%s]' % (repr(a))
#              #end for
#              cmd = "%s[%s] %s " % (result,
#                                    repr(r.dollar[1].strip()),
#                                    "".join( r.dollar[2:] )
#                                   )
# #            NTmessage( ' >%s<',cmd )
#
##  19 Feb 2007: much simpler
#             cmd = "obj[%s] = %s " % (repr(r.dollar[1].strip()),
#                                      " ".join( r.dollar[3:] )
#                                     )
#
#            NTmessage( ' >%s<',cmd )
#             exec( cmd )
##  17 Sep 2007; even simpler
            obj[r.dollar[1]] = eval( " ".join( r.dollar[3:] ) )
        else:
            pass
        #endif
    #end for
    mol.name=name

    #Path the properties for duplicates
    for res in mol:
        p = []
        # Do it a dumb way (check and copy) to preserve order
        for prop in res.properties:
            if not prop in p:
                p.append(prop)
            #end if
        #end for
        res.properties = p
        for atm in res:
            p = []
            for prop in res.properties:
                if not prop in p:
                    p.append(prop)
                #end if
            #end for
            atm.properties = p
        #end for
    #end for
    return mol
#end def


path, fname, ext = NTpath( __file__ )
#print '>>', __file__, path
# import the database table and generate the db-tree
NTdb = importNameDefs( os.path.realpath(cingPythonCingDir + '/Database/dbTable'), name='NTdb')

# Use dictionaries for quick lookup.
# Note it does not include the carbonyl anymore. Just like molmol doesn't.
backBoneProteinAtomDict = { 'C':1,'N'  :1,'H'  :1,'HN' :1,'H1' :1,'H2':1,'H3':1,'CA':1,'HA':1,'HA1':1,'HA2':1,'HA3':1 }
backBoneNucleicAtomDict = { 'P':1,"O3'":1,"C3'":1,"C4'":1,"C5'":1,"O5'":1 } # skipping 'backbone protons'
# Patches for attributes
if patches:
    def isAromatic( atmDef ):
        """Return true if it is an atom belonging to an aromatic ring
           Patched for now, have to store it in database
        """
        if not atmDef.residueDef.hasProperties('aromatic'): return False

        if (isCarbon(atmDef) and atmDef.shift != None and atmDef.shift.average > 100.0):
            return True
        if (isNitrogen(atmDef) and atmDef.shift != None and atmDef.shift.average > 130.0):
            return True
        elif (isProton(atmDef)):
            if len(atmDef.topology) == 0: return False #bloody CYANA pseudo atomsof some residues like CA2P do not have a topology
            heavy = atmDef.residueDef[atmDef.topology[0][1]]
            return isAromatic( heavy )
        #end if
        return False
    #end def

    def isBackbone( atmDef ):
        """
        Return True if it is a backbone atom.
        Patch for now, based upon explicit enumeration
        """
        if atmDef.residueDef.hasProperties('protein') and \
           backBoneProteinAtomDict.has_key( atmDef.name ):
                return True
        if atmDef.residueDef.hasProperties('nucleic') and \
           backBoneNucleicAtomDict.has_key( atmDef.name ):
                return True
        return False

    def isSidechain( atmDef ):
        """
        Return True if it is a sidechain atom,
        i.e. not isBackbone
        """
        return not isBackbone( atmDef )

    def isMethyl( atmDef ):
        """
        Return True atm is a methyl (either carbon or proton)
        """
        if isCarbon(atmDef):
            count = 0
            for dummy,p in atmDef.topology:
                if p in atmDef.residueDef and isProton( atmDef.residueDef[p] ):
                    count += 1
                #end if
            #end for
            return (count == 3) # Methyls have three protons!
        elif isProton(atmDef):
            # should be attched to a heavy atomo
            if len(atmDef.topology) == 0: return False #bloody CYANA pseudo atomsof some residues like CA2P do not have a topology
            heavy = atmDef.residueDef[atmDef.topology[0][1]]
            return isMethyl( heavy )
        else:
            return False
        #end if
    #end def

    def isMethylProton( atmDef ):
        """
        Return True if atm is a methyl proton
        """
        return isProton(atmDef) and isMethyl(atmDef)
    #end def

    def isProton( atmDef ):
        """Return Tue if atm is 1H
        """
        return (atmDef.spinType == '1H')
    #end def

    def isCarbon( atmDef ):
        """Return Tue if atm is 13C
        """
        return (atmDef.spinType == '13C')
    #end def

    def isNitrogen( atmDef ):
        """Return Tue if atm is 15N
        """
        return (atmDef.spinType == '15N')
    #end def

    def isSulfur( atmDef ):
        """Return Tue if atm is 32S
        """
        return (atmDef.spinType == '32S')
    #end def

    def isPseudoAtom( atmDef ):
        """Return True if atom is pseudoAtom"""
        return ( len(atmDef.real) > 0 )
    #end def

    def hasPseudoAtom( atmDef ):
        """Return True if atom has a correponding pseudoAtom"""
        return ( atmDef.pseudo != None )
    #end def

    for atmDef in NTdb.subNodes( depth = 2 ):
        props = NTlist( atmDef.name, atmDef.residueDef.name, atmDef.residueDef.shortName, atmDef.spinType, *atmDef.properties)

        if isProton(atmDef):
            props.append('isProton','proton')
        else:
            props.append('isNotProton','notproton')
        #end if
        if isCarbon(atmDef):
            props.append('isCarbon','carbon')
        else:
            props.append('isNotCarbon','notcarbon')
        #end if
        if isNitrogen(atmDef):
            props.append('isNitrogen','nitrogen')
        else:
            props.append('isNotNitrogen','notnitrogen')
        #end if
        if isSulfur(atmDef):
            props.append('isSulfur','isSulphur','sulfur','sulphur')
        else:
            props.append('isNotSulfur','isNotSulphur','notsulfur','notsulphur')
        #end if
        if isBackbone(atmDef):
            props.append('isBackbone','backbone')
        else:
            props.append('isSidechain','sidechain')
        #endif
        if isAromatic(atmDef):
            props.append('isAromatic','aromatic')
        else:
            props.append('isNotAromatic','notaromatic')
        #end if
        if isMethyl(atmDef):
            props.append('isMethyl','methyl')
        else:
            props.append('isNotMethyl','notmethyl')
        #end if
        if isMethylProton(atmDef):
            props.append('isMethylProton','methylproton')
        else:
            props.append('isNotMethylProton','notmethylproton')
        #end if
        if isPseudoAtom(atmDef):
            props.append('isPseudoAtom','pseudoatom')
        else:
            props.append('isNotPseudoAtom','notpseudoatom')
        #end if
        if hasPseudoAtom(atmDef):
            props.append('hasPseudoAtom','haspseudoatom')
        else:
            props.append('hasNoPseudoAtom','hasnopseudoatom')
        #end if

        atmDef.properties = props

        #print atmDef, atmDef.properties
#end if

