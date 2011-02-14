from cing import issueListUrl
from cing.Libs import PyMMLib
from cing.Libs.AwkLike import AwkLikeS
from cing.Libs.Geometry import to_0_360
from cing.Libs.NTplot import ssIdxToType
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.PyMMLib import ATOM
from cing.Libs.PyMMLib import HETATM
from cing.Libs.PyMMLib import PDBFile
from cing.Libs.cython.superpose import NTcMatrix #@UnresolvedImport
from cing.Libs.cython.superpose import NTcVector #@UnresolvedImport
from cing.Libs.cython.superpose import calculateRMSD #@UnresolvedImport
from cing.Libs.cython.superpose import superposeVectors #@UnresolvedImport
from cing.Libs.html import addPreTagLines
from cing.Libs.html import hPlot
from cing.PluginCode.required.reqDssp import DSSP_H
from cing.PluginCode.required.reqDssp import DSSP_S
from cing.PluginCode.required.reqDssp import getDsspSecStructConsensus
from cing.PluginCode.required.reqNih import TALOSPLUS_STR
from cing.core.ROGscore import ROGscore
from cing.core.classes2 import RestraintList
from cing.core.constants import * #@UnusedWildImport
from cing.core.database import AtomDef
from math import acos
from numpy import * #@UnusedWildImport overwrites such common functions as sum, max etc.
from numpy import linalg as LA
from operator import attrgetter
from parameters   import plotParameters
import database
import numpy

#==============================================================================
# Global variables
#==============================================================================
AtomIndex = 1
_DEFAULT_CHAIN_ID = 'A' # Use Chain.defaultChainId which is public.

# version <= 0.91: old sequence.dat defs
# version 0.92: xml-sequence storage, xml-stereo storage
# Superseded by SML routines >0.93
# 0.94 storage of molecule specific database stuff
NTmolParameters = NTdict(
    version        = 0.92,
    contentFile    = 'content.xml',
    sequenceFile   = 'sequence.xml',
    resonanceFile  = 'resonances.dat',
    coordinateFile = 'coordinates.dat',
    stereoFile     = 'stereo.xml'
)

#dots = '-----------' # moved to constants.py

chothiaClassA = 'a'
chothiaClassB = 'b'
chothiaClassAB = 'a/b'
chothiaClassC = 'c' # only coil
mapChothia_class2Int = {chothiaClassA: 0, chothiaClassB : 1, chothiaClassAB : 2, chothiaClassC : 3, None: None}

# Only 20 AA and 5 NA; Nota Bena no variants.
common20AAList = "ALA ARG ASN ASP CYS GLN GLU GLY HIS ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL".split()
commonAAList = common20AAList + "ASPH GLUH HISE CYSS".split() # do not put these into common20AAList
commonNAList = "A T G C U".split()
commonResidueList = commonAAList + commonNAList

common20AADict = NTlist2dict(common20AAList)

# GWV: moved to database.py
#terminalAtomDict = NTdict()
#terminalAtomDict.appendFromList( "H1 H2 H3 H' H'' HOP2 HOP3".split())

def chothiaClassInt(chothiaClass):
    """Integer value for fast lookup in db. Return None if class parameter is None"""
    return mapChothia_class2Int[ chothiaClass ]

def countDsspSecStructConsensus(resList):
    """Determine if molecule has at least one of alpha or beta protein regions.
    Molecule may contain other types of macromolecules than protein.
    Return None if DSSP wasn't run or no amino acids are present.
    """
    countA = 0
    countB = 0
    countC = 0
    for res in resList:
        if not res.hasProperties(PROTEIN_STR): # absense of this check was a bug.
            continue
        r = getDsspSecStructConsensus( res )
        if r == DSSP_H:
            countA += 1
        elif r == DSSP_S:
            countB += 1
        else:
            countC += 1
    return countA, countB, countC

def chothiaClass(resList):
    """Determine if molecule has at least one of alpha or beta protein regions.
    Molecule may contain other types of macromolecules than protein.
    Return None if DSSP wasn't run or no amino acids are present.
    Chothia's original paper distinguished between alpha and/plus beta which
    is beyond this function's scop.
    """
    countA, countB, countC = countDsspSecStructConsensus(resList)
    if countA:
        if countB:
            return chothiaClassAB
        else:
            return chothiaClassA
    elif countB:
        return chothiaClassB

    # There is a difference between Coil and None.
    if countC:
        return chothiaClassC

    return None

def getAssignmentCountMapForResList(resList, isAssigned = True):
    """
    Returns dictionary by isotope and overall keys with boolean values.
    Only spinTypes listed in AssignmentCountMap are filled.

    Method is designed to correspond to BMRB counting method:
    - Methylene protons are counted separately even when degenerate.

    In contrast to BMRB version 3 files here:
    - Methyl protons are only counted once.

    If isAssigned is not set then the unassigned spins will be counted.
    Together with the assigned spins they should constitute all assignable spins.
    """

    assignmentCountMap = AssignmentCountMap()

    atmList = NTlist()
    for res in resList:
        atmList.addList( res.allAtoms() )
    for atm in atmList:
        atmIsAssigned = atm.isAssigned()
        # spintype is not available for pseudos etc. perhaps
        spinType = getDeepByKeys(atm, DB_STR, SPINTYPE_STR)
#        NTdebug("atm, spinType, atmIsAssigned, isAssigned: %s %s %s %s" % (atm, spinType, atmIsAssigned, isAssigned))
        if not spinType:
#            NTdebug("Failed to find spinType for atom: %s" % atm)
            continue
        if not assignmentCountMap.has_key(spinType):
#            NTdebug("Failed to find spinType in assignmentCountMap: %s for atm %s" % (spinType, atm))
            continue
        # Only count the methyl pseudo atom e.g. Ala MB
        if atm.isMethylProton() and not atm.isPseudoAtom():
#            NTdebug("Skipping isMethylProton and not atm.isPseudoAtom() %s" % atm)
            continue
        if atm.isPseudoAtom() and not atm.isMethyl():
#            NTdebug("Skipping atm.isPseudoAtom() and not atm.isMethyl() %s" % atm)
            continue
        # Get rid of counts for terminii which usually are absent.
        if atm.isTerminal():
#            NTdebug("Skipping isTerminal %s" % atm)
            continue

        if isAssigned:
            if not atmIsAssigned:
#                NTdebug("%s skipped because requesting assigned and this atom was not for : " % atm)
                continue
        else:
            if atmIsAssigned:
#                NTdebug("%s skipped because requesting -unassigned- and this atoms was for: " % atm)
                continue
#        NTmessage("Including atm: %s " % atm)
        assignmentCountMap[spinType] += 1
    # end for
#    NTdebug("For isAssigned: %s found %s" % (isAssigned, assignmentCountMap))
    return assignmentCountMap

def allResiduesWithCoordinates(resList):
    """Returns NTlist with a subset of residues that have at least one atom with at least one coordinate"""
    result = NTlist()
    for res in resList:
        hasCoor = res.hasCoordinates()
#        NTdebug("Res %s has coordinates: %s" % ( res, hasCoor ))
        if hasCoor:
            result.add(res)
    return result



class ResidueList():
    def countDsspSecStructConsensus(self):
        return countDsspSecStructConsensus(self.allResidues())
    def chothiaClass(self):
        return chothiaClass(self.allResidues())
    def chothiaClassInt(self):
        return chothiaClassInt(chothiaClass(self.allResidues()))
    def getAssignmentCountMap(self,isAssigned=True):
        return getAssignmentCountMapForResList(self.allResidues(), isAssigned=isAssigned)
    def allResiduesWithCoordinates(self):
        return allResiduesWithCoordinates(self.allResidues())

#==============================================================================
class Molecule( NTtree, ResidueList ):
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
        self.ranges           = None         # ranges used for superposition/rmsd calculations. None means all. 'auto' will be converted.

#        self.saveXML('chainCount','residueCount','atomCount')

        # save the content definitions; depreciated since version 0.75
        # Maintained for compatibility
        self.content = NTdict( name = self.name, convention = INTERNAL )
        self.content.update( NTmolParameters )
        self.content.saveAllXML()
        self.content.keysformat()

        self.project = None # JFD: don't know where it gets set but it exists. GWV; when initializing molecules from a project
        self.rmsd = None
        # cv's
        self.cv_backbone = None # filled by self.setCvBackboneSidechain. Needs to be matched by cing.core.constants#CV_BACKBONE_STR
        self.cv_sidechain = None

        self.selectedResidues = None # this is a python array

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
        return sprintf('<Molecule %s>', self._Cname(-1))
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
#            NTdebug('After keepSelectedModels: %s' % self)
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
            NTwarning( 'Molecule.addChain: chain "%s" already present' % name )
            name = None
        if not isValidChainId( name ): # Catch ccpn ' ' etc.
            name = None

        if name==None:
            newName = self.getNextAvailableChainId()
            if not newName:
                NTerror('Molecule.addChain: failed getNextAvailableChainId; skipping add.')
                return None # Note the bug that this statement was leftshifted before revision 778.
            NTdebug( 'Molecule.addChain: got next available one: %s' % newName)
            name = newName

#            return None
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

#        resTranslated = res.translate(convention)
#        an = translateAtomName( convention, resTranslated, atomName, INTERNAL )
##        if (not an or (an not in res)): return None
#        if not an:
##            NTdebug("in Molecule.decodeNameTuple failed to translateAtomName for res: " + `resTranslated` + " and atom: " + `atomName`)
#            return None
#            # JFD adds. This makes no sense. The residue itself by number is known. Just get it's residue type
#            # and look up the atom translation. This can of course be fixed in the db too.
#
#
#        if not res.has_key(an):
##            NTdebug("in Molecule.decodeNameTuple atom not in residue: [%s]" % `an`)
#            return None


#        atm = res[an]

        # GWV 20 Apr 2010: all in one call
        atm = res.getAtom( atomName, convention )

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

    def _getResidueLoL(self):
        """
        Return list of list instance with chain number and residue number in order.
        For decoding usage with Wattos routines
        """
        result = NTlist()
        for ch in self.allChains():
            chList = NTlist()
            result.append(chList)
            for res in ch.allResidues():
                chList.append(res)
        return result
    #end def

    def _getResidueHash2LoL(self):
        """
        Return hash on residues that has a value of indices of chain idx and residue idx in same order as _getResidueLoL
        For decoding usage with Wattos routines
        """
        result = NTdict()
        for c,ch in enumerate(self.allChains()):
            for r,res in enumerate(ch.allResidues()):
                result[ res ] = ( c, r )
        return result
    #end def

    def rangesToMmCifRanges(self, ranges=None):
        """
        Return a new ranges string with residue numbering akin mmCIF/NMR-STAR i.e. residue numbering starting at 1
        and chain ids unchanged.

        E.g. 1brv's A.173-189 becomes A.3-19

        Return None on error.
        """
        if ranges == None:
            ranges = self.ranges

        rangesNew = ''
        residueList2StartStopList = self.ranges2StartStopList(ranges)
        if residueList2StartStopList == None:
            NTerror("Failed ranges2StartStopList for ranges: %s" % ranges)
            return None

#        residueLoL = self._getResidueLoL()
        residueHash2LoL = self._getResidueHash2LoL()
#        residuePair = [ None, None]
        residueNewNumberPair = [ None, None]
        pairCount = len(residueList2StartStopList) / 2
        for p in range(pairCount):
            for r in range(2):
                i = 2 * p + r
                residue = residueList2StartStopList[i]
                residueNewTuple = getDeepByKeysOrAttributes( residueHash2LoL, residue)
                if residueNewTuple == None:
                    NTerror("Failed to find residue in residueHash2LoL.")
                    return None
                residueNewNumberPair[r] = str(residueNewTuple[1] + 1) # Plus one 'cause indices start at zero and mmCIF starts at one.
#                NTdebug("Mapping %s %s to residueNewNumberPair %s" % (r,residue,residueNewNumberPair[r]))
                if residueNewNumberPair[r] < 1:
                    NTerror("In %s tried to map to mmCIF invalid residue number: %s" % ( getCallerName(), residueNewNumberPair[r] ))
                    return None
            # end for
            if p:
                rangesNew += ','
            rangesNew += residue.chain.name + '.'
            if residueNewNumberPair[0] != residueNewNumberPair[1]:
                rangesNew += '-'.join(residueNewNumberPair)
            else:
                rangesNew += residueNewNumberPair[0]
        # end for
#        NTdebug("Mapped ranges %s to %s" % (ranges,rangesNew))
        return rangesNew


    def _getAtomDictWithchain(self, convention=INTERNAL):
        """
        Return a dict instance with (chainId, resNum, atomName), Atom mappings.
        NB. atomName according to convention
        For decoding usage with CYANA/XEASY, and SHIFTX routines
        """
        NTcodeerror("Need to code dict in _getAtomDictWithchain")
        return None

    def _getAtomDict(self, convention=INTERNAL, ChainId = _DEFAULT_CHAIN_ID): # would like to have said Chain.defaultChainId but isn't known yet.
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
#                        NTwarning('In Molecule._getAtomDict found multiple mapped atoms (new key, old key): (%-20s,%-20s)',
#                                    atm, atomDict[t])
                        pass
                    else:
                        atomDict[t] = atm
                    #end if
                #end if
            #end for
        #end for
        return atomDict
    #end def

    def setRanges(self, ranges=None):
        """
        Expand 'auto', 'cv', 'all', None, and regular string to an actual list of residues and represent it again in the cing format string for residues.
        Returns True on error or None on success.
        """
        self.ranges = ranges # will be picked up by setResiduesFromRanges called next
        residueList = self.setResiduesFromRanges()
        if residueList == None:
            NTerror("In setRanges failed to setResiduesFromRanges from ranges: [%s]" % ranges)
            return True
        rangesReset = self.residueList2Ranges(residueList)
        if rangesReset != ranges:
            NTmessage("==> Ranges reset from: %s to %s" % ( ranges, rangesReset ))
            self.ranges = rangesReset

    def setResiduesFromRanges(self, ranges=None, autoLimit=LIMIT_RANGES):
        """
        Convert
              either:
                  'auto' keyword
              or
                  a residue ranges string, e.g. '10-20,34,50-60',
              or
                  a list with residue number or residue instances,
              or
                  None  ==> output will be all residues.

        to a NTlist instance with residue objects.

        Set the selectedResidues attributes in Molecule instance

        Return the list or None upon error.

        Routine should replace ranges2list eventually

        No longer sets the range so infinite recursion can be avoided.
        """

        if ranges == None:
            ranges = self.ranges

