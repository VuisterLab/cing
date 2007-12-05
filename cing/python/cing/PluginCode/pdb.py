"""
Adds initialise/import/export from/to PDB files


Methods:
    Molecule.importFromPDB( pdbFile, convention='PDB', verbose=True ):
        Import coordinates from pdbFile
        convention eq PDB, CYANA, CYANA2 or XPLOR
        return molecule or None on error
    
    Molecule.PDB2Molecule(pdbFile, moleculeName, convention, verbose=True ):
        Initialise  from pdbFile
        Return molecule instance
        convention eq PDB, CYANA, CYANA2 or XPLOR 
        staticmethod
    
    Project.initPDB( pdbFile, convention ):
        initialise from pdbFile, import coordinates          
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

#==============================================================================
# PDB stuff
#==============================================================================
def importFromPDB( molecule, pdbFile, convention='PDB', nmodels=None, verbose=True ):
    """Import coordinates from pdbFile (optionally: first nmodels)
convention eq PDB, CYANA, CYANA2 or XPLOR
return molecule or None on error
    """
    if not molecule: return None

    if verbose:
        NTmessage('==> Parsing pdbFile "%s" ... ', pdbFile ) 
        NTmessage.flush()
    #end if
    
    pdb = PyMMLib.PDBFile( pdbFile, verbose=False )
#    molecule.pdb = pdb; no longer save it: it eats massive memory and we don't use it
    
    foundModel = False
    modelCount = 0
    
    for record in pdb:

        recordName = record._name.strip()
        
        if  recordName == 'REMARK':
            pass
        
        elif recordName == "MODEL":
            foundModel = True
        
        elif recordName == "ENDMDL":
            modelCount += 1
            if nmodels and modelCount >= nmodels:
                break
            #end if
        
        elif recordName == "ATOM" or recordName == "HETATM":
            # see if we can find a definition for this residue, atom name in the database
       
            if (convention == CYANA):
                # the residue names are in Cyana1.x convention (i.e. for GLU-)
                # atm names of the Cyana1.x PDB files are in messed-up Cyana format
                atmName = record.name[1:4] + record.name[0:1]
            elif (convention == CYANA2):
                # the residue names are in Cyana2.x convention (i.e. for GLU)
                # atm names of the Cyana2.x PDB files are in messed-up Cyana format
                atmName = record.name[1:4] + record.name[0:1]
            else:
                atmName = record.name
            #end if
            
            # Not all PDB files have chainID's !@%^&*
            if record.has_key('chainID'):
                cname = record.chainID.strip()
            else:
                cname = 'A'
            #end if
            resID = record.resSeq
            atom  = molecule.decodeNameTuple( (convention, cname, resID, atmName) )

            if (atom == None):
                NTerror('WARNING: %s, model %d incompatible record (%s)\n', 
                         convention, modelCount, record 
                       )         
                #print '>>', convention, cname, resID, atmName

            else:
                # we did find a match in the molecule
                atom.addCoordinate( record.x, record.y, record.z, record.tempFactor )

                record.atom = atom
                atom.pdbRecord = record
                
            #end if
        #end if
    #end for
    
    # Patch to get modelCount right for X-ray or XPLOR structures with only one model
    if (not foundModel): 
        modelCount += 1
    #end if
    molecule.modelCount += modelCount
    
    if verbose:
        NTmessage( 'read %d records; added %d structure models\n', len(pdb), modelCount )  
    #end if
    
    del( pdb )

    return molecule
#end def
# Add as a method to Molecule class
Molecule.importFromPDB = importFromPDB

def PDB2Molecule( pdbFile, moleculeName, convention, nmodels=None, verbose=True ):
    """Initialise  from pdbFile
