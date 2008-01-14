"""
Adds shiftx method to predict chemical shifts
Methods:
"""
from cing.Libs.AwkLike import AwkLike
from cing.Libs.NTutils import ExecuteProgram
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTfill
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import sprintf
from cing.core.constants import IUPAC
from cing.core.constants import NOSHIFT
from cing.core.parameters import cingPaths
from cing.Libs.NTutils import printWarning
import cing
import os

def parseShiftxOutput( fileName, molecule ):
    """
    Parse shiftx generated output (gv_version!).
    Store result in shiftx attribute (which is a NTlist type) of each atom

format file:     

# Entries marked with a * may have inaccurate shift predictions.
# Entries marked with a value < -600 should be ignored
  501   H  N      116.3173
  501   H  CA      55.4902
  501   H  CB      29.9950
  501   H  C      169.8446
  501   H  H        8.4401

    """
    for line in AwkLike( fileName, commentString = '#', minNF = 4 ):
        if (line.float(4) != -666.000):
            lineCol1 = int(line.dollar[1].strip('*'))
            atm = molecule.decodeNameTuple( (IUPAC, 'A', lineCol1, line.dollar[3]) )
            if not atm:
                NTerror('ERROR parseShiftxOutput: line %d (%s)\n', line.NR, line.dollar[0] )
            else:
                atm.shiftx.append( line.float(4) )
            #end if
        #end if                                   
    #end for
#end def

def predictWithShiftx( project, model=None, verbose = True ):
    """
    Use shiftx program to predict chemical shifts
    Works only for protein residues.
    Adds a NTlist object with predicted values for each model as shiftx attribute
    to each atom for which there are predictions, or empty list otherwise.
    
    Throws warnings for non-protein residues.
    Returns project or None on error.
    
    Shiftx works on pdb files, uses only one model (first), so we have to write the files separately and analyze them
    one at the time.
    """
    if project.molecule == None:
        NTerror('ERROR predictWithShiftx: no molecule defined\n')
        return None
    #end if
    if project.molecule.modelCount == 0: 
        NTerror('ERROR predictWithShiftx: no models for "%s"\n', project.molecule)
        return None
    #end if
    if model != None and model >= project.molecule.modelCount: 
        NTerror('ERROR predictWithShiftx: invalid model (%d) for "%s"\n', model, project.molecule)
        return None
    #end if
    
    skippedAtoms = [] # Keep a list of skipped atoms for later
    skippedResidues = []
    for res in project.molecule.allResidues():
        if not res.hasProperties('protein'):
            skippedResidues.append(res)
            for atm in res.allAtoms():
                atm.pdbSkipRecord = True
                skippedAtoms.append( atm )
            #end for
        #end if
    #end for
    if skippedResidues:
        printWarning('predictWithShiftx: non-protein residues will be skipped:\n' + `skippedResidues`)
        
    if (model!=None):
        models = NTlist( model )
    else:
        models = NTlist(*range( project.molecule.modelCount ))
    #end if
    
    # initialize the shiftx attributes
    for atm in project.molecule.allAtoms():
        atm.shiftx = NTlist()
    #end for
        
    root = project.mkdir( project.molecule.name, project.moleculeDirectories.shiftx,  )
    shiftx = ExecuteProgram( pathToProgram=os.path.join(cing.cingRoot, cingPaths.bin, 'shiftx'), 
                             rootPath = root, redirectOutput = False, verbose = verbose )
    if verbose:
        NTmessage('==> Running shiftx ' )
        NTmessage.flush()
    for model in models:
        # set filenames
        rootname =  sprintf('model%03d', model)
        model_base_name =  os.path.join( root, rootname )
        
        pdbFile = project.molecule.toPDB( model=model, convention = IUPAC, verbose = verbose )       
        if not pdbFile:
            NTerror("Failed to generate a pdb file for model: " + `model`)
            return None 
        
        pdbFile.save( model_base_name + '.pdb', verbose = False )   
        shiftx('A', rootname + '.pdb', rootname + '.out' )
        
        if verbose:
            NTmessage('==> Parsing %s\n', model_base_name + '.out' )
        parseShiftxOutput( model_base_name + '.out', project.molecule )
        del( pdbFile )
    #end for
    
    if verbose:
        NTmessage(' averaging ...')
        NTmessage.flush()
    #end if
    
    # Restore the 'default' state
    for atm in skippedAtoms:
        atm.pdbSkipRecord = False
    #end for
    
    # Average the methyl proton shifts and b-methylene, before calculating average per atom 
    for atm in project.molecule.allAtoms():
        if atm.isCarbon():
            
            protons = atm.attachedProtons(includePseudo=False)
            if len(protons) >= 2:
                skip = False
                for p in protons:
                    if len(p.shiftx) == 0: # No prediction for this proton
                                           # Do not average
                        skip = True
                        #print p, p.shiftx
                        break
                    #end if
                #end for
                
                if not skip:
                    shifts  = NTfill(0.0,len(models))
                    for i in range(len(models)):
                        for p in protons:
                            shifts[i] += p.shiftx[i]
                        #end for
                        shifts[i] /= len(protons)
                    #end for
                    protons[0].pseudoAtom().shiftx = shifts
                #end if
            #end if         
        #end if
    #end for
    
    # Average's for each atom    
    for atm in project.molecule.allAtoms():
        # Set averages
        atm.shiftx.average()
        if atm.shiftx.av == None:
            atm.shiftx.av = -NOSHIFT
            atm.shiftx.sd = 0.0
        #end if
    #end for        
    if verbose:
        NTmessage(' done\n')
        NTmessage.flush()
    #end if
    
    return project
#end def


# register the functions
methods  = [(predictWithShiftx,None)
           ]
#saves    = []
#restores = []
#exports  = []