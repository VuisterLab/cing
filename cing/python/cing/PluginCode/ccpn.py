# Leave this at the top of ccp imports as to prevent non-errors from non-cing being printed.
from cing.Libs.NTutils import NTdebug
from cing.Libs.fpconst import NaN
from string import digits
from shutil import rmtree
from shutil import move
import tarfile
import sys
_bitBucket = open('/dev/null','aw')
_returnMyTerminal = sys.stdout
sys.stdout = _bitBucket
from ccp.general.Util import createMoleculeTorsionDict
from ccp.util.Molecule import makeMolecule
from memops.general import Io as genIo
sys.stdout = _returnMyTerminal
del(_bitBucket)

from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import NTdetail
from cing.Libs.NTutils import sprintf
from cing.core.constants import INTERNAL
from cing.core.classes import DihedralRestraint
from cing.core.classes import DistanceRestraint
from cing.core.classes import Peak
from cing.core.classes import RDCRestraint
from cing.core.dictionaries import NTdbGetResidue
from cing.core.molecule import Molecule
from cing.core.molecule import ensureValidChainId
#from cing.main import format
import os

"""
Adds initialize from CCPN project files


Methods:
    initCCPN( ccpnProjectFileName, convention ):
        initialise from CCPN project file

    initXEASY_FC( seqFile, convention ):
        initialise from xeasy seq file via CCPN formatConverter and CCPN project


    'molecule' in Cing = 'molSystem' in Ccpn

    loadCcpn( cingProject = None, ccpnFolder = None ): # phase 1
    '''Descrn: Load a Ccpn project from a Ccpn Xml file.
               Add '.ccpn' to Cing project if provided, i.e.,
               cingProject.ccpn = ccpnProject    and
               ccpnProject.cing = cingProject
       Inputs: Cing.Project instance, Ccpn project Xml file.
       Output: Ccpn Implementation.Project or None or error.
    '''
    '''
       calling only loadCcpn() will create, if successful, cingProject.ccpn,
       which is equivalent to ccpnProject.
    '''

    initCcpn( cingProject, ccpnFolder = None ):
    '''Descrn: Create a new Cing Project instance from a Ccpn Xml file.
       Inputs: Cing.Project instance, Ccpn project Xml file.
       Output: Cing.Project or None or error.
    '''

    importFromCcpn( cingProject = None, ccpnProject = None ):
    '''Descrn: Import data from Ccpn into a Cing instance.
               Either Cing instance or Ccpn instance, or both.
               Check if either instance has attribute .cing or .ccpn,
               respectively.
       Inputs: Ccpn Implementation.Project, cing instance.
       Output: cingProject or None or error.
    '''

    importFromCcpnMolecules( cingProject = None, ccpnProject = None,
                          moleculeName = None, coords = False ):
    '''Descrn: Import MolSystems (Molecules) from Ccpn.Project instance and
               append it to Cing.Project instance, including chains, residues
               and atoms.
               If parameter 'coords' (default False) is True, coordinates will
               be imported too.
               If 'moleculeName' is not defined, all MolSystem will be
               imported, otherwise only specified one.
               As input either Cing.Project instance or Ccpn.Project instance,
               or both, since it'll check if instances has attribute .ccpn or
               .cing, respectively.
       Inputs: Ccpn Implementation.Project, Cing.Project instance,
               moleculeName (string).
       Output: list of Cing.Molecule (obj) or None or error.
    '''

    importFromCcpnCoordinates( cingProject = None, ccpnProject = None,
                             moleculeName = None ):
    '''Descrn: Import coordinates from Ccpn.Project into a Cing.Project.
               If 'moleculeName' is not defined, all MolSystem's coordinates
               will be imported, otherwise only specified one.
               As input either Cing.Project instance or Ccpn.Project instance,
               or both, since it'll check if instances has attribute .ccpn or
               .cing, respectively.
       Inputs: Ccpn Implementation.Project, Cing.Project instance,
               moleculeName (string).
       Output: list of Cing.Molecule (obj) or None or error.
    '''

    importFromCcpnPeaksAndShifts( cingProject = None, ccpnProject = None,
                                  moleculeName = None ):
    '''Descrn: Import peaks and shifts from Ccpn.Project into a Cing.Project
               instance.
               If 'moleculeName' is not defined, all MolSystem will be
               imported, otherwise only specified one.
               As input either Cing.Project instance or Ccpn.Project instance,
               or both, since it'll check if instances has attribute .ccpn or
               .cing, respectively.
               Molecules should be imported previously.
       Inputs: Ccpn Implementation.Project, Cing.Project instance,
               moleculeName (string)
       Output: Cing.Project or None or error.
    '''

    importFromCcpnDistanceRestraints( cingProject = None, ccpnProject = None ):
    '''Descrn: Import distance restraints from Ccpn.Project into Cing.Project.
               As input either Cing.Project instance or Ccpn.Project instance,
               or both, since it'll check if instances has attribute .ccpn or
               .cing, respectively.
               Molecules and Coordinates should be imported previouly.
       Inputs: Ccpn Implementation.Project, Cing.Project instance
       Output: Cing.DistanceRestraintList or None or error
    '''

    importFromCcpnDihedralRestraints( cingProject = None, ccpnProject = None ):
    '''Descrn: Import dihedral restraints from Ccpn.Project into Cing.Project.
               As input either Cing.Project instance or Ccpn.Project instance,
               or both, since it'll check if instances has attribute .ccpn or
               .cing, respectively.
               Molecules and Coordinates should be imported previouly.
       Inputs: Ccpn Implementation.Project, Cing.Project instance
       Output: Cing.DihedralRestraintList or None or error
    '''

    createCcpn( cingProject = None ):
    '''Descrn: create a new Ccpn project and associates it to a Cing.Project
       Inputs: Cing.Project instance.
       Output: Ccpn Implementation.Project.
    '''

    createCcpnMolecules( cingProject = None, ccpnProject = None,
                         moleculeName = None ):
    '''Descrn: create from Cing.Molecule a molSystem into a existing
               Ccpn project instance.
       Inputs: Ccpn Implementation.Project, Cing.Project instance,
               moleculeName (string).
       Output: Ccpn Implementation.Project or None or error.
    '''

    export2Ccpn( cingProject = None ):
    '''Descrn: Export Ccpn.Project associated to a Cing.Project by creating
               a new Ccpn.Project from Cing data and saving it
               into Cing CCPN directory.
       Inputs: Cing.Project instance.
       Output: Ccpn Implementation.Project or None or error.
    '''

    createCcpnStructures( cingProject = None, ccpnProject = None,
                          moleculeName = None ):
    '''Descrn: create Ccpn.molStructures from Cing.Coordinates into a existing
               Ccpn project instance.
       Inputs: Ccpn Implementation.Project, Cing.Project instance,
               moleculeName (string).
       Output: Ccpn Implementation.Project or None or error.
    '''

def matchCing2Ccpn( cingProject = None, ccpnProject = None,
                    createCing = False, createCcpn = False ):
    '''Descrn: check consistency between Cing and Ccpn instances.
               It should try to fix problems if createCing/Ccpn is True.
               Either Cing instance or Ccpn instance, or both.
               Check if either instance has attribute .cing or .ccpn,
               respectively.
       Inputs: Ccpn Implementation.Project, cing instance.
       Output: list of object that failed to match in tuple
               (list from cing, list from ccpn) or None
    '''
    if (not Errors): return None
    # end if

    tupleErros = ( listFromCing, listFromCcpn )

    return tupleErros
# end def matchCing2Ccpn

"""
# The next import is possible but inside the cing package JFD prefers to
# have unspecified Classes to be from within cing and name the outside
# classes for eg CcpnMolecule. But that's up to you Alan.
# Ccpn imports below
# Try importing and catch error to print message
# Raise error again in order to exit the import process
# This error is then caught by the importPlugin routine
try:
    from memops.general.Io import loadProject
    from ccp.general.Util import findAtomSysNameByChemAtom #, findAtomSysNameByChemAtomSet

    NTdetail("Using CCPN version 2.x")
    namingSystem = 'CING'
except:
    NTerror("Import Error: CCPN framework not defined")
    raise ImportError
# end try

convention = INTERNAL
dictCif2Cing = {'ZN':'ZN2P', 'CA':'CA2P'}

