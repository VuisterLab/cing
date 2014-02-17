"""
Adds initialize/import/export from/to PDB files


Methods:
    Molecule.importFromPDB( pdbFile, convention='PDB')   :
        Import coordinates from pdbFile
        convention eq PDB, CYANA, CYANA2 or XPLOR
        return molecule or None on error

    Project.initPDB( pdbFile, convention ):
        initialize from pdbFile, import coordinates
        convention = PDB, CYANA, CYANA2 or XPLOR

    Project.importPDB( pdbFile, convention ):
        import coordinates from pdbFile
        convention = PDB, CYANA, CYANA2 or XPLOR

    Project.export2PDB( pdbFile ):
        export to pdbFile

Speed check: 103.609s for pdbParser.importCoordinates: <Molecule "pdb2k0e" (C:1,R:152,A:2647,M:160)>
"""
from cing.Libs import PyMMLib
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.constants import * #@UnusedWildImport
from cing.core.database import NTdb
from cing.core.molecule import Molecule
from cing.core.molecule import getNextAvailableChainId
from cing.core.molecule import isValidChainId
from cing.core.molecule import unmatchedAtomByResDictToString

defaultPrintChainCode = '.'

#==============================================================================
# PDB stuff
#==============================================================================
def importFromPDB(molecule, pdbFile, convention = IUPAC, nmodels = None, allowNonStandardResidue = True, verbosity = None):
    """Import coordinates from pdbFile (optionally: first nmodels)
       convention e.g. PDB, CYANA, CYANA2, XPLOR, IUPAC

       return molecule or None on error
    """
    if not molecule:
        return None
    savedVerbosity = cing.verbosity
    if verbosity != None:
#        print 'cing.verbosity = %s' % verbosity
        cing.verbosity = verbosity
    parser = pdbParser(pdbFile, convention = convention)
    if not parser:
        return None
    parser.map2molecule(molecule)
    parser.importCoordinates(nmodels = nmodels)
    cing.verbosity = savedVerbosity
    return molecule
#end def
# Add as a method to Molecule class
Molecule.importFromPDB = importFromPDB


# pylint: disable=C0103
class pdbParser:
    """
    Class to parse the pdb file and import into molecule instance
    Should handle all nitty gritty (sorry for the discriminatory derogative) details such as
    HIS/ARG/LYS/GLU/ASP/(R)Ade/(R)Cyt/(R)Gua and Cyana1.x related issues

    Steps:
    - Parse the pdbFile into records using PyMMlib.
    - Assemble a tree from chn's,res's,atm's, map records back to atm entries (_records2tree).
    - Map res's and atm's to CING db. Convert the idiocracies in the process. (_matchResidue2Cing and _matchAtom2Cing)
    - Optionally: generate a molecule from chn,res's
    - Map atm's to atoms of molecule.
    - Import the coordinates.

    The allowNonStandardResidue determines if the non-standard residues and atoms are read. If so they will be shown as
    a regular message. Otherwise they will be shown as a warning. Just like MolMol does; the unknown atoms per residue.
    See the image at: http://code.google.com/p/cing/issues/detail?id=126#c4

                             atom<->residue->chain<->molecule<-self
                              |
    self->tree<->chn<->res<->atm<-record<-self
                       |      |
               ResidueDef<->AtomDef

    """
    def __init__(self, pdbFile, convention = IUPAC, patchAtomNames = True, skipWaters = False, allowNonStandardResidue = True):

        self.pdbFile = pdbFile
        self.convention = convention
        self.patchAtomNames = patchAtomNames
        self.skipWaters = skipWaters
        self.allowNonStandardResidue = allowNonStandardResidue
        self.matchGame = MatchGame(convention=convention, patchAtomNames = patchAtomNames,
                                   skipWaters = skipWaters, allowNonStandardResidue = allowNonStandardResidue)

        if not os.path.exists(pdbFile):
            nTerror('pdbParser: missing PDB-file "%s"', pdbFile)
            return None

        nTmessage('==> Parsing pdbFile "%s" ... ', pdbFile)

        self.pdbRecords = PyMMLib.PDBFile(pdbFile)
        if not self.pdbRecords:
            nTerror('pdbParser: parsing PDB-file "%s"', pdbFile)
            return None
        #end if

        # parsing storage
        self._records2tree()
        self._matchResiduesAndAtoms()
        self.molecule = None
    #end def

    def _records2tree(self):
        """Convert the pdbRecords in a tree-structure. Really a HoHoH; Hash of...
        """
