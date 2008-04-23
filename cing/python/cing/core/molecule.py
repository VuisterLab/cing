from cing.Libs import PyMMLib
from cing.Libs.AwkLike import AwkLikeS
from cing.Libs.NTutils import NTcodeerror
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTset
from cing.Libs.NTutils import NTtree
from cing.Libs.NTutils import NTvalue
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import XML2obj
from cing.Libs.NTutils import XMLhandler
from cing.Libs.NTutils import angle3Dopt
from cing.Libs.NTutils import asci2list
from cing.Libs.NTutils import cross3Dopt
from cing.Libs.NTutils import fprintf
from cing.Libs.NTutils import length3Dopt
from cing.Libs.NTutils import obj2XML
from cing.Libs.NTutils import quote
from cing.Libs.NTutils import removedir
from cing.Libs.NTutils import sprintf
from cing.Libs.PyMMLib import ATOM
from cing.Libs.PyMMLib import HETATM
from cing.Libs.PyMMLib import PDBFile
from cing.Libs.cython.vector  import Vector #@UnresolvedImport
from cing.core.constants import COLOR_GREEN
from cing.core.constants import CYANA
from cing.core.constants import CYANA2
from cing.core.constants import CYANA_NON_RESIDUES
from cing.core.constants import INTERNAL
from cing.core.constants import IUPAC
from cing.core.constants import LOOSE
from cing.core.constants import NOSHIFT
from cing.core.constants import UNDEFINED_FLOAT
from cing.core.constants import XPLOR
from cing.core.dictionaries import translateAtomName
from cing.core.dictionaries import translateResidueName
from database     import NTdb
from parameters   import plotParameters
import math
import os

#==============================================================================
# Global variables
#==============================================================================
AtomIndex = 1

NTmolParameters = NTdict(
    version        = 0.9,
    contentFile    = 'content.xml',
    sequenceFile   = 'sequence.dat',
    resonanceFile  = 'resonances.dat',
    coordinateFile = 'coordinates.dat',
)

dots = '-----------'
#==============================================================================
class Molecule( NTtree ):
    """
-------------------------------------------------------------------------------
Molecule class: defines the holder for molecule items.

Mapping between the CING data model and NMR-STAR:

CING     | NMR-STAR             CCPN
--------------------------------
Molecule | Molecular system     MolSystem (from ccp.api.molecule.MolSystem)
Chain    | Assembly entity      Chain
Residue  | Chemical component   Residue

There are things that will be difficult to map from one to the other.
A Zinc ion will usually be part of the same chain in CING whereas it will be
in a different assembly entity in NMR-STAR. This has consequences for numbering.
-------------------------------------------------------------------------------
    
                                     Coordinate
                                       ^
                                       |
                                       v
  Molecule <-> Chain <-> Residue <-> Atom <-> Resonance <- Peak
                            |          |
                            v          v
              NTdb <-> ResidueDef <-> AtomDef
  _____________________________________________________________________________
                  
    Molecule.chains     List of Chain instances; equivalent to Molecule._children
    
    Chain.molecule      Parent Molecule instance
    Chain.residues      List of Residue instances; equivalent to Chain._children
  
    Residue.chain       Parent Chain instance
    Residue.atoms       List of Atom instances; equivalent to Residue._children
    Residue.db          Points to database ResidueDef instance
  
    Atom.residue        Parent Residue instance
    Atom.resonances     List of Resonances instances
    Atom.coordinates    List of Coordinate instances
    Atom.db             Points to database AtomDef instance
  
    Resonance.atom      Points to Atom instance 
  
    Coordinate.atom     Points to Atom instance 

    Peak.resonances     List of Resonance instances 
                        corresponding with dimensions of peak
  _____________________________________________________________________________

    Initiating attributes:
        name                    : Molecule name
      
    Derived attributes:
        chains                  : NTlist of Chain instances (identical to _children)
        residueCount            : Number of Residue instances
        chainCount              : Number of Chain instances
        
    Attributes inherited from NTtree:
        _parent                 : None
        _children               : NTlist of children NTtree instances.
 
    Methods:
        allChains()             : Returns a list of all chains objects of molecule.
        allResidues()           : Returns a list of all residue objects of molecule.
        allAtoms()              : Returns a list of all atom objects of molecule.
        
    Methods inherited from NTtree:
        _Cname( depth )         : Returns name expanded to depth
        addChild( child )       :
        sibling( relativeIndex ) :
        traverse()              :
        
    Methods inherited from NTdict:
        format()                : Return a formatted string of with values of selected fields.
        getAttr()       : Print a list of all attributes and their values.
        
    all dict methods
          
 """
  
    def __init__( self, name, **kwds ):
        NTtree.__init__(self, name, __CLASS__='Molecule', **kwds )

        self.__FORMAT__ =  self.header( dots ) + '\n' +\
                          'chains:     %(chainCount)d %(chains)s\n' +\
                          'residues:   %(residueCount)d\n' +\
                          'atoms:      %(atomCount)d\n' +\
                          'resonances: %(resonanceCount)d per atom\n' + \
                          'models:     %(modelCount)d\n' +\
                           self.footer( dots )
                          
        self.chains       = self._children
        self.chainCount   = 0
        self.residueCount = 0
        self.atomCount    = 0
        
        self.resonanceCount = 0

        self.modelCount   = 0
        
        self.xeasy        = None # reference to xeasy class, used in parsing

        self.saveXML('chainCount','residueCount','atomCount')

        NTdebug(self.format() )
        #end if
    #end def
    
    def __str__(self):
        return sprintf('<Molecule "%s" (C:%d,R:%d,A:%d,M:%d)>',
            self.name,self.chainCount,self.residueCount,self.atomCount,self.modelCount)
    #end def
    
    def __repr__(self):
        return str(self)
    #end def

    def setAllChildrenByKey(self, key, value):
        "Set chain,res, and atom children's keys to value"
        for chain in self.allChains():
            chain[key] = value
        for res in self.allResidues():
            res[key] = value
        for atm in self.allAtoms():
            atm[key] = value

    def getChainIdForChainCount(self):
        return Chain.DEFAULT_ChainNamesByAlphabet[ self.chainCount ]
        
    def addChain( self, name=None, **kwds ):
        """
            Add Chain instance name
           or 
           pick next chain identifier when chain=None
           
           Return Chain instance or None upon error
        """
#       We have to make sure that whatever goes on here is also done in the XML handler
        if name==None:
            name = self.getChainIdForChainCount()
        if name in self:
            NTerror( 'ERROR Molecule.addChain: chain "%s" already present\n', name )
            return None
        #end if
        chain = Chain( name=name, **kwds )
        self._addChild( chain )
        chain.molecule = self
        self.chainCount += 1
        return chain
    #end def

    def allChains( self ):
        """Returns a list of all chains of molecule"""
        return self.subNodes( depth = 1 )
    #end def    

    def allResidues( self ):
        """Returns a list of all residues of molecule"""
        return self.subNodes( depth = 2 )
    #end def
    
    def allAtoms( self ):
        """Returns a list of all atoms of molecule"""
        return self.subNodes( depth = 3 )
    #end def  
    
    def decodeNameTuple( self, nameTuple ):
        """
            Decode a (convention, chainName, resNum, atomName) tuple
            generated with the nameTuple methods of Chain, Residue, or Atom Classes.
            Return a Molecule, Chain, Residue or Atom instance on success or
            None on error.

            If no chain is given then the whole molecule is returned.
            If no residue is given then the whole chain is returned.
            ..etc..
            Caller is responsible for relaying error messages but debug
            statements within can be enabled from code.
        """
#        NTdebug("Now in decodeNameTuple for : "  + `nameTuple`)
        convention, chainName, resNum, atomName = nameTuple

        if chainName == None:
            return self
        # has_key is faster perhaps as "in" iterates whereas has_key uses true dictionary lookup.
#        if not chainName in self:
        if not self.has_key(chainName):
#            NTdebug( 'in molecule decodeNameTuple: in molecule ['+self.name+'] no chain Name: ['+chainName+']')
            return None
        
        chain = self[chainName]
        
        if resNum == None:
            return chain

        if not chain.has_key(resNum):
#            NTdebug( 'in molecule decodeNameTuple: in chain ['+`chain`+'] no residue number: ['+`resNum`+']')
            return None
        res = chain[resNum]

        if atomName == None:
            return res
        
        resTranslated = res.translate(convention)
        an = translateAtomName( convention, resTranslated, atomName, INTERNAL )
#        if (not an or (an not in res)): return None
        if not an:
#            NTdebug("in Molecule.decodeNameTuple failed to translateAtomName for res: " + resTranslated + " and atom: " + atomName)
            return None

        if not res.has_key(an):