def _checkCingProject( cingProject, funcName ):
    '''Descrn: Check if a Cing.Project exists for a given function.
       Inputs: Cing.Project, function name.
       Output: Ccpn.Project, None or error.
    '''

    if ( not cingProject ):
        NTerror(" '%s': undefined Cing.Project", funcName)
        return None
    # end if
    return cingProject
# end def _checkCingProject

def _checkCcpnProject( ccpnProject, cingProject, funcName ):
    '''Descrn: Check if a Ccpn.Project exists for a given function.
       Inputs: Cing.Project, Ccpn.Project, function name.
       Output: Ccpn.Project, None or error.
    '''

    if ( not ccpnProject ):
        if cingProject.has_key('ccpn'):
            ccpnProject = cingProject.ccpn
        else:
            NTerror(" '%s': no Ccpn.Project loaded", funcName)
            return None
        # end if
    # end if
    return ccpnProject
# end def _checkCcpnProject

def _checkCcpnMolecules( ccpnProject, moleculeName, funcName ):
    '''Descrn: Check which list of molSystem to return for a given function.
       Inputs: Cing.Project, moleculeName, function name.
       Output: List of Ccpn.MolSystems, None or error.
    '''

    # If 'moleculeName' is not specified, it'll import all MolSystems
    if ( moleculeName ):

        listMolSystems = ccpnProject.findFirstMolSystem(code = moleculeName)

        if not listMolSystems:
            NTerror( " '%s': molecule '%s' not found in Ccpn",
                     funcName, moleculeName )
            return []
        # end if
        listMolSystems = [listMolSystems]

    else:
        listMolSystems = ccpnProject.molSystems or []
    # end if
    return listMolSystems
# end def _checkCcpnMolecules

def _checkCcpnNmrProject( ccpnProject, funcName ):
    '''Descrn: Check which list of molSystem to return for a given function.
       Inputs: Cing.Project, function name.
       Output: ccp.nmr.Nmr.NmrProject, None or error.
    '''

    # TODO: this needs to be better! Taking only one NmrProject for the moment
    if ( ccpnProject.currentNmrProject ):
        ccpnNmrProject = ccpnProject.currentNmrProject
    elif ( ccpnProject.nmrProjects ):
        ccpnNmrProject = ccpnProject.findFirstNmrProject()
    else:
        NTerror(" '%s': no NmrProject found in Ccpn", funcName)
        return None
    # end if
    return ccpnNmrProject
# end def _checkCcpnNmrProject

def loadCcpn( cingProject = None, ccpnFolder = None ):
    '''Descrn: Load a Ccpn project from a Ccpn folder.
               Add '.ccpn' to Cing project if provided, i.e.,
               cingProject.ccpn = ccpnProject    and
               ccpnProject.cing = cingProject.
       Inputs: Cing.Project instance, Ccpn project Xml file.
       Output: Ccpn Implementation.Project or None or error.
    '''

    funcName = loadCcpn.func_name

    _checkCingProject( cingProject, funcName )
    if not cingProject:
        return None
    # end if

    if ( not ccpnFolder or not os.path.exists(ccpnFolder) ):
        NTerror(" '%s': ccpnFolder '%s' not found", funcName, ccpnFolder)
        return None
    # end if

    ccpnProject = loadProject(ccpnFolder)

    if ( ccpnProject ):
        # Make mutual linkages between Ccpn and Cing objects
        cingProject.ccpn = ccpnProject
        ccpnProject.cing = cingProject
    else:
        NTerror(" %s: ccpn project from file '%s' not loaded", funcName,
                ccpnFolder)
        return None
    # end if

    cingProject.addHistory( sprintf('%s from "%s"', funcName, ccpnFolder ) )
    cingProject.updateProject()

    return ccpnProject
# end def loadCcpn

def initCcpn( cingProject, ccpnFolder = None ):
    '''Descrn: Create a new Cing Project instance from a Ccpn folder project.
       Inputs: Cing.Project instance, Ccpn project Xml file or a gzipped tar file such as .tgz or .tar.gz
       Output: Cing.Project or None or error.
    '''

    funcName = initCcpn.func_name

    _checkCingProject( cingProject, funcName )
    if not cingProject:
        return None
    # end if

    NTdebug("ccpnFolder: %s", ccpnFolder) 
    if not ccpnFolder:
        NTerror("No ccpnFolder" ) 
        return None
        
    if os.path.exists(ccpnFolder) and os.path.isfile(ccpnFolder) and (\
        ccpnFolder.endswith(".tgz") or ccpnFolder.endswith(".tar.gz")):        
        try:
            rmtree( cingProject.name )
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
        tar = tarfile.open(ccpnFolder, "r:gz") 
        for itar in tar:                        
            tar.extract(itar.name, '.') # itar is a TarInfo object
            if _isRootDirectory(itar.name):
                if not ccpnRootDirectory: # pick the first one.
                    ccpnRootDirectory = _trimTrailingSlash( itar.name )
                    if not ccpnRootDirectory:
                        NTerror("Skipping potential ccpnRootDirectory")
        if not ccpnRootDirectory:
            NTerror("No ccpnRootDirectory found in gzipped tar file: %s" % ccpnFolder ) 
            return None
            
        if ccpnRootDirectory != cingProject.name:
            move( ccpnRootDirectory, cingProject.name)
        ccpnFolder = cingProject.name # Now it is a folder.
                 
    if not ccpnFolder or not os.path.exists(ccpnFolder):
        NTerror(" '%s': ccpnFolder '%s' not found", funcName, ccpnFolder)
        return None
    # end if

    ccpnProject = loadProject(ccpnFolder)

    if ( ccpnProject ):
        # Make mutual linkages between Ccpn and Cing objects
        cingProject.ccpn = ccpnProject
        ccpnProject.cing = cingProject
    else:
        NTerror(" %s: ccpn project from folder '%s' not loaded", funcName,
                 ccpnFolder)
        return None
    # end if

    if not importFromCcpn( cingProject, ccpnProject ):
        NTerror(" %s: failed to importFromCcpn", funcName)
        return None
    # end if

    cingProject.addHistory(sprintf('%s from "%s"', funcName, ccpnFolder))

    cingProject.updateProject()
# end def initCcpn

def importFromCcpn( cingProject = None, ccpnProject = None ):
    '''Descrn: Import data from Ccpn into a Cing instance.
               Either Cing instance or Ccpn instance, or both.
               Check if either instance has attribute .cing or .ccpn,
               respectively.
       Inputs: Ccpn Implementation.Project, Cing.Project instance.
       Output: Cing.Project or None or error.
    '''

    funcName = importFromCcpn.func_name

    if ( not cingProject ):
        NTerror(" '%s': undefined project", funcName)
        return None
    # end if

    ccpnProject = _checkCcpnProject( ccpnProject, cingProject, funcName )

    if ( ccpnProject ):

        NTmessage( '==> Importing data from Ccpn project "%s"', ccpnProject.name )
#        NTmessage.flush() # auto flushed (except for in Eclipse it seems)

        if not importFromCcpnMolecules(cingProject, ccpnProject, coords = True): #True is the correct, just for test now
            return None
        # end if


        importFromCcpnPeaksAndShifts(cingProject, ccpnProject)
        importFromCcpnDistanceRestraints(cingProject, ccpnProject)
        importFromCcpnDihedralRestraints(cingProject, ccpnProject)
        importFromCcpnRdcRestraints(cingProject, ccpnProject) #Cing can't store RDCs at the moment.

        cingProject.addHistory(sprintf(funcName))

        NTmessage( 'Ccpn project imported' )
        NTmessage( '%s', cingProject.format() )

        cingProject.updateProject()
    else:
        NTerror(" '%s': no Ccpn.Project imported", funcName)
        return None
    # end if
    cingProject.addHistory( sprintf(funcName) )
    return True # To distinguish success from failure.
# end def importFromCcpn

