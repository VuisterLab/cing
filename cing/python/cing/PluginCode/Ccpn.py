from cing.Libs.NTutils import switchOutput
switchOutput(False)
# Leave this at the top of ccp imports as to prevent non-errors from non-cing being printed.
from ccp.general.Util import createMoleculeTorsionDict
from ccp.general.Util import getResonancesFromPairwiseConstraintItem
from cing.Libs.NTutils import MsgHoL
from cing.Libs.NTutils import NTcodeerror
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTdetail
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTlimitSingleValue
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import removeRecursivelyAttribute
from cing.Libs.NTutils import sprintf
from cing.Libs.NTutils import val2Str
from cing.Libs.fpconst import NaN
from cing.core.classes import DihedralRestraint
from cing.core.classes import DistanceRestraint
from cing.core.classes import Peak
from cing.core.classes import RDCRestraint
from cing.core.constants import CCPN
from cing.core.constants import CING
from cing.core.constants import INTERNAL
from cing.core.constants import IUPAC
from cing.core.database import NTdb
from cing.core.molecule import Molecule
from cing.core.molecule import ensureValidChainId
from cing.core.molecule import unmatchedAtomByResDictToString
from memops.general.Io import loadProject
from shutil import move
from shutil import rmtree
from cing.core.constants import DR_LEVEL
from cing.core.constants import HBR_LEVEL
from cing.core.constants import AC_LEVEL
from cing.core.constants import RDC_LEVEL
import os
import string
import tarfile

switchOutput(True)

"""
    Adds initialize from CCPN project files
    Class to accommodate a ccpn project and import it into a CING project instance

    Steps:
    - Parse the ccpn file using the CCPN api
...
    - Import the coordinates.
    - Import the experimental data.

    The allowNonStandardResidue determines if the non-standard residues and atoms are read. If so they will be shown as
    a regular message. Otherwise they will be shown as a warning. Just like MolMol does; the unknown atoms per residue.
    See the image at: http://code.google.com/p/cing/issues/detail?id=126#c4
    
                             atom<->residue->chain<->molecule<-self
                              |
    self->tree<->chn<->res<->atm<-record<-self
                       |      |
               ResidueDef<->AtomDef
"""

