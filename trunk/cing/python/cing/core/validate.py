"""
Adds validation methods
----------------  Methods  ----------------


validate(   )
checkForSaltbridges( toFile = False )


----------------  Attributes generated  ----------------


Molecule:
    rmsd: RmsdResult object containing positional rmsd values



Residue:
    rmsd: RmsdResult object containing positional rmsd values

    distanceRestraints: NTlist instance containing all distance restraints of this residue, sorted on violation count over 0.3A.

    saltbridges: NTlist instances of (potential) saltbridges

Atom:
    validateAssignment: NTlist instance with potential warnings/errors concerning the assignment of this atom

    shiftx, shiftx.av, shiftx.sd: NTlist instance with shiftx predictions, average and sd
"""
from cing.Libs.Geometry import violationAngle
from cing.Libs.NTplot import ssIdxToType
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.cython.superpose import NTcVector #@UnresolvedImport
from cing.Libs.html import addPreTagLines
from cing.Libs.html import hPlot
from cing.Libs.html import removePreTagLines
from cing.Libs.numpyInterpolation import circularlizeMatrix
from cing.Libs.numpyInterpolation import interpn_linear
from cing.Libs.peirceTest import peirceTest
from cing.PluginCode.required.reqDssp import DSSP_STR
from cing.PluginCode.required.reqDssp import getDsspSecStructConsensus
from cing.PluginCode.required.reqNih import NIH_STR
from cing.PluginCode.required.reqProcheck import PROCHECK_STR
from cing.PluginCode.required.reqShiftx import SHIFTX_STR
from cing.PluginCode.required.reqWattos import WATTOS_STR
from cing.PluginCode.required.reqWattos import WATTOS_SUMMARY_STR
from cing.PluginCode.required.reqWhatif import WHATIF_STR
from cing.core.ROGscore import CingResult
from cing.core.constants import * #@UnusedWildImport
from cing.core.molecule import Atom
from cing.core.molecule import Chain
from cing.core.molecule import Molecule
from cing.core.molecule import Residue
from cing.core.parameters import plotParameters
from cing.core.parameters import plugins
from matplotlib.pylab import * #@UnusedWildImport for most imports

def runCingChecks( project, toFile=True, ranges=None ):
    """This set of routines needs to be run after a project is restored."""
#    NTdebug("Now in runCingChecks")
    project.partitionRestraints()
    project.analyzeRestraints()
    project.validateRestraints(toFile)
    project.validateDihedrals()
    project.validateModels()
    project.validateDihedralCombinations()
#    project.validateAssignments() in criticize now
    # project.mergeResonances() GWV says: don't do this

    project.checkForSaltbridges(toFile)

#    project.checkForDisulfides(toFile=True)
# GWV this is done in molecule.updateAll
    if project.molecule:
        project.molecule.calculateRMSDs( ranges=ranges)
        project.molecule.idDisulfides(toFile, applyBonds=False)

    project.criticize(toFile)
    project.summary(toFile)
    project.mkMacros()
#end def

"""Stolen from doValidate.py in Script directory. Need this here so the
code can be tested. I.e. returns a meaningful status if needed.
"""
def validate( project, ranges=None, parseOnly=False, htmlOnly=False,
        doProcheck = True, doWhatif=True, doWattos=True, doTalos=True ):
# KEEP THIS BLOCK SYNC-ED or unify WITH THE FOLLOWING FILES:
# python/cing/Scripts/doValidateiCing.py
    if hasattr(plugins, SHIFTX_STR) and plugins[ SHIFTX_STR ].isInstalled:
        project.runShiftx(parseOnly=parseOnly)
    if hasattr(plugins, DSSP_STR) and plugins[ DSSP_STR ].isInstalled:
        project.runDssp(parseOnly=parseOnly)
    if hasattr(plugins, WHATIF_STR) and plugins[ WHATIF_STR ].isInstalled:
        if doWhatif:
            project.runWhatif(parseOnly=parseOnly)
    if hasattr(plugins, PROCHECK_STR) and plugins[ PROCHECK_STR ].isInstalled:
        if doProcheck:
            project.runProcheck(ranges=ranges, parseOnly=parseOnly)
    if hasattr(plugins, WATTOS_STR) and plugins[ WATTOS_STR ].isInstalled:
        if doWattos:
            project.runWattos(parseOnly=parseOnly)
    if hasattr(plugins, NIH_STR) and plugins[ NIH_STR ].isInstalled:
        if doTalos:
            project.runTalosPlus(parseOnly=parseOnly)
    project.runCingChecks(toFile=True, ranges=ranges)
    project.setupHtml()
    project.generateHtml(htmlOnly = htmlOnly)
    project.renderHtml()
    NTmessage("Done with overall validation")


def criticizePeaks( project, toFile=True ):
    """
    Check's based upon peak's.
    Compare peak positions and assigned shifts
    """
    if not project.molecule:
        return
    #end if

    for atm in project.molecule.allAtoms(): atm.peakPositions = NTlist()

    # criticize peak based on deviation of assigned value
    # make a list of all assigned peaks positions for each atom
    errorMargins = {'15N':0.15, '13C':0.15, '1H':0.01, '31P':0.15} # single sided
    for pl in project.peaks:

#        NTdebug('criticizePeaks %s', pl)

        pl.rogScore.reset()
        for peak in pl:
            peak.rogScore.reset()
            for i in range(peak.dimension):
                resonance = peak.resonances[i]
                if resonance and resonance.atom != None and resonance.value != NOSHIFT:
                    resonance.atom.peakPositions.append(peak.positions[i])
                    if not resonance.atom.isAssigned():
                        peak.rogScore.setMaxColor( COLOR_ORANGE,
                                                    sprintf('%s unassigned', resonance.atom)
                                                  )
                    else:
                        if resonance.atom.db.spinType in errorMargins:
                            shift = resonance.atom.shift()
                            errM = errorMargins[resonance.atom.db.spinType]
                            if math.fabs(resonance.value-shift)> 2.0*errM:
                                peak.rogScore.setMaxColor( COLOR_RED,
                                    sprintf('dimension %d: position (%.2f) - shift Atom %s (%.2f) > 2.0*(%.2f)',
                                             i, resonance.value, resonance.atom, shift, errM)
                                )

                            elif math.fabs(resonance.value-shift)> 1.0*errM:
                                peak.rogScore.setMaxColor( COLOR_ORANGE,
                                    sprintf('dimension %d: position (%.2f) - shift Atom %s (%.2f) > 1.0*(%.2f)',
                                             i, resonance.value, resonance.atom, shift, errM)
                                )
                            #end if
                        #end if
                    #end if
                #end if
            #end for
            pl.rogScore.setMaxColor( peak.rogScore.colorLabel, comment='Cascaded from peak %d' % peak.peakIndex )
        #end for
    #end for

#    project.validateAssignments()

    for atm in project.molecule.allAtoms():
        atm.peakPositions.average()
    #end for

    if toFile:
        for pl in project.peaks:
            path = project.moleculePath('analysis',pl.name+'.txt')
            f = file(path, 'w')
            for peak in pl:
                fprintf(f, '%s  %s\n', peak, peak.rogScore.format())
            #end for
            f.close()
            NTdetail('==> Analyzing %s, output to: %s', pl, path)
        #end for
    #end if
#end def

def _criticizeChain( chain, valSets ):
    """Convenience method
    """
    for color in [COLOR_GREEN,COLOR_ORANGE,COLOR_RED]:
        chain[color] = NTlist()

    chain.rogScore.reset()

    for res in chain.allResidues():
        _criticizeResidue( res, valSets )
        chain[res.rogScore.colorLabel].append(res)
        chain.rogScore.setMaxColor(res.rogScore.colorLabel, 'Inferred from residue ROG scores')
    #end for
#end def
Chain.criticize = _criticizeChain

def _criticizeResidue( residue, valSets ):
    """
    Use whatif, procheck scores and CING for critique of residue; translate into ROG scores.
    """

    residue.rogScore.reset()

#    result = NTdict()
    # WHATIF
    #print residue, residue.has_key(WHATIF_STR), residue.hasProperties('protein')
    if residue.has_key(WHATIF_STR) and residue.hasProperties('protein'):
        #print '>', residue, residue.rogScore
        for key in ['BBCCHK', 'C12CHK', 'RAMCHK']:
#            NTdebug('Now criticizing %s, whatif key %s', residue, key )

            thresholdValuePoor = valSets[ 'WI_' + key + '_POOR'  ]
            thresholdValueBad = valSets[ 'WI_' + key + '_BAD' ]
            if (thresholdValuePoor == None) or (thresholdValueBad == None):
#                NTdebug("Skipping What If " + key + " critique")
                continue

            actualValue        = getDeepByKeys(residue, WHATIF_STR, key, VALUE_LIST_STR) #TODO remove this valueList stuff
            if actualValue == None:
                #print '>>', residue,key
                continue
            if isinstance(actualValue, NTlist):
                actualValue = actualValue.average()[0]

 #           NTdebug('%s key %s: actual %s, thresholdPoor %s, thresholdBad %s', residue, key,
 #                   actualValue, thresholdValuePoor, thresholdValueBad)

            actualValueStr = val2Str( actualValue, fmt='%8.3f', count=8 )
            if actualValue < thresholdValueBad: # assuming Z score
                comment = 'whatif %s value %s <%8.3f' % (key, actualValueStr, thresholdValueBad)
