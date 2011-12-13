'''
Collaborative Computing Project for NMR 
'''
from cing import issueListUrl
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.disk import isRootDirectory
from cing.Libs.forkoff import do_cmd
from cing.core.classes import DihedralRestraint
from cing.core.classes import DistanceRestraint
from cing.core.classes import Peak
from cing.core.classes import Project
from cing.core.classes import RDCRestraint
from cing.core.classes2 import ResonanceList
from cing.core.constants import * #@UnusedWildImport
from cing.core.database import NTdb
from cing.core.molecule import Molecule
from cing.core.molecule import unmatchedAtomByResDictToString
from shutil import move
from shutil import rmtree
import shutil
import string
import tarfile

if True: # for easy blocking of data, preventing the code to be resorted with imports above.
    from cing.PluginCode.required.reqCcpn import * #@UnusedWildImport
    switchOutput(False)
    try:
        import ccpnmr #@UnusedImport
        from ccp.general.Util import createMoleculeTorsionDict
        from ccp.general.Util import getResonancesFromPairwiseConstraintItem
        from ccp.util.Molecule import makeMolecule
        from ccp.util.Molecule import setMolResidueChemCompVar
        from ccp.util.Validation import getEnsembleValidationStore
        from ccp.util.Validation import getResidueValidation
        from memops.api.Implementation import MemopsRoot
        from memops.api.Implementation import AppDataString
        from memops.general.Io import loadProject
    except:
        switchOutput(True)
        raise ImportWarning(CCPN_STR)
#        raise SkipTest(CCPN_STR)        
    finally: # finally fails in python below 2.5
        switchOutput(True)
#    nTmessage('Using Ccpn')

class Ccpn:
    """
        Adds initialize from CCPN project files
        Class to accommodate a ccpn project and import it into a CING project instance
    
        Steps:
        - Parse the ccpn file using the CCPN api
        - Import the coordinates.
        - Import the experimental data.
    
        The allowNonStandardResidue determines if the non-standard residues and atoms are read. If so they will be shown as
        a regular message. Otherwise they will be shown as a warning. Just like MolMol does; the unknown atoms per residue.
    """
#    nTdebug("Using CCPN version %s" % currentModelVersion)

    SMALL_FLOAT_FOR_DIHEDRAL_ANGLES = 1.e-9

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

    CCPN_CS_LIST = 'ShiftList'

    CCPN_RUN_MEASUREMENT = 'MeasurementListData'
    CCPN_RUN_CONSTRAINT = 'ConstraintStoreData'
    CCPN_RUN_STRUCTURE = 'StructureEnsembleData'
    CCPN_RUN_RESIDUE = 'MolResidueData'
    CCPN_RUN_PEAK = 'PeakListData'
    
    CCPN_CLASSNAME_STR = 'className'

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

    CCPN_CING_RUN = 'cingRun'
    CCPN_CING_ATR = 'cing'
    CING_CCPN_ATR = 'ccpn'

    def __init__(self, project, ccpnFolder, convention = IUPAC, patchAtomNames = True,
                 skipWaters = False, allowNonStandardResidue = True):
        self.project = project
        self.ccpnProject = None # set in readCcpnFolder
        self.ccpnMolSystemList = None # set in importFromCcpnMolecule
        self.ccpnNmrProject = None # set in importFromCcpnMolecule
        self.ccpnNmrConstraintStore = None
        self.ccpnConstraintLists = None
        self.ccpnCingRun = None # set in importFromCcpnMolecule
        self.molecule = None # set in importFromCcpn ( importFromCcpnMolecule )
        project.ccpnFolder = ccpnFolder # Needed to store for conversion from ccpn to star.
        self.convention = convention
        self.patchAtomNames = patchAtomNames
        self.skipWaters = skipWaters
        self.allowNonStandardResidue = allowNonStandardResidue

    def _getCcpnRestraintLoL(self, allCcpnConstraintLists, classNames):
        """Descrn: Function to get a list of CCPN restraint lists given an
                   input list of CCPN Nmr Constraint Stores (containers for
                   the lists) and a list of class name to specify which
                   types of restraint list are sought (e.g. 'DistanceRestraintList'
                   or 'DihedralRestraintList')
           Inputs: List of CCPN NmrConstraint.NmrConstraintStore, List of Words
           Output: List of CCPN NmrConstraint.AbstractConstraintLists
        """

        ccpnRestraintLists = []
        for ccpnRestraintList in allCcpnConstraintLists:
            className = getDeepByKeysOrAttributes(ccpnRestraintList, self.CCPN_CLASSNAME_STR)
            if className == None:
                nTwarning("Failed to find className for ccpnRestraintList: %s. Skipping import of it." % str(ccpnRestraintList))
                continue
            if className in classNames:
                ccpnRestraintLists.append(ccpnRestraintList)
        return ccpnRestraintLists

    def readCcpnFolder(self):
        """Return ccpnProject on success or None on failure"""
        if not self.project.ccpnFolder:
            nTerror("No ccpnFolder")
            return None

        if os.path.exists(self.project.ccpnFolder) and os.path.isfile(self.project.ccpnFolder) and (\
            self.project.ccpnFolder.endswith(".tgz") or self.project.ccpnFolder.endswith(".tar.gz")):
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
            tar = tarfile.open(self.project.ccpnFolder, "r:gz")
            tarFileNames = []
            for itar in tar:
#                nTdebug("working on: " + itar.name)
                if os.path.exists(itar.name):
                    nTerror("Will not untar %s by overwriting current copy" % itar.name)
                    return None
                # Omit files like AR3436A/._ccp from projects obtained from Wim.
                if itar.name.count('._'):
#                    nTdebug("Skipping special hidden file: " + itar.name)
                    continue
                tar.extract(itar.name, '.') # itar is a TarInfo object
                # Try to match: BASP/memops/Implementation/BASP.xml
                if not ccpnRootDirectory: # pick only the first one.
                    tarFileNames.append(itar.name)
                    if isRootDirectory(itar.name):
                        ccpnRootDirectory = itar.name.replace("/", '')
                        if not ccpnRootDirectory:
                            nTerror("Skipping potential ccpnRootDirectory")
            tar.close()
            if not ccpnRootDirectory:
                # in python 2.6 tarfile class doesn't append '/' in root dir anymore
                # sorting by length and taking the shortest, likely the root dir.
                tarFileNames.sort()
                ccpnRootDirectory = tarFileNames[0]
                if not os.path.isdir(ccpnRootDirectory):
                    nTerror("No ccpnRootDirectory found in gzipped tar file: %s" % self.project.ccpnFolder)
                    nTerror("First listed directory after sorting: %s" % ccpnRootDirectory)
                    return None
                # end if
            # end if
            if ccpnRootDirectory != self.project.name:
                nTmessage("Moving CCPN directory from [%s] to [%s]" % (ccpnRootDirectory, self.project.name))
                move(ccpnRootDirectory, self.project.name)
            ccpnFolder = self.project.name # Now it is a folder.
        else:
            ccpnFolder = self.project.ccpnFolder

        if (not ccpnFolder) or (not os.path.exists(ccpnFolder)):
            nTerror("ccpnFolder '%s' not found", ccpnFolder)
            return None
        # end if

        self.project.ccpnFolder = os.path.abspath(ccpnFolder)

        switchOutput(False) # let's skip the note on stdout of changed hard-coded directories
        self.ccpnProject = loadProject(ccpnFolder)
        switchOutput(True)
        if not self.ccpnProject:
            nTerror(" ccpn project from folder '%s' not loaded", ccpnFolder)
            return None

        # Make mutual linkages between Ccpn and Cing objects
        self.project.ccpn = self.ccpnProject
        self.ccpnProject.cing = self.project
            # end if

        # Unless the below attr exists CING wont try to pick up CCPN NmrCalc settings
        self.ccpnProject.cingRun = None

        return self.project
    # end def initCcpn

    def _getCcpnMolSystemList(self, moleculeName = None):
        """Descrn: Internal function to set the molecular systems
                   in a CCPN project which are subject to analysis
                   by Cing, and create equivalent Molecule instances
                   where none exist.
                   Inputting a molecule name will only fetch and check
                   molecules with that name.
                   If no name is input any Cing calculation run already
                   setup inside the CCPN project will be used to
                   specify the relevant molecules.
           Inputs: CCPN Implementation.MemopsRoot, String, String
           Output: None for error; True for success.
        """

        ccpnMolSystemList = []

        ccpnCalc = self.ccpnCingRun
        ccpnMolSystem = None
        if ccpnCalc: # Fails for NRG-CING but a nice feature for use from within Analysis etc.
            # Mol System is the one associated with chosen structure
            structureData = ccpnCalc.findFirstData(className = self.CCPN_RUN_STRUCTURE, ioRole = 'input')
            if structureData:            
#              ccpnMolSystem = structureData.structureEnsemble.molSystem 
# Fails for Ulrich Schwartz's project that has no attribute molSystem
                ccpnMolSystem = getDeepByKeysOrAttributes(structureData, 'structureEnsemble', 'molSystem')
                if not ccpnMolSystem:
                    nTwarning("Found the unusual case of having structureData but no molSystem in structureData.structureEnsemble")
                #end if
            #end if
        #end if
        # Determine which CCPN molSystems to work with
        if moleculeName and ccpnMolSystem:
            if ccpnMolSystem and (ccpnMolSystem.code != moleculeName):
                msg = " Clash between specified molecule name (%s) and molecular"
                msg += " system specified in CCPN calculation object (%s)."
                msg += " Remove either specification or make them consistent."
                nTerror(msg, moleculeName, ccpnMolSystem.code)
                return None
            ccpnMolSystemList = [ccpnMolSystem, ]
        elif ccpnMolSystem:
            ccpnMolSystemList = [ccpnMolSystem, ]
        elif moleculeName:
            ccpnMolSystemList = [self.ccpnProject.findFirstMolSystem(code = moleculeName), ]
        else:
            ccpnMolSystemList = self.ccpnProject.sortedMolSystems()


        if not ccpnMolSystemList:
            nTerror("No molecular systems found in CCPN project")
            return None

        self.ccpnMolSystemList = ccpnMolSystemList
        return True


    def _getCcpnNmrProject(self):
        '''Descrn: Check which list of ccpnMolSystem to return.
           Inputs: Cing.Project, function name.
           Output: True, None on error.
        '''
        # Taking only one NmrProject for the moment
        if self.ccpnProject.currentNmrProject:
            ccpnNmrProject = self.ccpnProject.currentNmrProject
        elif self.ccpnProject.nmrProjects:
            ccpnNmrProject = self.ccpnProject.findFirstNmrProject()
        self.ccpnNmrProject = ccpnNmrProject
        return True


    def importFromCcpn(self, modelCount = None):
        '''Descrn: Import data from Ccpn into a Cing instance.
                   Check if either instance has attribute .cing or .ccpn,
                   respectively.
           Inputs: Ccpn Implementation.Project, Cing.Project instance.
           When modelCount is not None it will limit the number of models imported.
           Output: None on error.
        '''

        if not self.readCcpnFolder():
            nTerror("Failed readCcpnFolder")
            return None

        nTmessage('==> Importing data from Ccpn project "%s"', self.ccpnProject.name)

        if not self.importFromCcpnMolecule(modelCount = modelCount):
            nTerror("Failed to importFromCcpnMolecule")
            return None


        if self.importFromCcpnPeakAndShift():
#            nTdebug('Finished importFromCcpnPeakAndShift')
            pass
        else:
            nTerror("Failed to importFromCcpnPeakAndShift")
            return None
        if self.importFromCcpnDistanceRestraint():
#            nTdebug('Finished importFromCcpnDistanceRestraint')
            pass
        else:
            nTerror("Failed to importFromCcpnDistanceRestraint")
            return None
        if not self.importFromCcpnDistMetaData():
#            nTdebug('Finished importFromCcpnDistMetaData')
            pass
        else:
            nTerror("Failed to importFromCcpnDistMetaData")
            return None
        if self.importFromCcpnDihedralRestraint():
#            nTdebug('Finished importFromCcpnDihedralRestraint')
            pass
        else:
            nTerror("Failed to importFromCcpnDihedralRestraint")
            return None
        if self.importFromCcpnRdcRestraint():