#        nTdebug("Now in _records2tree")
        self.tree = NTtree('tree') # Tree like structure of pdbFile
        chn = None
        res = None
        atm = None
        self.modelCount = 0
        atomDict = {}

        mapChainId = {} # Keep track of mappings between input and CING when they're not the same.
        chainIdListAlreadyUsed = [] # simpler list.

#        atmCount = 0
        foundModel = False
        for _i,record in enumerate(self.pdbRecords):
#            if i >= 459:
#                nTdebug("Working on record: %s" % record)
            recordName = record._name.strip()
            if recordName == "MODEL":
                foundModel = True
                continue
            if recordName == "ENDMDL":
                self.modelCount += 1

            if recordName == "ATOM" or recordName == "HETATM":

                # Not all PDB files have chainID's !@%^&*
                # They do; if none returned then take the space that is always present!
                # JFD adds: take a look at 1ai0
                #    It features chain ids A thru F but also several residues with a ' ' for the chain id.
                #    Luckily the residues all have non-overlapping numbers. So let's program against
                #    this study case. Might have to be optimized.
                chainId = ' '
                if record.has_key('segID'): # Priority is given to chainID because xplor-nih doesn't write chain id in Refine setup.
                    chainId = record.segID.strip()
                if record.has_key('chainID'):
                    chainId = record.chainID
                if mapChainId.has_key(chainId):
                    chainId = mapChainId[chainId]
                if not isValidChainId(chainId):
                    chainIdNew = getNextAvailableChainId(chainIdListAlreadyUsed = chainIdListAlreadyUsed)
                    mapChainId[chainId] = chainIdNew
                    chainId = chainIdNew

                resName = record.resName.strip()
                resNum = record.resSeq
                fullResName = resName + str(resNum)

                atmName = record.name.strip()

                t = (chainId, fullResName, atmName)

                if atomDict.has_key(t):
                    atm = atomDict[t]
                else:

                    if not self.tree.has_key(chainId):
                        chn = self.tree.addChild(name = chainId)
                        if chainId in chainIdListAlreadyUsed:
                            nTcodeerror("list out of sync in _records2tree")
                        else:
                            chainIdListAlreadyUsed.append(chainId) # simpler object for getNextAvailableChainId
                    else:
                        chn = self.tree[chainId]
                    #end if
                    if not chn:
                        nTwarning('pdbParser._records2tree: strange, we should not have a None for chain; record %s', record)
                        continue
                    #end if

                    if not chn.has_key(fullResName):
                        res = chn.addChild(name = fullResName, resName = resName, resNum = resNum)
                    else:
                        res = chn[fullResName]
                    #end if
                    if not res:
                        nTwarning('pdbParser._records2tree: strange, we should not have a None for residue; record %s', record)
                        continue
                    #end if

                    if not res.has_key(atmName):
                        atm = res.addChild(atmName)
                    else:
                        atm = res[atmName]
                    #end if
                    if not atm:
                        nTwarning('pdbParser._records2tree: strange, we should not have a None for atom; record %s', record)
                        continue
                    #end if
                    atomDict[t] = atm
#                    print chn, res,atm
                #end if

                # Make a reference to the tree
                record.atm = atm
#                atmCount += 1
            #end if
        #end for
        if not foundModel: # X-rays do not have MODEL record
            self.modelCount = 1

#        nTdebug('end pdbParser._records2tree: parsed %d pdb records, %d models', atmCount, self.modelCount)
    #end def

    def _matchResiduesAndAtoms(self):
        """
        Match residues and Atoms in the tree to CING db using self.convention
        """
#        nTdebug("Now in _matchResiduesAndAtoms")
        unmatchedAtomByResDict = {}
#        unmatchedResDict = {}
        for res in self.tree.subNodes(depth = 2):
            self.matchGame.matchResidue2Cing(res)
            for atm in res:
                if not self.matchGame.matchAtom2Cing(atm):
                    if not unmatchedAtomByResDict.has_key(res.resName):
                        unmatchedAtomByResDict[ res.resName ] = ([], [])
                    atmList = unmatchedAtomByResDict[res.resName][0]
                    resNumList = unmatchedAtomByResDict[res.resName][1]
                    if atm.name not in atmList:
                        atmList.append(atm.name)
                    if res.resNum not in resNumList:
                        resNumList.append(res.resNum)

                    if not self.allowNonStandardResidue:
                        atm.skip = True
                        continue

#                   aName = moveFirstDigitToEnd(atm.name) # worry about this?
                    atm.db = res.db.appendAtomDef(atm.name)
                    if not atm.db:
#                        nTwarning("Should have been possible to add a non-standard atom %s to the residue %s" % (atm.name, res.resName))
                        continue

        msg = "==> Non-standard (residues and their) atoms"
        if self.allowNonStandardResidue:
            msg += " to add:\n"
        else:
            msg += " to skip:\n"

        if unmatchedAtomByResDict:
            msg += unmatchedAtomByResDictToString(unmatchedAtomByResDict)
            if self.allowNonStandardResidue:
                nTmessage(msg)
            else:
                nTerror(msg)
    #end def

    def initMolecule(self, moleculeName):
        """Initialize new Molecule instance from the tree.
        Return Molecule on None on error.
        """
        mol = Molecule(name = moleculeName)

        # The self.tree contains a tree-like representation of the pdb-records
        for ch in self.tree:
            chain = mol.addChain(name = ch.name)
            for res in ch:
#                print '>', ch, res, res.skip, res.db
                if not res.skip and res.db != None:
                    residue = chain.addResidue(res.db.name, res.resNum)
                    if residue == None:
                        nTerror("Not adding residue: %s" % res)
                        continue
                    residue.addAllAtoms()
                #end if
            #end for
        #end for
#        nTdebug('pdbParser.initMolecule: %s', mol)
        self.map2molecule(mol)
        return mol
    #end for

    def map2molecule(self, molecule):
        """
        Map the tree to CING molecule instance.
        """

        unmatchedAtomByResDict = {}

        for chn in self.tree:
            for res in chn:
#                nTdebug("map2molecule res: %s" % res)
                if res.skip or (not res.db):
                    continue
                for atm in res:
                    atm.atom = None
                    if atm.skip or (not atm.db):
#                        nTerror("pdbParser#map2molecule was flagged before right?")
#                        nTdebug( '>> %s' % atm )
                        continue
                    #t = (IUPAC, chn.name, res.resNum, atm.db.name)
                    # GV the atm.db.name is BY DEFINITION in INTERNAL format!
                    # IUPAC and other mapping has already been done before and should not be
                    # repeated here. It also will cause a potential swap of atoms
                    t = (INTERNAL, chn.name, res.resNum, atm.db.name)
                    atm.atom = molecule.decodeNameTuple(t)
#                    if res.resNum==83:
#                        nTdebug(  '>> %s %s %s', atm.name, t, atm.atom )
#                    if not atm.atom: # for the non-standard residues and atoms.
#                        t = (INTERNAL, chn.name, res.resNum, atm.db.name)
#                        atm.atom = molecule.decodeNameTuple(t)
                    if not atm.atom:
                        # JFD: Report all together now.
                        if not unmatchedAtomByResDict.has_key(res.resName):
                            unmatchedAtomByResDict[ res.resName ] = ([], [])
                        atmList = unmatchedAtomByResDict[res.resName][0]
                        resNumList = unmatchedAtomByResDict[res.resName][1]
                        if atm.name not in atmList:
                            atmList.append(atm.name)
                        if res.resNum not in resNumList:
                            resNumList.append(res.resNum)
                        #end if
                    #end if
                #end for
            #end for
        #end for
        self.molecule = molecule

        if unmatchedAtomByResDict:
            msg = "pdbParser.map2molecule: Strange! Warning mapping atom for:\n"
            msg += unmatchedAtomByResDictToString(unmatchedAtomByResDict)
            nTwarning(msg)
    #end def

    def importCoordinates(self, nmodels = None, update = True):
        """
        Import coordinates into self.molecule.
        Optionally use only first nmodels.
        Optionally do not update dihedrals, mean-coordinates, .. (Be careful; only intended for conversion
        purposes).

        Return True on error
        """

        if not self.molecule:
            nTerror('pdbParser.importCoordinates: undefined molecule')
            return True
        #end if

        if nmodels == None:
            nmodels = self.modelCount # import all models found in pdfFile
        #end if

        if nmodels > self.modelCount:
            nTerror('pdbParser.importCoordinates: requesting %d models; only %d present', nmodels, self.modelCount)
            return True
        #end if
        msgHol = MsgHoL()
        model = self.molecule.modelCount # set current model from models already present
        foundModel = False
        for record in self.pdbRecords:
            recordName = record._name.strip()
            if recordName == "MODEL":
                foundModel = True
#                nTdebug('pdbParser.importCoordinates: importing as MODEL %d', model)
                continue

            elif recordName == "ENDMDL":
                model += 1
                if model == self.molecule.modelCount + nmodels:
                    break

            elif recordName == "ATOM" or recordName == "HETATM":
#                if (not record.atm.skip) and (record.atm.atom != None):
                if not record.atm:
                    continue