#                NTdebug(comment)
                residue.rogScore.setMaxColor( COLOR_RED, comment)
            elif actualValue < thresholdValuePoor:
                comment = 'whatif %s value %s <%8.3f' % (key, actualValueStr, thresholdValuePoor)
#                NTdebug(comment)
                residue.rogScore.setMaxColor( COLOR_ORANGE, comment)
            #endif
            residue.rogScore[key] = actualValue
        #end for
    #end if

    #Procheck
    if residue.has_key('procheck'):
        for key in ['gf']:
#            NTdebug('Now criticizing %s, procheck key %s', residue, key )

            thresholdValuePoor = valSets[ 'PC_' + key.upper() +'_POOR']
            thresholdValueBad = valSets[ 'PC_' + key.upper() +'_BAD']

            if (thresholdValuePoor == None) or (thresholdValueBad == None):
#                NTdebug("Skipping procheck g factor critique")
                continue

            actualValue        = getDeepByKeys(residue,'procheck', key )
            if actualValue == None:
                #print '>>', residue,key
                continue
            if isinstance(actualValue, NTlist):
                actualValue = actualValue.average()[0]

#            NTdebug('actual %s, thresholdPoor %s, thresholdBad %s',
#                    actualValue, thresholdValuePoor, thresholdValueBad)

            actualValueStr = val2Str( actualValue, fmt='%8.3f', count=8 )
            if actualValue < thresholdValueBad: # assuming Z score
                comment = 'Procheck %s value %s <%8.3f' % (key, actualValueStr, thresholdValueBad)
#                NTdebug(comment)
                residue.rogScore.setMaxColor( COLOR_RED, comment)
            elif actualValue < thresholdValuePoor:
                comment = 'Procheck %s value %s <%8.3f' % (key, actualValueStr, thresholdValuePoor)
#                NTdebug(comment)
                residue.rogScore.setMaxColor( COLOR_ORANGE, comment)
            #endif
            residue.rogScore[key] = actualValue
        #end for
    #end if

    #OMEGA refs from: Wilson et al. Who checks the checkers? Four validation tools applied to eight atomic resolution structures. J Mol Biol (1998) vol. 276 pp. 417-436
    TRANS_OMEGA_VALUE = 179.6
    CIS_OMEGA_VALUE = 0.0
    OMEGA_SD = 4.7
    for key in ['OMEGA']:
        if residue.hasProperties('protein') and key in residue and residue[key]:
            d = residue[key] # NTlist object
            modelId = -1 # needs to be set even if enumerate doesn't assign it.
            vList = NTlist()
            for modelId,value in enumerate(d):
                v = violationAngle(value=value, lowerBound=TRANS_OMEGA_VALUE, upperBound=TRANS_OMEGA_VALUE)
                if v > 90.: # Check a cis
                    v = violationAngle(value=value, lowerBound=CIS_OMEGA_VALUE, upperBound=CIS_OMEGA_VALUE)
#                NTdebug('found residue %s model %d omega to violate from square trans/cis: %8.3f (omega: %8.3f)' % ( residue, modelId, v, value) )
                vList.append(v)
            #end for
#            rmsViol = 0.0
            avViol = 0.0
            if modelId >= 0:
#                rmsViol = vList.rms()
                vList.average()
                avViol = vList.av

#            NTdebug('found rmsViol: %8.3f' % rmsViol )
#            actualValueStr = val2Str( rmsViol, fmt='%8.3f', count=8 )
            actualValueStr = val2Str( avViol, fmt='%8.3f', count=8 )
            # Calculate the Z-score (the number of times of the known sd.)
#            timesKnownSd = rmsViol / OMEGA_SD
            timesKnownSd = avViol / OMEGA_SD
            postFixStr = '(%s times known s.d. of %.1f degrees)' % (val2Str(timesKnownSd, fmt='%.1f'), OMEGA_SD)
            if (valSets.OMEGA_MAXALL_BAD != None) and (avViol >= valSets.OMEGA_MAXALL_BAD):
                comment = '%s value %s >%8.3f %s' % (key, actualValueStr, valSets.OMEGA_MAXALL_BAD, postFixStr)
                residue.rogScore.setMaxColor( COLOR_RED, comment )
#                NTdebug('Set to red')
            elif (valSets.OMEGA_MAXALL_POOR != None) and (avViol >= valSets.OMEGA_MAXALL_POOR):
                comment = '%s value %s >%8.3f %s' % (key, actualValueStr, valSets.OMEGA_MAXALL_POOR, postFixStr)
                residue.rogScore.setMaxColor(COLOR_ORANGE, comment)
#                NTdebug('Set to orange (perhaps)')
            residue.rogScore[key] = avViol
        #end if
    # end for

    if residue.has_key(CHK_STR) and residue.hasProperties('protein'):
#        print '>', residue, residue.rogScore
        for key in [RAMACHANDRAN_CHK_STR, CHI1CHI2_CHK_STR, D1D2_CHK_STR]: # TODO: disable those not needed.
#        for key in [D1D2_CHK_STR]: # TODO: disable those not needed.
#            NTdebug('Now criticizing %s, whatif key %s', residue, key )

            thresholdValuePoor = valSets[ key + '_POOR'  ]
            thresholdValueBad = valSets[ key + '_BAD' ]
            if (thresholdValuePoor == None) or (thresholdValueBad == None):
#                NTdebug("Skipping CING " + key + " critique")
                continue

            actualValue        = getDeepByKeys(residue, CHK_STR, key, VALUE_LIST_STR) #TODO remove this valueList stuff
            if actualValue == None:
#                NTdebug("None available for >> %s,%s" % ( residue,key))
                continue
            if isinstance(actualValue, NTlist):
                actualValue = actualValue.average()[0]

#            NTdebug('%s key %s: actual %s, thresholdPoor %s, thresholdBad %s', residue, key,
#                    actualValue, thresholdValuePoor, thresholdValueBad)

            actualValueStr = val2Str( actualValue, fmt='%8.3f', count=8 )
            if actualValue < thresholdValueBad: # assuming Z score
                comment = 'CING %s value %s <%8.3f' % (key, actualValueStr, thresholdValueBad)
#                NTdebug(comment)
                residue.rogScore.setMaxColor( COLOR_RED, comment)
            elif actualValue < thresholdValuePoor:
                comment = 'CING %s value %s <%8.3f' % (key, actualValueStr, thresholdValuePoor)
#                NTdebug(comment)
                residue.rogScore.setMaxColor( COLOR_ORANGE, comment)
            #endif
            residue.rogScore[key] = actualValue
        #end for
    #end if


#    # Check for restraint violations
#Geerten prefers to disable that for now.
#    for restraint in residue.distanceRestraints + residue.dihedralRestraints + residue.rdcRestraints:
#        if restraint.rogScore.isRed():
#            residue.rogScore.setMaxColor(COLOR_ORANGE, 'ORANGE: restraint violation(s)')
#            break
#    #end for
    return residue.rogScore
#end def
#Convenience method
Residue.criticize = _criticizeResidue

def criticize(project, toFile=True):
    # initialize

    # GV: Criticize restraints, peaks etc first
    # Restraint red ROGs get carried as orange to residue ROGs

    # Restraints lists
    for drl in project.allRestraintLists():
        drl.criticize(project, toFile=toFile)

    #Peaks
    criticizePeaks( project, toFile=toFile )

    # Assignments
    validateAssignments( project )

    if project.molecule:
        project.molecule.rogScore.reset()
        for color in [COLOR_GREEN,COLOR_ORANGE,COLOR_RED]:
            project.molecule[color] = NTlist()

        for chain in project.molecule.allChains():
            _criticizeChain( chain, project.valSets )
            # also list the residues in molecule color lists
            for res in chain.allResidues():
#                _criticizeResidue( res, project.valSets ) # now done in _criticizeChain
                project.molecule[res.rogScore.colorLabel].append(res)
#                res.chain.rogScore.setMaxColor(res.rogScore.colorLabel, 'Inferred from residue ROG scores')
        #end for

        if len(project.molecule[COLOR_RED]) > 0:
            project.molecule.rogScore.setMaxColor(COLOR_RED,'Inferred from residue ROG scores')
        elif len(project.molecule[COLOR_ORANGE]) > 0:
            project.molecule.rogScore.setMaxColor(COLOR_ORANGE,'Inferred from residue ROG scores')

        if toFile:
            path = project.moleculePath('analysis', 'ROG.txt')
            f = file(path,'w')
            for residue in project.molecule.allResidues():
                fprintf(f, '%-15s %4d %-6s  ', residue._Cname(-1), residue.resNum, residue.rogScore.colorLabel)
                keys = residue.rogScore.keys()
                for key in ['BBCCHK', 'C12CHK', 'RAMCHK', 'gf', 'OMEGA']:
                    if key in keys:
                        fprintf(f,'%-6s %-8s   ', key, val2Str( residue.rogScore[key], fmt='%8.3f', count=8 ))
                    else:
                        fprintf(f,'%-6s %8s   ', key, '.   ')
                    #end if
                #end for
                fprintf(f,'%s\n', residue.rogScore.colorCommentList.zap(1))
            #end for
            f.close()
            NTdetail('==> Criticizing project: output to "%s"', path)

            # Generate an xml summary file
            # When Whatif optional component isn't installed this fails. Disabled for now.
            path = project.moleculePath('analysis', 'cingSummaryDict.xml')
            s = project.getCingSummaryDict()
            s.save( path )
        else:
            NTdetail('==> Criticizing project')
        #end if
    #end if

    # store an

#end def