#            nTdebug('Finished importFromCcpnRdcRestraint')
            pass
        else:
            nTerror("Failed to importFromCcpnRdcRestraint")
            return None

        nTmessage('==> Ccpn project imported')

        self.project.addHistory(sprintf('Imported CCPN project'))
        self.project.updateProject()

        return True # To distinguish success from failure.
    # end def importFromCcpn

    def isNonDescriptiveMolSysDefault(self, name):
        name = name.replace('_', '')
        name = name.lower()
        if name.find("molecularsystem") >= 0:
            return True
        return False

    def importFromCcpnMolecule(self, modelCount = None):
        '''Descrn: Import MolSystems (Molecules) from Ccpn.Project instance and
                   append it to Cing.Project instance, including chains, residues
                   and atoms.
                   As input either Cing.Project instance or Ccpn.Project instance,
                   or both, since it'll check if instances has attribute .ccpn or
                   .cing, respectively.
           When modelCount is not None it will limit the number of models imported.
           Output: True or None on error.
        '''

        if hasattr(self.ccpnProject, self.CCPN_CING_RUN): # Fails for NRG-CING but a nice feature for use from within Analysis etc.
            nmrCalcStore = self.ccpnProject.findFirstNmrCalcStore(name='CING')
            if nmrCalcStore:
                run = nmrCalcStore.findFirstRun(status='pending') or nmrCalcStore.findFirstRun()

            else:
                run = None

            self.ccpnCingRun = ccpnCalc = run
            self.ccpnProject.cingRun = run

            if run:
                runText = '%s:%s' % (nmrCalcStore.name, run.serial)
                nTmessage('==> Using run specification "%s" from CCPN project', runText)
        else:
            self.ccpnCingRun = ccpnCalc = None


        if not self._getCcpnMolSystemList():
            nTerror("Failed to _getCcpnMolSystemList")
            return None

        if not self._getCcpnNmrProject():
            nTerror("Failed to _getCcpnNmrProject")
            return None

        # Get the appropriate NMR constraint lists
        ccpnConstraintLists = []
        if ccpnCalc: # Fails for NRG-CING but a nice feature for use from within Analysis etc.
            ccpnConstraintLists = set() # Repeats technically possible
            for constraintData in ccpnCalc.findAllData(className = self.CCPN_RUN_CONSTRAINT, ioRole = 'input'):
                ccpnConstraintLists.update(constraintData.constraintLists)
            ccpnConstraintLists = list(ccpnConstraintLists)

        # No ccpnCalc or ccpnCalc could be empty
        if not ccpnConstraintLists:
            # Default to
            ccpnConstraintLists = []
            for constraintStore in self.ccpnNmrProject.sortedNmrConstraintStores():
                ccpnConstraintListsTmp = constraintStore.sortedConstraintLists()
                if len(ccpnConstraintListsTmp):
                    ccpnConstraintLists.extend(ccpnConstraintListsTmp)
                    if self.ccpnNmrConstraintStore == None:
                        self.ccpnNmrConstraintStore = constraintStore # just use one for now
                    else:
                        nTwarning("Skipping additional nmrConstraintStore %s, just maintaining first." % constraintStore)
                    # end if
                # end if
            # end for
        # end if
        self.ccpnConstraintLists = ccpnConstraintLists


        for ccpnMolSys in self.ccpnMolSystemList:
            moleculeName = self._ensureValidName(ccpnMolSys.code)
#            nTdebug("Working on ccpnMolSys.code: %s became moleculeName: %s" % (ccpnMolSys.code,moleculeName))
            if self.isNonDescriptiveMolSysDefault(moleculeName):
#                nTdebug("Swapping out non-descriptive molecule name %s for %s" % (moleculeName, self.project.name))
                moleculeName = self.project.name
            moleculeName = self.project.uniqueKey(moleculeName)

            self.molecule = Molecule(name = moleculeName)
            self.project.appendMolecule(self.molecule)

            self.molecule.ccpn = ccpnMolSys
            ccpnMolSys.cing = self.molecule


            if not len(ccpnMolSys.structureEnsembles):
                nTmessage("There are no coordinates for molecule %s", self.molecule.name)

            # stuff molecule with chains, residues and atoms and coords
            if not self._match2Cing(modelCount = modelCount):
                nTerror("Failed to _match2Cing")
                return None

            self.project.molecule.updateAll()
            nTmessage("==> Ccpn molecule '%s' imported", moleculeName)
        # end for
        self.project.updateProject()

        return True
    # end def importFromCcpnMolecule


    def _match2Cing(self, modelCount = None):
        '''Descrn: Imports chains, residues, atoms and coords
                   from Ccpn.MolSystem into a Cing.Project.Molecule instance.
                   (fastest way to import since it loops only once over
                   chains, residues, atoms and coordinates.)
           When modelCount is not None it will limit the number of models imported.
           Output: Cing.Molecule or None on error.
        '''
        unmatchedAtomByResDict = {}

        ccpnMolSys = self.molecule.ccpn
        ccpnStructureEnsemble = None
        ccpnCalc = self.ccpnCingRun

        if ccpnCalc: # Fails for NRG-CING but a nice feature for use from within Analysis etc.
            structureData = ccpnCalc.findFirstData(className = self.CCPN_RUN_STRUCTURE,
                                                   molSystemCode = ccpnMolSys.code,
                                                   ioRole = 'input')
            if structureData:
                ccpnStructureEnsemble = structureData.structureEnsemble

        # No ccpnCalc or ccpnCalc is empty
        if not ccpnStructureEnsemble:
            # Default
            ccpnStructureEnsembles = ccpnMolSys.sortedStructureEnsembles()
            if ccpnStructureEnsembles:
                # Just take the most recent Ensemble,
                # Don't rely on the 'current' one being set,
                # or even correct (e.g from ARIA)
                ccpnStructureEnsemble = ccpnStructureEnsembles[ - 1]
            else:
                # CCPN mol system must have a structure
                # otherwise no point in continuing
                msg = 'CCPN mol system %s has no structures'
                nTerror(msg % ccpnMolSys.code)

#        if False: # Block for debug.
#            try:
#                ensembleName = ccpnStructureEnsemble.structureGeneration.name
#            except AttributeError:
#                ensembleName = 'ensemble_name'
#            nTdebug("Using CCPN Structure Ensemble '%s'", ensembleName)

        ccpnMolCoordList = []
        maxModelCount = 0
        if hasattr(ccpnStructureEnsemble, 'models'):
            maxModelCount = len(ccpnStructureEnsemble.models)
            if modelCount:
                if maxModelCount > modelCount:
                    maxModelCount = modelCount
                    nTmessage("Limiting the number of imported models to: %d" % maxModelCount)
            self.molecule.modelCount += maxModelCount
            ccpnMolCoordList = [ccpnStructureEnsemble]


        # Set all the chains for this ccpnMolSystem
        for ccpnChain in ccpnMolSys.sortedChains():
            pdbOneLetterCode = ccpnChain.pdbOneLetterCode
#            pdbOneLetterCode = ensureValidChainId(ccpnChain.pdbOneLetterCode)
#            nTdebug("Chain id from CCPN %s to CING %s" % (ccpnChain.pdbOneLetterCode, pdbOneLetterCode))
#            if pdbOneLetterCode != ccpnChain.pdbOneLetterCode:
#                nTmessage("Changed chain id from CCPN [%s] to CING [%s]" % (ccpnChain.pdbOneLetterCode, pdbOneLetterCode))
#                nTdebug("Find out if this leads to inconsistencies in CING")
                # In example from Wim there is a chain without a chain ID so disabling the above error message.
                # This isn't a problem if CCPN uses the same chain id's i.e. no spaces or special chars.
                # From CCPN doc:
    #            One letter chain identifier. Will be used by PDB (and programs that use similar conventions). 
#    WARNING: having same oneLetterCode for different chains is legal but may cause serious confusion.
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

            chain = self.molecule.addChain(pdbOneLetterCode) # updated to catch invalid code such as a ' '.
            if chain == None:
                nTerror("Failed to molecule.addChain(pdbOneLetterCode) for pdbOneLetterCode [%s]" % pdbOneLetterCode)
                msg = "See also %s%s" % (issueListUrl,244)
                msg += "\n or %s%s" % (issueListUrl,223)
                nTwarning(msg)
                return
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
                ccpnMolType = ccpnResidue.molType 
                # Can not be taken outside loop because within a chain multiple molTypes might occur in CCPN.
                resNumber = ccpnResidue.seqCode
                chemCompVar = ccpnResidue.chemCompVar
                chemComp = chemCompVar.chemComp
                ccpnLinking = ccpnResidue.linking # start, middle, or end.
                ccpnResName3Letter = chemComp.code3Letter   # e.g. HIS absent in the case of entry 1kos, issue 198, for nucleic acid "5mu"
                ccpnResCode = ccpnResidue.ccpCode           # e.g. HIS
                ccpnResDescriptor = chemCompVar.descriptor  # e.g. protein His prot:HE2;deprot:HD1

                ccpnResDescriptorPatched = patchCcpnResDescriptor(ccpnResDescriptor, ccpnMolType, ccpnLinking)
                if not ccpnResName3Letter:
                    if not ccpnResCode:
                        nTcodeerror("found a ccpn residue without a ccpnResCode for residue: %s; skipping" % ccpnResidue)
                        continue
                    ccpnResName3Letter = ccpnResCode
#    nameDict = {'CCPN': 'DNA A deprot:H1'..
                ccpnResNameInCingDb = "%s %s %s" % (ccpnResidue.molType, ccpnResCode, ccpnResDescriptorPatched)
#                nTdebug("Name3Letter, Code, Descriptor, DescriptorPatched NameInCingDb %s, %s, %s, %s, %s" % (
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
#                    nTdebug("Residue '%s' identified in CING DB as %s." % (ccpnResNameInCingDb, matchingConvention))
                else:
                    # Happens for every terminal residue
#                    nTdebug("Residue '%s' not identified in CING DB as %s." % (ccpnResNameInCingDb, matchingConvention))
                    matchingConvention = INTERNAL
                    if NTdb.isValidResidueName(ccpnResName3Letter):
#                        nTdebug("Residue '%s' identified in CING DB as %s." % (ccpnResName3Letter, matchingConvention))
                        pass
                    else:
                        if self.allowNonStandardResidue:
#                            nTdebug("Residue '%s' will be a new residue in convention %s." % (ccpnResName3Letter, matchingConvention))
                            pass
                        else:
                            nTmessage("Residue '%s' will be skipped as it is non-standard in convention: %s." % (ccpnResName3Letter, 
                                                                                                                 matchingConvention))
                            addResidue = False
                            addingNonStandardResidue = True
#                        if not unmatchedAtomByResDict.has_key(ccpnResName3Letter):
#                            unmatchedAtomByResDict[ ccpnResName3Letter ] = ([], [])

                if not addResidue:
                    continue

                Nterminal = False # pylint: disable=C0103
                Cterminal = False # pylint: disable=C0103
                if ccpnMolType == Ccpn.CCPN_PROTEIN:
                    ccpnLinking = ccpnResidue.linking
                    if ccpnLinking == Ccpn.CCPN_START:
                        Nterminal = True # pylint: disable=C0103
                    elif ccpnLinking == Ccpn.CCPN_END:
                        Cterminal = True # pylint: disable=C0103

                resNameCing = ccpnResNameInCingDb
                if matchingConvention == INTERNAL:
                    resNameCing = ccpnResName3Letter

                if not resNameCing:
                    nTcodeerror("Failed to get a resNameCing for ccpnResidue: [" + ccpnResidue + ']')
                    continue
                residue = chain.addResidue(resNameCing, resNumber, convention = matchingConvention, Nterminal = Nterminal, Cterminal = 
                                           Cterminal)
                if not residue:
                    nTwarning("Failed to add residue: [" + resNameCing + ']')
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
#                        nTdebug('Creating non-standard atom %s' % repr(cingNameTuple))
                        cingResNameTuple = (INTERNAL, chain.name, resNumber, None)
                        res = self.molecule.decodeNameTuple(cingResNameTuple)
                        if not res:
                            nTcodeerror('No residue found in CING for tuple %s. Skipping creating non-standard atoms' % cingResNameTuple)
                            continue
                        atom = res.addAtom(atomName)
                        if not atom:
                            nTdebug('Failed to add atom to residue for tuple %s' % repr(cingNameTuple))
                            continue
                        if not unmatchedAtomByResDict.has_key(ccpnResName3Letter):
                            unmatchedAtomByResDict[ ccpnResName3Letter ] = ([], [])
                        atmList = unmatchedAtomByResDict[ccpnResName3Letter][0]
                        resNumList = unmatchedAtomByResDict[ccpnResName3Letter][1]

                        if (atomName not in atmList) and (atomName not in ATOM_LIST_TO_IGNORE_REPORTING):
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
                            #TODO: issue 128 or 129 JFD: It usually happens for H in N-term, which CING is not mapping yet. GV will fix.
#                            nTdebug('CING %s not found in CCPN: %s', atom, ccpnAtom)
                            continue
                        # end if

                        if ccpnCoordAtom.coords:
                            i = - 1
                            for ccpnModel in ccpnCoordResidue.parent.parent.sortedModels():
                                i += 1
                                # at this point i will be zero for the first model.
                                if i >= maxModelCount:
#                                    nTdebug("Not adding model idx %d and more." % i)
                                    break
                                ccpnCoord = ccpnCoordAtom.findFirstCoord(model = ccpnModel)
                                if not ccpnCoord: # as in entry 1agg GLU1.H2 and 3.
#                                    nTwarning("Skipping coordinate for CING failed to find coordinate for model %d for atom %s" % (
#i, atom)) 
# happens for 2xfm  <Atom A.VAL280.HG11> and many others.
                                    continue
                                atom.addCoordinate(ccpnCoord.x, ccpnCoord.y, ccpnCoord.z, ccpnCoord.bFactor, ocuppancy=ccpnCoord.occupancy)
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
                nTmessage(msg)
            else:
                nTerror(msg)

        return self.molecule
    # end def _match2Cing


    def _getCingAtom(self, ccpnAtomSet):
        """Matches to CING atoms or a pseudoAtom
        Return list or None on Error.
        """

