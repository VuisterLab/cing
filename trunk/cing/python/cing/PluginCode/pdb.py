"""
Adds initialize/import/export from/to PDB files


Methods:
    Molecule.importFromPDB( pdbFile, convention='PDB')   :
        Import coordinates from pdbFile
        convention eq PDB, CYANA, CYANA2 or XPLOR
        return molecule or None on error

    Molecule.PDB2Molecule(pdbFile, moleculeName, convention, nmodels)   :
        Initialize  from pdbFile
        Return molecule instance
        convention eq PDB, CYANA, CYANA2 or XPLOR
        staticmethod

    Project.initPDB( pdbFile, convention ):
        initialize from pdbFile, import coordinates
        convention = PDB, CYANA, CYANA2 or XPLOR

    Project.importPDB( pdbFile, convention ):
        import coordinates from pdbFile
        convention = PDB, CYANA, CYANA2 or XPLOR

    Project.export2PDB( pdbFile ):
        export to pdbFile

"""
from cing.Libs import PyMMLib
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTdetail
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTpath
from cing.Libs.NTutils import NTtree
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import sprintf
from cing.core.constants import CYANA
from cing.core.constants import CYANA2
from cing.core.constants import CYANA_NON_RESIDUES
from cing.core.constants import INTERNAL
from cing.core.constants import IUPAC
from cing.core.database import NTdb
from cing.core.molecule import Chain
from cing.core.molecule import Molecule
from cing.core.molecule import ensureValidChainId
import os

#==============================================================================
# PDB stuff
#==============================================================================
def importFromPDB( molecule, pdbFile, convention=IUPAC, nmodels=None)   :
    """Import coordinates from pdbFile (optionally: first nmodels)
       convention eq PDB, CYANA, CYANA2, XPLOR, IUPAC

       return molecule or None on error
    """
    if not molecule: return None

#    NTdetail('==> Parsing pdbFile "%s" ... ', pdbFile )
#    if not os.path.exists(pdbFile):
#        NTerror('importFromPDB: missing PDB-file "%s"', pdbFile)
#
#    pdb = PyMMLib.PDBFile( pdbFile)
#
##    atomDict = molecule._getAtomDict(convention)
#
#    foundModel = False
#    modelCount = 0
#    for record in pdb:
#        recordName = record._name.strip()
#        if  recordName == 'REMARK':
#            continue
#        if recordName == "MODEL":
#            foundModel = True
#            continue
#        if recordName == "ENDMDL":
#            modelCount += 1
#            if nmodels and modelCount >= nmodels:
#                break
#            continue
#        if recordName == "ATOM" or recordName == "HETATM":
#            # see if we can find a definition for this residue, atom name in the database
#            if convention == CYANA:
#                # the residue names are in Cyana1.x convention (i.e. for GLU-)
#                # atm names of the Cyana1.x PDB files are in messed-up Cyana format
#                atmName = record.name[1:4] + record.name[0:1]
#            elif convention == CYANA2:
#                # the residue names are in Cyana2.x convention (i.e. for GLU)
#                # atm names of the Cyana2.x PDB files are in messed-up Cyana format
#                atmName = record.name[1:4] + record.name[0:1]
#            else:
#                atmName = record.name
#            # Not all PDB files have chainID's !@%^&*
#            # Actually, they do. It might be an space character though.
#            # It's important to save it as is otherwise the residue number
#            # is no longer a unique key within the chain. E.g. HOH in 1n62
#            # has a space character for the chain id and similar residue
#            # numbering as the protein sequence in chain A.
#            chainId = Chain.defaultChainId
#            if record.has_key('chainID'):
#                chainId = record.chainID.strip()
#                chainId = ensureValidChainId(chainId)
##                print '>chain>', '>'+chainId+'<', len(chainId)
#            #end if
#            resID = record.resSeq
##            if chainId == Chain.defaultChainId:
##                # use the atomDict
##                t = (resID, atmName)
##                if atomDict.has_key(t):
##                    atom = atomDict[t]
##                else:
##                    atom = None
##            else:
#            atom  = molecule.decodeNameTuple( (convention, chainId, resID, atmName) )
#
#            if not atom:
#                NTerror('cing.PluginCode.pdb#importFromPDB: %s, model %d incompatible record (%s)',
#                         convention, modelCount, record )
#                #print '>>', convention, cname, resID, atmName
#                continue
#            atom.addCoordinate( record.x, record.y, record.z, Bfac=record.tempFactor )
#        #end if
#    #end for
#
#    # Patch to get modelCount right for X-ray or XPLOR structures with only one model
#    if not foundModel:
#        modelCount += 1
#
#    molecule.modelCount += modelCount
#
#    NTdetail( 'importFromPDB: read %d records; added %d structure models', len(pdb), modelCount )
#    #end if
#
#    del( pdb )
    parser = pdbParser( pdbFile, convention=convention )
    if not parser:
        return None
    parser.map2molecule( molecule )
    parser.importCoordinates( nmodels = nmodels )
    return molecule