def _ROGsummary( residueList, allowHtml=False ):
    """Return a ROG summary string for residues in residueList
    """
    c = NTlist( 0, 0, 0 ) # Counts for green, orange and red.
    for residue in residueList:
        if residue.rogScore.isRed():
            c[2] += 1
        elif residue.rogScore.isOrange():
            c[1] += 1
        else:
            c[0] += 1
    #end for
    total = reduce(lambda x, y: x+y+0.0, c) # total expressed as a float because of 0.0
    if total <= 0:
        msgTmp = '_ROGsummary: Funny, no residues encountered'
        NTwarning(msgTmp)
        return msgTmp
    else:
        p = map( lambda x: 100*x/total, c)
        msg = """Red:     %3d  (%3.0f%%)
Orange:  %3d  (%3.0f%%)
Green:   %3d  (%3.0f%%)
         -----------
Total    %3d  (%3.0f%%)""" % ( c[2], p[2], c[1], p[1], c[0], p[0], total, 100.0 )
    #end if
    if allowHtml:
        msg = addPreTagLines(msg)
    return msg
#end def


def summary( project, toFile = True ):
    """
    Generate a summary string and store to text file
    Return summary string or None on error.
    """

    incompleteItems = []
    """For keeping track of which programs/checks were not run"""

    if not project.molecule:
        NTerror('Project.Summary: Strange, there was no molecule in this project')
        return None

    msg = ''
#    msg += sprintf( '%s\n', project.molecule.format() )

    skippedRmsd = False # keep logic simple.
    if project.molecule.has_key( RMSD_STR ) and project.molecule.rmsd:
        # Next msg isn't returning when no models are present in CING.
        msgNext = project.molecule.rmsd.format(allowHtml=True)
        if msgNext:
            msg += msgNext
#        msg += sprintf( '\n%s\n', project.molecule.rmsd.format() )
        if not project.molecule.modelCount:
            # empty molecule can't have meaningfull rmsds and this might be an important factor to note here.
            skippedRmsd = True
    else:
        skippedRmsd = True
    if skippedRmsd:
        incompleteItems.append( RMSD_STR )

    for drl in project.distances + project.dihedrals + project.rdcs:
        msg += drl.format(allowHtml=True) + '\n'
#        msg += sprintf( '\n%s\n', drl.format() )

    msg += "\n%s CING ROG analysis (all residues) %s\n%s\n" % (dots, dots, _ROGsummary(project.molecule.allResidues(),allowHtml=True))
    if project.molecule.ranges:
        r = project.molecule.ranges
        msg += "\n%s CING ROG analysis (residues %s) %s\n%s\n" % \
               (dots, r, dots, _ROGsummary(project.molecule.getResiduesFromRanges(r), allowHtml=True))

    wiSummary = getDeepByKeys(project.molecule, WHATIF_STR, 'summary')
    if wiSummary:
        msg += "\n%s WHAT IF Summary %s\n" % (dots, dots )
        msg += addPreTagLines(wiSummary)
    else:
        incompleteItems.append( WHATIF_STR )

    pc = getDeepByKeys(project.molecule, PROCHECK_STR)
    if pc:
        if hasattr(pc, "summary"):
            msg += "\n%s Procheck Summary %s\n" % (dots, dots )
            msg += '\n' + addPreTagLines(pc.summary.format())
        else:
            NTerror("Failed to find the procheck summary attribute")
    else:
        incompleteItems.append( PROCHECK_STR )

    # TODO: change this like shiftx setup with wattosStatus.
    wattosSummary = getDeepByKeys(project.molecule, WATTOS_SUMMARY_STR)
    if wattosSummary:
        msg += "\n%s Wattos Summary %s\n" % (dots, dots )
        msg += '\n' + addPreTagLines(wattosSummary)
#    else:
#        incompleteItems.append( WATTOS_STR )

#    skippedShiftx = False
    # don't mark nucleic acid only entries at all.
    if project.molecule.hasAminoAcid():
#        shiftx = getDeepByKeys(project.molecule, SHIFTX_STR) # modded by GWV in revision 624.
        shiftx = project.shiftxStatus.completed
        if not shiftx:
#            NTmessage('runShiftx: not a single amino acid in the molecule so skipping this step.')
            incompleteItems.append( SHIFTX_STR )

    topMsg = sprintf( '%s CING SUMMARY project %s %s', dots, project.name, dots )
    if not incompleteItems:
        topMsg += '\nAll applicable programs/checks were performed'
#    for checkId in incompleteItems:
    else:
        topMsg += '\nWARNING: Program(s) or check(s) NOT performed: %s' % incompleteItems
#        topMsg += '\n<font color=orange>WARNING:</font> This may affect the CING ROG scoring.'
        topMsg += '\nThis may affect the CING ROG scoring.'

    msg = topMsg + '\n' + msg

    if toFile:
        fname = project.path(project.molecule.name, project.moleculeDirectories.analysis,'summary.txt')
        fp = open( fname, 'w' )
        NTmessage( '==> summary, output to %s', fname)
#        NTdebug(" msg: " + msg)
        msgClean = removePreTagLines( msg )
#        NTdebug(" msgClean: " + msgClean)
        fprintf( fp, msgClean )
        fp.close()
    #end if

    return msg
#end def

def partitionRestraints( project, tmp=None ):
    """
    Partition the restraints and generate per-residue lists
    """
#    NTdebug('partionRestraints of project %s', project)

    if not project.molecule:
        return

    # distances and dihedrals
    for res in project.molecule.allResidues():
        res.distanceRestraints = NTlist()
        res.dihedralRestraints = NTlist()
        res.rdcRestraints      = NTlist()
    #end for

    for drl in project.distances:
        for restraint in drl:
            for atm1,atm2 in restraint.atomPairs:
                atm1.residue.distanceRestraints.add( restraint ) #AWSS
                atm2.residue.distanceRestraints.add( restraint ) #AWSS
            #end for
        #end for
    #end for
    # dihedrals
    for drl in project.dihedrals:
        for restraint in drl:
            restraint.atoms[2].residue.dihedralRestraints.add( restraint ) #AWSS and JFD will copy this logic to html class.
        #end for
    #end for
    #RDCs
    for drl in project.rdcs:
        for restraint in drl:
            for atm1,atm2 in restraint.atomPairs:
                atm1.residue.rdcRestraints.add( restraint ) #AWSS
                if atm2.residue != atm1.residue:
                    atm2.residue.rdcRestraints.add( restraint ) #AWSS
            #end for
        #end for
    #end for
#end def


def validateRestraints( project, toFile = True)   :
    """
    Calculate rmsd's and violation on restraints
    """

#    fps = []
#    fps.append( sys.stdout )

    if not project.molecule: return

    msg = ""
    msg += sprintf('%s\n', project.format() )

#    # distances and dihedrals
#    for res in project.molecule.allResidues():
#        res.distanceRestraints = NTlist()
#        res.dihedralRestraints = NTlist()
#    #end for

    # distances
    for drl in project.distances:
#        drl.analyze()
        msg += sprintf( '%s\n', drl.format())
        drl.sort('violMax').reverse()
        msg += sprintf( '%s Sorted on Maximum Violations %s\n', dots, dots)
        msg += sprintf( '%s\n', formatList( drl[0:min(len(drl),30)] ) )

        drl.sort('violCount3').reverse()
        # omit restraints that have a violation less than cut off.  NEW FEATURE REQUEST
        msg += sprintf( '%s Sorted on Violations > 0.3 A %s\n', dots, dots)
        theList = drl[0:min(len(drl),30)]
#        NTdebug("Found list: " + `theList`)
        msg += sprintf( '%s\n', formatList( theList ) )

        # Sort restraints on a per-residue basis # now in partitionRestrainst
#        for restraint in drl:
#            for atm1,atm2 in restraint.atomPairs:
#                atm1.residue.distanceRestraints.add( restraint ) #AWSS
#                atm2.residue.distanceRestraints.add( restraint ) #AWSS
#            #end for
#        #end for
    #end for

    # dihedrals
    for drl in project.dihedrals:
#        drl.analyze()
        msg += sprintf( '%s\n', drl.format())
        drl.sort('violMax').reverse()
        msg += sprintf( '%s Sorted on Maximum Violations %s\n', dots, dots)
        msg += sprintf( '%s\n', formatList( drl[0:min(len(drl),30)] ) )

        drl.sort('violCount3').reverse()
        msg += sprintf( '%s Sorted on Violations > 3 degree %s\n', dots, dots)
        msg += sprintf( '%s\n', formatList( drl[0:min(len(drl),30)] ) )

        # sort the restraint on a per residue basis