class Ccpn:
    SMALL_FLOAT_FOR_DIHEDRAL_ANGLES = 1. / 1e9 # there's a bug in pydev extension preventing me to write: 1.e-9
    # Reported: https://sourceforge.net/tracker2/index.php?func=detail&aid=2049228&group_id=85796&atid=577329
    
    RESTRAINT_IDX_DISTANCE = 0
    RESTRAINT_IDX_HBOND = 1
    RESTRAINT_IDX_DIHEDRAL = 2
    RESTRAINT_IDX_RDC = 3
    RESTRAINT_IDX_CS = 4
    
    
    CCPN_PROTEIN = 'protein'
    CCPN_DNA = 'DNA'
    CCPN_RNA = 'RNA'
    CCPN_OTHER = 'other'
    
    CCPN_START = 'start'
    CCPN_MIDDLE = 'middle'
    CCPN_END = 'end'
    
    CCPN_NEUTRAL = 'neutral'
    CCPN_PROT_H3 = 'prot:H3'
    CCPN_DEPROT_H_DOUBLE_PRIME = "deprot:H''"
    CCPN_LINK_SG = 'link:SG'
    CCPN_DEPROT_HG = 'deprot:HG'
    
    CCPN_DISTANCE_CONSTRAINT = 'DistanceConstraint'
    CCPN_HBOND_CONSTRAINT = 'HBondConstraint'
    CCPN_DIHEDRAL_CONSTRAINT = 'DihedralConstraint'
    CCPN_RDC_CONSTRAINT = 'RdcConstraint'
    CCPN_CS_CONSTRAINT = 'ChemShiftConstraint'

    CCPN_DISTANCE_CONSTRAINT_LIST = 'DistanceConstraintList'
    CCPN_HBOND_CONSTRAINT_LIST = 'HBondConstraintList'
    CCPN_DIHEDRAL_CONSTRAINT_LIST = 'DihedralConstraintList'
    CCPN_RDC_CONSTRAINT_LIST = 'RdcConstraintList'
    CCPN_CS_CONSTRAINT_LIST = 'ChemShiftConstraintList'
    
    CCPN_CLASS_RESTRAINT = { RESTRAINT_IDX_DISTANCE: CCPN_DISTANCE_CONSTRAINT,
                            RESTRAINT_IDX_HBOND: CCPN_HBOND_CONSTRAINT,
                            RESTRAINT_IDX_DIHEDRAL: CCPN_DIHEDRAL_CONSTRAINT,
                            RESTRAINT_IDX_RDC: CCPN_RDC_CONSTRAINT,
                            RESTRAINT_IDX_CS: CCPN_CS_CONSTRAINT,
                            }

    CCPN_CLASS_RESTRAINT_LIST = { RESTRAINT_IDX_DISTANCE: CCPN_DISTANCE_CONSTRAINT_LIST,
                            RESTRAINT_IDX_HBOND: CCPN_HBOND_CONSTRAINT_LIST,
                            RESTRAINT_IDX_DIHEDRAL: CCPN_DIHEDRAL_CONSTRAINT_LIST,
                            RESTRAINT_IDX_RDC: CCPN_RDC_CONSTRAINT_LIST,
                            RESTRAINT_IDX_CS: CCPN_CS_CONSTRAINT_LIST,
                            }
    
    "Don't report on the next atoms"
    # Add these to CING lib later. For now, it's just clobbering the output to report on them.
    CCPN_ATOM_LIST_TO_IGNORE_REPORTING = []
    hideMissingAtomsJfdKnowsAbout = False # default should be False
    if hideMissingAtomsJfdKnowsAbout:
        CCPN_ATOM_LIST_TO_IGNORE_REPORTING = "ZN O' HO3' HO5' HOP2 HOP3 OP3".split(' ')
    
    def __init__(self, project, ccpnFolder, convention = IUPAC, patchAtomNames = True,
                 skipWaters = False, allowNonStandardResidue = True):
        self.project = project 
        self.ccpnProject = None # set in readCcpnFolder
        self.listMolSystems = None # set in importFromCcpnMolecule
        self.ccpnNmrProject = None # set in importFromCcpnMolecule
        self.molecule = None # set in importFromCcpn ( importFromCcpnMolecule )
        self.ccpnFolder = ccpnFolder
        self.convention = convention
        self.patchAtomNames = patchAtomNames
        self.skipWaters = skipWaters
        self.allowNonStandardResidue = allowNonStandardResidue
                
    def readCcpnFolder(self):
        """Return ccpnProject on success or None on failure"""
        if not self.ccpnFolder:
            NTerror("No ccpnFolder")
            return None
    
        if os.path.exists(self.ccpnFolder) and os.path.isfile(self.ccpnFolder) and (\
            self.ccpnFolder.endswith(".tgz") or self.ccpnFolder.endswith(".tar.gz")):
            try:
                rmtree(self.project.name)
            except:
                pass
            # Example layout.
    #        linkNmrStarData/
    #        linkNmrStarData/ccp/
    #        linkNmrStarData/ccp/nmr/
    #        linkNmrStarData/ccp/nmr/NmrConstraint/
    #        linkNmrStarData/ccp/nmr/NmrConstraint/1+1brv_user_2008-08-19-09-46-57-171_00002.xml
    
            # Get a TarFile class.
            ccpnRootDirectory = None # Will become linkNmrStarData at first.
            tar = tarfile.open(self.ccpnFolder, "r:gz")
            for itar in tar:
                tar.extract(itar.name, '.') # itar is a TarInfo object 
    #            NTdebug("extracted: " + itar.name)
                if isRootDirectory(itar.name):
                    if not ccpnRootDirectory: # pick only the first one.
                        ccpnRootDirectory = itar.name.replace("/", '')
                        if not ccpnRootDirectory:
                            NTerror("Skipping potential ccpnRootDirectory")
            tar.close()
            if not ccpnRootDirectory:
                NTerror("No ccpnRootDirectory found in gzipped tar file: %s" % self.ccpnFolder)
                return None
    
            if ccpnRootDirectory != self.project.name:
                move(ccpnRootDirectory, self.project.name)
            ccpnFolder = self.project.name # Now it is a folder.
    
        if (not ccpnFolder) or (not os.path.exists(ccpnFolder)):
            NTerror("ccpnFolder '%s' not found", ccpnFolder)
            return None
        # end if
    
        switchOutput(False) # let's skip the note on stdout of changed hard-coded directories
        self.ccpnProject = loadProject(ccpnFolder)
        switchOutput(True)
        if not self.ccpnProject:
            NTerror(" ccpn project from folder '%s' not loaded", ccpnFolder)
            return None
    
        # Make mutual linkages between Ccpn and Cing objects
        self.project.ccpn = self.ccpnProject
        self.ccpnProject.cing = self.project
            # end if
    
        return self.project
    # end def initCcpn
        
    def _getCcpnMolSystemList(self):
        '''Descrn: Check which list of molSystem to return for a given function.
           Inputs: 
           Output: List of Ccpn.MolSystems, None on error.
        '''
    
        # If 'moleculeName' is not specified, it'll import all MolSystems
        listMolSystems = self.ccpnProject.molSystems or [] 
        if not listMolSystems:
            NTerror(" _getCcpnMolSystemList: not found in Ccpn; returning error")
            return None

        return listMolSystems
    
    def _getCcpnNmrProject(self):
        '''Descrn: Check which list of molSystem to return.
           Inputs: Cing.Project, function name.
           Output: ccp.nmr.Nmr.NmrProject, None on error.
        '''
        # Taking only one NmrProject for the moment
        if self.ccpnProject.currentNmrProject:
            ccpnNmrProject = self.ccpnProject.currentNmrProject
        elif self.ccpnProject.nmrProjects:
            ccpnNmrProject = self.ccpnProject.findFirstNmrProject()            
        return ccpnNmrProject  
    
    
    def importFromCcpn(self):
        '''Descrn: Import data from Ccpn into a Cing instance.
                   Check if either instance has attribute .cing or .ccpn,
                   respectively.
           Inputs: Ccpn Implementation.Project, Cing.Project instance.
           Output: None on error.
        '''
        
        if not self.readCcpnFolder():
            NTerror("Failed readCcpnFolder")
            return None
        
        NTmessage('==> Importing data from Ccpn project "%s"', self.ccpnProject.name)
    
        if not self.importFromCcpnMolecule():
            NTerror("Failed to importFromCcpnMolecule")
            return None
    
    
        if self.importFromCcpnPeakAndShift():
            NTmessage('==> Ccpn peaks and shifts imported')
        if self.importFromCcpnDistanceRestraint():
            NTmessage('==> Ccpn distance restraints imported')
        if self.importFromCcpnDihedralRestraint():
            NTmessage('==> Ccpn dihedral restraints imported')
        if self.importFromCcpnRdcRestraint():
            NTmessage('==> Ccpn RDC restraints imported')
        
        NTmessage('==> Ccpn project imported')

        self.project.addHistory(sprintf('Imported CCPN project'))
        self.project.updateProject()
    
        return True # To distinguish success from failure.
    # end def importFromCcpn
    
    def importFromCcpnMolecule(self):
        '''Descrn: Import MolSystems (Molecules) from Ccpn.Project instance and
                   append it to Cing.Project instance, including chains, residues
                   and atoms.
                   If 'moleculeName' is not defined, all MolSystem will be
                   imported, otherwise only specified one.
                   As input either Cing.Project instance or Ccpn.Project instance,
                   or both, since it'll check if instances has attribute .ccpn or
                   .cing, respectively.
           Inputs: Ccpn Implementation.Project, Cing.Project instance,
                   moleculeName (string).
           Output: List of Cing.Molecule or None on error.
        '''
    
        self.listMolSystems = self._getCcpnMolSystemList() 
        if not self.listMolSystems: 
            NTerror("Failed to _getCcpnMolSystemList")
            return None         
        self.ccpnNmrProject = self._getCcpnNmrProject() 
        if not self._getCcpnNmrProject():
            NTerror("Failed to _getCcpnNmrProject")
            return None
         
        for ccpnMolSys in self.listMolSystems:
            moleculeName = self.project.uniqueKey(self._ensureValidName(ccpnMolSys.code))    
            self.molecule = Molecule(name = moleculeName)
            self.project.appendMolecule(self.molecule)
    
            self.molecule.ccpn = ccpnMolSys
            ccpnMolSys.cing = self.molecule
                
    
            if not len(ccpnMolSys.structureEnsembles):
                NTerror("There are no coordinates for molecule %s", self.molecule.name)
    
            # stuff molecule with chains, residues and atoms and coords
            if not self._match2Cing():
                NTerror("Failed to _match2Cing")
                return None
                
    
            self.project.molecule.updateAll()
            NTmessage("==> Ccpn molecule '%s' imported with coordinates", moleculeName)
        # end for
    
        self.project.updateProject()
    
        return True
    # end def importFromCcpnMolecule
    
    
    def _match2Cing(self):
        '''Descrn: Imports chains, residues, atoms and coords
                   from Ccpn.MolSystem into a Cing.Project.Molecule instance.
                   (fastest way to import since it loops only once over
                   chains, residues, atoms and coordinates.)
           Output: Cing.Molecule or None on error.
        '''
        unmatchedAtomByResDict = {}
    
        ccpnMolSys = self.molecule.ccpn
    
        # we are taking just the current Ensemble now
        ccpnStructureEnsemble = ccpnMolSys.parent.currentStructureEnsemble
        if ccpnStructureEnsemble.molSystem is not ccpnMolSys:
            ccpnStructureEnsemble = ccpnMolSys.findFirstStructureEnsemble(molSystem = ccpnMolSys)
    
        try:
            ensembleName = ccpnStructureEnsemble.structureGeneration.name
        except AttributeError:
            ensembleName = 'ensemble_name'
    
        NTdebug("Using CCPN Structure Ensemble '%s'", ensembleName)
    
        self.molecule.modelCount += len(ccpnStructureEnsemble.models)
    
        ccpnMolCoordList = [ccpnStructureEnsemble]
    
        # Set all the chains for this molSystem
        for ccpnChain in ccpnMolSys.sortedChains():
            
            ccpnChainLetter = ensureValidChainId(ccpnChain.pdbOneLetterCode)
    #        NTdebug("Chain id from CCPN %s to CING %s" % (ccpnChainLetter, ccpnChain.pdbOneLetterCode))
            if ccpnChainLetter != ccpnChain.pdbOneLetterCode:
                NTcodeerror("Changed chain id from CCPN %s to CING %s" % (ccpnChainLetter, ccpnChain.pdbOneLetterCode))
                NTerror("This will most likely lead to inconsistencies in CING")
                # This isn't a problem if CCPN uses the same chain id's i.e. no spaces or special chars.
                # From CCPN doc:
    #            One letter chain identifier. Will be used by PDB (and programs that use similar conventions). WARNING: having same oneLetterCode for different chains is legal but may cause serious confusion.
                # Looking at the complex case of 1ai0 which in the PDB formatted PDB file it has spaces for the chain id
                # the NRG derived CCPN file has beautiful unique simple chain ids A thru U.
    #    loop_
    #       _Entity_assembly.ID
    #       _Entity_assembly.Entity_assembly_name
    #       _Entity_assembly.Entity_ID
    #       _Entity_assembly.Entity_label
    #       _Entity_assembly.Asym_ID
    #       _Entity_assembly.Experimental_data_reported
    #       _Entity_assembly.Physical_state
    #       _Entity_assembly.Conformational_isomer
    #       _Entity_assembly.Chemical_exchange_state
    #       _Entity_assembly.Magnetic_equivalence_group_code
    #       _Entity_assembly.Role
    #       _Entity_assembly.Details
    #       _Entity_assembly.Entry_ID
    #       _Entity_assembly.Assembly_ID
    #
    #        1 R6_INSULIN_HEXAMER   2 $R6_INSULIN_HEXAMER   A . . yes yes . . . 1 1 
    #        2 R6_INSULIN_HEXAMER_2 1 $R6_INSULIN_HEXAMER_2 B . . yes yes . . . 1 1 
    #        3 R6_INSULIN_HEXAMER   2 $R6_INSULIN_HEXAMER   C . . yes yes . . . 1 1 
    #        4 R6_INSULIN_HEXAMER_2 1 $R6_INSULIN_HEXAMER_2 D . . yes yes . . . 1 1 
    #        5 R6_INSULIN_HEXAMER   2 $R6_INSULIN_HEXAMER   E . . yes yes . . . 1 1 
    #        6 R6_INSULIN_HEXAMER_2 1 $R6_INSULIN_HEXAMER_2 F . . yes yes . . . 1 1 
    #        7 R6_INSULIN_HEXAMER   2 $R6_INSULIN_HEXAMER   G . . yes yes . . . 1 1 
    #        8 R6_INSULIN_HEXAMER_2 1 $R6_INSULIN_HEXAMER_2 H . . yes yes . . . 1 1 
    #        9 R6_INSULIN_HEXAMER   2 $R6_INSULIN_HEXAMER   I . . yes yes . . . 1 1 
    #       10 R6_INSULIN_HEXAMER_2 1 $R6_INSULIN_HEXAMER_2 J . . yes yes . . . 1 1 
    #       11 R6_INSULIN_HEXAMER   2 $R6_INSULIN_HEXAMER   K . . yes yes . . . 1 1 
    #       12 R6_INSULIN_HEXAMER_2 1 $R6_INSULIN_HEXAMER_2 L . . yes yes . . . 1 1 
    #       13 ZINC_ION             3 $ZINC_ION             M . . yes yes . . . 1 1 
    #       14 ZINC_ION             3 $ZINC_ION             N . . yes yes . . . 1 1 
    #       15 PHENOL               4 $PHENOL               O . . yes yes . . . 1 1 
    #       16 PHENOL               4 $PHENOL               P . . yes yes . . . 1 1 
    #       17 PHENOL               4 $PHENOL               Q . . yes yes . . . 1 1 
    #       18 PHENOL               4 $PHENOL               R . . yes yes . . . 1 1 
    #       19 PHENOL               4 $PHENOL               S . . yes yes . . . 1 1 
    #       20 PHENOL               4 $PHENOL               T . . yes yes . . . 1 1 
    #       21 water                5 $water                U . . yes yes . . . 1 1 
    #    stop_
                              
            chain = self.molecule.addChain(ccpnChainLetter)
    
            # Make mutual linkages between Ccpn and Cing instances
            chain.ccpn = ccpnChain
            ccpnChain.cing = chain
    
            #ccpnModel = None # for ccpnModel in ccpnMolCoord.sortedModels():
    #        if coords:
            # Get coord info for chains from Ccpn
            ccpnCoordChainList = []
            for ccpnMolCoord in ccpnMolCoordList:
                ccpnCoordChain = ccpnMolCoord.findFirstCoordChain(chain = ccpnChain)
                if ccpnCoordChain:
                    ccpnCoordChainList.append(ccpnCoordChain)
                # end if
            # end for
            for ccpnResidue in ccpnChain.sortedResidues():                
                ccpnMolType = ccpnResidue.molType # Can not be taken outside loop because within a chain multiple molTypes might occur in CCPN.
                resNumber = ccpnResidue.seqCode
                chemCompVar = ccpnResidue.chemCompVar
                chemComp = chemCompVar.chemComp
                ccpnLinking = ccpnResidue.linking # start, middle, or end.
                ccpnResName3Letter = chemComp.code3Letter   # e.g. HIS
                ccpnResCode = ccpnResidue.ccpCode           # e.g. HIS
                ccpnResDescriptor = chemCompVar.descriptor  # e.g. protein His prot:HE2;deprot:HD1
                                                    
                ccpnResDescriptorPatched = patchCcpnResDescriptor(ccpnResDescriptor, ccpnMolType, ccpnLinking)
                                
#    nameDict = {'CCPN': 'DNA A deprot:H1'..
                ccpnResNameInCingDb = "%s %s %s" % (ccpnResidue.molType, ccpnResCode, ccpnResDescriptorPatched)
#                NTdebug("Name3Letter, Code, Descriptor, DescriptorPatched NameInCingDb %s, %s, %s, %s, %s" % (
#                          ccpnResName3Letter, ccpnResCode, ccpnResDescriptor, ccpnResDescriptorPatched, ccpnResNameInCingDb))
                
#See bottom of this file for CCPN residue name mappings in CING db.
# Note that this will be ok except for the terminii which will always deviate in the descriptor/stereochemistry info.
# The terminii will be dealt with in separate code below but JFD thinks it is acceptable to map in those cases to the
# simple 4 letter residue code.
                

                addResidue = True
                addingNonStandardResidue = False
                matchingConvention = CCPN
                if NTdb.isValidResidueName(ccpnResNameInCingDb, convention = matchingConvention):
                    pass