def importFromCcpnMolecules( cingProject = None, ccpnProject = None,
                          moleculeName = None, coords = False ):
    '''Descrn: Import MolSystems (Molecules) from Ccpn.Project instance and
               append it to Cing.Project instance, including chains, residues
               and atoms.
               If parameter 'coords' (default False) is True, coordinates will
               be imported too.
               If 'moleculeName' is not defined, all MolSystem will be
               imported, otherwise only specified one.
               As input either Cing.Project instance or Ccpn.Project instance,
               or both, since it'll check if instances has attribute .ccpn or
               .cing, respectively.
       Inputs: Ccpn Implementation.Project, Cing.Project instance,
               moleculeName (string).
       Output: List of Cing.Molecule (obj) or None or error.
    '''

    funcName = importFromCcpnMolecules.func_name

    ccpnProject = _checkCcpnProject( ccpnProject, cingProject, funcName )
    if not ccpnProject:
        return None
    # end if

    moleculeList = []

    listMolSystems = _checkCcpnMolecules( ccpnProject, moleculeName, funcName )

    for ccpnMolSys in listMolSystems:

        # add molecule from Ccpn to Cing
        moleculeName = cingProject.uniqueKey(_checkName(ccpnMolSys.code))

        molecule = Molecule(name = moleculeName)

        molecule.ccpn = ccpnMolSys # ccpn molSystem
        ccpnMolSys.cing = molecule

        moleculeList.append(molecule)

        cingProject.appendMolecule( molecule )

        if not len(ccpnMolSys.structureEnsembles):
            NTmessage("There's no coordinates for %s", molecule.name)
            coords = False
        # end if

        # stuff molecule with chains, residues and atoms
        # and coords if specified
        _getCcpnChainsResiduesAtomsCoords( molecule, coords = coords )

        if coords:
            NTmessage('==> Calculating dihedrals ... ' )

            cingProject.molecule.updateAll()

            NTmessage('done with coordinate import' )

            NTmessage( "Ccpn molecule '%s' imported with coordinates", moleculeName )
            NTmessage( '%s', cingProject.molecule.format() )
        else:
            NTmessage( "Ccpn molecule '%s' imported", moleculeName )
            NTmessage( '%s', cingProject.molecule.format() )
        # end if
    # end for

    cingProject.addHistory( sprintf(funcName) )
    cingProject.updateProject()

    return moleculeList
# end def importFromCcpnMolecules

def _getCcpnChainsResiduesAtomsCoords( molecule, coords=True ):
    '''Descrn: Core that'll import chains, residues, atoms and coords
               from Ccpn.MolSystem into a Cing.Project.Molecule instance.
               (fastest way to import since it loops only once over
               chains, residues, atoms and coordinates.)
       Inputs: Cing.Molecule instance (obj).
       Output: Cing.Molecule or None or error.
    '''

    ccpnMolSys = molecule.ccpn

    if coords:
        # we are taking just the current Ensemble now
        ccpnStructureEnsemble = ccpnMolSys.parent.currentStructureEnsemble
        if ccpnStructureEnsemble.molSystem is not ccpnMolSys:
            ccpnStructureEnsemble = ccpnMolSys.findFirstStructureEnsemble(
                                    molSystem = ccpnMolSys)
        # end if

        try:
            ensembleName = ccpnStructureEnsemble.structureGeneration.name
        except AttributeError:
            ensembleName = 'no_name'
        # end try

        NTmessage("Using CCPN Structure Ensemble '%s'", ensembleName)

        molecule.modelCount += len(ccpnStructureEnsemble.models)

        ccpnMolCoords = [ccpnStructureEnsemble]
    # end if

    # Set all the chains for this molSystem
    for ccpnChain in ccpnMolSys.sortedChains():
        ccpnChainLetter = ensureValidChainId(ccpnChain.pdbOneLetterCode)
        chain = molecule.addChain(ccpnChainLetter)
        #NOTE: if for some reason two or more ccpnChains have the same
        #pdbOneLetterCode, only the first will be imported. Maybe addChain
        #should deal with that.

        # Make mutual linkages between Ccpn and Cing instances
        chain.ccpn = ccpnChain
        ccpnChain.cing = chain

        #ccpnModel = None # for ccpnModel in ccpnMolCoord.sortedModels():
        if coords:
            # Get coord info for chains from Ccpn
            ccpnCoordChains = []
            for ccpnMolCoord in ccpnMolCoords: #TODO: rename variable
                ccpnCoordChain = ccpnMolCoord.findFirstCoordChain( chain = ccpnChain )
                if ccpnCoordChain:
                    ccpnCoordChains.append(ccpnCoordChain)
                # end if
            # end for
        # end if

        for ccpnResidue in ccpnChain.sortedResidues():

            #chemCompVar tells which residue variant is being used
            # TODO: mantaining CING namingSystem for CCPN.
            chemCompVar = ccpnResidue.chemCompVar
            newNamingSystem = 'CIF'

            chemComp = chemCompVar.chemComp
            namingSysObj = chemComp.findFirstNamingSystem(name = namingSystem)

            if namingSysObj:
                chemCompSysName = chemCompVar.findFirstSpecificSysName(namingSystem = namingSysObj) \
                               or chemCompVar.findFirstChemCompSysName(namingSystem = namingSysObj)
                if not chemCompSysName: # try CIF naming system
                    NTmessage("Trying to import '%s' via CIF naming system", ccpnResidue.ccpCode)
                    namingSysObj = chemComp.findFirstNamingSystem(name = newNamingSystem)
                    chemCompSysName = chemCompVar.findFirstSpecificSysName(namingSystem = namingSysObj) \
                                   or chemCompVar.findFirstChemCompSysName(namingSystem = namingSysObj)
                # end if
            else:
                NTwarning("No namingSysObj for '%s'", chemCompVar)
            # end if

            if not chemCompSysName:
                NTwarning( "Residue '%s' not identified", ccpnResidue.ccpCode )
                continue
            # end if
            # residue Name according namingSystem
            resNameInSysName = chemCompSysName.sysName
            NTdebug("Res %s name '%s' (CCPN) ==> '%s' ('%s')",
                      ccpnResidue.seqCode, ccpnResidue.ccpCode, resNameInSysName, namingSystem)

            if resNameInSysName in dictCif2Cing.keys():
                oldName = resNameInSysName
                resNameInSysName = dictCif2Cing[resNameInSysName]
                NTmessage("    Reconverted '%s' ('%s') ==> '%s' ('CING')", oldName, newNamingSystem, resNameInSysName)
            # end if
            if not NTdbGetResidue(resNameInSysName):
                NTwarning( "Residue '%s' not identified in CING DB", resNameInSysName )
                continue
            # end if

            residue=chain.addResidue(resNameInSysName,ccpnResidue.seqCode)

            # Make mutual linkages between Ccpn and Cing objects
            residue.ccpn = ccpnResidue
            ccpnResidue.cing = residue

            # add all atoms known for such cing residue instance
            residue.addAllAtoms()

            ccpnCoordResidues = []
            if coords:
                # Get coord info for residues from Ccpn
                # TODO: reuse prev coord chains
                for ccpnCoordChain in ccpnCoordChains:
                    ccpnCoordResidue = ccpnCoordChain.findFirstResidue( residue = ccpnResidue )
                    if ccpnCoordResidue:
                        ccpnCoordResidues.append(ccpnCoordResidue)
                    # end if
                # end for
            # end if
            _ccpnAtom2CingAndCoords( molecule, ccpnResidue, ccpnChainLetter,
                            ccpnCoordResidues, resNameInSysName, coords=coords )
        # end for
    # end for
    return molecule
# end def _getCcpnChainsResiduesAtomsCoords

