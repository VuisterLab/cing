"""
Adds initialize/import/export from/to PDB files


Methods:
    Molecule.importFromPDB( pdbFile, convention='PDB')   :
        Import coordinates from pdbFile
        convention eq PDB, CYANA, CYANA2 or XPLOR
        return molecule or None on error

    Molecule.PDB2Molecule(pdbFile, moleculeName, convention)   :
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
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTpath
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import sprintf
from cing.core.constants import CYANA
from cing.core.constants import CYANA2
from cing.core.constants import IUPAC
from cing.core.dictionaries import NTdbGetAtom
from cing.core.molecule import Chain
from cing.core.molecule import Molecule
from cing.core.molecule import ensureValidChainId
import pdb
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

    NTdetail('==> Parsing pdbFile "%s" ... ', pdbFile )
    if not os.path.exists(pdbFile):
        NTerror('importFromPDB: missing PDB-file "%s"', pdbFile)

    pdb = PyMMLib.PDBFile( pdbFile)

#    atomDict = molecule._getAtomDict(convention)

    foundModel = False
    modelCount = 0
    for record in pdb:
        recordName = record._name.strip()
        if  recordName == 'REMARK':
            continue
        if recordName == "MODEL":
            foundModel = True
            continue
        if recordName == "ENDMDL":
            modelCount += 1
            if nmodels and modelCount >= nmodels:
                break
            continue
        if recordName == "ATOM" or recordName == "HETATM":
            # see if we can find a definition for this residue, atom name in the database
            if convention == CYANA:
                # the residue names are in Cyana1.x convention (i.e. for GLU-)
                # atm names of the Cyana1.x PDB files are in messed-up Cyana format
                atmName = record.name[1:4] + record.name[0:1]
            elif convention == CYANA2:
                # the residue names are in Cyana2.x convention (i.e. for GLU)
                # atm names of the Cyana2.x PDB files are in messed-up Cyana format
                atmName = record.name[1:4] + record.name[0:1]
            else:
                atmName = record.name
            # Not all PDB files have chainID's !@%^&*
            # Actually, they do. It might be an space character though.
            # It's important to save it as is otherwise the residue number
            # is no longer a unique key within the chain. E.g. HOH in 1n62
            # has a space character for the chain id and similar residue
            # numbering as the protein sequence in chain A.
            chainId = Chain.defaultChainId
            if record.has_key('chainID'):
                chainId = record.chainID.strip()
                chainId = ensureValidChainId(chainId)
#                print '>chain>', '>'+chainId+'<', len(chainId)

            resID = record.resSeq
#            if chainId == Chain.defaultChainId:
#                # use the atomDict
#                t = (resID, atmName)
#                if atomDict.has_key(t):
#                    atom = atomDict[t]
#                else:
#                    atom = None
#            else:
            atom  = molecule.decodeNameTuple( (convention, chainId, resID, atmName) )

            if not atom:
                NTerror('cing.PluginCode.pdb#importFromPDB: %s, model %d incompatible record (%s)',
                         convention, modelCount, record )
                #print '>>', convention, cname, resID, atmName
                continue
            atom.addCoordinate( record.x, record.y, record.z, Bfac=record.tempFactor )
        #end if
    #end for

    # Patch to get modelCount right for X-ray or XPLOR structures with only one model
    if not foundModel:
        modelCount += 1

    molecule.modelCount += modelCount

    NTdetail( 'importFromPDB: read %d records; added %d structure models', len(pdb), modelCount )
    #end if

    del( pdb )

    return molecule
#end def
# Add as a method to Molecule class
Molecule.importFromPDB = importFromPDB

def _PDB2Molecule( recordList, moleculeName, convention=IUPAC ):
    """
    Generate a new molecule from PyMMLib record list of parsed PDB records
    """

    # Residue names that are ambigously defined by different PDB files
    checks = NTdict( #@UnusedVariable
        HIS = NTdict( atoms = ['HE2', 'HD1'],
                      HIS   = ['HD1'],
                      HISE  = ['HE2'],
                      HISH  = ['HE2', 'HD1']
                    ),
        GLU = ['HE2'],
        ASP = ['HD2'],
    )

    maps = NTdict( #@UnusedVariable

    )

    mol = Molecule( name=moleculeName )

    foundModel = False #@UnusedVariable
    lastResidue = None #@UnusedVariable
    lastChain   = None #@UnusedVariable

    for record in pdb:
        recordName = record._name.strip()
        if  recordName == 'REMARK':
            continue # JFD: this used to be a pass but that's weird.

        if recordName == "MODEL":
            foundModel = True #@UnusedVariable
            continue
        if recordName == "ENDMDL":
            break

        if recordName == "ATOM" or recordName == "HETATM":

            # Not all PDB files have chainID's !@%^&*
            # They do; if none returned then take the space that is always present!
            chainId = Chain.defaultChainId
            if record.has_key('chainID'):
                chainId = record.chainID.strip()
                chainId = ensureValidChainId(chainId)


            # Skip records with a
            # see if we can find a definition for this residue, atom name in the database
            a = record.name
            a = a.strip() # this improved reading 1y4o
            if convention == CYANA or convention == CYANA2:
                # the residue names are in Cyana1.x convention (i.e. for GLU-)
                # atm names of the Cyana1.x PDB files are in messed-up Cyana format
                # So: 1HD2 becomes HD21 where needed:
                a = moveFirstDigitToEnd(a)
            # strip is already done in function
            atm = NTdbGetAtom( record.resName, a, convention )


            # JFD adds to just hack these debilitating simple variations.
            if not atm: # some besides cyana have this too; just too easy to hack here
#                print "Atom ["+a+"] was mismatched at first"
                a = moveFirstDigitToEnd(a)
                atm = NTdbGetAtom( record.resName, a, convention )
            if not atm:
                if a == 'H': # happens for 1y4o_1model reading as cyana but in cyana we have hn for INTERNAL_0
                    a = 'HN'
                elif a == 'HN': # for future examples.
                    a = 'H'
                atm = NTdbGetAtom( record.resName, a, convention )
            if not atm:
                if shownWarnings <= showMaxNumberOfWarnings: #@UndefinedVariable
                    NTwarning('PDB2Molecule: %s format, model %d incompatible record (%s)' % (
                             convention, mol.modelCount+1, record))
                    if shownWarnings == showMaxNumberOfWarnings: #@UndefinedVariable
                        NTwarning('And so on.')
                    shownWarnings += 1 #@UndefinedVariable
                continue
            if atm.residueDef.hasProperties('cyanaPseudoResidue'):
                # skip CYANA pseudo residues
                continue

            # we did find a match in the database
            # Not all PDB files have chainID's !@%^&*
            # They do; if none returned then take the space that is always present!
            chainId = Chain.defaultChainId
            if record.has_key('chainID'):
                chainId = record.chainID.strip()
                chainId = ensureValidChainId(chainId)

            resID    = record.resSeq
            resName  = atm.residueDef.name
            fullName = resName+str(resID)
            atmName  = atm.name

            # check if this chain,fullName,atmName already exists in the molecule
            # if not, add chain or residue
            if not chainId in mol:
                mol.addChain( chainId )
            #end if

            if not fullName in mol[chainId]:
                res = mol[chainId].addResidue( resName, resID )
                res.addAllAtoms()
            #end if

            atom = mol[chainId][fullName][atmName]

            # Check if the coordinate already exists for this model
            # This might happen when alternate locations are being
            # specified. Simplify to one coordinate per model.
            numCoorinates = len(atom.coordinates)
            numModels     = mol.modelCount + 1 # current model counts already
            if numCoorinates < numModels:
                atom.addCoordinate( record.x, record.y, record.z, Bfac=record.tempFactor )
            else:
                NTwarning('Skipping duplicate coordinate within same record (%s)' % record)
        #end if
    #end for
    if shownWarnings: #@UndefinedVariable
        NTwarning('Total number of warnings: ' + `shownWarnings`) #@UndefinedVariable

    NTdetail( '==> _PDB2Molecule: new Molecule %s from %s', mol, pdbFile ) #@UndefinedVariable
    return mol
#end def

def PDB2Molecule( pdbFile, moleculeName, convention=IUPAC, nmodels=None)   :
    """Initialize  Molecule 'moleculeName' from pdbFile
       convention eq PDB, CYANA, CYANA2 or XPLOR, IUPAC
       optionally only include nmodels

       Return molecule instance or None on error
    """
    showMaxNumberOfWarnings = 100 # was 100
    shownWarnings = 0

    if not os.path.exists(pdbFile):
        NTerror('PDB2Molecule: missing PDB-file "%s"', pdbFile)
        return None

    NTdetail('==> Parsing pdbFile "%s" ... ', pdbFile )

    pdb = PyMMLib.PDBFile( pdbFile )
    mol = Molecule( name=moleculeName )

#    mol.pdb = pdb
    mol.modelCount  = 0
    foundModel = False

    for record in pdb:
        recordName = record._name.strip()
        if  recordName == 'REMARK':
            continue # JFD: this used to be a pass but that's weird.

        if recordName == "MODEL":
            foundModel = True
            continue
        if recordName == "ENDMDL":
            mol.modelCount += 1
            if nmodels and (mol.modelCount >= nmodels):
                break
            continue

        if recordName == "ATOM" or recordName == "HETATM":
            # Skip records with a
            # see if we can find a definition for this residue, atom name in the database
            a = record.name
            a = a.strip() # this improved reading 1y4o
            if convention == CYANA or convention == CYANA2:
                # the residue names are in Cyana1.x convention (i.e. for GLU-)
                # atm names of the Cyana1.x PDB files are in messed-up Cyana format
                # So: 1HD2 becomes HD21 where needed:
                a = moveFirstDigitToEnd(a)
            # strip is already done in function
            atm = NTdbGetAtom( record.resName, a, convention )


            # JFD adds to just hack these debilitating simple variations.
            if not atm: # some besides cyana have this too; just too easy to hack here
#                print "Atom ["+a+"] was mismatched at first"
                a = moveFirstDigitToEnd(a)
                atm = NTdbGetAtom( record.resName, a, convention )
            if not atm:
                if a == 'H': # happens for 1y4o_1model reading as cyana but in cyana we have hn for INTERNAL_0
                    a = 'HN'
                elif a == 'HN': # for future examples.
                    a = 'H'
                atm = NTdbGetAtom( record.resName, a, convention )
            if not atm:
                if shownWarnings <= showMaxNumberOfWarnings:
                    NTwarning('PDB2Molecule: %s format, model %d incompatible record (%s)' % (
                             convention, mol.modelCount+1, record))
                    if shownWarnings == showMaxNumberOfWarnings:
                        NTwarning('And so on.')
                    shownWarnings += 1
                continue
            if atm.residueDef.hasProperties('cyanaPseudoResidue'):
                # skip CYANA pseudo residues
                continue

            # we did find a match in the database
            # Not all PDB files have chainID's !@%^&*
            # They do; if none returned then take the space that is always present!
            chainId = Chain.defaultChainId
            if record.has_key('chainID'):
                chainId = record.chainID.strip()
                chainId = ensureValidChainId(chainId)

            resID    = record.resSeq
            resName  = atm.residueDef.name
            fullName = resName+str(resID)
            atmName  = atm.name

            # check if this chain,fullName,atmName already exists in the molecule
            # if not, add chain or residue
            if not chainId in mol:
                mol.addChain( chainId )
            #end if

            if not fullName in mol[chainId]:
                res = mol[chainId].addResidue( resName, resID )
                res.addAllAtoms()
            #end if

            atom = mol[chainId][fullName][atmName]

            # Check if the coordinate already exists for this model
            # This might happen when alternate locations are being
            # specified. Simplify to one coordinate per model.
            numCoorinates = len(atom.coordinates)
            numModels     = mol.modelCount + 1 # current model counts already
            if numCoorinates < numModels:
                atom.addCoordinate( record.x, record.y, record.z, Bfac=record.tempFactor )
            else:
                NTwarning('Skipping duplicate coordinate within same record (%s)' % record)
        #end if
    #end for
    if shownWarnings:
        NTwarning('Total number of warnings: ' + `shownWarnings`)

    # Patch to get modelCount right for X-ray structures with only one model
    if not foundModel:
        mol.modelCount += 1
    NTdetail( '==> PDB2Molecule: new Molecule %s from %s', mol, pdbFile )
    # delete the PyMMlib pdbFile instance # JFD: why?
    del(pdb)
    return mol
#end def
# Add as a staticmethod to Molecule class
Molecule.PDB2Molecule = staticmethod( PDB2Molecule )


def moleculeToPDBfile( molecule, path, model=None, convention=IUPAC, max_models = None):
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
    pdbFile = molecule.toPDB( model=model, convention = convention, max_models = max_models)
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
    molecule = PDB2Molecule( pdbFile, name, convention = convention, nmodels=nmodels)
    if not molecule:
        NTerror('Project.initPDB: failed parsing PDB-file "%s"', pdbFile)
        return None
    #end if
    project.appendMolecule( molecule )
    if update:
        project.molecule.updateAll()
#        project.dssp()   # TODO: move these calls toproject.molecule.updateAll()
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

    project.molecule.updateAll()
    project.dssp()     # TODO: move these calls toproject.molecule.updateAll()
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