Return molecule instance
convention eq PDB, CYANA, CYANA2 or XPLOR
    """

    if verbose:
        NTmessage('==> Parsing pdbFile "%s" ... ', pdbFile ) 
        NTmessage.flush()
    #end if
    pdb = PyMMLib.PDBFile( pdbFile, verbose=False )
    if verbose:
        NTmessage('done\n' ) 
        NTmessage.flush()
    #end if
    
    mol = Molecule( name=moleculeName )
    

#    mol.pdb = pdb
    mol.modelCount  = 0
    foundModel = False
    
    for record in pdb:

#        print '>', record
        recordName = record._name.strip()
        
        if  recordName == 'REMARK':
            pass
        
        elif recordName == "MODEL":
            foundModel = True
        
        elif recordName == "ENDMDL":
            mol.modelCount += 1
            if nmodels and mol.modelCount >= nmodels:
                break
            #end if
         
        elif recordName == "ATOM" or recordName == "HETATM":
            # see if we can find a definition for this residue, atom name in the database
       
            if (convention == CYANA):
                # the residue names are in Cyana1.x convention (i.e. for GLU-)
                # atm names of the Cyana1.x PDB files are in messed-up Cyana format
                a = record.name[1:4] + record.name[0:1]
                atm = NTdbGetAtom( record.resName, a, CYANA )
            elif (convention == CYANA2):
                # the residue names are in Cyana2.x convention (i.e. for GLU)
                # atm names of the Cyana2.x PDB files are in messed-up Cyana format
                a = record.name[1:4] + record.name[0:1]
                atm = NTdbGetAtom( record.resName, a, CYANA2 )
            else:
                atm = NTdbGetAtom( record.resName.strip(), record.name.strip(), convention )
            #end if    

            if (atm == None):
                NTerror('WARNING: %s, model %d incompatible record (%s)\n', 
                         convention, mol.modelCount, record 
                       )         
#                printf('res>%s<  atm>%s<\n',record.resName.strip(), record.name.strip())
            
            elif (atm.residueDef.hasProperties('cyanaPseudoResidue')):
                # skip CYANA pseudo residues
                pass

            else:
                # we did find a match in the database

                # Not all PDB files have chainID's !@%^&*
                if record.has_key('chainID'):
                    cname = record.chainID.strip()
                else:
                    cname = 'A'
                #end if
                resID    = record.resSeq
                resName  = atm.residueDef.name
                fullName = resName+str(resID)
                atmName  = atm.name
                
                # check if this chain,fullName,atmName already exists in the molecule
                # if not, add chain or residue                 
                if (not cname in mol):
                    mol.addChain( cname )
                #end if
                
                if (not fullName in mol[cname]):
                    res = mol[cname].addResidue( resName, resID )
                    res.addAllAtoms()
                #end if
                
                atom = mol[cname][fullName][atmName]
                atom.addCoordinate( record.x, record.y, record.z, record.tempFactor )

#               record.atom = atom
#               atom.pdbRecord = record
                
            #end if
        #end if
    #end for
    
    # Patch to get modelCount right for X-ray structures with only one model
    if (not foundModel): mol.modelCount += 1
    
    if verbose:
        NTmessage( '==> PDB2Molecule: completed, added %d structure models\n', mol.modelCount )  
    #end if
    
    # delete the PyMMlib pdbFile instance
    del(pdb)

    return mol
#end def
# Add as a staticmethod to Molecule class
Molecule.PDB2Molecule = staticmethod( PDB2Molecule )


def moleculeToPDBfile( molecule, path, model=None, convention=IUPAC, verbose=True ):
    """
    Save a molecule instance to PDB file.
    Convention eq PDB, CYANA, CYANA2, XPLOR.
    
    For speedup reasons, this routine should be explicitly coded.
    This routine should eventually replace toPDB.
    
    """
    pdbFile = molecule.toPDB( model=model, convention = IUPAC, verbose = verbose )
    pdbFile.save( path, verbose = verbose )   
    del(pdbFile)
#end def
Molecule.toPDBfile = moleculeToPDBfile


def initPDB( project, pdbFile, convention = IUPAC, name=None, nmodels=None ):
    """Initialise Molecule from pdbFile. returns molecule instance"""
    if not name: 
        dummy_path,name,dummy_ext  = NTpath( pdbFile )
    #end if
    molecule = PDB2Molecule( pdbFile, name, convention = convention, nmodels=nmodels,
                             verbose = project.parameters.verbose()
                           )
    project.appendMolecule( molecule )

    project.molecule.updateAll( verbose = project.parameters.verbose() )
        
    project.addHistory( sprintf('initPDB from "%s"\n', pdbFile ) )
    project.updateProject()

    return molecule
#end def


def importPDB( project, pdbFile, convention = IUPAC, nmodels=None ):
    """Import coordinates from pdbFile  
        return pdbFile or None on error
    """
    if (not project.molecule):
        NTerror("ERROR importPDB: no molecule defined\n")
        return None
    #end if
    if (not importFromPDB( project.molecule, pdbFile, convention, nmodels=nmodels, verbose = project.parameters.verbose() )):
        return None
    #end if

    project.molecule.updateAll( verbose = project.parameters.verbose() )

    project.addHistory( sprintf('importPDB from "%s"\n', pdbFile ) )
    project.updateProject()
    if project.parameters.verbose(): 
        NTmessage( '%s\n', project.molecule.format() )
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
            pdbFile = mol.toPDB( convention = IUPAC, verbose = project.parameters.verbose() )
            pdbFile.save( fname, verbose = project.parameters.verbose() )   
            del(pdbFile)
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