#            NTdebug("in Molecule.decodeNameTuple atom not in residue: [%s]" % `an`)
            return None
        return res[an]
    #end def

    def getResidue( self, resName, chains = None):
        """
        Return Residue instances corresponding to Name, or None if not
           found. Search all chains when chains = None
        """
        if not chains:
            chains = self.chains
        #end if

        # loop through all the chains until found
        for chain in chains:
            if resName in chain:
                return chain[resName]
            #end if
        #end for
        return None
    #end def 
    
    
    def ranges2list( self, ranges ):
        """
            Convert
              either a residue ranges string, e.g. '10-20,34,50-60', 
              or a list with residue number or residue instances,
              or None,
              
           to a NTlist instance with residue objects.
           
           Return the list or None upon error.
            When the input for ranges is None then the output will be all residues.
        """
        if ranges == None:
            return self.allResidues()
            
        if type(ranges) == str:
            # self.allResidues() is a list of NTtree with residue instances
            # .zap('resNum') returns the items collapsed by residue number
            # if two residues in the same chain have the same residue number then
            #  the resulting list will have the one of the 2 residues in there
            #  twice; which is a bug JFD thinks.
            resnumDict = dict(zip(self.allResidues().zap('resNum'), self.allResidues()))
            ranges =  asci2list(ranges)
            ranges.sort()
            result = NTlist()
            for resNum in ranges:
                if resnumDict.has_key(resNum):
                    result.append(resnumDict[resNum])
                else:
                    NTerror('Error Molecule.ranges2list: invalid residue number [%d]\n', resNum )
            return result
            
        if isinstance( ranges, list ):
            resnumDict = dict(zip(self.allResidues().zap('resNum'), self.allResidues()))
            result = NTlist()
            for item in ranges:
                if isinstance( item, int ):
                    if resnumDict.has_key(item):
                        result.append(resnumDict[item])
                    else:
                        NTerror('Error Molecule.ranges2list: invalid residue number [%d]\n', resNum )
                elif isinstance( item, Residue ):
                    result.append( item )
                else:
                    NTerror('Error Molecule.ranges2list: invalid item [%s] in ranges list\n', item )
            return result
                
        NTerror('Error Molecule.ranges2list: undefined ranges type [%s]\n', type(ranges) )
        return None
        
    def getFixedRangeList( self, max_length_range = 50, ranges=None ):
        """Return a list of NTlist instance with residue objects.
        The NTlist contains only residues in the given ranges and is at most
        max_length_range long.
        """
        selectedResidues = self.allResidues()
        if ranges:
            selectedResidues = self.ranges2list( ranges )
        r = NTlist()
        result = []
        for res in selectedResidues:
            if len(r) == max_length_range:
                result.append( r )
                r = NTlist()
            r.append(res)
        if r:
            result.append(r)
        return result

    
    
    def models2list( self, models ):
        """
            Convert
              either a models string, e.g. '0,3,5,6-19 
              or a list with model numbers,
              or None,
              
           to a NTlist instance with model numbers.
           
           Returns empty list if modelCount == 0, 
           Returns the list or None upon error.

            Note that model number start at zero .
        """
        if models == None:
            return NTlist( *range(self.modelCount))
            
        if self.modelCount == 0:
            return NTlist()
            
        if type(models) == str:
            models = asci2list(models)
            models.sort()
            result = NTlist()
            for model in models:
                if model < 0:
                    NTerror('Error Molecule.models2list: invalid model number %d (below zero)\n', model )
                    return None
                if model >= self.modelCount:
                    NTerror('Error Molecule.models2list: invalid model number %d (larger than modelCount: %d)\n',
                            (model, self.modelCount ))
                    return None
                result.append(model)
            #end for
            result.sort()
            return result
            
        if isinstance( models, list ):
            models.sort()
            result = NTlist()
            for model in models:
                if not isinstance( model, int):
                    NTerror('Error Molecule.models2list: invalid model "%s" in models list\n', model )
                    return None
                if model < 0:
                    NTerror('Error Molecule.models2list: Invalid model number %d (below zero)\n', model )
                    return None
                if model >= self.modelCount:
                    NTerror('Error Molecule.models2list: Invalid model number %d (larger than modelCount: %d)\n',
                                (model, self.modelCount ))
                    return None
                result.append(model)
            #end for
            return result
        NTerror('Error Molecule.ranges2list: undefined models type %s\n', type(models) )
        return None
    #end def  
    
          
    def save( self, path = None)   :
        """Create a directory path (or use name.NTmol)
           Save sequence, resonances and coordinates so it can be restored by 
           restore.
        """
        if not path: path = self.name + '.NTmol'
        if os.path.exists( path ): removedir( path )
        os.mkdir( path )
        
        content = NTdict( name = self.name, convention = INTERNAL )
        content.update( NTmolParameters )
        content.saveAllXML()        
        obj2XML( content, path=os.path.join( path, NTmolParameters.contentFile ) )
        
        self.saveSequence(    os.path.join( path, NTmolParameters.sequenceFile   ) )
        self.saveResonances(  os.path.join( path, NTmolParameters.resonanceFile  ) )
        self.saveCoordinates( os.path.join( path, NTmolParameters.coordinateFile ) )
        
        NTmessage('==> Saved %s to "%s"', self, path)
        #end if
    #end def
    
    def open( path)   :
        """Static method to restore molecule from directory path 
           return self or None on error
        """
        if (not os.path.exists( path )): 
            NTerror('Molecule.open: path "%s" not found\n', path)
            return None
        #end if
        
        content = XML2obj( path=os.path.join( path, NTmolParameters.contentFile ) ) 
        if not content:
            NTerror('Molecule.open: error reading contentFile "%s"\n',
                     os.path.join( path, NTmolParameters.contentFile )
                   )
            return None
        #end if

        NTmessage('==> Restoring Molecule from "%s" ... ', path )
     
        
        mol = Molecule( name = content.name )
        if not mol:
            NTerror('Molecule.open: initializing molecule\n')
            return None
        #end if
        
        mol.restoreSequence(    os.path.join( path, content.sequenceFile   ) )
        mol.restoreResonances(  os.path.join( path, content.resonanceFile  ), append=False )
        mol.restoreCoordinates( os.path.join( path, content.coordinateFile ), append=False )

        mol.updateAll(   )
       
        NTmessage('%s', mol.format())

        return mol
    #end def
    open = staticmethod(open)
    
    def saveSequence( self, fileName ):
        """Write a plain text-file with code to generate sequence
        """
        fp = open( fileName, 'w' )
        for res in self.allResidues():
            fprintf( fp, 'self._addResidue( %s, %s, %d, "CYANA" )\n', 
                          quote(res.chain.name), 
                          quote(res.db.translate(CYANA)), 
                          res.resNum 
                   )
        #end for
        fp.close()
    #end def
    
    def restoreSequence( self, sequenceFile ):
        if (not os.path.exists( sequenceFile ) ):
            NTerror('Molecule.restoreSequence: sequenceFile "%s" not found\n',
                     sequenceFile
                   )
            return None        
        #end if
        #execfile( sequenceFile )            
        # 25 Sep 2007: Explicit coding, less memory, better:
        file = open(sequenceFile, 'r')
        for line in file:
             exec(line)
        #end for
        file.close()
    #end def
    
    def saveResonances( self, fileName ):
        """Write a plain text file with code for saving resonances
        """
        fp = open( fileName, 'w' )
        fprintf( fp, 'self.resonanceCount = %d\n', self.resonanceCount )
        for atm in self.allAtoms():
            for r in atm.resonances:
                fprintf( fp, 'self%s.addResonance( value=%s, error=%s )\n', 
                              atm._Cname2( 2 ),
                              repr(r.value), repr(r.error) 
                       )
            #end for
        #end for
        fp.close()
    #end def
    
    def restoreResonances( self, fileName, append = True ):
        """Restore resonances from fileName
           Optionally append to existing settings
           Return resonanceCount or None on error
        """
        if not os.path.exists( fileName ):
            NTerror('Error Molecule.restoreResonances: file "%s" not found\n', fileName )
            return None
        #end if
        if not append:
            self.initResonances(   )
        #end if
        
        #execfile( fileName )
        # 25 Sep 2007: Explicit coding, less memory, better:
        file = open(fileName, 'r')
        for line in file:
             exec(line)
        #end for
        file.close()

        return self.resonanceCount
    #end def
    
    def newResonances( self ):
        """Initialize a new resonance slot for every atom.
           atom.resonances() will point to this new resonance.
        """
        for atom in self.allAtoms():
            atom.addResonance( value=NOSHIFT, error = 0.000 )
        #end for
        self.resonanceCount += 1                
    #end def
    
    def initResonances( self)   :
        """ Initialize resonances for all the atoms            
        """
        for atom in self.allAtoms():
            atom.resonances = NTlist()
        #end for
        self.resonanceCount = 0                
        NTmessage("==> Initialized resonances")
        #end if
    #end def
    
    def saveCoordinates( self, fileName ):
        """Write a plain text file with code for saving coordinates"""
        fp = open( fileName, 'w' )
        fprintf( fp, 'self.modelCount = %d\n', self.modelCount )
        for atm in self.allAtoms():
            for c in atm.coordinates:
                fprintf( fp, 'self%s.addCoordinate( %r, %r, %r, Bfac=%r )\n',
                              atm._Cname2( 2 ), c[0], c[1], c[2], c.Bfac)
        fp.close()
    
    def restoreCoordinates( self, fileName, append = True ):
        """Restore coordinates from fileName
           Optionally append to existing settings
           Return self or None on error
        """
        if not os.path.exists( fileName ):
            NTerror('Error Molecule.restoreCoordinates: file "%s" not found\n', fileName )
            return None
        #end if
        if not append:
            for atm in self.allAtoms():
                atm.coordinates = NTlist()
            #end for
        #end if
        #execfile(fileName); 
        # 25 Sep 2007: Explicit coding, less memory, better:
        file = open(fileName, 'r')
        for line in file:
             exec(line)
        #end for
        file.close()
        return self           
    #end def
    
    def updateDihedrals( self)   :
        """Calculate the dihedral angles for all residues         
        """
        if self.modelCount <= 0:
            NTmessage('==> No models so skipping calculating dihedral angles ... ')
            return
        NTmessage('==> Calculating dihedral angles ... ')
        self.dihedralDict = {} # will be filled by calling dihedral method of residue
        for res in self.allResidues():
            for dihedral in res.db.dihedrals:
                res.dihedral( dihedral.name )
 
    def updateMean( self)   :
        """Calculate mean coordinates for all atoms         
        """
        if self.modelCount:
            NTmessage('==> Calculating mean coordinates ... ')
        for atm in self.allAtoms():
            atm.meanCoordinates()
   
    def updateAll( self)   :
        """Calculate the dihedral angles for all residues
           Calculate mean coordinates for all atoms         
        """
        if self.modelCount > 0:
            self.updateDihedrals(   )
            self.updateMean(   )
        #end if
    #end def

    #--------------------------------------------------------------------------
    def initialize( name, path = None, convention=LOOSE   ):

        """
Static method to initialize a Molecule from a file 
Return an Molecule instance or None on error
         
       fromFile:  File ==  <resName1 [resNum1] [chainId1]
                            resName2 [resNum2] [chainId2]
                            ...
                           >
        """  
        #print '>', path, convention
        molecule = Molecule( name=name )
        
        sequenceS = ''
        if path:
            if (not os.path.exists( path )):
                NTerror('Molecule.initialize: File "%s" not found\n', path)
                return None
            #end if
            f = open( path, mode = 'r' )
            sequenceS = f.read()
            f.close()
        #end if 

        resNum = 1
        for f in AwkLikeS( sequenceS, minNF = 1, commentString = '#' ):
            resName = f.dollar[1]
            
            if ( (convention == CYANA or convention == CYANA2) and
                 resName in CYANA_NON_RESIDUES         # skip the bloody CYANA non-residue stuff
               ):
               pass
               
            else:
                if f.NF > 1:
                    resNum = f.int(2) 
                #end if
            
                chainId = Chain.defaultChainId # recommended to use your own instead of CING making one up.
                if f.NF >= 3:
                    chainId = f.dollar[3]
                chainId = ensureValidChainId( chainId )
            
                molecule._addResidue( chainId, resName, resNum, convention )
        NTmessage("%s", molecule.format())
        return molecule
    #end def    
    initialize = staticmethod( initialize )
    
    def _addResidue( self, chainId, resName, resNum, convention ):
        """
        Internal routine to add a residue to molecule
           return Residue or None or error
        """
        rn = translateResidueName( convention, resName, INTERNAL )
        if (rn == None):
            NTerror('Molecule._addResidue: chain %s, residue "%s" not valid for convention "%s"\n',
                     chainId, resName, convention
                   )
            return None
        else:
            if chainId == None:
                chainId = Chain.defaultChainId

            if chainId not in self:
                chain = self.addChain(chainId)
            else:
                chain = self[chainId]
            #end if
            if not chain: return None
            
            # Add the residue
            if resNum in chain:
                return chain[resNum]
            #end if
            residue = chain.addResidue( rn, resNum )
            if not residue: return None
            
            # Use database to add atoms
            residue.addAllAtoms()
        #end if
        return residue
    #end def
    
    def residuesWithProperties(self, *properties ):
        """
        Return a NTlist instance with Residues that have properties
        """  
        result = NTlist()
        
        if len(properties) == 0: return result
        for res in self.allResidues():
            if res.hasProperties(*properties):
                result.append(res)
            #end if
        #end for
        return result
    #end def
    
    def atomsWithProperties(self, *properties ):
        """
        Return a NTlist instance with Atoms that have properties
        """  
        result = NTlist()
        
        if len(properties) == 0: return result
        for atm in self.allAtoms():
            if atm.hasProperties(*properties):
                result.append(atm)
            #end if
        #end for
        return result
    #end def
    
    def toPDB( self, model = None, convention = IUPAC   ):
        """
        Return a PyMMlib PDBfile instance or None on error
        Format names according to convention
        Only export model if specified.
        Note that the first model is model numbered zero.
        Return None on error or pdbfile object on success.
        """
        
        if self.modelCount == 0:
            NTerror("modelCount is zero in Molecule instance: " + `self`)
            return None
        
        if model==None:
            models = NTlist(*range( self.modelCount ))
        else:
            if model<0:
                NTerror("model number is below zero in Molecule instance: " + `self` + " and model number: " + model)
                return None
            if model >= self.modelCount:
                NTerror("model number is larger than modelCount in Molecule instance: " + `self`)
                return None
            models = NTlist( model )
        
        NTmessage("==> Exporting to PDB file (%s convention, models: %d-%d) ... ", 
                   convention, models[0], models.last()                 )
        
        pdbFile = PDBFile()
     
        record = PyMMLib.REMARK()
        record.text = sprintf('PDB file of molecule %s', self.name )
        pdbFile.append( record )
            
        for m in models:
            if len(models) > 1:
                record = PyMMLib.MODEL()
                record.serial = m + 1 # only now change to a model number that starts at one.
                pdbFile.append( record )
            #end if
            
            atmCount = 1
            for chain in self.allChains():
                lastAtm = None
                for atm in chain.allAtoms():
                    atm.setdefault('pdbSkipRecord',False)
                    if atm.pdbSkipRecord:
                        continue
                    record = atm.toPDB( pdbIndex=atmCount, model=m, convention=convention )
                    if not record:
                        # this happens for all Q and even for like Cys HG which aren't always present in actual structure
                        # but are defined in db.