#        nTdebug("    ccpnAtomSet = %s" % ccpnAtomSet)

        ccpnAtomList = ccpnAtomSet.sortedAtoms()
        if not ccpnAtomList:
            nTerror("No ccpnAtomList: %s", ccpnAtomList)
            return None


        # Quicky for efficiency.
        if len(ccpnAtomList) == 1:
            ccpnAtom = ccpnAtomList[0]
            if not hasattr(ccpnAtom, self.CCPN_CING_ATR):
                nTerror("No Cing atom obj equivalent for Ccpn atom: %s", ccpnAtom)
                return None
            return ccpnAtom.cing

        cingAtomList = []
        atomSeenLast = None
        for ccpnAtom in ccpnAtomList:
#            nTdebug("      ccpn atom: %s" % ccpnAtom)
            if not hasattr(ccpnAtom, self.CCPN_CING_ATR):
                nTerror("No Cing atom obj equivalent for Ccpn atom: %s", ccpnAtom)
                return None
            atomSeenLast = ccpnAtom.cing
            cingAtomList.append(ccpnAtom.cing)

        if len(cingAtomList) < 2:
            return atomSeenLast

        if not atomSeenLast:
            nTerror("Failed to find single CING atom for ccpnAtomList %s" % ccpnAtomList)
            return None

        cingPseudoAtom = atomSeenLast.getRepresentativePseudoAtom(cingAtomList)
        if not cingPseudoAtom:

            return atomSeenLast
        return cingPseudoAtom


    def _getCcpnShiftList(self, ccpnMolSystem, ccpnShiftList):
        """Descrn: Internal function to transfer CCPN assignments in the
                   input shift list, which match to a given ccpnMolSystem,
                   to the relevant Cing objects. This function assumes
                   that Cing molecules are already mapped to CCPN molSystems
           Inputs: CCPN MolSystem.MolSystem, CCPN Nmr.ShiftList
           Output: True or None for error.

           NB CING data model has no CS list entity but rather stores the info at the atom & resonances level.
        """
#        nTdebug("Now in %s", getCallerName())
        shiftMapping = self._getShiftAtomNameMapping(ccpnShiftList, ccpnMolSystem)
        if not len(shiftMapping):
            nTmessage("Skipping empty CS list.")
            return True
#        if not self.molecule.hasResonances():
#            self.molecule.newResonances() # do only once per import now. TODO: enable multiple resonances per atom per CCPN project.

        resonanceListName = getDeepByKeysOrAttributes( ccpnShiftList, NAME_STR ) # may be absent according to api.
        if resonanceListName == None:
            nTwarning("Failed to get resonanceListName from CCPN which will not allow CING to match later on for e.g. Vasco. Continuing.")
            resonanceListName = 'source'
        resonanceListName = getUniqueName( self.molecule.resonanceSources, resonanceListName)
        resonanceList = self.molecule.newResonances()
        if not isinstance( resonanceList, ResonanceList ):
            nTerror("Failed to create a new resonance list to the project.")
            return True
#        nTdebug("Renaming resonance list from: %s to: %s" % ( resonanceList.name, resonanceListName) )
        resonanceList.rename(resonanceListName)
        knownTroubleResidues = {} # To avoid repeating the same messages over
        atomsTouched = {} # Use a hash to prevent double counting.

        # Called KeyList because of name class with ccpnShiftList
#        ccpnShiftKeyList = shiftMapping.keys()
        resonanceSetDoneMap = {}
        for ccpnShift in ccpnShiftList.sortedMeasurements():
            shiftValue = ccpnShift.value
            shiftError = ccpnShift.error
            ccpnResonance = ccpnShift.getResonance()
            ccpnResonanceSet = ccpnResonance.resonanceSet
            if not resonanceSetDoneMap.has_key( ccpnResonanceSet ):
                resonanceSetDoneMap[ccpnResonanceSet ] = -1
            resonanceSetDoneMap[ ccpnResonanceSet ] += 1
            resonanceSetDoneCount = resonanceSetDoneMap[ ccpnResonanceSet ]
            if resonanceSetDoneCount > 1:
#                nTdebug("Ignoring ccpnShift %s because count is %s which is over the 0/1 expected" % (ccpnShift, resonanceSetDoneCount))
                continue
            if not shiftMapping.has_key( ccpnShift ) :
#                nTdebug("Skipping shift outside molecular system or without atoms.")
                continue
            ccpnResidue, _ccpnAtoms = shiftMapping[ccpnShift]
#            nTdebug("Looking %s with %s and %s" % ( ccpnShift, ccpnResonanceSet, resonanceSetDoneCount ))

            if knownTroubleResidues.get(ccpnResidue):
                nTdebug("Skipping known trouble residue: %s" % ccpnResidue )
                continue

            if not hasattr(ccpnResidue, 'cing'):
                msg = "%s:CCPN residue %d %s skipped - no Cing link"
                nTwarning(msg, getCallerName(), ccpnResidue.seqCode, ccpnResidue.ccpCode)
                knownTroubleResidues[ccpnResidue] = True
                continue

            ccpnAtomSetList = ccpnResonanceSet.sortedAtomSets()
            isStereo = len(ccpnAtomSetList) == 1
            if resonanceSetDoneCount >= len(ccpnAtomSetList):
#                nTdebug("Ignoring ccpnShift %s because resonanceSetDoneCount is %s which is over length of ccpnAtomSetList %s" % (
#                    ccpnShift, len(ccpnAtomSetList)))
                continue
            ccpnAtomSet = ccpnAtomSetList[resonanceSetDoneCount]
#            for ccpnAtom in ccpnAtoms:
            ccpnAtom = list(ccpnAtomSet.atoms)[0] # Picking only the first hydrogen of say a methyl group. What sorting is used?
#            nTdebug("Looking at first ccpnAtom %s out of ccpnAtomSet %s" % ( ccpnAtom, ccpnAtomSet))
            try:
                a = ccpnAtom.cing
#                nTdebug("Looking at atom %s" % a)
                # Since we don't show methyls in the assignment list any more; they appear lost; this fixes issue 192.
                if a.isMethylProton() and a.pseudoAtom():
                    a = a.pseudoAtom() #

                index = len(a.resonances) - 1
#                nTdebug("Looking at atom %s resonanceSetDoneCount: %s isStereo %s" % (a, resonanceSetDoneCount, isStereo))
                lastAtomResonance = a.resonances[index] # last existing resonance of atom.
                lastAtomResonance.value = shiftValue
                lastAtomResonance.error = shiftError
                if a.isProChiral(): # only mark those that need marking.
                    if isStereo:
                        otherAtom = a.getStereoPartner()
#                        nTdebug("For stereo looking at otherAtom: %s" % ( otherAtom))
                        if otherAtom != None:
                            shiftValueOther = otherAtom.resonances[index].value
                            if math.fabs( shiftValueOther -  shiftValue ) < 0.01:
                                isStereo = False
                                otherAtom.setStereoAssigned(False)
#                        else:
#                            nTdebug("Failed to getStereoPartner from %s" % a)
                    a.setStereoAssigned(isStereo)
                # end if prochiral
                # Make mutual linkages between CCPN and Cing objects
                lastAtomResonance.ccpn = ccpnShift
                ccpnShift.cing = lastAtomResonance
                atomsTouched[a] = None
#                resonanceList.append( lastAtomResonance )
            except:
                msg = "%s: %s, shift CCPN atom %s skipped"
                nTwarning(msg, getCallerName(), ccpnResidue.cing, ccpnAtom.name)
            # end try
        # end for.over shifts.

#        nTdebug("==> CCPN ShiftList '%s' imported from CCPN Nmr project '%s' with %s items", 
#ccpnShiftList.name, ccpnShiftList.parent.name, len(resonanceList))
#        nTmessage("==> Count of (pseudo-)atom with resonances updated %s" % len(atomsTouched.keys()))
#        nTdebug(  "==> Count of resonances in list added %s (should be the same)" % len(resonanceList))
#        nTmessage("==> Count of resonanceSetDone %s (<= above count)" % len(resonanceSetDoneMap.keys()))

        return True

    def importFromCcpnPeakAndShift(self):
        """Descrn: Function to transfer assigned peaks from a CCPN project
                   to a Cing Project. Checks are made to ensure all the
                   relevant molecular descriptions are present or also
                   transferred.
                   As the name suggests, this also transfers the chemical shift lists.
           Inputs: Cing Project, CCPN Implementation.MemopsRoot
           Output: True or None
        """

        doneSetShifts = False
        ccpnCalc = self.ccpnCingRun
        if ccpnCalc:
            nTdebug("Using ccpnCalc object")
            ccpnMolSys = self.molecule.ccpn
            for measurementData in ccpnCalc.findAllData(className = self.CCPN_RUN_MEASUREMENT,
                                                        ioRole = 'input'):
                measurementList = measurementData.measurementList
                if measurementList and measurementList.className == 'ShiftList':
                    doneSetShifts = self._getCcpnShiftList(ccpnMolSys, measurementList)

        # No ccpCalc or ccpnCalc is empty
        if not doneSetShifts:
#            nTdebug("Not using ccpnCalc object")
            ccpnShiftLoL = []
            ccpnPeakLoL = self._getCcpnPeakLoL()

            for ccpnPeakList in ccpnPeakLoL:
                ccpnExperiment = ccpnPeakList.dataSource.experiment

                if ccpnExperiment.shiftList not in ccpnShiftLoL:
                    if ccpnExperiment.shiftList:
#                        nTdebug("Adding CCPN shiftList (%s) from CCPN experiment (%s)" % ( ccpnExperiment.shiftList, ccpnExperiment))
                        ccpnShiftLoL.append(ccpnExperiment.shiftList)
                    else:
                        pass
#                        nTdebug("Skipping because None, CCPN shiftList (%s) from CCPN experiment (%s)" % (
#ccpnExperiment.shiftList, ccpnExperiment))
                else:
#                    nTdebug("Skipping already found CCPN shiftList (%s) from CCPN experiment (%s)" % (
#ccpnExperiment.shiftList, ccpnExperiment))
                    pass


            if not ccpnShiftLoL:
#                nTdebug("There are no shift lists at this point, CCPN will most likely only find one in the CCPN project")
#                ccpnShiftLoL = self.ccpnNmrProject.findAllMeasurementLists(className = 'ShiftList') # not sorted
                # Use sorting by CCPN.
#                ccpnShiftLoL = filterListByObjectClassName( self.ccpnNmrProject.sortedMeasurementLists(), self.CCPN_CS_LIST )
                # or as per Rasmus' suggestion:
                a = self.ccpnNmrProject.sortedMeasurementLists()
                ccpnShiftLoL = [x for x in a if x.className == self.CCPN_CS_LIST]
#                nTdebug("There are shift lists: %s" % str(ccpnShiftLoL))
            if ccpnPeakLoL and (not ccpnShiftLoL):
                nTwarning('CCPN project has no shift lists linked to experiments. Using any/all available shift lists')

#            nTdebug("Shift lists %r" % ccpnShiftLoL)

            if not ccpnShiftLoL:
#                nTdebug('CCPN project contains no shift lists')
                return True

            for ccpnMolSystem in self.ccpnMolSystemList:
                for ccpnShiftList in ccpnShiftLoL:
                    if not ccpnShiftList:
                        nTerror("Observed ccpnShiftList (%s) in non-empty ccpnShiftLoL; happens in example data but JFD doesn't know why"
                                % ccpnShiftList)
                        continue
                    doneSetShifts = self._getCcpnShiftList(ccpnMolSystem, ccpnShiftList)
                    if not doneSetShifts:
                        nTerror("Import of CCPN chemical shifts failed")
                        return False
                    # end if
                # end for
            # end for
        # end if

        if not self._getCcpnPeakList():
            nTerror("Failed _getCcpnPeakList")
            return False

        return True


    def _getCcpnPeakList(self):
        """Descrn: Internal function to link the relevant peaks in a
                   CCPN project to a Cing Project. If a calculation
                   object is already setup in the CCPN project for
                   Cing this will be used to specify the peak lists
                   for analysis. Otherwise all peak lists will be
                   considered.
                   Will still report success if nothing was imported.
                   I.e. no peaks present.
           Inputs: Cing Project, CCPN Implementation.MemopsRoot
           Output: True or None for error.
        """
        for ccpnPeakList in self._getCcpnPeakLoL():
            ccpnDataSource = ccpnPeakList.dataSource
            ccpnExperiment = ccpnDataSource.experiment
            ccpnNumDim = ccpnDataSource.numDim

            shiftList = ccpnExperiment.shiftList
            if not shiftList:
                shiftLists = self.ccpnNmrProject.findAllMeasurementLists(className='ShiftList')
                if len(shiftLists) == 1:
                    shiftList = self.ccpnNmrProject.findFirstMeasurementList(className='ShiftList')
