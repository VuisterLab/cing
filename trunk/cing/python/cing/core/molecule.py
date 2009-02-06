from cing import issueListUrl
from cing.Libs import PyMMLib
from cing.Libs.AwkLike import AwkLikeS
from cing.Libs.NTutils import NTcodeerror
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTdetail
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTfill
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTset
from cing.Libs.NTutils import NTtree
from cing.Libs.NTutils import NTvalue
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import NoneObject
from cing.Libs.NTutils import ROGscore
from cing.Libs.NTutils import XML2obj
from cing.Libs.NTutils import angle3Dopt
from cing.Libs.NTutils import asci2list
from cing.Libs.NTutils import cross3Dopt
from cing.Libs.NTutils import fprintf
from cing.Libs.NTutils import length3Dopt
from cing.Libs.NTutils import list2asci
from cing.Libs.NTutils import obj2XML
from cing.Libs.NTutils import sprintf
from cing.Libs.PyMMLib import ATOM
from cing.Libs.PyMMLib import HETATM
from cing.Libs.PyMMLib import PDBFile
from cing.Libs.cython.superpose import NTcMatrix #@UnresolvedImport
from cing.Libs.cython.superpose import NTcVector #@UnresolvedImport
from cing.Libs.cython.superpose import calculateRMSD #@UnresolvedImport
from cing.Libs.cython.superpose import superposeVectors #@UnresolvedImport
from cing.Libs.fpconst import NaN
from cing.Libs.fpconst import isNaN
from cing.core.constants import COLOR_ORANGE
from cing.core.constants import CYANA
from cing.core.constants import CYANA2
from cing.core.constants import CYANA_NON_RESIDUES
from cing.core.constants import INTERNAL
from cing.core.constants import IUPAC
from cing.core.constants import LOOSE
from cing.core.constants import NOSHIFT
from cing.core.constants import XPLOR
from cing.core.database import AtomDef
from cing.core.database import translateAtomName
from cing.core.database import translateResidueName
from database import NTdb
from math import acos
from math import pi
from parameters   import plotParameters
import math
import os
import sys



#==============================================================================
# Global variables
#==============================================================================
AtomIndex = 1

# version <= 0.91: old sequence.dat defs
# version 0.92: xml-sequence storage, xml-stereo storage
# Superseeded by SML routines
NTmolParameters = NTdict(
    version        = 0.92,
    contentFile    = 'content.xml',
    sequenceFile   = 'sequence.xml',
    resonanceFile  = 'resonances.dat',
    coordinateFile = 'coordinates.dat',
    stereoFile     = 'stereo.xml'
)

dots = '-----------'
#==============================================================================
class Molecule( NTtree ):
    """
    Molecule class: defines the holder for molecule items.

    _____________________________________________________________________________
    API layout in cing.core.classes
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
        chainCount              : Number of Chain instances
        residueCount            : Number of Residue instances
        atomCount               : Number of Atom instances
        resonanceCount          : Number of Resonance Instances per atom
        modelCount              : Number of Coordinate instances per atom
  """

    def __init__( self, name, **kwds ):
        NTtree.__init__(self, name, __CLASS__='Molecule', **kwds )

        self.chains       = self._children

        # These will be set on the fly
        self.chainCount   = 0
        self.residueCount = 0
        self.atomCount    = 0

        # These will be maintained by the appropriate routines
        self.resonanceCount   = 0
        self.resonanceSources = NTlist()
        self.modelCount       = 0

#        self._coordinates = NTlist()       # internal array with coordinate references
        self._nameTupleDict   = {}          # Internal namedict for decodeNameTuple
        self._dihedralDict    = {}          # dihedralDict[(atoms1, atom2, atom3,atom4)] = (<Residue>, angleName, <AngleDef>)
                                            # will be filled by calling dihedral method of residue

        self.xeasy            = None         # reference to xeasy class, used in parsing
        self.rogScore         = ROGscore()
        self.ranges           = None         # ranges used for superposition/rmsd calculations

#        self.saveXML('chainCount','residueCount','atomCount')

        # save the content definitions; depreciated since version 0.75
        # Maintained for compatibility
        self.content = NTdict( name = self.name, convention = INTERNAL )
        self.content.update( NTmolParameters )
        self.content.saveAllXML()
        self.content.keysformat()

        NTdebug('Molecule.__init__: %s', self )
        #end if
    #end def

    def format(self):
        self.nAssigned = 0
        self.nStereoAssigned = 0
        for atm in self.allAtoms():
            if atm.isAssigned(): self.nAssigned += 1
            if atm.isStereoAssigned(): self.nStereoAssigned += 1
        #end for

        result = sprintf(
                          '%s\n' +\
                          'chains:      %d %s\n' +\
                          'residues:    %d\n' +\
                          'atoms:       %d\n' +\
                          'models:      %d\n' +\
                          'resonances:  %d per atom; sources %s\n' +\
                          'assignments: %d (%d stereo)\n' +\
                          '%s',
                           self.header( dots ),
                           self.chainCount, self.chains,
                           self.residueCount,
                           self.atomCount,
                           self.modelCount,
                           self.resonanceCount,
                           self.resonanceSources,
                           self.nAssigned, self.nStereoAssigned,
                           self.footer(dots)
                         )
        return result
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


    def ensureValidChainIdForThisMolecule(self, chainId ):
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
        space character, CING will translate it to the next still available chain id
        value. It's up to the caller to remember the mapping then!

        Bottom line: use a chain id character on input!
        """
        if isValidChainId( chainId ):
            return chainId

        if len(chainId) > 1:
            chainId = chainId[0]

        if isValidChainId( chainId ):
            return chainId

        return self.getNextAvailableChainId()


    def getNextAvailableChainId(self ):
        for chainId in Chain.DEFAULT_ChainNamesByAlphabet:
            if not( self.has_key(chainId)):
                return chainId
        issueId = 130
        msg = "CING exhausted the available %d chain identifiers; see issue %d here:\n" % (
            len(Chain.DEFAULT_ChainNamesByAlphabet), issueId)
        msg += issueListUrl+`issueId`
        NTcodeerror(msg)

    def keepSelectedModels(self, modelListStr):

        try:
            selectedModels = self.models2list(modelListStr)
            selectedModelCount = len(selectedModels)
            if not selectedModelCount:
                NTerror("No models selected to keep which must be a bug; please check input string: [" + modelListStr + "]")
                return
            if selectedModelCount == self.modelCount:
                NTwarning("No models to delete from ensemble sticking with: [" + modelListStr + "]")
                return
            lastModelIdx = selectedModels[ - 1]
            if lastModelIdx >= self.modelCount:
                NTwarning("Last selected model index (" + `lastModelIdx` + ") is not in ensemble; please check input string: [" + modelListStr + "]")
                return

    #        NTdebug("Truncating ensemble to: [" + modelListStr +"]")
    #        NTdebug("verify this is the same as: [" + `selectedModels` +"]")

            modelToRemoveList = []
            l = range(self.modelCount)
            l.reverse()
            for m in l:
                if m not in selectedModels:
                    modelToRemoveList.append(m)
            NTmessage("Keeping  " + `len(selectedModels)` + " models : [" + `modelListStr` + "]")
            NTmessage("Removing " + `len(modelToRemoveList)` + " models : [" + `modelToRemoveList` + "]")

            for atm in self.allAtoms():
                atmCoordCount = len(atm.coordinates) # some atoms have no coordinates or just some
                for i in modelToRemoveList:
                    if i >= atmCoordCount:
                        continue
                    del(atm.coordinates[i])

            self.modelCount = selectedModelCount
            self.updateAll() # needed otherwise the dihedral.baddies get thru.
            NTdebug('After keepSelectedModels: %s' % self)
        except:
            NTerror("Failed keepSelectedModels; please check the input string [" + modelListStr + "]")

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
            NTerror( 'Molecule.addChain: chain "%s" already present', name )
            return None
        #end if
        chain = Chain( name=name, **kwds )
        self._addChild( chain )
        chain.molecule = self
        #self[chain]    = chain
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
            Decode a 7-element nameTuple
                (moleculeName, chainName, resNum, atomName, modelIndex, resonanceIndex, convention)
            or older 4-element nameTuple
                 (convention, chainName, resNum, atomName)

            generated with the nameTuple methods of Chain, Residue, or Atom Classes.
            Return a Molecule, Chain, Residue or Atom instance on success or
            None on error.

            If chain is given then the whole molecule is returned.
            If no residue is given then the whole chain is returned.
            ..etc..
            Caller is responsible for relaying error messages but debug
            statements within can be enabled from code.

         """
#        NTdebug("Now in decodeNameTuple for : "  + `nameTuple`)
        if nameTuple == None:
            return None

        if self._nameTupleDict.has_key(nameTuple):
            return self._nameTupleDict[nameTuple]

        if len(nameTuple) == 4:
            convention, chainName, resNum, atomName = nameTuple
            moleculeName = self.name
            resonanceIndex = None
            model = None
        else:
            moleculeName, chainName, resNum, atomName, model, resonanceIndex, convention = nameTuple

        if moleculeName != self.name: return None

#        if not fromCYANA2CING:
        if chainName == None:
            return self

        # has_key is faster perhaps as "in" iterates whereas has_key uses true dictionary lookup.
        if not self.has_key(chainName):
#            NTdebug( 'in molecule decodeNameTuple: in molecule ['+self.name+'] no chain Name: ['+chainName+']')
            return None

        chain = self[chainName]

        if resNum == None:
            self._nameTupleDict[nameTuple] = chain
            return chain

        if not chain.has_key(resNum):
#            NTdebug( 'in molecule decodeNameTuple: in chain ['+`chain`+'] no residue number: ['+`resNum`+']')
            return None
        res = chain[resNum]

        if atomName == None:
            self._nameTupleDict[nameTuple] = res
            return res

        resTranslated = res.translate(convention)
        an = translateAtomName( convention, resTranslated, atomName, INTERNAL )
#        if (not an or (an not in res)): return None
        if not an:
#            NTdebug("in Molecule.decodeNameTuple failed to translateAtomName for res: " + `resTranslated` + " and atom: " + `atomName`)
            return None

        if not res.has_key(an):
            NTdebug("in Molecule.decodeNameTuple atom not in residue: [%s]" % `an`)
            return None

        atm = res[an]
        # JFD modifies to include brackets. Otherwise the 'and' operator has a higher precedence than '==' etc,
        if (resonanceIndex == None) and (model == None):
            self._nameTupleDict[nameTuple] = atm
            return atm

        if (model != None) and (resonanceIndex == None) and (model<len(atm.coordinates)):
            c = atm.coordinates[model]
            self._nameTupleDict[nameTuple] = c
            return c

        if (model == None) and (resonanceIndex != None) and (resonanceIndex<len(atm.resonances)):
            r = atm.resonances[resonanceIndex]
            self._nameTupleDict[nameTuple] = r
            return r

        return None