def _ccpnAtom2CingAndCoords(molecule, ccpnResidue, ccpnChainLetter,
                     ccpnCoordResidues, resNameInSysName, coords=False):
    '''Descrn: Given a Ccpn.Residue it'll match Ccpn atoms to Cing.Atoms
               and may add coordinates to Cing.Atoms as well.
       Inputs: Cing.Molecule instance, ccp.molecule.MolSystem.Residue instance,
               a chain letter (string).
       Output: Cing.Project or None or error.
    '''
    #TODO: link ccpn ensembles and cing molecule
    atomNamingSys = 'DIANA' # IUPAC for INTERNAL_1 and DIANA for INTERNAL_0
    chemCompVar = ccpnResidue.chemCompVar

    chemComp = chemCompVar.chemComp
    namingSysObj = chemComp.findFirstNamingSystem(name = atomNamingSys)

    for ccpnAtom in ccpnResidue.sortedAtoms():

        # Have to get atom name relevant for Cing

        #chemAtomSet = ccpnAtom.chemAtomSet # TODO: to be investigated
        #if chemAtomSet:
        #    atomSysName = findAtomSysNameByChemAtomSet(namingSystem,chemAtomSet)
        chemAtom = ccpnAtom.chemAtom

        #if chemAtom:
        atomSysName = findAtomSysNameByChemAtom(namingSysObj, chemAtom)
            #atomSysName = ccpnNamingSystem.findFirstAtomSysName(atomName=chemAtom.name, atomSubType=chemAtom.subType)
        if atomSysName:
            atomName = atomSysName.sysName
        else:
            atomName = ccpnAtom.name
            NTmessage("--- No NamingSystem. Assuming ccpn's name for: %s", atomName)
        # end if
        if atomName in dictCif2Cing.keys() and ccpnResidue.molType == 'other':
            oldName = atomName
            atomName = dictCif2Cing[atomName]
            NTmessage("    Reconverted '%s' ('%s') ==> '%s' ('CING')", oldName, atomNamingSys, atomName)
        # end if

        # it's returning cing atom instance according to convention
        ccpnResSeq = ccpnResidue.seqCode

        atom = molecule.decodeNameTuple( (convention, ccpnChainLetter,
                                          ccpnResSeq, atomName) )

        if not atom:
            NTwarning( 'Atom not found in Cing DB: %s, %s, %s, %s, %s, %s, %s Res name = %s',
                     namingSystem, convention, ccpnChainLetter,
                     ccpnResidue.ccpCode, ccpnResidue.seqCode, atomName,
                     namingSystem, resNameInSysName )
        else:
            # Make mutual linkages between Ccpn and Cing objects
            atom.ccpn = ccpnAtom
            ccpnAtom.cing = atom

            if coords:
            # Get coords for atoms
                for ccpnCoordResidue in ccpnCoordResidues:
                    ccpnCoordAtom = ccpnCoordResidue.findFirstAtom(atom = ccpnAtom)

                    if not ccpnCoordAtom:
                        #TODO: it usully happens for H in N-term, which CING is not mapping yet.
                        NTwarning('Atom not found in Ccpn: %s, %s', ccpnAtom, atom)
                        continue
                    # end if

                    if ccpnCoordAtom.coords:
                        for ccpnModel in ccpnCoordResidue.parent.parent.sortedModels():
                            ccpnCoord = ccpnCoordAtom.findFirstCoord(model= ccpnModel)
                            atom.addCoordinate(ccpnCoord.x, ccpnCoord.y,
                                               ccpnCoord.z, ccpnCoord.bFactor,
                                               ocuppancy = ccpnCoord.occupancy)
                        # end for
                    # end if
                # end for
            # end if
        # end if
    # end for
# end def _ccpnAtom2CingAndCoords

def importFromCcpnCoordinates( cingProject = None, ccpnProject = None,
                               moleculeName = None ):
    '''Descrn: Import coordinates from Ccpn.Project into a Cing.Project.
               If 'moleculeName' is not defined, all MolSystem's coordinates
               will be imported, otherwise only specified one.
               As input either Cing.Project instance or Ccpn.Project instance,
               or both, since it'll check if instances has attribute .ccpn or
               .cing, respectively.
       Inputs: Ccpn Implementation.Project, Cing.Project instance,
               moleculeName (string).
       Output: List of Cing.Molecule (obj) or None or error.
    '''

    funcName = importFromCcpnCoordinates.func_name

    ccpnProject = _checkCcpnProject( ccpnProject, cingProject, funcName )
    if not ccpnProject:
        return None
    # end if

    listMolSystems = _checkCcpnMolecules( ccpnProject, moleculeName, funcName )

    for ccpnMolSys in listMolSystems:

        moleculeName = _checkName(ccpnMolSys.code)

        try:
            molecule = ccpnMolSys.cing
        except KeyError:
            NTerror( "'%s': molecule '%s' not found in Cing.Project",
                     funcName, moleculeName )
            NTerror( "You may want to import '%s' from Ccpn first",
                       moleculeName )
        # end try

        _getCcpnCoordinates( molecule )

        NTmessage('==> Updating molecule (dihedrals etc.) ... ' )

        cingProject.molecule.updateAll()

        NTmessage('done' )

        NTmessage( "Ccpn coordinates for molecule '%s' imported", moleculeName )
        NTmessage( '%s', cingProject.molecule.format() )
    # end for
    cingProject.addHistory( sprintf(funcName) )
    cingProject.updateProject()
# end def importFromCcpnCoordinates

def _getCcpnCoordinates( molecule ):
    '''Descrn: Core that'll import coordinates from Ccpn.MolSystem
               into a Cing.Project.Molecule instance.
       Inputs: Cing.Molecule instance (obj)
       Output: Cing.Project or None or error.
    '''

    ccpnMolSys = molecule.ccpn

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
            ccpnCoordChain = ccpnMolCoord.findFirstCoordChain( chain = ccpnChain )
            if ccpnCoordChain:
                ccpnCoordChains.append(ccpnCoordChain)
            # end if
        # end for

        for ccpnResidue in ccpnChain.sortedResidues():
            # Get coord info for residues from Ccpn
            ccpnCoordResidues = []
            for ccpnCoordChain in ccpnCoordChains:
                ccpnCoordResidue = ccpnCoordChain.findFirstResidue(residue = ccpnResidue)
                if ccpnCoordResidue:
                    ccpnCoordResidues.append(ccpnCoordResidue)
                # end if
            # end for

            for ccpnAtom in ccpnResidue.sortedAtoms():

                try:
                    atom = ccpnAtom.cing
                except:
                    NTwarning( ' Ccpn atom %s/%s/%s not mapped into Cing.Project',
                              ccpnAtom.name,
                              ccpnResidue.ccpCode+str(ccpnResidue.seqCode),
                              ccpnChainLetter )
                    NTmessage( 'No coordinates taken, atom skipped...' )
                    continue
                # end try

                for ccpnCoordResidue in ccpnCoordResidues:
                    ccpnCoordAtom = ccpnCoordResidue.findFirstAtom( atom = ccpnAtom )
                    if ccpnCoordAtom and ccpnCoordAtom.coords:
                        for ccpnModel in ccpnCoordResidue.parent.parent.sortedModels():
                            ccpnCoord = ccpnCoordAtom.findFirstCoord(model= ccpnModel)
                            atom.addCoordinate( ccpnCoord.x, ccpnCoord.y, ccpnCoord.z, ccpnCoord.bFactor )
                        # end for
                    # end if
                # end for
            # end for
        # end for
    # end for
# end def _getCcpnCoordinates

def importFromCcpnPeaksAndShifts( cingProject = None, ccpnProject = None,
                                  moleculeName = None ):
    '''Descrn: Import peaks and shifts from Ccpn.Project into a Cing.Project
               instance.
               If 'moleculeName' is not defined, all MolSystem will be
               imported, otherwise only specified one.
               As input either Cing.Project instance or Ccpn.Project instance,
               or both, since it'll check if instances has attribute .ccpn or
               .cing, respectively.
       Inputs: Ccpn Implementation.Project, Cing.Project instance, moleculeName.
       Output: Cing.Project or None or error.
    '''

    funcName = importFromCcpnMolecules.func_name

    ccpnProject = _checkCcpnProject( ccpnProject, cingProject, funcName )
    if not ccpnProject:
        return None
    # end if

    ccpnNmrProject = _checkCcpnNmrProject( ccpnProject, funcName )
    if not ccpnNmrProject:
        return None
    # end if

    # Molecule selection is only appropriate for ShiftLists, not for PeakLists
    listMolSystems = _checkCcpnMolecules( ccpnProject, moleculeName, funcName )

    doneSetShifts = False

    # Get shift lists (linking resonances to atoms) from Ccpn for a Cing.Molecule
    # need to do it before importing Peaks
    for ccpnMolSys in listMolSystems:

        moleculeName = _checkName(ccpnMolSys.code)

        try:
            molecule = ccpnMolSys.cing
        except KeyError:
            NTerror( "'%s': molecule '%s' not found in Cing.Project",
                     funcName, moleculeName )
            NTerror( "You may want to import '%s' from Ccpn first",
                       moleculeName )
        # end try

        if ( molecule ):

            ccpnShiftLists = ccpnNmrProject.findAllMeasurementLists \
                                             (className = 'ShiftList') or ()

            for ccpnShiftList in ccpnShiftLists:

                shiftMapping = _getShiftAtomNameMapping( ccpnShiftList,
                                                         ccpnMolSys )
                doneSetShifts = _setShifts( molecule, shiftMapping,
                                            ccpnShiftList )
            # end for
            if doneSetShifts:
                NTmessage( "Ccpn shifts (resonances) for molecule '%s' imported", moleculeName )
                NTmessage( '%s', cingProject.molecule.format() )
            # end if
        # end if
    # end for

    # Get ALL peaks from Ccpn NmrProject and link them to resonances
    # It's supposed to be done only once
    doneSetPeaks = _setPeaks( cingProject, ccpnNmrProject )

    if doneSetPeaks:
        NTmessage( "Ccpn peaks for Cing.Project '%s' imported", cingProject.name )
        NTmessage( '%s', cingProject.format() )
    # end if

    if doneSetPeaks or doneSetShifts:
        cingProject.addHistory( sprintf(funcName) )
        cingProject.updateProject()
    # end if
