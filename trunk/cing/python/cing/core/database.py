from cing.core.constants import INTERNAL
from cing.Libs.AwkLike import AwkLike
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTdict # Used by obj[r.dollar[1]] = eval( " ".join( r.dollar[3:] ) ) @UnusedImport
from cing.Libs.NTutils import NTtree
from cing.Libs.NTutils import fprintf
from cing import cingPythonCingDir
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import NTerror

import os
import sys

patches = False

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

    def allResidueDefs(self):
        return self.subNodes( depth = 1 )
    #end def

    def allAtomDefs(self):
        return self.subNodes( depth = 2 )
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
        for atm in self.allAtomDefs():
            if atm.hasProperties(*properties):
                result.append(atm)
            #end if
        #end for
        return result
    #end def

    def exportDef( self, stream = sys.stdout, convention=INTERNAL ):
        "export name definitions to stream"
        fprintf(stream,'convention = %r\n', convention)
        for res in self:
            res.exportDef( stream=stream, convention=convention )
        #end for
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

    def allResidueDefs(self):
        return self
    #end def

    def allAtomDefs(self):
        return self.subNodes( depth = 1 )
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

    def postProcess(self):
        """
        Any post-reading actions
        """
        # Add name and shortName; Remove the duplicates;
        props2 =  [self.name, self.shortName]
        for prop in self.properties:
            if not prop in props2:
                props2.append(prop)
            #end if
        #end for
        self.properties = props2
    #end def

    def exportDef( self, stream = sys.stdout, convention = INTERNAL ):
        "export definitions to stream"
        fprintf( stream, '\n#=======================================================================\n')
        fprintf( stream,   '#\t%-8s %-8s\n','internal', 'short')
        fprintf( stream,   'RESIDUE\t%-8s %-8s\n', self.translate(convention), self.shortName )
        fprintf( stream,   '#=======================================================================\n')

        # saving different residue attributes
        for attr in ['nameDict', 'comment']:
            fprintf( stream, "\t%s = %s\n", attr, repr(self[attr]) )
        #end for

        # clean the properties list
        props = []
        for prop in self.properties:
            # Do not store name and residueDef.name as property. Add those dynamically upon reading
            if not prop in [self.name, self.shortName] and not prop in props:
                props.append(prop)
            #end if
        #end for
        fprintf( stream, "\t%s = %s\n", 'properties', repr(props) )

        for dh in self.dihedrals:
            dh.exportDef( stream=stream, convention=convention )
        #end for

        for atm in self.atoms:
            atm.exportDef( stream=stream, convention=convention )
        #end for

        fprintf( stream,   'END_RESIDUE\n')
        fprintf( stream,   '#=======================================================================\n')
    #end def
#end class

# Use dictionaries for quick lookup.
# Note it does not include the carbonyl anymore. Just like molmol doesn't.
backBoneProteinAtomDict = { 'C':1,'N'  :1,'H'  :1,'HN' :1,'H1' :1,'H2':1,'H3':1,'CA':1,'HA':1,'HA1':1,'HA2':1,'HA3':1 }
backBoneNucleicAtomDict = { 'P':1,"O3'":1,"C3'":1,"C4'":1,"C5'":1,"O5'":1 } # skipping 'backbone protons'

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

    def __str__(self):
        return '<AtomDef %s.%s>' % (self.residueDef.name, self.name)

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

    def allAtomDefs(self):
        return self
    #end def

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

    def postProcess(self):
        """
        Any post-reading actions
        """
        props = NTlist( self.name, self.residueDef.name, self.residueDef.shortName, self.spinType, *self.properties)

        # Append these defs so we will always have them. If they were already present, they will be removed again below.
        if isProton(self):
            props.append('isProton','proton')
        else:
            props.append('isNotProton','notproton')
        #end if
        if isCarbon(self):
            props.append('isCarbon','carbon')
        else:
            props.append('isNotCarbon','notcarbon')
        #end if
        if isNitrogen(self):
            props.append('isNitrogen','nitrogen')
        else:
            props.append('isNotNitrogen','notnitrogen')
        #end if
        if isSulfur(self):
            props.append('isSulfur','isSulphur','sulfur','sulphur')
        else:
            props.append('isNotSulfur','isNotSulphur','notsulfur','notsulphur')
        #end if
        if isBackbone(self):
            props.append('isBackbone','backbone')
        else:
            props.append('isSidechain','sidechain')
        #endif
        if isAromatic(self):
            props.append('isAromatic','aromatic')
        else:
            props.append('isNotAromatic','notaromatic')
        #end if
        if isMethyl(self):
            props.append('isMethyl','methyl')
        else:
            props.append('isNotMethyl','notmethyl')
        #end if
        if isMethylProton(self):
            props.append('isMethylProton','methylproton')
        else:
            props.append('isNotMethylProton','notmethylproton')
        #end if
        if isPseudoAtom(self):
            props.append('isPseudoAtom','pseudoatom')
        else:
            props.append('isNotPseudoAtom','notpseudoatom')
        #end if
        if hasPseudoAtom(self):
            props.append('hasPseudoAtom','haspseudoatom')
        else:
            props.append('hasNoPseudoAtom','hasnopseudoatom')
        #end if

        # Remove the duplicates; copy is much quicker then in-place props.removeDuplicates()
        props2 =  []
        for prop in props:
            if not prop in props2:
                props2.append(prop)
            #end if
        #end for
        self.properties = props2

        #Add aliases
        for aname in self.aliases:
            self.residueDef[aname] = self
    #end def

    def exportDef( self, stream = sys.stdout, convention=INTERNAL ):
        "export definitions to stream"
        fprintf( stream, '\t#---------------------------------------------------------------\n')
        fprintf( stream, '\tATOM %-8s\n',self.translate(convention))
        fprintf( stream, '\t#---------------------------------------------------------------\n')

        # Topology; optionally convert
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
        #end if
        fprintf( stream, "\t\t%s = %s\n", 'topology', repr(top2) )

        # clean the properties list
        props = []
        for prop in self.properties:
            # Do not store name and residueDef.name as property. Add those dynamically upon reading
            if not prop in [self.name, self.residueDef.name, self.residueDef.shortName, self.spinType] and not prop in props:
                props.append(prop)
            #end if
        #end for
        fprintf( stream, "\t\t%s = %s\n", 'properties', repr(props) )

        # Others
        for attr in ['nameDict','aliases','pseudo','real','type','spinType','shift','hetatm']:
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

    def __str__(self):
        return '<DihedralDef %s.%s>' % (self.residueDef.name, self.name)

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


def importNameDefs( tableFile, name)   :
    "Import residue and atoms name defs from tableFile"

    NTdebug('==> Importing database file '+ tableFile )

    mol = MolDef( name = 'mol' )
    obj = mol # object point to 'active' object (i.e. mol, residue, dihedral or atom); attributes get appended to obj.
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

    if mol.convention != INTERNAL:
        NTerror('Reading databse: current convention setting (%s) does not match database file "%s" (%s)',
                INTERNAL, tableFile, mol.convention
               )
        sys.exit(1)

    #Post-processing
    for res in mol.allResidueDefs():
        res.postProcess()
    for atm in mol.allAtomDefs():
        atm.postProcess()

    return mol
#end def


#path, fname, ext = NTpath( __file__ )
#print '>>', __file__, path
# import the database table and generate the db-tree
NTdebug('importing NTdb')
NTdebug( '>' + INTERNAL )
NTdb = importNameDefs( os.path.realpath(cingPythonCingDir + '/Database/dbTable.' + INTERNAL), name='NTdb')