#        NTdebug("In setResiduesFromRanges using ranges: %s" % ranges)


        if ranges == CV_RANGES_STR:
            rangesReset = self.rangesByCv()
            if rangesReset == None:
                NTerror("Failed rangesByCv in setResiduesFromRanges")
                return None
#            NTdebug("In setResiduesFromRanges used: cv to get ranges: %s" % rangesReset)
            selectedResidues = self.ranges2list(rangesReset)
            if selectedResidues == None:
                NTerror("Failed ranges2list (A) in setResiduesFromRanges")
                return None
        elif ranges == AUTO_RANGES_STR:
            selectedResidues = self._autoRanges( autoLimit )
            if selectedResidues == None:
                NTerror("Failed _autoRanges in setResiduesFromRanges")
                return None
        elif ranges == ALL_RANGES_STR:
            selectedResidues = self.allResidues()
        elif ranges == EMPTY_RANGES_STR:
            selectedResidues = NTlist()
        elif ranges == None:
            selectedResidues = self.allResidues()
        else:
            selectedResidues = self.ranges2list( ranges )
            if selectedResidues == None:
                NTerror("Failed ranges2list (B) in setResiduesFromRanges")
                return None
            # end if
        # end else

        if selectedResidues == None:
            NTerror("In setResiduesFromRanges failed to get selection of residues for ranges: [%s]" % ranges)
            return None

        self.selectedResidues = selectedResidues
        return selectedResidues
    #end def


    def residueList2Ranges(self, residueList):
        '''
        Translate residue list 2 a ranges string that cing can read itself.
        Return empty string for empty selection.
        Return None on error.
        Return string otherwise.
        An empty list is expressed as EMPTY_RANGES_STR which is a dot.
        '''
        result = ''
        if residueList == None:
            NTerror("In residueList2Ranges no input residueList.")
            return None
        if len(residueList) == 0:
            NTdebug("In residueList2Ranges empty residueList.")
            return EMPTY_RANGES_STR
        startStopList = self.ranges2StartStopList(residueList)
#        NTdebug( 'startStopList (just the inclusive boundaries): %s' % startStopList)
        if startStopList == None:
            NTerror("In residueList2Ranges failed to find startStopList.")
            return
        if len(startStopList) == 0:
#            NTdebug("In residueList2Ranges found empty startStopList.")
            return EMPTY_RANGES_STR
        useChainIds = len(self.allChains()) > 1
        for i in range(0, len(startStopList), 2):
            start = startStopList[i]
            stop = startStopList[i+1]
            todoList = [start,stop]
            strList = []
            for j,r in enumerate(todoList):
                rStr = str(r.resNum)
                if useChainIds and j==0: # only the start will be labelled by chain id.
                    rStr = r.chain.name + '.' + rStr
                strList.append(rStr)
            # end for
            if i != 0:
                result += ','
            if start == stop: # keep it simple
                result += strList[0]
            else:
                result += '-'.join(strList)
        # end for
#        NTdebug( "In residueList2Ranges ranges: %s" % result)
        return result
    # end def

    def ranges2StartStopList(self, ranges=None):
        """
        reduce this sorted list to pairs start, stop

        Return None on error.
        Return (empty) list otherwise.

        An empty list is expressed as EMPTY_RANGES_STR which is a dot.
        """

        if ranges == None:
            ranges = self.ranges
        selectedResidues = self.setResiduesFromRanges(ranges)
#        NTdebug( 'In Molecule#ranges2StartStopList selectedResidues: %s' % selectedResidues)
        if not selectedResidues:
            NTwarning("In Molecule#ranges2StartStopList, no residues selected from ranges: %s" % ranges)
            return

        rangeResidueList = [ selectedResidues[0] ]
        for i in range(len(selectedResidues)-1):
            if ((selectedResidues[i].resNum != selectedResidues[i+1].resNum - 1) or
                (selectedResidues[i].chain  != selectedResidues[i+1].chain)):
                rangeResidueList.append(selectedResidues[i])
                rangeResidueList.append(selectedResidues[i+1])
            # end if
        # end for
        rangeResidueList.append(selectedResidues[-1])

        if len(rangeResidueList) % 2:
            NTcodeerror("Expected to have an even number of residues in the start stop list but found %s residues."  % len(rangeResidueList) )
            return None
#        NTdebug( 'rangeResidueList (just the inclusive boundaries): %s' % rangeResidueList)
        return rangeResidueList


    def startStopList2ranges(self, startStopList):
        """
        Expand pairs start, stop to ranges

        Return None on error.
        Return (empty) list otherwise.
        """

        if startStopList == None:
            NTerror("Input to startStopList2ranges is None")
            return None

        useChainIds = False
        if self.allChains() > 1:
            useChainIds = True

#        NTdebug( 'startStopList2ranges working on startStopList: %s' % str(startStopList))

        ranges = ''
        for i in range(0, len(startStopList), 2):
#            NTdebug( 'startStopList2ranges working on i: %s' % i)
            resStrList = [None,None]
            for j,r in enumerate( [startStopList[i], startStopList[i+1]] ):
#                NTdebug( 'working on j: %s' % j)
                if useChainIds and j == 0:
                    resStrList[j] = '%s.%s' % (r.chain.name,r.resNum,)
                else:
                    resStrList[j] = str(r.resNum)
            # end for
            if i:
                ranges += ','
            ranges += '-'.join(resStrList)
        # end for
#        NTdebug( 'startStopList2ranges returning: %s' % ranges)
        return ranges



    def rangesIsAll( self, ranges ):
        """
        Return True if ranges are actually all residues
        """
        if ranges == ALL_RANGES_STR:
            return True
        residueList = self.ranges2list(ranges)
        if residueList == None:
            NTerror("Failed ranges2list in rangesIsAll for ranges: %s" % ranges)
            return False
        allResidueList = self.allResidues()
        nAll = len(allResidueList)
        nRanges = len(residueList)
        result = (nAll == nRanges)
#        NTdebug("In rangesIsAll nAll %s, nRanges %s so result: %s" % (nAll,nRanges, result))
        return result

    def useRanges(self, ranges=None):
        """Checks to see if the ranges specify something different from all residues"""
        if ranges == None:
            ranges = self.ranges
        return ranges and not self.rangesIsAll(ranges)

    def rangesToExpandedRanges( self, ranges ):
        """
        Return None on error. Simply cycles so it expands selections like all, auto, cv etc.
        """
        residueList = self.ranges2list(ranges)
        if residueList == None:
            NTerror("Failed ranges2list in rangesToExpandedRanges for ranges: %s" % ranges)
            return None
        rangesNew = self.residueList2Ranges(residueList)
        if rangesNew == None:
            NTerror("Failed residueList2Ranges in rangesToExpandedRanges for ranges: %s" % ranges)
            return None
        if rangesNew != ranges:
            NTdebug("Expanded ranges %s to %s" % (ranges,rangesNew))
        return rangesNew

    def _rangesStr2list( self, ranges ):
        """
        Only convert a residue ranges string, e.g. 'A.-10--2,B3'
        See unit test in test_molecule.py
        """
        if type(ranges) != str:
            NTerror('Error Molecule._rangesStr2list: ranges type [%s] should have been a string' % type(ranges) )
            return None

        if ranges == CV_RANGES_STR: # needs to be on top because it rewrites the ranges string to something like 'all' that might still need to be expanded.
            ranges = self.rangesByCv()
        if ranges == EMPTY_RANGES_STR:
            return NTlist()
        if ranges == ALL_RANGES_STR:
            return self.allResidues()
        if ranges == AUTO_RANGES_STR:
            result = self._autoRanges()
            if result == None:
                NTerror('In _rangesStr2list failed _autoRanges')
            return result

        rangesCollapsed = ranges.replace(' ', '')
        rangeStrList = rangesCollapsed.split(',')
        result = NTlist()

        # hashes by keys to use
        resNumDict = NTdict()
        for res in self.allResidues():
            resNumDict.setdefault(res.resNum, [])
            resNumDict[res.resNum].append(res)
#        NTdebug("Residue dict: %s" % resNumDict.items())

        for rangeStr in rangeStrList:
            rangeStrClean = rangeStr
            chainId = None # indicates no chain id present
            firstChar = rangeStr[0]
            if not (firstChar.isdigit() or firstChar == '-'):
                if rangeStr[1] != '.':
                    return None
                rangeStrClean = rangeStr[2:]
                chainId = rangeStr[0]
#            NTdebug("rangeStrClean: [%s] chainId [%s]" % (rangeStrClean, chainId))
            rangeIntList = asci2list(rangeStrClean)
            if not rangeIntList:
                NTwarning("Failed to asci2list in Molecule._rangesStr2list for rangeStrClean: %s" % rangeStrClean)
                continue
            for resNum in rangeIntList:
                if resNumDict.has_key(resNum):
                    for r in resNumDict[resNum]:
                        if (chainId == None) or (r.chain.name == chainId):
#                            NTdebug("r: [%s] chainId [%s]" % (r, chainId))
                            result.append(r)
        result.removeDuplicates()
        # Actually I would have preferred to define the natural ordering of residues in the class as cmp but
        resultSorted = sorted(result, key=attrgetter('chain.name', 'resNum'))
        result.clear()
        result.addList(resultSorted)
        return result
    # end def

    def ranges2resCount( self, ranges ):
        "Return None on error"
        residueList = self.ranges2list(ranges)
        if residueList == None:
            NTerror("Failed to ranges2list in ranges2resCount")
            return None
        return len(residueList)

    def rangesContainsResidue( self, residue, ranges=None  ):
        """Queries the self.selectedResidues in a slow way; scan.
        If ranges != None the the query is even slower because if will use the range.
        """
        selectedResidues = self.selectedResidues
        if ranges != None:
            selectedResidues = self.ranges2list(ranges)
        return residue in selectedResidues


    def ranges2list( self, ranges ):
        """
            Convert
              either:
                 a residue ranges string, e.g. '10-20,34,50-60',
              or
                  a list with residue number or residue instances,
              or
                  None  ==> output will be all residues.

           to a NTlist instance with residue objects.

           Return the list or None upon error.

           See unit test in test_molecule.py
        """
        if ranges == None:
            ranges = self.ranges

        if ranges == None or len(ranges) == 0:
            return self.allResidues()

        if type(ranges) == str:
            return self._rangesStr2list(ranges)

        if isinstance( ranges, list ):
            resnumDict = dict(zip(self.allResidues().zap('resNum'), self.allResidues()))
            result = NTlist()
            for item in ranges:
                if isinstance( item, int ):
                    if resnumDict.has_key(item):
                        result.append(resnumDict[item])
                    else:
                        NTerror('Error Molecule.ranges2list: invalid residue number item [%d]\n', item )
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

        if ranges == None:
            ranges = self.ranges

        if ranges:
            selectedResidues = self.ranges2list( ranges )
        else:
            selectedResidues = self.allResidues()
        # end if
        r = NTlist() # list of residues selected in
        result = [] # list of ranges
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
                    NTerror('Molecule.models2list: invalid model number %d ( < 0 )', model )
                    return None
                if model >= self.modelCount:
                    NTerror('Molecule.models2list: invalid model number %d ( >=  modelCount: %d)',
                             model, self.modelCount
                           )
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
        NTerror('Error Molecule.models2list: undefined models type %s\n', type(models) )
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
        """Create a directory with SML file
           Save sequence, resonances, stereo assignments and coordinates.
           Return self or None on error
        """
        if not path: path = self.objectPath
        if not path:
            NTerror('Molecule.save: undefined path')
        if os.path.exists(path):
            removedir(path)
        os.makedirs(path)

        # save special db entries
        dbpath = os.path.join(path,'Database')
        os.makedirs(dbpath)
        dblist = NTlist()
        for res in self.allResidues():
            if res.db.shouldBeSaved and res.db not in dblist:
                dblist.append(res.db)
        #end for
        #print dblist
        database.saveToSML( dblist, dbpath )

        fpath = os.path.join(path,'molecule.sml')
        if self.SMLhandler.toFile(self, fpath) != self:
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
            NTerror('Molecule.open: path "%s" not found\n', path)
            return None
        #end if

        dbpath = os.path.join( path, 'Database')
        database.restoreFromSML( dbpath, database.NTdb )

        fpath = os.path.join(path,'molecule.sml')
        if (not os.path.exists( fpath )):
            NTerror('Molecule.open: smlFile "%s" not found\n', fpath)
            return None
        #end if

        mol = Molecule.SMLhandler.fromFile(fpath)
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

    def _open094( path )   :
        """Static method to restore molecule from SML file path: 0.75< version <= 0.90
           returns Molecule instance or None on error
        """
        #print '*** Opening using Molecule._open094'

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
    _open094 = staticmethod(_open094)

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
#        NTdebug('content from xml-file: %s', content.format())

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