# end def importFromCcpnPeaksAndShifts

def _getShiftAtomNameMapping( ccpnShiftList, molSystem ):
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
#            namingSystemObject = chemCompVar.chemComp.findFirstNamingSystem(name=namingSystem)

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
#                    # Now create list, with namingSystem
#                    # (could be set to other one)
#                    # TODO: use cing object link made earlier.
#                    chemAtom = ccpnAtom.chemAtom
#                    chemAtomSysName = namingSystemObject.findFirstAtomSysName(atomName = chemAtom, atomSubType=chemAtom.subType)
#
#                    if chemAtomSysName:
#                        atomName = chemAtomSysName.sysName
#                    else:
#                        atomName = atom.name
#                    # end if


                    #atomNameList.append(atomName)
                    atomList.append(ccpnAtom)
                # end for
            # end for

            ccpnShiftMapping[ccpnResonanceToShift[ccpnResonance]] = [ccpnResidue, tuple(atomList) ]
        # end if
    # end for

    return (ccpnShiftMapping)
# end def _getShiftAtomNameMapping

def _setShifts( molecule, shiftMapping, ccpnShiftList ):
    '''Descrn: Core function that sets resonances to atoms.
       Inputs: Cing.Molecule instance (obj), ccp.molecule.MolSystem.MolSystem.
       Output: Cing.Project or None or error.
    '''
    # TODO: shiftMapping should pass cing objects
    molecule.newResonances()

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
                # TODO: set setStereoAssigned

                # Make mutual linkages between Ccpn and Cing objects
                # cingResonace.ccpn=ccpnShift, ccpnShift.cing=cinResonance
                atom.resonances[index].ccpn = ccpnShift
                ccpnShift.cing = atom.resonances[index]
            except:
                NTwarning("_setShifts (try):: %s, %s", ccpnResidue.cing,
                          ccpnAtom.name)
            # end try
        # end for
    # end for

    NTmessage( "ShiftList '%s' imported from Ccpn Nmr project '%s'",
                   ccpnShiftList.name, ccpnShiftList.parent.name )
    return True
# end def _setShifts

def _setPeaks( cingProject, ccpnNmrProject ):
    '''Descrn: Core function that sets peaks imported from Ccpn for a
               Cing.Project and links to resonances.
       Inputs: Cing.Project instance, ccp.nmr.Nmr.NmrProject.
       Output: Cing.Project or None or error. Returns True if peaks found.
    '''
    done = False

    for ccpnExperiment in ccpnNmrProject.experiments:
        shiftList = ccpnExperiment.shiftList
        if not shiftList:
            NTwarning(" no shift list found for Ccpn.Experiment '%s'",
                      ccpnExperiment.name)
        # end if
        # sampled data dimensions?
        for ccpnDataSource in ccpnExperiment.dataSources:
            ccpnNumDim = ccpnDataSource.numDim
            for ccpnPeakList in ccpnDataSource.peakLists:
                #Cing doen't like names with '|', like Aria does.
                # TODO decide on better peakList naming and merge uniqueness check
                plName = '%s_%s_%i' % (ccpnExperiment.name, ccpnDataSource.name,
                                       ccpnPeakList.serial)
                peakListName = _checkName(plName, 'Peak')
                peakListName = cingProject.uniqueKey(peakListName)

                pl = cingProject.peaks.new(peakListName, status = 'keep')

                pl.ccpn = ccpnPeakList
                ccpnPeakList.cing = pl

                for ccpnPeak in ccpnPeakList.peaks:
                    ccpnPeakDims = ccpnPeak.sortedPeakDims()
                    ccpnPositions = [pd.value for pd in ccpnPeakDims] #ppm

                    ccpnVolume = ccpnPeak.findFirstPeakIntensity(intensityType =
                                                                  'volume')
                    if ( ccpnVolume ):
                        vValue = ccpnVolume.value or 0.00
                        vError = ccpnVolume.error or 0.00
                    else:
                        vValue = 0.00
                        vError = 0.00
                    # end if

                    if str(vValue) == 'inf':
                        vValue = NaN
                    # end if

                    ccpnHeight = ccpnPeak.findFirstPeakIntensity(intensityType =
                                                                  'height')
                    if ( ccpnHeight ):
                        hValue = ccpnVolume.value or 0.00
                        hError = ccpnVolume.error or 0.00
                    else:
                        hValue = 0.00
                        hError = 0.00
                    # end if
                    if str(hValue) == 'inf':
                        hValue = NaN
                    # end if

                    if not (ccpnVolume or ccpnHeight):
                        NTwarning(" peak '%s' missing both volume and height",
                                  ccpnPeak)
                    # end if

                    resonances = []
                    for peakDim in ccpnPeakDims:
                        resonancesDim = []
                        for contrib in peakDim.peakDimContribs:
                            try:
                                cingResonance=contrib.resonance.findFirstShift \
                                                     (parentList=shiftList).cing
                                #print cingResonance.atom.format()
                                #resonances.append(cingResonance)
                                resonancesDim.append(cingResonance)
                            except:
                                print '==== contrib out ', contrib
                            # end try
                        # end for
                        if ( resonancesDim ):
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

                    peak = Peak( dimension = ccpnNumDim,
                                      positions = ccpnPositions,
                                      volume = vValue, volumeError = vError,
                                      height = hValue, heightError = hError,
                                      resonances = cingResonances )

                    peak.ccpn = ccpnPeak
                    ccpnPeak.cing = peak

                    # stuff PeakList with peaks imported from Ccpn
                    pl.append(peak)
                # end for

                NTmessage("PeakList '%s' imported from Ccpn Nmr project '%s'",
                              peakListName, ccpnNmrProject.name)
                done = True
            # end for
        # end for
    # end for
    if done: return True
    # end if
# end def _setPeaks

def _restraintsValues(constraint):
    '''Descrn: Return upper and lower values for a Ccpn constraint.
       Inputs: Ccpn constraint.
       Output: floats (lower, upper, targetValue, error) or (0, 0, 0, 0)
    '''
    if not constraint:
        return 0, 0, 0, 0
    # end if
    targetValue = constraint.targetValue or 0
    error = constraint.error or 0
    lower = constraint.lowerLimit or targetValue - error
    upper = constraint.upperLimit or targetValue + error

    return lower, upper, targetValue, error
# end def _restraintsValues

def importFromCcpnDistanceRestraints( cingProject = None, ccpnProject = None ):
    '''Descrn: Import distance restraints from Ccpn.Project into Cing.Project.
               As input either Cing.Project instance or Ccpn.Project instance,
               or both, since it'll check if instances has attribute .ccpn or
               .cing, respectively.
               Molecules and Coordinates should be imported previouly.
       Inputs: Ccpn Implementation.Project, Cing.Project instance.
       Output: Cing.DistanceRestraintList or None or error.
    '''

    funcName = importFromCcpnDistanceRestraints.func_name

    ccpnProject = _checkCcpnProject( ccpnProject, cingProject, funcName )
    if not ccpnProject:
        return None
    # end if

    ccpnNmrProject = _checkCcpnNmrProject( ccpnProject, funcName )
    if not ccpnNmrProject:
        return None
    # end if

    listOfDistRestList = []

    # loop over all constraint stores
    for ccpnConstraintStore in ccpnNmrProject.nmrConstraintStores:

        # TODO: Add hBond lists too!
        for ccpnDistanceList in ccpnConstraintStore.findAllConstraintLists \
                                         (className = 'DistanceConstraintList'):

            # TODO: better name for tracking
            ccpnDistanceListName = _checkName( ccpnDistanceList.name,
                                               'DistRestraint' )

            distanceRestraintList = cingProject.distances.new \
                                         (ccpnDistanceListName, status = 'keep')

            ccpnDistanceList.cing = distanceRestraintList
            distanceRestraintList.ccpn = ccpnDistanceList

            for ccpnDistanceConstraint in ccpnDistanceList.constraints:

                lower, upper, _value, _error = _restraintsValues \
                                                        (ccpnDistanceConstraint)

                atomPairs = _getConstraintAtoms(ccpnDistanceConstraint)

                if not atomPairs:
                    # restraints that will not be imported
                    NTmessage("%s: Ccpn distance restraint '%s' without atom pairs",
                              funcName, ccpnDistanceConstraint)
                    continue
                # end if

                distanceRestraint = DistanceRestraint( atomPairs, lower, upper)

                distanceRestraint.ccpn = ccpnDistanceConstraint
                ccpnDistanceConstraint.cing = distanceRestraint

                distanceRestraintList.append(distanceRestraint)
            # end for
            listOfDistRestList.append(distanceRestraintList)
        # end for
    # end for
    return listOfDistRestList