#                    NTdebug("Residue '%s' identified in CING DB as %s." % (ccpnResNameInCingDb, matchingConvention))
                else:
                    # Happens for every terminal residue
#                    NTdebug("Residue '%s' not identified in CING DB as %s." % (ccpnResNameInCingDb, matchingConvention))
                    matchingConvention = INTERNAL
                    if NTdb.isValidResidueName(ccpnResName3Letter):
#                        NTdebug("Residue '%s' identified in CING DB as %s." % (ccpnResName3Letter, matchingConvention))
                        pass
                    else:
                        if self.allowNonStandardResidue:
                            NTdebug("Residue '%s' will be a new residue in convention %s." % (ccpnResName3Letter, matchingConvention))
                        else:
                            NTdebug("Residue '%s' will be skipped as it is non-standard in convention: %s." % (ccpnResName3Letter, matchingConvention))
                            addResidue = False
                            addingNonStandardResidue = True
#                        if not unmatchedAtomByResDict.has_key(ccpnResName3Letter):
#                            unmatchedAtomByResDict[ ccpnResName3Letter ] = ([], [])
                        
                if not addResidue:
                    continue
                        
                Nterminal = False
                Cterminal = False        
                if ccpnMolType == Ccpn.CCPN_PROTEIN:
                    ccpnLinking = ccpnResidue.linking                
                    if ccpnLinking == Ccpn.CCPN_START:
                        Nterminal = True
                    elif ccpnLinking == Ccpn.CCPN_END:
                        Cterminal = True

                resNameCing = ccpnResNameInCingDb
                if matchingConvention == INTERNAL:
                    resNameCing = ccpnResName3Letter
                residue = chain.addResidue(resNameCing, resNumber, convention = matchingConvention, Nterminal = Nterminal, Cterminal = Cterminal)
                if not residue:
                    NTcodeerror("Failed to add residue: [" + resNameCing + ']')
                    continue
                    
                # Make mutual linkages between Ccpn and Cing objects
                residue.ccpn = ccpnResidue
                ccpnResidue.cing = residue
    
                if not addingNonStandardResidue:
                    residue.addAllAtoms()
    
                ccpnCoordResidueList = []
                # Get coord info for residues from Ccpn
                for ccpnCoordChain in ccpnCoordChainList:
                    ccpnCoordResidue = ccpnCoordChain.findFirstResidue(residue = ccpnResidue)
                    if ccpnCoordResidue:
                        ccpnCoordResidueList.append(ccpnCoordResidue)
                
                for ccpnAtom in ccpnResidue.sortedAtoms():
                    atomName = ccpnAtom.chemAtom.name
                    
                    # Luckily no need for residue names here.
                    cingNameTuple = (matchingConvention, chain.name, resNumber, atomName)
                    atom = self.molecule.decodeNameTuple(cingNameTuple)
            
                    if not atom:
#                        NTdebug('Creating non-standard atom %s' % `cingNameTuple`)
                        cingResNameTuple = (INTERNAL, chain.name, resNumber, None)
                        res = self.molecule.decodeNameTuple(cingResNameTuple)
                        if not res:
                            NTcodeerror('No residue found in CING for tuple %s. Skipping creating non-standard atoms' % cingResNameTuple)
                            continue
                        atom = res.addAtom(atomName)
                        if not atom:
                            NTdebug('Failed to add atom to residue for tuple %s' % `cingNameTuple`)
                            continue
                        if not unmatchedAtomByResDict.has_key(ccpnResName3Letter):
                            unmatchedAtomByResDict[ ccpnResName3Letter ] = ([], [])
                        atmList = unmatchedAtomByResDict[ccpnResName3Letter][0] 
                        resNumList = unmatchedAtomByResDict[ccpnResName3Letter][1]
                         
                        if (atomName not in atmList) and (atomName not in self.CCPN_ATOM_LIST_TO_IGNORE_REPORTING):
                            atmList.append(atomName)
                        if res.resNum not in resNumList:
                            resNumList.append(res.resNum)
                                    
                    atom.ccpn = ccpnAtom
                    ccpnAtom.cing = atom
            
                    # Get coords for atoms
                    for ccpnCoordResidue in ccpnCoordResidueList:
                        ccpnCoordAtom = ccpnCoordResidue.findFirstAtom(atom = ccpnAtom)
            
                        if not ccpnCoordAtom:
                            # GV says: do not know why we would have this error, as we have matched the atom objects
                            #TODO: issue 128 JFD: It usually happens for H in N-term, which CING is not mapping yet. GV will fix.
