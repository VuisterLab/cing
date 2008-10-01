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
from cing import NaNstring
from cing import cingPythonCingDir
from cing.Libs.Geometry import violationAngle
from cing.Libs.NTutils import NTcodeerror
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTdetail
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTfill
from cing.Libs.NTutils import NTlimit
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTsort
from cing.Libs.NTutils import NTvalue
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import ROGscore
from cing.Libs.NTutils import formatList
from cing.Libs.NTutils import fprintf
from cing.Libs.NTutils import getDeepByKeys #@UnresolvedImport
from cing.Libs.NTutils import list2asci #@UnusedImport
from cing.Libs.NTutils import sprintf
from cing.Libs.NTutils import val2Str
from cing.Libs.cython.superpose import NTcVector #@UnresolvedImport
from cing.Libs.fpconst import NaN
from cing.Libs.peirceTest import peirceTest
from cing.core.constants import COLOR_GREEN
from cing.core.constants import COLOR_ORANGE
from cing.core.constants import COLOR_RED
from cing.core.molecule import Residue
from cing.core.molecule import disulfideScore
from cing.core.molecule import dots
from cing.core.constants import NOSHIFT
from cing.core.molecule import Atom
import math
import os
import shelve
import sys
#from cing.PluginCode.Whatif import criticizeByWhatif
#from cing.core.classes import HTMLfile
#from cing.core.classes import htmlObjects

dbaseFileName = os.path.join( cingPythonCingDir,'PluginCode','data', 'phipsi_wi_db.dat' )
dbase = shelve.open( dbaseFileName )
#        histCombined               = dbase[ 'histCombined' ]
#histRamaBySsAndResType         = dbase[ 'histRamaBySsAndResType' ]
#    histBySsAndCombinedResType = dbase[ 'histBySsAndCombinedResType' ]
dbase.close()

def runCingChecks( project, ranges=None ):
    project.validateDihedrals()
    project.validateModels()
    project.validateAssignments(toFile=True)
    project.checkForSaltbridges(toFile=True)
    project.checkForDisulfides(toFile=True)
    project.validateRestraints( toFile=True)
    if project.molecule: 
        project.molecule.calculateRMSDs( ranges=ranges)
    project.criticize(toFile=True)
    project.summary(toFile=True)
    project.mkMacros()
#end def