#                    shiftList = shiftLists[0] # no indexing allowed on sets so we repeat the search above.
                else:
                    nTwarning("Skipping simply getting the first shift list as there are more than one lists")

            if not shiftList:
                nTwarning("No shift list found for CCPN Experiment '%s'", ccpnExperiment.name)
                continue

            # Setup peak list name
            plName = '%s_%s_%i' % (ccpnExperiment.name, ccpnDataSource.name,
                                                         ccpnPeakList.serial)
            peakListName = self._ensureValidName(plName, 'Peak')
            peakListName = self.project.uniqueKey(peakListName)


            # Make CING peak list and setup reciprocal links
            peakList = self.project.peaks.new(peakListName, status = 'keep')
            peakList.ccpn = ccpnPeakList
            ccpnPeakList.cing = peakList

            msgHol = MsgHoL()
            for ccpnPeak in ccpnPeakList.peaks:

                # Get frequency peak dimensions
                ccpnPeakDims = [pd for pd in ccpnPeak.sortedPeakDims() if pd.dataDimRef]
                ccpnPositions = [pd.value for pd in ccpnPeakDims] #ppm

                # Setup volumes & intensities
                vValue = NaN
                vError = NaN
                ccpnVolume = ccpnPeak.findFirstPeakIntensity(intensityType = 'volume')
                if ccpnVolume:
                    vValue = ccpnVolume.value or NaN
                    vError = ccpnVolume.error or NaN

                if str(vValue) == 'inf':
                    vValue = NaN

                hValue = NaN
                hError = NaN
                ccpnHeight = ccpnPeak.findFirstPeakIntensity(intensityType = 'height')
                if ccpnHeight:
                    hValue = ccpnHeight.value or NaN
                    hError = ccpnHeight.error or NaN

                if str(hValue) == 'inf':
                    hValue = NaN

                if isNaN(vValue) and isNaN(hValue):
#                    nTwarning("CCPN peak '%s' missing both volume and height" % ccpnPeak)
                    msgHol.appendWarning("CCPN peak '%s' missing both volume and height" % ccpnPeak)

                resonances = []
                for peakDim in ccpnPeakDims:
                    resonancesDim = []
                    for contrib in peakDim.peakDimContribs:
                        try:
                            cingResonance = contrib.resonance.findFirstShift(parentList = shiftList).cing
                            resonancesDim.append(cingResonance)
                        except:
#                            nTdebug('==== contrib out %s', contrib)
                            pass

                    if resonancesDim:
                        resonances.append(resonancesDim[0])
                    else:
                        resonances.append(None)

                cingResonances = list(resonances)

                peak = Peak(dimension = ccpnNumDim,
                                        positions = ccpnPositions,
                                        volume = vValue, volumeError = vError,
                                        height = hValue, heightError = hError,
                                        resonances = cingResonances)

                peak.ccpn = ccpnPeak
                ccpnPeak.cing = peak

                peakList.append(peak)
            # end for peak
            msgHol.showMessage(max_warnings=2)

            nTdetail("==> PeakList '%s' imported from CCPN Nmr project '%s'", peakListName, self.ccpnNmrProject.name)
        return True

    def _getCcpnPeakLoL(self):

        """Descrn: Get the CCPN peak lists to import from a CCPN NMR project.
                   Uses a previously setup CCPN calculation object for Cing
                   if it is available, otherwise all peaklists are used.
           Inputs: CCPN Nmr.NmrProject
           Output: List of CCPN Nmr.PeakLIsts
        """
        peakLists = []

        ccpnCalc = self.ccpnCingRun
        if ccpnCalc:
#            nTdebug("In %s using ccpnCalc" % getCallerName())
            for peakData in ccpnCalc.findAllData(className = self.CCPN_RUN_PEAK, ioRole = 'input'):
#                nTdebug("Using peakData %s" % peakData)
                peakList = peakData.peakList
                if peakList: # Technically possible that it may have been deleted
#                    nTdebug("Using peakList %s" % peakList)
                    peakLists.append(peakList)
        # No ccpnCalc or ccpnCalc is empty
        if not peakLists:
#            nTdebug("In %s no peakLists yet" % getCallerName())
            for experiment in self.ccpnNmrProject.sortedExperiments():
#                nTdebug("Using experiment %s" % experiment)
                for spectrum in experiment.sortedDataSources():
#                    nTdebug("Using spectrum %s" % spectrum)
                    for peakList in spectrum.peakLists:
#                        nTdebug("Using peakList %s" % peakList)
                        peakLists.append(peakList)

#        nTdebug("In %s return peakLists %s" % (getCallerName(), str(peakLists)))
        return peakLists

    def _getShiftAtomNameMapping(self, ccpnShiftList, ccpnMolSystem):
        """Descrn: Internal function to create a dictionary that maps between CCPN Shift objects (which in turn link to CCPN
                   Resonances) and a list of the CCPN Residues and Atoms to which they may be assigned.
           Inputs: CCPN Nmr.ShiftList, CCPN MoleSystem.MolSystem
           Output: Dict of CCPN Nmr.Shift:[CCPN MolSystem.Residue, Tuple of CCPN MolSystem.Atoms] which may be empty
                   if the input is empty.

           Details about this part of the CCPN API use at:
           http://www.ccpn.ac.uk/ccpn/data-model/python-api-v2-examples/assignment
        """

#        nTdebug("Now in _getShiftAtomNameMapping for ccpnShiftList (%r)" % ccpnShiftList)
        ccpnResonanceList = []
        ccpnResonanceToShiftMap = {}
        ccpnShiftMappingResult = {}

        measurementList = ccpnShiftList.sortedMeasurements()
        if not len(measurementList):
            nTwarning("Ccpn Shift List has no members; it is empty")
            return ccpnShiftMappingResult

        for ccpnShift in measurementList:
            ccpnResonance = ccpnShift.resonance
            ccpnResonanceList.append(ccpnResonance)
            ccpnResonanceToShiftMap[ccpnResonance] = ccpnShift
#            nTdebug("Mapped CCPN resonance %s to CCPN shift %s" % (ccpnResonance, ccpnShift))

        for ccpnResonance in ccpnResonanceList:
            if not ccpnResonance.resonanceSet: # i.e atom assigned
#                nTdebug("Skipping unassigned CCPN resonance %s" % ccpnResonance)
                continue
            ccpnAtomSetList = list(ccpnResonance.resonanceSet.atomSets)
            ccpnResidue = ccpnAtomSetList[0].findFirstAtom().residue
            if ccpnResidue.chain.molSystem is not ccpnMolSystem:
                nTdebug("Skipping resonance %s because CCPN residue falls outside the expected CCPN molSystem" % ccpnResonance)
                continue
            atomList = []
            if not ccpnAtomSetList:
                nTdebug("Skipping resonance %s because empty ccpnAtomSetList was created" % ccpnResonance)
                continue
            for ccpnAtomSet in ccpnAtomSetList:
#                nTdebug("Working on ccpnAtomSet: %r" % ccpnAtomSet)
                for ccpnAtom in ccpnAtomSet.atoms:
#                    nTdebug("Working on %s %s %r" % (ccpnResonance, ccpnAtomSet, ccpnAtom))
                    atomList.append(ccpnAtom)
            ccpnShift = ccpnResonanceToShiftMap[ccpnResonance]
            ccpnShiftMappingResult[ccpnShift] = [ccpnResidue, tuple(atomList) ]
        matchCount = len(ccpnShiftMappingResult)
#        nTdebug("_getShiftAtomNameMapping found %d elements in mapping." % matchCount)
        if matchCount == 0:
            nTwarning("All resonances in this list %r are unassigned" % ccpnShiftList)
        return ccpnShiftMappingResult


#    def _setShift(self, shiftMapping, ccpnShiftList):
#        '''Descrn: Core function that sets resonances to atoms.
#           Inputs: Cing.Molecule instance (obj), ccp.molecule.MolSystem.MolSystem.
#           Output: Cing.Project or None on error.
#        '''
#        # TO DO: shiftMapping should pass cing objects
#        self.molecule.newResonances()
#
#        ccpnShifts = shiftMapping.keys()
#
#        for ccpnShift in ccpnShifts:
#            shiftValue = ccpnShift.value
#            shiftError = ccpnShift.error
#            ccpnResidue, ccpnAtoms = shiftMapping[ccpnShift]
#
#            for ccpnAtom in ccpnAtoms:
#                try:
#                    atom = ccpnAtom.cing
#                    atom.resonances().value = shiftValue
#                    atom.resonances().error = shiftError
#                    index = len(atom.resonances) - 1
#                    atom.setStereoAssigned() # untested for JFD has no test data.
#                    # Make mutual linkages between Ccpn and Cing objects
#                    # cingResonace.ccpn=ccpnShift, ccpnShift.cing=cinResonance
#                    atom.resonances[index].ccpn = ccpnShift
#                    ccpnShift.cing = atom.resonances[index]
#                except:
#                    nTwarning("_setShift: %s, shift CCPN atom %s skipped", ccpnResidue.cing, ccpnAtom.name)
#                # end try
#            # end for
#        # end for
#
#        nTdetail("==> CCPN ShiftList '%s' imported from Ccpn Nmr project '%s'",
#                       ccpnShiftList.name, ccpnShiftList.parent.name)
#        return True
#    # end def _setShift

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
                nTwarning(" no shift list found for Ccpn.Experiment '%s'", ccpnExperiment.name)

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
                            nTwarning(" peak '%s' missing both volume and height", ccpnPeak)

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
                                    pass
