"""
Adds methods:
    Atom.export2aqua()
    Project.export2aqua()

Unit testing is done thru procheck.
"""
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import fprintf
from cing.core.constants import AQUA
from cing.core.molecule import Atom
from cing.Libs.NTutils import val2Str
from cing.Libs.NTutils import NTcodeerror
import time
#-----------------------------------------------------------------------------
def exportAtom2aqua( atom ):
    """
        returns string in aqua format from the manual:
        NOEULD  [CHAIN id]  residue_name  residue_number  [INSERT code]  atom_name
        ...[CHAIN id]  residue_name  residue_number  [INSERT code]  atom_name
        ...bound_1  [ bound_2 ]

    """
    residue = atom.residue
    chain = residue.chain
    return 'CHAIN %-3s %-4s %4d %-5s' % (
                      chain.name,
                      residue.translate(AQUA),
                      residue.resNum,
                      atom.translate(AQUA))
#end def
# add as a method to Atom Class
Atom.export2aqua = exportAtom2aqua
#-----------------------------------------------------------------------------

MIN_DISTANCE_ANY_ATOM_PAIR = 1.8
MAX_DISTANCE_ANY_ATOM_PAIR = 999.9

def export2aqua( project, tmp=None ):
    """
        export distanceRestraintLists to aqua
        export Molecules to PDB files in aqua format
        returns None on success and True on failure.
    """

    drLoLoL = [ project.distances, project.dihedrals ]
    typeId = -1
    extensionList = [ 'noe', 'tor' ]
    restraintTypeList = [ 'distance', 'dihedral angle' ]
    for drLoL in drLoLoL:
        typeId += 1
        if not drLoL:
            NTmessage("No DR lists to export")
        count = 0
        for drl in drLoL:
            count += len(drl)
        if not count:
            NTdebug("Skipping export of empty restraint list")
            continue
        # Instead of project.directories.aqua perhaps use project.moleculeDirectories.procheck
        exportPath = project.directories.aqua
        path = project.path( exportPath, project.name +'.' + extensionList[typeId] )
        NTmessage("Writing to: " + path )
        fp = open( path, 'w' )
        if not fp:
            NTerror('Unable to open: ' + path )
            return
        countActual = 0
        restraintListText = []
        warningCountMax = 10
        warningCount = 0
        warningCountAngle = 0
        for drl in drLoL:
            for dr in drl:
                if typeId == 0:
#                   Distance conversions
                    upper = dr.upper
                    if not upper:
                        upper = MAX_DISTANCE_ANY_ATOM_PAIR
                    lower = dr.lower
                    if not lower:
                        lower = MIN_DISTANCE_ANY_ATOM_PAIR
                    if not isinstance(lower, float):
                        NTcodeerror("What is the lower class: %s" % lower.__class__) # JFD Failed to reproduce the cause of issue 185 so keeping this statement in.
                        return True

#                    NTdebug("lower: %s" % lower)
                    fmt = '%8.3f'
                    upperStr = val2Str(upper, fmt)
                    if not upperStr:
                        upperStr = val2Str(MAX_DISTANCE_ANY_ATOM_PAIR, fmt)
                    lowerStr = val2Str(lower, fmt)
                    if not lowerStr:
                        lowerStr = val2Str(MIN_DISTANCE_ANY_ATOM_PAIR, fmt)

                    result = 'NOEUPLO %s %s  %s  %s' % (
                                 dr.atomPairs[0][0].export2aqua(),
                                 dr.atomPairs[0][1].export2aqua(),
                                 upperStr, lowerStr )
#                    NTdebug("result: %s" % result)

                    if len(dr.atomPairs) > 1:
                        if warningCount == warningCountMax+1:
                            NTwarning("And so on")
                        elif warningCount <= warningCountMax:
                            NTwarning("Ambiguous restraint exported as unambiguous for Aqua  ["+`warningCount`+"]")
                        warningCount += 1
                    for atomPair in dr.atomPairs[1:]:
                        result += ( '\n#       %s %s AMBI not read by Aqua' % (
                                 atomPair[0].export2aqua(),
                                 atomPair[1].export2aqua()))
                else:
                    # Dihderal
                    """Return string with restraint in Aqua format
                        ANGLE  [CHAIN id]  residue_name  residue_number  [INSERT code]
                        ...angle_name  bound_high  bound_low
                    """
                    # (<Residue>, angleName, <AngleDef>) tuple
                    _Residue, angleName, _AngleDef = dr.retrieveDefinition()
                    if not angleName:
                        if warningCountAngle == warningCountMax+1:
                            NTwarning("And so on")
                        elif warningCountAngle <= warningCountMax:
                            strResidue ="Unknown"
                            if hasattr(dr, 'residue'):
                                strResidue = '%s' % dr.residue
                            NTwarning("Skipping dihedral angle restraint '%s' (%s) because angle name could not be retrieved.",
                                      dr.id, strResidue)
                        warningCountAngle += 1
                        #return None

                    atom = dr.atoms[1] # this is true except for Omega? TODO correct!
                    if angleName == "OMEGA":
                        atom = dr.atoms[2]
                    residue = atom.residue
                    chain = residue.chain
                    result = 'ANGLE CHAIN %-3s %-4s %4d %-10s %8.2f %8.2f' % (
                                      chain.name,
                                      residue.resName,
                                      residue.resNum,
                                      angleName,
                                      dr.lower,
                                      dr.upper)
                if result:
                    countActual += 1
                    restraintListText.append(result)
                else:
                    NTwarning("Skipped restraint")
        if warningCount:
            NTwarning("Ambiguous distance restraint exported as unambiguous for Aqua for count: ["+`warningCount`+"]")
        if warningCountAngle:
            NTwarning("Dihedral angle restraint not exported                for Aqua for count: ["+`warningCountAngle`+"]")
        if countActual:
            # Important to let the join do this as one for optimalization.
            restraintListTextCombined = '\n'.join(restraintListText)
            fprintf( fp, 'Restraint list generated by CING for Aqua on: %s\n', time.asctime() )
            fprintf( fp, 'count %d type aqua\n', count )
            fprintf( fp, restraintListTextCombined )
            fp.close()
        else:
            NTwarning("Failed to convert a single restraint of this type: "+restraintTypeList[typeId])
            return True
#-----------------------------------------------------------------------------
# register the functions in the project class
methods  = [
           ]
#saves    = []
#restores = []
exports  = [(export2aqua, None),
           ]