#                        NTwarning("Failed to get PDB atom record for atom: " + `atm`)
                        continue
                    pdbFile.append( record )
                    atmCount += 1
                    lastAtm = atm
                #end for
                if lastAtm and convention != XPLOR:
                    record = lastAtm.toPDBTER( pdbIndex=atmCount, convention=convention )
                    pdbFile.append( record )
                    atmCount += 1
                #end if
            #end for

            if len(models) > 1:
                record = PyMMLib.ENDMDL()
                pdbFile.append( record )
            #end for

        #end for
        record = PyMMLib.END()
        pdbFile.append( record )
        return pdbFile
    #end def
#end class      

class XMLMoleculeHandler( XMLhandler ):
    """Molecule handler class"""
    def __init__( self ):
        XMLhandler.__init__( self, name='Molecule') 
    #end def
    
    def handle( self, node ):
        attrs = self.handleDictElements( node )
        if attrs == None: return None
        result = Molecule( name = attrs['name'] )

        # update the attrs values
        result.update( attrs )
            
        # restore the tree structure
        for child in result._children:
#           print '>child>', repr(child)
            result[child.name] = child
            child._parent = result
        return result
    #end def
#end class

#register this handler
moleculehandler = XMLMoleculeHandler()

#      
#==============================================================================
#           

def ensureValidChainId( chainId ):
    """
    In CING all chains must have one non-space character (chain id) because:

    - More than 1 characters would not fit in PDB column 22. Note that
    some programs read the chain id from PDB columns [73-76> but others
    programs (e.g. SHIFTX, ???) used by CING do not.
    In the future, the CING code could be extended to interface
    to these programs but for now CING uses the lowest common denominator.
    - No space allowed because it does not materialize to a nice file name,
    one that can be used without quotes. If the value is a space it is hard to
    pass this to some programs; such as SHIFTX. A space would also be
    making it impossible to CING to use e.g.:
    print project.molecule.A.GLU77.procheck.CHI1[0]
    where A stands for chain id A.
    - The letters A-Z are often used already which will cause name space
    collisions. It is important to choose an id that will most likely not be
    used in the above formats.

    The chain id is ALWAYS given in PDB and XPLOR coordinate files.
    It might be a space character but it's always implicitly present. If it's a
    space character, CING will translate it to the defaultChainId value.

    Bottom line: use a chain id character on input!
    """
    if chainId==None:
        return Chain.defaultChainId
    if len(chainId) > 1:
        chainId = chainId[0]
    chainId = chainId.upper()
    charOrd = ord(chainId)
    if charOrd >= ord('A') and charOrd <= ord('Z'):
        return chainId
    if chainId in Chain.validChainIdListBesidesTheAlphabet:
        return chainId
    return Chain.defaultChainId