#                                    nTdebug('==== contrib out %s', contrib)
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

                    nTdetail("==> PeakList '%s' imported from Ccpn Nmr project '%s'",
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
           Output: True or None on error.
        '''

#        mapDistListType = { self.CC: 'DistRestraint', 'HBondConstraintList': 'HbondRestraint'}

        # map to CING names were possible note the presence of DistanceRestraintList.Hbond
        mapDistListType = { self.CCPN_DISTANCE_CONSTRAINT_LIST: DR_LEVEL, self.CCPN_HBOND_CONSTRAINT_LIST: HBR_LEVEL}

        msgHoL = MsgHoL()

        classNameList = (self.CCPN_DISTANCE_CONSTRAINT_LIST, self.CCPN_HBOND_CONSTRAINT_LIST)
        ccpnConstraintLoL = self._getCcpnRestraintLoL(self.ccpnConstraintLists, classNameList)
        if not ccpnConstraintLoL:
#            nTdebug("No ccpnDistanceLoL which can be normal.")
            return True

        for ccpnDistanceList in ccpnConstraintLoL:
            distType = mapDistListType[ccpnDistanceList.className]
            ccpnDistanceListName = self._ensureValidName(ccpnDistanceList.name, distType)
            distanceRestraintList = self.project.distances.new(ccpnDistanceListName, status = 'keep')

            ccpnDistanceList.cing = distanceRestraintList
            distanceRestraintList.ccpn = ccpnDistanceList

#                    for ccpnDistanceConstraint in ccpnDistanceList.sortedConstraints():
            for ccpnDistanceConstraint in ccpnDistanceList.sortedConstraints():
                result = getRestraintBoundList(ccpnDistanceConstraint, Ccpn.RESTRAINT_IDX_DISTANCE, msgHoL)
                if not result:
                    msgHoL.appendMessage("%s with bad distances imported." % (ccpnDistanceConstraint))
                    result = (None, None)
                lower, upper = result

                atomPairList = self._getConstraintAtomPairList(ccpnDistanceConstraint)

                if not atomPairList:
                    # restraints that will not be imported
                    msgHoL.appendMessage("%s without atom pairs will be skipped" % (ccpnDistanceConstraint))
                    continue
                # end if

                distanceRestraint = DistanceRestraint(atomPairList, lower, upper)
#                nTdebug('distanceRestraint.isValid: %s' % distanceRestraint.isValid)

                if not (distanceRestraint and distanceRestraint.isValid): # happened for entry 1f8h and 2xfm
                    # restraints that will not be imported
                    msgHoL.appendMessage("%s failed to be instantiated as CING DistanceRestraint" % (ccpnDistanceConstraint))
                    continue
                # end if

                distanceRestraint.ccpn = ccpnDistanceConstraint
                ccpnDistanceConstraint.cing = distanceRestraint

                distanceRestraintList.append(distanceRestraint)
            if distanceRestraintList.simplify():
                nTerror("Failed to simplify the distanceRestraintList")
            if len(distanceRestraintList) == 0:
                nTdetail("Ccpn distance restraint list remained empty and will be removed")
                self.project.distances.delete(ccpnDistanceListName)


        msgHoL.showMessage()
        return True
    # end def importFromCcpnDistanceRestraint

    def importFromCcpnDistMetaData(self):
        '''Descrn: Import meta data from nmr constraint store.
                put in by StereoAssignmentCleanup#storeToAppData
           Output: True on error.
        '''
        if self.ccpnNmrConstraintStore == None:
#            nTdebug("Ignoring meta data because no self.ccpnNmrConstraintStore ")
            return

        if not hasattr(self.ccpnNmrConstraintStore, 'findAllApplicationData'):
#            nTdebug("Ignoring meta data because no self.ccpnNmrConstraintStore.findAllApplicationData")
            return

        appDataList = self.ccpnNmrConstraintStore.findAllApplicationData(application='FormatConverter', 
                                                                         keyword='stereoAssignmentCorrectionsFile')
        if len(appDataList) == 0:
#            nTdebug("No FC meta data on SSA")
            return

        if len(appDataList) > 1:
            nTdebug("Ignoring FC meta data beyond the first element.")
        appDataString = appDataList[0]

        if not isinstance(appDataString, AppDataString):
            nTerror("FC meta data isn't a AppDataString")
            return True

        star_text = appDataString.value
        if not isinstance(star_text, str):
            nTerror("FC meta data value isn't a String")
            return True

        if len(star_text) < 100:
            nTerror("FC meta data value isn't long enough to be valid")
            return True

#        nTdebug("Got meta data on SSA")
#                 + star_text[:30])
        projectDistList = self.project.distances
        if not len(projectDistList):
            nTwarning("self.project.distances is empty but FC meta data will still be added.")
        projectDistList.__setattr__(STEREO_ASSIGNMENT_CORRECTIONS_STAR_STR, star_text)
    # end def importFromCcpnDistMetaData

    def importFromCcpnDihedralRestraint(self):
        '''Descrn: Import dihedral restraints from Ccpn.Project into Cing.Project.
                   As input either Cing.Project instance or Ccpn.Project instance,
                   or both, since it'll check if instances has attribute .ccpn or
                   .cing, respectively.
                   Molecules and Coordinates should be imported previouly.
           Inputs: Ccpn Implementation.Project, Cing.Project instance.
           Output: True or None on error.
        '''

        # it should be done only if Ccpn.Project has dihedral constraints
        molSysTorsions = {}
        for ccpnMolSystem in self.ccpnProject.molSystems:
            molSysTorsions[ccpnMolSystem] = createMoleculeTorsionDict(ccpnMolSystem)
        # end for

        msgHoL = MsgHoL()
        classNameList = (self.CCPN_DIHEDRAL_CONSTRAINT_LIST)
        ccpnConstraintLoL = self._getCcpnRestraintLoL(self.ccpnConstraintLists, classNameList)
        if not ccpnConstraintLoL:
#            nTdebug("No ccpnDihedralLoL which can be normal.")
            return True

        for ccpnDihedralList in ccpnConstraintLoL:
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
                    nTdetail("Ccpn dihedral restraint '%s' with bad values imported." % ccpnDihedralConstraint)
                    result = (None, None)

                lower, upper = result
                atoms = self._getConstraintAtomList(ccpnDihedralConstraint)
                if not atoms:
                    msgHoL.appendMessage("Ccpn dihedral restraint '%s' without atoms will be skipped" % ccpnDihedralConstraint)
                    continue

                dihedralRestraint = DihedralRestraint(atoms, lower, upper)
                if not (dihedralRestraint and dihedralRestraint.isValid): # happened for entry 1f8h and 2xfm
                    # restraints that will not be imported
                    msgHoL.appendMessage("%s failed to be instantiated as CING DihedralRestraint" % (ccpnDihedralConstraint))
                    continue
                # end if

                dihedralRestraintList.append(dihedralRestraint)

                dihedralRestraint.ccpn = ccpnDihedralConstraint
                ccpnDihedralConstraint.cing = dihedralRestraint
            # end for ccpnDihedralConstraint
            if len(dihedralRestraintList) == 0:
                nTdetail("Ccpn dihedral restraint list remained empty and will be removed")
                self.project.dihedrals.delete(ccpnDihedralListName)
        # end for
        msgHoL.showMessage()
        return True
    # end def importFromCcpnDihedralRestraint

    def importFromCcpnRdcRestraint(self):
        '''Descrn: Import RDC restraints from Ccpn.Project into Cing.Project.
                   As input either Cing.Project instance or Ccpn.Project instance,
                   or both, since it'll check if instances has attribute .ccpn or
                   .cing, respectively.
                   Molecules and Coordinates should be imported previously.
           Inputs: Ccpn Implementation.Project, Cing.Project instance.
           Output: True or None on error.
        '''
        msgHoL = MsgHoL()
        classNameList = (self.CCPN_RDC_CONSTRAINT_LIST)
        ccpnConstraintLoL = self._getCcpnRestraintLoL(self.ccpnConstraintLists, classNameList)
        if not ccpnConstraintLoL:
#            nTdebug("No ccpnRDCLoL which can be normal.")
            return True
        for ccpnRdcList in ccpnConstraintLoL:
            ccpnRdcListName = self._ensureValidName(ccpnRdcList.name, RDC_LEVEL)

            rdcRestraintList = self.project.rdcs.new(ccpnRdcListName, status = 'keep')

            ccpnRdcList.cing = rdcRestraintList
            rdcRestraintList.ccpn = ccpnRdcList

            for ccpnRdcConstraint in ccpnRdcList.sortedConstraints():
                result = getRestraintBoundList(ccpnRdcConstraint, self.RESTRAINT_IDX_RDC, msgHoL)
                if not result:
                    nTdetail("Ccpn RDC restraint '%s' with bad values imported." %
                              ccpnRdcConstraint)
                    result = (None, None)
                lower, upper = result

                atomPairList = self._getConstraintAtomPairList(ccpnRdcConstraint)

                if not atomPairList:
                    # restraints that will not be imported
                    nTdetail("Ccpn RDC restraint '%s' without atom pairs will be skipped" % ccpnRdcConstraint)
                    continue
                # end if

                rdcRestraint = RDCRestraint(atomPairList, lower, upper)

                rdcRestraint.ccpn = ccpnRdcConstraint
                ccpnRdcConstraint.cing = rdcRestraint

                rdcRestraintList.append(rdcRestraint)
            # end for
            if len(rdcRestraintList) == 0:
                nTdetail("Ccpn distance restraint list remained empty and will be removed")
                self.project.rdcs.delete(ccpnRdcListName)

        # end for
        msgHoL.showMessage()
        return True
    # end def importFromCcpnRdcRestraint


    def ccpnDistanceRestraintToString(self, ccpnConstraint):
        lowerLimit = None
        upperLimit = None
        if hasattr(ccpnConstraint, 'lowerLimit'):
            lowerLimit = ccpnConstraint.lowerLimit
            upperLimit = ccpnConstraint.upperLimit
        result = 'Constraint [%d]: [%s] - [%s]' % (
            ccpnConstraint.serial,
            val2Str(lowerLimit, '%.1f'),
            val2Str(upperLimit, '%.1f')) # Deals with None.

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

            resonanceListLength = len(resonanceList)
            assert(resonanceListLength == 2) 
            # During a regular run (not with -O option given to python interpreter) this might cause a exception being thrown.
            if resonanceListLength != 2:
                nTcodeerror("expected a pair but found number: %d for ccpnConstraint %s" % (resonanceListLength, ccpnConstraint))
                return None
            for resonance in resonanceList:
                resAtomList = []
                resonanceSet = resonance.resonanceSet
                if resonanceSet:
                    for atomSet in resonanceSet.sortedAtomSets():
                        # atom set is a group of atoms that are in fast exchange and therefore are not assigned to individually 
#                        (e.g. methyl group).
                        for atom in atomSet.sortedAtoms():
                            resAtomList.append('%d.%s' % (
                                atom.residue.seqCode, atom.name))
                else:
                    nTwarning("No resonanceSet (means unassigned) for ccpnConstraint %s" % ccpnConstraint)
                resAtomList.sort()
                resAtomString = ','.join(resAtomList)
                atomList.append(resAtomString)
            result += '  [%s] - [%s]' % (atomList[0], atomList[1])
        # end for
        return result
    # end def

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
#        # Example code from Wim is a nice demonstration.
        if 0:
            for constItem in ccpnConstraint.sortedItems():
                nTdebug( 'ccpn restraint: %s' % self.ccpnDistanceRestraintToString(ccpnConstraint))
#            nTdebug('')

        # Now the real code.
        atomPairList = []
        atomPairSet = set()
        fixedResonanceLoL = []

        for constItem in ccpnConstraint.sortedItems():
            # JFD from WV. Tries to use sorted items where available.
            fixedResonanceLoL.append(getResonancesFromPairwiseConstraintItem(constItem))

#        nTdebug("fixedResonanceLoL: %s" % fixedResonanceLoL)
        for fixedResonanceList in fixedResonanceLoL:
#            nTdebug("  fixedResonanceList: %s" % fixedResonanceList)
            # JFD Normally would use less levels of loops here but just to figure out how it's done it's nicer to spell it out.
            fixedResonanceSetLeft = fixedResonanceList[0].resonanceSet
            fixedResonanceSetRight = fixedResonanceList[1].resonanceSet
            if not fixedResonanceSetLeft:
#                nTdebug("Failed to find fixedResonanceSet Left for ccpnConstraint %s" % ccpnConstraint)
                return None
            if not fixedResonanceSetRight:
#                nTdebug("Failed to find fixedResonanceSet Right for ccpnConstraint %s" % ccpnConstraint)
                return None
            fixedAtomSetListLeft = fixedResonanceSetLeft.sortedAtomSets()
            fixedAtomSetListRight = fixedResonanceSetRight.sortedAtomSets()
#            nTdebug("    fixedAtomSetListLeft  = %s" % fixedAtomSetListLeft)
#            nTdebug("    fixedAtomSetListRight = %s" % fixedAtomSetListRight)
            for fixedAtomSetLeft in fixedAtomSetListLeft:
#                nTdebug("      fixedAtomSetLeft: %s" % fixedAtomSetLeft)
                atomListLeft = []
                for ccpnAtomLeft in fixedAtomSetLeft.sortedAtoms():
#                    nTdebug("        ccpnAtom Left: %s" % ccpnAtomLeft)
                    if not hasattr(ccpnAtomLeft, self.CCPN_CING_ATR):
                        nTerror("No Cing ccpnAtomLeft obj equivalent for Ccpn atom: %s", ccpnAtomLeft)
                        return None
                    atomLeft = ccpnAtomLeft.cing
                    atomListLeft.append(atomLeft)
                if not atomLeft:
                    nTerror("Failed to find at least one atomLeft for ccpnConstraint %s" % ccpnConstraint)
                    return None
                pseudoAtomLeft = atomLeft.getRepresentativePseudoAtom(atomListLeft)
                if pseudoAtomLeft: # use just the pseudo representative.
                    atomListLeft = [ pseudoAtomLeft ]
#                nTdebug("      atomListLeft: %s" % atomListLeft)
                for atomLeft in atomListLeft:
#                    nTdebug("        atomLeft: %s" % atomLeft)
                    for fixedAtomSetRight in fixedAtomSetListRight:
#                        nTdebug("          fixedAtomSetRight: %s" % fixedAtomSetRight)
                        atomListRight = []
                        for ccpnAtomRight in fixedAtomSetRight.sortedAtoms():
#                            nTdebug("                ccpnAtom Right: %s" % ccpnAtomRight)
                            if not hasattr(ccpnAtomRight, self.CCPN_CING_ATR):
                                nTerror("No Cing ccpnAtomRight obj equivalent for Ccpn atom: %s", ccpnAtomRight)
                                return None
                            atomRight = ccpnAtomRight.cing
                            atomListRight.append(atomRight)
                        if not atomRight:
                            nTerror("Failed to find at least one atomRight for ccpnConstraint %s" % ccpnConstraint)
                            return None
                        pseudoAtomRight = atomRight.getRepresentativePseudoAtom(atomListRight)
                        if pseudoAtomRight: # use just the pseudo representative.
                            atomListRight = [ pseudoAtomRight ]
#                        nTdebug("          atomListRight: %s" % atomListRight)
                        for atomRight in atomListRight:
                            atomPair = (atomLeft, atomRight)
#                            nTdebug("            atomPair: %s %s" % atomPair)
                            if atomPair in atomPairSet:
#                                nTdebug("Skipping pair already represented.")
                                continue
                            atomPairSet.add(atomPair)
                            atomPairList.append(atomPair)
#        nTdebug("_getConstraintAtomPairList: %s" % atomPairList)
        return atomPairList

    def _getConstraintAtomList(self, ccpnConstraint):
        """ Use this routine instead of the above for dihedrals and chemical shifts.
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
            nTcodeerror("Routine _getConstraintAtomList should only be called for %s and %s" % (
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
                            if not hasattr(atom, self.CCPN_CING_ATR):
#                                nTdebug("No Cing atom obj equivalent for Ccpn atom: %s", atom.name)
                                pass
                    atomList.append(equivAtoms.keys())

            if len(atomList) == len(fixedResonanceList):
                try:
                    atoms = [ x[0].cing for x in atomList ]
                except:
#                    nTdebug("No Cing atom obj equivalent for Ccpn atom list %s" % atomList)
                    pass
        return list(atoms)
    # end def


    def _ensureValidName(self, name, prefix = "_"):
        '''Descrn: For checking string names from Ccpn.Project for objects like molecule, peak list, restraint list, etc.
                   Objects may start with a digit now in CING.
                   Cing doesn't like names starting with spaces neither '|', '.', or '+'.
           Inputs: a string 'name'.
           Output: same string 'name', 'prefix' + string 'name' or
                   just 'prefix' if 'name' = None'''

#        if not name: # JFD doesn't understand this line. Is name sometimes an empty string or so?
        if not name:
            name = prefix

#        if name[0].isdigit():
#            name = prefix + '_' + name
#        else:
#            name = prefix
        # end if

        name = name.replace('|', '_')
        name = name.replace(' ', '_')
        name = name.replace('.', '_')
        name = name.replace('+', '_')

        return name
    # end def _ensureValidName

    # # # # # # Functions to Export into CCPN from CING # # # # # #

    # # # # # # # CHECKS # # # # # # #

    def _checkCingProject(self):
        """Descrn: Function to check that an object really is a Cing Project
           Output: True or None
        """

        if not self.project:
            nTerror("Undefined CING project")
            return None

        if not isinstance(self.project, Project):
            nTerror("Input object is not a CING project - %s", self.project)
            return None

        return True


    def createCcpnProject(self):
        """Descrn: Function to add a CCPN project to self.
           Inputs: Cing Project
           Output: None for error.
        """

        if self.ccpnProject:
            nTerror("ccpnProject already present")
            return None

        name = self.project.name
        if os.path.exists(name):
            nTmessage("Removing directory with assumed CCPN project: %s" % name)
            shutil.rmtree(name)

        nTmessage("==> Creating new CCPN project '%s' ", name)

        self.ccpnProject = MemopsRoot(name = name)
        self.project.ccpn = self.ccpnProject
        self.ccpnProject.cing = self.project
        self.ccpnProject.cingRun = None
        return True

    def createCcpn(self):
        """Descrn: Create a new CCPN project and associates it to a Cing.Project.
           Inputs: Cing.Project instance.
           Output: True for success, None for error.
        """
        self.ccpnProject = None # removing it.
        if not self.createCcpnProject():
            nTerror(" Failed createCcpnProject")
            return None
        if not self.createCcpnMolSystem():
            nTerror("Failed to createCcpnMolSystem")
            return None
#        if not self.ccpnNmrProject:
#            self.ccpnNmrProject = self.ccpnProject.newNmrProject(name = self.ccpnProject.name)
#            if not self.ccpnNmrProject:
#                nTerror("Failed ccpnProject.newNmrProject")
#                return None

#        if not self.createCcpnStructures():
#            nTerror("Failed to createCcpnStructures")
#            return None
#        if not self.createCcpnRestraints():
#            nTerror("Failed to createCcpnRestraints")
#            return None
        # TODO: Peaks, Shift CS & restraint Lists
        return True
    # end def createCcpn

    def createCcpnPeakLists(self):
        """Descrn: An empty shell of a function until TJS works out what to do.
           Inputs:
           Output:
        """
        # The CCPN experiments and dataSources are hollow shells
        # they could be better filled in the future
        # What are the dimension nucleii?
        # What is the point referencing?
        pass
#        for peakList in self.project.peaks:
#            if peakList.ccpn:
#                continue
            # end if
        # end for
    # end def

    def createCcpnMolSystem(self):
        """Descrn: Create from first Cing.Molecule a ccpn molSystem.
           Inputs: self
           Output: Return None on error
        """

        matchingConvention = INTERNAL
        unmatchedAtomByResDict = {}

        if not self.project.moleculeNames:
            nTerror("No molecule present")
            return

        moleculeName = self.project.moleculeNames[0]
        molecule = self.project[moleculeName]

        nTdebug("Doing create CCPN mol system (%s)", moleculeName)
        if hasattr(molecule, self.CING_CCPN_ATR):
            nTerror("createCcpnMolSystem tried for molecule (%s) with existing link. Giving up.", moleculeName)
            return

#        nTdebug("self.ccpnProject.molSystems: %s" % self.ccpnProject.molSystems)
        ccpnMolSystem = self.ccpnProject.findFirstMolSystem()
        if ccpnMolSystem:
            nTerror("Found prexisting ccpnMolSystem in ccpnProject. Giving up on recreating.")
            return
        ccpnMolSystem = self.ccpnProject.newMolSystem(code = moleculeName, name = moleculeName)

        ccpnMolSystem.cing = molecule
        molecule.ccpn = ccpnMolSystem

        msgHol = MsgHoL()
        self.molecule = molecule # Needed in this class even if it's temp. JFD: don't think it's needed now.
        for chain in molecule.chains:
            residues = chain.residues
            # chain is guaranteed unique in a CING molecule and hopefully also in CCPN mol system.
#            moleculeChainName = moleculeName + '_' + chain.name
            firstRes = residues[0]
            molType = 'other'
#            nTdebug("Residue props: %s" % (firstRes.db.properties))
            if firstRes.hasProperties('protein'):
                molType = 'protein'
            elif firstRes.hasProperties('nucleic'):
                if firstRes.hasProperties('deoxy'):
                    molType = 'DNA'
                else:
#                    nTdebug("Assumed to be RNA in CCPN when no deoxy property set in CING nucleotide for: %s." % firstRes)
                    molType = 'RNA'
                # end if
            elif firstRes.hasProperties('water'):
                molType = 'water'
            else:
                nTwarning("Found chain with first residue: %s of unknown chain type. No problem if names in CING and CCPN match."%firstRes)
#            nTdebug("molType: %s" % molType)

            sequence = []
            resSkippedList = []
            ccpnResDescriptorList = []
            for res in chain:
                resNameCcpnFull = res.db.translate(CCPN)
                if not resNameCcpnFull:
                    nTerror("Failed to get CCPN residue name for %s" % res)
                    resSkippedList.append(res)
                    continue
                # Actually gives: 'DNA G prot:H1;deprot:H7' or 'protein Val neutral'
#                    resNameCcpn = upperCaseFirstCharOnly(res.resName)
                resNameCcpnList = resNameCcpnFull.split(' ')
#                nTdebug("resNameCcpnList %s" % resNameCcpnList)
                if len(resNameCcpnList) != 3:
                    nTwarning("JFD thought the full ccpn residue name is always of length 3; found: %d %s" % (
                     len(resNameCcpnList), resNameCcpnList))
                    nTwarning("JFD thought the full ccpn residue name always included a moltype,"+
                              "3-letter name, and a descriptor even if it's just 'neutral'")
                    resSkippedList.append(res)
                    continue
                resNameCcpn = resNameCcpnList[1]
                sequence.append(resNameCcpn)
                ccpnResDescriptor = resNameCcpnList[2]
                ccpnResDescriptorList.append(ccpnResDescriptor)
            if resSkippedList:
                nTerror("Skipping chain with residue names that failed to be translated to CCPN: %s" % resSkippedList)
                continue
#            nTdebug("sequence for CCPN: %s" % sequence)

            ccpnMolecule = makeMolecule(self.ccpnProject, molType, isCyclic = False, startNum = firstRes.resNum,
                                        molName = chain.name, sequence = sequence)
            ccpnChain = ccpnMolSystem.newChain(code = chain.name, molecule = ccpnMolecule)
            ccpnChain.cing = chain
            chain.ccpn = ccpnChain

            ccpnResidueList = ccpnChain.sortedResidues()
            seqLength = len(ccpnResidueList)
            for i in range(seqLength):
                ccpnResidue = ccpnResidueList[i]
                ccpnResidueSeqId = ccpnResidue.seqId
                r = residues[i]
                resName = r.resName
                resNum = r.resNum

                try:
                    ccpnResidue.checkValid()
                except:
                    nTerror("Failed ccpnResidue.checkValid() first try")
                    return None

                ccpnResDescriptorOrg = ccpnResDescriptorList[i]
                ccpnResDescriptor = modResDescriptorForTerminii( ccpnResDescriptorOrg, i, seqLength, molType)
#                nTdebug("Looking at CING residue [%s] with ccpnResDescriptor, ccpnResidue.linking [%s] [%s]" % (r, 
#ccpnResDescriptor, ccpnResidue.linking))

                chemCompVarNew = None
                # check if patching is needed. E.g. for nucleic acids it is not and the code below wouldn't even work.
                # TODO: debug this mechanism so it also works for Nucleic Acid structures.
                if molType == 'protein':
#                    nTdebug("Modifying residue %s variant from %s to %s" % ( r, ccpnResDescriptorOrg, ccpnResDescriptor ))
                    # block of code adapted from ccp.util.Molecule#setMolResidueCcpCode
                    chemComp = ccpnResidue.root.findFirstChemComp(ccpCode = ccpnResidue.ccpCode, molType = molType)
                    if not chemComp:
                        nTcodeerror("Failed to find chemComp for CING residue: %s." % r)
                        return
                    chemCompVar = ccpnResidue.getChemCompVar()
#                    nTdebug("Found chemCompVar: %s" % chemCompVar)
                    chemCompVarNew = chemComp.findFirstChemCompVar( descriptor = ccpnResDescriptor, linking = ccpnResidue.linking)
                    if chemCompVarNew:
#                        nTdebug("Found chemCompVarNew: %s" % chemCompVarNew)
                        if chemCompVarNew != chemCompVar:
#                            nTdebug("chemCompVar is not chemCompVarNew, need to update.")
#                            ccpnResidueOrg = ccpnResidue
                            ccpnMolResidueOrg = ccpnResidue.molResidue
                            # TODO; JFD: the below line fails and I don't know why.
                            setMolResidueChemCompVar(ccpnMolResidueOrg, chemCompVarNew)
#                            if ccpnMolResidueNew is ccpnMolResidueOrg:
#                                nTerror("ccpnMolResidueNew is ccpnMolResidueOrg after it should have been replaced")
#                            ccpnResidue = ccpnChain.findFirstResidue(molResidue = ccpnMolResidueNew)
                            ccpnResidue = ccpnChain.findFirstResidue(seqId = ccpnResidueSeqId)
#                            nTdebug("Found %s %s" % (ccpnResidueOrg, ccpnResidue))
#                            nTdebug("Found %s %s" % (ccpnMolResidueOrg, ccpnMolResidueNew))
                            if not ccpnResidue:
                                nTerror("Failed to get ccpnResidue from api back while working on %s" % ccpnResidueList[i])
                                return
#                            if ccpnResidue is ccpnResidueOrg:
#                                nTerror("ccpnResidue is ccpnResidueOrg after it should have been replaced")
    #                        nTdebug("Replacing ccpnMolResidue %s with %s" % (ccpnMolResidueOrg, ccpnMolResidue))
#                            nTdebug("Confirming ccpnResidue.chemCompVar %s TODO: this line reports bad ccv but it's done correctly." % 
#ccpnResidue.getChemCompVar())
                        else:
#                            nTdebug("chemCompVar is same as chemCompVarNew")
                            pass
                    else:
                        nTwarning( ("Failed to find CCPN chemCompVarNew for chemComp [%s]/chemCompVar" +
                                    " [%s] with descriptor [%s] and linking [%s].") % (
                               chemComp, chemCompVar, ccpnResDescriptor, ccpnResidue.linking))
#                        for ccv in chemComp.chemCompVars:
#                            nTdebug("Available molType, ccpCode, linking, descriptor,default: %s %s %s %s %s" % ( 
#chemComp.molType, chemComp.ccpCode, ccv.linking, ccv.descriptor, ccv.isDefaultVar))
                    # end if chemCompVarNew
                # end if patch needed.

#                nTdebug("Now with ccpnResDescriptor, ccpnResidue.linking [%s] [%s]" % (ccpnResDescriptor, ccpnResidue.linking))
                try:
                    ccpnResidue.checkValid()
                except:
                    nTerror("Failed ccpnResidue.checkValid() second try")
                    return None

                ccpnResidue.cing = r
                r.ccpn = ccpnResidue

                # If the ccv was replaced then use only those atoms that are also in it. E.g. exclude Cys HG
                if chemCompVarNew:
                    ccpnAtomList = []
                    chemAtomList = chemCompVarNew.sortedChemAtoms()
                    nTmessageNoEOL("DEBUG: %-80s  " % ccpnResidue )
                    for chemAtom in chemAtomList:
                        if chemAtom.name.startswith('prev_') or chemAtom.name.startswith('next_'):
                            continue
                        nTmessageNoEOL("%-4s  " % chemAtom.name )
#                        if chemAtom.name == 'HE2':
#                            nTdebug('at breakpoint')
                        ccpnAtom = ccpnResidue.findFirstAtom( name = chemAtom.name )
                        if not ccpnAtom:
                            msgHol.appendError("Failed to find %-4s in %-80s; skipping atom" % (chemAtom.name, ccpnResidue))
                            continue
                        ccpnAtomList.append(ccpnAtom)
                    nTmessage('')
                else:
                    ccpnAtomList = ccpnResidue.sortedAtoms()


#                nTdebug("Setting info for ccpn atoms: %s " % ccpnAtomList)
                for ccpnAtom in ccpnAtomList:
#                    nTmessageNoEOL("%s " % ccpnAtom.name )
                    atom = None # cing atom

                    ccpnAtomName = ccpnAtom.getName()
                    if not ccpnAtomName:
#                        nTdebug("Failed to lookup ccpnAtomName in ccpnAtom: %s; skipping." % ccpnAtom)
                        continue
#                    ccpnChemAtom = ccpnAtom.getChemAtom()
#                    try:
#                        ccpnChemAtom = ccpnAtom.chemAtom # code bug in CCPN ccp.api.molecule.MolSystem.Atom#getChemAtom?
#                    except:
#                        pass
#                        nTdebug("Failed to lookup cpnChemAtom in ccpnAtom: %s; skipping." % ccpnAtom)

#                    ccpnAtomName = ccpnAtom.name
#                    if ccpnChemAtom:
#                        ccpnAtomName = ccpnChemAtom.name
#                    else:
#                        pass
#                        nTdebug("Found name of ccpnAtom.name (only directly): %s" % ccpnAtomName)

                    nameTuple = (matchingConvention, r.chain.name, resNum, ccpnAtomName)
                    atom = self.molecule.decodeNameTuple(nameTuple)

                    if not atom:
                        if ccpnAtomName not in ATOM_LIST_TO_IGNORE_REPORTING:
                            if not unmatchedAtomByResDict.has_key(resName):
                                unmatchedAtomByResDict[ resName ] = ([], [])
                            atmList = unmatchedAtomByResDict[resName][0]
                            resNumList = unmatchedAtomByResDict[resName][1]
                            if ccpnAtomName not in atmList:
                                atmList.append(ccpnAtomName)
                            if resNum not in resNumList:
                                resNumList.append(resNum)
                            msgHol.appendError('No atom found in CING for tuple %s. Skipping creating non-standard atoms' % str(nameTuple))
                        # end if
                        continue
                    # end if
                    atom.ccpn = ccpnAtom
                    ccpnAtom.cing = atom
                # end for loop over atom
#                nTmessage('')
            # end for loop over residue
            try:
                ccpnMolecule.checkAllValid(complete=True)
            except:
                nTerror("Failed ccpnMolecule.checkAllValid; ")
                return None
            nTmessage("Cing.Chain '%s' of Cing.Molecule '%s' exported to Ccpn.Project", chain.name, moleculeName)
        # end for for loop over chain

        msg = "Non-standard (residues and their) atoms (CING residue type name and CCPN atom name)"
        if self.allowNonStandardResidue:
            msg += " added:\n"
        else:
            msg += " skipped:\n"
        msgHol.showMessage()

        if unmatchedAtomByResDict:
            msg += unmatchedAtomByResDictToString(unmatchedAtomByResDict)
            if self.allowNonStandardResidue:
                nTmessage(msg)

        return True

    # end def createCcpnMolecules

    def createCcpnStructures(self, moleculeName = None):
        """Descrn: create Ccpn.molStructures from Cing.Coordinates into a existing
                   CCPN project instance.
           Inputs: CCPN Implementation.Project, Cing.Project, String (Molecule.name)
           Output: True or None for error.
        """

        listMolecules = []

        #if 'moleculeName' is not specified, it'll export all Cing.Molecules
        if moleculeName:
            listMolecules = [self.project[moleculeName]]
            if not listMolecules:
                nTerror("molecule '%s' not found in Cing.Project", moleculeName)
                return None
        else:
            listMolecules = [ self.project[mol] for mol in self.project.moleculeNames ]
        # end if

        for molecule in listMolecules:
            if molecule.modelCount == 0:
                continue

            ccpnMolSystem = molecule.ccpn

            ensembleId = 1
            while self.ccpnProject.findFirstStructureEnsemble(molSystem = ccpnMolSystem, ensembleId = ensembleId):
                ensembleId += 1

            structureEnsemble = self.ccpnProject.newStructureEnsemble(molSystem = ccpnMolSystem, ensembleId = ensembleId)

            models = []
            for _modelIndex in range(molecule.modelCount): #@UnusedVariable
                models.append(structureEnsemble.newModel())
            # end for

            for chain in molecule.chains:
                ccpnChain = chain.ccpn

                coordChain = structureEnsemble.newChain(code = ccpnChain.code)

                for residue in chain.allResidues():
                    ccpnResidue = residue.ccpn
                    coordResidue = coordChain.newResidue(seqCode = ccpnResidue.seqCode,
                                                          seqId = ccpnResidue.seqId)
                    for atom in residue.allAtoms():
                        if not atom.coordinates:
                            if not atom.isPseudoAtom():
                                if atom.name not in ATOM_LIST_TO_IGNORE_REPORTING:
                                    nTwarning("Skipping %s because no coordinates were found", atom)
    #                        nTwarning('atom: '+atom.format())
                            continue
                        # end if
                        if not atom.has_key('ccpn'):
                            nTwarning("Skipping %s because no ccpn attribute was found to be set", atom)
    #                        nTwarning('atom: '+atom.format())
                            continue
                        # end if
                        ccpnAtom = atom.ccpn
                        coordAtom = coordResidue.newAtom(name = ccpnAtom.name)
                        for i, model in enumerate(models):
                            coordinate = atom.coordinates[i]
                            x, y, z = coordinate.e  #[:3]
                            _c = coordAtom.newCoord(model = model, x = x, y = y, z = z,
                               occupancy = coordinate.occupancy,
                               bFactor = coordinate.Bfac)

                        # end for
                    # end for
                # end for
            # end for
        # end for

        return True



    def createCcpnRestraints(self):
        """Descrn: Create a CCPN AbstractConstraintList from a
                   Cing.xxxRestraintList into a existing
                   CCPN project instance.
           Inputs: CCPN Implementation.Project, Cing.Project instance.
           Output: CCPN NmrConstraint.NmrConstraintStore or None
        """

        nTcodeerror("This code is a first setup but is NOT functional yet; see the TODOs below.")

        ccpnConstraintStore = self.ccpnProject.newNmrConstraintStore(nmrProject = self.ccpnNmrProject)

        for distanceRestraintList in self.project.distances:
            ccpnDistanceList = ccpnConstraintStore.newDistanceConstraintList(name = distanceRestraintList.name)
            for distanceRestraint in distanceRestraintList:
                upper = distanceRestraint.lower
                lower = distanceRestraint.upper
                error = upper - lower
                targetValue = (upper + lower) / 2.0
                resonances = ()

                ccpnDistanceList.newDistanceConstraint(resonances = resonances,
                   targetValue = targetValue, lowerLimit = lower, upperLimit = upper, error = error)

                # TODO: IMPORTANT Resonances Better Target resonances, error, weight
# Currently fails as:
#  File "/Users/jd/workspace35/cing/python/cing/PluginCode/Ccpn.py", line 1837, in createCcpnRestraints
#    error = upper - lower)
#  File "/Users/jd/workspace35/ccpn/python/ccp/api/nmr/NmrConstraint.py", line 32136, in newDistanceConstraint
#    return DistanceConstraint(self, **attrlinks)
#  File "/Users/jd/workspace35/ccpn/python/ccp/api/nmr/NmrConstraint.py", line 42901, in __init__
#    % (self, key))
#ApiError: <ccp.nmr.NmrConstraint.DistanceConstraint [1, 1, None]>: error setting resonances - not a modeled attribute

                #print distanceRestraint.atomPairs[0][0].ccpn
            # end for
        # end for

        for dihedralRestraintList in self.project.dihedrals:
            ccpnDihedralList = ccpnConstraintStore.newDihedralConstraintList(name =
                                                        dihedralRestraintList.name)
            for dihedralRestraint in dihedralRestraintList:
                upper = dihedralRestraint.lower
                lower = dihedralRestraint.upper
                resonances = (None, None, None, None)
                ccpnRestraint = ccpnDihedralList.newDihedralConstraint(resonances = resonances)
                ccpnRestraint.newDihedralConstraintItem(lowerLimit = lower, upperLimit = upper)
            # end for
        # end for

        # TODO: RDC restraint types
        return ccpnConstraintStore
    # end def createCcpnRestraints
# end class

def isDistanceOrHBondType(restraintTypeIdx):
    """Returns True if the restraint is either a distance or a HB"""
    return restraintTypeIdx == Ccpn.RESTRAINT_IDX_DISTANCE or restraintTypeIdx == Ccpn.RESTRAINT_IDX_HBOND

def getRestraintBoundList(constraint, restraintTypeIdx, msgHoL):
    '''Descrn: Return upper and lower values for a Ccpn constraint.
       Inputs: Ccpn constraint.
       Output: floats (lower, upper) or None

       Mind you that CING only supports lower and upper bounds like cyana so far.

       In CCPN according to: file:///Users/jd/workspace35/ccpn/python/ccp/api/doc/nmr/NmrConstraint/DistanceConstraint/index.html
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

#    nTdebug(" CCPN: constraint.targetValue    %8s" % constraint.targetValue)
#    nTdebug(" CCPN: constraint.lowerLimit     %8s" % constraint.lowerLimit)
#    nTdebug(" CCPN: constraint.upperLimit     %8s" % constraint.upperLimit)
#    nTdebug(" CCPN: constraint.error          %8s" % constraint.error)
#    nTdebug(" CCPN: restraintTypeIdx          %8s" % restraintTypeIdx)
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
#        nTdebug("Simplest case first for speed reasons.")
    else:
        if constraint.targetValue == None:
            pass
#            msg = "One or both of the two bounds are None but no target available to derive them. Lower/upper: [%s,%s]" % (lower, upper)
#            msgHoL.appendDebug(msg)
        else:
            # When there is a target value and no lower or upper we will use a error of zero by default which makes
            # the range of their error zero in case the error was not defined. This is a reasonable assumption according
            # to JFD.
            error = constraint.error or 0
            if error < 0:
                msgHoL.appendError("Found error below zero; taking absolute value of error: %r" % error)
                error = - error
            if restraintTypeIdx == Ccpn.RESTRAINT_IDX_DIHEDRAL:
                if error > 180.:
                    msgHoL.appendWarning("Found dihedral angle restraint error above half circle; "+
                                         "which means all's possible; translated well to CING: %r" % error)
                    return (0.0, - Ccpn.SMALL_FLOAT_FOR_DIHEDRAL_ANGLES)

            if lower == None:
                if restraintTypeIdx != Ccpn.RESTRAINT_IDX_DIHEDRAL:
                    pass
#                    msgHoL.appendDebug("Setting lower bound from target and (perhaps assumed dev). For restraint: %s" % constraint )
                lower = constraint.targetValue - error

            if upper == None:
                if restraintTypeIdx != Ccpn.RESTRAINT_IDX_DIHEDRAL:
                    pass
#                    msgHoL.appendDebug("Setting upper bound from target and (perhaps assumed dev). For restraint: %s" % constraint )
                upper = constraint.targetValue + error


    if isDistanceOrHBondType(restraintTypeIdx):
        if (lower != None) and (upper != None):
            if lower > upper:
                msgHoL.appendError("Lower bound is above upper bound: [%s,%s]" % (lower, upper))                
                msgHoL.appendError("CING prefers upper bound and thus unsetting lower bound as if unexisting; please check your data.")
                lower = None
        if (lower != None) and (lower < 0):
            msgHoL.appendWarning("Lower distance bound is negative. CING prefers to unset lower bound as if unexisting; please check data.")
            lower = None
        if (upper != None) and (upper < 0):
            msgHoL.appendWarning("Upper distance bound is negative. CING prefers to unset lower bound as if unexisting; please check data.")
            upper = None

    # Unfortunately, sometimes it would be nice to preserve the info on the range but can't be here.
    if restraintTypeIdx == Ccpn.RESTRAINT_IDX_DIHEDRAL:
        lower = nTlimitSingleValue(lower, - 180., 180.) # routine is ok with None input.
        upper = nTlimitSingleValue(upper, - 180., 180.)

    return (lower, upper)


def removeCcpnReferences(self):
    """To slim down the memory footprint; should allow garbage collection."""
    attributeToRemove = "ccpn"
    try:
        removeRecursivelyAttribute(self, attributeToRemove)
    except:
        nTerror("Failed removeCcpnReferences")

def initCcpn(project, ccpnFolder, modelCount = None):
    '''Descrn: Adds to the Cing Project instance from a Ccpn folder project.
       Inputs: Cing.Project instance, Ccpn project XML file or a gzipped tar file such as .tgz or .tar.gz
       When modelCount is not None it will limit the number of models imported.
       Output: Cing.Project or None on error.
    '''
    # work horse class.
    if not os.path.exists( ccpnFolder ):
        nTerror('initCcpn: ccpnFolder "%s" does not exist', ccpnFolder)
        return None
    ccpn = Ccpn(project = project, ccpnFolder = ccpnFolder )
    if not ccpn.importFromCcpn(modelCount = modelCount):
        nTerror("initCcpn: Failed importFromCcpn")
        return None
    return project


def saveCcpn(project, ccpnFolder, ccpnTgzFile = None):
    '''Descrn: Creates a Ccpn folder for an old project or a new Ccpn project.
       Inputs: Cing project.
       Output: Ccpn Project or None on error.
    '''
    if project.has_key('ccpn'):
        ccpnProject = project.ccpn
        nTmessage('saveCcpn: Saving any changes to original CCPN project')
    else:
        nTmessage('saveCcpn: Creating new CCPN project')
        # work horse class.
        ccpn = Ccpn(project = project, ccpnFolder = ccpnFolder)
        if not ccpn.createCcpn():
            nTerror("Failed ccpn.createCcpn")
            return None
        ccpnProject = ccpn.ccpnProject
    # end if

    switchOutput(False)
    status = ccpnProject.saveModified() # TODO: can't change from original ccpnFolder
    switchOutput(True)
    if status:
        nTerror("Failed ccpnProject.saveModified in " + getCallerName())
        return None

    nTmessage("Saved ccpn project to folder: %s" % ccpnFolder)

    if ccpnTgzFile:
        cmd = "tar -czf %s %s" % (ccpnTgzFile, ccpnFolder)
        if do_cmd(cmd):
            nTerror("Failed tar")
            return None
        nTmessage("Saved ccpn project to tgz: %s" % ccpnTgzFile)
    # end if
    return ccpnProject
# end def

def exportValidation2ccpn(project):
    """
    Proof of principle: export validation scores to ccpn project

    Return Project or None on error.
    """
    if not project.has_key('ccpn'):
        nTerror('exportValidation2ccpn: No open CCPN project present')
        return None

    ccpnMolSystem = project.molecule.ccpn
    ccpnEnsemble = ccpnMolSystem.findFirstStructureEnsemble()

    if not ccpnEnsemble:
        nTmessage("Failing to exportValidation2ccpn, perhaps because there is no ensemble")
        return project

    nTmessage('==> Exporting to Ccpn')
    for residue in project.molecule.allResidues():
        valObj = storeResidueValidationInCcpn(project, residue)
        if not valObj:
            # Happens for all residues without coordinates.
            nTmessage('exportValidation2ccpn: no export of validation done for residue %s', residue)
        else:
            pass
#            nTdebug('exportValidation2ccpn: residue %s, valObj: %s', residue, valObj)
    #end for
    if cing.verbosity < cing.verbosityDebug:
        switchOutput(False) # disable standard out.
    project.ccpn.saveModified()
    if cing.verbosity < cing.verbosityDebug:
        switchOutput(True)
    return project
#end def

def storeResidueValidations(validStore, context, keyword, residues, scores):
    """Descrn: Store the per-residue scores for a an ensemble within
               CCPN validation objects.
               *NOTE* This function may be quicker than using the generic
               replaceValidationObjects() because it is class specifc
       Inputs: Validation.ValidationStore,
               List of MolStructure.Residues, List if Floats
       Output: List of Validation.ResidueValidations
    """

    validObjs = []

    # Define data model call for new result
    newValidation = validStore.newResidueValidation

    for i, residue in enumerate(residues):

        score = scores[i]

        # Find any existing residue validation objects
        validObj = getResidueValidation(validStore, residue, context, keyword)

        # Validated object(s) must be in a list
        residueObjs = [residue, ]

        # Make a new validation object if none was found
        if not validObj:
            validObj = newValidation(context = context, keyword = keyword,
                                     residues = residueObjs)

        # Set value of the score
        validObj.floatValue = score

        validObjs.append(validObj)

    return validObjs


def storeResidueValidationInCcpn(project, residue, context = 'CING'):
    """
    Store residue ROG result in ccpn
    Return ccpn StructureValidation.ResidueValidation obj on success or None on error
    Return NaN when there is no ensemble.
    """

    keyword = 'ROGscore'

    ccpnMolSystem = project.molecule.ccpn
    ccpnEnsemble = ccpnMolSystem.findFirstStructureEnsemble()

    if not ccpnEnsemble:
        nTerror("Failing to storeResidueValidationInCcpn, perhaps because there is no ensemble")
        return None
    if not project.has_key('ccpnValidationStore'):
        project.ccpnValidationStore = getEnsembleValidationStore(ensemble = ccpnEnsemble,
                                                                 context = context,
                                                                 keywords = [keyword]
                                                                )
    #end if

    # Need to convert the CCPN MolSystem.Residue to MolStructure.Residue
    ccpnStrucResidue = None
    for ccpnChain in ccpnEnsemble.coordChains:
        ccpnStrucResidue = ccpnChain.findFirstResidue(residue = residue.ccpn)
        if ccpnStrucResidue:
            break

    if not ccpnStrucResidue:
        return

    # Find any existing residue validation objects
    validObj = getResidueValidation(project.ccpnValidationStore, ccpnStrucResidue,
                                    context = context, keyword = keyword)

    # Validated object(s) must be in a list
    residueObjs = [ccpnStrucResidue, ]

    # Make a new validation object if none was found
    if not validObj:
        newValidation = project.ccpnValidationStore.newResidueValidation
        validObj = newValidation(context = context, keyword = keyword,
                                 residues = residueObjs)

    # Set value of the score
    validObj.textValue = residue.rogScore.colorLabel or None
    # Failed for 2jn8 because one of the items itself was a tuple instead of string.
#    validObj.details = '\n'.join(residue.rogScore.colorCommentList) or None
    validObj.details = residue.rogScore.getColorCommentText() or None

    return validObj

#end def



def patchCcpnResDescriptor(ccpnResDescriptor, ccpnMolType, ccpnLinking):
    """See #modResDescriptorForTerminii for inverse op."""
    # CING db has only non-terminal CCPN descriptors in DB so CING can be more concise.
    ccpnResDescriptorList = NTlist()
    ccpnResDescriptorList.addList(ccpnResDescriptor.split(';'))
#    nTdebug("ccpnResDescriptorList: %s " % ccpnResDescriptorList)
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
#    nTdebug("ccpnResDescriptorList: %s " % ccpnResDescriptorList)
    ccpnResDescriptorPatched = string.join(ccpnResDescriptorList, ';')
    return ccpnResDescriptorPatched

def upperCaseFirstCharOnly(inputStr):
    """For creating CCPN residue names"""
    if not inputStr:
        return None
    if len(inputStr) == 1:
        return string.upper(inputStr)
    return string.upper(inputStr[0]) + string.lower(inputStr[1:])


def getProjectNameInFileName(fileName):
    regExpProjectNameInFileName = re.compile(".*/memops/Implementation/(.*).xml")
#    nTdebug("Matching fileName [%s]"%fileName)
    m = regExpProjectNameInFileName.match(fileName, 1)
    if not m:
#        nTdebug("No match")
        return None
    g = m.groups()
    if not g:
#        nTdebug("No groups")
        return None
    projectName = g[0]
#    nTdebug("projectName: [%s]" % projectName)
    return projectName
# end def

def modResDescriptorForTerminii( ccpnResDescriptor, i, seqLength, molType):
    """
    i starts at zero like in CING model numbering.
    Do not mix in start, middle, end for linking description.

From ccp.api.molecule.chemcomp.chemcompvar routines:

A descriptor is a semicolon-separated string of individual descriptors
an individual descriptor is of the form : tag:atName(,atName)+
the tags must appear in the order given in validTags,
and the atoms must be present
examples: 'prot:HD1''  'prot:HD1,HO;deprot:H1;link:SG' 'stereo_2:C1'
'link:C2_2'
The ''link' tag is an exception, in that the 'atNames' are actually
LinkEnd.linkCodes. These are atom names, but may in some cases have a '_n'
suffix where n is an integer. The linkCodes must correspond to linkEnds present in the ChemCompVar
For all other atNames after the tag, atom (name=atName)
must be present in  the ChemCompVar
'stereo' tags are of the form stereo_n, where n is a subType no.
and are the only tags to contain an underscore
Here, for all atNames after the tag, atom (name=atName, subType=subTypeNo)
must be present in  the ChemCompVar. The interpretation is that these
atom subtypes are chosen to give the correct stereochemistry; what that
stereochemistry is cna be seen by examining the atom network.

          # valid special descriptor
          validDescriptors = ('neutral',)

          # valid tags (key) and the order they must appear in (value)
          validTags = {'prot':0, 'deprot':1, 'link':2, 'stereo':3,}
"""
    if i > 0 and i < (seqLength-1):
        return ccpnResDescriptor

    protList = {} # dict used as sets with bogus values to the important set keys.
    deprotList = {}

    ccpnResDescriptorList = ccpnResDescriptor.split(';')
    if not ccpnResDescriptorList:
        return ccpnResDescriptor

    ccpnResDescriptorItemSaveList = [] # maintain the same order as found to fulfill validTags order requirement.
    for ccpnResDescriptorItem in ccpnResDescriptorList:
#        nTdebug("Working on ccpnResDescriptorItem: " + ccpnResDescriptorItem)
        if ccpnResDescriptorItem.startswith('prot:'):
            li = ccpnResDescriptorItem[5:].split(',' )
            for j in li:
#                nTdebug("Working on j " + j)
                protList[j] = None
        elif ccpnResDescriptorItem.startswith('deprot:'):
            li = ccpnResDescriptorItem[7:].split(',' )
            for j in li:
                deprotList[j] = None
        elif ccpnResDescriptorItem != Ccpn.CCPN_NEUTRAL:
            ccpnResDescriptorItemSaveList.append(ccpnResDescriptorItem)

    if molType == Ccpn.CCPN_PROTEIN:
        if i == 0:
            protList["H3"] = None
        elif i == (seqLength-1):
            deprotList["H''"] = None
        else:
            nTcodeerror("modResDescriptorForTerminii for protein")
#    elif molType == 'DNA' or molType == 'RNA':
#        if i == 0:
#            protList["H3"] = None
#        elif i == seqLength:
#            deprotList["H''"] = None
#        else:
#            nTcodeerror("1 in modResDescriptorForTerminii for an NA")
    ccpnResDescriptorNew = ''
    if protList:
        keyList = protList.keys()
        keyList.sort()
        ccpnResDescriptorNew += 'prot:' + ','.join(keyList)
    if deprotList:
        if ccpnResDescriptorNew != '':
            ccpnResDescriptorNew += ';'
        keyList = deprotList.keys()
        keyList.sort()
        ccpnResDescriptorNew += 'deprot:' + ','.join(keyList)
    if ccpnResDescriptorItemSaveList:
        if ccpnResDescriptorNew != '':
            ccpnResDescriptorNew += ';'
        ccpnResDescriptorNew += ','.join(ccpnResDescriptorItemSaveList)
#    if ccpnResDescriptor != ccpnResDescriptorNew:
#        nTdebug("Changed from %s to %s" % (ccpnResDescriptor,ccpnResDescriptorNew))
    return ccpnResDescriptorNew
# end def

def restoreCcpn(project, tmp=None):
    """
    Restore ccpn meta data if present
    tmp is not used but needed to fit into the api.

    Return True on error
    """
#    nTdebug("Now in " + getCallerName())

    if not project:
        nTerror('%s: no project defined' % getCallerName())
        return True
    #end if
    if not project.molecule:
        return True
    #end if
    rootPath = project.moleculePath( CCPN_LOWERCASE_STR )
    fileName = os.path.join(rootPath, STEREO_ASSIGN_FILENAME_STR)
    if not os.path.exists(fileName):
#        nTdebug("No stereo assign meta data from ccpn because no file named: " + fileName)
        return
    star_text = readTextFromFile(fileName)

    projectDistList = project.distances
    if not len(projectDistList):
        nTwarning("self.project.distances is empty but FC meta data will still be added.")
    projectDistList.__setattr__(STEREO_ASSIGNMENT_CORRECTIONS_STAR_STR, star_text)

#    nTmessage('==> Restored CCPN meta data')
#end def

def saveCcpnMetaData(project, tmp = None):
    """
    Save ccpn meta data if present
    tmp is not used but needed to fit into the api.

    Return True on error
    """
#    nTdebug("Now in " + getCallerName())
    if not project:
        nTerror('%s: no project defined' % getCallerName())
        return True
    #end if
    if not project.molecule:
        return True
    #end if
    projectDistList = project.distances
    if not len(projectDistList):
        pass
#        nTdebug("self.project.distances is empty but FC meta data will still be looked for.")
    star_text = getDeepByKeysOrAttributes(projectDistList, STEREO_ASSIGNMENT_CORRECTIONS_STAR_STR)
    if not star_text:
#        nTdebug("No star_text")
        return
    rootPath = project.moleculePath( CCPN_LOWERCASE_STR )
    fileName = os.path.join(rootPath, STEREO_ASSIGN_FILENAME_STR)
    if not os.path.exists(rootPath):
#        nTdebug("No rootPath named: " + rootPath)
        return
    if writeTextToFile(fileName, star_text):
        nTdebug("writeTextToFile failed to file: " + fileName)
        return True
#    nTdebug('Stored CCPN meta data (only SSA for now)')
#end def

# register the function
methods = [ (initCcpn, None),
           (removeCcpnReferences, None),
           (exportValidation2ccpn, None),
           (saveCcpn, None),
           ]

saves    = [(saveCcpnMetaData, None)]
restores = [(restoreCcpn, None)]

#exports  = []