#end def
# Add as a method to Molecule class
Molecule.importFromPDB = importFromPDB

class pdbParser:
    """
    Class to parse the pdb file and import into molecule instance
    Should handle all nitty/gritty details such as HIS/ARG/LYS/GLU/ASP/(R)Ade/(R)Cyt/(R)Gua and Cyana1.x related issues

    Steps:
    - Parse the pdbFile into records using PyMMlib.
    - Assemble a tree from chn's,res's,atm's, map records back to atm entries (_records2tree).
    - Map res's and atm's to CING db. Convert the idiocraties in the process. (_matchResidue2Cing and _matchAtom2Cing)
    - Optionally: generate a molecule from chn,res's
    - Map atm's to atoms of molecule.
    - Import the coordinates.

                             atom<->residue->chain<->molecule<-self
                              |
    self->tree<->chn<->res<->atm<-record<-self
                       |      |
               ResidueDef<->AtomDef

    """
    def __init__(self, pdbFile, convention=IUPAC, patchAtomNames = False, skipWaters=False ):
        if not os.path.exists(pdbFile):
            NTerror('pdbParser: missing PDB-file "%s"', pdbFile)
            return None

        NTdetail('==> Parsing pdbFile "%s" ... ', pdbFile )

        self.pdbRecords = PyMMLib.PDBFile( pdbFile )
        if not self.pdbRecords:
            NTerror('pdbParser: parsing PDB-file "%s"', pdbFile)
            return None
        #end if
        self.pdbFile = pdbFile
        self.convention = convention
        self.patchAtomNames = patchAtomNames
        self.skipWaters = skipWaters

        # parsing storage
        self._records2tree()
        self._matchResiduesAndAtoms()
        self.molecule = None
    #end def

    def _records2tree(self):
        """Convert the pdbRecords in a tree-structure.
        """
        self.tree = NTtree('tree') # Tree like structure of pdbFile
        chn  = None
        res  = None
        atm  = None
        self.modelCount = 0
        atomDict  = {}

        atmCount = 0
        foundModel = False
        for record in self.pdbRecords:
            recordName = record._name.strip()
            if recordName == "MODEL":
                foundModel = True
                continue
            if recordName == "ENDMDL":
                self.modelCount += 1

            if recordName == "ATOM" or recordName == "HETATM":

                # Not all PDB files have chainID's !@%^&*
                # They do; if none returned then take the space that is always present!
                chainId = Chain.defaultChainId
                if record.has_key('chainID'):
                    chainId = record.chainID.strip()
                    chainId = ensureValidChainId(chainId)
                #end if

                resName  = record.resName.strip()
                resNum   = record.resSeq
                fullResName = resName+str(resNum)

                atmName = record.name.strip()

                t= (chainId, fullResName, atmName)

                if atomDict.has_key( t ):
                    atm = atomDict[t]
                else:

                    if not self.tree.has_key(chainId):
                        chn = self.tree.addChild(name=chainId)
                    else:
                        chn = self.tree[chainId]
                    #end if
                    if not chn:
                        NTdebug('pdbParser._records2tree: strange, we should not have a None for chain; record %s', record)
                        continue
                    #end if

                    if not chn.has_key(fullResName):
                        res = chn.addChild(name=fullResName, resName=resName, resNum=resNum)
                    else:
                        res = chn[fullResName]
                    #end if
                    if not res:
                        NTdebug('pdbParser._records2tree: strange, we should not have a None for residue; record %s', record)
                        continue
                    #end if

                    if not res.has_key(atmName):
                        atm = res.addChild(atmName)
                    else:
                        atm = res[atmName]
                    #end if
                    if not atm:
                        NTdebug('pdbParser._records2tree: strange, we should not have a None for atom; record %s', record)
                        continue
                    #end if
                    atomDict[t] = atm
                    #print chn, res,atm
                #end if

                # Make a reference to the tree
                record.atm = atm
                atmCount += 1
            #end if
        #end for
        if not foundModel: # X-rays do not have MODEL record
            self.modelCount = 1

        NTdebug( 'end pdbParser._records2tree: parsed %d pdb records, %d models',  atmCount, self.modelCount)
    #end def

    def _matchResidue2Cing(self, res):
        """
        Match res to CING database using previously defined convention;
        Account for 'ill-defined' residues by examining crucial atom names.
        Use CYANA (==DIANA) Naming for conversion to INTERNAL (i.e. These names will not likely change)

        Return NTdb resDef object None on Error

        """
        res.db = None
        res.skip = False

        # Residue names that are ambigiously defined by different PDB file formats
        if res.resName[0:3] == 'ARG':
            if 'HH1' in res:
                res.db = NTdb.getResidueDefByName( 'ARG', convention = CYANA )
            elif '1HH' in res: # Second set for CYANA 1.x, AMBER
                res.db = NTdb.getResidueDefByName( 'ARG', convention = CYANA )
            else:
                # Default protonated; this also assures most common for X-ray without protons
                res.db = NTdb.getResidueDefByName( 'ARG+', convention = CYANA )
            #end if
        #end if
        elif res.resName[0:3] == 'ASP':
            if 'HD2' in res:
                #print 'ASPH'
                res.db = NTdb.getResidueDefByName( 'ASP', convention = CYANA )
            else:
                # Default deprot; this also assures most common for X-ray without protons
                #print 'ASP'
                res.db = NTdb.getResidueDefByName( 'ASP-', convention = CYANA )
            #end if
        elif res.resName[0:3] == 'GLU':
            if 'HE2' in res:
                #print 'GLUH'
                res.db = NTdb.getResidueDefByName( 'GLU', convention = CYANA )
            else:
                # Default deprot; this also assures most common for X-ray without protons
                #print 'GLU'
                res.db = NTdb.getResidueDefByName( 'GLU-', convention = CYANA )
            #end if
        elif res.resName[0:3] == 'HIS':
            if 'HD1' in res and 'HE2' in res:
                #print 'HISH'
                res.db = NTdb.getResidueDefByName( 'HIS+', convention = CYANA )
            elif not 'HD1' in res and 'HE2' in res:
                # print HISE
                res.db = NTdb.getResidueDefByName( 'HIST', convention = CYANA )
            else:
                # Default HD1
                #print 'HIS'
                res.db = NTdb.getResidueDefByName( 'HIS', convention = CYANA )
            #end if
        elif res.resName[0:3] == 'LYS':
            if ('HZ1' in res and not 'HZ3' in res):
                res.db = NTdb.getResidueDefByName( 'LYS', convention = CYANA )
            elif ('1HZ' in res and not '3HZ' in res): # Second set for CYANA 1.x
                res.db = NTdb.getResidueDefByName( 'LYS', convention = CYANA )
            else:
                # Default prot; this also assures most common for X-ray without protons
                res.db = NTdb.getResidueDefByName( 'LYS+', convention = CYANA )
            #end if
        elif res.resName in CYANA_NON_RESIDUES:
            res.skip = True
        elif res.resName == 'HOH' and self.skipWaters:
            res.skip = True
        else:
            res.db = NTdb.getResidueDefByName( res.resName, convention = self.convention )
        #end if
        return res.db
    #end def

    def _matchAtom2Cing(self, atm):
        """
        Match atm.name to CING database using previously defined convention;
        Account for 'ill-defined' atoms, such as CYANA definitions in PDB file

        If self.patchAtomNames=True (defined on __init__), several patches are tried (NOT advised to use).

        Return NTdb AtomDef object or None on Error

        """
        if not atm:
            NTerror('pdbParser._matchAtom: undefined atom')
            return None
        #end if

        atm.db   = None
        atm.skip = False
        res   = atm._parent

        if not res:
            NTerror('pdbParser._matchAtom: undefined parent residue, atom %s, convention %s, not matched',
                    atm.name, self.convention
                   )
            return None
        #end if
        #print '>',atm,res

        if res.skip:
            atm.skip = True
            return atm
        #end if

        if not res.db:
            return None
        #end if

        # Now try to match the name of the atom
        if self.convention == CYANA or self.convention == CYANA2:
            # the residue names are in Cyana1.x convention (i.e. for GLU-)
            # atm names of the Cyana1.x PDB files are in messed-up Cyana format
            # So: 1HD2 becomes HD21 where needed:
            aName = moveFirstDigitToEnd(atm.name)
        else:
            aName = atm.name
        #end if

        # For the atom name conversion step, we use the res.db object. This points to the proper ResidueDef that we just
        # mapped in the _matchResidue2Cing routine.
        atm.db = res.db.getAtomDefByName( aName, convention = self.convention )

        # JFD adds hacks these debilitating simple variations if nothing is found so far
        # GWV does not like this at all and therefore hides it behind an option
        if self.patchAtomNames and not atm.db:
            NTdebug('pdbParser._matchAtom: patching atom %s, residue %s %s, convention %s',
                       atm.name, res.resName, res.resNum, self.convention
                     )
            if not atm.db: # some besides CYANA have this too; just too easy to hack here
                aName = moveFirstDigitToEnd(atm.name)
                atm.db = res.db.getAtomDefByName( aName, convention = self.convention )
            #end if

            if not atm.db:
                if atm.name == 'H': # happens for 1y4o_1model reading as cyana but in cyana we have hn for INTERNAL_0
                    aName = 'HN'
                elif atm.name == 'HN': # for future examples.
                    aName = 'H'
                atm.db = res.db.getAtomDefByName( aName, convention = self.convention )
            #end if
        #end if

        return atm.db
    #end def

    def _matchResiduesAndAtoms(self):
        """
        Match residues and Atoms in the tree to CING db using self.convention
        """
        for res in self.tree.subNodes(depth=2):
            self._matchResidue2Cing( res )
            for atm in res:
                self._matchAtom2Cing( atm )
                if not atm.skip and atm.db == None:
                    NTwarning('pdbParser._matchResiduesAndAtoms: atom %s, residue %s %s, convention %s, not matched to CING',
                               atm.name, res.resName, res.resNum, self.convention
                             )
                    atm.skip = True
            #end for
        #end for
    #end def

    def initMolecule(self, moleculeName):
        """Initialize new Molecule instance from the tree.
        Return Molecule on None on error.
        """
        mol = Molecule( name = moleculeName )

        # The self.tree contains a tree-like representation of the pdb-records
        for ch in self.tree:
            chain = mol.addChain( name = ch.name )
            for res in ch:
                #print '>', ch, res, res.skip, res.db
                if not res.skip and res.db!=None:
                    residue = chain.addResidue( res.db.name, res.resNum )
                    residue.addAllAtoms()
                #end if
            #end for
        #end for
        NTdebug('pdbParser.initMolecule: %s', mol)
        self.map2molecule( mol )
        return mol
    #end for

    def map2molecule(self, molecule):
        """
        Map the pdb records of self to molecule instance.
        """
        for chn in self.tree:
            for res in chn:
                for atm in res:
                    atm.atom = None
                    if not atm.skip and atm.db != None:
                        t = (INTERNAL, chn.name, res.resNum, atm.db.name)
                        atm.atom = molecule.decodeNameTuple(t)
                        if not atm.atom:
                            NTerror('pdbParser.map2molecule: Strange! error mapping atom (%s, %s, %s, %s) to %s; This should not happen!',
                                     chn.name, res.db.name, res.resNum, atm.name, molecule
                                   )
                        #end if
                    #end if
                #end for
            #end for
        #end for
        self.molecule = molecule
    #end def

    def importCoordinates( self, nmodels=None, update=True ):
        """
        Import coordinates into self.molecule.
        Optionally use only first nmodels.
        Optionally do not update dihedrals, mean-coordiates, .. (Be careful; only intended for conversion
        purposes).

        Return True on error
        """

        if not self.molecule:
            NTerror('pdbParser.importCoordinates: undefined molecule')
            return True
        #end if

        if nmodels==None:
            nmodels = self.modelCount # import all models found in pdfFile
        #end if

        if nmodels > self.modelCount:
            NTerror('pdbParser.importCoordinates: requesting %d models; only %d present', nmodels, self.modelCount)
            return True
        #end if

        model = self.molecule.modelCount # set current model from models already present
        foundModel = False
        for record in self.pdbRecords:
            recordName = record._name.strip()
            if recordName == "MODEL":
                foundModel = True
                NTdebug('pdbParser.importCoordinates: importing as MODEL %d', model)
                continue

            elif recordName == "ENDMDL":
                model += 1
                if model == self.molecule.modelCount + nmodels:
                    break

            elif recordName == "ATOM" or recordName == "HETATM":
                if not record.atm.skip and record.atm.atom != None:
                    atom = record.atm.atom
                    # Check if the coordinate already exists for this model
                    # This might happen when alternate locations are being
                    # specified. Simplify to one coordinate per model.
                    if len(atom.coordinates) <= model:
                        atom.addCoordinate( record.x, record.y, record.z, Bfac=record.tempFactor, occupancy=record.occupancy )
                    else:
                        NTdebug('pdbParser.importCoordinates: Skipping duplicate coordinate within same record (%s)' % record)
                #end if
            #end if
        #end for
        if not foundModel: # X-rays do not have MODEL record
            self.molecule.modelCount += 1
        else:
            self.molecule.modelCount = model

        if update:
            self.molecule.updateAll()

        NTdebug('pdbParser.importCoordinates: %s', self.molecule)
        return False
    #end def