class Chain( NTtree ):
    """
-------------------------------------------------------------------------------
Chain class: defines chain properties and methods
-------------------------------------------------------------------------------
    Initiating attributes:
        name                    : Chain identifier such as 'A'.
      
    Derived attributes:
        residues                : NTlist of Residue instances (identical to _children)
        residueCount            : Number of Residue instances
        
    Attributes inherited from NTtree:
        _parent                 : None
        _children               : NTlist of children NTtree instances.
 
    Methods:
        allChains()             : Returns a list containing self.
        allResidues()           : Returns a list of all residue objects of chain.
        allAtoms()              : Returns a list of all atom objects of chain.
        
    Methods inherited from NTtree:
        _Cname( depth )         : Returns name expanded to depth
        addChild( child )       :
        sibling( relativeIndex ) :
        traverse()              :
        
    Methods inherited from NTdict:
        format()                : Return a formatted string of with values of selected fields.
        getAttr()       : Print a list of all attributes and their values.
        
    all dict methods
    """

    DEFAULT_ChainNamesByAlphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ#^_'
    validChainIdListBesidesTheAlphabet = '#^_' # last 3 chars of above.
    'Nothing that is a special character in Python, or tcsh.'
    defaultChainId = '_'
    'See documentation: molecule#ensureValidChainId'

    NULL_VALUE = 'CHAIN_CODE_NULL_VALUE' # can not be a valied chain code but needs to be able to be passed on commandline
    # like in: Scripts/getPhiPsiWrapper.py
    
    def __init__( self, name, **kwds ):
        NTtree.__init__( self, name=name, __CLASS__='Chain', **kwds )
        self.__FORMAT__ =  self.header( dots ) + '\n' +\
                          'residues (%(residueCount)d): %(residues)s\n' +\
                           self.footer( dots )
                          
        self.residues = self._children
        self.residueCount = 0
    #end def
            
    def __repr__(self):
        return str(self)
    #end def
  
    def isNullValue(id):
        return id == Chain.NULL_VALUE
    isNullValue = staticmethod( isNullValue )
    
    def addResidue( self, resName, resNum, **kwds ):
#       We have to make sure that whatever goes on here is also done in the XML handler
        name = resName + str(resNum)
        if name in self:
            NTerror( 'ERROR Chain.addResidue: residue "%s" already present\n', name )
            return None
        #end if
        res = Residue( resName=resName, resNum=resNum, **kwds )
        self._addChild( res )
        res.chain = self
        self[resNum] = res
        self[res.shortName] = res
        self._parent.residueCount += 1
        self.residueCount += 1
        return res
    #end def
    
    def removeResidue( self, residue)   :
        if (not residue in self._children):
            NTerror( 'ERROR Chain.removeResidue: residue "%s" not present in chain %s\n', 
                     residue, self
                   )
            return None
        #end if

        # remove name references
        del( self[residue.resNum] )
        del( self[residue.shortName] )
        # update the counts
        self._parent.residueCount -= 1
        self.residueCount -= 1
        self._parent.atomCount -= len( residue.atoms )
        
        res = self.removeChild( residue )
        if (res == None):
            NTerror('Error Chain.removeResidue: error removing %s from %s\n', residue, self)
            return None
        else:
            res.chain = None
            NTmessage('==> Removed residue %s from %s', residue, self )
            return res
        #end if
    #end def

    def allChains( self ):
        """return self"""
        return self.subNodes( depth = 0 )
    #end def    

    def allResidues( self ):
        """Returns a list of all residues of chain"""
        return self.subNodes( depth = 1 )
    #end def
    
    def allAtoms( self ):
        """Returns a list of all atoms of chain"""
        return self.subNodes( depth = 2 )
    #end def  
    
    def nameTuple( self, convention = INTERNAL ):
        """
        Return a (convention, chainName, None, None) tuple
           for usage with Molecule.decodeNameTuple
        """
        return (convention, self.name, None, None)
    #end def
    
    def residuesWithProperties(self, *properties ):
        """
        Return a NTlist instance with Residues that have properties
        """  
        result = NTlist()
        
        if len(properties) == 0: return result
        for res in self.allResidues():
            if res.hasProperties(*properties):
                result.append(res)
            #end if
        #end for
        return result
    #end def
    
    def atomsWithProperties(self, *properties ):
        """
        Return a NTlist instance with Atoms that have properties
        """  
        result = NTlist()
        
        if len(properties) == 0: return result
        for atm in self.allAtoms():
            if atm.hasProperties(*properties):
                result.append(atm)
            #end if
        #end for
        return result
    #end def
#end class


class XMLChainHandler( XMLhandler ):
    """Chain handler class"""
    def __init__( self ):
        XMLhandler.__init__( self, name='Chain') 
    #end def
    
    def handle( self, node ):
        attrs = self.handleDictElements( node )
        if attrs == None: return None
        result = Molecule( name = attrs['name'] )

        # update the attrs values
        result.update( attrs )
            
        # restore the tree structure and references
        for res in result._children:
#           print '>child>', repr(child)
            result[res.name] = res
            result[res.shortName] = res
            result[res.resNum] = res
            res._parent = result
        return result
    #end def
#end class

#register this handler
chainhandler = XMLChainHandler()

#      
#==============================================================================
#
class Residue( NTtree ):
    """
-------------------------------------------------------------------------------
Residue class: Defines residue properties  
-------------------------------------------------------------------------------
    Initiating attributes:
        resName                 : Residue name according to the nomenclature list.
        resNum                  : Unique residue number within this chain.
      
    Derived attributes:
        atoms                   : NTlist of Atom instances.
        db                      : Reference to database residueDef instance
        chain                   : Reference to Chain instance
        
    Attributes inherited from NTtree:
        _parent                 : Reference to parent NTtree instance (None for root)
        _children               : NTlist of children NTtree instances.
 
    Methods:
        translate( convention ) : translate resName according to convention.
        addAtom()
        addAllAtoms()

        allResidues()           : Returns a list containing self.
        allAtoms()              : Returns a list of all atom objects of residue.

        ...
        
    Methods inherited from NTtree:
        _Cname( depth )         : Returns name expanded to depth
        addChild( child )       :
        sibling( relativeIndex ) :
        traverse()              :
        
    Methods inherited from NTdict:
        format()                : Return a formatted string of with values of selected fields.
        getAttr()       : Print a list of all attributes and their values.
        
    all dict methods
          
    """
    def __init__( self, resName, resNum, **kwds ):
        #print '>',resName, resNum
        NTtree.__init__(self, name=resName + str(resNum), 
                              __CLASS__='Residue', **kwds 
                       )
        self.atoms     = self._children
        self.atomCount = 0        
        self.chain     = self._parent

        self._nameResidue( resName, resNum )
        self.saveXML('resName','resNum')
        self.colorLabel = COLOR_GREEN # innocent until proven guilty.

    #end def
    
    def __repr__(self):
        return str(self)
    #end def
    
    def _nameResidue( self, resName, resNum ):
        """Internal routine to set al the naming right and database refs right
        """
        self.resName  = resName
        self.resNum   = resNum
        self.name     = resName + str(resNum)
        # find the database entry
        if resName in NTdb:
            self.db        = NTdb[self.resName]
            # add the two names to the dictionary
            self.shortName = self.db.shortName + str(resNum)
            self.names     = [self.shortName, self.name]
        else:
            NTwarning('Residue._nameResidue: residue "%s" not defined in database', resName )
            self.db        = None
            self.shortName = '_' + str(resNum)
            self.names     = [self.shortName, self.name]
        #end if         
        self.__FORMAT__ =  self.header( dots ) + '\n' +\
                          'shortName:  %(shortName)s\n' +\
                          'chain:      %(chain)s\n' +\
                          'atoms (%(atomCount)2d): %(atoms)s\n' +\
                           self.footer( dots )
                          
    #end def

    def renumber( self, newResNum ):
        """
        Renumber residue
           Return self or None on error
        """
        newName = self.resName + str(newResNum)
        if newName in self._parent:
            NTerror( 'ERROR Residue.renumber: residue "%s" already present\n', newName )
            return None
        #end if
        
        # remove old name references
        del( self._parent[self.name] )
        del( self._parent[self.resNum] )
        del( self._parent[self.shortName] )

        # set the new naming
        self._nameResidue( self.resName, newResNum )

        # Set new name references
        self._parent.renameChild( self, self.name )
        self._parent[self.resNum]    = self
        self._parent[self.shortName] = self
        
#         self._parent.renameChild( self, newName )
#         self.resNum = newResNum
#         # define the new names
#         self.shortName = self.db.shortName + str( self.resNum )
#         self.names = [self.shortName, self.name]
#         self._parent[self.resNum] = self
#         self._parent[self.shortName] = self
        return self        
    #end def    


    def mutate( self, resName   ):
        """
        Mutate residue to resName
           Return self or None on error
        """
        # find the database entry
        if resName not in NTdb:
            self.db = NTdb[self.resName]
            NTerror('Residue.mutate: residue "%s" not defined in database\n', resName )
            return None
        #end if 
        newRes  = Residue( resName, self.resNum )

        NTmessage('==> Mutating %s to %s', self._Cname(-1), newRes._Cname(-1) )
        
        # remove old name references
        del( self._parent[self.name] )
        del( self._parent[self.resNum] )
        del( self._parent[self.shortName] )

        # replace self with newRes
        self.chain.replaceChild( self, newRes )
        self.chain   = None
        newRes.chain = newRes._parent
        newRes.chain.molecule.atomCount -= self.atomCount
        
        # Set new name references
        newRes._parent[newRes.name]      = newRes
        newRes._parent[newRes.resNum]    = newRes
        newRes._parent[newRes.shortName] = newRes