#        else: # fromCYANA2CING
#            if chainName != None:
#                NTerror('Expected a None for chainName in Molecule.decodeNameTuple but got: [%s]' % chainName)
#                return None
#
#            for chain in self.allChains():
#                if resNum == None:
#                    return chain
#
#                if not chain.has_key(resNum):
##                    NTdebug( 'in molecule decodeNameTuple: in chain ['+`chain`+'] no residue number: ['+`resNum`+']')
#                    continue # perhaps in other chain?
#                res = chain[resNum]
#
#                if atomName == None:
#                    return res
#
#                resTranslated = res.translate(convention)
#                an = translateAtomName( convention, resTranslated, atomName, INTERNAL )
#
#                if not an:
#                    NTdebug("in Molecule.decodeNameTuple failed to translateAtomName for res: " + resTranslated + " and atom: " + atomName)
#                    return None
#
#                if not res.has_key(an):
#                    NTdebug("in Molecule.decodeNameTuple atom not in residue: [%s]" % `an`)
#                    return None
#                return res[an]
#            NTdebug("in Molecule.decodeNameTuple residue number [%s] not in any chain " % `resNum`)
#            return None
#        # end else
    #end def

    def nameTuple(self,convention=INTERNAL):
        """Return the 7-element name tuple:
           (moleculeName, chainName, resNum, atomName, modelIndex, resonanceIndex, convention)
        """
        return (self.name, None, None, None, None, None, convention)
    #end def

    def getResidue( self, resName, chains = None):
        """
        Return Residue instances corresponding to 'resName', or None if not
           found. Search all chains when chains = None.

           Since chain contain resNum, resName and <Residue> keys to <Residue> instances,
           either of these are valid for the 'resName' argument.
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

    def _getResNumDict(self):
        """
        Return dict instance with resNum, Residue mappings.
        For decoding usage with CYANA/XEASY routines
        """
        resNumDict = dict()
        for res in self.allResidues():
            if resNumDict.has_key(res.resNum):
                NTerror('Molecule._getResNumDict: multiple mapped residues (%s,%s)',
                        res, resNumDict[res,res.resNum]
                       )
            resNumDict[res.resNum] = res
        #end for
        return resNumDict
    #end def

    def _getAtomDict(self, convention=INTERNAL, ChainId = 'A'):
        """
        Return a dict instance with (resNum, atomName), Atom mappings.
        NB. atomName according to convention
        For decoding usage with CYANA/XEASY, and SHIFTX routines
        """
#        NTdebug("Creating mapping from (residue number, atom name) to atom object for chain: [%s]" % ChainId)
        atomDict = NTdict()
        for chain in self.allChains():
            if chain.name != ChainId:
#                NTdebug("Skipping add of different chain [%s] than requested [%s]" % (chain.name,ChainId ))
                continue
            for atm in chain.allAtoms():
                aname = atm.translate(convention)
                if aname != None:
                    t = (atm.residue.resNum, aname)
                    if atomDict.has_key( t ):
                        # GV needs to check if this still needs to be an error or as is, down graded to warning level.
                        # see example in H2_2Ca_53 with test_shiftx routine. FIXME:
                        # GV, Yes maintain, but  test for aname should reduce warnings
                        NTwarning('In Molecule._getAtomDict found multiple mapped atoms (new key, old key): (%-20s,%-20s)',
                                    atm, atomDict[t])
                    else:
                        atomDict[t] = atm
                    #end if
                #end if
            #end for
        #end for
        return atomDict
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

    def _save075( self, path = None)   :
        """Save sequence, resonances, stereo assignments and coordinates in <=0.75 format

           gwv 13 Jun 08: Return self or None on error
        """
        if not path: path = self.name + '.NTmol'

        content = NTdict( name = self.name, convention = INTERNAL )
        content.update( NTmolParameters )
        content.saveAllXML()
        content.keysformat()
        xmlfile = os.path.join( path, NTmolParameters.contentFile )
        if (obj2XML( content, path=xmlfile ) != content):
            NTerror('Molecule.save: writing xml file "%s" failed', xmlfile)
            return None
        #end if
        self.content = content
        self._saveSequence(   os.path.join( path, NTmolParameters.sequenceFile   ) )
        self._saveResonances(  os.path.join( path, NTmolParameters.resonanceFile  ) )
        self._saveStereoAssignments( os.path.join( path, NTmolParameters.stereoFile ) )
        self._saveCoordinates( os.path.join( path, NTmolParameters.coordinateFile ) )
#        NTdetail('==> Saved %s to "%s"', self, smlFile) # smlFile was undefined.
        NTdetail('==> Saved %s to "%s"', self )
        return self
    #end def

    def save( self, path = None)   :
        """Create a SML file
           Save sequence, resonances, stereo assignments and coordinates.
           Return self or None on error
        """
        if not path: path = self.objectPath
        if self.SMLhandler.toFile(self, path) != self:
            NTerror('Molecule.save: failed creating "%s"', path)
            return None
        #end if

        NTdetail('==> Saved %s to "%s"', self, path)
        return self
    #end def

    def open( path )   :
        """Static method to restore molecule from SML file path
           returns Molecule instance or None on error
        """
        if (not os.path.exists( path )):
            NTerror('Molecule.open: smlFile "%s" not found\n', path)
            return None
        #end if

        mol = Molecule.SMLhandler.fromFile(path)
        if not mol:
            NTerror('Molecule.open: open from "%s" failed', path)
            return None
        #end if

        mol._check()
        mol.updateAll()

        NTdetail('%s', mol.format())

        return mol
    #end def
    open = staticmethod(open)

    def _open075( path )   :
        """Static method to restore molecule from directory path
           implements the <=0.75 storage model
           returns Molecule instance or None on error
        """
        # old format
        NTdetail('Molecule._open075: opening from old format "%s"', path)

        if (not os.path.exists( path )):
            NTerror('Molecule._open075: path "%s" not found\n', path)
            return None
        #end if

        content = XML2obj( path=os.path.join( path, NTmolParameters.contentFile ) )
        if not content:
            NTerror('Molecule._open075: error reading xml file "%s"\n',
                     os.path.join( path, NTmolParameters.contentFile )
                   )
            return None
        #end if
        content.keysformat()
        NTdebug('content from xml-file: %s', content.format())

        mol = Molecule( name = content.name )
        if not mol:
            NTerror('Molecule._open075: initializing molecule\n')
            return None
        #end if

        mol.content = content
        if content.has_key('sequenceFile') and not mol._restoreSequence(    os.path.join( path, content.sequenceFile   ) ):
            return None
        if content.has_key('resonanceFile') and mol._restoreResonances(  os.path.join( path, content.resonanceFile  ), append=False ) < 0:
            return None
        if content.has_key('stereoFile') and mol._restoreStereoAssignments( os.path.join( path, content.stereoFile ) ) < 0:
            return None
        mol._restoreCoordinates( os.path.join( path, content.coordinateFile ), append=False )

        mol._check()
        mol.updateAll()

        NTdebug('%s', mol.format())

        return mol
    #end def
    _open075 = staticmethod(_open075)

    def _check(self):
        # check for potential atoms with incomplete resonances
        # Might occur after change of database
        # convert old NOSHIFT values to NaN
        for atm in self.allAtoms():
            for r in atm.resonances:
                if r.value == NOSHIFT:
                    r.value = NaN
                    r.error = NaN
                #end if
            #end for
            l = len(atm.resonances)
            if l < self.resonanceCount:
                NTdebug('Molecule._check: atom %s has only %d resonances; expected %d; repairing now',
                          atm, l, self.resonanceCount
                        )
                for _i in range(l,self.resonanceCount):
                    atm.addResonance()
                #end for
            #end if
        #end for
    #end def

    def _saveSequence( self, fileName ):
        """Write a xml sequence file.
        return self or None on error
        """
        sequence = NTlist()
        for res in self.allResidues():
            # append a tuple
            sequence.append( ( res.chain.name,
                               res.db.translate(CYANA),
                               res.resNum,
                               CYANA
                             )
                           )
        #end for
        if obj2XML( sequence, path=fileName ) != sequence:
            NTerror('Molecule._saveSequence: writing xml sequence file "%s"', fileName)
            return None
        #end if
        return self
    #end def

    def _restoreSequence( self, sequenceFile ):
        """Restore sequence from sequenceFile.
        Return self or None on error.
        """
        if (not os.path.exists( sequenceFile ) ):
            NTerror('Molecule.restoreSequence: sequenceFile "%s" not found\n',
                     sequenceFile
                   )
            return None
        #end if
        # compatibility
        if self.content.version < 0.92:
            file = open(sequenceFile, 'r')
            for line in file:
                exec(line)
            #end for
            file.close()
        else:
            sequence = XML2obj( sequenceFile )
            if sequence == None:
                NTerror('Molecule._restoreSequence: error parsing xml-file "%s"', sequenceFile)
                return None
            for chainId, resName, resNum, convention in sequence:
                self._addResidue( chainId, resName, resNum, convention )
            #end for
        #end if
        #NTdebug('Molecule._restoreSequence: %s', sequenceFile)
        return self
    #end def

    def _saveResonances( self, fileName ):
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
        #NTdebug('Molecule.saveResonances: %s', fileName)
    #end def

    def _restoreResonances( self, fileName, append = True ):
        """Restore resonances from fileName
           Optionally append to existing settings
           Return resonanceCount or -1 on error
        """
        if not os.path.exists( fileName ):
            NTerror('Error Molecule._restoreResonances: file "%s" not found\n', fileName )
            return -1
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

        #NTdebug('Molecule.restoreResonances: %s (%d)', fileName, self.resonanceCount)
        return self.resonanceCount
    #end def

    def newResonances( self, source=None ):
        """Initialize a new resonance slot for every atom.
           atom.resonances() will point to this new resonance.
        """
        if not source:
            source = 'source_%d' % self.resonanceCount
        for atom in self.allAtoms():
            atom.addResonance()
        #end for
        self.resonanceCount += 1
        self.resonanceSources.append(source)
    #end def

    def initResonances( self)   :
        """ Initialize resonances for all the atoms
        """
        for atom in self.allAtoms():
            atom.resonances = NTlist()
        #end for
        self.resonanceCount = 0
        self.resonanceSources = NTlist()
        #NTmessage("==> Initialized resonances")
        #end if
    #end def

    def mergeResonances( self, order=None, selection=None, append=True ):
        """ Merge resonances for all the atoms
            check all the resonances in the list, optionally using selection
            and take the first one which has a assigned value,
            append or collapse the resonances list to single entry depending on append.
        """
        for atom in self.allAtoms():
            if ( len(atom.resonances) != self.resonanceCount ):
                NTerror('Molecule.mergeResonances %s: length resonance list (%d) does not match resonanceCount (%d)',
                         atom, len(atom.resonances), self.resonanceCount
                       )
                return
            else:
                rm = None
                if (selection == None or atom.name in selection):
                    for res in atom.resonances:
                        if not isNaN(res.value):
                            rm=res
                            break
                        #end if
                    #end for
                #end if
            #end if

            if (rm):
                atom.resonances.append(rm)
            else:
                rm = atom.resonances[0]
                atom.resonances.append(rm)
            #end if

            # Optionally reduce the list
            if not append:
                atom.resonances = NTlist( atom.resonances() )
        #end for

        if not append:
            self.resonanceCount = 1
            self.resonanceSources = NTlist('merged')
        else:
            self.resonanceCount += 1
            self.resonanceSources.append('merged')
        #end if
    #end def

    def _saveStereoAssignments( self, stereoFileName ):
        """
        Save the stereo assignments to xml stereoFileName.
        Return self of None on error
        """
        stereo = NTlist()
        for atm in self.allAtoms():
            if atm.isStereoAssigned():
                stereo.append( atm.nameTuple(convention=CYANA) )
            #endif
        #end for
        if obj2XML(stereo, path=stereoFileName) != stereo:
            NTerror('Molecule._saveStereoAssignments: write xml-file "%s" failed', stereoFileName)
            return None
        #end if

        #NTdebug('Molecule.saveStereoAssignments: saved %d stereo assignments to "%s', len(stereo), stereoFileName)
        return self
    #end def

    def _restoreStereoAssignments( self, stereoFileName ):
        """
        Restore the stereo assignments from xml stereoFileName,
        return count or -1 on error
        """
        if not os.path.exists( stereoFileName ):
            return -1

        stereo = XML2obj(stereoFileName)
        if stereo == None:
            NTerror('Molecule._restoreStereoAssignment: parsing xml-file "s"', stereoFileName)
            return -1
        #end if

        count = 0
        for nameTuple in stereo:
            atm = self.decodeNameTuple( nameTuple )
            if atm == None:
                NTerror('Molecule._restoreStereoAssignment: invalid atom nameTuple (%s)', nameTuple)
            else:
                atm.stereoAssigned = True
                count += 1
            #end if
        #end for

        #NTdebug('Molecule.restoreStereoAssignments: restored %d stereo assignments from "%s\n',count, stereoFileName)
        return count
    #end def

    def _saveCoordinates( self, fileName ):
        """Write a plain text file with code for saving coordinates"""
        fp = open( fileName, 'w' )
        fprintf( fp, 'self.modelCount = %d\n', self.modelCount )
        for atm in self.allAtoms():
            for c in atm.coordinates:
                fprintf( fp, 'self%s.addCoordinate( %r, %r, %r, Bfac=%r )\n',
                              atm._Cname2( 2 ), c[0], c[1], c[2], c.Bfac)
        fp.close()
        #NTdebug('Molecule.saveCoordinates: %s', fileName)

    def _restoreCoordinates( self, fileName, append = True ):
        """Restore coordinates from fileName
           Optionally append to existing settings
           Return self or None on error
        """
        if not os.path.exists( fileName ):
            NTerror('Error Molecule._restoreCoordinates: file "%s" not found\n', fileName )
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
        #NTdebug('Molecule.restoreCoordinates: %s (%d)', fileName, self.modelCount)
        return self
    #end def

    def initCoordinates(self):
        """
        Initialize the coordinate lists of all atoms
        set modelCount to 0
        """
        for atm in self.allAtoms():
            atm.coordinates = NTlist()
        self.modelCount = 0

    def updateTopology( self)   :
        """Define the _topology key for all atoms.
        """
        NTdebug('Defining topology')
        for residue in self.allResidues():
            for atm in residue:
                atm._topology = NTlist()
                if atm.db:
                    topDef = atm.db.topology
                    # manage N- and C-terminal exceptions
                    if residue.Nterminal and len(atm.db.NterminalTopology) > 0:
                        topDef = atm.db.NterminalTopology
                    if residue.Cterminal and len(atm.db.CterminalTopology) > 0:
                        topDef = atm.db.CterminalTopology

                    for i,atomName in topDef:
                        try:
                            idx = int(i)
                            res = residue.sibling( idx )
                            if res == None or not res.has_key( atomName ):
                                result.append( None )
                                continue
                            atm._topology.append( res[atomName] )

                        except:
                            pass # exceptional cases here
                        #end try
                    #end for
                else:
                    NTdebug('Molecule.updateTopolgy: atm %s: odd db==None', atm)
                #end if
            #end for
        #end for
    #end def

    def updateDihedrals( self)   :
        """Calculate the dihedral angles for all residues
        """
        NTdebug('Calculating dihedral angles')
        for res in self.allResidues():
#            res.addAllDihedrals()
            for d in res.dihedrals:
                d.calculateValues()
            #end for
        #end for
    #end def

    def updateMean( self):
        """Calculate mean coordinates for all atoms
        """
        NTdebug('modelCount: %d; Calculating mean coordinates', self.modelCount)
        for atm in self.allAtoms():
            atm.calculateMeanCoordinate()

    def idDisulfides(self):
        """Just identify the disulfide bonds.
        """
        CUTOFF_SCORE = 0.9 # Default is 0.9
        NTdebug('Identify the disulfide bonds.')
        cys=self.residuesWithProperties('CYS')
        cyss=self.residuesWithProperties('CYSS') # It might actually have been read correctly.
        for c in cyss:
            if c not in cys:
                cys.append(c)
        pairList = []
        cyssDict2Pair = {}
        # all cys(i), cys(j) pairs with j>i
        for i in range(len(cys)):
            c1 = cys[i]
            for j in range(i+1, len(cys)):
                c2 = cys[j]
                scoreList = disulfideScore( c1, c2)
#                if cing.verbosity > cing.verbosityDebug: # impossible of course
                if False:
                    da = c1.CA.distance( c2.CA )
                    db = c1.CB.distance( c2.CB )
                    dg = c1.SG.distance( c2.SG )
                    chi3SS( db[0] )
                    NTdebug( 'Considering pair : %s with %s' % (c1, c2))
                    NTdebug( 'Ca-Ca            : %s', da)
                    NTdebug( 'Cb-Cb            : %s', db)
                    NTdebug( 'Sg-Sg            : %s', dg)
                    NTdebug( 'chi3             : %s', chi3SS( db[0] ))
                    NTdebug( 'scores           : %s', disulfideScore( c1, c2))
                    NTdebug( '\n\n' )
                if scoreList[3] >= CUTOFF_SCORE:
                    toAdd = True
                    for c in ( c1, c2 ):
                        if cyssDict2Pair.has_key( c ):
                            toAdd = False
                            c_partner_found_before = cyssDict2Pair[c][0]
                            if c_partner_found_before == c:
                                c_partner_found_before = cyssDict2Pair[c][1]
                            c_partner_found = c1
                            if c_partner_found == c:
                                c_partner_found = c2
                            NTwarning('%s was id-ed before with %s so not pairing with %s (no effort will be done to optimize)' % (
                                  c, c_partner_found_before, c_partner_found ))
                    if toAdd:
                        pair = (c1, c2)
                        pairList.append(pair)
                        cyssDict2Pair[c1] = pair
                        cyssDict2Pair[c2] = pair
        if pairList:
            NTmessage( '==> Molecule %s: Potential disulfide bridges: %d' %( self.name, len(pairList)))
            for pair in pairList:
                NTdebug( '%s %s' % (pair[0], pair[1] ))
        else:
            NTdetail( '==> Molecule %s: No potential disulfide bridged residues found', self.name )
    # end def

    def syncModels(self ):
        """E.g. entry 1brv has more atoms in the second than in the first model. CING will not include those extra
        atoms
        """
        atomListToSyncToSink = []
        n = self.modelCount
        for atom in self.allAtoms():
            if atom.isPseudoAtom():
                continue
            actualCoordinateListLength = len(atom.coordinates)
            # The pseudos above handled and the atoms for which normally there are no coordinates
            # will be saved.
            if (actualCoordinateListLength == 0) or (actualCoordinateListLength == n):
                continue
            atomListToSyncToSink.append(atom)

        if not atomListToSyncToSink:
            return

        unmatchedAtomByResDict = {}
        for atom in atomListToSyncToSink:
            res = atom._parent
            if not res.deleteAtom(atom.name):
                NTcodeerror("Failed to delete atom %s from residue %s" % ( atom, res ))
            # JFD: Report all together now.
            if not unmatchedAtomByResDict.has_key(res.resName):
                unmatchedAtomByResDict[ res.resName ] = ([],[])
            atmList = unmatchedAtomByResDict[res.resName][0]
            resNumList = unmatchedAtomByResDict[res.resName][1]
            if atom.name not in atmList:
                atmList.append(atom.name)
            if res.resNum not in resNumList:
                resNumList.append(res.resNum)

        if unmatchedAtomByResDict:
            msg = "Molecule#syncModels Removed atoms that differ over the different models:\n"
            msg += unmatchedAtomByResDictToString(unmatchedAtomByResDict)
            NTwarning(msg)


    def updateAll( self)   :
        """Define and calculate the dihedral angles for all residues
           Calculate mean coordinates for all atoms
           Generate an ensemble from coordinates
           Generate an atomList
           Define the topological connections
           Calculate the rmsd's
        """
        for res in self.allResidues():
            res.addAllDihedrals()
        if self.modelCount > 0:
            self.syncModels()
            self.updateDihedrals()
            self.updateMean()
            self.ensemble = Ensemble( self )
            self.atomList = AtomList( self )
            self.idDisulfides()
            if not self.has_key('ranges'):
                self.ranges = None
            self.calculateRMSDs(ranges=self.ranges)
        #end if

        self.updateTopology()
    #end def


    def initialize( name, path = None, convention=LOOSE, **kwds   ):

        """