#end class

def PDB2Molecule( pdbFile, moleculeName, convention=IUPAC, nmodels=None)   :
    """Initialize  Molecule 'moleculeName' from pdbFile
       convention eq PDB, CYANA, CYANA2 or XPLOR, IUPAC
       optionally only include nmodels

       Return molecule instance or None on error
    """
#    showMaxNumberOfWarnings = 100 # was 100
#    shownWarnings = 0
#
#    if not os.path.exists(pdbFile):
#        NTerror('PDB2Molecule: missing PDB-file "%s"', pdbFile)
#        return None
#
#    NTdetail('==> Parsing pdbFile "%s" ... ', pdbFile )
#
#    pdb = PyMMLib.PDBFile( pdbFile )
#    mol = Molecule( name=moleculeName )
#
##    mol.pdb = pdb
#    mol.modelCount  = 0
#    foundModel = False
#
#    for record in pdb:
#        recordName = record._name.strip()
#        if  recordName == 'REMARK':
#            continue # JFD: this used to be a pass but that's weird.
#
#        if recordName == "MODEL":
#            foundModel = True
#            continue
#        if recordName == "ENDMDL":
#            mol.modelCount += 1
#            if nmodels and (mol.modelCount >= nmodels):
#                break
#            continue
#
#        if recordName == "ATOM" or recordName == "HETATM":
#            # Skip records with a
#            # see if we can find a definition for this residue, atom name in the database
#            a = record.name
#            a = a.strip() # this improved reading 1y4o
#            if convention == CYANA or convention == CYANA2:
#                # the residue names are in Cyana1.x convention (i.e. for GLU-)
#                # atm names of the Cyana1.x PDB files are in messed-up Cyana format
#                # So: 1HD2 becomes HD21 where needed:
#                a = moveFirstDigitToEnd(a)
#            # strip is already done in function
#            atm = NTdbGetAtom( record.resName, a, convention )
#
#
#            # JFD adds to just hack these debilitating simple variations.
#            if not atm: # some besides cyana have this too; just too easy to hack here
##                print "Atom ["+a+"] was mismatched at first"
#                a = moveFirstDigitToEnd(a)
#                atm = NTdbGetAtom( record.resName, a, convention )
#            if not atm:
#                if a == 'H': # happens for 1y4o_1model reading as cyana but in cyana we have hn for INTERNAL_0
#                    a = 'HN'
#                elif a == 'HN': # for future examples.
#                    a = 'H'
#                atm = NTdbGetAtom( record.resName, a, convention )
#            if not atm:
#                if shownWarnings <= showMaxNumberOfWarnings:
#                    NTwarning('PDB2Molecule: %s format, model %d incompatible record (%s)' % (
#                             convention, mol.modelCount+1, record))
#                    if shownWarnings == showMaxNumberOfWarnings:
#                        NTwarning('And so on.')
#                    shownWarnings += 1
#                continue
#            if atm.residueDef.hasProperties('cyanaPseudoResidue'):
#                # skip CYANA pseudo residues
#                continue
#
#            # we did find a match in the database
#            # Not all PDB files have chainID's !@%^&*
#            # They do; if none returned then take the space that is always present!
#            chainId = Chain.defaultChainId
#            if record.has_key('chainID'):
#                chainId = record.chainID.strip()
#                chainId = ensureValidChainId(chainId)
#
#            resID    = record.resSeq
#            resName  = atm.residueDef.name
#            fullName = resName+str(resID)
#            atmName  = atm.name
#
#            # check if this chain,fullName,atmName already exists in the molecule
#            # if not, add chain or residue
#            if not chainId in mol:
#                mol.addChain( chainId )
#            #end if
#
#            if not fullName in mol[chainId]:
#                res = mol[chainId].addResidue( resName, resID )
#                res.addAllAtoms()
#            #end if
#
#            atom = mol[chainId][fullName][atmName]
#
#            # Check if the coordinate already exists for this model
#            # This might happen when alternate locations are being
#            # specified. Simplify to one coordinate per model.
#            numCoorinates = len(atom.coordinates)
#            numModels     = mol.modelCount + 1 # current model counts already
#            if numCoorinates < numModels:
#                atom.addCoordinate( record.x, record.y, record.z, Bfac=record.tempFactor )
#            else:
#                NTwarning('Skipping duplicate coordinate within same record (%s)' % record)
#        #end if
#    #end for
#    if shownWarnings:
#        NTwarning('Total number of warnings: ' + `shownWarnings`)
#
#    # Patch to get modelCount right for X-ray structures with only one model
#    if not foundModel:
#        mol.modelCount += 1
#    NTdetail( '==> PDB2Molecule: new Molecule %s from %s', mol, pdbFile )
#    # delete the PyMMlib pdbFile instance # JFD: why?
#    del(pdb)
    parser = pdbParser( pdbFile, convention=convention )
    if not parser:
        return None
    mol = parser.initMolecule( moleculeName )
    if not mol:
        return None
    parser.importCoordinates( nmodels = nmodels )
    return mol
