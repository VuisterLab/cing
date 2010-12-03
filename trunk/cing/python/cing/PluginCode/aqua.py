"""
Adds methods:
    Atom.export2aqua()
    Project.export2aqua()

Unit testing is done thru procheck.
"""
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.constants import * #@UnusedWildImport
from cing.core.molecule import Atom
#-----------------------------------------------------------------------------
def exportAtom2aqua(atom):
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

def export2aqua(project, tmp=None):
    """
        export distanceRestraintLists to aqua
        export Molecules to PDB files in aqua format
        returns None on success and True on failure.
    """

    drLoLoL = [ project.distances, project.dihedrals ]
    typeId = -1
    extensionList = [ 'noe', 'tor' ]
    restraintTypeList = [ 'distance', 'dihedral angle' ]
    msgHol = MsgHoL() # Used for messages per restraint not per restraint list.
    encounteredError = False
    for drLoL in drLoLoL:
        typeId += 1
        if not drLoL:
            NTmessage("No %s list to export" % extensionList[typeId])
        count = 0
        for drl in drLoL:
            count += len(drl)
        if not count:
#            NTdebug("Skipping export of empty restraint list")
            continue
        # Instead of project.directories.aqua perhaps use project.moleculeDirectories.procheck
        exportPath = project.directories.aqua
        path = project.path(exportPath, project.name + '.' + extensionList[typeId])
#        NTmessage("Writing to: " + path)
        fp = open(path, 'w')
        if not fp:
            NTerror('Unable to open: ' + path)
            return
        countActual = 0
        restraintListText = []
#        warningCountMax = 10 # DEFAULT
#        warningCountMax = 10000 # TESTING
#        warningCount = 0
        ambiDistanceCount = 0
        skippedDihedralCount = 0
        for drl in drLoL:
            for dr in drl:
                if not dr.isValidForAquaExport():
                    msgHol.appendWarning("Restraint is not valid for export to Aqua (perhaps missing assignment? As in issue 224)\n%s" % dr)
                    ambiDistanceCount += 1
                    continue
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
                                 upperStr, lowerStr)
#                    NTdebug("result: %s" % result)

                    if len(dr.atomPairs) > 1:
                        msgHol.appendWarning("Ambiguous restraint exported as unambiguous for Aqua  [" + `ambiDistanceCount` + "]")
                        ambiDistanceCount += 1
                    for atomPair in dr.atomPairs[1:]:
                        result += ('\n#       %s %s AMBI not read by Aqua' % (
                                 atomPair[0].export2aqua(),
                                 atomPair[1].export2aqua()))
                    # end for
                else:
                    # Dihedral
                    """Return string with restraint in Aqua format
                        ANGLE  [CHAIN id]  residue_name  residue_number  [INSERT code]
                        ...angle_name  bound_high  bound_low
                    """
                    result = None
                    # (<Residue>, angleName, <AngleDef>) tuple
                    _Residue, angleName, _AngleDef = dr.retrieveDefinition()
                    if not angleName:
                        strResidue = "Unknown"
                        if hasattr(dr, 'residue'):
                            strResidue = '%s' % dr.residue
                        msg = "Skipping dihedral angle restraint '%s' (%s) because angle name could not be retrieved." % (
                                  dr.id, strResidue)
                        msgHol.appendWarning(msg)
                        skippedDihedralCount += 1
                    else:
                        atom = dr.atoms[1] # this is true except for Omega? TODO correct!
                        if angleName == "OMEGA":
                            atom = dr.atoms[2]
                        residue = atom.residue
                        chain = residue.chain
                        try:
                            result = 'ANGLE CHAIN %-3s %-4s %4d %-10s %8.2f %8.2f' % (
                                              chain.name,
                                              residue.resName,
                                              residue.resNum,
                                              angleName,
                                              dr.lower,
                                              dr.upper)
                        except:
                            result = None
                            strResidue = "Unknown"
                            if hasattr(dr, 'residue'):
                                strResidue = '%s' % dr.residue
                            msg = "Skipping dihedral angle restraint '%s' (%s) because conversion of data to string failed." % (
                                      dr.id, strResidue)
                            msgHol.appendWarning(msg)
                            skippedDihedralCount += 1
                    # end else
                # end else
                if result:
                    countActual += 1
                    restraintListText.append(result)
                else:
                    msgHol.appendWarning("Skipped restraint")
        if ambiDistanceCount:
            NTwarning("Ambiguous distance restraint exported as unambiguous for Aqua for count: [%s]" % ambiDistanceCount)
        if skippedDihedralCount:
            NTwarning("Dihedral angle restraint not exported                for Aqua for count: [%s]" % skippedDihedralCount)
        if countActual:
            # Important to let the join do this as one for optimalization.
            restraintListTextCombined = '\n'.join(restraintListText)
            fprintf(fp, 'Restraint list generated by CING for Aqua on: %s\n', time.asctime())
            fprintf(fp, 'count %d type aqua\n', count)
            fprintf(fp, restraintListTextCombined)
            fp.close()
        else:
            NTwarning("Failed to convert a single restraint of this type: " + restraintTypeList[typeId])
            encounteredError = True

    msgHol.showMessage()
    if encounteredError:
        return True
    return None
#-----------------------------------------------------------------------------
# register the functions in the project class
methods = [
           ]
#saves    = []
#restores = []
exports = [(export2aqua, None),
           ]