#        for restraint in drl:
#            restraint.atoms[2].residue.dihedralRestraints.add( restraint ) #AWSS
#        #end for
    #end for

    # Process the per residue restraints data
    msg += sprintf( '%s Per residue scores %s\n', dots, dots )
    count = 0
    for res in project.molecule.allResidues():

        if len(res.distanceRestraints):
            # Sort on violation count
            NTsort(res.distanceRestraints, 'violCount3', inplace=True )
            res.distanceRestraints.reverse()

            # Calculate sum, rmsd and sum_of_average_deviation of restraints per residue
            sum   = 0.0
            sumsq = 0.0
            n = 0
            for d in res.distanceRestraints:
                if d.violations == None: # Happens for ParvulustatParis
                    continue
                sum   = d.violations.sum( sum )
                sumsq = d.violations.sumsq( sumsq )
                n += len(d.violations)
            #end for
            if n == 0:
                NTmessage('Only DRs without values so no rmsd for residue: %s' % res)
            else:
                res.distanceRestraints.rmsd = math.sqrt(sumsq/n)
                res.distanceRestraints.sum = sum

            res.distanceRestraints.violAv     = res.distanceRestraints.zap('violAv').sum()
            res.distanceRestraints.violCount1 = res.distanceRestraints.zap('violCount1').sum()
            res.distanceRestraints.violCount3 = res.distanceRestraints.zap('violCount3').sum()
            res.distanceRestraints.violCount5 = res.distanceRestraints.zap('violCount5').sum()
        else:
            res.distanceRestraints.rmsd       = 0.0
            res.distanceRestraints.sum        = 0.0
            res.distanceRestraints.violAv     = 0.0
            res.distanceRestraints.violCount1 = 0
            res.distanceRestraints.violCount3 = 0
            res.distanceRestraints.violCount5 = 0
        #end if

        # print every 10 lines
        if not count % 30:
            msg += sprintf('%-18s %15s  %15s   %s\n', '--- RESIDUE ---', '--- PHI ---', '--- PSI ---', '-- dist 0.1A 0.3A 0.5A   rmsd   violAv --')
        #end if
        if res.has_key('PHI'):
            phi = NTvalue( res.PHI.cav, res.PHI.cv, fmt='%7.1f %7.2f', fmt2='%7.1f' )
        else:
            phi = NTvalue( '-', '-', fmt='%7s %7s', fmt2='%7s' )
        #end if
        if res.has_key('PSI'):
            psi = NTvalue( res.PSI.cav, res.PSI.cv, fmt='%7.1f %7.2f', fmt2='%7.1f' )
        else:
            psi = NTvalue( '-', '-', fmt='%7s %7s', fmt2='%7s' )
        #end if
        try:
            msg += sprintf( '%-18s %-15s  %-15s      %3d %4d %4d %4d  %6.3f %6.3f\n',
                 res, phi, psi,
                 len(res.distanceRestraints),
                 res.distanceRestraints.violCount1,
                 res.distanceRestraints.violCount3,
                 res.distanceRestraints.violCount5,
                 res.distanceRestraints.rmsd,
                 res.distanceRestraints.violAv
                   )
        except:
            pass
#            NTerror("validateRestraints: No Phi,Psi result for residue %s", res)
        count += 1
    #end for
#    NTdebug(msg)
    if toFile:
        #project.mkdir(project.directories.analysis, project.molecule.name)
        fname = project.path(project.molecule.name, project.moleculeDirectories.analysis,'restraints.txt')
        fp = open( fname, 'w' )
        NTmessage( '==> validateRestraints, output to %s', fname)
        fprintf(fp, msg)
    #end if
#end def


def checkForSaltbridges( project, cutoff = 0.5, toFile=False)   :
    """
    Routine to analyze all potential saltbridges involving E,D,R,K and H residues.
    Initiates an NTlist instances as saltbridges attribute for all residues.

    Only list/store for a particular pair if fraction 'not-observed' <= cutoff)

    Returns a NTlist with saltbridge summaries.

    Optionally print output to file in analysis directory of project.
    """
    if not project.molecule:
        NTerror('checkForSaltbridges: no molecule defined')
        return None
    #end if

    result = NTlist()

    if project.molecule.modelCount == 0:
        NTwarning('checkForSaltbridges: no models for "%s"', project.molecule)
        return result
    #end if

    if toFile:
        #project.mkdir(project.directories.analysis, project.molecule.name)
        fname = project.path(project.molecule.name, project.moleculeDirectories.analysis,'saltbridges.txt')
        fp = open( fname, 'w' )
        NTmessage( '==> checkSaltbridges, output to %s', fname)
    else:
        fp = None
    #end if

    if toFile:
        fprintf( fp, '%s\n', project.molecule.format() )
#    NTmessage(     '%s', project.molecule.format() )

    residues1 = project.molecule.residuesWithProperties('E') + \
                project.molecule.residuesWithProperties('D')

    residues2 = project.molecule.residuesWithProperties('R') + \
                project.molecule.residuesWithProperties('K') + \
                project.molecule.residuesWithProperties('H')

    # initialize
    for res in project.molecule.allResidues():
        res.saltbridges = NTlist()
    #end for

    s = None
    for res1 in residues1:
        for res2 in residues2:
            #print '>>', res1, res2
            s = validateSaltbridge(res1,res2)
            if not (s and s.result): # no s.result for entry 1f96 issue 197
                continue
            if float(s.types[4][1])/float(len(s.result)) > cutoff:    # fraction 'not observed' > then cutoff (default 0.5), skip
                continue

            if toFile:
                fprintf(fp, '%s\n', s.format() )
#                    NTdebug(    '%s\n', s.format() )
            res1.saltbridges.append( s )
            res2.saltbridges.append( s )
            result.append( s )
        #end for
    #end for

    if s and toFile:
        fprintf( fp, '%s\n', s.comment )
        #NTdebug(     '%s\n', s.comment )
    #end if

    if toFile:
        fp.close()
    sys.stdout.flush()
    #end if

    return result
#end def

def validateSaltbridge( residue1, residue2 ):
    """
    ValidateSaltbridge( residue1, residue2 )

    Validate presence of saltbridge, CC-Bridge, NO-bridge, or ion-pair between residue1 and residue2
    Ref: Kumar, S. and Nussinov, R. Biophys. J. 83, 1595-1612 (2002)

    residue1, residue2: Residue instances of type E,D,H,K,R

    Arbitrarily set the criteria for ion-pair r,theta to be within 2 sd of average,
    else set type to none.

    Returns summary NTdict or None on error
    """
#    NTdebug('validateSaltBridge: %s %s', residue1, residue2)

    # Definitions of the centroids according to the paper
    # TODO: fix problem as in 1bzb most likely due to uncommon residues within getting recognized as regular ones.
    # Recode to use fullnames including variants.(Store in Database?)

    centroids = NTdict(
        E = ['OE1','OE2'],
        D = ['OD1','OD2'],
        H = ['CG','ND1','CD2','CE1', 'NE2'],
        K = ['NZ'],
        R = ['NE','CZ','NH1','NH2']
    )
    donorAcceptor = NTdict(
        E = ['OE1','OE2'],
        D = ['OD1','OD2'],
        H = ['ND1','NE2'],
        K = ['NZ'],
        R = ['NE','NH1','NH2']
    )

    if residue1 == None:
        NTerror('validateSaltbridge: undefined residue1')
        return None
    #end if
    if residue2 == None:
        NTerror('validateSaltbridge: undefined residue2')
        return None
    #end if

    modelCount = residue1.chain.molecule.modelCount
    if modelCount == 0:
        NTerror('validateSaltbridge: no structure models')
        return None
    #end if

    if residue1.db.shortName not in ['E','D','H','K','R']:
        NTerror('validateSaltbridge: invalid residue %s, should be E,D,H,K, or R', residue1)
        return None
    #end if


    if residue2.db.shortName not in ['E','D','H','K','R']:
        NTerror('validateSaltbridge: invalid residue %s, should be E,D,H,K, or R', residue2)
        return None
    #end if

    for residue in [residue1, residue2]:
        for atmName in centroids[residue.db.shortName]:
            atm = None
            try: # Fails for entry 1bzb which has a NH2 residue capping the C-terminus.
                atm = residue[atmName]
            except:
                NTerror("Failed to get atom for atom name [%s] in residue [%s]" % (atmName, residue))
                return None
            if len(atm.coordinates) == 0:
                # Happens for all residues without coordinates. E.g. 1brv 159-170