#end def
# Add as a staticmethod to Molecule class
Molecule.PDB2Molecule = staticmethod( PDB2Molecule )


def moleculeToPDBfile( molecule, path, model=None, convention=IUPAC, max_models=None):
    """
    Save a molecule instance to PDB file.
    Convention eq PDB, CYANA, CYANA2, XPLOR.

    For speedup reasons, this routine should be explicitly coded.
    This routine should eventually replace toPDB.

    NB model should be ZERO for the first model. Not one.
    Returns True on error.
    """
    NTdebug('MoleculeToPDBfile: %s, path=%s, model=%s, convention=%s',
             molecule, path, model, convention)
    pdbFile = molecule.toPDB( model=model, convention = convention, max_models=None )
    if not pdbFile:
        return True
    pdbFile.save( path)
    del(pdbFile)
#end def
Molecule.toPDBfile = moleculeToPDBfile

def moveFirstDigitToEnd(a):
    if a[0:1].isdigit():
        a = a[1:] + a[0:1]
    return a

def initPDB( project, pdbFile, convention = IUPAC, name=None, nmodels=None, update=True ):
    """Initialize Molecule from pdbFile.
       convention eq. CYANA, CYANA2, XPLOR, IUPAC

       Optionally include only nmodels.
       Optionally do not update dihedrals, mean-coordiates, .. (Be careful; only intended for conversion
       purposes).

       returns molecule instance or None on error
    """
    if not os.path.exists(pdbFile):
        NTerror('Project.initPDB: missing PDB-file "%s"', pdbFile)

    NTmessage('==> initializing from PDB file "%s"', pdbFile)

    if not name:
        _path,name,_ext  = NTpath( pdbFile )