#                            NTdebug('CING %s not found in CCPN: %s', atom, ccpnAtom)
                            continue
                        # end if
            
                        if ccpnCoordAtom.coords:
                            i = - 1
                            for ccpnModel in ccpnCoordResidue.parent.parent.sortedModels():
                                i += 1
                                ccpnCoord = ccpnCoordAtom.findFirstCoord(model = ccpnModel)
                                if not ccpnCoord: # as in entry 1agg GLU1.H2 and 3.
                                    NTwarning("Skippng coordinate for CING failed to find coordinate for model %d for atom %s" % (i, atom))
                                    continue
                                atom.addCoordinate(ccpnCoord.x, ccpnCoord.y, ccpnCoord.z, ccpnCoord.bFactor, ocuppancy = ccpnCoord.occupancy)
                            # end for
                        # end if
                    # end for
                # end for                
            # end for
        # end for
        msg = "Non-standard (residues and their) atoms"
        if self.allowNonStandardResidue:
            msg += " added:\n"
        else:
            msg += " skiped:\n"
        
        if unmatchedAtomByResDict:
            msg += unmatchedAtomByResDictToString(unmatchedAtomByResDict)
            if self.allowNonStandardResidue:
                NTmessage(msg)
            else:
                NTerror(msg)             
        
        return self.molecule
    # end def _match2Cing
    
    def _getCingAtom(self, ccpnAtomSet):
        """Matches to CING atoms or a pseudoAtom
        Return list or None on Error.
        """
        
        NTdebug("    ccpnAtomSet = %s" % ccpnAtomSet)
        
        ccpnAtomList = ccpnAtomSet.sortedAtoms()
        if not ccpnAtomList:
            NTerror("No ccpnAtomList: %s", ccpnAtomList)
            return None
                
        
        # Quicky for efficiency.
        if len(ccpnAtomList) == 1:
            ccpnAtom = ccpnAtomList[0]
            if not hasattr(ccpnAtom, 'cing'):
                NTerror("No Cing atom obj equivalent for Ccpn atom: %s", ccpnAtom)
                return None
            return ccpnAtom.cing
            
        cingAtomList = []
        atomSeenLast = None
        for ccpnAtom in ccpnAtomList:
            NTdebug("      ccpn atom: %s" % ccpnAtom)
            if not hasattr(ccpnAtom, 'cing'):
                NTerror("No Cing atom obj equivalent for Ccpn atom: %s", ccpnAtom)
                return None
            atomSeenLast = ccpnAtom.cing
            cingAtomList.append(ccpnAtom.cing)

        if len(cingAtomList) < 2:
            return atomSeenLast
        
        if not atomSeenLast:
            NTerror("Failed to find single CING atom for ccpnAtomList %s" % ccpnAtomList)
            return None
        
        cingPseudoAtom = atomSeenLast.getRepresentativePseudoAtom(cingAtomList)
        if not cingPseudoAtom:
            
            return atomSeenLast
        return cingPseudoAtom
        
    
    def _getCcpnCoordinate(self):
        '''Descrn: Core that'll import coordinates from Ccpn.MolSystem
                   into a Cing.Project.Molecule instance.
           Inputs: Cing.Molecule instance (obj)
           Output: Cing.Project or None on error.
        '''
    
        ccpnMolSys = self.molecule.ccpn
    
        # we are taking just the current Ensemble now
        ccpnStructureEnsemble = ccpnMolSys.parent.currentStructureEnsemble
        molecule.modelCount += len(ccpnStructureEnsemble.models)
    
        ccpnMolCoords = [ccpnStructureEnsemble]
    
    #   Set all the chains for this molSystem
        for ccpnChain in ccpnMolSys.sortedChains():
    
            chain = ccpnChain.cing
    
            ccpnChainLetter = chain.name
    
            # Get coord info for chains from Ccpn
            ccpnCoordChains = []
            for ccpnMolCoord in ccpnMolCoords:
                ccpnCoordChain = ccpnMolCoord.findFirstCoordChain(chain = ccpnChain)
                if ccpnCoordChain:
                    ccpnCoordChains.append(ccpnCoordChain)
                # end if
            # end for
    
            for ccpnResidue in ccpnChain.sortedResidues():
                # Get coord info for residues from Ccpn
                ccpnCoordResidueList = []
                for ccpnCoordChain in ccpnCoordChains:
                    ccpnCoordResidue = ccpnCoordChain.findFirstResidue(residue = ccpnResidue)
                    if ccpnCoordResidue:
                        ccpnCoordResidueList.append(ccpnCoordResidue)
                    # end if
                # end for
    
                for ccpnAtom in ccpnResidue.sortedAtoms():
    
                    try:
                        atom = ccpnAtom.cing
                    except:
                        NTwarning(' Ccpn atom %s/%s/%s not mapped into Cing.Project',
                                  ccpnAtom.name,
                                  ccpnResidue.ccpCode + str(ccpnResidue.seqCode),
                                  ccpnChainLetter)
                        NTmessage('No coordinates taken, atom skipped...')
                        continue
                    # end try
    
                    for ccpnCoordResidue in ccpnCoordResidueList:
                        ccpnCoordAtom = ccpnCoordResidue.findFirstAtom(atom = ccpnAtom)
                        if ccpnCoordAtom and ccpnCoordAtom.coords:
                            for ccpnModel in ccpnCoordResidue.parent.parent.sortedModels():
                                ccpnCoord = ccpnCoordAtom.findFirstCoord(model = ccpnModel)
                                atom.addCoordinate(ccpnCoord.x, ccpnCoord.y, ccpnCoord.z, ccpnCoord.bFactor)
                            # end for
                        # end if
                    # end for
                # end for
            # end for
        # end for
    # end def _getCcpnCoordinate
    
    def importFromCcpnPeakAndShift(self, moleculeName = None):
        '''Descrn: Import peaks and shifts from Ccpn.Project into a Cing.Project
                   instance.
                   If 'moleculeName' is not defined, all MolSystem will be
                   imported, otherwise only specified one.
                   As input either Cing.Project instance or Ccpn.Project instance,
                   or both, since it'll check if instances has attribute .ccpn or
                   .cing, respectively.
           Inputs: Ccpn Implementation.Project, Cing.Project instance, moleculeName.
           Output: Cing.Project or None on error.
        '''
        doneSetShifts = False #@UnusedVariable
    
        # Get shift lists (linking resonances to atoms) from Ccpn for a Cing.Molecule
        # need to do it before importing Peaks
        for ccpnMolSys in self.listMolSystems:
    
            moleculeName = self._ensureValidName(ccpnMolSys.code)
    
            if not hasattr(ccpnMolSys, 'cing'):
                NTerror("molecule '%s' not found in Ccpn.Project", moleculeName)
                NTerror("You may want to import '%s' from Ccpn first", moleculeName)
                return None
                
            ccpnShiftLists = self.ccpnNmrProject.findAllMeasurementLists(className = 'ShiftList') or []
    
            for ccpnShiftList in ccpnShiftLists:
                shiftMapping = self._getShiftAtomNameMapping(ccpnShiftList, ccpnMolSys)
                _doneSetShifts = self._setShift(shiftMapping, ccpnShiftList)
            # end for
    #            if doneSetShifts:
    #                NTmessage( "==> Ccpn shifts (resonances) for molecule '%s' imported", moleculeName )
    #                NTmessage( '%s', self.project.molecule.format() )
            # end if
            # end if
        # end for
    
        # Get ALL peaks from Ccpn NmrProject and link them to resonances
        # It's supposed to be done only once
        doneSetPeaks = self._setPeak() #@UnusedVariable
    
    #    if doneSetPeaks:
    #        NTmessage( "==> Ccpn peaks imported" )
    #        NTmessage( '%s', self.project.format() )
        # end if
    
    #    if doneSetPeaks or doneSetShifts:
    #        self.project.addHistory( sprintf(funcName) )
    #        self.project.updateProject()
        # end if
        return self.project
    # end def importFromCcpnPeakAndShift
    
    def _getShiftAtomNameMapping(self, ccpnShiftList, molSystem):
        '''Descrn: Core function that maps Ccpn resonances (shifts) to Ccpn residues
                   and actual atoms.
           Inputs: ccp.nmr.Nmr.ShiftList, ccp.molecule.MolSystem.MolSystem.
           Output: A tupled dict mapping shifts (resonances) to residues/atoms.
        '''
    
        ccpnResonances = []
        ccpnResonanceToShift = {}
    
        for ccpnShift in ccpnShiftList.measurements:
            ccpnResonance = ccpnShift.resonance
            ccpnResonances.append(ccpnResonance)
            ccpnResonanceToShift[ccpnResonance] = ccpnShift
        # end for
    
        ccpnShiftMapping = {}
    
        # First make quick link for resonance -> atom
    
        for ccpnResonance in ccpnResonances:
    
            # Only a link from the resonance to an atom if there is a resonanceSet
    
            if ccpnResonance.resonanceSet:
    
                ccpnAtomSets = list(ccpnResonance.resonanceSet.atomSets)
                ccpnResidue = ccpnAtomSets[0].findFirstAtom().residue
    #            chemCompVar = ccpnResidue.chemCompVar
    #            namingSystemObject = chemCompVar.chemComp.findFirstNamingSystem(name=CING)
    
                # to skip residues outside molSystem whose atoms has resonances
                if ccpnResidue.chain.molSystem != molSystem:
                    continue
                # end if
    
                # Go over the atomSets and atoms, get right naming system for them
    
                atomList = []
    
                for ccpnAtomSet in ccpnAtomSets:
    
                    ccpnRefAtom = ccpnAtomSet.findFirstAtom()
                    currentCcpnResidue = ccpnRefAtom.residue
    
                    # Check if all is OK (no mapping to different residues)
                    if currentCcpnResidue != ccpnResidue:
                        NTerror("two residues to same resonance! (%s and %s)",
                                currentCcpnResidue.cing, ccpnResidue.cing)
                        break
                    # end if
    
                    for ccpnAtom in ccpnAtomSet.atoms:
    #                    # Now create list, with CING
    #                    # (could be set to other one)
    #                    # JFD: fails to see why this is a TO DO: 
                            #    use cing object link made earlier.
    #                    chemAtom = ccpnAtom.chemAtom
    #                    chemAtomSysName = namingSystemObject.findFirstAtomSysName(atomName = chemAtom, atomSubType=chemAtom.subType)
    #                    if chemAtomSysName:
    #                        atomName = chemAtomSysName.sysName
    #                    else:
    #                        atomName = atom.name
                        #atomNameList.append(atomName)
                        atomList.append(ccpnAtom)
                    # end for
                # end for    
                ccpnShiftMapping[ccpnResonanceToShift[ccpnResonance]] = [ccpnResidue, tuple(atomList) ]
            # end if
        # end for
    
        return (ccpnShiftMapping)
    # end def _getShiftAtomNameMapping
    
    def _setShift(self, shiftMapping, ccpnShiftList):
        '''Descrn: Core function that sets resonances to atoms.
           Inputs: Cing.Molecule instance (obj), ccp.molecule.MolSystem.MolSystem.
           Output: Cing.Project or None on error.
        '''
        # TO DO: shiftMapping should pass cing objects
        self.molecule.newResonances()
    
        ccpnShifts = shiftMapping.keys()
    
        for ccpnShift in ccpnShifts:
            shiftValue = ccpnShift.value
            shiftError = ccpnShift.error
            ccpnResidue, ccpnAtoms = shiftMapping[ccpnShift]
    
            for ccpnAtom in ccpnAtoms:
                try:
                    atom = ccpnAtom.cing
                    atom.resonances().value = shiftValue
                    atom.resonances().error = shiftError
                    index = len(atom.resonances) - 1
                    atom.setStereoAssigned() # untested for JFD has no test data.
                    # Make mutual linkages between Ccpn and Cing objects
                    # cingResonace.ccpn=ccpnShift, ccpnShift.cing=cinResonance
                    atom.resonances[index].ccpn = ccpnShift
                    ccpnShift.cing = atom.resonances[index]
                except:
                    NTwarning("_setShift: %s, shift CCPN atom %s skipped", ccpnResidue.cing, ccpnAtom.name)
                # end try
            # end for
        # end for
    
        NTdetail("==> CCPN ShiftList '%s' imported from Ccpn Nmr project '%s'",
                       ccpnShiftList.name, ccpnShiftList.parent.name)
        return True
    # end def _setShift
    
    def _setPeak(self):
        '''Descrn: Core function that sets peaks imported from Ccpn for a
                   Cing.Project and links to resonances.
           Inputs: Cing.Project instance, ccp.nmr.Nmr.NmrProject.
           Output: Cing.Project or None on error. Returns True if peaks found.
        '''
        done = False
    
        for ccpnExperiment in self.ccpnNmrProject.experiments:
            shiftList = ccpnExperiment.shiftList
            if not shiftList:
                NTwarning(" no shift list found for Ccpn.Experiment '%s'", ccpnExperiment.name)
    
            # sampled data dimensions?
            for ccpnDataSource in ccpnExperiment.dataSources:
                ccpnNumDim = ccpnDataSource.numDim
                for ccpnPeakList in ccpnDataSource.peakLists:
                    #Cing doen't like names with '|', like Aria does.
                    # TODO decide on better peakList naming and merge uniqueness check
                    plName = '%s_%s_%i' % (ccpnExperiment.name, ccpnDataSource.name, ccpnPeakList.serial)
                    peakListName = self._ensureValidName(plName, 'Peak')
                    peakListName = self.project.uniqueKey(peakListName)
    
                    pl = self.project.peaks.new(peakListName, status = 'keep')
    
                    pl.ccpn = ccpnPeakList
                    ccpnPeakList.cing = pl
    
                    for ccpnPeak in ccpnPeakList.peaks:
                        ccpnPeakDims = ccpnPeak.sortedPeakDims()
                        ccpnPositions = [pd.value for pd in ccpnPeakDims] #ppm
    
                        ccpnVolume = ccpnPeak.findFirstPeakIntensity(intensityType = 'volume')
                        if ccpnVolume:
                            vValue = ccpnVolume.value or 0.0
                            vError = ccpnVolume.error or 0.0
                        else:
                            vValue = 0.0
                            vError = 0.0
                        # end if
    
                        if str(vValue) == 'inf':
                            vValue = NaN
                        # end if
    
                        ccpnHeight = ccpnPeak.findFirstPeakIntensity(intensityType = 'height')
                        if ccpnHeight:
                            hValue = ccpnVolume.value or 0.0
                            hError = ccpnVolume.error or 0.0
                        else:
                            hValue = 0.0
                            hError = 0.0
                        # end if
                        if str(hValue) == 'inf':
                            hValue = NaN
                        # end if
    
                        if not (ccpnVolume or ccpnHeight):
                            NTwarning(" peak '%s' missing both volume and height", ccpnPeak)
    
                        resonances = []
                        for peakDim in ccpnPeakDims:
                            resonancesDim = []
                            for contrib in peakDim.peakDimContribs:
                                try:
                                    cingResonance = contrib.resonance.findFirstShift(parentList = shiftList).cing
                                    #print cingResonance.atom.format()
                                    #resonances.append(cingResonance)
                                    resonancesDim.append(cingResonance)
                                except:
                                    NTdebug('==== contrib out %s', contrib)
                                # end try
                            # end for
                            if resonancesDim:
                                # Taking only first resonance found
                                resonances.append(resonancesDim[0])
                                # debugging
                                #if len(resonancesDim) > 1:
                                #    print 'oooo ',len(resonancesDim)
                            else:
                                resonances.append(None)
                            # end if
                        # end for
                        #cingResonances = resonances
                        cingResonances = list(resonances)
                        #print "3@@@", len(cingResonances), vValue
    
                        peak = Peak(dimension = ccpnNumDim,
                                          positions = ccpnPositions,
                                          volume = vValue, volumeError = vError,
                                          height = hValue, heightError = hError,
                                          resonances = cingResonances)
    
                        peak.ccpn = ccpnPeak
                        ccpnPeak.cing = peak
    
                        # stuff PeakList with peaks imported from Ccpn
                        pl.append(peak)
                    # end for
    
                    NTdetail("==> PeakList '%s' imported from Ccpn Nmr project '%s'",
                                  peakListName, self.ccpnNmrProject.name)
                    done = True
                # end for
            # end for
        # end for
        if done: 
            return True
        return None # Just to be explicit on this.
    # end def _setPeak
    
    
    
    def importFromCcpnDistanceRestraint(self):
        '''Descrn: Import distance restraints from Ccpn.Project into Cing.Project.
                   As input either Cing.Project instance or Ccpn.Project instance,
                   or both, since it'll check if instances has attribute .ccpn or
                   .cing, respectively.
                   Molecules and Coordinates should be imported previouly.
           Inputs: Ccpn Implementation.Project, Cing.Project instance.
           Output: Cing.DistanceRestraintList or None on error.
        '''
    
        funcName = self.importFromCcpnDistanceRestraint.func_name
        listOfDistRestList = []