#                NTerror('validateSaltbridge: no coordinates for atom %s', atm)
                return None
            #end if
        #end for
    #end for

    # get the vectors c1, c1a, c2, c2a for each model and compute the result
    result  = NTlist()
    summary = NTdict(
        residue1 = residue1,
        residue2 = residue2,
        comment  = """
Ref: Kumar, S. and Nussinov, R. Biophys. J. 83, 1595-1612 (2002)
Arbitrarily set the criteria for ion-pair (r,theta) to be within
2 sd ~ 2*(1.2A,39) of average (7.6A,118), else set type to 'not observed'.
""",
        __FORMAT__ = '------------------ Saltbridge ------------------\n' +\
                     'residues:          %(residue1)s %(residue2)s\n' +\
                     'r (av,sd,min,max): (%(rAv).1f, %(rSd).1f, %(min).1f, %(max).1f)\n' +\
                     'theta (av,sd):     (%(thetaAv).1f, %(thetaSd).1f)\n' +\
                     'types:             %(types)s'
    )
    types = ['saltbridge','C-C bridge','N-O bridge','ion pair','not observed']
    counts = NTfill(0,5)

    # get the vectors c1, c1a, c2, c2a for each model and compute the result
    for model in range( modelCount ):
        #c1 is geometric mean of centroid atms
        c1 = NTcVector(0,0,0)
        for atmName in centroids[residue1.db.shortName]:
            atm = residue1[atmName]
            c1 += atm.coordinates[model].e
        #end for
        # not yet: c1 /= len(centroids[residue1.db.shortName])
        for j in range(3):
            c1[j] /= len(centroids[residue1.db.shortName])

        try:
            c1a = residue1['CA'].coordinates[model].e
        except:
            break

        #c2 is geometric mean of centroid atms
        c2 = NTcVector(0,0,0)
        for atmName in centroids[residue2.db.shortName]:
            atm = residue2[atmName]
            c2 += atm.coordinates[model].e
        #end for
        # not yet: c2 /= len(centroids[residue2.db.shortName])
        for j in range(3):
            c2[j] /= len(centroids[residue2.db.shortName])

        c2a = residue2['CA'].coordinates[model].e

        #print '>>', c1, c2
        r = c2-c1
        rl = r.length()
        theta = 180.0 - (c1-c1a).angle(c2-c2a)

        # Check criteria
        criterium1 = (rl < 4.0)
        count = 0
        for atmName1 in donorAcceptor[residue1.db.shortName]:
            atm1 = residue1[atmName1]
            for atmName2 in donorAcceptor[residue2.db.shortName]:
                atm2 = residue2[atmName2]
                d = (atm1.coordinates[model].e-atm2.coordinates[model].e).length()
                if d < 4.0:
                    count += 1
                #print '>', atm1,atm2,d,count

        criterium2 = count>0
        if   criterium1 and criterium2:
            type = 0
        elif criterium1 and not criterium2:
            type = 1
        elif not criterium1 and criterium2:
            type = 2
        elif not criterium1 and not criterium2 and rl < 7.6+2.1*2 and 118-39*2< theta and theta < 118+39*2:
            type = 3
        else:
            type = 4

        counts[type] += 1

        data = NTdict(
            residue1   = residue1,
            residue2   = residue2,
            model      = model,
            r          = rl,
            theta      = theta,
            criterium1 = criterium1,
            criterium2 = criterium2,
            type       = types[type],

            __FORMAT__ = '--- saltbridge analysis %(residue1)s-%(residue2)s ---\n' +\
                         'model: %(model)d\n' +\
                         'type:  %(type)s\n' +\
                         'r (A): %(r).1f\n' +\
                         'theta: %(theta).1f\n' +\
                         'criteria: %(criterium1)s, %(criterium2)s\n'
        )


        result.append(data)
    #end for

    summary.result = result
    r_resultNTList = result.zap('r') # cache for speed
    summary.rAv, summary.rSd, summary.modelCount = r_resultNTList.average()
    if r_resultNTList:
        summary.min   = min( r_resultNTList )
        summary.max   = max( r_resultNTList )
    else:
        summary.min   = NaN
        summary.max   = NaN

    summary.thetaAv, summary.thetaSd, _n = result.zap('theta').average()
    summary.types = zip( types,counts)
    if not summary.rSd:
        summary.rSd = -999.9 # wait until we have a standard approach for dealing with Nans. TODO:
    if not summary.thetaSd:
        summary.thetaSd = -999.9 # wait until we have a standard approach for dealing with Nans. TODO:
    return summary
#end def
Residue.checkSaltbridge = validateSaltbridge

#==============================================================================
def checkHbond( donorH, acceptor,
                minAngle = 100.0, maxAngle=225.0, maxDistance = 3.0,
                fraction = 0.5
              ):
    """
    Check for presence of H-bond between donorH proton and acceptor.

    H-bond is present for a particular conformer if:
        heavyAtom-donorH-acceptor angle between minAngle and maxAngle
        and adonorH-acceptor distance < maxDistance.

    H-bond is accepted when H-bond is present in at least fraction of
    the models in the ensemble.
    """

    if not donorH or not donorH.isProton():
        NTerror('checkHbond: non-proton donor %s\n', donorH )
        return None
    #end if

    if not acceptor:
        NTerror('checkHbond: undefined acceptor %s\n', donorH )
        return None
    #end if

    result = NTdict( __FORMAT__ = '=== H-bond %(donor)s - %(donorH)s - %(acceptor)s ===\n' +\
                                    'accepted: %(accepted)s (%(acceptedCount)d out of %(modelCount)d)\n' +\
                                    'distance: %(distance).2f  +- %(distanceSD).2f\n' +\
                                    'angle:    %(angle).1f  cv: %(angleCV).2f\n'
                     )
    result.donor         = donorH.topology()[0]
    result.donorH        = donorH
    result.acceptor      = acceptor
    result.minAngle      = minAngle
    result.maxAngle      = maxAngle
    result.maxDistance   = maxDistance
    result.fraction      = fraction
    result.distance      = NaN
    result.distanceSD    = 0.0
    result.angle         = NaN
    result.angleCV       = 0.0
    result.accepted      = False

    result.av, result.sd, _mind, _maxd = donorH.distance( acceptor )
    result.cav, result.cv = donorH.angle( result.donor, acceptor,
                                          radians=False
                                        )

    result.data           = map( None, donorH.distances, donorH.angles )
    result.acceptedModels = NTlist()
    result.acceptedCount  = 0
    result.modelCount     = 0
    distances             = NTlist()    # make copies to calculate averages of accepted
    angles                = NTlist()    # make copies to calculate averages of accepted
    for d,a in result.data:
        if d <= maxDistance and a >= minAngle and a <= maxAngle:
            result.acceptedModels.append( (result.modelCount, d, a ) )
            result.acceptedCount += 1
            distances.append( d )
            angles.append( a )
        #end if
        result.modelCount += 1
    #end for
    if len(distances) > 0: result.distance, result.distanceSD, _n = distances.average()
    if len(angles) > 0: result.angle, result.angleCV, _n = angles.cAverage()
    result.accepted = ((float(len( result.acceptedModels)) / float(len( result.data ))) >= fraction)
    del distances
    del angles
    return result
#end def
Atom.checkHbond = checkHbond

def _fixStereoAssignments( project  ):
    """Action is implemented here; this routine needs to be called twice to propagate the adjustments
    """
    for atm in project.molecule.allAtoms():
        if atm.isAssigned() and atm.isStereoAssigned():
            # check stereo methyl protons
            if atm.isMethylProton():
                heavy = atm.heavyAtom()
                if heavy and heavy.isAssigned() and not heavy.isStereoAssigned():
                    heavy.stereoAssigned = True
                    NTmessage('==> fixed stereo assignment %s', heavy)
                #end if

            # check stereo methyl carbon
            elif atm.isMethyl() and atm.isCarbon():
                pseudo = atm.attachedProtons(includePseudo=True).last()
                if pseudo and pseudo.isAssigned() and not pseudo.isStereoAssigned():
                    pseudo.stereoAssigned = True
                    NTmessage('==> fixed stereo assignment %s', pseudo)
                #end if
            #end if
            partner = atm.proChiralPartner()
            if partner and partner.isAssigned() and not partner.isStereoAssigned():
                partner.stereoAssigned = True
                NTmessage('==> fixed stereo assignment %s', partner)
            #end if
        #end if
    #end for
#end def

def fixStereoAssignments( project  ):
    """
    Fix the stereo assignments of the prochiral methyls; i.e. if either carbon or proton is stereo-specifically
    assigned, also assign the proton or carbon
    """
    # Since the changes may have to propagate I.e. methyls QD2->QD1->CD1, it is most easy done by doing it twice
    _fixStereoAssignments( project )
    _fixStereoAssignments( project )
#end def


MULTIPLE_ASSIGNMENT             = 'MULTIPLE_ASSIGNMENT'
MISSING_ASSIGNMENT              = 'MISSING_ASSIGNMENT'
EXPECTED_ASSIGNMENT             = 'EXPECTED_ASSIGNMENT'
INVALID_STEREO_ASSIGNMENT       = 'STEREO_ASSIGNMENT'
SHIFT                           = 'SHIFT'
# To use the below?
CIS_PRO_MISSED                  = 'CIS_PRO_MISSED'
TRANS_PRO_MISSED                = 'TRANS_PRO_MISSED'

def moleculeValidateAssignments( molecule  ):
    """
    Validate the assignments; check for potential problems and inconsistencies
    Add's NTlist instance with strings of warning description to each atom as
    validateAssignment attribute

    New: skipping issuing a warning MISSING_ASSIGNMENT when no chemical shifts are present of that nucleii.

    return an NTlist of atoms with errors.

    return None on code error.

    @todo: Also correlate assignment with peak values (if present)
    """

    funcName = moleculeValidateAssignments.func_name #@UnusedVariable
    result   = NTlist()
#    if molecule.resonanceCount == 0:
#        NTdebug("Molecule.validateAssignments: No resonance assignments read so no real validation on it can be done. Let's try anyway.")
#        pass
#        return result

    # Keep track of what assignments are done and don't complain about specific ones missing
    # if there are none at all assigned of that type.
    # Just initialize the ones that are checked below; not 1H or P etc.; GV added 1H anyway
    assignmentCountMap = molecule.getAssignmentCountMap()
    hasAssignment = {}
    for key in assignmentCountMap.keys():
        hasAssignment[key] = assignmentCountMap[key] > 0

#    NTdebug("Molecule.validateAssignments: Found assignments for the following spin types: %s" % hasAssignment.keys())

    for atm in molecule.allAtoms():
        atm.rogScore.reset()
        atm.validateAssignment = NTlist()

    for res in molecule.allResidues():