#        print '.>',newRes.shortName, newRes._parent
        
        # Move like atoms from self, create new atoms if needed
        for atmDef in newRes.db.atoms:
            if (atmDef.name in self):
                atm = self.removeChild( self[atmDef.name] )
                self.atomCount -= 1
                atm.residue = newRes
                newRes._addChild( atm )
                newRes.atomCount += 1
                newRes.chain.molecule.atomCount += 1
            else:
                atm = newRes.addAtom( atmDef.name )
                for dummy in range(newRes.chain.molecule.resonanceCount):
                    atm.addResonance( value=NOSHIFT, error = 0.000 )
                #end for
            #end if
        #end for

        return self,newRes
    #end def    
    
    def addAtom( self, name, **kwds ):
        """add atomName, return Atom instance
        """
#       We have to make sure that whatever goes on here is also done in the XML handler
        ac = Atom( resName=self.resName, atomName=name, **kwds )
        self._addChild( ac )
        ac.residue = self
        self._parent._parent.atomCount += 1
        self.atomCount += 1
        return ac
    #end def
    
    def addAllAtoms( self ):
        """Add all atoms according to the definition database
        """
        # Use database to add atoms
        for atm in self.db:
            self.addAtom( atm.name )
        #end for
    #end def
    
    def dihedral( self, dihedralName ):
        """Return cmean,cv tuple for dihedralName,
        or None on error
        
        set self[dihedralName] to NTlist of results
        """
        # optimized out.
#        if dihedralName not in self.db:
        if not self.db.has_key(dihedralName):
            return None
        
        self[dihedralName] = NTlist()
        self[dihedralName].cAverage()
        self[dihedralName].cav = UNDEFINED_FLOAT
        self[dihedralName].cv  = UNDEFINED_FLOAT
        self[dihedralName].db  = self.db[dihedralName] # linkage to the database
        self[dihedralName].residue  = self             # linkage to self
        
        # Get/Check the topology
        atoms = translateTopology( self, self.db[dihedralName].atoms )
        if (atoms == None or len(atoms) != 4 or None in atoms):
            return None
        
        # Check if all atoms have the same number of coordinates
        l = len( atoms[0].coordinates)
        for a in atoms[1:]:
            if len(a.coordinates) != l:
                return None
            #end if
        #end for
        
        #add dihedral to dict for lookup later
        self.chain.molecule.dihedralDict[(atoms[0],atoms[1],atoms[2],atoms[3])] = \
            (self, dihedralName, self.db[dihedralName])
        self.chain.molecule.dihedralDict[(atoms[3],atoms[2],atoms[1],atoms[0])] = \
            (self, dihedralName, self.db[dihedralName])

        
        for i in range(0,l):
            self[dihedralName].append( NTdihedralOpt(
               atoms[0].coordinates[i],
               atoms[1].coordinates[i],
               atoms[2].coordinates[i],
               atoms[3].coordinates[i]))
        
        plotpars = plotParameters.getdefault(dihedralName,'dihedralDefault')
        self[dihedralName].limit( plotpars.min, plotpars.max )
        cav,cv,_n = self[dihedralName].cAverage(min=plotpars.min,max=plotpars.max)
        
        return cav,cv
    #end def 
    
    def translate( self, convention ):
        """return translated name according to convention"""
        return self.db.translate(convention)
    #end def

    def allResidues( self ):
        """return self"""
        return self.subNodes( depth = 0 )
    #end def
    
    def allAtoms( self ):
        """Returns a list of all atom instances of residue"""
        return self.subNodes( depth = 1 )
    #end def  
        
    def nameTuple( self, convention = INTERNAL ):
        """
        Return a (convention, chainName, resNum, None) tuple
           for usage with Molecule.decodeNameTuple
        """
        return (convention, self.chain.name, self.resNum, None)
    #end def

    def getAtom( self, atomName, convention = INTERNAL ):
        """
        Return Atom instance of atomName, or None if it does not exist
           translate from convention if needed
        """
        if atomName == None:
            return None
        #end if
        
        if (convention != INTERNAL):
            atomName = translateAtomName( convention, self.resName, atomName, INTERNAL )
        #end if
        if (atomName in self):
            return self[atomName]
        #end if
        return None
    #end def
    
    def getAtoms( self, atomNames, convention = INTERNAL ):
        """
        Return a list of Atom instances corresponding to atomName
           translate from convention if needed
        """ 
        if atomNames == None:
            return NTlist()
        #end if
                
        result = NTlist()
        for name in atomNames:
            a = self.getAtom( name, convention=convention )
            if (a != None):
                result.append( a )
            #end if
        #end for
        return result
    #end def
                        
    def hasProperties(self, *properties):
        """
        Returns True if Residue has the argument properties, False otherwise.
        Special case: if no properties are set return True
        """
        if not len(properties):
            return True
        props = NTlist( self.db.name, self.db.shortName, *self.db.properties)
        for p in properties:
            if not p in props:
               return False
            #end if
        #end for
        return True
    #end def
     
    def residuesWithProperties(self, *properties ):
        """
        Return a NTlist instance with self if it has properties.
        NB (ode copied from Molecule and Chain; could be shorter.
        """  
        result = NTlist()
        
        if len(properties) == 0: return result
        for res in self.allResidues():
            if res.hasProperties(*properties):
                result.append(res)
            #end if
        #end for
        return result
    #end def
    
    def atomsWithProperties(self, *properties ):
        """
        Return a NTlist instance with Atoms that have properties
        """  
        result = NTlist()
        
        if len(properties) == 0: return result
        for atm in self.allAtoms():
            if atm.hasProperties(*properties):
                result.append(atm)
            #end if
        #end for
        return result
    #end def
    
#end class

class XMLResidueHandler( XMLhandler ):
    """Residue handler class"""
    def __init__( self ):
        XMLhandler.__init__( self, name='Residue') 
    #end def
    
    def handle( self, node ):
        attrs = self.handleDictElements( node )
        if attrs == None: return None
        result = Residue( resName = attrs['resName'], resNum = attrs['resNum'] )

        # update the attrs values
        result.update( attrs )
            
        # restore the tree structure
        for atm in result._children:
            result[atm.name] = atm
            atm._parent = result
        return result
    #end def
#end class

#register this handler
residuehandler = XMLResidueHandler()
  

#==============================================================================
class Atom( NTtree ):
    """
-------------------------------------------------------------------------------
Atom class: Defines object for storing atom properties 
-------------------------------------------------------------------------------
    Initiating attributes:
        resName                 : Residue name according to the nomenclature list.
        atomName                : Atom name according to the nomenclature list.
      
    Derived attributes:
        atomIndex               : Unique atom index (several external programs need one).
        resonances              : NTlist of Resonance instances.
        db                      : Reference to database AtomDef instance
        residue                 : Reference to Residue instance
        
    Attributes inherited from NTtree:
        _parent                 : Reference to parent NTtree instance (None for root)
        _children               : NTlist of children NTtree instances.
 
    Methods:
        translate( convention ) : translate atomName according to convention.
        topology()              : Return list of Atom instances defining topology
        isAssigned()            : Return true if atoms has ta least one assignment
        set()                   : Return a NTset instance containing Atom instances:
                                     if   isPseudoAtom():  set contains self and the real atom instances
                                     elif hasPseudoAtom(): set contains self and pseudoAtom instances
                                     else:                 set contains self
        
        allAtoms()              : Returns a list containing self.

    Methods inherited from NTtree:
        _Cname( depth )         : Returns name expanded to depth
        addChild( child )       :
        sibling( relativeIndex ) :
        traverse()              :
        
    Methods inherited from NTdict:
        format()                : Return a formatted string of with values of selected fields.
        getAttr()       : Print a list of all attributes and their values.
        
    all dict methods
          
    """
    def __init__( self, resName, atomName, **kwds ):
    
        NTtree.__init__(self, name=atomName, __CLASS__='Atom',**kwds )
        
        self.__FORMAT__ = self.header( dots ) + '\n' +\
                          'residue:     %(residue)s\n' +\
                          'resonances:  %(resonances)s\n' +\
                          'coordinates: %(coordinates)s\n' +\
                          self.footer( dots ) 

        self.resonances  = NTlist()
        self.coordinates = NTlist()
#        self.resName     = resName # have to store because initialisation is done
#                                   # without knowledge of parent
        
        self.saveXML('resName', 'resonances','coordinates')
        
        # several external programs need an index
        global AtomIndex
        self.atomIndex = AtomIndex
        AtomIndex += 1

        # find the database entry
        if ( (resName in NTdb) and (atomName in NTdb[resName]) ):
            self.db = NTdb[resName][atomName]
        else:
            self.db = None
            NTerror('Atom.__init__: atom "%s" not defined for residue %s in database\n',
                     atomName, resName 
                   )
        #end if
    #end def 
    
    def __str__( self ):
#        return self._Cname( 1 )
        return '<%s %s>' % ( self._className(), self._Cname(1) )
    #end def
    
    def __repr__(self):
        return str(self)
    #end def
 
    def addCoordinate( self, x, y, z, Bfac, **kwds ):
        """Append coordinate to coordinates list
        Convenience method."""
        c = Coordinate( x, y, z, Bfac=Bfac, occupancy=Coordinate.DEFAULT_OCCUPANCY, atom=self )