#        NTdebug('%s', mol.format())

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
#                NTdebug('Molecule._check: atom %s has only %d resonances; expected %d; repairing now',
#                          atm, l, self.resonanceCount)
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
        self.currentResonancesIndex = self.resonanceCount
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

        if not self.resonanceCount:
            NTmessage("Skipping molecule.mergeResonances because there are no resonances")
            return

        for atom in self.allAtoms():
            if len(atom.resonances) != self.resonanceCount:
                NTerror('Molecule.mergeResonances %s: length resonance list (%d) does not match resonanceCount (%d)',
                         atom, len(atom.resonances), self.resonanceCount)
                return
            #end if
            matchedResonance = None
            if selection == None or atom.name in selection:
                for resonance in atom.resonances:
                    if not isNaN(resonance.value):
                        matchedResonance=resonance
                        break
                    #end if
                #end for
            #end if

            if matchedResonance:
                atom.resonances.append(matchedResonance)
            else:
#                NTdebug("For atom no matched resonance yet so let's take the first")
                matchedResonance = atom.resonances[0]
                atom.resonances.append(matchedResonance)
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
#        NTdebug('Defining topology')
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
                                continue
                            atm._topology.append( res[atomName] )

                        except:
                            pass # exceptional cases here
                        #end try
                    #end for
                else:
                    pass
#                    NTdebug('Molecule.updateTopolgy: atm %s: odd db==None', atm)
                #end if
            #end for
        #end for
    #end def

    def updateDihedrals( self, residueList = None)   :
        """Calculate the dihedral angles for all residues
        Return True on error.
        """
#        NTdebug('Calculating dihedral angles')
        if residueList == None:
            residueList = self.allResidues()
        for res in residueList:
#            res.addDihedralsAll()
            for d in res.dihedrals:
                d.calculateValues()
            #end for
            res.setCvBackboneSidechain() # will automatically skip non-amino acids.
        #end for

        if not isinstance(residueList, list):
            NTcodeerror("In updateDihedrals the residueList is not of a class list")
            return True
        if not isinstance(residueList, NTlist):
            residueList = NTlist( *residueList )

        for cvType in [ CV_BACKBONE_STR, CV_SIDECHAIN_STR ]:
            cvList = residueList.zap(cvType)
            av = cvList.average()
#            NTdebug("Set %s to average %s" % ( cvType, av))
            self[cvType] = av[0]
    #end def

    def updateMean( self):
        """Calculate mean coordinates for all atoms
        """
#        NTdebug('modelCount: %d; Calculating mean coordinates', self.modelCount)
        for atm in self.allAtoms():
            atm.calculateMeanCoordinate()

    def idDisulfides(self, toFile=False, applyBonds=True):
        """Identify the disulfide bonds.
        Takes into account residues with missing coordinates as long as they are all missing.
        By default the bonds that are determined with a certainty above CUTOFF_SCORE will actually be
        applied.
        """
        CUTOFF_SCORE = 0.9 # Default is 0.9
        CUTOFF_SCORE_MAYBE = 0.3 # Default is 0.3

        if self.modelCount == 0:
            NTwarning('idDisulfides: no models for "%s"', self)
            return
        #end if

        cys=self.residuesWithProperties('CYS') # Called cysteine if thiol sidechain is not oxidized.
        cyssTmp=self.residuesWithProperties('CYSS') # It might actually have been read correctly as a cystine (lacks an 'e' in the name and an 'H' in the structure as it is reduced.
        for c in cyssTmp:
            if c not in cys:
                cys.append(c)
#        NTdebug('Identify the disulfide bonds between cysteines/cystines: %s' % cys)

        iList = range(len(cys))
        iList.reverse()
        # delete from the end as not to mess up the in operator below.
        for i in iList:
            c = cys[i]
            coordinatesRetrieved = getDeepByKeysOrAttributes(c, 'CA', 'coordinates')
            if not coordinatesRetrieved:
#                NTdebug("No coordinates for CA even set, skipping residue: %s" % c)
                del( cys[i] )
            elif not len(coordinatesRetrieved): # model count see entry 1abt and issue 137
#                NTdebug("No coordinates for CA, skipping residue: %s" % c)
                del( cys[i] )
        pairList = []
        disulfides = [] # same as pairList but with scoreList.
        cyssDict2Pair = {}
        # all cys(i), cys(j) pairs with j>i
        for i in range(len(cys)):
            c1 = cys[i]
            for j in range(i+1, len(cys)):
                c2 = cys[j]
                scoreList = disulfideScore( c1, c2)
                if not scoreList:
                    NTdebug("Failed to get disulfideScore")
                    continue

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
#                            NTdebug('%s was id-ed before with %s so not pairing with %s (no effort will be done to optimize)' % (
#                                  c, c_partner_found_before, c_partner_found ))
                    if toAdd:
                        pair = (c1, c2)
                        pairList.append(pair)
                        disulfides.append( (c1, c2,scoreList))
                        cyssDict2Pair[c1] = pair
                        cyssDict2Pair[c2] = pair
        # end for
        if False: # debug info really.
            if pairList:
                NTdebug( '==> Molecule %s: Potential disulfide bridges: %d. applying bonds: %s' %( self.name, len(pairList), applyBonds))
    #            for pair in pairList:
    #                NTdebug( '%s %s' % (pair[0], pair[1] ))
            else:
                NTdebug( '==> Molecule %s: No potential disulfide bridged residues found', self.name )
        # end if

        if toFile:
            path = self.project.moleculePath('analysis','disulfides.txt')
            f = file(path,'w')
            fprintf(f, '========= Disulfide analysis %s =========\n\n', self)
            for c1,c2,scoreList in disulfides:
                fprintf(f, '%s %s: scores dCa, dCb, S-S dihedral: %s ', c1,c2,scoreList)
                if scoreList[3] >= CUTOFF_SCORE:
                    fprintf(f,' certain disulfide\n')
                elif scoreList[3] >= CUTOFF_SCORE_MAYBE:
                    fprintf(f,' potential disulfide\n')
                else:
                    fprintf(f,'\n')
            #end for
            NTmessage('==> Disulfide analysis, output to %s', path)
#        else:
#            NTmessage('==> Disulfide analysis, no output requested to file')
        #end if

        if applyBonds:
#            NTdebug('Applying %d disulfide bonds' % len(disulfides))
            for c1,c2,scoreList in disulfides:
#                NTdebug('%s %s: scores dCa, dCb, S-S dihedral: %s ' %( c1,c2,scoreList))
                if scoreList[3] < CUTOFF_SCORE:
#                    NTdebug("Skipping potential disulfide")
                    continue
                for c in (c1, c2):
                    if c.hasProperties('CYSS'):
#                        NTdebug("Skipping %s that is already a CYSS" % c)
                        continue
                    c.mutate('CYSS') # this looses connections to ccpn in residue and atom objects.
        #end if

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
            if not res.removeAtom(atom.name):
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
           Check for cis proline and update when found
           Calculate mean coordinates for all atoms
           Generate an ensemble from coordinates
           Generate an atomList
           Define the topological connections
           Calculate the rmsd's

           Return True on error. Note that an empty atom list is not an error perse.
        """

        msgHol = MsgHoL()
        for res in self.allResidues():
            res.addDihedralsAll(msgHol=msgHol)
        msgHol.showMessage(MAX_MESSAGES=2, MAX_DEBUGS = 2)

        if self.modelCount > 0:
            self.syncModels()
            self.updateDihedrals()

            mutantList = []
            #check for cis Pro's
            for res in self.residuesWithProperties('PRO'):
                if res.has_key('OMEGA') and res.OMEGA.isWithinLimits( -90.0, 90.0):
                    # Cis omega; change to cPRO
                    _tmp,new=res.mutate('cPRO')
                    NTmessage('Mutated %s to %s', res.shortName, new.shortName )
#                    res.addDihedralsAll(msgHol=msgHol) # Needed when testing with 1bus.A.cPRO13
                    mutantList.append(res)
                #end if
            #end for
            if mutantList:
                self.updateDihedrals(residueList = mutantList )
            self.updateMean()
            self.ensemble = Ensemble( self )
#            self.atomList = AtomList( self )
#            if not self.atomList:
#                NTcodeerror("Failed to generate AtomList in molecule#updateAll")
            self.idDisulfides()
#            if not self.has_key('ranges'): # JFD: now in init.
#                self.ranges = None
            self.calculateRMSDs()
        #end if
        # Atom list is needed even when no coordinates are present.
        self.atomList = AtomList( self )
        if self.atomList == None:
            NTcodeerror("Failed to generate AtomList in molecule#updateAll")
            return True
        if len(self.atomList) == 0:
            NTwarning("Empty AtomList in molecule#updateAll")

        self.updateTopology()
    #end def


    def initialize( name, path = None, convention=LOOSE, **kwds   ):

        """
Static method to initialize a Molecule from path
Return an Molecule instance or None on error

       fromFile:  File ==  <resName1 [resNum1] [chainId1] [Nterminal|Cterminal]
                            resName2 [resNum2] [chainId2] [Nterminal|Cterminal]
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
                chainId = molecule.ensureValidChainIdForThisMolecule( chainId )

                if f.NF >= 4 and f.dollar[4] == 'Nterminal':
                    Nterminal = True
                else:
                    Nterminal = False

                if f.NF >= 4 and f.dollar[4] == 'Cterminal':
                    Cterminal = True
                else:
                    Cterminal = False

                molecule._addResidue( chainId, resName, resNum, convention, Nterminal=Nterminal, Cterminal=Cterminal )
            #end if
        #end for
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

    def hasNucleicAcid(self):
        for res in self.allResidues():
            if res.hasProperties('nucleic'):
                return True
        return None # is actually the default of course.

    def hasResonances(self):
        """Return True if at least one atom has at least one resonance"""
        for res in self.allResidues(): # faster to split this in 2 loops.
            for atm in res.allAtoms():
                if atm.resonances:
                    return True
        return None # is actually the default of course.

    def hasDNA(self):
        for res in self.allResidues():
            if res.hasProperties('DNA'):
                return True
        return None # is actually the default of course.

#    def molTypeInt(self):
#        """Integer value for fast lookup in db"""
#        return self.mapColorString2Int[ self.colorLabel ]

    def selectFitAtoms( self, fitResidues, backboneOnly=True, includeProtons = False ):
        """
        Select the atoms to be fitted from a list of fitResidues
        return NTlist instance or NoneObject on error

        No longer changes self.ranges
        """

        if self.modelCount <= 0:
            return NoneObject
        #end if

##        self.ensemble = Ensemble( molecule )

        # Partition the Atoms
        fitted        = []
#        fitResidues   = self.ranges2list( ranges )
        # store the ranges
#        self.ranges   = list2asci( fitResidues.zap('resNum'))
#        self.ranges   = self.residueList2Ranges( fitResidues )

        for res in fitResidues:
            for a in res.allAtoms():
                if len(a.coordinates) != self.modelCount:
                    continue
                if ( (not includeProtons and a.isProton()) ):
                    continue
                if backboneOnly and a.isSidechain():
                    continue
                else:
                    fitted.append( a )
                #end if
            #end for
        #end for
#        NTdebug("Atom list to be fitted:\n%s" % fitted)
        return fitted
    #end def

    def _autoRanges(self, autoLimit=LIMIT_RANGES):
        """
        Automatically define a set of ranges for superposition.
        Return a list of residues
        """
        if getDeepByKeysOrAttributes(self.project, 'status', TALOSPLUS_STR, 'completed'):
            NTdebug("Deriving auto ranges from talos plus")
#        if self.project.status.has_key('talosPlus') and self.project.status.talosPlus.completed:
            # we will do two passes:
            # First: select all residues that have S2> autoLimit
            # Second: fill gaps of one for 0.5<S2<autoLimit
            for res in self.allResidues():
                res._tmp = 0 # 0: do not qualify; 1: qualify first round; 2: check in second round
                if res.talosPlus and not isNaN(res.talosPlus.S2):
                    if res.talosPlus.S2>autoLimit:
                        res._tmp = 1
                    elif res.talosPlus.S2>0.5:
                        res._tmp = 2
                    #end if
                #end if
            #end if

            # Pass two
            r = NTlist()
            for res in self.allResidues():
                if res._tmp == 1:
                    r.append(res)
                elif res._tmp == 2:
                    prev = res.sibling(-1)
                    next = res.sibling(1)
                    if prev and prev._tmp == 1 and next and next._tmp == 1:
                        r.append(res)
                #end if
            #end for
            if len(r) > 0:
                return r
            NTwarning(' Molecule._autoRanges: empty list by Talos. Considering other criteria.')
        # end if
        NTdebug(' Molecule._autoRanges: no talos+ data')
        if self.modelCount > 1:
            NTdebug(' Molecule._autoRanges: using cv to auto determine ranges')
            return self.rangesByCv()
        NTdebug(' Molecule._autoRanges: returning all residues')
        return self.allResidues()
    #end def

    def rangesByCv(self, cvCutoff=0.2, includeGapSize = 4, excludeFragmentSize = 4 ):
        #cvWindowSize=3,
        """
        Automatically define a set of ranges on the basis of cv.

        Return a ranges string.
        Return None on error.

        Residues that do not have a backbone cvList such as nucleic acid bases will
        be included if they meet the rest of the criteria.

        First the includeGapSize (DEFAULT: 4) is used to reintroduce the fragments that
        are equal to or shorter than 'includeGapSize'. This prevents small gaps.

        Second the excludeFragmentSize parameter (DEFAULT: 4) will remove a
        short fragment (equal to or shorter than excludeFragmentSize).

        If the result is an empty selection then invert and return all.
        """
        debugRoutine = False

        if self.modelCount < 2:
            if debugRoutine:
                NTdebug("Without multiple models the cv can not be used for determining the ranges in rangesByCv. Currently %s model(s)" % self.modelCount)
            return ALL_RANGES_STR

        residueList = NTlist()
        max_cv = 0.0
        cvWindowSize = 2