#        Routine below needs to be called after  atm.validateAssignment is initialized.
        if res.hasProperties('PRO') or res.hasProperties('cPRO'):
            if res.validateChemicalShiftProPeptide(result):
                NTerror("Failed to _validateChemicalShiftProPeptide for %s" % res)
        for atm in res.allAtoms():
            if atm.isAssigned():
                shift = atm.shift()
                pseudo = atm.pseudoAtom()

                # Check the shift against the database
                if atm.db.shift:
                    av = atm.db.shift.average
                    sd = atm.db.shift.sd
                elif pseudo and pseudo.db.shift:
                    av = pseudo.db.shift.average
                    sd = pseudo.db.shift.sd
                else:
    #                NTdebug("%s: '%s' not in in DB SHIFTS", funcName, atm)
                    av = None
                    sd = None
                #end if

                if av and sd:
                    delta = math.fabs(shift - av) / sd
                    if delta > 3.0:
                        string = sprintf('%.1f*sd from (%.2f,%.2f)', delta, av, sd )
                        result.append( atm )
                        atm.validateAssignment.append(string)
                    #end if
                #end if

                # Check if not both realAtom and pseudoAtom are assigned
                if atm.hasPseudoAtom() and atm.pseudoAtom().isAssigned():
                    string = sprintf('%s: and %s', MULTIPLE_ASSIGNMENT, atm.pseudoAtom() )
    #                NTmessage('%-20s %s', atm, string)
                    result.append( atm )
                    atm.validateAssignment.append(string)
                #end if

                # Check if not pseudoAtom and realAtom are assigned
                if atm.isPseudoAtom():
                    for a in atm.realAtoms():
                        if a.isAssigned():
                            string = sprintf('%s: and %s', MULTIPLE_ASSIGNMENT, a )
    #                        NTmessage('%-20s %s', atm, string)
                            result.append( atm )
                            atm.validateAssignment.append(string)
                        #end if
                    #end for
                #end if

                # Check if all realAtoms are assigned in case there is a pseudo atom
                if atm.hasPseudoAtom():
                    for a in atm.pseudoAtom().realAtoms():
                        if a.isMethylProtonButNotPseudo():
                            continue
                        if not a.isAssigned():
                            string = sprintf('%s: expected %s', MISSING_ASSIGNMENT, a )
    #                        NTmessage('%-20s %s', atm, string )
                            result.append( atm )
                            atm.validateAssignment.append(string)
                        #end if
                    #end for
                #end if

                # Check for protons with unassigned heavy atoms
                if atm.isProton():
                    heavyAtm = atm.heavyAtom()
                    if not heavyAtm.isAssigned():
                        spinType = getDeepByKeys(heavyAtm, 'db', 'spinType')
                        if spinType:
                            # Only complain if type has at least one assignment.
                            if getDeepByKeys( hasAssignment, spinType):
                                string = sprintf('%s: %s', EXPECTED_ASSIGNMENT, heavyAtm )
            #                    NTmessage('%-20s %s', atm, string )
                                result.append( atm )
                                atm.validateAssignment.append(string)
                    #end if
                #end if atm.isProton()

                # stereo assignments checks
                if atm.isStereoAssigned():
                    if not atm.isProChiral():
                        string = sprintf('%s: %s', INVALID_STEREO_ASSIGNMENT, atm )
                        result.append( atm )
                        atm.validateAssignment.append(string)
                    else:
                        # Check prochiral partner assignments
                        partner = atm.proChiralPartner()
                        if partner:
                            if not partner.isAssigned():
                                string = sprintf('%s: %s unassigned', INVALID_STEREO_ASSIGNMENT, partner )
                                result.append( atm )
                                atm.validateAssignment.append(string)
                            else:
                                if not partner.isStereoAssigned():
                                    string = sprintf('%s: %s not stereo assigned', INVALID_STEREO_ASSIGNMENT, partner )
                                    result.append( atm )
                                    atm.validateAssignment.append(string)
                                #end if
                            #end if
                        #end if
                    #end if
                #end if

                # check stereo methyl protons
                if atm.isMethylProton():
                    heavy = atm.heavyAtom()
                    if heavy and heavy.isAssigned():
                        if atm.isStereoAssigned() and not heavy.isStereoAssigned():
                            string = sprintf('%s: %s not stereo assigned', INVALID_STEREO_ASSIGNMENT, heavy )
                            result.append( atm )
                            atm.validateAssignment.append(string)
                        #end if
                        if not atm.isStereoAssigned() and heavy.isStereoAssigned():
                            string = sprintf('%s: %s is stereo assigned', INVALID_STEREO_ASSIGNMENT, heavy )
                            result.append( atm )
                            atm.validateAssignment.append(string)
                        #end if
                    #end if
                #end if

                # check stereo methyl carbon
                if atm.isMethyl() and atm.isCarbon():
                    pseudo = atm.attachedProtons(includePseudo=True).last()
                    if pseudo and pseudo.isAssigned():
                        if atm.isStereoAssigned() and not pseudo.isStereoAssigned():
                            string = sprintf('%s: %s not stereo assigned', INVALID_STEREO_ASSIGNMENT, pseudo )
                            result.append( atm )
                            atm.validateAssignment.append(string)
                        #end if
                        if not atm.isStereoAssigned() and pseudo.isStereoAssigned():
                            string = sprintf('%s: %s is stereo assigned', INVALID_STEREO_ASSIGNMENT, pseudo )
                            result.append( atm )
                            atm.validateAssignment.append(string)
                        #end if
                    #end if
                #end if

            else:
                # Atm is not assigned but stereo assignment is set
                if atm.isStereoAssigned():
                    string = sprintf('%s: not assigned but stereo-assignment %s set', INVALID_STEREO_ASSIGNMENT, atm )
                    result.append( atm )
                    atm.validateAssignment.append(string)
                #end if

                if atm.isProChiral():
                    partner = atm.proChiralPartner()
                    if partner and partner.isAssigned() and partner.isStereoAssigned():
                        string = sprintf('%s: prochiral partner %s is stereo assigned', INVALID_STEREO_ASSIGNMENT, partner )
                        result.append( atm )
                        atm.validateAssignment.append(string)
                #end if

            #end if atm.isAssigned():

            if atm.validateAssignment:
                atm.rogScore.setMaxColor( COLOR_ORANGE, atm.validateAssignment )
                if hasattr(molecule, 'atomList'):
                    molecule.atomList.rogScore.setMaxColor( COLOR_ORANGE, 'Inferred from atoms')
            #end if
        #end for atoms
    #end for residues


    return result
#end def
#Patch the Molecule class
Molecule.validateAssignments = moleculeValidateAssignments

def validateAssignments( project  ):
    """
    Validate the assignments of current molecule in project.
    Calls Molecule.validateAssignment for the action (defined above).

    return a NTlist of atoms with errors.

    return None on code error.
    """

#    NTdebug("Starting validateAssignments")
    if not project.molecule:
#        NTdebug('validateAssignments: no molecule defined')
        return None
    #end if

    return project.molecule.validateAssignments()
#end def

def restoreDihRestraintInfo(project):
    """To restore restraint.residue and restraint.angle"""
    #GV does not understand why this routine would be needed
    for dihRestraintList in project.dihedrals:
        for dihRestraint in dihRestraintList:
            residue, angle, _val3 = dihRestraint.retrieveDefinition()
            if angle:
                dihRestraint.residue = residue
                dihRestraint.angle = '%s_%i' % (angle, residue.resNum)
            else:
                dihRestraint.residue = dihRestraint.atoms[2].residue #'Invalid'
                dihRestraint.angle = 'Discarted'
# end def

def validateDihedrals(self):
    """Validate the dihedrals of dihedralList for outliers and cv using pierceTest.
    Return True on error.
    """

    if not self.molecule:
        return True
    if not self.molecule.modelCount:
        return True

    restoreDihRestraintInfo(self)

    for res in self.molecule.allResidues():
        for dihed in res.db.dihedrals.zap('name'):
            if not dihed in res:
                continue
            if not res.has_key(dihed):
                continue

            d = res[dihed]
            if not d: # skip dihedrals without values e.g. n terminal phi.
                continue
#            print res, dihed, d

            plotpars = self.plotParameters.getdefault(dihed,'dihedralDefault')

            cav, _cv, _n = d.cAverage(min=plotpars.min, max=plotpars.max)
            NTlimit( d, cav-180.0, cav+180.0 )

            goodAndOutliers = peirceTest( d )
            if not goodAndOutliers:
                NTcodeerror("in validateDihedrals: error from peirceTest")
                return True
            d.good, d.outliers = goodAndOutliers

            d.limit(          plotpars.min, plotpars.max )
            d.cAverage(       plotpars.min, plotpars.max )
            d.good.limit(     plotpars.min, plotpars.max, byItem=1 )
            d.good.cAverage(  plotpars.min, plotpars.max, byItem=1 )
            d.outliers.limit( plotpars.min, plotpars.max, byItem=1 )
            if False:
                NTmessage( '--- Residue %s, %s ---', res, dihed )
                NTmessage( 'good:     %2d %6.1f %4.3f',
                           d.good.n, d.good.cav, d.good.cv )
                NTmessage( 'outliers: %2d models: %s',
                           len(d.outliers), d.outliers.zap(0) )
#end def

def validateDihedralCombinations(project):
    """Validate the dihedral angle combinations such as the Ramachandran phi/psi
    wrt database derived preferences.
    The routine (re-)sets properties such as:
    res.CHK.RAMACHANDRAN_CHK.VALUE_LIST
    """