#                nTdebug("record.atm: %s" % record.atm)
                if record.atm.skip:
                    continue
                if not record.atm.atom:
                    continue
                atom = record.atm.atom
                # Check if the coordinate already exists for this model
                # This might happen when alternate locations are being
                # specified. Simplify to one coordinate per model.
                if len(atom.coordinates) <= model:
                    atom.addCoordinate(record.x, record.y, record.z, Bfac = record.tempFactor, occupancy = record.occupancy)
                else:
                    msgHol.appendMessage('pdbParser.importCoordinates: Skipping duplicate coordinate within same record (%s)' % record)
                #end if
            #end if
        #end for
        msgHol.showMessage(max_messages=20)
        if not foundModel: # X-rays do not have MODEL record
            self.molecule.modelCount += 1
        else:
            self.molecule.modelCount = model

        if update:
            self.molecule.updateAll()

#        nTdebug('pdbParser.importCoordinates: %s', self.molecule)
        return False
    #end def
#end class

class MatchGame:
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

#        nTdebug("Now in _matchResidue2Cing: %s" % res)

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
        res.db = NTdb.appendResidueDef(name = res.resName, shortName = '_', comment='From parsing PDB file')
        if not res.db:
            nTcodeerror("Adding a non-standard residue should have been possible.")
            return None
        res.db.nameDict[self.convention] = res.resName

        # Just a check, disable for speed.
        _x = NTdb.getResidueDefByName(res.resName)
        if not _x:
            nTcodeerror("Added residue but failed to find it again in pdbParser#_matchResidue2Cing")

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

#        nTdebug("Now in _matchAtom2Cing: %s" % atm)

        if not atm:
            nTerror('pdbParser._matchAtom: undefined atom')
            return None
        #end if

        atm.db = None
        atm.skip = False
        res = atm._parent

        if not res:
            nTerror('pdbParser._matchAtom: undefined parent residue, atom %s, convention %s, not matched',
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
            nTerror('_matchAtom2Cing: undefined parent residue DB')
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

        #print '>============>', atm, aName, self.convention, res.db.format()

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
#                nTdebug('pdbParser._matchAtom: patched atom %s, residue %s %s, convention %s',
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


def initPDB(project, pdbFile, convention = IUPAC, name = None, nmodels = None, update = True, allowNonStandardResidue = True):
    """Initialize Molecule from pdbFile.
       convention eq. CYANA, CYANA2, XPLOR, IUPAC

       Optionally include only nmodels.
       Optionally do not update dihedrals, mean-coordinates, .. (Be careful; only intended for conversion
       purposes).

       returns molecule instance or None on error
    """
    if not os.path.exists(pdbFile):
        nTerror('Project.initPDB: missing PDB-file "%s"', pdbFile)
        return None

#    nTmessage('==> initializing from PDB file "%s"', pdbFile) # repeated in the parser.

    if not name:
        _path, name, _ext = nTpath(pdbFile)
    parser = pdbParser(pdbFile, convention = convention, allowNonStandardResidue = allowNonStandardResidue)
    if not parser:
        nTerror('No pdbParser found in initPDB.')
        return None
    molecule = parser.initMolecule(name)
    if not molecule:
        return None
    if not molecule:
        nTerror('Project.initPDB: failed parsing PDB-file "%s"', pdbFile)
        return None
    parser.importCoordinates(nmodels = nmodels, update = update)
    project.appendMolecule(molecule)
#    if update:
#        project.molecule.updateAll()
    #end if
    project.addHistory(sprintf('New molecule from PDB-file "%s"', pdbFile))
    return molecule
#end def


def importPDB(project, pdbFile, convention = IUPAC, nmodels = None):
    """Import coordinates from pdbFile
        return pdbFile or None on error
    """
    if not project.molecule:
        nTerror("importPDB: no molecule defined")
        return None
    if not importFromPDB(project.molecule, pdbFile, convention, nmodels = nmodels):
        return None

    project.addHistory(sprintf('importPDB from "%s"', pdbFile))
    nTmessage('%s', project.molecule.format())
    #end if
    return pdbFile
#end def

def export2PDB(project, tmp = None):
    """
    Export coordinates to pdb file.
    Return filename on first exported file or None for error.
    """
    for mol in project.molecules:
        if mol.modelCount > 0:
            fname = project.path(project.directories.PDB, mol.name + '.pdb')
            nTdetail('==> Exporting to PDB file "%s"', fname)
            pdbFile = mol.toPDB(fileName = fname, convention = IUPAC)
            pdbFile.save(fname)
            #del(pdbFile)
            return fname
        #end if
    #end for
    return None
#end def