#        mapDistListType = { self.CC: 'DistRestraint', 'HBondConstraintList': 'HbondRestraint'}
        
        # map to CING names were possible note the presence of DistanceRestraintList.Hbond
        mapDistListType = { self.CCPN_DISTANCE_CONSTRAINT_LIST: DR_LEVEL, self.CCPN_HBOND_CONSTRAINT_LIST: HBR_LEVEL}
        
        msgHoL = MsgHoL()
#        msgHoL.appendDebug("Let's start off with one")
        for distListType in mapDistListType.keys(): # loop over regular distance and hydrogen bond restraints.
            distType = mapDistListType[distListType]
            # loop over all constraint stores
            for ccpnConstraintStore in self.ccpnNmrProject.nmrConstraintStores:
                ccpnDistanceListOfList = ccpnConstraintStore.findAllConstraintLists(className = distListType)
                
                for ccpnDistanceList in ccpnDistanceListOfList:
                    ccpnDistanceListName = self._ensureValidName(ccpnDistanceList.name, distType)
                    distanceRestraintList = self.project.distances.new(ccpnDistanceListName, status = 'keep')
        
                    ccpnDistanceList.cing = distanceRestraintList
                    distanceRestraintList.ccpn = ccpnDistanceList
        
#                    for ccpnDistanceConstraint in ccpnDistanceList.sortedConstraints():
                    for ccpnDistanceConstraint in ccpnDistanceList.sortedConstraints():
                        result = getRestraintBoundList(ccpnDistanceConstraint, Ccpn.RESTRAINT_IDX_DISTANCE, msgHoL)
                        if not result:
                            msgHoL.appendMessage("%s: Ccpn %s restraint '%s' with bad distances imported." % (funcName, distType, ccpnDistanceConstraint))
                            result = (None, None)
                        lower, upper = result
        
                        atomPairList = self._getConstraintAtomPairList(ccpnDistanceConstraint)
        
                        if not atomPairList:
                            # restraints that will not be imported
                            msgHoL.appendMessage("%s: skipped Ccpn %s restraint '%s' without atom pairs" % (funcName, distType, ccpnDistanceConstraint))
                            continue
                        # end if
        
                        distanceRestraint = DistanceRestraint(atomPairList, lower, upper)
        
                        distanceRestraint.ccpn = ccpnDistanceConstraint
                        ccpnDistanceConstraint.cing = distanceRestraint
        
                        distanceRestraintList.append(distanceRestraint)
                    # end for
                    listOfDistRestList.append(distanceRestraintList)
                    if distanceRestraintList.simplify():
                         NTerror("Failed to simplify the distanceRestraintList")
                # end for
            # end for
        # end for dist types.
        msgHoL.showMessage()
        return listOfDistRestList
    # end def importFromCcpnDistanceRestraint
    
    
    def importFromCcpnDihedralRestraint(self):
        '''Descrn: Import dihedral restraints from Ccpn.Project into Cing.Project.
                   As input either Cing.Project instance or Ccpn.Project instance,
                   or both, since it'll check if instances has attribute .ccpn or
                   .cing, respectively.
                   Molecules and Coordinates should be imported previouly.
           Inputs: Ccpn Implementation.Project, Cing.Project instance.
           Output: Cing.DihedralRestraintList or None on error.
        '''
        
        # it should be done only if Ccpn.Project has dihedral constraints
        molSysTorsions = {}
        for molSystem in self.ccpnProject.molSystems:
            molSysTorsions[molSystem] = createMoleculeTorsionDict(molSystem)
        # end for
    
        listOfDihRestList = []
        msgHoL = MsgHoL()
        # loop over all constraint stores
        for ccpnConstraintStore in self.ccpnNmrProject.nmrConstraintStores:
    
            for ccpnDihedralList in ccpnConstraintStore.findAllConstraintLists(className = self.CCPN_DIHEDRAL_CONSTRAINT_LIST):
                ccpnDihedralListName = self._ensureValidName(ccpnDihedralList.name, AC_LEVEL)
    
                dihedralRestraintList = self.project.dihedrals.new(ccpnDihedralListName, status = 'keep')
    
                ccpnDihedralList.cing = dihedralRestraintList
                dihedralRestraintList.ccpn = ccpnDihedralList
    
                for ccpnDihedralConstraint in ccpnDihedralList.sortedConstraints():
                    # TODO merge (dilute) ambig dihedrals
                    dihConsItem = ccpnDihedralConstraint.findFirstItem()
    
                    result = getRestraintBoundList(dihConsItem, self.RESTRAINT_IDX_DIHEDRAL, msgHoL)
    #                [None, None] evaluates to True
                    if not result:
                        NTdetail("Ccpn dihedral restraint '%s' with bad values imported." % ccpnDihedralConstraint)
                        result = (None, None)
    
                    lower, upper = result
                    atoms = self._getConstraintAtomList(ccpnDihedralConstraint)
                    if not atoms:
                        NTdetail("Ccpn dihedral restraint '%s' without atoms will be skipped" % ccpnDihedralConstraint)
                        continue
    
                    dihedralRestraint = DihedralRestraint(atoms, lower, upper)
                    dihedralRestraintList.append(dihedralRestraint)
    
                    dihedralRestraint.ccpn = ccpnDihedralConstraint
                    ccpnDihedralConstraint.cing = dihedralRestraint
                # end for
                listOfDihRestList.append(dihedralRestraintList)
            # end for
        # end for
        msgHoL.showMessage()
        return listOfDihRestList
    # end def importFromCcpnDihedralRestraint
    
    def importFromCcpnRdcRestraint(self):
        '''Descrn: Import RDC restraints from Ccpn.Project into Cing.Project.
                   As input either Cing.Project instance or Ccpn.Project instance,
                   or both, since it'll check if instances has attribute .ccpn or
                   .cing, respectively.
                   Molecules and Coordinates should be imported previously.
           Inputs: Ccpn Implementation.Project, Cing.Project instance.
           Output: Cing.RdcRestraintList or None on error.
        '''
        listOfRdcRestList = []    
        
        msgHoL = MsgHoL()
        # loop over all constraint stores
        for ccpnConstraintStore in self.ccpnNmrProject.nmrConstraintStores:
    
            for ccpnRdcList in ccpnConstraintStore.findAllConstraintLists(className = self.CCPN_RDC_CONSTRAINT_LIST):
                ccpnRdcListName = self._ensureValidName(ccpnRdcList.name, RDC_LEVEL)
    
                rdcRestraintList = self.project.rdcs.new(ccpnRdcListName, status = 'keep')
    
                ccpnRdcList.cing = rdcRestraintList
                rdcRestraintList.ccpn = ccpnRdcList
    
                for ccpnRdcConstraint in ccpnRdcList.sortedConstraints():
                    result = getRestraintBoundList(ccpnRdcConstraint, self.RESTRAINT_IDX_RDC, msgHoL)
                    if not result:
                        NTdetail("Ccpn RDC restraint '%s' with bad values imported." % 
                                  ccpnRdcConstraint)
                        result = (None, None)
                    lower, upper = result
                    
                    atomPairList = self._getConstraintAtomPairList(ccpnRdcConstraint)
    
                    if not atomPairList:
                        # restraints that will not be imported
                        NTdetail("Ccpn RDC restraint '%s' without atom pairs will be skipped" % ccpnRdcConstraint)
                        continue
                    # end if
    
                    rdcRestraint = RDCRestraint(atomPairList, lower, upper)
    
                    rdcRestraint.ccpn = ccpnRdcConstraint
                    ccpnRdcConstraint.cing = rdcRestraint
    
                    rdcRestraintList.append(rdcRestraint)
                # end for
                listOfRdcRestList.append(rdcRestraintList)
            # end for
        # end for
        msgHoL.showMessage()
        return listOfRdcRestList
    # end def importFromCcpnRdcRestraint
    
    
    
    def _getConstraintAtomPairList(self, ccpnConstraint):
        """Descrn: Get the atoms that may be assigned to the constrained resonances.
           Inputs: NmrConstraint.AbstractConstraint.
           Output: List of Cing.Atoms, tupled Cing.Atoms pairs or [] for dihedrals and
           or None on error.
           JFD adds just to be clear the output is an atomPairList structured:
           [ ( a1, a2 ), 
             ( a3, a4), .. ] where a1 is an atom which may be a pseudo atom. a1 may not be
           a set of atoms such as is the case in the CCPN data model.: E.g.
           [ [ [a0, a1], [ a2 ] ], 
             [ [a3],[a4]]] will first be translated below to CING:
           [ ( a0, a2 ), 
             ( a1, a2 ), 
             ( a3, a4), .. ]
            Later the code in the standard CING api will be tried to compress the structure if
            a0 and a1 can be represented by a pseudo of some sort.
            
            Basically, this is because a resonance in CCPN can represent several atoms.
             
           Note that pseudo atoms are collapsed from CCPN to CING for those and only those
           cases were the FC has expanded them. I.e. Issue 1 in the nmrrestrntsgrid project.
           
Original data: HG* is nicest to be written QG instead of writing it as a
ambi.

1 2 1 1 1 14 VAL MG1 1 171 VALn HG* 1 1
1 2 2 1 1 14 VAL HA 1 171 VALn HA 1 1
1 3 1 1 1 14 VAL MG2 1 171 VALn HG* 1 1
1 3 2 1 1 14 VAL HA 1 171 VALn HA 1 1      

Note that this doesn't happen with other pseudos. Perhaps CCPN does not have the pseudo?    
        """
    
        # for speed reasons put this debug info in block.