"""Stolen from doValidate.py in Script directory. Need this here so the
code can be tested. I.e. returns a meaningful status if needed.
"""
def validate( project, ranges=None, parseOnly=False, htmlOnly=False,  
        doProcheck = True, doWhatif=True ):
    project.runShiftx()
    project.runDssp(parseOnly=parseOnly)
    if doProcheck:
        project.runProcheck(ranges=ranges, parseOnly=parseOnly)
    if doWhatif:
        project.runWhatif(parseOnly=parseOnly)
    project.runCingChecks(ranges=ranges)
    project.setupHtml()
    project.generateHtml(htmlOnly = htmlOnly)    
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
        pl.rogScore.reset()
        for peak in pl:
            peak.rogScore.reset()
            for i in range(peak.dimension):
                resonance = peak.resonances[i]
                if resonance and resonance.atom != None and resonance.value != NOSHIFT:
                    resonance.atom.peakPositions.append(peak.positions[i])
                    if not resonance.atom.isAssigned():
                         peak.rogScore.setMaxColor( COLOR_ORANGE,
                                                    sprintf('ORANGE: dimension %d: Atom %s not assigned', i, resonance.atom)
                                                  )
                    else:
                        if resonance.atom.db.spinType in errorMargins:
                            shift = resonance.atom.shift()
                            errM = errorMargins[resonance.atom.db.spinType]
                            if math.fabs(resonance.value-shift)> 2.0*errM:
                                peak.rogScore.setMaxColor( COLOR_RED,
                                    sprintf('RED: dimension %d: position (%.2f) - shift Atom %s (%.2f) > 2.0*(%.2f)',
                                             i, resonance.value, resonance.atom, shift, errM)
                                )

                            elif math.fabs(resonance.value-shift)> 1.0*errM:
                                peak.rogScore.setMaxColor( COLOR_ORANGE,
                                    sprintf('ORANGE: dimension %d: position (%.2f) - shift Atom %s (%.2f) > 1.0*(%.2f)',
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

#    project.validateAssignments(toFile = False)

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
            NTdetail('Peak analysis %s, output to: %s', pl, path)
        #end for
    #end if
#end def


def _criticizeResidue( residue, valSets ):
    """
    Use whatif, procheck scores and CING for critique of residue; translate into ROG scores.
    """

    residue.rogScore.reset()

#    result = NTdict()
    # WHATIF
    if residue.has_key('whatif'):
        for key in ['BBCCHK', 'C12CHK', 'RAMCHK']:
            NTdebug('Now criticizing %s, whatif key %s', residue, key )

            thresholdValuePoor = valSets[ 'WI_POOR_'+key ]
            thresholdValueBad  = valSets[ 'WI_BAD_'+key ]

            actualValue        = getDeepByKeys(residue,'whatif', key, 'valueList') #TODO remove this valueList stuff
            if actualValue == None:
                #print '>>', residue,key
                continue
            if isinstance(actualValue, NTlist):
                actualValue = actualValue.average()[0]

            NTdebug('actual %s, thresholdPoor %s, thresholdBad %s',
                    actualValue, thresholdValuePoor, thresholdValueBad)

            actualValueStr = val2Str( actualValue, fmt='%8.3f', count=8 )
            if actualValue < thresholdValueBad: # assuming Z score
                comment = 'RED: whatif [%s] value %s <%8.3f' % (key, actualValueStr, thresholdValueBad)
                NTdebug(comment)
                residue.rogScore.setMaxColor( COLOR_RED, comment)
            elif actualValue < thresholdValuePoor:
                comment = 'ORANGE: whatif [%s] value %s <%8.3f' % (key, actualValueStr, thresholdValuePoor)
                NTdebug(comment)
                residue.rogScore.setMaxColor( COLOR_ORANGE, comment)
            #endif
            residue.rogScore[key] = actualValue
        #end for
    #end if

    #Procheck
    if residue.has_key('procheck'):
        for key in ['gf']:
            NTdebug('Now criticizing %s, procheck key %s', residue, key )

            thresholdValuePoor = valSets[ 'PC_POOR_'+key.upper() ]
            thresholdValueBad  = valSets[ 'PC_BAD_'+key.upper() ]

            actualValue        = getDeepByKeys(residue,'procheck', key )
            if actualValue == None:
                #print '>>', residue,key
                continue
            if isinstance(actualValue, NTlist):
                actualValue = actualValue.average()[0]

            NTdebug('actual %s, thresholdPoor %s, thresholdBad %s',
                    actualValue, thresholdValuePoor, thresholdValueBad)

            actualValueStr = val2Str( actualValue, fmt='%8.3f', count=8 )
            if actualValue < thresholdValueBad: # assuming Z score
                comment = 'RED: procheck [%s] value %s <%8.3f' % (key, actualValueStr, thresholdValueBad)
                NTdebug(comment)
                residue.rogScore.setMaxColor( COLOR_RED, comment)
            elif actualValue < thresholdValuePoor:
                comment = 'ORANGE: procheck [%s] value %s <%8.3f' % (key, actualValueStr, thresholdValuePoor)
                NTdebug(comment)
                residue.rogScore.setMaxColor( COLOR_ORANGE, comment)
            #endif
            residue.rogScore[key] = actualValue
        #end for
    #end if

    #OMEGA
    dihed = 'OMEGA'
    if dihed in residue and residue[dihed]:
        d = residue[dihed] # NTlist object
        modelId = 0
        for value in d:
            v = violationAngle(value=value, lowerBound=180., upperBound=180)
            if v > 90.: # Never mind a cis
                v = violationAngle(value=value, lowerBound=-180., upperBound=-180)
#                    NTdebug('found residue %s model %d omega to violate from square trans/cis: %8.3f' % (
#                            res, modelId, v) )
            if v >= valSets.OMEGA_MAXALL_BAD:
                residue.rogScore.setMaxColor( COLOR_RED, ROGscore.ROG_COMMENT_BAD_OMEGA )
#                        res.rogScore.setMaxColor( COLOR_RED, ROGscore.ROG_COMMENT_BAD_OMEGA + ' double on purpose; TODO: REMOVE')
                NTdebug('Set to red')
            elif v >= valSets.OMEGA_MAXALL_POOR:
                residue.rogScore.setMaxColor( COLOR_ORANGE, ROGscore.ROG_COMMENT_BAD_OMEGA )
                NTdebug('Set to orange (perhaps)')
            modelId += 1
        #end for
        residue.rogScore['OMEGA'] = v
    #end if
    return residue.rogScore
#end def


def criticize(project, toFile=True):
    # initialize
    NTdetail('==> criticizing project')

    if project.molecule:
        project.molecule.rogScore.reset()
        for color in [COLOR_GREEN,COLOR_ORANGE,COLOR_RED]:
            project.molecule[color] = NTlist()

        for res in project.molecule.allResidues():
            _criticizeResidue( res, project.valSets )
            project.molecule[res.rogScore.colorLabel].append(res)
            res.chain.rogScore.setMaxColor(res.rogScore.colorLabel, 'Inferred from residue ROG scores')
        #end for

        if len(project.molecule[COLOR_RED]) > 0:
            project.molecule.rogScore.setMaxColor(COLOR_RED,'Inferred from residue ROG scores')
        elif len(project.molecule[COLOR_ORANGE]) > 0:
            project.molecule.rogScore.setMaxColor(COLOR_ORANGE,'Inferred from residue ROG scores')

        if toFile:
            path = project.moleculePath('analysis', 'ROG.txt')
            f = file(path,'w')
            for residue in project.molecule.allResidues():
                fprintf(f, '%-8s %4d %-6s  ', residue.name, residue.resNum, residue.rogScore.colorLabel)
                keys = residue.rogScore.keys()
                for key in ['BBCCHK', 'C12CHK', 'RAMCHK', 'gf', 'OMEGA']:
                    if key in keys:
                        fprintf(f,'%-6s %-8s   ', key, val2Str( residue.rogScore[key], fmt='%8.3f', count=8 ))
                    else:
                        fprintf(f,'%-6s %8s   ', key, '.   ')
                    #end if
                #end for
                fprintf(f,'%s\n', residue.rogScore.colorCommentList)
            #end for
            f.close()
            NTdetail('Project.critique: output to "%s"', path)
        #end if
    #end if

    # distance and dihedral restraints
    for drl in project.distances + project.dihedrals:
        drl.criticize(project, toFile=toFile)
    #Peaks
    criticizePeaks( project, toFile=toFile )

#end def

def _ROGsummary( residueList ):
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
    return msg
#end def


def summary( project, toFile = True ):
    """
    Generate a summary string and store to text file
    Return summary string or None on error.
    """
    if not project.molecule:
        NTerror('Project.Summary: Strange, there was no molecule in this project')
        return None

    msg = sprintf( '=================== CING SUMMARY project %s ===================\n', project.name )

#    msg += sprintf( '%s\n', project.molecule.format() )

    if project.molecule.has_key('rmsd' ):
        msg += sprintf( '\n%s\n', project.molecule.rmsd.format() )

    for drl in project.distances + project.dihedrals + project.rdcs:
        msg += sprintf( '\n%s\n', drl.format() )

    msg += "\n%s CING ROG analysis (all residues) %s\n%s\n" % (dots, dots, _ROGsummary(project.molecule.allResidues()))
    if project.molecule.ranges:
        r = project.molecule.ranges
        msg += "\n%s CING ROG analysis (residues %s) %s\n%s\n" % \
               (dots, r, dots, _ROGsummary(project.molecule.ranges2list(r)))

    wiSummary = getDeepByKeys(project.molecule, 'wiSummary') # Hacked bexause should be another procheck level inbetween.
    if wiSummary:
        msg += '\n' + wiSummary

    pc = getDeepByKeys(project.molecule, 'procheck')
    if pc:
        if hasattr(pc, "summary"):
            msg += '\n' + pc.summary.format()
        else:
            NTerror("Failed to find the procheck summary attribute")

    if toFile:
        fname = project.path(project.molecule.name, project.moleculeDirectories.analysis,'summary.txt')
        fp = open( fname, 'w' )
        NTmessage( '==> summary, output to %s', fname)
        fprintf( fp, msg )
        fp.close()
    #end if

    return msg
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

    # distances and dihedrals
    for res in project.molecule.allResidues():
        res.distanceRestraints = NTlist()
        res.dihedralRestraints = NTlist()
    #end for

    # distances
    for drl in project.distances:
        drl.analyze()
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

        # Sort restraints on a per-residue basis
        for restraint in drl:
            for atm1,atm2 in restraint.atomPairs:
                atm1.residue.distanceRestraints.add( restraint ) #AWSS
                atm2.residue.distanceRestraints.add( restraint ) #AWSS
            #end for
        #end for
    #end for

    # dihedrals
    for drl in project.dihedrals:
        drl.analyze()
        msg += sprintf( '%s\n', drl.format())
        drl.sort('violMax').reverse()
        msg += sprintf( '%s Sorted on Maximum Violations %s\n', dots, dots)
        msg += sprintf( '%s\n', formatList( drl[0:min(len(drl),30)] ) )

        drl.sort('violCount3').reverse()
        msg += sprintf( '%s Sorted on Violations > 3 degree %s\n', dots, dots)
        msg += sprintf( '%s\n', formatList( drl[0:min(len(drl),30)] ) )

        # sort the restraint on a per residue basis
        for restraint in drl:
            restraint.atoms[2].residue.dihedralRestraints.add( restraint ) #AWSS
        #end for
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
                sum   = d.violations.sum( sum )
                sumsq = d.violations.sumsq( sumsq )
                n += len(d.violations)
            #end for
            if n == 0:
                NTwarning('No DRs so no rmsd')
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
            phi = NTvalue( res.PHI.cav, res.PHI.cv, fmt='%7.1f %7.2f' )
        else:
            phi = NTvalue( '-', '-', fmt='%7s %7s' )
        #end if
        if res.has_key('PSI'):
            psi = NTvalue( res.PSI.cav, res.PSI.cv, fmt='%7.1f %7.2f' )
        else:
            psi = NTvalue( '-', '-', fmt='%7s %7s' )
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
    NTdebug(msg)
    if toFile:
        #project.mkdir(project.directories.analysis, project.molecule.name)
        fname = project.path(project.molecule.name, project.moleculeDirectories.analysis,'restraints.txt')
        fp = open( fname, 'w' )
        NTmessage( '==> validateRestraints, output to %s', fname)
        fprintf(fp, msg)
    #end if
#end def

def checkForDisulfides(project, toFile=True):
    """Just check for potential disulfide bonds.
    """
    NTdebug('Identify the disulfide bonds.')

    if not project.molecule:
        NTerror('checkForDisulfides: no molecule defined')
        return None
    #end if

    cys=project.molecule.residuesWithProperties('C')
    disulfides = NTlist()
    # all cys(i), cys(j) pairs with j>i
    for i in range(len(cys)):
        c1 = cys[i]
        for j in range(i+1, len(cys)):
            c2 = cys[j]
            scoreList = disulfideScore( c1, c2)
            disulfides.append( (c1, c2, scoreList) ) # keep track of data
        #end for
    #end for
    if toFile:
        path = project.moleculePath('analysis','disulfides.txt')
        f = file(path,'w')
        fprintf(f, '========= Disulfide analysis %s =========\n\n', project.molecule)
        for c1,c2,scoreList in disulfides:
            fprintf(f, '%s %s: scores dCa, dCb, S-S dihedral: %s ', c1,c2,scoreList)
            if scoreList[3] >= 0.9:
                fprintf(f,' certain disulfide\n')
            elif scoreList[3] >= 0.3:
                fprintf(f,' potential disulfide\n')
            else:
                fprintf(f,'\n')
            #end if
        #end for
        NTmessage('==> Disulfide analysis, output to %s', path)
    #end if
# end def


def checkForSaltbridges( project, cutoff = 5, toFile=False)   :
    """
    Routine to analyze all potential saltbridges involving E,D,R,K and H residues.
    Initiates an NTlist instances as saltbridges attribute for all residues.

    Returns a NTlist with saltbridge summaries.

    Optionally print output to file in analysis directory of project.
    """
    if not project.molecule:
        NTerror('checkForSaltbridges: no molecule defined')
        return None
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
    result = NTlist()
    for res1 in residues1:
        for res2 in residues2:
            #print '>>', res1, res2
            s = validateSaltbridge(res1,res2)
            if s:
                if (s.types[4][1] <= cutoff):    # less then cutoff 'not observed'
                    if toFile:
                        fprintf(fp, '%s\n', s.format() )
#                    NTdebug(    '%s\n', s.format() )
                    res1.saltbridges.append( s )
                    res2.saltbridges.append( s )
                    result.append( s )
                #end if
            #end if
        #end for
    #end for

    if s:
        if toFile:
            fprintf( fp, '%s\n', s.comment )
        NTdebug(     '%s\n', s.comment )
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

    Validate presence of saltbridge, CC-Bridge, NO-bridge, or ion-pair beteween residue1 and residue2
    Ref: Kumar, S. and Nussinov, R. Biophys. J. 83, 1595-1612 (2002)

    residue1, residue2: Residue instances of type E,D,H,K,R

    Arbitrarily set the criteria for ion-pair r,theta to be within 2 sd of average,
    else set type to none.

    Returns summary NTdict or None on error
    """

    # Definitions of the centroids according to the paper
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
        NTerror('validateSaltbridge: undefined residue1\n')
        return None
    #end if
    if residue2 == None:
        NTerror('validateSaltbridge: undefined residue2\n')
        return None
    #end if

    modelCount = residue1.chain.molecule.modelCount
    if modelCount == 0:
        NTerror('validateSaltbridge: no structure models\n')
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
            atm = residue[atmName]
            if len(atm.coordinates) == 0:
                NTerror('validateSaltbridge: no coordinates for atom %s', atm)
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
    summary.rAv, summary.rSd, summary.modelCount = result.zap('r').average()
    summary.min   = min( result.zap('r') )
    summary.max   = max( result.zap('r') )
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

def validateAssignments( project, toFile = True   ):
    """
    Validate the assignments; check for potential problems and inconsistencies
    Add's NTlist instance with strings of warning description to each atom as
    validateAssignment attribute

    return a NTlist of atoms with errors.
    Generate output in moleculeName/Cing/validateAssignments.txt if toFile is True.

    return None on code error.

    @todo: Also correlate assignment with peak values (if present)
    """
    NTdebug("Starting validateAssignments")
    if not project.molecule:
        NTerror('validateAssignments: no molecule defined')
        return None
    #end if

    funcName = validateAssignments.func_name
    result = NTlist()
    if project.molecule.resonanceCount == 0:
        NTdebug("No resonance assignments read so no real validation on it can be done. Let's try anyway.")
#        return result

    for atm in project.molecule.allAtoms():
        atm.rogScore.reset()
        atm.validateAssignment = NTlist()
        if atm.isAssigned():
            # Check database
            #print '===>', atm
            if not atm.db.shift:
                dummy = atm.pseudoAtom()
                if dummy.db.shift:
                    av = dummy.db.shift.average
                    sd = dummy.db.shift.sd
                else:
                    NTerror("%s: '%s' not in in DB SHIFTS\n", funcName, atm)
                    continue
                #end if
            else:
                av = atm.db.shift.average
                sd = atm.db.shift.sd
            #end if

            shift = atm.shift()

            # Check the shift against the database
            delta = math.fabs(shift - av) / sd
            if delta > 3.0:
                string = sprintf('%s: %.2f ppm is %.1f*sd away from average (%.2f,%.2f)',
                                 'SHIFT', shift, delta, av, sd
                                )
#                NTmessage('%-20s %s', atm, string)
                result.append( atm )
                atm.validateAssignment.append(string)
            #end if

            # Check if not both realAtom and pseudoAtom are assigned
            if atm.hasPseudoAtom() and atm.pseudoAtom().isAssigned():
                string = sprintf('%s: atm also has %s assigned', MULTIPLE_ASSIGNMENT, atm.pseudoAtom() )
#                NTmessage('%-20s %s', atm, string)
                result.append( atm )
                atm.validateAssignment.append(string)
            #end if

            # Check if not pseudoAtom and realAtom are assigned
            if atm.isPseudoAtom():
                for a in atm.realAtoms():
                    if a.isAssigned():
                        string = sprintf('%s: atm also has %s assigned', MULTIPLE_ASSIGNMENT, a )
#                        NTmessage('%-20s %s', atm, string)
                        result.append( atm )
                        atm.validateAssignment.append(string)
                    #end if
                #end for
            #end if

            # Check if all realAtoms are assigned in case there is a pseudo atom
            if atm.hasPseudoAtom():
                for a in atm.pseudoAtom().realAtoms():
                    if not a.isAssigned():
                        string = sprintf('%s: expected also %s to be assigned.', MISSING_ASSIGNMENT, a )
#                        NTmessage('%-20s %s', atm, string )
                        result.append( atm )
                        atm.validateAssignment.append(string)
                    #end if
                #end for
            #end if

            # Check for protons with unassigned heavy atoms
            if atm.isProton():
                heavyAtm = atm.topology()[0]
                if not heavyAtm.isAssigned():
                    string = sprintf('%s: expected %s to be assigned', EXPECTED_ASSIGNMENT, heavyAtm )
#                    NTmessage('%-20s %s', atm, string )
                    result.append( atm )
                    atm.validateAssignment.append(string)
                #end if
            #end if atm.isProton()

            # stereo assignments checks
            if atm.isStereoAssigned():
                if not atm.isProChiral():
                    string = sprintf('%s: %s not a prochiral atom', INVALID_STEREO_ASSIGNMENT, atm )
                    result.append( atm )
                    atm.validateAssignment.append(string)
                else:
                    # Check prochiral partner assignments
                    partner = atm.proChiralPartner()
                    if partner:
                        if not partner.isAssigned():
                            string = sprintf('%s: prochiral partner %s not assigned', INVALID_STEREO_ASSIGNMENT, partner )
                            result.append( atm )
                            atm.validateAssignment.append(string)
                        else:
                            if not partner.isStereoAssigned():
                                string = sprintf('%s: prochiral partner %s not stereo assigned', INVALID_STEREO_ASSIGNMENT, partner )
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
                        string = sprintf('%s: prochiral methyl carbon %s not stereo assigned', INVALID_STEREO_ASSIGNMENT, heavy )
                        result.append( atm )
                        atm.validateAssignment.append(string)
                    #end if
                    if not atm.isStereoAssigned() and heavy.isStereoAssigned():
                        string = sprintf('%s: prochiral methyl carbon %s is stereo assigned', INVALID_STEREO_ASSIGNMENT, heavy )
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
                        string = sprintf('%s: prochiral methyl proton %s not stereo assigned', INVALID_STEREO_ASSIGNMENT, pseudo )
                        result.append( atm )
                        atm.validateAssignment.append(string)
                    #end if
                    if not atm.isStereoAssigned() and pseudo.isStereoAssigned():
                        string = sprintf('%s: prochiral methyl proton %s is stereo assigned', INVALID_STEREO_ASSIGNMENT, pseudo )
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
        #end if
    #end for


    if toFile:
        #path = project.mkdir( project.directories.analysis, project.molecule.name )
        fname = project.path(project.molecule.name, project.moleculeDirectories.analysis, 'validateAssignments.txt')
        fp = open( fname,'w' )
        if not fp:
            NTerror("Failed to open for writing: " + fname)
            return None
        NTdebug("Writing assignment validation to: " + fname)

        fmt = '%-18s   %8s %6s %6s   %8s %6s   %8s %8s  %8s %6s   %s\n'
        for res in project.molecule.allResidues():
            fprintf(fp, fmt, '#',  'resonance', 'error', 'stereo', 'shiftx', 'error', 'delta', 'error', 'dbase', 'error', 'Critique')

            for atm in res.allAtoms():
                #TODO: this code also appears in AtomsHTMLfile
                sav     = None
                ssd     = None
                delta   = None
                rdelta  = None
                dav     = None
                dsd     = None
                value   = None
                error   = None

                if atm.has_key('shiftx') and len(atm.shiftx) > 0:
                    sav = atm.shiftx.av
                    ssd = atm.shiftx.sd
                if atm.isAssigned() and sav:
                    delta = atm.resonances().value - sav
                    rdelta = 1.0
                    if ssd > 0.0:
                        rdelta = sav/ssd
                if atm.db.shift:
                    dav = atm.db.shift.average
                    dsd = atm.db.shift.sd
                if atm.resonances():
                    value = atm.resonances().value
                    error = atm.resonances().error

                savStr     = val2Str(sav,   '%6.2f', 6 )
                ssdStr     = val2Str(ssd,   '%6.2f', 6 )
                deltaStr   = val2Str(delta, '%6.2f', 6 )
                rdeltaStr  = val2Str(rdelta,'%6.2f', 6 )
                davStr     = val2Str(dav,   '%6.2f', 6 )
                dsdStr     = val2Str(dsd,   '%6.2f', 6 )
                valueStr   = val2Str(value, '%6.2f', 6 ) # was sometimes set to a NOSHIFT
                if valueStr==NaNstring:
                    error=None
                errorStr   = val2Str(error, '%6.2f', 6 )

                if atm.isStereoAssigned():
                    stereo = 'S'
                else:
                    stereo = '.'

                fprintf(fp,fmt,
                        atm._Cname(-1),
                        valueStr,
                        errorStr,
                        stereo,
                        savStr, ssdStr,
                        deltaStr, rdeltaStr,
                        davStr, dsdStr,
                        atm.validateAssignment.format()
                       )
            #end for
        #end for
        fp.close()
        NTmessage('==> validateAssignments: output to "%s"', fname)
    #end if

    return result
#end def

def restoreDihRestraintInfo(project):
    """To restore restraint.residue and restraint.angle"""
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

def validateModels( self)   :
    """Validate the models on the basis of the dihedral outliers
    """

    if not self.molecule:
        NTerror("validateModels: no molecule defined")
        return True
    if not self.molecule.modelCount:
        NTerror("validateModels: no model for molecule %s defined", project.molecule) #@UndefinedVariable
        return True

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
    for m, count in self.models.items():
        NTdebug('Model %2d: %2d backbone dihedral outliers', m, count )
#end def


#def validate( project, ranges=None, htmlOnly = False, doProcheck = True, doWhatif = True ):
#    """Validatation tests returns None on success or True on failure.
#    """
#    # OBSOLETE; eplaced by script doValidate
#    if setupValidation( project, ranges=ranges, doProcheck=doProcheck, doWhatif=doWhatif ):
#        NTerror("validate: Failed to setupValidation")
#        return True
#
#    if setupHtml(project):
#        NTerror("validate: Failed to setupHtml")
#        return True
#
#
#    if renderHtml(project):
#        NTerror("validate: Failed to renderHtml")
#        return True
#
#    NTmessage("Done with overall validation")
##end def

# register the functions
methods  = [(validateDihedrals, None),
            (validateModels,None),
            (validateAssignments, None),
            (validateRestraints, None),
#            (validate, None),
            (runCingChecks, None),
            (validate,None),
            (criticizePeaks, None),
            (summary, None),

            (checkForSaltbridges, None),
            (checkForDisulfides, None),
            (fixStereoAssignments, None),
#            (setupValidation, None),

#            (setupHtml, None),
#            (generateHtml, None),
#            (renderHtml, None),

#            (calculateRmsd, None),
#            (makeDihedralHistogramPlot, None),
#            (makeDihedralPlot, None),
           ]
#saves    = []
restores = [(criticize,False)
           ]
#exports  = []