#        c.update( **kwds )
        self.coordinates.append( c )
    #end def
 
    def addResonance( self, value, error=0.0 ):
        r = Resonance( atom=self, value=value, error = 0.000 )
        self.resonances.append( r )
    #end def
 
    def distance( self, other ):
        """Return (av,sd,min,max) tuple corresponding to distance
           between self and other or None on error
           Set the distances array for later usage.
        """
        lenSelf = len( self.coordinates)
        if lenSelf == 0:
            return None
        #end if
        if (lenSelf != len( other.coordinates ) ):
            return None
        #end if
        self.distances = NTlist()
        for i in range(0, lenSelf):
            self.distances.append( NTdistanceOpt(self.coordinates[i], other.coordinates[i]) )
        #end for
        av,sd,dummy = self.distances.average()
        minv = min(self.distances)
        maxv = max(self.distances)
        return (av,sd,minv,maxv)
    #end def
    
    def meanCoordinates( self ):
        """"
        Store and return mean Coordinate instance, or None on error.
        Todo: Set dx, dy, dz, rmsd attributes of meanCoordinate
        and store variance of x, variance of y, variance of z and rmsd of coordinate
        """
        n   = len( self.coordinates)

        if n == 0:
            self.meanCoordinate = None
            return None

        c = Coordinate( x=0.0, y=0.0, z=0.0,
                        Bfac=Coordinate.DEFAULT_BFACTOR,
                        occupancy=Coordinate.DEFAULT_OCCUPANCY,
                        atom = self 
                      )
        self.meanCoordinate = c
        self.meanCoordinate.__FORMAT__ = '<mean Coordinate (%6.2f,%6.2f,%6.2f)>'
        
#        if n==1:
#            self.meanCoordinate[0] = self.coordinates[0][0]
#            self.meanCoordinate[1] = self.coordinates[0][1]
#            self.meanCoordinate[2] = self.coordinates[0][3]
#            self.meanCoordinate.dx = 0.0
#            self.meanCoordinate.dy = 0.0
#            self.meanCoordinate.dz = 0.0
#            for axis in ['x','y','z']:
#                self.meanCoordinate[axis] = self.coordinates[0][axis]
#                self.meanCoordinate['d'+axis] = 0.0
            #end for
#            self.meanCoordinate.rmsd = 0.0
#        else:
#            fn  = float(n)
#            fn1 = fn-1.0
#            self.meanCoordinate.rmsd = 0.0
#        for d in range(3):
#        xdata = NTlist()
#        ydata = NTlist()
#        zdata = NTlist()
        for i in range(n):
            cc = self.coordinates[i]
            c[0] += cc[0]
            c[1] += cc[1]
            c[2] += cc[2]
        c[0] /= n
        c[1] /= n
        c[2] /= n
        
#            for axis in ['x','y','z']:
#                #For speed we store the array first
#                data  = self.coordinates.zap(axis)
#                sum   = data.sum()
##                sumsq = data.sumsq()
#
#                self.meanCoordinate[axis]     = sum/fn
                
                #sumsq/(fn-1.0) - (sum*sum)/(fn*(fn-1.0))
#                self.meanCoordinate['d'+axis] = sumsq - sum*sum/fn/fn1
#                self.meanCoordinate.rmsd += sumsq - sum*sum/fn
            #end for
            
#            self.rmsd = 0.0
#            for c in self.coordinates:
#                self.rmsd += NTdistance(c, self.meanCoordinate )
#            #end for
#            self.rmsd /= fn
#        #end if    
                
        return self.meanCoordinate
    #end def
    
    def angle( self, other1, other2, min = 0.0, max = 360.0, radians = False ):
        """Return (cav,cv) tuple corresponding to angle
           other1-self-other2 or None on error.
           Set the angles array for later usage.
        """
        lenSelf = len( self.coordinates)
        if lenSelf == 0:
            return None
        #end if
        if (lenSelf != len( other1.coordinates ) ):
            return None
        #end if
        if (lenSelf != len( other2.coordinates ) ):
            return None
        #end if
        self.angles = NTlist()
        for i in range(0, lenSelf):
            self.angles.append( NTangleOpt(other1.coordinates[i], self.coordinates[i], other2.coordinates[i], radians=radians ) )
        #end for
        cav,cv,dummy = self.angles.cAverage( min=min, max=max, radians= radians )
        return (cav,cv)
    #end def
    
    def translate( self, convention ):
        """return translates name according to convention"""
        return self.db.translate(convention)
    #end def
     
    def topology( self ):
        """return list of Atom instances defining the topology"""
        return translateTopology( self._parent, self.db.topology )
    #end def
    
    def isAssigned( self ):
        """return true if atom current resonance has a valid assignment"""
        if (self.resonances() != None):
            return (self.resonances().value != NOSHIFT)
        #end if 
        return False
    #end def
    
    def shift( self ):
        if self.isAssigned():
            return self.resonances().value
        else:
            return NOSHIFT
        #end if
    #end def
    
#    def isAromatic( self ):
#        """Return true if it is an atom belonging to an aromatic ring
#           Patched for now, have to store it in database
#        """
#        if not self.residue.db.hasProperties('aromatic'): return False
#        
#        if (self.isCarbon() and self.db.shift.average > 100.0):
#            return True
#        if (self.isNitrogen() and self.db.shift.average > 130.0):
#            return True
#        elif (self.isProton()):
#            topo = self.topology()
#            if len(topo) == 0: return False #bloody CYANA pseudo atomsof some residues like CA2P do not have a topology
#            heavy = self.topology()[0]
#            return heavy.isAromatic()
#        #end if
#        return False
#    #end def
#    
#    def isBackbone( self ):
#        """
#        Return True if it is a backbone atom.
#        Patch for now, based upon explicit enumeration
#        """
#        if self.name in ['C','O','N','H','HN','H1','H2','H3','CA','HA','HA1','HA2']:
#            return True
#        else:
#            return False
#    #end def
#    
#    def isSidechain( self ):
#        """
#        Return True if it is a sidechain atom,
#        i.e. not isBackbone
#        """
#        return not self.isBackbone()
#    #end def
#    
#    def isMethyl( self ):
#        """
#        Return True atm is a methyl (either carbon or proton)
#        """
#        if self.isCarbon() and len(self.attachedProtons(includePseudo = False)) == 3:
#            return True
#        elif self.isProton(): 
#            # should be attched to a heavy atomo
#            topo = self.topology()
#            if len(topo) == 0 or topo[0] == None: return False            
#            return topo[0].isMethyl()
#        else:
#            return False
#        #end if
#    #end def
#    
#    def isMethylProton( self ):
#        """
#        Return True if atm is a methyl proton
#        """
#        return self.isProton() and self.isMethyl()
#    #end def
    def isAromatic( self ):
        """Return true if it is an atom belonging to an aromatic ring
        """
        return self.db.hasProperties('aromatic')
    #end def
    
    def isBackbone( self ):
        """
        Return True if it is a backbone atom.
        """
        return self.db.hasProperties('backbone')
    #end def
    
    def isSidechain( self ):
        """
        Return True if it is a sidechain atom,
        """
        return self.db.hasProperties('sidechain')
    #end def
    
    def isMethyl( self ):
        """
        Return True atm is a methyl (either carbon or proton)
        """
        return self.db.hasProperties('methyl')
    #end def
    
    def isMethylProton( self ):
        """
        Return True if atm is a methyl proton
        """
        return self.db.hasProperties('methylproton')
    #end def
        
    def isProton( self ):
        """Return Tue if atm is 1H
        """
        return (self.db.spinType == '1H')
    #end def

    def isCarbon( self ):
        """Return Tue if atm is 13C
        """
        return (self.db.spinType == '13C')
    #end def
    
    def isNitrogen( self ):
        """Return Tue if atm is 15N
        """
        return (self.db.spinType == '15N')
    #end def

    def isSulfur( self ):
        """Return Tue if atm is 32S
        """
        return (self.db.spinType == '32S')
    #end def
                       
    def hasProperties(self, *properties):
        """
        Returns True if Atom has properties, expand with db properties for atom
        False otherwise
        """
        if len(properties) == 0: return False

        props = NTlist(*self.db.properties)
        
        if self.isAssigned(): 
            props.append('isAssigned','assigned')
        else:
            props.append('isNotAssigned','notassigned')
        #end if
# in database now
#        if self.isBackbone(): 
#            props.append('isBackbone','backbone')
#        else:
#            props.append('isSidechain','sidechain')
#        #endif
#        if self.isAromatic():
#            props.append('isAromatic','aromatic')
#        else:
#            props.append('isNotAromatic','notaromatic')
#        #end if
#        if self.isMethyl():
#            props.append('isMethyl','methyl')
#        else:
#            props.append('isNotMethyl','notmethyl')
#        #end if
#        if self.isMethylProton():
#            props.append('isMethylProton','methylproton')
#        else:
#            props.append('isNotMethylProton','notmethylproton')
#        #end if