#        if cing.verbosity >= cing.verbosityDebug:
        if False:
            #        # Example code from Wim is a nice demonstration.
            lowerLimit = None
            upperLimit = None
            if hasattr(ccpnConstraint, 'lowerLimit'):
                lowerLimit = ccpnConstraint.lowerLimit
                upperLimit = ccpnConstraint.upperLimit
            NTdebug( 'Constraint [%d]: [%s] - [%s]' % (
                ccpnConstraint.serial, 
                val2Str(lowerLimit, '%.1f'), 
                val2Str(upperLimit, '%.1f'))) # Deals with None.
            for constItem in ccpnConstraint.sortedItems():
                atomList = []
                # Sometimes there may also be an ordered<Class> method.
                resonanceList = None
                if hasattr(constItem, 'orderedResonances'): # dihedrals don't have this.
                    resonanceList = constItem.orderedResonances    
                # Otherwise, use the usual sorted<Class> method.
                if not resonanceList:
                    resonanceList = constItem.sortedResonances()
                # Here, resonanceList should always have 2 resonances.
                assert(len(resonanceList) == 2)
                for resonance in resonanceList:
                    resAtomList = []
                    resonanceSet = resonance.resonanceSet
                    if resonanceSet:                                        
                        for atomSet in resonanceSet.sortedAtomSets():
                            for atom in atomSet.sortedAtoms():
                                resAtomList.append('%d.%s' % (
                                    atom.residue.seqCode, atom.name))
                    else:
                        NTwarning("No resonanceSet (means unassigned) for ccpnConstraint %s" % ccpnConstraint)
                    resAtomList.sort()
                    resAtomString = ','.join(resAtomList)
                    atomList.append(resAtomString)
                NTdebug('  [%s] - [%s]' % (atomList[0], atomList[1]))
            NTdebug('')

        # Now the real code.
        atomPairList = []
        atomPairSet = set()
        fixedResonanceListOfList = []

        for constItem in ccpnConstraint.sortedItems():
            # JFD from WV. Tries to use sorted items where available.
            fixedResonanceListOfList.append(getResonancesFromPairwiseConstraintItem(constItem)) 

#        NTdebug("fixedResonanceListOfList: %s" % fixedResonanceListOfList)
        for fixedResonanceList in fixedResonanceListOfList:
#            NTdebug("  fixedResonanceList: %s" % fixedResonanceList)
            # JFD Normally would use less levels of loops here but just to figure out how it's done it's nicer to spell it out.
            fixedResonanceSetLeft = fixedResonanceList[0].resonanceSet 
            fixedResonanceSetRight = fixedResonanceList[1].resonanceSet 
            if not fixedResonanceSetLeft:
                NTdebug("Failed to find fixedResonanceSet Left for ccpnConstraint %s" % ccpnConstraint)
                return None
            if not fixedResonanceSetRight:
                NTdebug("Failed to find fixedResonanceSet Right for ccpnConstraint %s" % ccpnConstraint)
                return None
            fixedAtomSetListLeft = fixedResonanceSetLeft.sortedAtomSets()
            fixedAtomSetListRight = fixedResonanceSetRight.sortedAtomSets()
#            NTdebug("    fixedAtomSetListLeft  = %s" % fixedAtomSetListLeft)
#            NTdebug("    fixedAtomSetListRight = %s" % fixedAtomSetListRight)
            for fixedAtomSetLeft in fixedAtomSetListLeft:
#                NTdebug("      fixedAtomSetLeft: %s" % fixedAtomSetLeft)
                atomListLeft = []
                for ccpnAtomLeft in fixedAtomSetLeft.sortedAtoms():
#                    NTdebug("        ccpnAtom Left: %s" % ccpnAtomLeft)
                    if not hasattr(ccpnAtomLeft, 'cing'):
                        NTerror("No Cing ccpnAtomLeft obj equivalent for Ccpn atom: %s", ccpnAtomLeft)
                        return None
                    atomLeft = ccpnAtomLeft.cing
                    atomListLeft.append(atomLeft)
                if not atomLeft:
                    NTerror("Failed to find at least one atomLeft for ccpnConstraint %s" % ccpnConstraint)
                    return None
                pseudoAtomLeft = atomLeft.getRepresentativePseudoAtom(atomListLeft)
                if pseudoAtomLeft: # use just the pseudo representative.
                    atomListLeft = [ pseudoAtomLeft ]
#                NTdebug("      atomListLeft: %s" % atomListLeft)
                for atomLeft in atomListLeft: 
#                    NTdebug("        atomLeft: %s" % atomLeft)
                    for fixedAtomSetRight in fixedAtomSetListRight:
#                        NTdebug("          fixedAtomSetRight: %s" % fixedAtomSetRight)
                        atomListRight = []
                        for ccpnAtomRight in fixedAtomSetRight.sortedAtoms():
#                            NTdebug("                ccpnAtom Right: %s" % ccpnAtomRight)
                            if not hasattr(ccpnAtomRight, 'cing'):
                                NTerror("No Cing ccpnAtomRight obj equivalent for Ccpn atom: %s", ccpnAtomRight)
                                return None
                            atomRight = ccpnAtomRight.cing
                            atomListRight.append(atomRight)
                        if not atomRight:
                            NTerror("Failed to find at least one atomRight for ccpnConstraint %s" % ccpnConstraint)
                            return None
                        pseudoAtomRight = atomRight.getRepresentativePseudoAtom(atomListRight)
                        if pseudoAtomRight: # use just the pseudo representative.
                            atomListRight = [ pseudoAtomRight ]
#                        NTdebug("          atomListRight: %s" % atomListRight)
                        for atomRight in atomListRight:
                            atomPair = (atomLeft, atomRight) 
#                            NTdebug("            atomPair: %s %s" % atomPair)
                            if atomPair in atomPairSet:
#                                NTdebug("Skipping pair already represented.")
                                continue 
                            atomPairSet.add(atomPair)
                            atomPairList.append(atomPair)
#        NTdebug("_getConstraintAtomPairList: %s" % atomPairList)
        return atomPairList

    def _getConstraintAtomList(self, ccpnConstraint):
        """ Use this routine instead of the above for dihedrals and chem shifts.
        Descrn: Get the atoms that may be assigned to the constrained resonances.
       Inputs: NmrConstraint.AbstractConstraint.
       Output: List of Cing.Atoms, tupled Cing.Atoms pairs or []."""

        atoms = set()
        fixedResonances = []
        className = ccpnConstraint.className
    
        if className == self.CCPN_DIHEDRAL_CONSTRAINT:
            fixedResonances.append(ccpnConstraint.resonances)
        elif className == self.CCPN_CS_CONSTRAINT:
            fixedResonances.append([ccpnConstraint.resonance, ])
        else:
            NTcodeerror("Routine _getConstraintAtomList should only be called for %s and %s" %(
               self.CCPN_DIHEDRAL_CONSTRAINT, self.CCPN_CS_CONSTRAINT))
            return None
        
        for fixedResonanceList in fixedResonances:
            atomList = []
            for fixedResonance in fixedResonanceList:
                fixedResonanceSet = fixedResonance.resonanceSet
    
                if fixedResonanceSet:
                    equivAtoms = {}
    
                    for fixedAtomSet in fixedResonanceSet.atomSets:
                        for atom in fixedAtomSet.atoms:
                            equivAtoms[atom] = True
                            if not hasattr(atom, 'cing'):
                                NTdebug("No Cing atom obj equivalent for Ccpn atom: %s", atom.name)
                    atomList.append(equivAtoms.keys())

            if len(atomList) == len(fixedResonanceList):
                try:
                    atoms = [ x[0].cing for x in atomList ]
                except:
                    NTdebug("No Cing atom obj equivalent for Ccpn atom list %s" % atomList)
        return list(atoms)
    # end def 
    
    
    def _ensureValidName(self, name, prefix = CING):
        '''Descrn: For checking string names from Ccpn.Project for objects like molecule, peak list, restraint list, etc.
                   If 'name' start with a digit, 'CING_' will prefix 'name'.
                   Cing doesn't like names starting with digits, spaces neither '|'.
           Inputs: a string 'name'.
           Output: same string 'name', 'prefix' + string 'name' or
                   just 'prefix' if 'name' = None'''
    
#        if not name: # JFD doesn't understand this line. Is name sometimes an empty string or so?
        if not name:
            name = prefix
            
        if name[0].isdigit():
            name = prefix + '_' + name
        else:
            name = prefix
        # end if
        
        name = name.replace('|', '_')
        name = name.replace(' ', '_')
        name = name.replace('.', '_')
        name = name.replace('+', '_')
    
        return name
    # end def _ensureValidName
# end class

def isDistanceOrHBondType(restraintTypeIdx):
    return restraintTypeIdx == Ccpn.RESTRAINT_IDX_DISTANCE or restraintTypeIdx == Ccpn.RESTRAINT_IDX_HBOND
 
def getRestraintBoundList(constraint, restraintTypeIdx, msgHoL):
    '''Descrn: Return upper and lower values for a Ccpn constraint.
       Inputs: Ccpn constraint.
       Output: floats (lower, upper) or None
       
       Mind you that CING only supports lower and upper bounds like cyana so far.
       
       In CCPN according to: file:///Users/jd/workspace34/ccpn/python/ccp/api/doc/nmr/NmrConstraint/DistanceConstraint/index.html
       none of the four is mandatory. 
       
       When CING wants access to more than lower/upper then this code needs to be updated.
       
       When the isDistanceRestraint is set to True then the result will be checked for the knowledge that 
       distance restraints should not have negative bounds.
       
       For full circle dihedral angle restraints derived from a error larger than 180. degrees:
       return: (0.0, -1.0E-9) which should be ok.
       
       Should report to msgHoL (a class MsgHoL)
    '''
    
    if not constraint:
        msgHoL.appendWarning("Restraint in CCPN was None") 
        return None
    