# end def importFromCcpnDistanceRestraints

def importFromCcpnDihedralRestraints( cingProject = None, ccpnProject = None ):
    '''Descrn: Import dihedral restraints from Ccpn.Project into Cing.Project.
               As input either Cing.Project instance or Ccpn.Project instance,
               or both, since it'll check if instances has attribute .ccpn or
               .cing, respectively.
               Molecules and Coordinates should be imported previouly.
       Inputs: Ccpn Implementation.Project, Cing.Project instance.
       Output: Cing.DihedralRestraintList or None or error.
    '''

    funcName = importFromCcpnDihedralRestraints.func_name

    ccpnProject = _checkCcpnProject( ccpnProject, cingProject, funcName )
    if not ccpnProject:
        return None
    # end if

    ccpnNmrProject = _checkCcpnNmrProject( ccpnProject, funcName )
    if not ccpnNmrProject:
        return None
    # end if

    # it should be done only if Ccpn.Project has dihedral constraints
    molSysTorsions = {}
    for molSystem in ccpnProject.molSystems:
        molSysTorsions[molSystem] = createMoleculeTorsionDict(molSystem)
    # end for

    listOfDihRestList = []

    # loop over all constraint stores
    for ccpnConstraintStore in ccpnNmrProject.nmrConstraintStores:

        for ccpnDihedralList in ccpnConstraintStore.findAllConstraintLists \
                                         (className = 'DihedralConstraintList'):
            # TODO: better name
            ccpnDihedralListName = _checkName( ccpnDihedralList.name,
                                               'DihRestraint' )

            dihedralRestraintList = cingProject.dihedrals.new \
                                         (ccpnDihedralListName, status = 'keep')

            ccpnDihedralList.cing = dihedralRestraintList
            dihedralRestraintList.ccpn = ccpnDihedralList

            for ccpnDihedralConstraint in ccpnDihedralList.constraints:
                # TODO merge (dilute) ambig dihedrals
                dihConsItem = ccpnDihedralConstraint.findFirstItem()
                lower, upper, _value, _error = _restraintsValues(dihConsItem)


                atoms = _getConstraintAtoms(ccpnDihedralConstraint)

                if not atoms:
                    # restraints that will not be imported
                    NTmessage( "%s: Ccpn dihedral restraint '%s' without atoms",
                               funcName, ccpnDihedralConstraint )
                    continue
                # end if

                #residue = atoms[2].residue
                # TODO remove angle name - this is generated
#                dihedralName = _getTorsionAngleName(atoms, molSysTorsions)
#                angleName = '%s_%i' % ( dihedralName, residue.resNum )
                #print angleName
                # TODO remove below
#                if dihedralName not in ['PHI', 'PSI']:
#                    if lower < 0.0:
#                        lower += 360
#                    # end if
#                    if upper < 0.0:
#                        upper += 360
#                    # end if
#                # end if

                #10/10/07 angle and residue parameters are no longer mandatory
                dihedralRestraint = DihedralRestraint( atoms, lower, upper)#,
#                                                            residue = residue,
#                                                            angle = angleName )

                dihedralRestraint.ccpn = ccpnDihedralConstraint
                ccpnDihedralConstraint.cing = dihedralRestraint

                dihedralRestraintList.append(dihedralRestraint)
            # end for
            listOfDihRestList.append(dihedralRestraintList)
        # end for
    # end for
    return listOfDihRestList
# end def importFromCcpnDihedralRestraints

def importFromCcpnRdcRestraints( cingProject = None, ccpnProject = None ):
    '''Descrn: Import RDC restraints from Ccpn.Project into Cing.Project.
               As input either Cing.Project instance or Ccpn.Project instance,
               or both, since it'll check if instances has attribute .ccpn or
               .cing, respectively.
               Molecules and Coordinates should be imported previouly.
       Inputs: Ccpn Implementation.Project, Cing.Project instance.
       Output: Cing.RdcRestraintList or None or error.
    '''

    funcName = importFromCcpnRdcRestraints.func_name

    ccpnProject = _checkCcpnProject( ccpnProject, cingProject, funcName )
    if not ccpnProject:
        return None
    # end if

    ccpnNmrProject = _checkCcpnNmrProject( ccpnProject, funcName )
    if not ccpnNmrProject:
        return None
    # end if

    listOfRdcRestList = []

    # loop over all constraint stores
    for ccpnConstraintStore in ccpnNmrProject.nmrConstraintStores:

        for ccpnRdcList in ccpnConstraintStore.findAllConstraintLists \
                                         (className = 'RdcConstraintList'):
            # TODO better name
            ccpnRdcListName = _checkName( ccpnRdcList.name, 'RdcRestraint' )

            rdcRestraintList = cingProject.rdcs.new \
                                         (ccpnRdcListName, status = 'keep')

            ccpnRdcList.cing = rdcRestraintList
            rdcRestraintList.ccpn = ccpnRdcList

            for ccpnRdcConstraint in ccpnRdcList.constraints:

                lower, upper, _value, _error = _restraintsValues \
                                                        (ccpnRdcConstraint)
                atomPairs = _getConstraintAtoms(ccpnRdcConstraint)

                if not atomPairs:
                    # restraints that will not be imported
                    NTmessage("%s: Ccpn RDC restraint '%s' without atom pairs",
                              funcName, ccpnRdcConstraint)
                    continue
                # end if

                rdcRestraint = RDCRestraint( atomPairs, lower, upper )

                rdcRestraint.ccpn = ccpnRdcConstraint
                ccpnRdcConstraint.cing = rdcRestraint

                rdcRestraintList.append(rdcRestraint)
            # end for
            listOfRdcRestList.append(rdcRestraintList)
        # end for
    # end for
    return listOfRdcRestList
# end def importFromCcpnRdcRestraints