#        print '>>', props
        
        for p in properties:
            if not p in props:
               return False
            #end if
        #end for
        return True
    #end def
    
    def atomsWithProperties(self, *properties ):
        """
        Return a NTlist instance with self if it has propeties.
        NB. Code could be shorter but is copied from Molecule,Chain,Residue
        """  
        result = NTlist()
        
        if len(properties) == 0: return result
        for atm in self.allAtoms():
            if atm.hasProperties(*properties):
                result.append(atm)
            #end if
        #end for
        return result
    #end def
    
    def allAtoms( self ):
        """return self"""
        return self.subNodes( depth = 0 )
    #end def
        
    def nameTuple( self, convention = INTERNAL ):
        """Return a (convention, chainName, resNum, atomName) tuple
           for usage with Molecule.decodeNameTuple
           or None on translate error of atomName
        """
        an = self.translate( convention )
        if not an: return None
        return ( convention, self.residue.chain.name, self.residue.resNum, an )
    #end def

    def isPseudoAtom( self ):
        """Return 1 if atom is pseudoAtom"""
        return ( len(self.db.real) > 0 )
    #end def
        
    def hasPseudoAtom( self ):
        """Return 1 if atom has a correponding pseudoAtom"""
        return ( self.db.pseudo != None ) 
    #end def

    def pseudoAtom( self ):
        """Return the pseudoAtom instance (if exist, or None otherwise)"""
        if self.hasPseudoAtom():
            return self.residue.getAtom( self.db.pseudo )
        else:
            return None
        #end if
    #end def
    
    def realAtoms( self ):
        """IF pseudoAtom: Return an NTlist with real Atom instances of a pseudoAtom
           else NTlist with self.
           gv 7 Sept 2007: changed else from empty list to list with self.
        """
        if self.isPseudoAtom():
            return self.residue.getAtoms( self.db.real )
        else:
            return NTlist( self )
        #end if
    #end def
    
    def set( self ):
        """ 
        set()                   : Return a NTset instance containing Atom instances:
                                     if   isPseudoAtom():  set contains self and the real atom instances
                                     elif hasPseudoAtom(): set contains self and pseudoAtom instances
                                     else:                 set contains self
        """
        # generate the set
        result = NTset( self )
        if  self.isPseudoAtom():  
            # set contains self and the real atoms
            for a in self.realAtoms():
                result.append( a )
            #end for
        elif self.hasPseudoAtom(): 
            #set contains self and pseudoAtom instances
            result.append( self.pseudoAtom() )
        else:                 
            # set contains self
            pass
        #end if
        return result
    #end def
    
    def attachedProtons( self, includePseudo = 0 ):
        """
        Return all attached proton instances or empty list
        voor protons or pseudoatoms (spinType = '1H')
        Optionally include pseudoatom
        """
        result = NTlist()
        if (self.db.spinType == '1H'):
            return result
        #endif
        
        for a in self.topology():
            if (a != None and a.db.spinType == '1H'):
                result.append( a )
            #end if
        #end for
        if (includePseudo and len(result) > 0):
            if result[0].hasPseudoAtom():
                result.append( result[0].pseudoAtom() )
            #end if
        #end if
        return result
    #end def
    
    def observableProtons( self, includePseudo = 0 ):
        """
        Return all NMR observable proton instances or empty list
        voor protons or pseudoatoms (spinType = '1H')
        Optionally include pseudoatom
        """
        result = self.attachedProtons( includePseudo = False )
        # Methyl
        if (len(result) == 3):
            result = NTlist( result[0].pseudoAtom() )
        elif (includePseudo and len(result) > 0):
            if result[0].hasPseudoAtom():
                result.append( result[0].pseudoAtom() )
            #end if
        #end if
        return result
    #end def
    
    def toPDB( self, pdbIndex, model, convention = IUPAC ):
        """Convert to PyMMLib ATOM record; 
           use x,y,z values of model
           use convention nomenclature
           return record on success or None on error/non-valid atoms
           
           16 Oct 2007: GV Fixed bug: model=0 would also invoke
                        The "current" setting; i.e would map to last
                        coordinate added.
        """
        if model >= len(self.coordinates):
            # this happens for all pseudos and atoms like Cys HG which aren't always present
            # but are defined in the db.
#            NTdebug("Trying to Atom.toPDB for model: " + `model`)
#            NTdebug("but only found coordinates length: " + `len(self.coordinates)`)
            return None
        if model < 0:
            NTcodeerror("In Atom.toPDB found model to be <0: " + `model`)
            return None
#        modelId = model - 1
        
        pdbAtmName = self.translate( convention )
        if not pdbAtmName:
            if self.name.startswith('Q'):
                return None
            NTwarning("Failed to translate from CING to convention: %s atom: %-20s" % ( convention, self ))
            return None
        
        pdbResName = self.residue.translate( convention )
        if not pdbResName:
            NTwarning("Failed to translate from CING to convention: %s residue: %-20s" % ( convention, self.residue ))
            return None

        coor = self.coordinates[model]
        
        if self.db.hetatm:
            record = HETATM()
        else:
            record = ATOM()

        chainId = self.residue.chain.name
        
        record.serial     = pdbIndex
        record.name       = pdbAtmName
        record.resName    = pdbResName
            
        record.chainID    = chainId
        record.resSeq     = self.residue.resNum
        record.x          = coor[0]
        record.y          = coor[1]
        record.z          = coor[2]
        record.tempFactor = coor.Bfac
        record.occupancy  = coor.occupancy

        return record
    #end def
    
    def toPDBTER( self, pdbIndex, convention = IUPAC ):
        """Convert to PyMMLib TER record; 
           return record on success or None on error
        """
        pdbAtmName = self.translate( convention )
        if not pdbAtmName: return None
        
        pdbResName = self.residue.translate( convention )
        if not pdbResName: return None
        
        record = PyMMLib.TER()
        
        record.serial   = pdbIndex
        record.name     = pdbAtmName
        record.resName  = pdbResName
            
        record.chainID  = self.residue.chain.name
        record.resSeq   = self.residue.resNum

        return record
    #end def

#end class


class XMLAtomHandler( XMLhandler ):
    """Atom handler class"""
    def __init__( self ):
        XMLhandler.__init__( self, name='Atom') 
    #end def
    
    def handle( self, node ):
        attrs = self.handleDictElements( node )
        if attrs == None: return None
        result = Atom( resName = attrs['resName'], atomName = attrs['name'] )

        # update the attrs values
        result.update( attrs )
            
        # restore the resonance references
        for r in result.resonances:
            r.atom = result

        return result
    #end def
#end class

#register this handler
atomhandler = XMLAtomHandler()

class CoordinateOld( list ):
    """
--
Coordinate class optimized because dictionary indexing and attribute calls
are too expensive. Just remember the attributes have a fixed order.
Usually this is to be avoided but the speed improvement makes it worth our
while.
Added getter/setters for the non obvious ones.
--
    """
    DEFAULT_BFACTOR   = 0.0
    DEFAULT_OCCUPANCY = 1.0
    def __init__( self, x, y, z, Bfac=DEFAULT_BFACTOR, occupancy=DEFAULT_OCCUPANCY, atom=None ):
        list.__init__( self  )
        self.append( x )
        self.append( y )
        self.append( z )
        self.append( Bfac )
        self.append( occupancy )
        self.append( atom )
    def getBFac(self):
        return self[3]
    def getOccupancy(self):
        return self[4]
    def getAtom(self):
        return self[5]
    def setBFac(self, v):
        self[3] = v
    def setOccupancy(self, v):
        self[4] = v
    def setAtom(self, v):
        self[5] = v
#        self.dx = "blabla" optional.
    def __call__( self ):
        return self

#==============================================================================
class Coordinate( Vector ):
    """
-------------------------------------------------------------------------------
GWV:
Derived from Vector class
TODO: compile super class with Pyrex
    correct superclass name in above definition to "cing.Libs.vector.vector".
    """

    DEFAULT_BFACTOR   = 0.0
    DEFAULT_OCCUPANCY = 1.0

    def __init__( self, x, y, z, 
                        Bfac=DEFAULT_BFACTOR, occupancy=DEFAULT_OCCUPANCY, atom = None 
                ):
        Vector.__init__( self, x, y, z )
#        NTstruct.__init__(   self,
#                           __CLASS__  = 'Coordinate', 
#                           __FORMAT__ = '(%(x)6.2f,%(y)6.2f,%(z)6.2f)'
#                         )
#        self.x = x
#        self.y = y
#        self.z = z
        self.Bfac = Bfac
        self.atom = atom
        self.occupancy = occupancy
        self.__FORMAT__ = '<Coordinate (%6.2f,%6.2f,%6.2f)>'
    #end def
    
    # Mimic the dict functionality for all but integers and x,y,z
    def __getitem__(self, item):
        if isinstance( item, int ):
            return Vector.__getitem__(self, item)
        elif  item == 'x':
            return self.x
        elif  item == 'y':
            return self.y
        elif  item == 'z':
            return self.z
        else: 
            return self.__dict__[item]

    def __setitem__(self, item, value):
        if isinstance( item, int ):
            Vector.__setitem__( self, item, value )
        elif  item == 'x':
            self.x = value
        elif  item == 'y':
            self.y = value
        elif  item == 'z':
            self.z = value
        else: 
            self.__dict__[item] = value
    
    def __delitem__(self, item):
        if isinstance( item, int ):
            pass
        elif  item == 'x':
            pass
        elif  item == 'y':
            pass
        elif  item == 'z':
            pass
        else: 
            del(self.__dict__[item])

    def format(self):
         return sprintf( self.__FORMAT__, self.x, self.y, self.z )   
    #end def
    
    def __repr__(self):
        return sprintf('Coordinate( x=%f, y=%f, z=%f, Bfac=%f )', self.x, self.y, self.z, self.Bfac )
    #end def    
    def __call__( self ):