#    NTdebug(" CCPN: constraint.targetValue    %8s" % constraint.targetValue)
#    NTdebug(" CCPN: constraint.lowerLimit     %8s" % constraint.lowerLimit)
#    NTdebug(" CCPN: constraint.upperLimit     %8s" % constraint.upperLimit)
#    NTdebug(" CCPN: constraint.error          %8s" % constraint.error)
#    NTdebug(" CCPN: restraintTypeIdx          %8s" % restraintTypeIdx)
# wrong lowerbound in the following valid case.    
#constraint.targetValue         5.5
#constraint.lowerLimit          0.0
#constraint.upperLimit          5.5
#constraint.error              None
#lower, upper, targetValue, error (5.5, 5.5, 5.5, 0)    


    # only if all 3 items (except error value) are absent it is a bug.
    if (constraint.targetValue == None) and (constraint.lowerLimit == None) and (constraint.upperLimit == None):
        msgHoL.appendWarning("Restraint with all None for lower, upper and target")
        return None
    
    # Generate some warnings which might be helpful to a user because it should not be out of whack like this.
    # Perhaps this gets checked in ccpn api already?
    if isDistanceOrHBondType(restraintTypeIdx):
        if constraint.targetValue != None:
            if constraint.lowerLimit != None:
                if constraint.targetValue < constraint.lowerLimit:                 
                    msgHoL.appendWarning("Target value is below lower bound: [%s,%s]" % (constraint.targetValue, constraint.lowerLimit))
            if constraint.upperLimit != None:
                if constraint.targetValue > constraint.upperLimit:                 
                    msgHoL.appendWarning("Target value is above upper bound: [%s,%s]" % (constraint.targetValue, constraint.upperLimit))
        if (constraint.lowerLimit != None) and (constraint.upperLimit != None):
            if constraint.lowerLimit > constraint.upperLimit:                 
                msgHoL.appendWarning("Lower bound is above upper bound: [%s,%s]" % (constraint.lowerLimit, constraint.upperLimit))



        
    # two situations are common: l+u (cyana), t+l+u (xplor).
    # Mind you that only 3 parameters need to be given and then the fourth comes by definition.
    # By assuming the target value if unknown will be taken for the upper bound.
    # Perhaps None's or zero. Zero is taken as zero; which is different from None.
    # None means no information on the value. Zero means it's present. 
    lower = constraint.lowerLimit
    upper = constraint.upperLimit

    if (lower != None) and (upper != None):
        pass
#        NTdebug("Simplest case first for speed reasons.")
    else:    
        if constraint.targetValue == None:
            msgHoL.appendDebug("One or both of the two bounds are None but no target available to derive them. Lower/upper: [%s,%s]" % (lower, upper))
        else:    
            # When there is a target value and no lower or upper we will use a error of zero by default which makes
            # the range of their error zero in case the error was not defined. This is a reasonable assumption according
            # to JFD.
            error = constraint.error or 0
            if error < 0:                 
                msgHoL.appendError("Found error below zero; taking absolute value of error: " + `error`)
                error = - error
            if restraintTypeIdx == Ccpn.RESTRAINT_IDX_DIHEDRAL:
                if error > 180.:                 
                    msgHoL.appendWarning("Found dihedral angle restraint error above half circle; which means all's possible; translated well to CING: " + `error`)
                    return (0.0, - Ccpn.SMALL_FLOAT_FOR_DIHEDRAL_ANGLES)                
            
            if lower == None:
                msgHoL.appendDebug("Setting lower bound from target and (perhaps assumed error).")
                lower = constraint.targetValue - error
                
            if upper == None:
                msgHoL.appendDebug("Setting upper bound from target and (perhaps assumed error).")
                upper = constraint.targetValue + error
                
            
    if isDistanceOrHBondType(restraintTypeIdx):
        if (lower != None) and (upper != None):
            if lower > upper:                 
                msgHoL.appendError("Lower bound is above upper bound: [%s,%s]" % (lower, upper))
                msgHoL.appendError("Assuming CING prefers upper bound and thus unsetting lower bound as if unexisting; please check your data.")
                lower = None
        if (lower != None) and (lower < 0):
            msgHoL.appendWarning("Lower distance bound is negative assuming CING prefers to unset lower bound as if unexisting; please check your data.")
            lower = None
        if (upper != None) and (upper < 0):
            msgHoL.appendWarning("Upper distance bound is negative assuming CING prefers to unset lower bound as if unexisting; please check your data.")
            upper = None
            
    # Unfortunately, sometimes it would be nice to preserve the info on the range but can't be here.
    if restraintTypeIdx == Ccpn.RESTRAINT_IDX_DIHEDRAL:
        lower = NTlimitSingleValue(lower, - 180., 180.) # routine is ok with None input.
        upper = NTlimitSingleValue(upper, - 180., 180.)

    return (lower, upper)

def isRootDirectory(f):
    """ Algorithm for finding just the root dir.
    See unit test for examples.
    """
#    NTdebug("Checking _isRootDirectory on : ["+f+"]")
    idxSlash = f.find("/")
    if idxSlash < 0:
        NTerror("Found no forward slash in entry in tar file.")
        return None

    idxLastChar = len(f) - 1
    if idxSlash == idxLastChar or idxSlash == (idxLastChar - 1):
#        NTdebug("If the first slash is the last or second last BINGO: ["+f+"]")
        return True
    return False

def removeCcpnReferences(self):
    """To slim down the memory footprint; should allow garbage collection."""
    attributeToRemove = "ccpn"
    try:
        removeRecursivelyAttribute(self, attributeToRemove)
    except:
        NTerror("Failed removeCcpnReferences")

def initCcpn(project, ccpnFolder):
    '''Descrn: Adds to the Cing Project instance from a Ccpn folder project.
       Inputs: Cing.Project instance, Ccpn project XML file or a gzipped tar file such as .tgz or .tar.gz
       Output: Cing.Project or None on error.
    '''
    # work horse class.
    ccpn = Ccpn(project = project, ccpnFolder = ccpnFolder)
    if not ccpn.importFromCcpn():
        NTerror("Failed importFromCcpn")
        return None
    return project
    

# register the function
methods = [ (initCcpn, None),
           (removeCcpnReferences, None),
           ]