#        coefficients = [ 0.25, 0.50, 0.25 ] # part of sample Savitzky-Golay coefficients from Numerical Recipes p 651.
        for ch in self.chains:
            proteinResidues = ch.residuesWithProperties('protein' )
            if len(proteinResidues) == 0:
                if debugRoutine:
                    NTdebug("Adding all residues of non-protein chain: %s" % ch)
                residueList.addList( ch.allResidues() )
            resList = ch.allResidues()
            n = len(resList)
            if not n:
                continue
            cvList = NTlist()
            for r in resList:
                cv = r.getDeepByKeys(CV_BACKBONE_STR)
                if cv == None:
                    cv = 0.0
                cvList.append( cv )
                max_cv = max( max_cv, cv)

            if debugRoutine:
                NTdebug("Found cvList list: %s" % ' '.join([ "%5.2f" % x for x in cvList ]))
            cvListWindowAveraged = cvList
            # Do window averaging by numpy
            if False: # convolve will return a wrong sized array if cvList is smaller
#            if n > 2 and n > cvWindowSize: # convolve will return a wrong sized array if cvList is smaller
                w=ones(cvWindowSize,'d')
                cvListWindowAveraged=convolve(w/w.sum(),cvList,mode='same')
                if debugRoutine:
                    NTdebug("data: %s" % str(cvList))
                cvListWindowAveraged[0] = cvList[0] # Preserves up to the first derivative.
                cvListWindowAveraged[n-1] = cvList[n-1]

                # above works fine except for terminii.
                if debugRoutine:
                    NTdebug("Filtd cvList list: %s" % ' '.join([ "%5.2f" % x for x in cvListWindowAveraged ]))
            for i,r in enumerate(resList): # can be optimized by NTlist method
                if cvListWindowAveraged[i] <= cvCutoff:
                    residueList.append(r)
            # end for
        if not residueList:
            NTwarning("No residues left in rangesByCv; max cvList of any residue: %s. Return all residues." % max_cv)
            return ALL_RANGES_STR
#        if max_cv < 0.2:
#            NTdebug("No residues with cv above 0.2 which is weird. Max cv is: %s" % max_cv)
        if debugRoutine:
            NTdebug("In rangesByCv; max cvList of any residue: %s" % max_cv)

        ranges = self.residueList2Ranges(residueList)
        if ranges == None:
            NTerror("Failed to get residueList2Ranges in rangesByCv")
            return None

        if includeGapSize:
            if debugRoutine:
                NTdebug("Starting includeGapSize with ranges: %s" % ranges)
            startStopList = self.ranges2StartStopList(ranges)
            if startStopList == None:
                NTerror("Failed to get ranges2StartStopList in rangesByCv")
                return None
            i = len(startStopList) - 2 # start of last segment
            while i >= 2:
                j = i/2 #@UnusedVariable
                res1 = startStopList[i-1] # stop
                res2 = startStopList[i] # start
                resDifCount = residueNumberDifference( res1, res2 )
                if debugRoutine:
                    NTdebug("Trying to join 2 ranges [j=%s,i=%s] to a larger one by including residues between: %s %s diff %s" % (j,i, res1,res2, resDifCount))
                if resDifCount == None:
                    if debugRoutine:
                        NTdebug("Failed to get residueNumberDifference in rangesByCv for residues[%s %s]" % (res1,res2))
                    i -= 2
                    continue
                if resDifCount > (includeGapSize+1):
                    if debugRoutine:
                        NTdebug("Skipping gap between: %s %s diff %s includeGapSize %s" % (res1,res2, resDifCount, includeGapSize))
                    i -= 2
                    continue
                # This routine can be use to join adjacent ranges. by virtue of condition "resDifCount == 1"
                if debugRoutine:
                    NTdebug("By includeGapSize, joining 2 ranges (j-1,j) (%s,%s) to a larger one by including residues between" % (j-1,j))
                startStopList[i-1] = startStopList[i+1] # stop last segment
                del startStopList[i+1] # delete stop in a way that deletes can't bite each other.
                del startStopList[i] # delete start
                if debugRoutine:
                    NTdebug("By includeGapSize, ranges modified to: %s" % self.startStopList2ranges(startStopList))
                i -= 2
            # end while
            ranges = self.startStopList2ranges(startStopList)
            if ranges == None:
                NTerror("Failed to get startStopList2ranges in rangesByCv for startStopList %s" % str(startStopList))
                return None
            if debugRoutine:
                NTdebug("Finishing includeGapSize with ranges: %s" % ranges)
        # end if

        if excludeFragmentSize:
            if debugRoutine:
                NTdebug("Starting excludeFragmentSize with ranges: %s" % ranges)
            rangeListNew = []
            for rangeStr in ranges.split(','):
                if debugRoutine:
                    NTdebug("In excludeFragmentSize looking at range: %s" % rangeStr)
                residueListSingleRange = self.ranges2list(rangeStr)
                if residueListSingleRange == None:
                    NTerror("Failed to get ranges2list in rangesByCv for single range: [%s] in rangesByCv" % rangeStr)
                    return None
                if len(residueListSingleRange) <= excludeFragmentSize:
                    if debugRoutine:
                        NTdebug("Short fragment will be ignored in rangesByCv: [%s]" % rangeStr)
                    continue
                rangeListNew.append(rangeStr)
            # end for
            if not rangeListNew:
                NTwarning("No residues left in rangesByCv for ranges: [%s] in rangesByCv after sub selecting for excludeFragmentSize. Returning all residues." % ranges)
                return ALL_RANGES_STR
            ranges = ','.join(rangeListNew)
            if debugRoutine:
                NTdebug("Finishing excludeFragmentSize with ranges: %s" % ranges)
            return ranges # No need to construct this again. It wouldn't simplify the string.
        # end if

        ranges = self.residueList2Ranges(residueList)
        return ranges

    def superpose( self, ranges=None, backboneOnly=True, includeProtons = False, iterations=2, autoLimit=0.7 ):
        """
        Superpose the coordinates of molecule
        returns ensemble or NoneObject on error
        """

#        NTdebug("Now in superpose")
        if self.modelCount <= 0:
            return NoneObject
        #end if
        if ranges == None:
            ranges = self.ranges
        selectedResidues = self.setResiduesFromRanges( ranges, autoLimit=autoLimit )

        fitted = self.selectFitAtoms( selectedResidues, backboneOnly=backboneOnly, includeProtons = includeProtons )

        NTmessage("==> Superposing: fitted %s on %d atoms (residues=%s, backboneOnly=%s, includeProtons=%s)",
                      self, len(fitted), ranges, backboneOnly, includeProtons
                 )
        self.ensemble.superpose( fitted, iterations=iterations )
#        NTdebug("... rmsd's: [ %s] average: %.2f +- %.2f",
#                self.ensemble.rmsd.format('%.2f '), self.ensemble.rmsd.av, self.ensemble.rmsd.sd
#               )
        r = self.calculateRMSDs(ranges=ranges) #@UnusedVariable
#        NTdetail( r.format() )
        return self.ensemble
    #end def


    def calculateRMSDs( self, ranges=None, models = None   ):
        """
        Calculate the positional rmsd's. Store in rmsd attributes of molecule and residues
        Optionally select for ranges and models.
        return rmsd result of molecule, or None on error
        When no models are present return NaN.
        """

#        NTdebug("Now in calculateRMSDs")

        if self.modelCount == 0:
            NTwarning('Molecule.calculateRMSDs: no coordinates for %s', self)
            return NaN
        #end if

        if models == None:
            models = sprintf('%s-%s', 0, self.modelCount-1)

        if ranges == None:
            ranges = self.ranges

        selectedResidues = self.setResiduesFromRanges( ranges )
        if selectedResidues == None:
            NTwarning('Molecule.calculateRMSDs: error in getting selected residues for ranges %s' % ranges)
            return NaN
        if len(selectedResidues) == 0:
            NTwarning('Molecule.calculateRMSDs: no selected residues for ranges %s' % ranges)
            return NaN

        allResiduesWithCoord = self.allResiduesWithCoordinates()
        selectedResiduesWithCoord = allResiduesWithCoord.intersection(selectedResidues)
        ranges = self.residueList2Ranges(selectedResiduesWithCoord)
        selectedModels = self.models2list( models )

        NTdetail("==> Calculating rmsd's (ranges: %s, models: %s)", ranges, models)

        comment = 'Ranges %s' % ranges
        self.rmsd = RmsdResult( selectedModels, selectedResiduesWithCoord, comment=comment )
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
            if res in selectedResiduesWithCoord:
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
                        if len(atm.coordinates)>=(model+1): # JFD adds because for now I don't seem to be able to do Residue#removeAtom.
                            Vbb.append(atm.coordinates[model].e)
                        else:
                            Vbb.append(atm.coordinates[0].e)
                            NTcodeerror("TODO: fix Residue#removeAtom.")
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
                        if len(atm.coordinates)>=(model+1): # JFD adds because for now I don't seem to be able to do Residue#removeAtom.
                            Vhv.append(atm.coordinates[model].e)
                        else:
                            Vhv.append(atm.coordinates[0].e)
                            NTcodeerror("TODO: fix Residue#removeAtom.")
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

    def toPDB(self, fileName = None, model=None, ranges=None, convention=IUPAC, max_models=None,
              useRangesForLoweringOccupancy=False):
        """
        Return a PyMMlib PDBfile instance or None on error
        Format names according to convention
        Only export model if specified.
        Note that the first model is model numbered zero.
        Return None on error or pdbfile object on success.
        If the fileName is set it will do an actual write.
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

        useRanges = ranges and not self.rangesIsAll(ranges)
        rangesStr = '' #@UnusedVariable
        resHashSelection = NTdict() # use for speed
#        NTdebug("In toPDB ranges: %s useRanges %s" % (ranges, useRanges))
        if useRanges:
            rangesStr = ', ranges: %s' % ranges #@UnusedVariable
            resListSelection = self.ranges2list(ranges)
            resHashSelection.appendFromList(resListSelection)
#        NTdebug("In toPDB resHashSelection.keys: %s" % str(resHashSelection.keys()))
#        NTdebug("==> Exporting to PDB file (%s convention, models: %d-%d%s) ... ",
#                   convention, models[0], models.last(), rangesStr                 )

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
                for res in chain.allResidues():
                    inSelection = resHashSelection.has_key(res)
#                    NTdebug("In toPDB inSelection %s for residue: %s" % (inSelection,res))
                    if useRanges and (not inSelection) and (not useRangesForLoweringOccupancy):
#                        NTdebug("In toPDB skipping residue: %s" % res)
                        continue
                    for atm in res.allAtoms():
                        atm.setdefault('pdbSkipRecord',False)
                        if atm.pdbSkipRecord:
                            continue
                        record = atm.atomToPDB( pdbIndex=atmCount, model=m, convention=convention )
                        if not record:
                            # this happens for all Q and even for like Cys HG which aren't always present in actual structure
                            # but are defined in db.
    #                        NTwarning("Failed to get PDB atom record for atom: " + `atm`)
                            continue
                        if useRangesForLoweringOccupancy:
                            if useRanges and (not inSelection) and atm.isBackbone() and (
                                atm.name == 'CA' or atm.name == "P" ):
                                record.occupancy = 0.49 # special meaning in Whatif for ignoring the residue in Structure Z-scores.
#                                NTdebug("In toPDB lowering occ. to below half for atom: %s" % atm)
                        pdbFile.append( record )
                        atmCount += 1
                        lastAtm = atm
                    #end for
                #end for
                if lastAtm and convention != XPLOR:
                    record = lastAtm.toPDBTER( pdbIndex=atmCount, convention=convention )
                    if not record:
#                        NTdebug("Failed to create a PDB file terminating record; ignoring for now.") # TODO check if this matters.
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

        if fileName:
            pdbFile.save(fileName)
            # Can't test the above for success so let's try this:
            if not os.path.exists(fileName):
                NTerror("Failed to find pdb file %s or has zero size." % fileName)
                return None
            if os.path.getsize(fileName) == 0:
                NTerror("Found pdb file %s with zero size." % fileName)
                return None
        # end if
        return pdbFile
    #end def

    def toSML(self, stream=sys.stdout ):
        if hasattr(Molecule,'SMLhandler'):
            Molecule.SMLhandler.toSML( self, stream )
        else:
            NTerror('Molecule.toSML: no SMLhandler defined')
        #end if
    #end def


    def radiusOfGyration( self, ranges=None, model=0 ):
        """
        Return radius of gyration of model.
        Uses CA coordinates
        Following
        HAVEL and WUTHRICH. AN EVALUATION OF THE COMBINED USE OF NUCLEAR MAGNETIC-RESONANCE AND DISTANCE GEOMETRY
        FOR THE DETERMINATION OF PROTEIN CONFORMATIONS IN SOLUTION.
        Journal of Molecular Biology (1985) vol. 182 (2) pp. 281-294

        Algorithm: pp. 284
        """


        if ranges==None:
            ranges = self.ranges

        if ranges==None:
            residues = self.allResidues()
        else:
            residues = self.setResiduesFromRanges(ranges)
        #end if

        xx  = 0.0
        yy  = 0.0
        zz  = 0.0
        xy  = 0.0
        xz  = 0.0
        yz  = 0.0
        n = 0
        for res in residues:
            if res.hasProperties('protein') and res.CA.hasCoordinates() and model < len(res.CA.coordinates):
                x = res.CA.coordinates[model].x
                y = res.CA.coordinates[model].y
                z = res.CA.coordinates[model].z
                xx  += x*x
                yy  += y*y
                zz  += z*z
                xy  += x*y
                xz  += x*z
                yz  += y*z
                n += 1
            #end if
        #end for

        a = numpy.array([
                      [yy+zz,      -xy,      -xz],
                      [  -xy,    xx+zz,      -yz],
                      [  -xz,      -xy,    xx+yy]
                     ])
        a = a*(3.0/n)

        w, v = LA.eig(a)
        print w,v
        return NTlist(*map(math.sqrt, w))
    #end def
#end class


class Ensemble( NTlist ):
    """
    Ensemble class hold is a list of Models instances.
    Initialization is done from a Molecule instance, thus the class represents
    a different arrangement of the coordinate instances of a molecule.
    """
    def __init__( self, molecule=None ):
        NTlist.__init__( self )
        self.averageModel       = None
        #self.closestToMeanModel = None # not yet used
        self.molecule           = molecule

        if self.molecule == None:
            return # allow he class to be initialised without a molecule instance

        for i in range(0,molecule.modelCount):
            mName = sprintf('%s_model_%d', molecule.name, i)
            m = Model(mName, i )
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
        return rmsd between self and other using fitCoordinates or NaN on Error
        """
        v1 = self.fitCoordinates.zap( 'e' )
        v2 = other.fitCoordinates.zap( 'e' )
        if len(v1) != len(v2):
            NTerror("Model.superpose: unequal length fitCoordinates (%s and %s)", self, other)
            return NaN
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
                         backbone        = NTfill(0.0, len(modelList)), # needs to match BACKBONE_STR
                         backboneCount   = 0,
                         backboneAverage = NTvalue( NaN, NaN, fmt='%4.2f +- %4.2f', fmt2='%4.2f' ),

                         heavyAtoms      = NTfill(0.0, len(modelList)), # needs to match HEAVY_ATOMS_STR
                         heavyAtomsCount = 0,
                         heavyAtomsAverage = NTvalue( NaN, NaN, fmt='%4.2f +- %4.2f', fmt2='%4.2f'  ),

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

    def format(self, allowHtml=False):
        msg = sprintf(
                       'backboneAverage:      %s\n'  +\
                       'heavyAtomsAverage:    %s\n'  +\
                       'models:               %s\n' +\
                       'backbone   (n=%4d): [%s]\n' +\
                       'heavyAtoms (n=%4d): [%s]\n' +\
                       'closestToMean:        model %d\n',
                       str(self.backboneAverage),
                       str(self.heavyAtomsAverage),
                       self.models.format('%4d '),
                       self.backboneCount,
                       self.backbone.format(fmt='%4.2f '),
                       self.heavyAtomsCount,
                       self.heavyAtoms.format(fmt='%4.2f '),
                       self.closestToMean
                      )
        if allowHtml:
            msg = addPreTagLines(msg)
        return '\n'.join( [self.header(), msg, '' ])
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