Static method to initialize a Molecule from a file
Return an Molecule instance or None on error

       fromFile:  File ==  <resName1 [resNum1] [chainId1]
                            resName2 [resNum2] [chainId2]
                            ...
                           >
        """
        #print '>', path, convention
        molecule = Molecule( name=name, **kwds )

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
                chainId = molecule.ensureValidChainId( chainId )

                molecule._addResidue( chainId, resName, resNum, convention )
        NTmessage("%s", molecule.format())
        return molecule
    #end def
    initialize = staticmethod( initialize )

    def _addResidue( self, chainId, resName, resNum, convention, Nterminal=False, Cterminal=False ):
        """
        Internal routine to add a residue to molecule
        Add chain if not yet present

        return Residue instance or None or error
        """
#        rn = translateResidueName( convention, resName, INTERNAL )
#        if (rn == None):
#            NTerror('Molecule._addResidue: chain %s, residue "%s" not valid for convention "%s"',
#                     chainId, resName, convention
#                   )
#            return None
#        else:
#            if chainId == None:
#                chainId = Chain.defaultChainId
#
#            if chainId not in self:
#                chain = self.addChain(chainId)
#            else:
#                chain = self[chainId]
#            #end if
#            if not chain: return None
#
#            # Add the residue if not present
#            if resNum in chain:
#                return chain[resNum]
#            #end if
#            residue = chain.addResidue( rn, resNum, Nterminal=Nterminal, Cterminal=Cterminal )
#            if not residue: return None
#
#            # Use database to add atoms
#            residue.addAllAtoms()
#        #end if

        if chainId == None:
            chainId = Chain.defaultChainId

        if chainId not in self:
            chain = self.addChain(chainId)
        else:
            chain = self[chainId]
        #end if
        if not chain: return None

        # Add the residue if not present
        if resNum in chain:
            return chain[resNum]
        #end if
        residue = chain.addResidue( resName, resNum, convention=convention, Nterminal=Nterminal, Cterminal=Cterminal )
        if not residue: return None

        # Use database to add atoms
        residue.addAllAtoms()

        return residue
    #end def

    def residuesWithProperties(self, *properties ):
        """
        Return a NTlist instance with Residues that have properties
        """
        result = NTlist()

        if not len(properties):
            return result
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

    def hasAminoAcid(self):
        for res in self.allResidues():
            if res.hasProperties('protein'):
                return True
        return None # is actually the default of course.

    def superpose( self, ranges=None, backboneOnly=True, includeProtons = False, iterations=2 ):
        """
        Superpose the coordinates of molecule
        returns ensemble or NoneObject on error
        """

        if self.modelCount <= 0:
            return NoneObject
        #end if

##        self.ensemble = Ensemble( molecule )

        # Partition the Atoms
        fitted        = []
        notFitted     = []
        noCoordinates = []
        fitResidues   = self.ranges2list( ranges )
        # store the ranges
        self.ranges   = list2asci( fitResidues.zap('resNum'))

        for res in self.allResidues():
            fitResidue = res in fitResidues
            for a in res.allAtoms():
                if len(a.coordinates) != self.modelCount:
                    noCoordinates.append( a )
                    continue
                if ( (not fitResidue) or
                     (not includeProtons and a.isProton()) ):
                    notFitted.append( a )
                    continue
                if backboneOnly and a.isSidechain():
                    notFitted.append( a )
                else:
                    fitted.append( a )
                #end if
            #end for
        #end for
        #print fitted

        NTmessage("==> Superposing: fitted %s on %d atoms (ranges=%s, backboneOnly=%s, includeProtons=%s)",
                      self, len(fitted), ranges, backboneOnly, includeProtons
                 )
        self.ensemble.superpose( fitted, iterations=iterations )
        NTdebug("... rmsd's: [ %s] average: %.2f +- %.2f",
                self.ensemble.rmsd.format('%.2f '), self.ensemble.rmsd.av, self.ensemble.rmsd.sd
               )
        r = self.calculateRMSDs(ranges=ranges)
        NTdetail( r.format() )
        return self.ensemble
    #end def


    def calculateRMSDs( self, ranges=None, models = None   ):
        """
        Calculate the positional rmsd's. Store in rmsd attributes of molecule and residues
        Optionally  select for ranges and models.
        return rmsd result of molecule, or None on error
        """

        if self.modelCount == 0:
            NTerror('Molecule.calculateRMSDs: no coordinates for %s', self)
            return None
        #end if

        NTdebug("Calculating rmsd's (ranges: %s, models: %s)", ranges, models)

        selectedResidues = self.ranges2list( ranges )
        selectedModels   = self.models2list( models )

        self.rmsd = RmsdResult( selectedModels, selectedResidues, comment='Residues ' + list2asci( selectedResidues.zap('resNum')) )
        for res in self.allResidues():
            res.rmsd = RmsdResult( selectedModels,  NTlist( res ), comment = res.name )
            res.rmsd.bbtemp = NTlist() # list of included bb-atms
            res.rmsd.hvtemp = NTlist() # list of included heavy-atms

            for atm in res.allAtoms():
                if not atm.isProton() and len(atm.coordinates)>0:
                    res.rmsd.hvtemp.append(atm)
                    if not atm.isSidechain():
                        res.rmsd.bbtemp.append(atm)
            #end for
            res.rmsd.backboneCount   = len(res.rmsd.bbtemp)
            res.rmsd.heavyAtomsCount = len(res.rmsd.hvtemp)
            if res in selectedResidues:
                res.rmsd.included = True
                self.rmsd.backboneCount += res.rmsd.backboneCount
                self.rmsd.heavyAtomsCount += res.rmsd.heavyAtomsCount
                #print '>>',res.rmsd.bbtemp
            else:
                res.rmsd.included = False
            #end if
        #end for

        for res in self.allResidues():
            if res.rmsd.backboneCount > 0:
                Vmean = []
                for atm in res.rmsd.bbtemp:
                    Vmean.append(atm.meanCoordinate.e)
                #end for
                for i,model in enumerate(selectedModels):   # number of evaluated models (does not have to coincide with model
                                                            # since we may supply an external list
                    Vbb = []
                    for atm in res.rmsd.bbtemp:
                        # JFD: when there are 2 models of 1brv and VAL H1 is only present in the second model
                        # the len is 1 and model will become 1.
                        if len(atm.coordinates)>=(model+1): # JFD adds because for now I don't seem to be able to do Residue#deleteAtom.
                            Vbb.append(atm.coordinates[model].e)
                        else:
                            Vbb.append(atm.coordinates[0].e)
                            NTcodeerror("TODO: fix Residue#deleteAtom.")
                    #end for
                    res.rmsd.backbone[i] = calculateRMSD(Vbb,Vmean)

                    if res.rmsd.included:
                        self.rmsd.backbone[i] += (res.rmsd.backbone[i]**2)*res.rmsd.backboneCount
                    #end if
                #end for
            #end if
            if res.rmsd.heavyAtomsCount > 0:
                Vmean = []
                for atm in res.rmsd.hvtemp:
                    Vmean.append(atm.meanCoordinate.e)
                #end for
                for i,model in enumerate(selectedModels):   # number of evaluated models (does not have to coincide with model
                                                            # since we may supply an external list
                    Vhv = []
                    for atm in res.rmsd.hvtemp:
                        if len(atm.coordinates)>=(model+1): # JFD adds because for now I don't seem to be able to do Residue#deleteAtom.
                            Vhv.append(atm.coordinates[model].e)
                        else:
                            Vhv.append(atm.coordinates[0].e)
                            NTcodeerror("TODO: fix Residue#deleteAtom.")
                    #end for
                    res.rmsd.heavyAtoms[i] = calculateRMSD(Vhv,Vmean)

                    if res.rmsd.included:
                        self.rmsd.heavyAtoms[i] += (res.rmsd.heavyAtoms[i]**2)*res.rmsd.heavyAtomsCount
                    #end if
                #end for
            #end if
            res.rmsd._closest()
            res.rmsd._average()
        #end for

        for i, model in enumerate(selectedModels):
            self.rmsd.backbone[i]   = math.sqrt(self.rmsd.backbone[i]/max(self.rmsd.backboneCount,1))
            self.rmsd.heavyAtoms[i] = math.sqrt(self.rmsd.heavyAtoms[i]/max(self.rmsd.heavyAtomsCount,1))
        #end for
        self.rmsd._closest()
        self.rmsd._average()

        return self.rmsd
    #end def

    def toPDB(self, model=None, convention=IUPAC, max_models=None):
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
            models = NTlist(model)

        if max_models:
            if len(models) > max_models:
                models = models[0:max_models]

#        NTdebug("==> Exporting to PDB file (%s convention, models: %d-%d) ... ",
#                   convention, models[0], models.last()                 )

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
                    if not record:
                        NTwarning("Failed to create a PDB file terminating record; ignoring for now.")
                        continue
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

    def toSML(self, stream=sys.stdout ):
        if hasattr(Molecule,'SMLhandler'):
            Molecule.SMLhandler.toSML( self, stream )
        else:
            NTerror('Molecule.toSML: no SMLhandler defined')
        #end if
    #end def
#end class



class Ensemble( NTlist ):
    """
    Ensemble class hold is a list of Models instances.
    Initialization is done from a Molecule instance, thus the class represents
    a different arrangement of the coordinate instances of a molecule.
    """
    def __init__( self, molecule ):
        NTlist.__init__( self )
        self.averageModel = None
        self.molecule     = molecule

        for i in range(0,molecule.modelCount):
            m = Model('model'+str(i), i )
            self.append( m )
        #end for
        self.averageModel = Model('averageModel', molecule.modelCount )

        # Assemble the coordinates of the models
        for atm in molecule.allAtoms():
            if len(atm.coordinates) == molecule.modelCount:
                for i in range(0,molecule.modelCount):
                    self[i].coordinates.append( atm.coordinates[i] )
                #end for
                self.averageModel.coordinates.append( atm.meanCoordinate )
            #end if
        #end for
    #end def

    def calculateAverageModel( self ):
        """
        Calculate averageModel from members of self
        Calculate rmsd to average for each model using fitCoordinates
        and store values in NTlist instance in rmsd attribute of self
        Set rmsd of average model to <rmsd>
        Return averageModel or None on error

        """
        for atm in self.molecule.allAtoms():
            atm.calculateMeanCoordinate()
        #end for
        self.rmsd = NTlist()
        for m in self:
            self.rmsd.append( m.calculateRMSD( self.averageModel ) )
        #end for
        self.averageModel.rmsd, _tmp, _tmp = self.rmsd.average()
        return self.averageModel
    #end def

    def setFitCoordinates( self, fitAtoms ):
        """
        Initialize the fitCoordinates lists of models of self from fitAtoms
        """
        for model in self:
            model.fitCoordinates = NTlist()
        #end for
        self.averageModel.fitCoordinates = NTlist()

        for atm in fitAtoms:
            for i in range(0, len(self) ):
                self[i].fitCoordinates.append( atm.coordinates[i] )
            #end for
            self.averageModel.fitCoordinates.append( atm.meanCoordinate )
        #end for
    #end def

    def superpose( self, fitAtoms, iterations=2 ):
        """
        superpose the members of the ensemble using fitAtoms
        calculate averageModel

        iteration 0: superpose on model[0]
        iterations 1-n: calculate average; superpose on average

        return averageModel or None on error
        """
        if len( self) == 0 or len( fitAtoms ) == 0:
            return None
        #end if

        # Assemble the coordinates for the fitting
        self.setFitCoordinates( fitAtoms )

        # iteration 1: fit to first model
        m0 = self[0]
        for m in self[1:]:
            if len(m.fitCoordinates) != len(m0.fitCoordinates):
                return None
            #end if
            m.superpose( m0 )
        #end for

        niter = 1
        while ( niter < iterations ):
            av = self.calculateAverageModel()
            for m in self:
                m.superpose( av )
            #end for
            niter = niter + 1
        #end while

        return self.calculateAverageModel()
    #end def

    def __str__( self ):
        return sprintf( '<Ensemble ("%s", models:%d, rmsd to mean: %.2f)>',
                        self.molecule.name, len(self), self.averageModel.rmsd
                      )
    #end def

    def __repr__( self ):
        return str(self)
    #end def

    def format( self ):
        return str( self )
    #end def
#end class


class Model( NTcMatrix ):
    """
    Model class, rotation translation 4x4  superpose
    Contains a list of fitCooridinates and

    """
    def __init__( self, name, index ):

        NTcMatrix.__init__( self )
        self.name              = name
        self.index             = index
        self.coordinates       = NTlist()  # All coordinate instances of Model
        self.fitCoordinates    = NTlist()  # Coordinates used for fitting
        self.rmsd              = 0.0
    #end def

    def superpose( self, other ):
        """
        Superpose coordinates of self onto other.
        Use vectors of fitCoordinates for superposition.
        return rmsd between self and other using fitCoordinates or -1.0 on Error
        """
        v1 = self.fitCoordinates.zap( 'e' )
        v2 = other.fitCoordinates.zap( 'e' )
        if len(v1) != len(v2):
            NTerror("Model.superpose: unequal length fitCoordinates (%s and %s)", self, other)
            return -1.0
        #end if

        smtx = superposeVectors( v1, v2 )
        #copy the result to self
        smtx.copy( self )

        # transform and calculate rmsd
        self.transform()
        self.rmsd = calculateRMSD( v1, v2 )
        return self.rmsd
    #end def

    def calculateRMSD( self, other ):
        """
        Calculate rmsd of fitCoordinates of Model with respect to other
        store in rmsd attribute
        return rmsd or -1.0 on Error
        """
        v1 = self.fitCoordinates.zap( 'e' )
        v2 = other.fitCoordinates.zap( 'e' )
        if len(v1) != len(v2):
            NTerror("Model.calculateRMSD: unequal length fitCoordinates (%s and %s)", self, other)
            return -1.0
        #end if
        self.rmsd = calculateRMSD( v1, v2 )
        return self.rmsd
    #end def

    def transform( self ):
        # Transform all coordinates according to rotation/translation matrix
        for c in self.coordinates:
            self.transformVector( c.e )
        #end for
    #end def

    def __str__( self ):
        return sprintf('<Model "%s" (coor:%d,fit:%d)>', self.name, len(self.coordinates), len(self.fitCoordinates) )
    #end def

    def __repr__( self ):
        return str(self)
    #end def

    def format( self ):
        # generate a string representation
        s = sprintf('%s %s %s\n', dots, str(self), dots)
        s = s + "rmsd:  %10.3f\n" %  (self.rmsd, )
        s = s + "matrix:\n%s\n" % (NTcMatrix.__str__(self), )
        return s
    #end def
#end class


class RmsdResult( NTdict ):
    """Class to store rmsd results
    """
    def __init__(self, modelList, ranges, comment='' ):
        NTdict.__init__( self,
                         __CLASS__       = 'RmsdResult',
                         backbone        = NTfill(0.0, len(modelList)),
                         backboneCount   = 0,
                         backboneAverage = NTvalue( NaN, NaN, fmt='%4.2f (+- %4.2f)', fmt2='%4.2f' ),

                         heavyAtoms      = NTfill(0.0, len(modelList)),
                         heavyAtomsCount = 0,
                         heavyAtomsAverage = NTvalue( NaN, NaN, fmt='%4.2f (+- %4.2f)', fmt2='%4.2f'  ),

                         models          = modelList,
                         closestToMean   = -1,    #indicates undefined
                         ranges          = ranges,
                         comment         = comment
                       )
    #end def

    def _closest(self):
        """Internal routine to calculate the model closest to mean
        """
        c = zip(self.heavyAtoms, self.models)
        c.sort()
        self.closestToMean = c[0][1]
    #end def

    def _average(self):
        """Calculate the averages
        """
        self.backboneAverage.value, self.backboneAverage.error, _n = self.backbone.average()
        self.heavyAtomsAverage.value, self.heavyAtomsAverage.error, _n = self.heavyAtoms.average()
    #end def

    def __str__(self):
        return sprintf('<RmsdResult %s>', self.comment)

    def header(self, dots='-'*20):
        return sprintf('%s %s %s', dots, self, dots)

    def format(self):
        return sprintf('%s\n' +\
                       'backboneAverage:      %s\n'  +\
                       'heavyAtomsAverage:    %s\n'  +\
                       'models:               %s\n' +\
                       'backbone   (n=%4d): [%s]\n' +\
                       'heavyAtoms (n=%4d): [%s]\n' +\
                       'closestToMean:        model %d\n' +\
                       '%s',
                       self.header(),
                       str(self.backboneAverage),
                       str(self.heavyAtomsAverage),
                       self.models.format('%4d '),
                       self.backboneCount,
                       self.backbone.format(fmt='%4.2f '),
                       self.heavyAtomsCount,
                       self.heavyAtoms.format(fmt='%4.2f '),
                       self.closestToMean,
                       self.footer()
                      )
    #end def
#end class


#class XMLMoleculeHandler( XMLhandler ):
#    """Molecule handler class"""
#    def __init__( self ):
#        XMLhandler.__init__( self, name='Molecule')
#    #end def
#
#    def handle( self, node ):
#        attrs = self.handleDictElements( node )
#        if attrs == None: return None
#        result = Molecule( name = attrs['name'] )
#
#        # update the attrs values
#        result.update( attrs )
#
#        # restore the tree structure
#        for child in result._children:
##           print '>child>', repr(child)
#            result[child.name] = child
#            child._parent = result
#        return result
#    #end def
##end class
#
##register this handler
#Molecule.XMLhandler = XMLMoleculeHandler()


#
#==============================================================================
#






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
        printAttr()             : Print a list of all attributes and their values.

    all dict methods
    """

    DEFAULT_ChainNamesByAlphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ^01234567890abcdefghijklmnopqrstuvwxyz'