# Obtained by a grep on INTERNAL_0 file.
#    nameDict = {'BMRBd': 'RADE', 'IUPAC': 'A', 'AQUA': 'A', 'INTERNAL_0': 'RADE', 'INTERNAL_1': 'RADE', 'CYANA': 'RADE', 'CCPN': 'RNA A deprot:H1', 'PDB': 'RADE', 'XPLOR': 'RADE'}
#    nameDict = {'CCPN': 'DNA A deprot:H1', 'BMRBd': 'ADE', 'IUPAC': 'DA', 'AQUA': 'A', 'INTERNAL_0': 'ADE', 'INTERNAL_1': 'DA', 'CYANA': 'ADE', 'CYANA2': 'ADE', 'PDB': 'ADE', 'XPLOR': 'ADE'}
#    nameDict = {'CCPN': 'DNA C deprot:H3', 'BMRBd': 'CYT', 'IUPAC': 'DC', 'AQUA': 'C', 'INTERNAL_0': 'CYT', 'INTERNAL_1': 'DC', 'CYANA': 'CYT', 'CYANA2': 'CYT', 'PDB': 'CYT', 'XPLOR': 'CYT'}
#    nameDict = {'CCPN': 'DNA G prot:H1;deprot:H7', 'BMRBd': 'GUA', 'IUPAC': 'DG', 'AQUA': 'G', 'INTERNAL_0': 'GUA', 'INTERNAL_1': 'DG', 'CYANA': 'GUA', 'CYANA2': 'GUA', 'PDB': 'GUA', 'XPLOR': 'GUA'}
#    nameDict = {'CCPN': 'DNA T prot:H3', 'BMRBd': 'THY', 'IUPAC': 'DT', 'AQUA': 'T', 'INTERNAL_0': 'THY', 'INTERNAL_1': 'DT', 'CYANA': 'THY', 'CYANA2': 'THY', 'PDB': 'THY', 'XPLOR': 'THY'}
#    nameDict = {'CCPN': 'RNA C deprot:H3', 'BMRBd': 'RCYT', 'IUPAC': 'C', 'AQUA': 'C', 'INTERNAL_0': 'RCYT', 'INTERNAL_1': 'C', 'CYANA': 'RCYT', 'CYANA2': 'RCYT', 'PDB': 'RCYT', 'XPLOR': 'RCYT'}
#    nameDict = {'CCPN': 'RNA G prot:H1;deprot:H7', 'BMRBd': 'RGUA', 'IUPAC': 'G', 'AQUA': 'G', 'INTERNAL_0': 'RGUA', 'INTERNAL_1': 'G', 'CYANA': 'RGUA', 'CYANA2': 'RGUA', 'PDB': 'RGUA', 'XPLOR': 'RGUA'}
#    nameDict = {'CCPN': 'RNA U prot:H3', 'BMRBd': 'URA', 'IUPAC': 'U', 'AQUA': 'U', 'INTERNAL_0': 'URA', 'INTERNAL_1': 'U', 'CYANA': 'URA', 'CYANA2': 'URA', 'PDB': 'U', 'XPLOR': 'URA'}
#    nameDict = {'CCPN': 'other Hoh neutral', 'BMRBd': 'HOH', 'IUPAC': 'HOH', 'AQUA': 'HOH', 'INTERNAL_0': 'HOH', 'INTERNAL_1': 'HOH', 'CYANA': None, 'CYANA2': None, 'PDB': 'HOH', 'XPLOR': 'HOH'}
#    nameDict = {'CCPN': 'protein Ala neutral', 'BMRBd': 'ALA', 'IUPAC': 'ALA', 'AQUA': 'ALA', 'INTERNAL_0': 'ALA', 'INTERNAL_1': 'ALA', 'CYANA': 'ALA', 'CYANA2': 'ALA', 'PDB': 'ALA', 'XPLOR': 'ALA'}
#    nameDict = {'CCPN': 'protein Arg deprot:HH12', 'BMRBd': None, 'IUPAC': 'ARG', 'AQUA': 'ARG', 'INTERNAL_0': 'ARGx', 'INTERNAL_1': 'ARGx', 'CYANA': 'ARG', 'CYANA2': None, 'PDB': None, 'XPLOR': None}
#    nameDict = {'CCPN': 'protein Arg prot:HH12', 'BMRBd': 'ARG', 'IUPAC': 'ARG', 'AQUA': 'ARG', 'INTERNAL_0': 'ARG', 'INTERNAL_1': 'ARG', 'CYANA': 'ARG+', 'CYANA2': 'ARG', 'PDB': 'ARG', 'XPLOR': 'ARG'}
#    nameDict = {'CCPN': 'protein Asn neutral', 'BMRBd': 'ASN', 'IUPAC': 'ASN', 'AQUA': 'ASN', 'INTERNAL_0': 'ASN', 'INTERNAL_1': 'ASN', 'CYANA': 'ASN', 'CYANA2': 'ASN', 'PDB': 'ASN', 'XPLOR': 'ASN'}
#    nameDict = {'CCPN': 'protein Asp deprot:HD2', 'BMRBd': 'ASP', 'IUPAC': 'ASP', 'AQUA': 'ASP', 'INTERNAL_0': 'ASP', 'INTERNAL_1': 'ASP', 'CYANA': 'ASP-', 'CYANA2': 'ASP', 'PDB': 'ASP', 'XPLOR': 'ASP'}
#    nameDict = {'CCPN': 'protein Asp prot:HD2', 'BMRBd': 'ASP', 'IUPAC': 'ASP', 'AQUA': 'ASP', 'INTERNAL_0': 'ASPH', 'INTERNAL_1': 'ASPH', 'CYANA': 'ASP', 'CYANA2': None, 'PDB': 'ASP', 'XPLOR': None}
#    nameDict = {'CCPN': 'protein Cys deprot:HG', 'BMRBd': 'CYS', 'IUPAC': 'CYS', 'AQUA': 'CYS', 'INTERNAL_0': 'CYSS', 'INTERNAL_1': 'CYSS', 'CYANA': 'CYSS', 'CYANA2': 'CYSS', 'PDB': 'CYS', 'XPLOR': 'CYS'}
#    nameDict = {'CCPN': 'protein Cys prot:HG', 'BMRBd': 'CYS', 'IUPAC': 'CYS', 'AQUA': 'CYS', 'INTERNAL_0': 'CYS', 'INTERNAL_1': 'CYS', 'CYANA': 'CYS', 'CYANA2': 'CYS', 'PDB': 'CYS', 'XPLOR': 'CYS'}
#    nameDict = {'CCPN': 'protein Gln neutral', 'BMRBd': 'GLN', 'IUPAC': 'GLN', 'AQUA': 'GLN', 'INTERNAL_0': 'GLN', 'INTERNAL_1': 'GLN', 'CYANA': 'GLN', 'CYANA2': 'GLN', 'PDB': 'GLN', 'XPLOR': 'GLN'}
#    nameDict = {'CCPN': 'protein Glu deprot:HE2', 'BMRBd': 'GLU', 'IUPAC': 'GLU', 'AQUA': 'GLU', 'INTERNAL_0': 'GLU', 'INTERNAL_1': 'GLU', 'CYANA': 'GLU-', 'CYANA2': 'GLU', 'PDB': 'GLU', 'XPLOR': 'GLU'}
#    nameDict = {'CCPN': 'protein Glu prot:HE2', 'BMRBd': 'GLU', 'IUPAC': 'GLU', 'AQUA': 'GLU', 'INTERNAL_0': 'GLUH', 'INTERNAL_1': 'GLUH', 'CYANA': 'GLU', 'CYANA2': None, 'PDB': 'GLU', 'XPLOR': None}
#    nameDict = {'CCPN': 'protein Gly neutral', 'BMRBd': 'GLY', 'IUPAC': 'GLY', 'AQUA': 'GLY', 'INTERNAL_0': 'GLY', 'INTERNAL_1': 'GLY', 'CYANA': 'GLY', 'CYANA2': 'GLY', 'PDB': 'GLY', 'XPLOR': 'GLY'}
#    nameDict = {'CCPN': 'protein His prot:HD1,HE2', 'BMRBd': 'HIS', 'IUPAC': 'HIS', 'AQUA': 'HIS', 'INTERNAL_0': 'HISH', 'INTERNAL_1': 'HISH', 'CYANA': 'HIS+', 'CYANA2': 'HIS', 'PDB': 'HIS', 'XPLOR': 'HIS'}
#    nameDict = {'CCPN': 'protein His prot:HD1;deprot:HE2', 'BMRBd': 'HIS', 'IUPAC': 'HIS', 'AQUA': 'HIS', 'INTERNAL_0': 'HIS', 'INTERNAL_1': 'HIS', 'CYANA': 'HIS', 'CYANA2': 'HIS', 'PDB': 'HIS', 'XPLOR': 'HIS'}
#    nameDict = {'CCPN': 'protein His prot:HE2;deprot:HD1', 'BMRBd': 'HIS', 'IUPAC': 'HIS', 'AQUA': 'HIS', 'INTERNAL_0': 'HISE', 'INTERNAL_1': 'HISE', 'CYANA': 'HIST', 'CYANA2': 'HIST', 'PDB': 'HIS', 'XPLOR': 'HIS'}
#    nameDict = {'CCPN': 'protein Ile neutral', 'BMRBd': 'ILE', 'IUPAC': 'ILE', 'AQUA': 'ILE', 'INTERNAL_0': 'ILE', 'INTERNAL_1': 'ILE', 'CYANA': 'ILE', 'CYANA2': 'ILE', 'PDB': 'ILE', 'XPLOR': 'ILE'}
#    nameDict = {'CCPN': 'protein Leu neutral', 'BMRBd': 'LEU', 'IUPAC': 'LEU', 'AQUA': 'LEU', 'INTERNAL_0': 'LEU', 'INTERNAL_1': 'LEU', 'CYANA': 'LEU', 'CYANA2': 'LEU', 'PDB': 'LEU', 'XPLOR': 'LEU'}
#    nameDict = {'CCPN': 'protein Lys deprot:HZ3', 'BMRBd': None, 'IUPAC': 'LYS', 'AQUA': 'LYS', 'INTERNAL_0': 'LYSx', 'INTERNAL_1': 'LYSx', 'CYANA': 'LYS', 'CYANA2': None, 'PDB': None, 'XPLOR': None}
#    nameDict = {'CCPN': 'protein Lys prot:HZ3', 'BMRBd': 'LYS', 'IUPAC': 'LYS', 'AQUA': 'LYS', 'INTERNAL_0': 'LYS', 'INTERNAL_1': 'LYS', 'CYANA': 'LYS+', 'CYANA2': 'LYS', 'PDB': 'LYS', 'XPLOR': 'LYS'}
#    nameDict = {'CCPN': 'protein Met neutral', 'BMRBd': 'MET', 'IUPAC': 'MET', 'AQUA': 'MET', 'INTERNAL_0': 'MET', 'INTERNAL_1': 'MET', 'CYANA': 'MET', 'CYANA2': 'MET', 'PDB': 'MET', 'XPLOR': 'MET'}
#    nameDict = {'CCPN': 'protein Phe neutral', 'BMRBd': 'PHE', 'IUPAC': 'PHE', 'AQUA': 'PHE', 'INTERNAL_0': 'PHE', 'INTERNAL_1': 'PHE', 'CYANA': 'PHE', 'CYANA2': 'PHE', 'PDB': 'PHE', 'XPLOR': 'PHE'}
#    nameDict = {'CCPN': 'protein Pro neutral', 'BMRBd': 'PRO', 'IUPAC': 'PRO', 'AQUA': 'PRO', 'INTERNAL_0': 'PRO', 'INTERNAL_1': 'PRO', 'CYANA': 'PRO', 'CYANA2': 'PRO', 'PDB': 'PRO', 'XPLOR': 'PRO'}
#    nameDict = {'CCPN': 'protein Ser prot:HG', 'BMRBd': 'SER', 'IUPAC': 'SER', 'AQUA': 'SER', 'INTERNAL_0': 'SER', 'INTERNAL_1': 'SER', 'CYANA': 'SER', 'CYANA2': 'SER', 'PDB': 'SER', 'XPLOR': 'SER'}
#    nameDict = {'CCPN': 'protein Thr prot:HG1', 'BMRBd': 'THR', 'IUPAC': 'THR', 'AQUA': 'THR', 'INTERNAL_0': 'THR', 'INTERNAL_1': 'THR', 'CYANA': 'THR', 'CYANA2': 'THR', 'PDB': 'THR', 'XPLOR': 'THR'}
#    nameDict = {'CCPN': 'protein Trp prot:HE1', 'BMRBd': 'TRP', 'IUPAC': 'TRP', 'AQUA': 'TRP', 'INTERNAL_0': 'TRP', 'INTERNAL_1': 'TRP', 'CYANA': 'TRP', 'CYANA2': 'TRP', 'PDB': 'TRP', 'XPLOR': 'TRP'}
#    nameDict = {'CCPN': 'protein Tyr prot:HH', 'BMRBd': 'TYR', 'IUPAC': 'TYR', 'AQUA': 'TYR', 'INTERNAL_0': 'TYR', 'INTERNAL_1': 'TYR', 'CYANA': 'TYR', 'CYANA2': 'TYR', 'PDB': 'TYR', 'XPLOR': 'TYR'}
#    nameDict = {'CCPN': 'protein Val neutral', 'BMRBd': 'VAL', 'IUPAC': 'VAL', 'AQUA': 'VAL', 'INTERNAL_0': 'VAL', 'INTERNAL_1': 'VAL', 'CYANA': 'VAL', 'CYANA2': 'VAL', 'PDB': 'VAL', 'XPLOR': 'VAL'}

def patchCcpnResDescriptor(ccpnResDescriptor, ccpnMolType, ccpnLinking):
    # CING db has only non-terminal CCPN descriptors in DB so CING can be more concise.
    ccpnResDescriptorList = NTlist()
    ccpnResDescriptorList.addList(ccpnResDescriptor.split(';'))
#    NTdebug("ccpnResDescriptorList: %s " % ccpnResDescriptorList)
    if ccpnLinking == Ccpn.CCPN_START:
        if ccpnMolType == Ccpn.CCPN_PROTEIN:
            ccpnResDescriptorList.removeIfPresent(Ccpn.CCPN_PROT_H3)
    if ccpnLinking == Ccpn.CCPN_END:
        if ccpnMolType == Ccpn.CCPN_PROTEIN:
            ccpnResDescriptorList.removeIfPresent(Ccpn.CCPN_DEPROT_H_DOUBLE_PRIME)
    # Didn't find anything specific for RNA/DNA in Analysis windows on examples 1ai0, 1cjg, and 1a4d.

    # Note that in 1brv's CCPN this Cys is listed as 'deprot:HG' whereas CING has: 'link:SG'
    # Fixed in lib now.  
#    if ccpnMolType == Ccpn.CCPN_PROTEIN:
#        ccpnResDescriptorList.replaceIfPresent(Ccpn.CCPN_DEPROT_HG, Ccpn.CCPN_LINK_SG )
    
    if not len(ccpnResDescriptorList):
        ccpnResDescriptorList.add(Ccpn.CCPN_NEUTRAL)
#    NTdebug("ccpnResDescriptorList: %s " % ccpnResDescriptorList)
    ccpnResDescriptorPatched = string.join(ccpnResDescriptorList, ';')
    return ccpnResDescriptorPatched
