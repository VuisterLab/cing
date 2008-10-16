"""
Adds shiftx method to predict chemical shifts
Methods:
"""
from cing.Libs.AwkLike import AwkLike
from cing.Libs.NTutils import ExecuteProgram
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTfill
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTdetail
from cing.Libs.NTutils import NTprogressIndicator
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import sprintf
from cing.Libs.fpconst import NaN
from cing.core.constants import IUPAC
from cing.core.parameters import cingPaths
import cing
import os

def parseShiftxOutput( fileName, molecule, chainId ):
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
  or in 1y4o:
  1     G  N      109.7404
  1     G  CA      45.2787


    """
    atomDict = molecule._getAtomDict(IUPAC, chainId)
    for line in AwkLike( fileName, commentString = '#', minNF = 4 ):
        if (line.float(4) != -666.000):
            lineCol1 = int(line.dollar[1].strip('*'))
            if chainId != None:
                atm = molecule.decodeNameTuple( (IUPAC, chainId, lineCol1, line.dollar[3]) )
            else:
                atm =None
                if atomDict.has_key( (lineCol1,line.dollar[3]) ):
                    atm = atomDict[ (lineCol1,line.dollar[3]) ]
            #end if
#            if not atm:
#                atm = molecule.decodeNameTuple( (IUPAC, None, lineCol1, line.dollar[3]), fromCYANA2CING=True )

            if not atm:
                NTerror('parseShiftxOutput: chainId [%s] line %d (%s)', chainId, line.NR, line.dollar[0] )
            else:
                atm.shiftx.append( line.float(4) )
            #end if
        #end if
    #end for
#end def

def runShiftx( project, model=None   ):
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
        NTerror('runShiftx: no molecule defined')
        return None
    #end if
    if project.molecule.modelCount == 0:
        NTerror('runShiftx: no models for "%s"', project.molecule)
        return None
    #end if
    if model != None and model >= project.molecule.modelCount:
        NTerror('runShiftx: invalid model (%d) for "%s"', model, project.molecule)
        return None
    #end if

    NTmessage('==> Running shiftx' )

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
        NTwarning('runShiftx: non-protein residues %s will be skipped.',  skippedResidues)

    if model!=None:
        models = NTlist( model )
    else:
        models = NTlist(*range( project.molecule.modelCount ))

    # initialize the shiftx attributes
    for atm in project.molecule.allAtoms():
        atm.shiftx = NTlist()
    #end for

    root = project.mkdir( project.molecule.name, project.moleculeDirectories.shiftx)
    shiftx = ExecuteProgram( pathToProgram=os.path.join(cing.cingRoot, cingPaths.bin, 'shiftx'),
                             rootPath = root, redirectOutput = False)

    for model in NTprogressIndicator(models):
        # set filenames
        rootname =  sprintf('model_%03d', model)
        model_base_name =  os.path.join( root, rootname )

        pdbFile = project.molecule.toPDB( model=model, convention = IUPAC  )
        if not pdbFile:
            NTerror("runShiftx: Failed to generate a pdb file for model: " + `model`)
            return None

        pdbFile.save( model_base_name + '.pdb'   )
        for chain in project.molecule.allChains():
#            NTmessage('Doing chain code [%s]' % (chain.name))
            # quotes needed because by default the chain id is a space now.
#            chainId =  "'" + chain.name + "'"
            # According to the readme in shiftx with the source this is the way to call it.
            chainId =  "1" + chain.name
            outputFile = rootname + '_' + chain.name + '.out'
            shiftx(chainId, rootname + '.pdb', outputFile )
            outputFile = os.path.join(root,outputFile)
#            outputFile = os.path.abspath(outputFile)
            NTdebug('runShiftx: Parsing file: %s for chain Id: [%s]' % (outputFile,chain.name))
            parseShiftxOutput( outputFile, project.molecule, chain.name )
        del( pdbFile )
    #end for

    # Restore the 'default' state
    for atm in skippedAtoms:
        atm.pdbSkipRecord = False

    NTdetail('... averaging')
    # Average the methyl proton shifts and b-methylene, before calculating average per atom
    for atm in project.molecule.allAtoms():
        if atm.isCarbon():

            protons = atm.attachedProtons(includePseudo=False)
            if len(protons) >= 2:
                skip = False
                for p in protons:
                    if len(p.shiftx) == 0:  # No prediction for this proton
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
    averageShiftx(project)

    return project
#end def

def averageShiftx( project, tmp=None ):
    """Average shiftx array for each atom
    """

    NTdebug('doing averageShiftx')
    if project.molecule == None:
        return
    #end if

    for atm in project.molecule.allAtoms():
        # Set averages
        if atm.has_key('shiftx'):
            atm.shiftx.average()
            if atm.shiftx.av == None:
                atm.shiftx.av = NaN
                atm.shiftx.sd = NaN
            #end if
        #end if
    #end for
#end def


# register the functions
methods  = [(runShiftx,None),
           ]
#saves    = []
restores = [
            (averageShiftx,None)
           ]
#exports  = []