#    validChainIdListBesidesTheAlphabet = '^' # last 1 chars of above.; JFD removed pound and underscore because they have a special meaning in STAR files.
    'Nothing that is a special character in Python, or tcsh.'
    defaultChainId = 'A'
    'See documentation: molecule#ensureValidChainId'

    NULL_VALUE = 'CHAIN_CODE_NULL_VALUE' # can not be a valied chain code but needs to be able to be passed on commandline
    # like in: Scripts/getPhiPsiWrapper.py

    def __init__( self, name, **kwds ):
        NTtree.__init__( self, name=name, __CLASS__='Chain', **kwds )
        self.__FORMAT__ =  self.header( dots ) + '\n' +\
                          'residues (%(residueCount)d): %(residues)s\n' +\
                           self.footer( dots )
        self.rogScore = ROGscore()
        self.residues = self._children
        self.residueCount = 0
    #end def

    def __repr__(self):
        return str(self)
    #end def

    def isNullValue(id):
        return id == Chain.NULL_VALUE
    isNullValue = staticmethod( isNullValue )

    def addResidue( self, resName, resNum, convention=INTERNAL, Nterminal=False, Cterminal=False, **kwds ):
        if self.has_key(resNum):
            NTerror( 'Chain.addResidue: residue number "%s" already present in %s', resNum, self )
            return None
        #end if
        res = Residue( resName=resName, resNum=resNum, convention=convention, Nterminal=Nterminal, Cterminal=Cterminal, **kwds )
        if res.name in self:
            NTerror( 'Chain.addResidue: residue "%s" already present in %s', res.name, chain )
            return None
        #end if
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
            NTerror( 'Chain.removeResidue: residue "%s" not present in chain %s',
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
            NTerror('Chain.removeResidue: error removing %s from %s', residue, self)
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
        """Return the 7-element name tuple:
           (moleculeName, chainName, resNum, atomName, modelIndex, resonanceIndex, convention)
        """
        return (self.molecule.name, self.name, None, None, None, None, convention)
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

    def toSML(self, stream=sys.stdout ):
        if hasattr(Chain,'SMLhandler'):
            Chain.SMLhandler.toSML( self, stream )
        else:
            NTerror('Chain.toSML: no SMLhandler defined')
        #end if
    #end def

#end class

#class XMLChainHandler( XMLhandler ):
#    """Chain handler class"""
#    def __init__( self ):
#        XMLhandler.__init__( self, name='Chain')
#    #end def
#
#    def handle( self, node ):
#        attrs = self.handleDictElements( node )
#        if attrs == None: return None
#        result = Molecule( name = attrs['name'] )
#
#        # update the attrs values
#        result.update( attrs )
#
#        # restore the tree structure and references
#        for res in result._children:
##           print '>child>', repr(child)
#            result[res.name] = res
#            result[res.shortName] = res
#            result[res.resNum] = res
#            res._parent = result
#        return result
#    #end def
##end class
#
##register this handler
#Chain.XMLhandler = XMLChainHandler()

class Residue( NTtree ):
    """
-------------------------------------------------------------------------------
Residue class: Defines residue properties
-------------------------------------------------------------------------------
    Initiating attributes:
        resName                 : Residue name according to the nomenclature convention.
        resNum                  : Unique residue number within this chain.
        convention              : Convention descriptor; eg. INTERNAL, CYANA2, IUPAC

    Derived attributes:
        atoms                   : NTlist of Atom instances.
        db                      : Reference to database residueDef instance
        chain                   : Reference to Chain instance
        dihedrals               : NTlist of Dihedral instances

    """
    def __init__( self, resName, resNum, convention=INTERNAL, Nterminal=False, Cterminal=False, **kwds ):
        #print '>',resName, resNum
        NTtree.__init__(self, __CLASS__ = 'Residue',
                              name=resName + str(resNum),    # Only a temporarily name, will be formalised after
                                                             # this init
                              Nterminal = Nterminal,         # defines the residue to be N-terminus
                              Cterminal = Cterminal,         # defines the residue to be C-terminus
                              **kwds
                       )
        self._nameResidue( resName, resNum, convention=convention ) # sets all naming and links correctly

        self.atoms     = self._children
        self.atomCount = 0
        self.chain     = self._parent

        self.dihedrals = NTlist()

        self.rogScore = ROGscore()

        self.__FORMAT__ =  self.header( dots ) + '\n' +\
                          'shortName:  %(shortName)s\n' +\
                          'chain:      %(chain)s\n' +\
                          'atoms (%(atomCount)2d): %(atoms)s\n' +\
                           self.footer( dots )
    #end def

    def __repr__(self):
        return str(self)
    #end def

    def toString(self, showChainId=True, showResidueType=True):
        """A unique compact string identifier.e.g B.LYS282"""
        if showChainId:
            chn = self._parent
            result = chn.name + '.'
        else:
            result = ''
        if showResidueType:
            result += self.name
        else:
            result += self.number
        return result

    def _nameResidue( self, resName, resNum, convention = INTERNAL ):
        """Internal routine to set all the naming right and database references right
        """
        # find the database entry in NTdb (which is of type MolDef)
        db = NTdb.getResidueDefByName( resName, convention )
        if not db:
            NTwarning('Residue._nameResidue: residue "%s" not defined in database by convention [%s]. Adding non-standard one now.' %( resName, convention))
            self.db = NTdb.appendResidueDef( name=resName, shortName = '_' )
            x = NTdb.getResidueDefByName( resName, convention )
            if not x:
                NTcodeerror("Added residue but failed to find it again")
        #end if
        self.resNum   = resNum
        if not db:
            self.name      = resName + str(resNum)
            self.resName   = resName
            self.shortName = '_' + str(resNum)
#            self.db        = None # JFD adds: It's erased again? Must be a bug.
        else:
            self.db        = db
            self.name      = db.translate(INTERNAL) + str(resNum)
            self.resName   = db.translate(INTERNAL)
            self.shortName = db.shortName + str(resNum)
        #end if
        # add the two names to the dictionary
        self.names     = [self.shortName, self.name]
    #end def

    def renumber( self, newResNum ):
        """
        Renumber residue
           Return self or None on error
        """
        if newResNum in self._parent:
            NTerror( 'ERROR Residue.renumber: residue  number "%s" already present\n', newResNum )
            return None
        #end if
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
        Mutate residue to resName:
            Generate newResidue <Residue> instance.
            Move the 'like' atoms from self to newResidue.
            Replace self by newResidue in chain.

        Return (self,newResidue) tuple or None on error
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
                for alias in atm.db.aliases:
                    if alias in self:
                        del(self[alias])
                #end for
                self.atomCount -= 1
                atm.residue = newRes
                newRes._addChild( atm )
                newRes.atomCount += 1
                newRes.chain.molecule.atomCount += 1
                for alias in atm.db.aliases:
                    newRes[alias] = atm
                #end for
            else:
                atm = newRes.addAtom( atmDef.name )
                for dummy in range(newRes.chain.molecule.resonanceCount):
                    atm.addResonance()
                #end for
            #end if
        #end for

        return self,newRes
    #end def

    def deleteAtom(self, name, convention=INTERNAL ):
        """JFD adds: GV please check
        Return True on success.
        """
        atm = self.getAtom(name, convention=convention)
        if not atm:
            return False
        if atm.db:
            for alias in atm.db.aliases:
                if alias in self:
                    del(self[alias])
        self.removeChild( atm )
        self.atomCount -= 1
        self._parent._parent.atomCount -= 1
        return True

    def addAtom( self, name, convention=INTERNAL, **kwds ):
        """add atomName to self as well as potential alias references
           return Atom instance
        """
        atm = Atom( resName=self.db.translate(convention), atomName=name, convention=convention, **kwds )
        self._addChild( atm )
        atm.residue = self
        self._parent._parent.atomCount += 1
        self.atomCount += 1
        for alias in atm.db.aliases:
            self[alias] = atm
        return atm
    #end def

    def addAllAtoms( self ):
        """Add all atoms according to the definition database.
        """
        # Use database to add atoms
        if self.db:
            for atm in self.db:
                self.addAtom( atm.name )
            #end for
        #end if
    #end def

    def addAllDihedrals(self):
        """Add all dihedrals according to definition database.
        """
        self.dihedrals = NTlist()
        if self.db:
            for d in self.db.dihedrals:
                dihed = Dihedral( self, d.name )
                if dihed.atoms:
                    self.dihedrals.append(dihed)
                    self[dihed.name] = dihed
                #end if
            #end for
        #end if
    #end def


#    def dihedral( self, dihedralName ):
#        """Return cmean,cv tuple for dihedralName,
#        or None on error
#
#        set self[dihedralName] to NTlist of results
#        """
#        # optimized out.
##        if dihedralName not in self.db:
#        if not self.db.has_key(dihedralName):
#            return None
#
#        self[dihedralName] = NTlist()
#        self[dihedralName].cAverage()
##        self[dihedralName].cav = NAN_FLOAT Now redundant because cAverage will already have set them
##        self[dihedralName].cv  = NAN_FLOAT To be set at the end of this routine by calling cAverage() again.
#        self[dihedralName].db  = self.db[dihedralName] # linkage to the database
#        self[dihedralName].residue  = self             # linkage to self
#
#        # Get/Check the topology
#        self[dihedralName].atoms  = None
#        atoms = translateTopology( self, self.db[dihedralName].atoms )
#        if atoms == None or len(atoms) != 4 or None in atoms:
#            return None
#        self[dihedralName].atoms  = atoms
#
#        #add dihedral to dict for lookup later
#        self.chain.molecule._dihedralDict[(atoms[0],atoms[1],atoms[2],atoms[3])] = \
#            (self, dihedralName, self.db[dihedralName])
#        self.chain.molecule._dihedralDict[(atoms[3],atoms[2],atoms[1],atoms[0])] = \
#            (self, dihedralName, self.db[dihedralName])
#
#        # Check if all atoms have the same number of coordinates
#        l = len( atoms[0].coordinates)
#        for a in atoms[1:]:
#            if len(a.coordinates) != l:
#                return None
#            #end if
#        #end for
#
#        for i in range(0,l):
#            self[dihedralName].append( NTdihedralOpt(
#               atoms[0].coordinates[i],
#               atoms[1].coordinates[i],
#               atoms[2].coordinates[i],
#               atoms[3].coordinates[i]))
#
#        plotpars = plotParameters.getdefault(dihedralName,'dihedralDefault')
#        self[dihedralName].limit( plotpars.min, plotpars.max )
#        cav,cv,_n = self[dihedralName].cAverage(min=plotpars.min,max=plotpars.max)
#
#        return cav,cv
#    #end def

    def translate( self, convention ):
        """return translated name according to convention or None if not defined"""
        return self.db.translate(convention)
    #end def

    def translateWithDefault( self, convention ):
        """return translated name according to convention or internal CING name if not defined"""
        return self.db.translateWithDefault(convention)
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
        """Return the 7-element name tuple:
           (moleculeName, chainName, resNum, atomName, modelIndex, resonanceIndex, convention)
        """
        return (self.chain.molecule.name, self.chain.name, self.resNum, None, None, None, convention)
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
            atomName = translateAtomName( convention, self.translate(convention), atomName, INTERNAL )
        #end if
        if self.has_key(atomName):
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

    def toSML(self, stream=sys.stdout ):
        if hasattr(Residue,'SMLhandler'):
            Residue.SMLhandler.toSML( self, stream )
        else:
            NTerror('Residue.toSML: no SMLhandler defined')
        #end if
    #end def
#end class

class Dihedral( NTlist ):
    """
    Class to represent a dihedral angle
    """

    def __init__(self, residue, dihedralName, range=None ):
        NTlist.__init__(self)

        self.residue = residue
        self.name = dihedralName
        if not range:
            plotpars = plotParameters.getdefault(dihedralName,'dihedralDefault')
            self.range = ( plotpars.min, plotpars.max )
        else:
            self.range = range
        #end if


        if not dihedralName or not residue or not residue.db or not residue.db.has_key(dihedralName):
            self.db = None
            self.atoms = None
        else:
            self.db = residue.db[dihedralName]
            atoms = translateTopology( self.residue, self.db.atoms )
            if atoms == None or len(atoms) != 4 or None in atoms:
                self.atoms = None
            else:
                self.atoms  = atoms
                #add dihedral to dict for lookup later
                self.residue.chain.molecule._dihedralDict[(atoms[0],atoms[1],atoms[2],atoms[3])] = \
                    (self.residue, dihedralName, self.db)
                self.residue.chain.molecule._dihedralDict[(atoms[3],atoms[2],atoms[1],atoms[0])] = \
                    (self.residue, dihedralName, self.db)
            #end if
        #end if
        self.cav = NaN
        self.cv  = NaN
    #end def

    def __str__(self):
        if self.residue:
            dname = self.residue.name + '.' + self.name
        else:
            dname = self.name
        #end if
        return sprintf('<Dihedral %s: %.1f, %.2f>', dname, self.cav, self.cv)
    #end def

    def format(self):
        if self.residue:
            dname = self.residue.name + '.' + self.name
        else:
            dname = self.name
        #end if
        return sprintf('%s Dihedral %s %s\n' +\
                       'values:   %s\n' +\
                       'average:  %.1f\n' +\
                       'variance: %.2f\n' +\
                       'range:    %s\n' +\
                       'atoms:    %s',
                        dots, dname, dots,
                        NTlist.__str__(self),
                        self.cav, self.cv, self.range,
                        self.atoms
                       )


    def calculateValues(self):
        """Calculate the dihedral values: return cav, cv tuple or NaN,NaN on error
        """
        # Check if all atoms have the same number of coordinates
        l = len( self.atoms[0].coordinates)
        for a in self.atoms[1:]:
            if len(a.coordinates) != l:
                return NaN,NaN
            #end if
        #end for

        for i in range(0,l):
            self.append( NTdihedralOpt(
                                       self.atoms[0].coordinates[i],
                                       self.atoms[1].coordinates[i],
                                       self.atoms[2].coordinates[i],
                                       self.atoms[3].coordinates[i]
                                      )
                       )

        cav,cv,_n = self.cAverage(min=self.range[0],max=self.range[1])

        return cav,cv
    #end def
#end class


class Coordinate:
    """
-------------------------------------------------------------------------------
Coordinate class
-------------------------------------------------------------------------------
coordinates stored in attribute e (NTcVector instance)

Several mappings implemented
e.g.
    c=Coordinate(5.0, 6.0, 7.0)

    c[0] == c.x == c.e[0]
-------------------------------------------------------------------------------
    """

    DEFAULT_BFACTOR   = 0.0
    DEFAULT_OCCUPANCY = 1.0

    def __init__( self, x=0.0, y=0.0, z=0.0, Bfac=DEFAULT_BFACTOR, occupancy=DEFAULT_OCCUPANCY, atom = None ):
        self.e         = NTcVector( x, y, z )
        self.Bfac      = Bfac
        self.occupancy = occupancy
        self.atom      = atom
        self.model     = -1    # index of the model
    #end def

    #implement  x,y,z attributes mapped to e vector
    def __getattr__(self, item):
        if  item == 'x':
            return self.e[0]
        elif  item == 'y':
            return self.e[1]
        elif  item == 'z':
            return self.e[2]
        else:
            raise AttributeError
    #end def

    def __setattr__(self, item, value):
        if  item == 'x':
            self.e[0] = value
        elif  item == 'y':
            self.e[1] = value
        elif  item == 'z':
            self.e[2] = value
        else:
            self.__dict__[item] = value
    #end def

    # Implement a dict-like functionality
    # map integers and x,y,z
    def __getitem__(self, item):
        if isinstance( item, int ):
            return NTcVector.__getitem__(self.e, item)
        elif  item == 'x':
            return self.e[0]
        elif  item == 'y':
            return self.e[1]
        elif  item == 'z':
            return self.e[2]
        else:
            return self.__dict__[item]
    #end def

    def __setitem__(self, item, value):
        if isinstance( item, int ):
            NTcVector.__setitem__( self.e, item, value )
        elif  item == 'x':
            self.e[0] = value
        elif  item == 'y':
            self.e[1] = value
        elif  item == 'z':
            self.e[2] = value
        else:
            self.__dict__[item] = value
    #end def

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
    #end def

    def distance( self, other ):
        return self.e.distance( other.e )
    #end def

    def dot( self, other ):
        return self.e.dot( other.e )
    #end def

    def format(self):
        return sprintf( '<Coordinate: %s>', self )
    #end def

    def __str__(self):
        return sprintf('(%6.2f,%6.2f,%6.2f)', self.e[0], self.e[1], self.e[2])
    #end def

    def __repr__(self):
        return sprintf('Coordinate( x=%f, y=%f, z=%f, Bfac=%f, occupancy=%f )',
                       self.e[0], self.e[1], self.e[2], self.Bfac, self.occupancy
                      )

    def nameTuple(self, convention=INTERNAL):
        """Return the 7-element name tuple:
           (moleculeName, chainName, resNum, atomName, modelIndex, resonanceIndex, convention)
        """
        if not self.atom: return (None, None, None,None,self.model,None,convention)
        else:
            return (self.atom.residue.chain.molecule.name,
                    self.atom.residue.chain.name,
                    self.atom.residue.resNum,
                    self.atom.translate(convention),
                    self.model,
                    None,
                    convention
                   )
    #end def
#end class


class Atom( NTtree ):
    """
-------------------------------------------------------------------------------
Atom class: Defines object for storing atom properties
-------------------------------------------------------------------------------
    Initiating attributes:
        resName                 : Residue name according to convention.
        atomName                : Atom name according to the convention.
        convention              : Naming convention; e.g. INTERNAL, CYANA2, IUPAC

    Derived attributes:
        atomIndex               : Unique (sequential) atom index (several external programs need one).
        resonances              : NTlist of Resonance instances.
        coordinates             : NTlist of Coordinate instances.
        db                      : Reference to database AtomDef instance
        residue                 : Reference to Residue instance
        rogScore                : ROGscore instance
-------------------------------------------------------------------------------
    """

    def __init__( self, resName, atomName, convention=INTERNAL, **kwds ):

        NTtree.__init__(self, name=atomName, __CLASS__='Atom', **kwds )

        self.__FORMAT__ = self.header( dots ) + '\n' +\
                          'residue:     %(residue)s\n' +\
                          'resonances:  %(resonances)s\n' +\
                          'coordinates: %(coordinates)s\n' +\
                          self.footer( dots )

        self.setdefault( 'stereoAssigned', False )

        self.resonances  = NTlist()
        self.coordinates = NTlist()
        self.rogScore    = ROGscore()

        self._topology = None #intially None; defined by the updateTopolgy call of the Molecule class

        # several external programs need an index
        global AtomIndex
        self.atomIndex = AtomIndex
        AtomIndex += 1

        db = NTdb.getAtomDefByName( resName, atomName, convention = convention )
        if db:
            self.name = db.translate(INTERNAL)
            self.db = db
        else:
#            NTerror('Atom.__init__: atom "%s" not defined for residue %s in database' % (atomName, resName ))
            NTwarning('Atom.__init__: (%-4s,%-4s) not valid for convention "%s". Creating non-standard definition.',
                       resName, atomName, convention
                      )
            self.db = AtomDef(atomName) # TODO: check if absense of residue defs within here cause problems.
        #end if
    #end def

    def __str__( self ):
#        return self._Cname( 1 )
        return '<%s %s>' % ( self._className(), self._Cname(1) )
    #end def

    def __repr__(self):
        return str(self)
    #end def

    def criticize(self):
#        NTdebug( '%s' % self )
        if not len(self.coordinates):
            NTdebug('Setting atom to max orange [crit.1] because it has no coordinates')
            self.rogScore.setMaxColor( COLOR_ORANGE, comment=ROGscore.ROG_COMMENT_NO_COOR)

    def toString(self, showChainId=True, showResidueType=True):
        res = self._parent

        if showChainId:
            chn = res._parent
            result = chn.name + '.'
        else:
            result = ''
        # Compressed for speed.
        if showResidueType:
            result += res.name + '.' + self.name
        else:
            result += res.number + '.'  + self.name

        return result

    def addCoordinate(self, x, y, z, Bfac, occupancy=Coordinate.DEFAULT_OCCUPANCY, **kwds):
        """Append coordinate to coordinates list
        Convenience method.
        """
        c = Coordinate( x, y, z, Bfac=Bfac, occupancy=occupancy, atom=self )
#        c.update( **kwds )
        c.model = len(self.coordinates)
        self.coordinates.append( c )
    #end def

    def addResonance( self, value=NaN, error=NaN ):
        r = Resonance( atom=self, value=value, error = error )
        r.resonanceIndex = len(self.resonances)
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

    def calculateMeanCoordinate( self ):
        """"
        Calculate mean of coordinates of self
        Return mean Coordinate instance, or NoneObject on error.

        """
        n   = len( self.coordinates)
        fn  = float(n)

        if n == 0:
            self.meanCoordinate = NoneObject
            return self.meanCoordinate
        #end if

        if 'meanCoordinate' not in self or not self.meanCoordinate:
            self.meanCoordinate = Coordinate( 0.0, 0.0, 0.0, Bfac = 0.0, atom = self )
        #end if

        self.meanCoordinate.rmsd = 0.0
        self.meanCoordinate.e.set(0.0, 0.0, 0.0)
        for c in self.coordinates:
            self.meanCoordinate.e += c.e
        #end for

        for axis in ['x','y','z']:
                self.meanCoordinate[axis] /= fn
        #end for

        for c in self.coordinates:
            self.meanCoordinate.rmsd += (c.e-self.meanCoordinate.e).sqsum()
        #end for
        self.meanCoordinate.rmsd = math.sqrt(self.meanCoordinate.rmsd/fn)

#         if (n==1):
#             self.coordinates
#             for axis in ['x','y','z']:
#                 self.meanCoordinate[axis] = self.coordinates[0][axis]
#             #end for
#         else:
#
# #            fn1 = fn-1.0
#             self.meanCoordinate.rmsd = 0.0
#
# #            for axis in ['x','y','z']:
#                 #For speed we store the array first
# #                data  = self.coordinates.zap(axis)
# #                sum   = data.sum()
# #                sumsq = data.sumsq()
#
#                 self.meanCoordinate[axis]     = sum/fn
#
#                 #sumsq/(fn-1.0) - (sum*sum)/(fn*(fn-1.0))
# #                self.meanCoordinate['d'+axis] = sumsq - sum*sum/fn/fn1
# #                self.meanCoordinate.rmsd += sumsq - sum*sum/fn
#             #end for
#
# #            self.rmsd = 0.0
# #            for c in self.coordinates:
# #                self.rmsd += NTdistance(c, self.meanCoordinate )
# #            #end for
# #            self.rmsd /= fn
# #        #end if

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
        """return translated name according to convention or None if not defined"""
        return self.db.translate(convention)
    #end def

    def translateWithDefault( self, convention ):
        """return translated name according to convention or internal CING name if not defined"""
        return self.db.translateWithDefault(convention)
    #end def

    def topology( self ):
        """return list of Atom instances defining the topology"""
        if self._topology != None:
            return self._topology
        else: #old style#
            return translateTopology( self._parent, self.db.topology )
    #end def

    def isAssigned( self ):
        """return true if atom current resonance has a valid assignment"""
        if (self.resonances() != None):
            return not isNaN(self.resonances().value)
        #end if
        return False
    #end def

    def shift( self ):
        if self.isAssigned():
            return self.resonances().value
        else:
            return NaN
        #end if
    #end def

    def swapAssignments( self, other ):
        """
        Swap the assignments of self with other
        """
        for r in self.resonances:
            r.atom = other
        for r in other.resonances:
            r.atom = self
        tmp = self.resonances
        self.resonances = other.resonances
#        other.resonances = self
        other.resonances = tmp
    #end def


    def setStereoAssigned( self ):
        """
        Return stereoAssigned flag to True
        """
        if not self.isProChiral():
            NTerror('Atom.setStereoAssigned: %s is not prochiral', self)
        self.stereoAssigned = True
    #end def


    def isStereoAssigned( self ):
        """
        Return True if stereoAssigned flag present and True
        """
        return self.stereoAssigned
    #end def

    def isProChiral( self ):
        """
        Return True if atm is pro-chiral and thus can have stereo assignment
        Should be in in database
        """
        LVdict = dict( CD1 = 'CD2', CD2 = 'CD1', QD1 = 'QD2', QD2 = 'QD1', MD1 = 'MD2', MD2 = 'MD1',
                       CG1 = 'CG2', CG2 = 'CG1', QG1 = 'QG2', QG2 = 'QG1', MG1 = 'MG2', MG2 = 'MG1'
                     )
        self.db.proChiralPartnerAtom = None
        if self.residue.db.name in ['LEU', 'VAL'] and self.db.name in LVdict:
            # patch database
            self.db.proChiralPartnerAtom = LVdict[ self.db.name ]
            return True
        #end if
        if self.isProton():
            p = self.pseudoAtom()
            if p != None:
                r = p.realAtoms()
                if len(r) == 2:
                    if self == r[0]:
                        self.db.proChiralPartnerAtom = r[1].db.name
                    else:
                        self.db.proChiralPartnerAtom = r[0].db.name
                    return True
                #end if
            #end if
        #end if
        return False
    #end def

    def proChiralPartner( self ):
        """
        Return proChiral partner Atom instance of self or None if this does not exist
        should be in database
        """

        if self.isProChiral():
            return self.residue[self.db.proChiralPartnerAtom]
        #end if
        return None
    #end def

    def heavyAtom( self ):
        """
        For protons return heavyAtom of self,
        None otherwise
        """
        if not self.isProton():
            return None
        return self.topology()[0]
    #end def

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

    def isOxygen( self ):
        """Return Tue if atm is 16O
        """
        return (self.db.spinType == '16O')
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

        if self.isStereoAssigned():
            props.append('isStereoAssigned','stereoassigned')
        else:
            props.append('isNotStereoAssigned','notstereoassigned')
        #end if

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
        """Return the 7-element name tuple:
           (moleculeName, chainName, resNum, atomName, modelIndex, resonanceIndex, convention)
        """
        an = self.translate( convention )
        if not an: return (None,None,None,None,None,None,convention)
        return (self.residue.chain.molecule.name,
                self.residue.chain.name,
                self.residue.resNum,
                an,
                None,
                None,
                convention
               )
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
            NTwarning("Failed to translate from CING to convention: %s atom: %-20s returning CING atom name" % (convention, self))
            pdbAtmName = self.name

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

    def toSML(self, stream=sys.stdout ):
        if hasattr(Atom,'SMLhandler'):
            Atom.SMLhandler.toSML( self, stream )
        else:
            NTerror('Atom.toSML: no SMLhandler defined')
        #end if
    #end def
#end class


#class XMLAtomHandler( XMLhandler ):
#    """Atom handler class"""
#    def __init__( self ):
#        XMLhandler.__init__( self, name='Atom')
#    #end def
#
#    def handle( self, node ):
#        attrs = self.handleDictElements( node )
#        if attrs == None: return None
#        result = Atom( resName = attrs['resName'], atomName = attrs['name'] )
#
#        # update the attrs values
#        result.update( attrs )
#
#        # restore the resonance references
#        for r in result.resonances:
#            r.atom = result
#
#        return result
#    #end def
##end class
##register this handler
#Atom.XMLhandler = XMLAtomHandler()

class AtomList( NTlist ):
    """
    Class based on NTlist that holds atoms.
    Also manages the "id's". GV wants to know why as atoms have an id???
    Sort by item of Atom Class.

    NB this list is only instantiated for the validate plugin. It has very little
    functionality. Most functionality should be in Residue, Chains, etc.
    """
    def __init__( self, molecule ):
        NTlist.__init__( self )
        self.name       = molecule.name + '.atoms'
#        self.status     = status      # Status of the list; 'keep' indicates storage required
        self.currentId  = 0           # Id for each element of list
        self.rogScore   = ROGscore()
        self.appendFromMolecule( molecule )
        self.criticize()
    #end def

    def criticize(self):
        for atom in self:
#            atom.criticize()
            self.rogScore.setMaxColor( atom.rogScore.colorLabel, comment='Cascaded from: %s' %atom.toString() )

    def append( self, o ):
        o.id = self.currentId
        NTlist.append( self, o )
        self.currentId += 1

    def appendFromMolecule( self, molecule ):
        for atom in molecule.allAtoms():
            self.append( atom )
        #end for
        # Mutual references
        self.molecule = molecule
        molecule.atomList = self
    #end def

    def __str__( self ):
        return sprintf( '<AtomList "%s" (%d)>',self.name, len(self) )
    #end def

    def format( self ):
        return str(self)
    #end def
#end class

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


def NTdistance( c1, c2 ):
    """
    Return distance defined by Coordinate instances c1-c2
    """
    return (c2.e-c1.e).length()
#end def


def NTangle( c1, c2, c3, radians = False ):
    """
    Return angle defined by Coordinate instances c1-c2-c3
    """
#    a = c2()-c1()
#    b = c2()-c3()
    a = c2.e-c1.e
    b = c2.e-c3.e
    return a.angle( b, radians=radians )
#end def

def NTdihedral( c1, c2, c3, c4, radians=False ):
    """
    Return dihedral angle defined by Coordinate instances c1-c2-c3-c4
    Adapted from biopython-1.41

    """
#    ab = c1() - c2()
#    cb = c3() - c2()
#    db = c4() - c3()
    ab = c1.e - c2.e
    cb = c3.e - c2.e
    db = c4.e - c3.e

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

def NTdistanceOpt( c1, c2 ):
    """
    Return distance defined by Coordinate instances c1-c2
    """
#    d = c2()-c1()
    d = ( c2[0]-c1[0], c2[1]-c1[1], c2[2]-c1[2] )
#    return d.length()
    return length3Dopt(d)


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

#end def
def NTdihedralOpt( c1, c2, c3, c4 ):
    """ To replace unoptimized routine. It's 7 times faster (20.554/2.965s)
    for 100,000 calculations. Since last the performance dropped with
    the coordinate based on CoordinateOld(list) to 3.0 s per 10,000.
    gv 4 Nov 2008: Only equally fast when using c0.e, c1.e, ... etc directly
    Return dihedral angle defined by Coordinate instances c1-c2-c3-c4
    Adapted from biopython-1.41
    """
#    ab = c1() - c2() optimized
#    cb = c3() - c2()
#    db = c4() - c3()
    ab = ( c1.e[0]-c2.e[0], c1.e[1]-c2.e[1], c1.e[2]-c2.e[2] )
    cb = ( c3.e[0]-c2.e[0], c3.e[1]-c2.e[1], c3.e[2]-c2.e[2] )
    db = ( c4.e[0]-c3.e[0], c4.e[1]-c3.e[1], c4.e[2]-c3.e[2] )

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

    def __init__( self, atom=None, value=NaN, error=NaN ):
        NTvalue.__init__( self, __CLASS__  = 'Resonance',
                                value      = value,
                                error      = error,
                                fmt        = '<%7.3f  (%7.3f)>',
                                atom       = atom,
                                resonanceIndex = -1 # undefined
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

    def __repr__( self ):
        return sprintf('Resonance( value=%r, error=%r)', self.value, self.error)

    def match( self, other ):
        """Return probability of matching between self and other
        """
        sigma1 = self.error
        if sigma1 == 0.0: sigma1 = 1.0
        sigma2 = other.error
        if sigma2 == 0.0: sigma2 = 1.0

        return math.exp( -(self.value-other.value )**2 / (sigma1*sigma2*2) )
    #end def

    def nameTuple(self, convention=INTERNAL):
        """Return the 7-element name tuple.
           (moleculeName, chainName, resNum, atomName, modelIndex, resonanceIndex, convention)

        """
        if not self.atom: return (None, None, None,None,None,self.resonanceIndex,convention)
        else:
            return (self.atom.residue.chain.molecule.name,
                    self.atom.residue.chain.name,
                    self.atom.residue.resNum,
                    self.atom.translate(convention),
                    None,
                    self.resonanceIndex,
                    convention
                   )
    #end def
#end class


#class XMLResonanceHandler( XMLhandler ):
#    """Resonance handler class"""
#    def __init__( self ):
#        XMLhandler.__init__( self, name='Resonance')
#    #end def
#
#    def handle( self, node ):
#        attrs = self.handleDictElements( node )
#        if attrs == None: return None
#        result = Resonance( value = attrs['value'], error = attrs['error'] )
#        # update the attrs values
#        result.update( attrs )
#        return result
#    #end def
##end class
#
##register this handler
#Resonance.XMLhandler = XMLResonanceHandler()



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

def mapMolecules( mol1, mol2, molMap=None ):
    """Give residues and atoms a 'map' attribute
            that points to the corresponding residue/atom in the other molecule

       molMap is an optional list of(mol1ResNum, mol2ResNum) tuples.
       if molMap == None, its is generated by the allResidues() method of  mol1 and mol2.

    """
    if not molMap:
        res1 = mol1.allResidues()
        res2 = mol2.allResidues()
        if len(res1) != len(res2):
            NTerror('mapMolecules: unequal %s and %s have unequal number of residues', mol1, mol2)
            return
        #end if
        molMap = zip(res1,res2)
    #end if

    # Initialize (should not be neccessary! but alas)
    for res in mol1.allResidues(): res.map = None
    for res in mol2.allResidues(): res.map = None
    for atm in mol1.allAtoms(): atm.map = None
    for atm in mol2.allAtoms(): atm.map = None

    for i1,i2 in molMap:
        res1 = mol1.getResidue( i1 )
        res2 = mol2.getResidue( i2 )
        if (res1 != None and res2 != None):
            res1.map = res2
            res2.map = res1
            for atm in res1.atoms:
                if atm.name in res2:
                    atm.map = res2[atm.name]
                else:
                    atm.map = None
                #end if
            #end for
            for atm in res2.atoms:
                if atm.name in res1:
                    atm.map = res1[atm.name]
                else:
                    atm.map = None
                #end if
            #end for
        elif (res1!=None and res2 == None):
            res1.map = res2
            for atm in res1.atoms:
                atm.map = None
            #end for
        elif (res1==None and res2 != None):
            res2.map = res1
            for atm in res2.atoms:
                atm.map = None
            #end for
    #end for
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
#def saveMolecule( molecule, fileName=None)   :
#    """save to fileName for restoring with restoreMolecule"""
#    if not fileName:
#        fileName = molecule.name + '.xml'
#    #end if
#
#    if (molecule == None):
#        NTerror("saveMolecule: molecule not defined")
#        return
#    #end if
#
#    obj2XML( molecule, path=fileName )
#
#    NTmessage( '==> saveMolecule: saved to %s', fileName )
#    #end if
#end def

#==============================================================================
#def restoreMolecule( fileName)   :
#    """restore from fileName, return Molecule instance """
#
#    mol = XML2obj( path=fileName )
#    if (mol == None): return None
#
#    mol.source = fileName
#
#    NTmessage( '==> restoreMolecule: restored %s', mol.format())
#    #end if
#
#    return mol
##end def

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


def chi3SS( dCbCb ):
    """
    Return approximation of the chi3 torsion angle as
    fie of the distance between the Cb atoms of each Cys residue

    Dombkowski, A.A., Crippen, G.M, Protein Enginering, 13, 679-89, 2000
    Page 684, eq. 9
    """
    try:
        val = acos( 1.0 - (dCbCb*dCbCb - 8.555625) / 6.160 ) * 180.0/pi
    except:
        val = NaN
    return val


def disulfideScore( cys1, cys2 ):
    """
    Define a score [0.0,1.0] for a potential cys1-cys2 disulfide bridge.
    Based upon simple counting:
    - Ca-Ca distance
    - Cb-Cb distance
    - Ability to form S-S dihedral within specified range or the presence
      of short distance SG-SG

    Initial test show that existing disulfides have scores > 0.9
    Potential disulfides score > ~0.25

    Limits based upon analysis by:
      Pellequer J-L and Chen, S-W.W, Proteins, Struct, Func and Bioinformatics
      65, 192-2002 (2006)
      DOI: 10.1002/prot.21059

    cys1, cys2: Residue instances
    returns a NTlist with four numbers:
        [d(Ca-Ca) count, d(Cb-Cb) count, S-S count, final score]

    """
    mc = len(cys1.CA.coordinates) # model count
    score = NTlist(0., 0., 0., 0.)
    for m in range( mc ):
        da = NTdistance( cys1.CA.coordinates[m], cys2.CA.coordinates[m] )
        if da >= 3.72 and da <= 6.77:
            score[0] += 1

        db = NTdistance( cys1.CB.coordinates[m], cys2.CB.coordinates[m] )
        if db >= 3.18 and db <= 4.78:
            score[1] += 1

        dg = NTdistance( cys1.SG.coordinates[m], cys2.SG.coordinates[m] )
        chi3 = chi3SS( db )
        if (dg >= 1.63 and dg <= 2.72) or (chi3 >= 27.0 and chi3 <= 153.0):
            score[2] += 1
        #print '>', da, db, dg, chi3, score
    #end for

    score[3] = score.sum() / (3. * mc)
    return score


def isValidChainId( chainId ):
    """For use by ccpn importer; call this routine to see if chain id is valid
    otherwise call ensureValidChainId to make it a valid one.
    """
    if chainId==None:
        return False
    if len(chainId) != 1:
        return False
#    if chainId.islower(): # given up as per issue 130.
#        return False
    return chainId in Chain.DEFAULT_ChainNamesByAlphabet
#        return False
#    return True

def ensureValidChainId(chainId ):
    """See doc Molecule#ensureValidChainIdForThisMolecule
    In absence of an existing molecule this routine can only return the default chain id
    if the presented id is not valid.
    """

    if isValidChainId( chainId ):
        return chainId
    if chainId and len(chainId) > 1:
        chainId = chainId[0]
    if isValidChainId( chainId ):
        return chainId
    return Chain.defaultChainId



def getNextAvailableChainId(chainIdListAlreadyUsed = []):
#    NTdebug("chainIdListAlreadyUsed: %s" % chainIdListAlreadyUsed)
    for chainId in Chain.DEFAULT_ChainNamesByAlphabet:
        if not( chainId in chainIdListAlreadyUsed ):
            return chainId
    issueId = 130
    msg = "CING exhausted the available %d chain identifiers; see issue %d here:\n" % (
        len(Chain.DEFAULT_ChainNamesByAlphabet), issueId)
    msg += issueListUrl+`issueId`
    NTcodeerror(msg)


def unmatchedAtomByResDictToString(unmatchedAtomByResDict):
    msg = ''
    resNameList = unmatchedAtomByResDict.keys()
    resNameList.sort()
    for resName in resNameList:
        atmNameList = unmatchedAtomByResDict[ resName ][0]
        resNumbList = unmatchedAtomByResDict[ resName ][1]
        atmNameList.sort()
        resNumbList.sort()
        msg += "%-4s: " % resName
        for atmName in atmNameList:
            msg += "%-4s " % atmName
        msg += '['
        for resNumb in resNumbList:
            msg += " %d" % resNumb
        msg += ']'
        if resName != resNameList[-1]:
            msg += '\n'
    return msg


