"""
Adds export2aqua methods to: 
DistanceRestraint , DistanceRestraintList, DihedralRestraint, DihedralRestraintList,
Atom, Molecule and Project classes.

    DistanceRestraint.export2aqua()

    DistanceRestraintList.export2aqua( path, verbose )

    DihedralRestraint.export2aqua()

    DihedralRestraintList.export2aqua( path, verbose )

    Atom.export2aqua()
 
    Project.export2aqua():
        exports DistanceRestraintLists in aqua format
        
!!TODO: NEED to Check periodicity in dihedrals
                
"""
from cing.Libs.NTutils import fprintf
from cing.Libs.NTutils import printError
from cing.Libs.NTutils import printMessage
from cing.Libs.NTutils import printWarning
from cing.core.classes import DihedralRestraint
from cing.core.classes import DistanceRestraint
from cing.core.constants import IUPAC
from cing.core.molecule import Atom
import time
import string
#-----------------------------------------------------------------------------
def exportAtom2aqua( atom ):
    """returns string in aqua format from the manual:
     NOEULD  [CHAIN id]  residue_name  residue_number  [INSERT code]  atom_name
          ...[CHAIN id]  residue_name  residue_number  [INSERT code]  atom_name
          ...bound_1  [ bound_2 ]
    
    """
    residue = atom.residue
    chain = residue.chain
    return 'CHAIN %-3s %-4s %4d %-5s' % (
                      chain.name, 
                      residue.resName,
                      residue.resNum,
                      atom.translate(IUPAC))
#end def
# add as a method to Atom Class
Atom.export2aqua = exportAtom2aqua


#-----------------------------------------------------------------------------
def exportDistanceRestraint2aqua( distanceRestraint ):
    """Return string with restraint in Aqua format"""
    result = 'DISUPLO %s %s  %8.3f  %8.3f' % (
                 distanceRestraint.atomPairs[0][0].export2aqua(),
                 distanceRestraint.atomPairs[0][1].export2aqua(),
                 distanceRestraint.upper, 
                 distanceRestraint.lower )
     
    if len(distanceRestraint.atomPairs) > 1:
        printWarning("Ambiguous restraint exported as unambiguous for Aqua.")
    for atomPair in distanceRestraint.atomPairs[1:]:
        result += ( '\n#AMBI-not-read-by-aqua DISUPLO %s %s' % (
                 atomPair[0].export2aqua(),
                 atomPair[1].export2aqua()))
    return result

    # add as a method to DistanceRestraint Class
DistanceRestraint.export2aqua = exportDistanceRestraint2aqua

#-----------------------------------------------------------------------------
def exportDihedralRestraint2aqua( dihedralRestraint ):
    """Return string with restraint in Aqua format
ANGLE  [CHAIN id]  residue_name  residue_number  [INSERT code]
          ...angle_name  bound_high  bound_low
    """
    # (<Residue>, angleName, <AngleDef>) tuple
    dummyResidue, angleName, dummyAngleDef = dihedralRestraint.retrieveDefinition()
    if not angleName:
        printWarning("Skipping dihedral angle restraint because angle name could not be retrieved.")
        return None
    
    atom = dihedralRestraint.atoms[1] # this is true except for Omega?
    if angleName == "OMEGA":
        atom = dihedralRestraint.atoms[2]
    residue = atom.residue
    chain = residue.chain
    result = 'ANGLE CHAIN %-3s %-4s %4d %-10s %8.2f %8.2f' % (
                      chain.name, 
                      residue.resName,
                      residue.resNum,
                      angleName,
                      dihedralRestraint.lower, 
                      dihedralRestraint.upper)
    return result
#end def
# add as a method to DihedralRestraint Class
DihedralRestraint.export2aqua = exportDihedralRestraint2aqua



#-----------------------------------------------------------------------------
def export2aqua( project, tmp=None ):
    """export distanceRestraintLists to aqua
       export Molecules to PDB files in aqua format
    """
    drLoLoL = [ project.distances, project.dihedrals ]
    typeId = -1
    extensionList = [ 'dis', 'tor' ]
    restraintTypeList = [ 'distance', 'dihedral angle' ]
    for drLoL in drLoLoL:
        typeId += 1
        if not drLoL:
            printMessage("No DR lists to export")    
        count = 0
        for drl in drLoL:
            count += len(drl)
        if not count:
            printWarning("Skipping export of empty restraint list")
            continue
        # Instead of project.directories.aqua perhaps use project.moleculeDirectories.procheck
        exportPath = project.directories.aqua        
        path = project.path( exportPath, project.name +'.' + extensionList[typeId] )
        printMessage("Writing to: " + path )
        fp = open( path, 'w' )
        if not fp: 
            printError('Unable to open: ' + path )
            return
        countActual = 0
        restraintListText = []
        for drl in drLoL:
            for dr in drl:
                restraintText = dr.export2aqua()
                if restraintText:
                    countActual += 1
                    restraintListText.append(restraintText)
        if countActual:
            # Important to let the join do this as one for optimalization.
            restraintListTextCombined = string.join( restraintListText, '\n')
                               
            fprintf( fp, 'Restraint list generated by CING for Aqua on: %s\n', time.asctime() )
            fprintf( fp, 'count %d type aqua\n', count )
            fprintf( fp, restraintListTextCombined )
            fp.close()
        else:
            printWarning("Failed to convert a single restraint of this type: "+restraintTypeList[typeId])
#-----------------------------------------------------------------------------
# register the functions in the project class
methods  = [
           ]
#saves    = []
#restores = []
exports  = [(export2aqua, None),
           ]