class Chain( NTtree, ResidueList ):
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
    defaultChainId = _DEFAULT_CHAIN_ID
    'See documentation: molecule#ensureValidChainId'

    NULL_VALUE = 'CHAIN_CODE_NULL_VALUE' # can not be a valid chain code but needs to be able to be passed on commandline
    # like in: Scripts/getPhiPsiWrapper.py

    def __init__( self, name, **kwds ):
        NTtree.__init__( self, name=name, __CLASS__='Chain', **kwds )
        self.__FORMAT__ =  self.header( dots ) + '\n' +\
                          'residues (%(residueCount)d): %(residues)s\n' +\
                           self.footer( dots )
        self.rogScore = ROGscore()
        self[CHK_STR] = NTdict()
        self.residues = self._children
        self.residueCount = 0
    #end def

    def isNullValue(id):
        return id == Chain.NULL_VALUE
    isNullValue = staticmethod( isNullValue )


    def addResidue( self, resName, resNum, convention=INTERNAL, Nterminal=False, Cterminal=False, FiveTerminal=False, ThreeTerminal=False, **kwds ):
        if self.has_key(resNum):
            NTwarning( 'Chain.addResidue: residue number "%s" already present in %s perhaps there is a insertion code? Skipping residue', resNum, self )
            NTwarning("See also issue: %s%d" % (issueListUrl, 226))
            return None
        #end if
        res = Residue( resName=resName, resNum=resNum, convention=convention, Nterminal=Nterminal, Cterminal=Cterminal, **kwds )
        if res.name in self:
            NTwarning( 'Chain.addResidue: residue "%s" already present in %s; skipping residue', res.name, self.name )
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
        if not residue in self._children:
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
        if res == None:
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

    def countDsspSecStructConsensus(self):
        """Determine if molecule has at least one of alpha or beta protein regions.
        Molecule may contain other types of macromolecules than protein.
        Return None if DSSP wasn't run or no amino acids are present.
        """
        countA = 0
        countB = 0
        countC = 0
        for res in self.allResidues():
            r = getDsspSecStructConsensus( res )
            if r == DSSP_H:
                countA += 1
            elif r == DSSP_S:
                countB += 1
            else:
                countC += 1
        return countA, countB, countC


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

        # restraints associated with this residue; filled in partition restraints
        self.distanceRestraints = RestraintList('distanceRestraints')
        self.dihedralRestraints = RestraintList('dihedralRestraints')
        self.rdcRestraints      = RestraintList('rdcRestraints')

        self.cv_backbone = None # filled by self.setCvBackboneSidechain. Needs to be matched by cing.core.constants#CV_BACKBONE_STR
        self.cv_sidechain = None
        self.rmsd = None # will be filled by molecule.calculateRMSDs.
        self.rogScore = ROGscore()
        self[CHK_STR] = NTdict()

        self.__FORMAT__ =  self.header( dots ) + '\n' +\
                          'shortName:  %(shortName)s\n' +\
                          'chain:      %(chain)s\n' +\
                          'atoms (%(atomCount)2d): %(atoms)s\n' +\
                           self.footer( dots )
    #end def

    def __repr__(self):
#        return sprintf('<Residue %s>', self._Cname(-1))
        return self.__str__()
    #end def

    def __str__(self):
#        return sprintf('<Residue %s>', self._Cname(-1))
        return sprintf('<Residue %s>', self.toString())
    #end def

    def toString(self, showChainId=True, showResidueType=True):
        """A unique compact string identifier.e.g B.LYS282"""
        if showChainId:
            chn = self._parent
            chnName = '?'
            if chn != None: # Happens when debugging  functions that happen early in setting up a molecule.
                chnName = chn.name
            result = chnName + '.'
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
        # find the database entry in database.NTdb (which is of type MolDef)
        db = database.NTdb.getResidueDefByName( resName, convention )
        if not db:
#            NTdebug('Residue._nameResidue: residue "%s" not defined in database by convention [%s]. Adding non-standard one now.' %( resName, convention))
            database.NTdb.appendResidueDef( name=resName, shortName = '_', commonName = resName,
                                            nameDict = {INTERNAL_0:resName, INTERNAL_1:resName, INTERNAL:resName, convention:resName},
                                            comment = 'Non-standard residue'
                                          )
            db = database.NTdb.getResidueDefByName( resName, convention ) # checking if things went ok1
            if not db:
                NTcodeerror("Residue._nameResidue: Added residue '%s' but failed to find it again", resName)
        #end if
        self.resNum   = resNum
        self.db        = db
        self.name      = db.commonName + str(resNum)
        self.shortName = db.shortName + str(resNum)
        self.resName   = db.translate(INTERNAL)
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
        newName = self.db.commonName + str(newResNum)
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

        NB this looses connections from/to CCPN in residue and atom objects.

        Return (self,newResidue) tuple or None on error
        """
        # find the database entry
        if resName not in database.NTdb:
            #self.db = database.NTdb[self.resName]
            NTerror('Residue.mutate: residue "%s" not defined in database', resName )
            return None
        #end if
        newRes  = Residue( resName, self.resNum )
        if not newRes:
            NTerror('Residue.mutate: error defining residue "%s"', resName )
            return None
        #end if

#        NTdetail('==> Mutating %s to %s', self._Cname(-1), resName )

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
                # remove the references to atm from self
                atm = self.removeChild( self[atmDef.name] )
                for alias in atm.db.aliases:
                    if alias in self:
                        del(self[alias])
                #end for
                self.atomCount -= 1

                #add the atom to newRes
                atm.residue = newRes
                atm.db = atmDef
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

        # dihedrals
        newRes.addDihedralsAll()
        for d in newRes.dihedrals:
            d.calculateValues()

        return self,newRes
    #end def

    def removeAtom(self, name, convention=INTERNAL ):
        """JFD adds: GV please check
        Return Atom on success or None on error
        """
        atm = self.getAtom(name, convention=convention)
        if not atm:
            return None
        if atm.db:
            for alias in atm.db.aliases:
                if alias in self:
                    del(self[alias])
        self.removeChild( atm )
        self.atomCount -= 1
        self._parent._parent.atomCount -= 1
        return atm

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
                # GWV: skip non-relevant N- and C-terminal atoms
                if not self.Nterminal and database.isNterminalAtom(atm):
                    pass
                elif self.Nterminal and atm.translate(INTERNAL_0) == 'HN':
                    pass
                elif not self.Cterminal and database.isCterminalAtom(atm):
                    pass
                else:
                    self.addAtom( atm.name )
                #end if
            #end for
        #end if
    #end def

    def addDihedralsAll(self,msgHol=None):
        """Add all dihedrals according to definition database plus
        the new D1.
        """
        # Speed optimization.
        if self.hasProperties('water'):
            return

        if self.db:
            self.dihedrals = NTlist()
            for d in self.db.dihedrals:

                dihed = Dihedral( self, d.name )
                if dihed == None:
                    continue

                if dihed.atoms == None:
                    continue
 #               print '>>',dihed.format()

                missingCoordinates = False
                for a in dihed.atoms:

                    if len(a.coordinates) != self.chain.molecule.modelCount:
                        missingCoordinates = True
                        continue
                #end for
                if missingCoordinates:
                    continue

                self.dihedrals.append(dihed)
                self[dihed.name] = dihed
                # if db and aliases, add them; e.g. DNA/RNA DELTA==NU3
                if dihed.db:
                    for aname in dihed.db.aliases:
                         self[aname] = dihed
                    #end for
                #end if
            #end for
        #end if
        self.addDihedralD1(msgHol=msgHol)
    #end def

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

#        if (convention != INTERNAL):
#            atomName = translateAtomName( convention, self.translate(convention), atomName, INTERNAL )
#        #end if
        aDef = self.db.getAtomDefByName( atomName, convention )
        if aDef and self.has_key(aDef.name):
            return self[aDef.name]
        #end if

        # For when the atom defs were not store with CING project as with entry 2ksi.B.PLM200
        # TODO: GWV to review.
#        if self.has_key(atomName):
#            return self[atomName]

        return None
    #end def

    def getMinDistanceCalpha(self, other):
        """
        Returns the minimum distance between the C alphas in the ensemble of models.
        Meant to be a fast quiet routine.
        Returns None if no C alpha atoms or coordinates are present.
        """
        caSelf = getDeepByKeysOrAttributes(self, "CA")
        if not caSelf:
            return None
        caOther = getDeepByKeysOrAttributes(other, "CA")
        if not caOther:
            return None
        return caSelf.getMinDistance(caOther)

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

    def isNterminal(self):
        """Return True for N-terminal residue; ie. a residue with H1, H2, H3 atoms.
        """
        return self.Nterminal

    def isCterminal(self):
        """Return True for C-terminal residue; ie. a residue with OXT (O'') atom.
        """
        return self.Cterminal

    def isCommon(self, resType):
        """Return True if residue is one of the common 20 AA or 5 NA.
        """
        return resType in commonResidueList

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

    def hasCoordinates(self):
        """
        Returns False if all atoms have no coordinates.
        Returns True if any atom has a coordinate.
        """
#        NTdebug("Checking residue.hasCoordinates for %s" % self)
        for atom in self.allAtoms():
            if atom.hasCoordinates():
                return True
        return False
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

    def setCvBackboneSidechain(self):
#        if not self.hasProperties('protein'):
#            NTdebug("Skipping setCvBackboneSidechain for non-protein residue: %s" % self.name)
#            return
        # CING doesn't use IUPAC nomenclature for chi beyond 1. E.g. the IUPAC Chi2,1 in Ile is simply named Chi2.
        # This is incorrect but does make the code very simple here.
        # Optimized for speed so no loop setups.
        cv1 = getDeepByKeysOrAttributes(self, PHI_STR, CV_STR)
        cv2 = getDeepByKeysOrAttributes(self, PSI_STR, CV_STR)
        self.cv_backbone = NTcVarianceAverage( (cv1, cv2) )
        # This still fails by issue
#        if 'PRO' in self.resName:
#            NTdebug("Pro cv phi,psi,avg %s %s %s %s" % (cv1, cv2, self.cv_backbone, self.name))
        if False:
            fmt = '%8.3f'
            count = 8
            NTdebug('%20s phi/psi/avg: %s %s %s' % (self,
                val2Str(cv1, fmt, count),
                val2Str(cv2, fmt, count),
                val2Str(self.cv_backbone, fmt, count)))
        cv1 = getDeepByKeysOrAttributes(self, CHI1_STR, CV_STR)
        cv2 = getDeepByKeysOrAttributes(self, CHI2_STR, CV_STR)
        self.cv_sidechain = NTcVarianceAverage( (cv1, cv2) )

    def addDihedralD1(self,msgHol=None):
        """Calculates and adds the Cb4N dihedral to this residue and the same dihedral as
        Cb4C to the previous residue.

        Return None on error.
        First residue in chain will return a d1 of None.
        """

        if not self.hasProperties('protein'):
            return
#        TODO: change to HA3 when CING switches to IUPAC
        doublet = NTlist()
        for i in [-1,0]:
            doublet.append( self.sibling(i) )

        if None in doublet:
            if not self.isNterminal():
                msg = 'Residue.addDihedralD1: skipping non N-terminal residue without doublet %s (missing preceding neighbor but not N-terminal)' % self
                if msgHol == None:
                    NTdebug(msg)
                else:
                    msgHol.appendDebug(msg)
            return
        CA_atms = doublet.zap('CA')
        CB_atms = [] # CB or Gly HA3 (called HA2 in INTERNAL_0) atom list
        for doubletResidue in doublet:
            resTypeSimple = getDeepByKeys(doubletResidue.db.nameDict, IUPAC)
            if resTypeSimple not in commonAAList:
#                NTdebug( "Skipping doublet %s with uncommon residue: %s" % (doublet, doubletResidue))
                continue

#            CB_atm = None
#            if doubletResidue.has_key('CB'):
#                CB_atm = doubletResidue.CB
#            elif doubletResidue.has_key(GLY_HA3_NAME_CING):
#                CB_atm = doubletResidue[GLY_HA3_NAME_CING]
#            else:
#                NTerror( 'Molecule.addDihedralD1: skipping for absent CB/%s in doubletResidue %s of doublet %s' % ( GLY_HA3_NAME_CING, doubletResidue, doublet ))
#                continue

            # Use the API!
            if doubletResidue.hasProperties('GLY'):
                CB_atm = doubletResidue.getAtom('HA3',IUPAC)
            else:
                CB_atm = doubletResidue.getAtom('CB',IUPAC)
            if not CB_atm:
                msg = 'Residue.addDihedralD1: skipping for absent CB/%s in doubletResidue %s of doublet %s' % ( GLY_HA3_NAME_CING, doubletResidue, doublet )
                if msgHol == None:
                    NTerror(msg)
                else:
                    msgHol.appendError(msg)
                continue

            CB_atms.append(CB_atm)
#                print res, triplet, CA_atms, CB_atms
        if len(CB_atms) != len(doublet): # skip for preceding or trailing uncommon residues for now.
#            NTdebug( '"CB" (or %s) missing in triplet %s' % (GLY_HA3_NAME_CING, doublet ))
            return
        prevRes = doublet[0]
        d1 = Dihedral( self, DIHEDRAL_NAME_Cb4N, range=range0_360)
        d1PrevRes = Dihedral( prevRes, DIHEDRAL_NAME_Cb4C, range=range0_360)
        d1.atoms = [CB_atms[0], CA_atms[0], CA_atms[1], CB_atms[1]]
        d1PrevRes.atoms = d1.atoms

        missingCoordinates = False
        for a in d1.atoms:
            if len(a.coordinates) != self.chain.molecule.modelCount:
                missingCoordinates = True
                continue
        #end for
        if missingCoordinates:
            if False:
                msg = 'Residue.addDihedralD1: skipping residue %s because of missing atoms' % self
                # wrap this call so that not all get printed; very common in X-ray structures like 2uva
                if msgHol == None:
                    NTdebug(msg)
                else:
                    msgHol.appendDebug(msg)
            return


#        d1.calculateValues() Should not do this as it will be done in updateAll
#        d1PrevRes.calculateValues()
        self[DIHEDRAL_NAME_Cb4N] = d1 # append dihedral to residue
        prevRes[DIHEDRAL_NAME_Cb4C] = d1PrevRes # append dihedral to residue
        self.dihedrals.append(d1)
        prevRes.dihedrals.append(d1PrevRes)

        # Make sure we always have something to hold onto.
        d1_value_list = getDeepByKeysOrDefault( self, [ NaN ], DIHEDRAL_NAME_Cb4N)
        return d1_value_list
    #end def

    def getTripletHistogramList(self, doOnlyOverall = False, ssTypeRequested = None, doNormalize = False, normalizeSeparatelyToZ = False ):
        """Returns a list of convoluted 1d by 1d -> 2d histo over 3 residues (a triplet) or
        an empty array when it could not be constructed.

        See namesake method in this module's name space for complete documentation on parameters.
        Return None on error.
            or empty array when it could not be constructed.
        """

        if True: # just a checking block.
            triplet = NTlist()
            tripletIdxList = [0,-1,1] # Note that this was a major bug before today June 3, 2010. Matches the one in
            # cing.core.validate#validateDihedralCombinations

    #        for i in [-1,0,1]:
            for i in tripletIdxList:
                triplet.append( self.sibling(i) )

            if None in triplet:
    #            NTdebug( 'Skipping residue without triplet %s' % self)
                return []

#        resTypePrev = getDeepByKeys(triplet[-1].db.nameDict, IUPAC) # bug 4 fixed on June 4, 2010
#        resType     = getDeepByKeys(triplet[ 0].db.nameDict, IUPAC)
#        resTypeNext = getDeepByKeys(triplet[ 1].db.nameDict, IUPAC)
        resTypePrev = getDeepByKeys(self.sibling(-1).db.nameDict, IUPAC)
        resType     = getDeepByKeys(            self.db.nameDict, IUPAC)
        resTypeNext = getDeepByKeys(self.sibling (1).db.nameDict, IUPAC)
        resTypeListBySequenceOrder = ( resTypePrev, resType, resTypeNext)
        return getTripletHistogramList(resTypeListBySequenceOrder, doOnlyOverall = doOnlyOverall, ssTypeRequested = ssTypeRequested,
                                       doNormalize = doNormalize, normalizeSeparatelyToZ = normalizeSeparatelyToZ )


    def toSML(self, stream=sys.stdout ):
        if hasattr(Residue,'SMLhandler'):
            Residue.SMLhandler.toSML( self, stream )
        else:
            NTerror('Residue.toSML: no SMLhandler defined')
        #end if
    #end def

    def validateChemicalShiftLeu( self, resultList ):
        """Returns True on error.
        Append to result list if validation found a problem.

        Uses the data in:
        Frans Mulder's Leucine side-chain conformations and dynamics in proteins from 13D NMR chemical shifts. ChemBioChem (2009)

        DELTA delta(13C) = 13CD1-13CD2 = -5 + 10*Pt (Eq.2)

        With Pt is the portion trans (180) for chi2 and assumed Pt = 1 - Pg.
        With Pg being gauche+ (60) for chi2

        The cutoff for assuming the CS difference indicates multiple rotameric state is set to -4 < csd < 4 which corresponds to
        0.1 < Pt < 0.9.

        The cutoff for assuming the chi2 dihedral is sampling multiple rotameric states is set to having a cv over 0.2.

        In case there is only one model the one state will be used for comparison.

        If the csd < 0.01 then the resonances were assumed to overlap and no critiques are attempted.

        TODO:
            -
        """

        CUTOFF_LOL_CSD_LEU_CD = [[ -4, 4 ], [ -3, 3 ]] # ERROR/WARNING LIMITS
        cvCutOffList = [ 0.2, 0.2 ]
        if not self.hasProperties('LEU'):
            NTerror("Can not validateChemicalShiftLeu for non Leu: %s" % self)
            return True
        # Allready generalize for VAL application TODO:
        atomC1 = self.CD1
        atomC2 = self.CD2
        c1Shift = atomC1.shift()
        c2Shift = atomC2.shift()
        chi = getDeepByKeysOrAttributes( self, CHI2_STR )
        if chi == None:
            NTdebug("Skipping %s for missing dihedral" % self)

        if isNaN( c1Shift ) or isNaN( c2Shift ):
            NTdebug("CS unavailabe for both Cs for %s" % self)
            return

        shiftDifference = c1Shift - c2Shift
        if math.fabs(shiftDifference) < 0.01:
            NTdebug("shiftDifference zero so assuming they were not ssa" % self)
            return

        if not atomC1.isStereoAssigned():
            NTdebug("%s is not ssa" % atomC1)
            return

#        shiftDifference = -5. + 10.*Pt
        Pt = (shiftDifference + 5.)/10.
        PtLimited = limitToRange(Pt, 0., 1.)
        if Pt != PtLimited:
            NTwarning("CS difference for C in %s exceed expected range of [-5,5] being at %s" % (self, shiftDifference))
            Pt = PtLimited

#        for i,color in enumerate( [ COLOR_RED, COLOR_ORANGE ]):
        for i,color in enumerate( [ COLOR_RED ]):
            str = None
            rangeListCd = CUTOFF_LOL_CSD_LEU_CD[i]
            # Determine CS indication
            csIndicatesAveraging = rangeListCd[0] < shiftDifference < rangeListCd[1]
            csIndicatesSingleConformer = None
            if not csIndicatesAveraging:
                if shiftDifference < rangeListCd[0]:
                    csIndicatesSingleConformer = DIHEDRAL_60_STR
                else:
                    csIndicatesSingleConformer = DIHEDRAL_180_STR

            # Determine CV indication
            if getDeepByKeysOrAttributes(chi, CV_STR) == None:
                NTerror("Failed to get chi cv of %s" % self)
                return True

            cvIndicatesAveraging = chi.cv >= cvCutOffList[ i ]
            dihedralIndicatesSingleConformer = chi.getRotamerState()
            if dihedralIndicatesSingleConformer == None:
                NTerror("Failed to get rotameric state of %s" % self)
                return True
            NTdebug("res shiftDifference, csIndicatesAveraging, csIndicatesSingleConformer, cvIndicatesAveraging, dihedralIndicatesSingleConformer: %10s %8.3f %s %s %s %s" % (
                   self, shiftDifference, csIndicatesAveraging, csIndicatesSingleConformer, cvIndicatesAveraging, dihedralIndicatesSingleConformer ))

            if dihedralIndicatesSingleConformer == DIHEDRAL_300_STR:
                str = 'Conformer %s chi impossible regardless of csd value [%.3f]' % (dihedralIndicatesSingleConformer, shiftDifference)
                # will be flagged by other software as well so eliminate here?
            else:
                if cvIndicatesAveraging:
                    if csIndicatesAveraging:
                        pass
                    else:
                        str = 'csd [%.3f]: single conformer but cv [%.3f]' % (shiftDifference, chi.cv)
                    # end if
                else:
                    if csIndicatesAveraging:
                        str = 'csd [%.3f]: averaging but cv [%.3f]' % (shiftDifference, chi.cv)
                    else:
                        # cs and dihedral agree on single conformer. Now do they match?
                        if csIndicatesSingleConformer == dihedralIndicatesSingleConformer:
                            continue
                        str = 'csd [%.3f]: %s but found %s' % ( shiftDifference, dihedralIndicatesSingleConformer)
                    # end if
                # end if
            # end if
            if not str:
                continue
            NTdebug("critque: %s %s" % ( color, str))
            resultList.append( atomC1 ) # Just do this once.
#            atomC1.validateAssignment.append(str)
            atomC1.rogScore.setMaxColor( color, comment = str )
            if i == 0: # skip orange if red was already established
                return
        # end for
#    # end def

    def validateChemicalShiftProPeptide( self, resultList ):
        """Returns True on error.
        Append to result list if validation found a problem.

        Uses the data in:
        Schubert et al. A software tool for the prediction of Xaa-Pro peptide bond conformation in proteins based on 13C chemical shift statistics. J Biomol NMR (2002) vol. 24 (2) pp. 149-54
        From their text:
        100% certainty  trans    [0.0,  4.8]
                        cis      [9.15,14.4]
        Conflicts will be marked as bad.

        For a poor mark the cutoffs are shrunk by 1.2 ppm (1 sd) to:
                        trans    [0.0,  6.0]
                        cis      [7.95,14.4]

        The first model in the ensemble is used for determining if the cis or trans nature. I.e. no provision for
        dynamics on this is provided.
        """

        if not ( self.hasProperties('PRO') or self.hasProperties('cPRO')):
            NTerror("Can not validateChemicalShiftProPeptide for non Pro: %s" % self)
            return True
        atomCb = self.CB
        atomCg = self.CG
        cbShift = atomCb.shift()
        cgShift = atomCg.shift()

        if isNaN( cbShift ) or isNaN( cgShift ):
#            NTdebug("CS unavailabe for CB and/or CG for %s" % self)
            return

        shiftDifference = cbShift - cgShift
        if shiftDifference < 0.:
            str = sprintf('For %s the difference of cb %8.3f minus cg  %8.3f: was not expected to be negative but is %8.3f.' % (self, cbShift,cgShift,shiftDifference))
            NTdebug(str)
            resultList.append( atomCb ) # Just do this once.
            atomCb.validateAssignment.append(str)
            return

        omega = getDeepByKeysOrAttributes( self, OMEGA_STR)
        if omega == None:
            # Happens for CGR26AUtrecht2
            NTwarning("Failed to find the omega dihedral angle for: %s" % self)
            return

        isTrans = omega.isWithinLimits(90.,270.,checkMore=True)
        if isTrans == None: # in case of absent coordinates.
            NTdebug("Failed to find peptide configuration for %s" % self)
            return

        color = COLOR_GREEN
        if shiftDifference < 4.8 and not isTrans:
            str = "CS CB-CG %8.3f (<4.8) contradicted a trans state with great certainty." % shiftDifference
            color = COLOR_RED
        elif shiftDifference > 9.15 and isTrans:
            str = "CS CB-CG %8.3f (>9.15) contradicted a cis state with great certainty."  % shiftDifference
            color = COLOR_RED
        if shiftDifference < 6.0 and not isTrans:
            str = "CS CB-CG %8.3f (<6.0) contradicted a trans state."  % shiftDifference
            color = COLOR_ORANGE
        elif shiftDifference > 7.95 and isTrans:
            str = "CS CB-CG %8.3f (>7.95) contradicted a cis state."  % shiftDifference
            color = COLOR_ORANGE

        if color == COLOR_GREEN:
            return

        resultList.append( atomCb ) # Just do this for one atom of the residue..
        atomCb.validateAssignment.append(str)
        NTdebug("For %s found %s" % (self, str))
        if color == COLOR_RED:
            atomCb.rogScore.setMaxColor( COLOR_RED, atomCb.validateAssignment )
#end class

class Dihedral( NTlist ):
    """
    Class to represent a dihedral angle
    """

    def __init__(self, residue, dihedralName, range=None ):
        NTlist.__init__(self)

        self.residue = residue
        self.name = dihedralName
        self.atoms = None # Moved up here for clarity.
        self.db = None
        self.range = range
        self.cav = NaN
        self.cv  = NaN

        if not range:
            plotpars = plotParameters.getdefault(dihedralName,'dihedralDefault')
            self.range = ( plotpars.min, plotpars.max )
        #end if

        if not (not dihedralName or not residue or not residue.db or not residue.db.has_key(dihedralName)):
            self.db = residue.db[dihedralName]
            atoms = translateTopology( self.residue, self.db.atoms )
            if not (atoms == None or len(atoms) != 4 or None in atoms):
                self.atoms  = atoms
                #add dihedral to dict for lookup later
                self.residue.chain.molecule._dihedralDict[(atoms[0],atoms[1],atoms[2],atoms[3])] = \
                    (self.residue, dihedralName, self.db)
                self.residue.chain.molecule._dihedralDict[(atoms[3],atoms[2],atoms[1],atoms[0])] = \
                    (self.residue, dihedralName, self.db)
            #end if
        #end if
    #end def

    def isWithinLimits(self, lower, upper, checkMore = False):
        """
        Check id cav is within [lower,upper] taking periodicity into account.
        When checkMore is set then the presence of a self.cav will be checked rather then assumed.
        The signal for absence of self.cav will be a return value of None.
        """
        if checkMore:
            if isNaN(self.cav):
                return None

        tmp = NTlist(self.cav).limit(lower,lower+360.0) # Rescale cav to the range lower, lower+360.0
        if tmp[0] >= lower and tmp[0] <= upper:
            return True
        return False
    #end def

    def getRotamerState(self):
        """
        Return None on error or
        DIHEDRAL_60_STR etc.
        Lowerbound is inclusive. E.g. 0 and 360 become DIHEDRAL_60_STR
        """
        if self.cav == None:
            return None
        cav = to_0_360( self.cav )
        if cav < 120.:
            return DIHEDRAL_60_STR # zero inclusive
        if cav < 240.:
            return DIHEDRAL_180_STR
        return DIHEDRAL_300_STR # 240 inclusive. 360 never occurs here.


    def __str__(self):
        if self.residue:
            dname = self.residue.name + '.' + self.name
        else:
            dname = self.name
        #end if
        return sprintf('<Dihedral %s: %.1f, %.2f>', dname, self.cav, self.cv)
    #end def

    def __repr__(self):
        return self.__str__()

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

        del(self[:]) # initialize

        for i in range(0,l):
            self.append( NTdihedralOpt(
                                       self.atoms[0].coordinates[i],
                                       self.atoms[1].coordinates[i],
                                       self.atoms[2].coordinates[i],
                                       self.atoms[3].coordinates[i]
                                      )
                       )

        cav,cv,_n = self.cAverage(min=self.range[0],max=self.range[1])

        self.limit(self.range[0], self.range[1])
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

    LVdict = dict( CD1 = 'CD2', CD2 = 'CD1', QD1 = 'QD2', QD2 = 'QD1', MD1 = 'MD2', MD2 = 'MD1',
                   CG1 = 'CG2', CG2 = 'CG1', QG1 = 'QG2', QG2 = 'QG1', MG1 = 'MG2', MG2 = 'MG1'
                 )
    def __init__( self, resName, atomName, convention=INTERNAL, **kwds ):

        NTtree.__init__(self, name=atomName, __CLASS__='Atom', **kwds )

        self.setdefault( 'stereoAssigned', False )

        self.resonances  = NTlist()
        self.coordinates = NTlist()
        self.rogScore    = ROGscore()
        self[CHK_STR] = NTdict()

        self._topology = None #intially None; defined by the updateTopolgy call of the Molecule class

        # several external programs need an index
        global AtomIndex
        self.atomIndex = AtomIndex
        AtomIndex += 1

        db = database.NTdb.getAtomDefByName( resName, atomName, convention = convention )
        if db:
            self.name = db.translate(INTERNAL)
            self.db = db
        else:
            # see if we can add to the definition database
            patches = NTdict()

            patches.nameDict = {INTERNAL_0:atomName, INTERNAL_1:atomName, convention:atomName}

            if atomName[0:1] in ['H','Q', 'M']:
                patches.spinType = '1H'
            elif atomName[0:1] == 'N':
                patches.spinType = '15N'
            elif atomName[0:1] == 'C':
                patches.spinType = '13C'
            elif atomName[0:1] == 'P':
                patches.spinType = '31P'
            elif atomName[0:1] == 'S':
                patches.spinType = '32S'
            #end if

            rdef = database.NTdb.getResidueDefByName( resName, convention = convention )
            db = None
            if rdef and rdef.canBeModified:
                #print '****', rdef, atomName
#                NTdebug("Atom.__init__: adding non-standard '%s' to database %s", atomName, rdef)
                db=rdef.appendAtomDef( atomName, **patches )
            #end if
            #print '***', db
            if db:
                self.db = db
            else:
                self.db = AtomDef( atomName, **patches ) # TODO: check if absense of residue defs within here cause problems.
        #end if
    #end def

    def __str__( self ):
#        return self._Cname( 1 )
        return '<%s %s>' % ( self._className(), self._Cname(2) ) # Include chain id as well as residue id.
    #end def

    def format(self):
        return sprintf("""%s %s %s