#TODO: check the sec.struct of the both pairs in
#Xxx-Yyy
#    Yyy-Zzz
    if not project.molecule:
        return True
    if not project.molecule.modelCount:
        return True
    modelCount = project.molecule.modelCount
    if hPlot.histRamaBySsAndCombinedResType == None:
        hPlot.initHist()

    # 0: Check id
    # 1: angle 1 name
    # 2: angle 2 name
    # 3: Angle combination name
    plotDihedral2dLoL = [ # truncate if needed.
        [RAMACHANDRAN_CHK_STR, PHI_STR,  PSI_STR,  'Ramachandran'],
        [CHI1CHI2_CHK_STR, CHI1_STR, CHI2_STR, 'Janin'],
        [D1D2_CHK_STR, DIHEDRAL_NAME_Cb4N, DIHEDRAL_NAME_Cb4C, 'D1D2']
       ]

    msgHol = MsgHoL()
    for residue in project.molecule.allResidues():
        if residue.hasProperties('water'): # important speed opt. for waters in X-ray.
            continue
        ssType = getDsspSecStructConsensus(residue)
        if not ssType:
            msgHol.appendDebug("Failed to getDsspSecStructConsensus from validateDihedralCombinations for residue; skipping: %s" % (residue))
            continue
        # The assumption is that the derived residues can be represented by the regular.
        resName = getDeepByKeysOrDefault(residue, residue.resName, 'nameDict', PDB)
        if len( resName ) > 3: # The above line doesn't work. Manual correction works 95% of the time.
            resName = resName[:3]  # .pdb files have a max of 3 chars in their residue name.
        for checkIdx in range(len(plotDihedral2dLoL)):
#        for checkIdx in [2]:
            checkId = plotDihedral2dLoL[checkIdx][0]
#            NTdebug('Looking at %s %s' % (residue, checkId) )
            dihedralName1 = plotDihedral2dLoL[checkIdx][1]
            dihedralName2 = plotDihedral2dLoL[checkIdx][2]

            residue[CHK_STR][checkId] = CingResult( checkId, level=RES_LEVEL, modelCount = modelCount)
            ensembleValueList = getDeepByKeysOrAttributes( residue, CHK_STR, checkId, VALUE_LIST_STR )
            ensembleValueLoL = []

            doingNewD1D2plot = False
            bins = bins360P # most common. (chis & ds)
            resTypeList = None # used for lookup of C tuple
            normalizeBeforeCombining = False
            if dihedralName1==PHI_STR and dihedralName2==PSI_STR:
                histBySsAndResType         = hPlot.histRamaBySsAndResType
                histCtupleBySsAndResType   = hPlot.histRamaCtupleBySsAndResType
                bins = bins180P
            elif dihedralName1==CHI1_STR and dihedralName2==CHI2_STR:
                histBySsAndResType         = hPlot.histJaninBySsAndResType
                histCtupleBySsAndResType   = hPlot.histJaninCtupleBySsAndResType
            elif dihedralName1==DIHEDRAL_NAME_Cb4N and dihedralName2==DIHEDRAL_NAME_Cb4C:
#                histBySsAndResType         = hPlot.histd1BySsAndResTypes
                histBySsAndResType         = None
                histCtupleBySsAndResType   = hPlot.histd1CtupleBySsAndResTypes
                doingNewD1D2plot = True
                doNormalize = False
                normalizeBeforeCombining = False
                ssType = None # use all now for scoring.
                triplet = NTlist()
#                tripletIdxList = [-1,0,1]
                tripletIdxList = [0,-1,1] # Note that this was a major bug before today June 3, 2010.
                for i in tripletIdxList:
                    triplet.append( residue.sibling(i) )
                if None in triplet:
#                    NTdebug( 'Skipping residue without triplet %s' % residue)
                    continue
#                resTypeList = [getDeepByKeys(triplet[i].db.nameDict, IUPAC) for i in tripletIdxList]  # Note that this was a major bug before today June 3, 2010.
                resTypeList = [getDeepByKeys(triplet[i].db.nameDict, IUPAC) for i in range(3)]
            else:
                NTcodeerror("validateDihedralCombinations called for non Rama/Janin/d1d2")
                return None

            if doingNewD1D2plot:
                # depending on doOnlyOverall it will actually return an array of myHist.
                myHistList = residue.getTripletHistogramList( doOnlyOverall = False, ssTypeRequested = ssType, doNormalize=doNormalize  )
                if myHistList == None:
                    NTdebug("Failed to get the D1D2 hist for %s; skipping. Perhaps a non-protein residue was the neighbor?" % residue)
                    continue
                if len(myHistList) != 3:
                    NTerror("Expected exactly one but found %s histogram for %s; skipping" % (len(myHistList),residue))
                    continue
#                myHist = myHistList[0]
            else:
                myHist = getDeepByKeysOrAttributes(histBySsAndResType,ssType,resName)
                if myHist == None:
#                    NTdebug("No hist for ssType %s and resName %s of residue %s" % (ssType,resName,residue))
                    continue
                myHistList = [ myHist ]

            d1 = getDeepByKeysOrAttributes(residue, dihedralName1)
            d2 = getDeepByKeysOrAttributes(residue, dihedralName2)

            if not (d1 and d2):
#                NTdebug( 'in validateDihedralCombinations dihedrals not found for residue: %s and checkId %s; skipping' % (residue, checkId ))
                continue

            if not (len(d1) and len(d2)):
#                NTdebug( 'in validateDihedralCombinations dihedrals had no defining atoms for 1: %s or', dihedralName1 )
#                NTdebug( 'in validateDihedralCombinations dihedrals had no defining atoms for 2: %s; skipping'   , dihedralName2 )
                continue

            pointList = zip( d1, d2 ) # x,y tuple list NOT REALLY NEEDED JUST CHECKING COUNTS
            modelCountNew = len(pointList)
            if modelCountNew != modelCount:
                NTwarning("Will use %d models instead of %d expected" %(modelCountNew, modelCount))
            if not resTypeList:
                resTypeList = [ resName ]

            zkList = []
            for i, myHist in enumerate(myHistList):
                if doingNewD1D2plot:
                    ssType = ssIdxToType(i)
                keyList = [ ssType ]
                keyList += resTypeList
#                NTdebug("Checking with keyList [%s]" % str(keyList))
                if normalizeBeforeCombining: # can't use predefined ones. Of course the debug checking below makes no sense with this.
                    Ctuple = getEnsembleAverageAndSigmaFromHistogram( myHist )
    #                Ctuple = getArithmeticAverageAndSigmaFromHistogram( myHist ) # TODO: discuss with GWV.
                    (c_av, c_sd, hisMin, hisMax) = Ctuple #@UnusedVariable
                else:
                    Ctuple = getDeepByKeysOrAttributes( histCtupleBySsAndResType, *keyList)
        #            NTdebug("keyList: %s" % str(keyList))
                    if not Ctuple:
                        NTwarning("Failed to get Ctuple for residue %s with keyList %s; skipping" % (residue, keyList))
                        continue
                    (c_av, c_sd, hisMin, hisMax, keyListStr) = Ctuple
                    keyListQueryStr = str(keyList)
                    if keyListStr != keyListQueryStr:
                        NTerror("Got keyListStr != keyListQueryStr: %s and %s" % (keyListStr, keyListQueryStr))
                        continue

                if myHist == None:
                    NTerror("Got None for hist for %s" % residue)
                    continue
                if True: # costly checks to be disabled later.
                    minHist = amin( myHist )
                    maxHist = amax( myHist )
                    zMin = (minHist - c_av) / c_sd
                    zMax = (maxHist - c_av) / c_sd

                myHistP = circularlizeMatrix(myHist) # consider caching if this is too slow.
                for modelIdx in range(modelCountNew):
                    if len(ensembleValueLoL) <= modelIdx:
                        ensembleValueLoL.append( NTlist())
                    a1 = d1[modelIdx]
                    a2 = d2[modelIdx]
                    # NB the histogram is setup with rows/columns corresponding to y/x-axis so reverse the order of the call here:
                    ck = getValueFromHistogramUsingInterpolation( myHistP, a2, a1, bins)
                    zk = ( ck - c_av ) / c_sd
                    zkList.append(zk)
                    if modelIdx == 0: # costly checks to be disabled later.
    #                if checkIdx == 2: # costly checks to be disabled later.
    #                if cing.verbosity >= cing.verbosityDebug: # costly checks to be disabled later.
                        msg = "chk %d ssType %4s res %20s mdl %2d a2 %8.2f a1 %8.2f c_av %12.3f c_sd %12.3f ck %12.3f zk %8.2f h- %12.3f h+ %12.3f z- %8.2f z+ %8.2f" % (
                                    checkIdx,
                                    ssType,residue,modelIdx,a2, a1,
                                    c_av, c_sd,ck,zk,
                                    minHist, maxHist, zMin, zMax)
                        if maxHist < c_av:
                            NTerror(msg + " maxHist < c_av")
                        elif maxHist < ck:
                            NTerror(msg + " maxHist < ck")
                        elif minHist > 1000.: # was found in GLY ASN LEU
                            NTwarning(msg + " minHist > 1000") # ' ' GLY GLY GLY
                        elif hisMin != minHist:
                            NTerror(msg + " hisMin != minHist: %8.0f %8.0f" % (hisMin, minHist))
                        elif hisMax != maxHist:
                            NTerror(msg + " hisMax != maxHist: %8.0f %8.0f" % (hisMax, maxHist))
                        else:
                            if doingNewD1D2plot:
                                NTdebug(msg)
                        # end if on checks
                    # end if on True
                    if not doingNewD1D2plot:
                        ensembleValueList[modelIdx] = zk
                    else:
                        ensembleValueLoL[modelIdx].append(zk)
                # end for modelIdx
            # end for SS
            if doingNewD1D2plot:
                for modelIdx in range(modelCountNew):
                    ensembleValueList[modelIdx] = max(ensembleValueLoL[modelIdx])
                    if modelIdx == 0:
                        NTdebug("For modelIdx %s found: %s and selected max: %s" % (modelIdx, str(ensembleValueLoL[modelIdx]), ensembleValueList[modelIdx] ))
        # end for checkIdx
    # end for residue
    msgHol.showMessage(MAX_MESSAGES=10, MAX_DEBUGS = 10)