def _getTorsionAngleName(atoms, molSysTorsions):
    """Descrn: Get torsion angle name according IUPAC for a set of 4 atoms.
       Inputs: a list of 4 Cing.Atoms.
       Output: string (e.g.: PHI), error or None
       DEPRECATED
    """

    #atom1, atom2, atom3, atom4 = atoms
    #s1 = set([i.name for i in atom1.ccpn.chemAtom.chemTorsions]).intersection(
    #         set([i.name for i in atom2.ccpn.chemAtom.chemTorsions]))
    #s2 = set([i.name for i in atom3.ccpn.chemAtom.chemTorsions]).intersection(
    #         set([i.name for i in atom4.ccpn.chemAtom.chemTorsions]))
    #angle = s1.intersection(s2)
    #print angle
    #return angle.pop()

    _atom1, _atom2, atom3, _atom4 = atoms
    molSystem = atom3.ccpn.residue.chain.molSystem #getTopObject()
    ccpnMol = atom3.ccpn.residue.chain.molecule
    ccpnRes = atom3.ccpn.residue.molResidue

    #print'---', [i.name for i in atoms]

    chemAtoms = [i.ccpn.chemAtom for i in atoms]

    matchPatterns = {'forward': {}, 'backward': {}, 'forward_inout': {}, 'backward_inout': {}}
    matchInfo = (('forward', (0, 1, 2, 3)), ('backward', (3, 2, 1, 0)), ('forward_inout', (1, 0, 3, 2)), ('backward_inout', (2, 3, 0, 1)))
    torsion = None

    for (torsion, atomList) in molSysTorsions[molSystem][ccpnMol][ccpnRes]:
        #print '===', torsion.name, [i[1].name for i in atomList]
        #break
        for (matchType, matchIndexes) in matchInfo:

            match = ""

            for i in range(0, 4):
                caIndex = matchIndexes[i]
                #print "asdfasfasdfasfas", chemAtoms[caIndex], atomList[i][1]
                #print '***', chemAtoms[caIndex].name, atomList[i][1].name
                if chemAtoms[caIndex] == atomList[i][1]:
                    match += "1"
                else:
                    match += "0"
                # end if
            # end for
            #print matchType, match, torsion.name
            if match == '1111':
                # All is fine...
                matchPatterns = {}
                break
            else:
                matchPatterns[matchType][match] = torsion
            # end if
        # end for

        if not matchPatterns:
            break
        # end if
    # end for

    #print match
    if 'CHI' in torsion.name:
        torsionName = torsion.name[:4]
    else:
        torsionName = torsion.name
    # end if
    return torsionName

    if matchPatterns or not torsion:

        torsion = None

        for pattern in ("0111", "1110", "0110"):
            for (matchType, matchIndexes) in matchInfo:
                if matchPatterns[matchType].has_key(pattern):
                    NTmessage('Fixed atoms order for torsional angle')
                    torsion = matchPatterns[matchType][pattern]

                    if matchType[:8] == 'backward':
                        chemAtoms.reverse()
                    # end if

                    if matchType[-5:] == 'inout':
                        tca = chemAtoms[:]
                        chemAtoms[0] = tca[1]
                        chemAtoms[1] = tca[0]
                        chemAtoms[2] = tca[3]
                        chemAtoms[3] = tca[2]
                    # end if
                # end if
            # end for
            break
        # end for
    # end if

    if torsion:
        NTmessage('Torsinal angle not matched')
        print match
    # end if
    if hasattr(torsion, 'name'):
        if 'CHI' in torsion.name:
            torsionName = torsion.name[:4]
        else:
            torsionName = torsion.name
        # end if
        return torsionName
    # end if
    else:
        return None
    # end if
# end def _getTorsionAngleName

def _getConstraintAtoms(ccpnConstraint):
    """Descrn: Get the atoms that may be assigned to the constrained resonances.
       Inputs: NmrConstraint.AbstractConstraint.
       Output: List of Cing.Atoms, tupled Cing.Atoms pairs or [].
    """

    atoms = set()
    fixedResonances = []
    className = ccpnConstraint.className

    if className == 'DihedralConstraint':
        fixedResonances.append(ccpnConstraint.resonances)

    elif className == 'ChemShiftConstraint':
        fixedResonances.append([ccpnConstraint.resonance, ])

    else:
        for item in ccpnConstraint.items:
            fixedResonances.append(item.resonances)
        # end for
    # end if

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
                            NTmessage("No Cing atom obj equivalent for Ccpn atom: %s", atom.name)
                        # end if
                    # end for
                # end for

                atomList.append(equivAtoms.keys())
            # end if
        # end for

        if len(atomList) == len(fixedResonanceList):
            if className == 'DihedralConstraint':
                try:
                    atoms = [ x[0].cing for x in atomList ]
                except:
                    NTmessage("No Cing atom obj equivalent for Ccpn atom list", atomList)
                # end try
            elif className in ['DistanceConstraint', 'RdcConstraint']:
                for ccpnAtom1 in atomList[0]:
                    for ccpnAtom2 in atomList[1]:
                        try:
                            atom1, atom2 = ccpnAtom1.cing, ccpnAtom2.cing
                        except:
                            NTmessage("No Cing atom obj equivalent for Ccpn atoms %s and %s", ccpnAtom1.name, ccpnAtom2.name)
                            continue
                        # end try
                        atom1 = atom1.pseudoAtom() or atom1
                        atom2 = atom2.pseudoAtom() or atom2
                        if atom1 != atom2:
                            aset, arset = set(), set()
                            atomPair = (atom1, atom2)
                            aset.add(atomPair)
                            atomPairRev = (atom2, atom1)
                            arset.add(atomPairRev)
                            if not atoms.issuperset(aset) and not atoms.issuperset(arset):
                                atoms.add(atomPair)
                            # end if
                        # end if
                    # end for
                # end for
            else:
                NTmessage("Type of constraint '%s' not recognised", className)
            # end if
        # end if
    # end for
    return list(atoms)
# end def _getConstraintAtoms

def _checkName(name, prefix='CING'):
    '''Descrn: For checking string names from Ccpn.Project.
               If 'name' start with a digit, 'CING_' will prefix 'name'.
               Cing doesn't like names starting with digits, spaces neither '|'.
       Inputs: a string 'name'.
       Output: same string 'name', 'prefix' + string 'name' or
               just 'prefix' if 'name' = None
    '''

    if not name:
        if name[0] in digits:
            name = prefix + '_' + name
        else:
            name = prefix
        # end if
    # end if

    name = name.replace('|', '_')
    name = name.replace(' ', '_')
    name = name.replace('.', '_')
    name = name.replace('+', '_')

    return name
# end def _checkName

def createCcpn( cingProject = None ):
    '''Descrn: Create a new Ccpn project and associates it to a Cing.Project.
       Inputs: Cing.Project instance.
       Output: Ccpn Implementation.Project.
    '''

    funcName = createCcpn.func_name

    _checkCingProject( cingProject, funcName )
    if not cingProject:
        return None
    # end if

    #TODO: Check CING to CCPN link before making new

    #create ccpnProject
    # First you always have to create a project (this is the root object)
    projectName = cingProject.name
    ccpnDir = os.path.abspath(cingProject.path(cingProject.directories.ccpn))
    ccpnProject = genIo.newProject(projectName, path=ccpnDir)
#        ccpnProject = MemopsRoot(name = projectName)
    ccpnProject.newNmrProject(name = ccpnProject.name)

    cingProject.ccpn = ccpnProject
    ccpnProject.cing = cingProject

    #createCcpnMolecules( cingProject )
    #createCcpnStructures( cingProject )
    #createCcpnRestraints( cingProject )

    # TODO: check about saveModified()
    ccpnProject.saveAll()

    return ccpnProject
# end def createCcpn

def createCcpnMolecules( cingProject = None, ccpnProject = None,
                         moleculeName = None ):
    '''Descrn: create from Cing.Molecule a molSystem into a existing
               Ccpn project instance.
       Inputs: Ccpn Implementation.Project, Cing.Project instance,
               moleculeName (string).
       Output: Ccpn Implementation.Project or None or error.
    '''

    funcName = createCcpnMolecules.func_name

    ccpnProject = _checkCcpnProject( ccpnProject, cingProject, funcName )
    if not ccpnProject:
        return None
    # end if

    moleculeList = [] #@UnusedVariable

    #if 'moleculeName' is not specified, it'll export all Cing.Molecules
    if ( moleculeName ):

        listMolecules = [cingProject[moleculeName]]

        if ( not listMolecules ):
            NTerror( " '%s': molecule '%s' not found in Cing.Project",
                     funcName, moleculeName )
            return None
        # end if
    else:
        listMolecules = [ cingProject[mol] for mol in cingProject.moleculeNames ]
    # end if

    for molecule in listMolecules:

        # add molecule from Cing to Ccpn
        # Cing.Molecule <=> molSystem
        # Cing.Chain <=> ccpnMolSys
        moleculeName = molecule.name

        molSystem = ccpnProject.newMolSystem(code = moleculeName, name = moleculeName)

        molSystem.cing = molecule
        molecule.ccpn = molSystem

#        ccpnChains = []
        for chain in molecule.chains:

            moleculeChainName = moleculeName+'_'+chain.name

            #ccpnMolSys = ccpnProject.newMolecule(name = moleculeChainName)
            sequence = [ res.name for res in chain ]
            ccpnMolSys = makeMolecule(ccpnProject,'protein',
                                molName = moleculeChainName, sequence=sequence )

            ccpnChain = molSystem.newChain(code = chain.name,
                                         molecule = ccpnMolSys)
            ccpnChain.cing = chain
            chain.ccpn = ccpnChain

            index = 0
            for ccpnResidue in ccpnChain.residues:
                residue = sequence[index]

                ccpnResidue.cing = residue
                residue.ccpn = ccpnResidue
                _ccpnAtom2CingAndCoords( molecule, ccpnResidue, chain.name )
                index += 1
            # end for
            NTmessage( "Cing.Chain '%s' of Cing.Molecule '%s' exported to Ccpn.Project", chain.name, moleculeName )
        # end for
    # end for
    return ccpnProject