resonances:  %s
coordinates: %s"""  , dots, self, dots
                    , self.resonances
                    , self.coordinates
                    )
        #end def

    def criticize(self):
#        NTdebug( '%s' % self )
        if not self.hasCoordinates():
#            NTdebug('Setting atom to max orange [crit.1] because it has no coordinates')
            self.rogScore.setMaxColor( COLOR_ORANGE, comment=ROGscore.ROG_COMMENT_NO_COOR)

    def toString(self, showChainId=True, showResidueType=True):
        res = self._parent
        if not res:
            NTerror("Failed to get parent residue for atom with name: %s" % self.name)
            return None

        if showChainId:
            chn = res._parent
            if chn == None:
                result = ' .'
            else:
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

    def hasCoordinates(self):
        """
        Returns True if atom has coordinates
        """
#        NTdebug("Checking atom.hasCoordinates for %s" % self)
        return len(self.coordinates) > 0
    #end def

    def hasMissingCoordinates(self):
        """
        Returns True if atom has less coordinates instances than would be expected from modelCount
        """
        if self.getModelCount() == None:
            return True

        if len(self.coordinates) < self.residue.chain.molecule.modelCount:
            return True
        else:
            return False
    #end def

    def getModelCount(self):
        """
        Returns the number of models derived from the top level object; molecule.
        This might be different from the length of self.coordinates in case the sync hasn't been done yet.
        """
#        return self.residue.chain.molecule.modelCount
        modelCount = getDeepByKeys(self, 'residue', 'chain', 'molecule', 'modelCount' )
#        if modelCount == None:
#            NTdebug("Failed to get modelCount for atom")
        return modelCount
    #end def

    def getMolecule(self):
        mol = self.getParent(level=3) # TODO : test.
#        if mol == None:
#            NTdebug("Failed to get molecule for atom")
#        return self.residue.chain.molecule
        return mol

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

    def getMinDistance(self, other):
        """
        Returns the minimum distance in the ensemble of models.
        Meant to be a fast quiet routine.
        Returns None if no atoms or coordinates are present.
        """
        result = self.distance(other)
        if result == None:
            return None
        (_av,_sd,minv,_maxv) = result
        return minv


    def calculateMeanCoordinate( self ):
        """
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
        """return list of Atom instances defining the topology. Returns None on error"""
        if self._topology != None:
            return self._topology
        #old style#
        return translateTopology( self._parent, self.db.topology )
    #end def

    def isAssigned( self ):
        """return true if atom current resonance has a valid assignment"""
        lastResonance = self.resonances()
        if lastResonance == None:
            return False
        return not isNaN(lastResonance.value)
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


    def setStereoAssigned( self, ssa = True ):
        """
        Return stereoAssigned flag to True or if ssa == False set it to False.
        """
        if not self.isProChiral():
            NTerror('Atom.setStereoAssigned: %s is not prochiral', self)
        self.stereoAssigned = ssa
    #end def


    def isStereoAssigned( self ):
        """
        Return True if stereoAssigned flag present and True.

        For non prochirals this property is not set.
        """
        if not self.isProChiral():
            return False
        return self.stereoAssigned
    #end def

    def isProChiral( self ):
        """
        Return True if atm is pro-chiral and thus can have stereo assignment
        Should be in in database
        """
        self.db.proChiralPartnerAtom = None
        if self.residue.db.name in ['LEU', 'VAL'] and self.db.name in self.LVdict:
            # patch database
            self.db.proChiralPartnerAtom = self.LVdict[ self.db.name ]
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

    def getSterospecificallyRelatedPartner( self ):
        """
        Return prochiral partner Atom instance of self or
        another Atom instance that is related by another stereospecific relation.
        E.g. Phe HD1 will return HD2,
             Asn HD1 too
             Arg QH1 will return QH2.
        should be in database; of course.
        """
        proChiralPartner = self.proChiralPartner()
        if proChiralPartner:
            return proChiralPartner

        pseudoAtom = self.pseudoAtom()
        if not pseudoAtom:
#            NTdebug("There is no pseudo defined for %s" % self)
            return None

        realAtomList = pseudoAtom.realAtoms()
        if len(realAtomList) > 2:
#            NTwarning("This routine wasn't meant to be used for atoms that are part of a group of more than 2; please improve code") # happens in AtT13Paris for I guess isopropyl groups or alike.
            return None
        if len(realAtomList) < 2:
#            NTdebug("This routine wasn't meant to be used when the pseudo atom has no (or not all) real atoms present.")
            return None

        if self == realAtomList[0]:
            return  realAtomList[1]
        return realAtomList[0]
    #end def

    def getPseudoOfPseudoAtom(self):
        """Return pseudo atom containing self or None"""

        res = self._parent
        resName = res.resName # use shorthand.
#        NTdebug(" my name %s, parent residue: %s" % ( self.name, res))

        if resName == 'LEU' and self.name.startswith('QD'):
            return res.QQD

        if resName == 'VAL' and self.name.startswith('QG'):
            return res.QQG

#        if resName == 'ARG' and self.name.startswith('QH'):
#            return res.QQH # Not present yet.

        if resName == 'PHE' or resName == 'TYR':
            if self.name == 'QD' or self.name == 'QE' :
                return res.QR

        return None

    def heavyAtom( self ):
        """
        For protons return heavyAtom of self,
        None otherwise
        """
        if not self.isProton():
            return None
        topology = self.topology()
        if topology == None:
            NTwarning("Failed to get topology for heavy atom routine: %s" % self)
            return None
        if len(topology) < 1:
            NTwarning("Failed to get any atom in topology for heavy atom routine: %s" % self)
            return None
        return self.topology()[0]
    #end def

    def isAromatic( self ):
        """Return true if it is an atom belonging to an aromatic ring
        """
        return database.isAromatic(self.db)
    #end def

    def isBackbone( self ):
        """
        Return True if it is a backbone atom.
        """
        return database.isBackbone(self.db)
    #end def

    def isTerminal( self ):
        """
        Return True for Amino acid H1, H2, H3 etc.
        """
        return database.isTerminal(self.db)
    #end def

    def isSidechain( self ):
        """
        Return True if it is a sidechain atom,
        """
        return database.isSidechain(self.db)
    #end def

    def isMethyl( self ):
        """
        Return True atm is a methyl (either carbon or proton)
        """
        return database.isMethyl(self.db)
    #end def

    def isMethylProton( self ):
        """
        Return True if atm is a methyl proton
        """
        return database.isMethylProton(self.db)
    #end def

    def isMethylene( self ):
        """
        Return True atm is a methylene (either carbon or proton)
        """
        return database.isMethylene(self.db)
    #end def

    def isMethyleneProton( self ):
        """
        Return True if atm is a methylene proton
        """
        return database.isMethyleneProton(self.db)
    #end def

    def isMethylProtonButNotPseudo( self ):
        """
        Return True if atm is a methyl proton but not a pseudo atom.
        """
        return database.isMethylProtonButNotPseudo(self.db)
    #end def

    def isIsopropylOrGuanidinium( self ):
        """Return True if atom is a Leu or Val isopropyl or Arg guanidinium pseudo"""
        return database.isIsopropylOrGuanidinium(self.db)
    #end def

    def isProton( self ):
        """Return Tue if atm is 1H
        """
        return database.isProton(self.db)
    #end def

    def isCarbon( self ):
        """Return Tue if atm is 13C
        """
        return database.isCarbon(self.db)
    #end def

    def isNitrogen( self ):
        """Return Tue if atm is 15N
        """
        return database.isNitrogen(self.db)
    #end def

    def isSulfur( self ):
        """Return Tue if atm is 32S
        """
        return database.isSulfur(self.db)
    #end def

    def isOxygen( self ):
        """Return Tue if atm is 16O
        """
        return database.isOxygen(self.db)
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
        Return a NTlist instance with self if it has properties.
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
        """Return True if atom is pseudoAtom"""
        return database.isPseudoAtom(self.db)
    #end def

    def hasPseudoAtom( self ):
        """Return True if atom has a correponding pseudoAtom"""
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

    def pseudoAtomList( self ):
        """Return list of pseudoAtom instance (if exist, or empty list otherwise)"""
        result = []

        if self.hasPseudoAtom():
            pseudoAtom = self.residue.getAtom( self.db.pseudo )
            result.append( pseudoAtom )
        # Add the complex pseudos:
#    DEFAULT_PSEUDO_ATOM_ID_TWO_NH2_OR_CH2        = 3
#    DEFAULT_PSEUDO_ATOM_ID_TWO_METHYL            = 4
#    DEFAULT_PSEUDO_ATOM_ID_AROMAT_2H             = 5
#    DEFAULT_PSEUDO_ATOM_ID_AROMAT_4H             = 6
            if pseudoAtom.hasPseudoAtom():
                pseudoAtom2 = self.residue.getAtom( pseudoAtom.db.pseudo )
                result.append( pseudoAtom2 )
        return result
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
    #end def

    def getRepresentativePseudoAtom( self, atomList ):
        """Return pseudo atom that represents all the atoms in the list and no more
        or None. Input sorting is unimportant.
        """
        inputLength = len(atomList)
        if inputLength <= 1:
#            NTwarning("Trying to getRepresentativePseudoAtom for atomList: %s" % atomList )
            return None

        pseudoAtom = self.pseudoAtom()
        if not pseudoAtom:
            return None
        realAtomList = pseudoAtom.realAtoms()
        realAtomListLength = len(realAtomList)
        if inputLength == 1:
            NTwarning("Found pseudo with single real atom [%s] (itself?) for atomList: %s" % (realAtomList[0], atomList ))
            return None

        # efficiency in my mind
        if inputLength != realAtomListLength:
#            NTdebug("Found unrepresentative pseudo [%s] for atomList: [%s] and realAtomListLength: [%s]" % (pseudoAtom, atomList, realAtomListLength ))
            return None

        for atom in atomList:
            if atom not in realAtomList:
#                NTdebug("Found atom [%s] in atomList: %s unrepresented by pseudo %s" % (atom, atomList, pseudoAtom))
                return None
        return pseudoAtom

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

    def atomToPDB( self, pdbIndex, model, convention = IUPAC ):
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
#            NTdebug("Trying to Atom.atomToPDB for model: " + `model`)
#            NTdebug("but only found coordinates length: " + `len(self.coordinates)`)
            return None
        if model < 0:
            NTcodeerror("In Atom.atomToPDB found model to be <0: " + `model`)
            return None
#        modelId = model - 1

        pdbAtmName = self.translate( convention )
        if not pdbAtmName:
            if self.name.startswith('Q'):
                return None
#            NTdebug("Failed to translate from CING to convention: %s atom: %-20s returning CING atom name" % (convention, self))
            pdbAtmName = self.name

        pdbResName = self.residue.translate( convention )
        if not pdbResName:
#            NTdebug("Failed to translate from CING to convention: %s residue: %-20s returning CING residue name" % ( convention, self.residue ))
            pdbResName = self.residue.name
#            return None

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

    JFD: why not skip this intermediate object and hang functionality straight off Atom and AtomsHTMLfile classes?
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


class AssignmentCountMap(NTdict):
    def __init__(self, *args, **kwds):
        d = {'1H': 0, '13C': 0, '15N': 0,  '31P':0} # sync these defs with RDB
        # skipping: O & S that are not observed in BMRB
        # Observed were F in bmr16409, & Cd in bmr4363. None in BMRB and PDB for these 2 nucleii so leave out of code for now.
#        '19F':0, '113Cd': 0
        NTdict.__init__(self, __CLASS__='AssignmentCountMap')
        self.update(d)
    def __str__(self):
        'Default is to have no zero elements. Using trick with different method name to prevent recursion.'
        return self.__repr__(showEmptyElements=0)
    def overallCount(self):
        r = sum([self[key] for key in self.keys()]) # numpy.int64 type because sum is from numpy.
        r = int(r)
#        NTdebug("type of overall count %s: %s" % ( r, r.__class__))
        return r
#end class

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
#        if res == None or not res.has_key( atomName ):
#            result.append( None )
#            continue
#        result.append( res[atomName] )
        # simplified:
        result.append( getDeepByKeysOrAttributes( res, atomName) )
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
        val = acos( 1.0 - (dCbCb*dCbCb - 8.555625) / 6.160 ) * 180.0/math.pi
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
        or None on error (eg when there were no coordinates.
    """
    mc = len(cys1.CA.coordinates) # model count
    if not mc: # see entry 1abt
        NTwarning("No coordinates for CA of residue: %s" % cys1)
        return None

    # For C alpha only models
    for cysResidue in [ cys1, cys2 ]:
        for atomName in [ 'CA', 'CB', 'SG' ]:
            atom = cysResidue[atomName]
            if not len(atom.coordinates):
                NTdebug("Skipping disulfideScore between %s and %s for there are no coordinates for atom: %s" % (cys1, cys2, atom))
                return None # The white space on this line was screwed up with Eclipse svn finding a diff. It has been in for over a year.

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
        NTerror("Truncating chainId [%s] to first char only" % chainId)
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

def getTripletHistogramList(resTypeListBySequenceOrder, doOnlyOverall = False, ssTypeRequested = None, doNormalize = False, normalizeSeparatelyToZ = False):
    """Returns a list of convoluted 1d by 1d -> 2d histo over 3 residues (a triplet) or
    an empty array when it could not be constructed.

    If doOnlyOverall it will be a list with a single element. If not then
    it will be a list of three elements one each for every sstype.

    If ssTypeRequested is None then all types will be returned otherwise just the
    type requested.

    If doNormalize = True then the 3 histograms for each ssType are normalized to have an integral of 100/3 % before they
    are added to have an integral of 100 %. The result will therefor be one histogram and not the usual 3. The value of ssTypeRequested will be
    checked to be None. It's a code bug if it differs.

    resTypeListBySequenceOrder is a list of three residue type names in sequence order.
    E.g. VAL171, PRO172, ILE173.

    If normalizeSeparatelyToZ then the 3 histograms will be individually scaled to a Z-score based of the overall histogram. This is pretty wild
    statistics.

    Return None on error.
        or empty array when it could not be constructed.
    """

    if not resTypeListBySequenceOrder:
        NTerror( 'getTripletHistogramList was given an empty sequence: %s' % str(resTypeListBySequenceOrder))
        return None

    if None in resTypeListBySequenceOrder:
#        NTerror( 'getTripletHistogramList has a None residue type in sequence: %s' % str(resTypeListBySequenceOrder))
        return None

    if doNormalize or normalizeSeparatelyToZ:
        if ssTypeRequested != None:
            NTerror( 'getTripletHistogramList was called with normalizing for specific ssType [%s] or with normalizeSeparately which is impossible.' % ssTypeRequested)
            return

    resTypePrev, resType, resTypeNext = resTypeListBySequenceOrder
    histListTuple = []
    if doOnlyOverall and not doNormalize:
        hist1 = getDeepByKeys(hPlot.histd1ByResTypes, resType, resTypePrev) # x-axis
    #        hist2 = getDeepByKeys(hPlot.histd1ByResTypes, resType, resTypeNext) # bug fixed on June 3rd, 2010
        hist2 = getDeepByKeys(hPlot.histd1ByResTypes, resTypeNext, resType)
        histListTuple.append((hist1,hist2))
    else:
        ssTypeList = hPlot.histd1BySs0AndResTypes.keys()
        ssTypeList.sort() # in place sort to: space, H, S
#        NTdebug("ssTypeList: %s" % ssTypeList)
        for ssType in ssTypeList:
            if ssTypeRequested and ssType != ssTypeRequested:
#                    NTdebug("Skipping ssType %s because only requested: %s" % (ssType, ssTypeRequested) )
                continue
#                NTdebug("Processing ssType: %s" % ssType)
            hist1 = getDeepByKeys(hPlot.histd1BySs0AndResTypes, ssType, resType, resTypePrev) # x-axis
            hist2 = getDeepByKeys(hPlot.histd1BySs1AndResTypes, ssType, resTypeNext, resType) # y-axis; this was a bug see convertD1D2_2Db2.py
            histListTuple.append((hist1,hist2))
        # end for
    # end if

    histList = []
    for histTuple in histListTuple:
        hist1, hist2 = histTuple
        if hist1 == None:
#                    NTdebug('skipping for hist1 is empty for [%s] [%s] [%s]' % (ssType, resTypePrev, resType))
            continue
        if hist2 == None:
#                    NTdebug('skipping for hist2 is empty for [%s] [%s] [%s]' % (ssType, resType, resTypeNext))
            continue
        m1 = mat(hist1,dtype='float')
        m2 = mat(hist2,dtype='float')
        m2 = m2.transpose()
        hist = multiply(m1,m2)
        histList.append(hist)


    if not doNormalize:
        return histList

    if len(histList) != 3:
        NTcodeerror("Expected 3 hist for resTypeListBySequenceOrder " + str(resTypeListBySequenceOrder))
        return None

    for hist in histList:
        histSum = sum(hist)
        factor = 3 * histSum / 100.0
        hist /= factor # normalize the new sum to be 33.
        histSumNew = sum(hist)
#            NTdebug("Normalized histogram with sum %10.3f by dividing by factor %10.3f to have 33.333 and found %10.3f" % (
#                histSum, factor, histSumNew))
        if math.fabs( 33.333 - histSumNew) > 0.1:
            NTcodeerror("Failed to normalize histogram with sum %10.3f by dividing by factor %10.3f to have 33.333 instead found %10.3f" % (
                histSum, factor, histSumNew))
            return None

    histOverall = histList[0] + histList[1] + histList[2]

    if not normalizeSeparatelyToZ:
        histList = [ histOverall ]
        return histList

    # NB this is now in percentage as they have been normalized.
    Ctuple = getEnsembleAverageAndSigmaFromHistogram( histOverall )
    (c_av, c_sd, hisMin, hisMax) = Ctuple
    zMin = (hisMin - c_av) / c_sd
    zMax = (hisMax - c_av) / c_sd

    NTmessage("       SS R1  R2  R3         c_av         c_sd       hisMin       hisMax         zMin         zMax")
    # A for all
    msg = '%s %s %s %s %12.3f %12.3f %12.3f %12.3f %12.3f %12.3f' % ('A', resTypePrev, resType, resTypeNext,
        c_av, c_sd, hisMin, hisMax, zMin, zMax)
    if hisMax < c_av:
        NTerror(msg + " maxHist < c_av")
    else:
        NTmessage("       " + msg)

#        histOverall *= 3.    # to get it's sum back to 100%
    histOverall -= c_av
    histOverall /= c_sd
    CtupleA = getArithmeticAverageAndSigmaFromHistogram(histOverall)
    (c_avA, c_sdA, hisMinA, hisMaxA) = CtupleA
    msg = '%s %s %s %s %12.3f %12.3f %12.3f %12.3f' % ('A', resTypePrev, resType, resTypeNext,
        c_avA, c_sdA, hisMinA, hisMaxA)
    if hisMaxA < c_avA:
        NTerror(msg + " maxHistA < c_avA")
    else:
        NTmessage("       " + msg)

    for i,hist in enumerate(histList):
        hist *= 3.    # to get it's sum back to 100%
        hist -= c_av
        hist /= c_sd
#            CtupleSS = getEnsembleAverageAndSigmaFromHistogram( hist )
        CtupleSS = getArithmeticAverageAndSigmaFromHistogram(hist)
#            NTdebug("CtupleSS: [%s]" % str(CtupleSS))
        (c_avSS, c_sdSS, hisMinSS, hisMaxSS) = CtupleSS
        mySsType = ssIdxToType(i)
        msg = '%s %s %s %s %12.3f %12.3f %12.3f %12.3f' % (mySsType, resTypePrev, resType, resTypeNext,
            c_avSS, c_sdSS, hisMinSS, hisMaxSS)
        if hisMaxSS < c_avSS:
            NTerror(msg + " maxHistSS < c_avSS")
        else:
            NTmessage("       " + msg)
    return histList
# end def

def residueNumberDifference(res1, res2):
    "Returns res2.resNum - res1.resNum. Ignoring gaps in sequence."
    if res1._parent != res2._parent:
#        NTdebug("In Chain.residueCountDifference residues aren't in same chain so result is pointless; returning None")
        return None
    return res2.resNum - res1.resNum
# end def