#        return Vector(self.x, self.y, self.z)
        return self
    #end def
    
#end class

#class XMLCoordinateHandler( XMLhandler ):
#    """Coordinate handler class"""
#    def __init__( self ):
#        XMLhandler.__init__( self, name='Coordinate') 
#    #end def
#    
#    def handle( self, node ):
#        attrs = self.handleDictElements( node )
#        if attrs == None: return None
#        result = Coordinate( x = attrs['x'], y = attrs['y'], z=attrs['z'] )
#        # update the attrs values
#        result.update( attrs )      
#        return result
#    #end def
##end class
#
##register this handler
#coordinatehandler = XMLCoordinateHandler()

#==============================================================================
def NTdistance( c1, c2 ):
    """
    Return distance defined by Coordinate instances c1-c2
    """
    return (c2-c1).length()
#end def

def NTdistanceOpt( c1, c2 ):
    """
    Return distance defined by Coordinate instances c1-c2
    """
#    d = c2()-c1()
    d = ( c2[0]-c1[0], c2[1]-c1[1], c2[2]-c1[2] )
#    return d.length()
    return length3Dopt(d)


def NTangle( c1, c2, c3, radians = False ):
    """
    Return angle defined by Coordinate instances c1-c2-c3
    """
#    a = c2()-c1()
#    b = c2()-c3()
    a = c2-c1
    b = c2-c3
    return a.angle( b, radians=radians )    
#end def

def NTangleOpt( c1, c2, c3, radians = False ):
    """
    Return angle defined by Coordinate instances c1-c2-c3
    """
#    a = c2()-c1()
#    b = c2()-c3()
    a = ( c2[0]-c1[0], c2[1]-c1[1], c2[2]-c1[2] )
    b = ( c2[0]-c3[0], c2[1]-c3[1], c2[2]-c3[2] )

#    return a.angle( b, radians=radians )
    return angle3Dopt( a, b )
#end def

def NTdihedral( c1, c2, c3, c4, radians=False ):
    """
    Return dihedral angle defined by Coordinate instances c1-c2-c3-c4
    Adapted from biopython-1.41
    
    """
#    ab = c1() - c2()
#    cb = c3() - c2()
#    db = c4() - c3()
    ab = c1 - c2
    cb = c3 - c2
    db = c4 - c3
    
    u = ab.cross( cb )
    v = db.cross( cb )
    w = u.cross( v )
    
    angle = u.angle( v, radians=radians )
    # determine sign of angle
    try:
        if cb.angle( w, radians=True ) > 0.001: angle *= -1.0
    except ZeroDivisionError:
        # dihedral=pi or 0
        pass    
    
    return angle
#end def
def NTdihedralOpt( c1, c2, c3, c4 ):
    """ To replace unoptimized routine. It's 7 times faster (20.554/2.965s)
    for 100,000 calculations. Since last the performance dropped with
    the coordinate based on CoordinateOld(list) to 3.0 s per 10,000.
    Return dihedral angle defined by Coordinate instances c1-c2-c3-c4
    Adapted from biopython-1.41
    """
#    ab = c1() - c2() optimized
#    cb = c3() - c2()
#    db = c4() - c3()
    ab = ( c1[0]-c2[0], c1[1]-c2[1], c1[2]-c2[2] )
    cb = ( c3[0]-c2[0], c3[1]-c2[1], c3[2]-c2[2] )
    db = ( c4[0]-c3[0], c4[1]-c3[1], c4[2]-c3[2] )

    # Optimized out.
#    u = ab.cross( cb )
#    v = db.cross( cb )
#    w =  u.cross( v )

    u = cross3Dopt(ab,cb)
    v = cross3Dopt(db,cb)
    w = cross3Dopt( u,v)

#    angle = u.angle( v, radians=radians )
    angle = angle3Dopt( u, v )

    # Tries are expensive; next step of optimalization is to remove it.
    # Speed check showed major bottleneck(s) disappeared so leaving it in.
    # determine sign of angle
    try:
        cbAngleDegrees = angle3Dopt( cb, w )
#        if cb.angle( w, radians=True ) > 0.001:
        if cbAngleDegrees > 0.001:
#            angle *= -1.0 optimized
            angle = -angle
    except ZeroDivisionError:
        # dihedral=pi or 0
        pass

    return angle
#end def

#==============================================================================
class Resonance( NTvalue  ):
    """Resonance class; implemented as an NTvalue object
    """
    
    def __init__( self, atom=None, value=NOSHIFT, error=0.000 ):
        NTvalue.__init__( self, __CLASS__  = 'Resonance', 
                                value      = value, 
                                error      = error, 
                                fmt        = '<%7.3f  (%7.3f)>', 
                                atom       = atom
                         )
        self.__FORMAT__ =  self.header( dots ) + '\n' +\
                          'atom:  %(atom)-12s\n' +\
                          'value: %(value)7.3f\n' +\
                          'error: %(error)7.3f\n' +\
                           self.footer( dots ) 

    #end def
    
    def __str__( self ):
        return sprintf('<Resonance: %.3f %.3f %s>', self.value, self.error, self.atom )
    #end def
    
    def match( self, other ):
        """Return probability of matching between self and other
        """
        sigma1 = self.error
        if sigma1 == 0.0: sigma1 = 1.0
        sigma2 = other.error
        if sigma2 == 0.0: sigma2 = 1.0
         
        return math.exp( -(self.value-other.value )**2 / (sigma1*sigma2*2) )
    #end def
#end class

class XMLResonanceHandler( XMLhandler ):
    """Resonance handler class"""
    def __init__( self ):
        XMLhandler.__init__( self, name='Resonance') 
    #end def
    
    def handle( self, node ):
        attrs = self.handleDictElements( node )
        if attrs == None: return None
        result = Resonance( value = attrs['value'], error = attrs['error'] )
        # update the attrs values
        result.update( attrs )      
        return result
    #end def
#end class

#register this handler
resonancehandler = XMLResonanceHandler()


#==============================================================================
def translateTopology( residue, topDefList ):
    """internal routine to translate a list of topology (resdiffIndex,atomName) 
       tuples to Atom instances 
       return NTlist instance or None on error 
    """ 
    result = NTlist()
    
    for resdiffIndex,atomName in topDefList:
        # optimized
        res = residue.sibling( resdiffIndex )
        if res == None or not res.has_key( atomName ):
            result.append( None )
            continue
        result.append( res[atomName] )
    return result
#end def
                    
#==============================================================================
def allAtoms( molecule ):
  """generator looping over all atoms of molecule
     25 Feb 2006: depreciated: use molecule.allAtoms() method in stead.
  """
  return molecule.allAtoms()  
#end def    

#==============================================================================
def allResidues( molecule ):
  """generator looping over all residues of molecule
     25 Feb 2006: depreciated: use molecule.allResidues() method in stead.
  """
  return molecule.allResidues()
#end def

#==============================================================================
def updateResonancesFromPeaks( peaks, axes = None)   :
    """Update the resonance entries using the peak shifts"""
    for peak in peaks:
        if (axes == None):
            axes = range(0,peak.dimension)
        #end if
        for i in axes:
            if (peak.resonances[i] != None):
                peak.resonances[i].value = peak.positions[i]
                if peak.resonances[i].atom != None:
                    NTmessage("Updating resonance %s", peak.resonances[i].atom)
                #end if
            #end if
        #end for
    #end for
#end def
     
#==============================================================================
def saveMolecule( molecule, fileName=None)   :
    """save to fileName for restoring with restoreMolecule"""
    if not fileName:
        fileName = molecule.name + '.xml'
    #end if
    
    if (molecule == None):
        NTerror("saveMolecule: molecule not defined\n")
        return
    #end if
  
    obj2XML( molecule, path=fileName )

    NTmessage( '==> saveMolecule: saved to %s', fileName )
    #end if
#end def

#==============================================================================
def restoreMolecule( fileName)   :
    """restore from fileName, return Molecule instance """
    
    mol = XML2obj( path=fileName )
    if (mol == None): return None
  
    mol.source = fileName
  
    NTmessage( '==> restoreMolecule: restored %s', mol.format())
    #end if
  
    return mol
#end def

def rmsd( atomList ):
    """
    return (rmsd,n) tuple for all atoms in atomList 
    """
    
    result = 0.0
    n = 0
    for atm in atomList:
        if atm.mean: 
            result += atm.mean.variance
            n += 1
        #end if
    #end for
    return (math.sqrt( result/n ), n)       
#end def