# end def createCcpnMolecules

def createCcpnStructures( cingProject = None, ccpnProject = None,
                          moleculeName = None ):
    '''Descrn: create Ccpn.molStructures from Cing.Coordinates into a existing
               Ccpn project instance.
       Inputs: Ccpn Implementation.Project, Cing.Project instance,
               moleculeName (string).
       Output: Ccpn Implementation.Project or None or error.
    '''

    funcName = createCcpnStructures.func_name

    ccpnProject = _checkCcpnProject( ccpnProject, cingProject, funcName )
    if not ccpnProject:
        return None
    # end if

    moleculeList = [] #@UnusedVariable

    #if 'moleculeName' is not specified, it'll export all Cing.Molecules
    if ( moleculeName ):

        listMolecules = [cingProject[moleculeName]]

        if ( not listMolecules ):
            NTerror( " '%s': molecule '%s' not found in Cing.Project",
                     funcName, moleculeName )
            return None
        # end if

    else:
        listMolecules = [ cingProject[mol] for mol in cingProject.moleculeNames ]
    # end if

    ensembleId = 0 # ccpn 2.x
    for molecule in listMolecules:
        ensembleId += 1 #ccpn 2.x
        if molecule.modelCount == 0: continue
        # end if

        molSystem = molecule.ccpn
        structureEnsemble = ccpnProject.newStructureEnsemble(molSystem=molSystem, ensembleId=ensembleId)
        for modelIndex in range(molecule.modelCount):
            structureEnsemble.newModel()
        # end for
        models = structureEnsemble.sortedModels()

        for chain in molecule.chains:
            ccpnChain = chain.ccpn

            coordChain = structureEnsemble.newChain(code = ccpnChain.pdbOneLetterCode)

            for residue in chain.allResidues():
                ccpnResidue = residue.ccpn
                coordResidue = coordChain.newResidue(seqCode = ccpnResidue.seqCode,
                                                      seqId =  ccpnResidue.seqId)
                for atom in residue.allAtoms():
                    if not atom.coordinates:
                        NTwarning("Skipping atom because no coordinates were found.")
                        NTwarning('atom: '+atom.format())
                        continue
                    # end if
                    if not atom.has_key('ccpn'):
                        NTwarning("Skipping atom because no ccpn attribute was found to be set")
                        NTwarning('atom: '+atom.format())
                        continue
                    # end if
                    ccpnAtom = atom.ccpn
                    coordAtom = coordResidue.newAtom(name = ccpnAtom.name)
                    for modelIndex in range(molecule.modelCount):
                        x = atom.coordinates[modelIndex][0]
                        y = atom.coordinates[modelIndex][1]
                        z = atom.coordinates[modelIndex][2]
                        occupancy = atom.coordinates[modelIndex][4]
                        bFactor = atom.coordinates[modelIndex][3]
                        c = coordAtom.newCoord(x=x, y=y, z=z,model=models[modelIndex])
                        c.setOccupancy(occupancy)
                        c.setBFactor(bFactor)
                    # end for
                # end for
            # end for
        # end for
    # end for

    return ccpnProject
# end def createCcpnStructures

def createCcpnRestraints( cingProject = None, ccpnProject = None ):
    '''Descrn: create ccp.nmr.NmrConstraint.xxxConstraintList from
               Cing.xxxRestraintList into a existing
               Ccpn project instance.
       Inputs: Ccpn Implementation.Project, Cing.Project instance.
       Output: Ccpn Implementation.Project or None or error.
    '''

    #from ccpnmr.analysis.ConstraintBasic import makeNmrConstraintStore

    funcName = createCcpnRestraints.func_name

    ccpnProject = _checkCcpnProject( ccpnProject, cingProject, funcName )
    if not ccpnProject:
        return None
    # end if

    ccpnNmrProject = ccpnProject.currentNmrProject

    ccpnConstraintStore = _makeNmrConstraintStore(ccpnNmrProject)

    for distanceRestraintList in cingProject.distances:
        ccpnDistanceList = ccpnConstraintStore.newDistanceConstraintList( name =
                                                    distanceRestraintList.name )
        for distanceRestraint in distanceRestraintList:
            ccpnDistanceConstraint = ccpnDistanceList.newDistanceConstraint( #@UnusedVariable
                                           lowerLimit = distanceRestraint.lower,
                                           upperLimit = distanceRestraint.upper)
            #print distanceRestraint.atomPairs[0][0].ccpn
        # end for
    # end for

    for dihedralRestraintList in cingProject.dihedrals:
        ccpnDihedralList = ccpnConstraintStore.newDihedralConstraintList( name = #@UnusedVariable
                                                    dihedralRestraintList.name )
        for dihedralRestraint in dihedralRestraintList: #@UnusedVariable
            pass
            #ccpnDihedralList.newDihedralConstraint()
        # end for
    # end for
    return ccpnProject
# end def createCcpnRestraints

def _isRootDirectory(f=""):
    """ Algorithm for finding just the root dir
    TODO: check with ccpn crowd.
    """
#        linkNmrStarData/
#        linkNmrStarData/ccp/

#    NTdebug("Checking _isRootDirectory on : ["+f+"]")
    if f.count("/") != 2: 
        return False
    if f.count("//") != 1: 
        return False
    n = len(f)
    if f[n-1] != '/':
        return False
    if n == 2:
        NTerror("Found a // entry in tar file.")
        return None
    return True

def _trimTrailingSlash(f):
#DEBUG: Checking _isRootDirectory on : [linkNmrStarData//]
#DEBUG: Checking _isRootDirectory on : [linkNmrStarData/ccp//]
#DEBUG: Checking _isRootDirectory on : [linkNmrStarData/ccp/nmr//]
#    n = len(f)
#    if f[len(f)-1] != '/':
#        return f
    r = f[:-2]
    NTdebug("Found RootDirectory: [" + r + "]")
    return r # because of check in _isRootDirectory the length of f is at least 3

def _makeNmrConstraintStore(nmrProject):
    '''Descrn: Make a new NMR constraint head object for a project which will
               contain constraints and violations.
               Sets up a strorage so that the NmrConstraint package data is
               stored in its own XML file.
       Inputs: Nmr.NmrProject
       Output: Nmr.NmrConstraintStore
    '''
    # adapted from ccpnmr.analysis.ConstraintBasic
    # it probably doesn't work for ccpn 2.x

    project = nmrProject.root

    url = project.findFirstStorage(package='ccp.nmr.Nmr').url

    if not os.path.exists(url.path):
        os.makedirs(url.path)
    # end if
    if not os.path.exists(url.path + '/ccp/'):
        os.makedirs(url.path + '/ccp/')
    # end if
    if not os.path.exists(url.path + '/ccp/NmrConstraint/'):
        os.makedirs(url.path + '/ccp/NmrConstraint/')
    # end if

    dict = nmrProject.__dict__.get('serialDict') or {} #hack
    if dict.get('nmrConstraintStores') is None:
        # need to make sure that the Nmr package is loaded and that we have a serialDict
        _nmrConstraintStores = project.nmrConstraintStores
    # end if

    n = dict.get('nmrConstraintStores', 0) + 1

    _dataPath = 'ccp/NmrConstraint/NmrConstraint_%d.xml' % (n)
    storage   = None #ContentStorage( project,package='ccp.nmr.NmrConstraint', path=dataPath, url=url )
    nmrConstraintStore = nmrProject.newNmrConstraintStore( contentStorage = storage )
    nmrConstraintStore.quickResonances = {}
    nmrConstraintStore.quickAtomSets   = {}

    return nmrConstraintStore
# end def _makeNmrConstraintStore

# register the functions
methods  = [(loadCcpn, None),
            (initCcpn, None),
            (importFromCcpn, None),
            (importFromCcpnMolecules, None),
            (importFromCcpnCoordinates, None),
            (importFromCcpnPeaksAndShifts, None),
            (importFromCcpnDistanceRestraints, None),
            (importFromCcpnDihedralRestraints, None),
            (importFromCcpnRdcRestraints, None),
            (createCcpn, None),
            (createCcpnMolecules, None)
           ]
#saves    = []
#restores = []
#exports  = [( ,None)]