#    molecule = PDB2Molecule( pdbFile, name, convention = convention, nmodels=nmodels)
    parser = pdbParser( pdbFile, convention=convention )
    if not parser:
        return None
    molecule = parser.initMolecule( name )
    if not molecule:
        return None
    if not molecule:
        NTerror('Project.initPDB: failed parsing PDB-file "%s"', pdbFile)
        return None
    parser.importCoordinates( nmodels = nmodels, update=update )
    project.appendMolecule( molecule )
#    if update:
#        project.molecule.updateAll()
    #end if
    project.addHistory( sprintf('New molecule from PDB-file "%s"', pdbFile ) )
    project.updateProject()
    return molecule
#end def


def importPDB( project, pdbFile, convention = IUPAC, nmodels=None ):
    """Import coordinates from pdbFile
        return pdbFile or None on error
    """
    if not project.molecule:
        NTerror("importPDB: no molecule defined")
        return None
    if not importFromPDB( project.molecule, pdbFile, convention, nmodels=nmodels):
        return None

    project.addHistory( sprintf('importPDB from "%s"', pdbFile ) )
    project.updateProject()
    NTmessage( '%s', project.molecule.format() )
    #end if
    return pdbFile
#end def

def export2PDB( project, tmp=None ):
    """Export coordinates to pdb file
    """
    for mol in project.molecules:
        if mol.modelCount > 0:
            fname = project.path( project.directories.PDB, mol.name + '.pdb' )
            NTdetail('==> Exporting to PDB file "%s"', fname)
            pdbFile = mol.toPDB( convention = IUPAC)
            pdbFile.save( fname)
            del( pdbFile )
        #end if
    #end for
#end def

# register the functions
methods  = [(initPDB, None),
            (importPDB, None)
           ]
#saves    = []
#restores = []
exports  = [(export2PDB, None)
           ]