#end def



def validateModels( self)   :
    """Validate the models on the basis of the dihedral outliers
    """

    if not self.molecule:
        NTerror("validateModels: no molecule defined")
        return True
    if not self.molecule.modelCount:
        NTwarning("validateModels: no model for molecule %s defined", self.molecule)
        return None

    backbone = ['PHI','PSI','OMEGA']

#    self.validateDihedrals(    )
    # self.models keeps track of the number of outliers per model.
    self.models = NTdict()
    for m in range(self.molecule.modelCount):
        self.models[m] = 0

    for res in self.molecule.allResidues():
#        for dihed in res.db.dihedrals.zap('name'):
        for dihed in backbone:
#            print res, dihed
#            if dihed in res and res[dihed] != None:
            if dihed in res and res[dihed]:
                d = res[dihed] # NTlist object
                try: # Looks like d doesn't always have good; TODO check why this can be so.
                    if not d.good:
                        continue
                except:
                    continue
                for m in d.outliers.zap( 0 ):    #get all modelId of outliers
                    self.models[m] += 1
            #end if
        #end for
    #end for
#    for m, count in self.models.items():
#        NTdebug('Model %2d: %2d backbone dihedral outliers', m, count )
#end def

# Originally in Scripts.convertPhiPsi2Db.py
binSize   = 10
binCount  = 360/binSize
# for ogrid: If the step length is not a complex number, then the stop is not inclusive.
#binCountJ = (binCount + 0)* 1j # used for numpy's 'gridding'.but fails anyway.
# Used for linear interpolation
# 0-360 is the most common range for the dihedrals; e.g. chis & ds
plotparams360 = plotParameters.getdefault(CHI1_STR,'dihedralDefault')
plotparams360P = deepcopy(plotparams360)
plotparams360P.min -= binSize
plotparams360P.max += binSize
#xGrid360,yGrid360 = ogrid[ plotparams360.min:plotparams360.max:binCountJ, plotparams360.min:plotparams360.max:binCountJ ]
xGrid360,yGrid360 = ogrid[ plotparams360.min:plotparams360.max:binSize, plotparams360.min:plotparams360.max:binSize ]
bins360 = (xGrid360,yGrid360)
xGrid360P,yGrid360P = ogrid[ plotparams360P.min:plotparams360P.max:binSize, plotparams360P.min:plotparams360P.max:binSize ]
bins360P = (xGrid360P,yGrid360P)

plotparams180 = plotParameters.getdefault(PHI_STR,'dihedralDefault')
plotparams180P = deepcopy(plotparams180)
plotparams180P.min -= binSize
plotparams180P.max += binSize
#xGrid180,yGrid180 = ogrid[ plotparams180.min:plotparams180.max:binCountJ, plotparams180.min:plotparams180.max:binCountJ ]
xGrid180,yGrid180 = ogrid[ plotparams180.min:plotparams180.max:binSize, plotparams180.min:plotparams180.max:binSize ]
bins180 = (xGrid180,yGrid180)
xGrid180P,yGrid180P = ogrid[ plotparams180P.min:plotparams180P.max:binSize, plotparams180P.min:plotparams180P.max:binSize ]
bins180P = (xGrid180P,yGrid180P)

def zscaleHist( hist2d, Cav, Csd ):
    hist2d -= Cav
    hist2d /= Csd
    return hist2d

def getValueFromHistogramUsingInterpolation( hist, v0, v1, bins):
    """Returns the value from the bin pointed to by v0,v1.
        think
    v0 row    y-axis
    v1 col    x-axis
    """
    tx = ogrid[ v0:v0:1j, v1:v1:1j ]
    interpolatedValueArray = interpn_linear( hist, tx, bins )
    interpolatedValue = interpolatedValueArray[ 0, 0 ]
#    NTdebug( 'tx: %-40s bins[1]: \n%s \nhist: \n%s\n%s' % ( tx, bins[1], hist, interpolatedValue ))
    return interpolatedValue



def getRescaling(valuesByEntrySsAndResType):
    '''Use a jack knife technique to get an estimate of the average and sd over all entry) scores.
    http://en.wikipedia.org/wiki/Resampling_%28statistics%29#Jackknife

    Returns the average, standard deviation, and the number of elements in the distribution.

    TODO: ADJUST FOR CIRCULAR NATURE.
    '''
    C = NTlist()
    for entryId in valuesByEntrySsAndResType.keys():
        histRamaBySsAndResTypeExcludingEntry = getSumHistExcludingEntry( valuesByEntrySsAndResType, entryId)
#        NTdebug("histRamaBySsAndResTypeExcludingEntry: %s" % histRamaBySsAndResTypeExcludingEntry )
        z = NTlist()
        for ssType in valuesByEntrySsAndResType[ entryId ].keys():
            for resType in valuesByEntrySsAndResType[ entryId ][ssType].keys():
                angleDict =valuesByEntrySsAndResType[  entryId ][ssType][resType]
                angleList0 = angleDict[ 'phi' ]
                angleList1 = angleDict[ 'psi' ]
                his = getDeepByKeys(histRamaBySsAndResTypeExcludingEntry,ssType,resType)
                if his == None:
                    NTdebug('when testing not all residues are present in smaller sets.')
                    continue
                (c_av, c_sd, hisMin, hisMax) = getEnsembleAverageAndSigmaFromHistogram( his )
#                NTdebug("For entry %s ssType %s residue type %s found (c_av, c_sd) %8.3f %s" %(entryId,ssType,resType,c_av,`c_sd`))
                if c_sd == None:
                    NTdebug('Failed to get c_sd when testing not all residues are present in smaller sets.')
                    continue
                if c_sd == 0.:
                    NTdebug('%s Got zero c_sd, ignoring histogram. This should only occur in smaller sets.' % entryId)
                    continue
                if True: # disable when done debugging.
                    keyList = [ ssType, resType ]
                    Ctuple = getDeepByKeysOrAttributes( hPlot.histRamaCtupleBySsAndResType, *keyList)
                    if not Ctuple:
                        NTwarning("Failed to get Ctuple for keyList %s; skipping" % (keyList))
                        continue
                    (c_av_stored, c_sd_stored, minHist, maxHist, keyListStr) = Ctuple #@UnusedVariable
                    if hisMin != minHist:
                        NTerror(" hisMin != minHist: %8.0f %8.0f" % (hisMin, minHist))
                    elif hisMax != maxHist:
                        NTerror(" hisMax != maxHist: %8.0f %8.0f" % (hisMax, maxHist))
                    # TODO: extend checks to stored; then when debugged rewrite the code to use only the stored.
                for k in range(len(angleList0)):
                    ck = getValueFromHistogramUsingInterpolation(
                        histRamaBySsAndResTypeExcludingEntry[ssType][resType],
                        angleList0[k], angleList1[k])
                    zk = ( ck - c_av ) / c_sd
#                    NTdebug("For entry %s ssType %s residue type %s resid %3d found ck %8.3f zk %8.3f" %(entryId,ssType,resType,k,ck,zk))
                    z.append( zk )
        (av, sd, n) = z.average()
        NTdebug("%4s,%8.3f,%8.3f,%d" %( entryId, av, sd, n))
        C.append( av )
    (Cav, Csd, Cn) = C.average()
    return (Cav, Csd, Cn)


def getSumHistExcludingEntry( valuesByEntrySsAndResType,  entryIdToExclude, isRange360=True):
    """Todo generalize to do other angles."""
    xRange = (plotparams360.min, plotparams360.max)
    yRange = (plotparams360.min, plotparams360.max)
    hrange = (xRange, yRange)
    histRamaBySsAndResTypeExcludingEntry = {}
    result = {}

    for entryId in valuesByEntrySsAndResType.keys():
        if entryId == entryIdToExclude:
            continue
        valuesBySsAndResType = valuesByEntrySsAndResType[entryId]
        for ssType in valuesBySsAndResType.keys():
            for resType in valuesBySsAndResType[ssType].keys():
                angleList0 = valuesBySsAndResType[ssType][resType]['phi']
                angleList1 = valuesBySsAndResType[ssType][resType]['psi']
                appendDeepByKeys(result,angleList0,ssType,resType,'phi')
                appendDeepByKeys(result,angleList1,ssType,resType,'psi')


    for ssType in result.keys():
        for resType in result[ssType].keys():
            angleList0 = result[ssType][resType]['phi']
            angleList1 = result[ssType][resType]['psi']
#            NTdebug( 'entry: %s ssType %s resType %s angleList0 %s' % (
#                entryId, ssType, resType, angleList0 ))
            hist2d, _xedges, _yedges = histogram2d(
                angleList1, # think rows (y)
                angleList0, # think columns (x)
                bins = binCount,
                range= hrange)
            setDeepByKeys( histRamaBySsAndResTypeExcludingEntry, hist2d, ssType, resType )

    return histRamaBySsAndResTypeExcludingEntry



def inRange(a, isRange360=True):
    if isRange360:
        if a < plotparams360.min or a > plotparams360.max:
            return False
        return True
    if a < plotparams180.min or a > plotparams180.max:
        return False
    return True

