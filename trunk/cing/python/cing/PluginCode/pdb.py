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
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTpath
from cing.Libs.NTutils import sprintf
from cing.core.constants import CYANA
from cing.core.constants import CYANA2
from cing.core.constants import IUPAC
from cing.core.dictionaries import NTdbGetAtom
from cing.core.molecule import Molecule
from cing.Libs.NTutils import NTwarning
from cing.core.molecule import Chain
from cing.core.molecule import ensureValidChainId
#import string

#==============================================================================
# PDB stuff
#==============================================================================
def importFromPDB( molecule, pdbFile, convention='PDB', nmodels=None)   :
    """Import coordinates from pdbFile (optionally: first nmodels)
convention eq PDB, CYANA, CYANA2 or XPLOR
return molecule or None on error
    """
    if not molecule: return None

    NTmessage('==> Parsing pdbFile "%s" ... ', pdbFile ) 
           
    #end if
    
    pdb = PyMMLib.PDBFile( pdbFile)   
#    molecule.pdb = pdb; no longer save it: it eats massive memory and we don't use it
    
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
                
            resID = record.resSeq
            atom  = molecule.decodeNameTuple( (convention, chainId, resID, atmName) )

            if not atom:
                NTerror('WARNING in cing.PluginCode.pdb#importFromPDB: %s, model %d incompatible record (%s)\n', 
                         convention, modelCount, record )                         
                #print '>>', convention, cname, resID, atmName
                continue
            atom.addCoordinate( record[0], record[1], record[2], record[3] )
            record.atom = atom
            atom.pdbRecord = record
                
    
    # Patch to get modelCount right for X-ray or XPLOR structures with only one model
    if not foundModel: 
        modelCount += 1
    #end if
    molecule.modelCount += modelCount
    
    NTmessage( 'read %d records; added %d structure models', len(pdb), modelCount )  
    #end if
    
    del( pdb )

    return molecule
#end def
# Add as a method to Molecule class
Molecule.importFromPDB = importFromPDB

def PDB2Molecule( pdbFile, moleculeName, convention, nmodels=None)   :
    """Initialize  from pdbFile
Return molecule instance
convention eq PDB, CYANA, CYANA2 or XPLOR, BMRB
    """
    showMaxNumberOfWarnings = 100 # was 100
    shownWarnings = 0
    NTmessage('==> Parsing pdbFile "%s" ... ', pdbFile ) 
    
    pdb = PyMMLib.PDBFile( pdbFile )
    mol = Molecule( name=moleculeName )
    
#    mol.pdb = pdb
    mol.modelCount  = 0
    foundModel = False
    
    for record in pdb:
        recordName = record._name.strip()        
        if  recordName == 'REMARK':
            pass
        
        if recordName == "MODEL":
            foundModel = True
            continue
        if recordName == "ENDMDL":
            mol.modelCount += 1
            if nmodels and mol.modelCount >= nmodels:
                break
            continue
         
        if recordName == "ATOM" or recordName == "HETATM":
            # Skip records with a 
            # see if we can find a definition for this residue, atom name in the database
            a = record.name
            if convention == CYANA or convention == CYANA2:
                # the residue names are in Cyana1.x convention (i.e. for GLU-)
                # atm names of the Cyana1.x PDB files are in messed-up Cyana format
                # So: 1HD2 becomes HD21 where needed:
                a = moveFirstDigitToEnd(a)
            # strip is already done in function
            atm = NTdbGetAtom( record.resName, a, convention )
            if not atm:
                if shownWarnings <= showMaxNumberOfWarnings:
                    NTwarning('in #PDB2Molecule: %s, model %d incompatible record (%s)' % (
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
        #end if
    #end for
    if shownWarnings:
        NTwarning('Total number of warnings: ' + `shownWarnings`)
    
    # Patch to get modelCount right for X-ray structures with only one model
    if not foundModel: 
        mol.modelCount += 1
    NTmessage( '==> PDB2Molecule: completed, added %d structure models', mol.modelCount )  
    # delete the PyMMlib pdbFile instance # JFD: why?
    del(pdb)
    return mol
#end def
# Add as a staticmethod to Molecule class
Molecule.PDB2Molecule = staticmethod( PDB2Molecule )


def moleculeToPDBfile( molecule, path, model=None, convention=IUPAC):
    """
    Save a molecule instance to PDB file.
    Convention eq PDB, CYANA, CYANA2, XPLOR.
    
    For speedup reasons, this routine should be explicitly coded.
    This routine should eventually replace toPDB.
    
    NB model should be 1 for the first model. Not zero.
    """
    pdbFile = molecule.toPDB( model=model, convention = convention)
    pdbFile.save( path)   
    del(pdbFile)
#end def
Molecule.toPDBfile = moleculeToPDBfile

def moveFirstDigitToEnd(a):
    if a[0:1].isdigit():
        a = a[1:] + a[0:1]
    return a

def initPDB( project, pdbFile, convention = IUPAC, name=None, nmodels=None ):
    """Initialize Molecule from pdbFile. returns molecule instance"""
    if not name: 
        _path,name,_ext  = NTpath( pdbFile )
    molecule = PDB2Molecule( pdbFile, name, convention = convention, nmodels=nmodels)
    project.appendMolecule( molecule )
    project.molecule.updateAll()
    project.addHistory( sprintf('initPDB from "%s"', pdbFile ) )
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

    project.addHistory( sprintf('importPDB from "%s"', pdbFile ) )
    project.updateProject()
    NTmessage( '%s', project.molecule.format() )
    #end if
    return pdbFile
#end def
    
def export2PDB( project, tmp=None ):
    """Export coordinates to pdb file
    """
    for molName in project.molecules:
        mol   = project[molName]
        if (mol.modelCount > 0):
            fname = project.path( project.directories.PDB, mol.name + '.pdb' )
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
