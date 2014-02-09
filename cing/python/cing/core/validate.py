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

v3:
object have ValidationResults container (key VALIDATION_KEY) with "Program"Results objects
stored under "PROGRAM"_KEY
"""

import time

import cing
from cing import definitions as cdefs
from cing import constants
from cing.Libs import Adict
from cing.Libs import io

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
from cing.PluginCode.required.reqProcheck import PROCHECK_STR
from cing.PluginCode.required.reqShiftx import SHIFTX_STR
from cing.PluginCode.required.reqVasco import VASCO_STR
from cing.PluginCode.required.reqWattos import WATTOS_STR
from cing.PluginCode.required.reqWattos import WATTOS_SUMMARY_STR
from cing.PluginCode.required.reqWhatif import WHATIF_STR
from cing.core.ROGscore import CingResult
from cing.core.classes2 import RestraintList
from cing.constants import * #@UnusedWildImport
from cing.core.molecule import Atom
from cing.core.molecule import Chain
from cing.core.molecule import Molecule
from cing.core.molecule import Residue
from cing.core.parameters import plotParameters
from cing.definitions import validationDirectories
from cing import plugins
from numpy.lib.index_tricks import ogrid
from numpy.lib.twodim_base import histogram2d

CUTOFF_SALTBRIDGE_BY_Calpha = 20.0 # DEFAULT: 20
TRANS_OMEGA_VALUE           = 179.6
CIS_OMEGA_VALUE             = 0.0
OMEGA_SD                    = 4.7  # Know from literature of hi-res X-ray structures.

class ValidationResultsContainer( Adict.Adict ):
    """v3: Container class for validation results
    key: constants.VALIDATION_KEY
    """
    def __init__(self, *args, **kwds):
        Adict.Adict.__init__(self, *args, **kwds)
        self.setattrOnly(constants.OBJECT_KEY, None)
    #end def

    def format(self):
        object = self.getattrOnly(constants.OBJECT_KEY)
        if object == None:
            return ''
        result = '======== %s ========\n' % str(object)
        for key, value in self.iteritems():
            if value != None:
                result += '-------- %s --------\n' % value
                result += io.formatDictItems(value,
                                             '{key:20} : {value!s}\n'
                                            )
            #end if
        #end for
        return result
    #end def
#end class

class ValidationResult( Adict.Adict ):
    """v3:base class for validation results dict's
    """
    def __str__(self):
        if self.object != None:
            s =  '<%s: %s>'      % (self.__class__.__name__,
                                    self.object.cName(-1)
                                   )
        else:
            s =  '<%s: %s>'      % (self.__class__.__name__,
                                    'None'
                                   )
        #end if
        return s

    def asPid(self):
        if self.object != None:
            key = self.getattrOnly(constants.KEY_KEY)
            s =  '<%s:%s.%s.%s>' % (self.__class__.__name__,
                                    self.object.cName(-1),
                                    constants.VALIDATION_KEY,
                                    key
                                   )
        else:
            s =  '<%s:%s>'       % (self.__class__.__name__,
                                    'None'
                                   )
        #end if
        return s
    #end def
#end class

def hasValidationResult(object,key):
    return (getValidationResult() != None)

def getValidationResult(object,key):
    """v3:Returns validation result for key or None if not present
    """
    if not hasattr(object, constants.VALIDATION_KEY):
        return None
    validation = getattr(object, constants.VALIDATION_KEY)
    if key not in validation:
        return None
    return validation[key]
#end def

def setValidationResult(object,key,result):
    """v3: Add result to objects validation container instance under key,
    add reverse linkage to result under constants.OBJECT_KEY
    return True on error
    """
#    print '>>', object, key, result
    if object == None:
        nTerror('setValidationResult: invalid object')
        return True
    if key == None:
        nTerror('setValidationResult: invalid key')
        return True
    #v3: use attribute method so v3 will not 'suffer'
    if not hasattr(object, constants.VALIDATION_KEY):
        setattr(object, constants.VALIDATION_KEY, ValidationResultsContainer())
    validation = getattr(object, constants.VALIDATION_KEY)

    validation[key] = result
    validation.setattrOnly(constants.OBJECT_KEY, object)

    if result != None:
        result[constants.OBJECT_KEY] = object
        result.setattrOnly(constants.KEY_KEY, key)
    return False
#end def


def runCingChecks( project, toFile=True, ranges=None ):
    """This set of routines needs to be run after a project is restored."""

    if project.molecule:
        if ranges == None:
            ranges = project.molecule.ranges

#    nTdebug("Now in validate#runCingChecks with toFile:%s and ranges: %s" % (toFile,ranges))
    project.partitionRestraints()
    project.analyzeRestraints()
    project.validateRestraints(toFile)
    project.validateDihedrals()
    project.validateModels()
    project.validateDihedralCombinations()
#    project.validateAssignments() in criticize now
    # project.mergeResonances() GWV says: don't do this

    project.checkForSaltbridges(toFile=toFile)

# GWV this is done in molecule.updateAll
    if project.molecule:
        project.molecule.calculateRMSDs( ranges=ranges)
        project.molecule.idDisulfides(toFile=toFile, applyBonds=False)

    project.criticize(toFile)
    project.summaryForProject(toFile)
    project.mkMacros()
    project.getCingSummaryDict()
#end def

def validate( project, ranges=None, parseOnly=False, htmlOnly=False,
        doShiftx = True,
        doProcheck = True, doWhatif=True, doWattos=True, doTalos=True, doQueeny=True, doSuperpose = True,
        filterVasco = False, filterTopViolations = False,
        validateFastest = False, validateCingOnly = False, validateImageLess = False ):
    "Need this here so the code can be tested. I.e. returns a meaningful status if needed."
    if ranges == None:
        ranges = project.molecule.ranges

    if validateFastest or validateCingOnly:
        doWhatif = False
        doProcheck = False
        doWattos = False
        doTalos = False
        doQueeny = False
        filterVasco = filterVasco
        if validateFastest:
            doShiftx = False
    if validateFastest or validateImageLess:
        htmlOnly = True

    t0 = tx = time.time()
#    nTdebug('Starting validate#validate with toFile True')
    if doShiftx and getDeepByKeysOrAttributes(plugins, SHIFTX_STR, IS_INSTALLED_STR):
        project.runShiftx(parseOnly=parseOnly)
#    tt = time.time()
#    nTmessage('Time for runShiftx %s' % (tt -tx))
#    tx = tt
    if getDeepByKeysOrAttributes(plugins, DSSP_STR, IS_INSTALLED_STR):
        project.runDssp(parseOnly=parseOnly)
#    tt = time.time()
#    nTmessage('Time for runDssp %s' % (tt -tx))
#    tx = tt
    if doWhatif and getDeepByKeysOrAttributes(plugins, WHATIF_STR, IS_INSTALLED_STR):
        project.runWhatif(ranges=ranges, parseOnly=parseOnly)
#    tt = time.time()
#    nTmessage('Time for runWhatif %s' % (tt -tx))
#    tx = tt
    if doProcheck and getDeepByKeysOrAttributes(plugins, PROCHECK_STR, IS_INSTALLED_STR):
        project.runProcheck(ranges=ranges, parseOnly=parseOnly)
#    tt = time.time()
#    nTmessage('Time for runProcheck %s' % (tt -tx))
#    tx = tt
    if doWattos and getDeepByKeysOrAttributes(plugins, WATTOS_STR, IS_INSTALLED_STR):
        project.runWattos(parseOnly=parseOnly)
#    tt = time.time()
#    nTmessage('Time for runWattos %s' % (tt -tx))
#    tx = tt
    if doQueeny:
        project.runQueeny()
#    tt = time.time()
#    nTmessage('Time for runQueeny %s' % (tt -tx))
#    tx = tt
    if doTalos and getDeepByKeysOrAttributes(plugins, TALOSPLUS_STR, IS_INSTALLED_STR):
        project.runTalosPlus(parseOnly=parseOnly)
#    tt = time.time()
#    nTmessage('Time for runTalosPlus %s' % (tt -tx))
#    tx = tt
    if doSuperpose:
        project.superpose(ranges=ranges)
#    tt = time.time()
#    nTmessage('Time for superpose %s' % (tt -tx))
#    tx = tt

    if filterVasco:
        if not getDeepByKeysOrAttributes(plugins, VASCO_STR, IS_INSTALLED_STR):
            nTdebug("Missing required plugin %s or not installed." % VASCO_STR)
            return True
        if project.molecule.hasVascoApplied():
            nTmessage("==> Keeping Vasco rereferencing done before.")
        else:
            if not project.runVasco():
                nTerror("Failed to filterVasco but will continue with validation.")
#            tt = time.time()
#            nTmessage('Time for runVasco %s' % (tt -tx))
#            tx = tt
            # end if
        # end if
    # end if
    if filterTopViolations:
        if not project.filterHighRestraintViol():
            nTerror("Failed to filterHighRestraintViol but will continue with validation.")
#        tt = time.time()
#        nTmessage('Time for filterHighRestraintViol %s' % (tt -tx))
#        tx = tt

    project.runCingChecks(toFile=True, ranges=ranges)
#    tt = time.time()
#    nTmessage('Time for runCingChecks %s' % (tt -tx))
#    tx = tt
    project.setupHtml()
    tt = time.time()
#    nTmessage('Time for setupHtml %s' % (tt -tx))
    tx = tt
    project.generateHtml(htmlOnly = htmlOnly)
    tt = time.time()
    nTmessage('Time for generateHtml %s' % (tt -tx))
    tx = tt
    project.renderHtml()
#    tt = time.time()
#    nTmessage('Time for renderHtml %s' % (tt -tx))
#    tx = tt
    tt = time.time()
#    nTmessage('Time for cing operations %s' % (tt -tx))
    nTmessage("Done overall validation, time was %s" % (tt -t0))


def criticizePeaks( project, toFile=True ):
    """
    Check's based upon peak's.
    Compare peak positions and assigned shifts
    """
    if not project.molecule:
        return
    #end if

    for atm in project.molecule.allAtoms():
        atm.peakPositions = NTlist()

    # criticize peak based on deviation of assigned value
    # make a list of all assigned peaks positions for each atom
    errorMargins = {'15N':0.15, '13C':0.15, '1H':0.01, '31P':0.15} # single sided
    for pl in project.peaks:

#        nTdebug('criticizePeaks %s', pl)

        pl.rogScore.reset()
        for peak in pl:
            peak.rogScore.reset()
            for i in range(peak.dimension):
                resonance = peak.resonances[i]
                if resonance and resonance.atom != None and resonance.value != NOSHIFT:
                    resonance.atom.peakPositions.append(peak.positions[i])
                    if not resonance.atom.isAssigned(resonanceListIdx=RESONANCE_LIST_IDX_ANY):
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
            nTdetail('==> Analyzing %s, output to: %s', pl, path)
        #end for
    #end if
#end def

def _criticizeChain( chain, valSets ):
    """
    Convenience method
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
#            nTdebug('Now criticizing %s, whatif key %s', residue, key )

            thresholdValuePoor = valSets[ 'WI_' + key + '_POOR'  ]
            thresholdValueBad = valSets[ 'WI_' + key + '_BAD' ]
            if (thresholdValuePoor == None) or (thresholdValueBad == None):
#                nTdebug("Skipping What If " + key + " critique")
                continue

            actualValue        = getDeepByKeys(residue, WHATIF_STR, key, VALUE_LIST_STR) #TODO remove this valueList stuff
            if actualValue == None:
                #print '>>', residue,key
                continue
            if isinstance(actualValue, NTlist):
                actualValue = actualValue.average()[0]

#           nTdebug('%s key %s: actual %s, thresholdPoor %s, thresholdBad %s', residue, key,
#                   actualValue, thresholdValuePoor, thresholdValueBad)

            actualValueStr = val2Str( actualValue, fmt='%8.3f', count=8 )
            if actualValue < thresholdValueBad: # assuming Z score
                comment = 'whatif %s value %s <%8.3f' % (key, actualValueStr, thresholdValueBad)
#                nTdebug(comment)
                residue.rogScore.setMaxColor( COLOR_RED, comment)
            elif actualValue < thresholdValuePoor:
                comment = 'whatif %s value %s <%8.3f' % (key, actualValueStr, thresholdValuePoor)
#                nTdebug(comment)
                residue.rogScore.setMaxColor( COLOR_ORANGE, comment)
            #endif
            residue.rogScore[key] = actualValue
        #end for
    #end if

    #Procheck
    if residue.has_key('procheck'):
        for key in ['gf']:
#            nTdebug('Now criticizing %s, procheck key %s', residue, key )

            thresholdValuePoor = valSets[ 'PC_' + key.upper() +'_POOR']
            thresholdValueBad = valSets[ 'PC_' + key.upper() +'_BAD']

            if (thresholdValuePoor == None) or (thresholdValueBad == None):
#                nTdebug("Skipping procheck g factor critique")
                continue

            actualValue        = getDeepByKeys(residue,'procheck', key )
            if actualValue == None:
                #print '>>', residue,key
                continue
            if isinstance(actualValue, NTlist):
                actualValue = actualValue.average()[0]

#            nTdebug('actual %s, thresholdPoor %s, thresholdBad %s',
#                    actualValue, thresholdValuePoor, thresholdValueBad)

            actualValueStr = val2Str( actualValue, fmt='%8.3f', count=8 )
            if actualValue < thresholdValueBad: # assuming Z score
                comment = 'Procheck %s value %s <%8.3f' % (key, actualValueStr, thresholdValueBad)
#                nTdebug(comment)
                residue.rogScore.setMaxColor( COLOR_RED, comment)
            elif actualValue < thresholdValuePoor:
                comment = 'Procheck %s value %s <%8.3f' % (key, actualValueStr, thresholdValuePoor)
#                nTdebug(comment)
                residue.rogScore.setMaxColor( COLOR_ORANGE, comment)
            #endif
            residue.rogScore[key] = actualValue
        #end for
    #end if

    #OMEGA refs from: Wilson et al. Who checks the checkers? Four validation tools applied to eight atomic resolution structures.
    #J Mol Biol (1998) vol. 276 pp. 417-436
    for key in ['OMEGA']:
        if residue.hasProperties('protein') and key in residue and residue[key]:
            d = residue[key] # NTlist object
            modelId = -1 # needs to be set even if enumerate doesn't assign it.
            vList = NTlist()
            for modelId,value in enumerate(d):
                v = violationAngle(value=value, lowerBound=TRANS_OMEGA_VALUE, upperBound=TRANS_OMEGA_VALUE)
                if v > 90.: # Check a cis
                    v = violationAngle(value=value, lowerBound=CIS_OMEGA_VALUE, upperBound=CIS_OMEGA_VALUE)
#                nTdebug('found residue %s model %d omega to violate from square trans/cis: %8.3f (omega: %8.3f)' % (
#                            residue, modelId, v, value) )
                vList.append(v)
            #end for
#            rmsViol = 0.0
            avViol = 0.0
            if modelId >= 0:
#                rmsViol = vList.rms()
                vList.average()
                avViol = vList.av

#            nTdebug('found rmsViol: %8.3f' % rmsViol )
#            actualValueStr = val2Str( rmsViol, fmt='%8.3f', count=8 )
            actualValueStr = val2Str( avViol, fmt='%8.3f', count=8 )
            # Calculate the Z-score (the number of times of the known sd.)
#            timesKnownSd = rmsViol / OMEGA_SD
            timesKnownSd = avViol / OMEGA_SD
            postFixStr = '(%s times known s.d. of %.1f degrees)' % (val2Str(timesKnownSd, fmt='%.1f'), OMEGA_SD)
            if (valSets.OMEGA_MAXALL_BAD != None) and (avViol >= valSets.OMEGA_MAXALL_BAD):
                comment = '%s value %s >%8.3f %s' % (key, actualValueStr, valSets.OMEGA_MAXALL_BAD, postFixStr)
                residue.rogScore.setMaxColor( COLOR_RED, comment )
#                nTdebug('Set to red')
            elif (valSets.OMEGA_MAXALL_POOR != None) and (avViol >= valSets.OMEGA_MAXALL_POOR):
                comment = '%s value %s >%8.3f %s' % (key, actualValueStr, valSets.OMEGA_MAXALL_POOR, postFixStr)
                residue.rogScore.setMaxColor(COLOR_ORANGE, comment)
#                nTdebug('Set to orange (perhaps)')
            residue.rogScore[key] = avViol
        #end if
    # end for

    if residue.has_key(CHK_STR) and residue.hasProperties('protein'):
#        print '>', residue, residue.rogScore
        for key in [RAMACHANDRAN_CHK_STR, CHI1CHI2_CHK_STR, D1D2_CHK_STR]: # TODO: disable those not needed.
#        for key in [D1D2_CHK_STR]: # TODO: disable those not needed.
#            nTdebug('Now criticizing %s, whatif key %s', residue, key )

            thresholdValuePoor = valSets[ key + '_POOR'  ]
            thresholdValueBad = valSets[ key + '_BAD' ]
            if (thresholdValuePoor == None) or (thresholdValueBad == None):
#                nTdebug("Skipping CING " + key + " critique")
                continue

            actualValue        = getDeepByKeys(residue, CHK_STR, key, VALUE_LIST_STR) #TODO remove this valueList stuff
            if actualValue == None:
#                nTdebug("None available for >> %s,%s" % ( residue,key))
                continue
            if isinstance(actualValue, NTlist):
                actualValue = actualValue.average()[0]

#            nTdebug('%s key %s: actual %s, thresholdPoor %s, thresholdBad %s', residue, key,
#                    actualValue, thresholdValuePoor, thresholdValueBad)

            actualValueStr = val2Str( actualValue, fmt='%8.3f', count=8 )
            if actualValue < thresholdValueBad: # assuming Z score
                comment = 'CING %s value %s <%8.3f' % (key, actualValueStr, thresholdValueBad)
#                nTdebug(comment)
                residue.rogScore.setMaxColor( COLOR_RED, comment)
            elif actualValue < thresholdValuePoor:
                comment = 'CING %s value %s <%8.3f' % (key, actualValueStr, thresholdValuePoor)
#                nTdebug(comment)
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
    """
    initialize

    GV: Criticize restraints, peaks etc first
    Restraint red ROGs get carried as orange to residue ROGs
    """

#    nTdebug("Now in validate.py#criticize")
    if project.decriticize():
        nTerror("Failed to project.decriticize in validate#criticize")
        return True
    # end if
    for drl in project.allRestraintLists():
        drl.criticize(project, toFile=toFile)
    # end for

    #Peaks
    criticizePeaks( project, toFile=toFile )

    # Assignments
    validateAssignments( project )

    if project.molecule:
        project.molecule.rogScore.reset()
        for color in [COLOR_GREEN,COLOR_ORANGE,COLOR_RED]:
            project.molecule[color].clear() # is a NTlist
        #end for

        for chain in project.molecule.allChains():
            _criticizeChain( chain, project.valSets )
            # also list the residues in molecule color lists
            for res in chain.allResidues():
#                _criticizeResidue( res, project.valSets ) # now done in _criticizeChain
                project.molecule[res.rogScore.colorLabel].append(res)
#                res.chain.rogScore.setMaxColor(res.rogScore.colorLabel, 'Inferred from residue ROG scores')
            #end for
        #end for

        useOldMethod = 0
        color = project.molecule.getRogColor()
        if useOldMethod:
            if len(project.molecule[COLOR_RED]) > 0:
                color = COLOR_RED
            elif len(project.molecule[COLOR_ORANGE]) > 0:
                color = COLOR_ORANGE
            # end if
        # end if
        if color == None:
            nTerror("Failed to determine the entry rog score color")
        else:
            # TODO: NB if the rog was more severe before it will not be reset here.
#            nTdebug("If worse, setting molecule rog color to: %s" % color)
            project.molecule.rogScore.setMaxColor(color, 'Inferred from residue ROG scores')
        # end if

        if toFile:
            path = project.moleculePath('analysis', 'ROG.txt')
            f = file(path,'w')
            for residue in project.molecule.allResidues():
                fprintf(f, '%-15s %4d %-6s  ', residue.cName(-1), residue.resNum, residue.rogScore.colorLabel)
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
            nTdetail('==> Criticizing project: output to "%s"', path)


            # Generate an xml summary file
            # When Whatif optional component isn't installed this fails. Disabled for now.
            path = project.moleculePath('analysis', 'cingSummaryDict.xml')
            s = project.getCingSummaryDict()
            s.save( path )
        else:
            nTdetail('==> Criticizing project')
        #end if
    #end if
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
        nTwarning(msgTmp)
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


def summaryForProject( project, toFile = True, ranges=None ):
    """
    Generate a summary string and store to text file by default.
    Return summary string or None on error.
    """

    #: For keeping track of which programs/checks were not run
    incompleteItems = []

    if not project.molecule:
        nTerror('Project.Summary: Strange, there was no molecule in this project')
        return None

    mol = project.molecule
    if ranges == None:
        ranges = mol.ranges
    nTdebug('validate#summaryForProject: ranges=%s type:%s', ranges, type(ranges) )

    msg = ''
#    msg += sprintf( '%s\n', mol.format() )

    skippedRmsd = False # keep logic simple.
    if mol.has_key( RMSD_STR ) and mol.rmsd:
        # Next msg isn't returning when no models are present in CING.
        msgNext = mol.rmsd.format(allowHtml=True)
        if msgNext:
            msg += msgNext
#        msg += sprintf( '\n%s\n', mol.rmsd.format() )
        if not mol.modelCount:
            # empty molecule can't have meaningfull rmsds and this might be an important factor to note here.
            skippedRmsd = True
    else:
        skippedRmsd = True
    if skippedRmsd:
        incompleteItems.append( RMSD_STR )

    for drl in project.distances + project.dihedrals + project.rdcs:
        msg += drl.format(allowHtml=True) + '\n'
#        msg += sprintf( '\n%s\n', drl.format() )
    allResidues = mol.allResidues()
    allResiduesWithCoord = mol.allResiduesWithCoordinates()
    rangesStrAll = mol.residueList2Ranges(allResidues)
    rangesStrAllWithCoord = mol.residueList2Ranges(allResiduesWithCoord)
#    nTdebug("rangesStrAll, rangesStrAllWithCoord: %s %s" % ( rangesStrAll, rangesStrAllWithCoord))
    msgRanges = "all residues"
    if rangesStrAll != rangesStrAllWithCoord:
        msgRanges += " with coordinates: " + rangesStrAllWithCoord
    msg += "\n%s CING ROG analysis (%s) %s\n%s\n" % (dots, msgRanges, dots, _ROGsummary(allResiduesWithCoord,allowHtml=True))

    useRanges = mol.useRanges(ranges)
    if useRanges:
        rangeResidueList = mol.ranges2list(ranges)
        rangeResidueListWithCoord = allResiduesWithCoord.intersection(rangeResidueList)
        rangesStrRangeWithCoord = mol.residueList2Ranges(rangeResidueListWithCoord)
#        nTdebug("rangesStrAll, rangesStrRangeWithCoord: %s %s" % ( rangesStrAll, rangesStrRangeWithCoord))
        msg += "\n%s CING ROG analysis (%s) %s\n%s\n" % \
               (dots, rangesStrRangeWithCoord, dots, _ROGsummary(rangeResidueListWithCoord, allowHtml=True))

    wiSummary = getDeepByKeys(mol, WHATIF_STR, 'summary')
    if wiSummary:
        msg += "\n%s WHAT IF Summary %s\n" % (dots, dots )
        msg += addPreTagLines(wiSummary)
    else:
        incompleteItems.append( WHATIF_STR )

    pc = getDeepByKeys(mol, PROCHECK_STR)
    if pc:
        if hasattr(pc, SUMMARY_STR):
            msg += "\n%s Procheck Summary %s\n" % (dots, dots )
            if mol.useRanges(pc.ranges):
                msg += '     (ranges %s)\n' % pc.ranges
            msg += '\n' + addPreTagLines(pc.summary.format())
        else:
            nTerror("Failed to find the procheck summary attribute")
    else:
        incompleteItems.append( PROCHECK_STR )

    # TODO: change this like shiftx setup with wattosStatus.
    wattosSummary = getDeepByKeys(mol, WATTOS_SUMMARY_STR)
    if wattosSummary:
        msg += "\n%s Wattos Summary %s\n" % (dots, dots )
        msg += '\n' + addPreTagLines(wattosSummary)
#    else:
#        incompleteItems.append( WATTOS_STR )

#    skippedShiftx = False
    # don't mark nucleic acid only entries at all.
    if mol.hasAminoAcid():
#        shiftx = getDeepByKeys(mol, SHIFTX_STR) # modded by GWV in revision 624.
        shiftx = project.shiftxStatus.completed
        if not shiftx:
#            nTmessage('runShiftx: not a single amino acid in the molecule so skipping this step.')
            incompleteItems.append( SHIFTX_STR )
    topMsg = sprintf( '%s CING SUMMARY project %s %s', dots, project.name, dots )

    # Block from storeCING2db keep synced.
    p_assignmentCountMap = project.molecule.getAssignmentCountMap()
    p_cs_count = p_assignmentCountMap.overallCount()
    p_peak_count = project.peaks.lenRecursive(max_depth = 1)
    p_distance_count = project.distances.lenRecursive(max_depth = 1)
    p_dihedral_count = 0
    for dihList in project.dihedrals:
        if dihList.isFromTalos():
            continue
        # end if
        p_dihedral_count += len(dihList)
    # end for
    p_rdc_count = project.rdcs.lenRecursive(max_depth = 1)
    hasExperimentalData = p_distance_count or p_dihedral_count or p_rdc_count or p_peak_count or p_cs_count
    bestMsg = '\nAll applicable programs/checks were performed.'
    if not hasExperimentalData:
        bestMsg = '\nBecause there were no experimental data, this project was not fully validated. %s' % (
                   '\nAll applicable programs/checks for the coordinate data were performed.' )
    else:
        if False: # DEFAULT: False
            debugMsg = """
                p_distance_count =  %(p_distance_count)5d
                p_dihedral_count =  %(p_dihedral_count)5d
                p_rdc_count      =  %(p_rdc_count)5d
                p_peak_count     =  %(p_peak_count)5d
                p_cs_count       =  %(p_cs_count)5d
            """ % dict(
                           p_distance_count= p_distance_count,
                           p_dihedral_count= p_dihedral_count,
                           p_rdc_count     = p_rdc_count,
                           p_peak_count    = p_peak_count,
                           p_cs_count      = p_cs_count
                        )
            nTdebug(debugMsg)
        # end if
    # end if
    if not incompleteItems:
        topMsg += bestMsg
#    for checkId in incompleteItems:
    else:
        topMsg += '\nWARNING: Some programs or checks were not performed: %s' % incompleteItems
#        topMsg += '\n<font color=orange>WARNING:</font> This may affect the CING ROG scoring.'
        topMsg += '\nThis may affect the CING ROG scoring.'
        if not hasExperimentalData:
            topMsg += '\nBecause there were no experimental data, this project was also not fully validated.'
        # end if
    # end if
    msg = topMsg + '\n' + msg

    if toFile:
        fname = project.path(mol.name, validationDirectories.analysis,'summary.txt')
        fp = open( fname, 'w' )
        nTmessage( '==> summary, output to %s', fname)
#        nTdebug(" msg: " + msg)
        msgClean = removePreTagLines( msg )
#        nTdebug(" msgClean: " + msgClean)
        fprintf( fp, msgClean )
        fp.close()
    #end if

    return msg
#end def

def partitionRestraints( project ):
    """
    Partition the restraints and generate per-residue lists
    """
#    nTdebug('partionRestraints of project %s', project)

    if not project.molecule:
        return

    # distances and dihedrals
    for res in project.molecule.allResidues():
        res.distanceRestraints = RestraintList('distanceRestraints')
        res.dihedralRestraints = RestraintList('dihedralRestraints')
        res.rdcRestraints      = RestraintList('rdcRestraints')
    #end for

    for drl in project.distances:
        for restraint in drl:
            for atm1,atm2 in restraint.atomPairs:
                if not (atm1 and atm2): # Not observed yet.
                    nTerror("Found distance restraint without atom1 or 2. For restraint: %s" % restraint)
                    continue
                #print '>>', atm1, atm2
                atm1.residue.distanceRestraints.add( restraint ) #AWSS
                atm2.residue.distanceRestraints.add( restraint ) #AWSS
            #end for
        #end for
    #end for

    # dihedrals
    for drl in project.dihedrals:
        for restraint in drl:
            atom = restraint.atoms[2]
            if not atom:
                # Failed for entry 8psh but in fact this shouldn't occur because the atoms should not exist then.
                #NB this only happens after restoring.
                nTerror("Found restraint without an atom at index 2. For restraint: %s" % restraint)
                continue
            residue = atom.residue
            if not residue:
                nTerror("Found restraint with an atom without residue. For restraint: %s" % restraint)
                continue
            residue.dihedralRestraints.add( restraint ) #AWSS and JFD will copy this logic to html class.
        #end for
    #end for

    #RDCs
    for drl in project.rdcs:
        for restraint in drl:
            for atm1,atm2 in restraint.atomPairs:
                if not (atm1 and atm2): # Not observed yet.
                    nTerror("Found rdc restraint without atom1 or 2. For restraint: %s" % restraint)
                    continue
                atm1.residue.rdcRestraints.add( restraint ) #AWSS
                if atm2.residue != atm1.residue:
                    atm2.residue.rdcRestraints.add( restraint ) #AWSS
            #end for
        #end for
    #end for
#end def


def validateRestraints( project, toFile = True):
    """
    Calculate rmsd's and violation on restraints
    """

#    fps = []
#    fps.append( sys.stdout )

    if not project.molecule:
        return

    msg = ""
    msg += sprintf('%s\n', project.format() )

#    # distances and dihedrals
#    for res in project.molecule.allResidues():
#        res.distanceRestraints = RestraintList()
#        res.dihedralRestraints = RestraintList()
#    #end for

    # distances
    rL = project.distanceRestraintNTlist = RestraintList('distanceRestraintNTlist') # used for DB as a list of all restraints combined.
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
#        nTdebug("Found list: " + repr(theList))
        msg += sprintf( '%s\n', formatList( theList ) )
        rL.addList(drl)
    #end for
    getStatsRestraintNTlist(rL)

    # dihedrals
    rL = project.dihedralRestraintNTlist = RestraintList('dihedralRestraintNTlist')
    for drl in project.dihedrals:
#        drl.analyze()
        msg += sprintf( '%s\n', drl.format())
        drl.sort('violMax').reverse()
        msg += sprintf( '%s Sorted on Maximum Violations %s\n', dots, dots)
        msg += sprintf( '%s\n', formatList( drl[0:min(len(drl),30)] ) )

        drl.sort('violCount3').reverse()
        msg += sprintf( '%s Sorted on Violations > 3 degree %s\n', dots, dots)
        msg += sprintf( '%s\n', formatList( drl[0:min(len(drl),30)] ) )
        rL.addList(drl)
    #end for
    getStatsRestraintNTlist(rL)

    # Process the per residue restraints data
    msg += sprintf( '%s Per residue scores %s\n', dots, dots )
    for restraintListAtribute in ( 'distanceRestraints', 'dihedralRestraints'):
        count = 0
        for res in project.molecule.allResidues():
            rL = res[ restraintListAtribute ]
            getStatsRestraintNTlist(rL)

            # print every 10 lines
            if not count % 30:
                msg += sprintf('%-18s %15s  %15s   %s\n', '--- RESIDUE ---', '--- PHI ---', '--- PSI ---',
                               '-- dist 0.1A 0.3A 0.5A   rmsd   violAv violMaxAll --')
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
                msg += sprintf( '%-18s %-15s  %-15s      %3d %4d %4d %4d  %6.3f %6.3f %6.3f\n',
                     res, phi, psi,
                         len(rL),
                         rL.violCount1,
                         rL.violCount3,
                         rL.violCount5,
                         rL.rmsd,
                         rL.violAv,
                         rL.violMaxAll
                       )
            except:
    #                nTdebug("Still giving misfits here in validateRestraints?") # yes
                pass
            count += 1
        #end for
    #end for
#    nTdebug(msg)
    if toFile:
        #project.mkdir(project.directories.analysis, project.molecule.name)
        fname = project.path(project.molecule.name, validationDirectories.analysis,'restraints.txt')
        fp = open( fname, 'w' )
        nTmessage( '==> validateRestraints, output to %s', fname)
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

#    nTdebug("Starting checkForSaltbridges with toFile:%s" % toFile)
    if not project.molecule:
        nTerror('checkForSaltbridges: no molecule defined')
        return None
    #end if

    result = NTlist()

    if project.molecule.modelCount == 0:
        nTwarning('checkForSaltbridges: no models for "%s"', project.molecule)
        return result
    #end if

    if toFile: # This output could easily be cached before write at once.
        #project.mkdir(project.directories.analysis, project.molecule.name)
        fname = project.path(project.molecule.name, validationDirectories.analysis,'saltbridges.txt')
        fp = open( fname, 'w' )
        nTmessage( '==> checkSaltbridges, output to %s', fname)
    else:
        fp = None
#        nTdebug( '==> checkSaltbridges, no output requested')
    #end if

    if toFile:
        fprintf( fp, '%s\n', project.molecule.format() )
#    nTmessage(     '%s', project.molecule.format() )

    residues1 = project.molecule.residuesWithProperties('E') + \
                project.molecule.residuesWithProperties('D')

    residues2 = project.molecule.residuesWithProperties('R') + \
                project.molecule.residuesWithProperties('K') + \
                project.molecule.residuesWithProperties('H')

#    nTdebug("residues1 count: %s" % (len(residues1)))
#    nTdebug("residues2 count: %s" % (len(residues2)))
    # initialize
    for res in project.molecule.allResidues():
        res.saltbridges = NTlist()
    #end for

    pairCountDistant = 0
    pairCountSkipped = 0
    pairCountBelowCutoff = 0
    s = None
    for res1 in residues1:
        for res2 in residues2:
#            nTdebug('>> %s %s' % ( res1, res2 ))

            # Quick optimalization based on distances
            # Arg CA to NH1 maxes out at 7.3 so let's take 8 twice plus max distance of a valid saltbridge4 Ang.
            residuePairDistance = res1.getMinDistanceCalpha( res2 )
            if residuePairDistance > CUTOFF_SALTBRIDGE_BY_Calpha:
#                nTdebug("Ignoring distant pair: %s %s - %s" % ( residuePairDistance, res1, res2 ))
                pairCountDistant += 1
                continue

            s = validateSaltbridge(res1,res2)
            if not (s and s.result): # no s.result for entry 1f96 issue 197
                pairCountSkipped += 1
                continue
            if float(s.types[4][1])/float(len(s.result)) > cutoff:    # fraction 'not observed' > then cutoff (default 0.5), skip
                pairCountBelowCutoff += 1
                continue
            if toFile:
                fprintf(fp, '%s\n', s.format() )
#            nTdebug(    '%s\n', s.format() )
            res1.saltbridges.append( s )
            res2.saltbridges.append( s )
            result.append( s )
        #end for
    #end for
    lresult = len(result)
    lresidues1 = len(residues1)
    lresidues2 = len(residues2)
    pairCountConsidered = lresidues1*lresidues2
    msg = "==> CheckForSaltbridges distant: %s skipped: %s below cutoff %s present %s total considered %s" % (
        pairCountDistant, pairCountSkipped, pairCountBelowCutoff, lresult, pairCountConsidered )
    sumPairs = pairCountDistant + pairCountSkipped + pairCountBelowCutoff + lresult
    if sumPairs != pairCountConsidered:
        nTcodeerror("Failed sum check in checkForSaltbridges")
    nTmessage(msg)
    if s and toFile:
        fprintf( fp, '%s\n', msg )
        fprintf( fp, '%s\n', s.comment )
        #nTdebug(     '%s\n', s.comment )
    #end if

    if toFile:
        fp.close()
#    sys.stdout.flush()
    #end if
#    nTdebug("Ending checkForSaltbridges")

    return result
#end def

def validateSaltbridge( residue1, residue2 ):
    """
    ValidateSaltbridge( residue1, residue2 )

    Validate presence of saltbridge, CC-Bridge, NO-bridge, or ion-pair between residue1 and residue2
    Ref: Kumar, S. and Nussinov, R. Biophys. J. 83, 1595-1612 (2002)

    residue1, residue2: Residue instances of type E,D,H,K,R

    Arbitrarily set the criteria for ion-pair r,theta to be within 2 sd of average,
    else set sb_type to none.

    Returns sb_summary NTdict or None on error.


    """
#    nTdebug('validateSaltBridge: %s %s', residue1, residue2)

    # Definitions of the centroids according to the paper
    # TODO: fix problem as in 1bzb most likely due to uncommon residues within getting recognized as regular ones.
    # Recode to use fullnames including variants.(Store in Database?)

    if residue1 == None:
        nTerror('validateSaltbridge: undefined residue1')
        return None
    #end if
    if residue2 == None:
        nTerror('validateSaltbridge: undefined residue2')
        return None
    #end if

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

    modelCount = residue1.chain.molecule.modelCount
    if modelCount == 0:
        nTerror('validateSaltbridge: no structure models')
        return None
    #end if

    if residue1.db.shortName not in ['E','D','H','K','R']:
        nTwarning('validateSaltbridge: invalid residue %s, should be E,D,H,K, or R', residue1)
        return None
    #end if


    if residue2.db.shortName not in ['E','D','H','K','R']:
        nTwarning('validateSaltbridge: invalid residue %s, should be E,D,H,K, or R', residue2)
        return None
    #end if

    # Check if all atoms are present
    for residue in [residue1, residue2]:
        for atmName in centroids[residue.db.shortName]:
            atm = None
            try: # Fails for entry 1bzb which has a NH2 residue capping the C-terminus.
                atm = residue[atmName]
            except:
                nTerror("Failed to get atom for atom name [%s] in residue [%s]" % (atmName, residue))
                return None
            if len(atm.coordinates) == 0:
                # Happens for all residues without coordinates. E.g. 1brv 159-170
#                nTerror('validateSaltbridge: no coordinates for atom %s', atm)
                return None
            #end if
        #end for
    #end for

    # get the vectors c1, c1a, c2, c2a for each model and compute the result
    result  = NTlist()
    sb_summary = NTdict(
        residue1 = residue1,
        residue2 = residue2,
        comment  = """
Ref: Kumar, S. and Nussinov, R. Biophys. J. 83, 1595-1612 (2002)
Arbitrarily set the criteria for ion-pair (r,theta) to be within
2 sd ~ 2*(1.2A,39) of average (7.6A,118), else set sb_type to 'not observed'.
""",
        __FORMAT__ = '------------------ Saltbridge ------------------\n' +\
                     'residues:          %(residue1)s %(residue2)s\n' +\
                     'r (av,sd,min,max): (%(rAv).1f, %(rSd).1f, %(min).1f, %(max).1f)\n' +\
                     'theta (av,sd):     (%(thetaAv).1f, %(thetaSd).1f)\n' +\
                     'types:             %(types)s'
    )
    types = ['saltbridge','C-C bridge','N-O bridge','ion pair','not observed']
    counts = nTfill(0,5)

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
            sb_type = 0
        elif criterium1 and not criterium2:
            sb_type = 1
        elif not criterium1 and criterium2:
            sb_type = 2
        elif not criterium1 and not criterium2 and rl < 7.6+2.1*2 and 118-39*2< theta and theta < 118+39*2:
            sb_type = 3
        else:
            sb_type = 4

        counts[sb_type] += 1

        data = NTdict(
            residue1   = residue1,
            residue2   = residue2,
            model      = model,
            r          = rl,
            theta      = theta,
            criterium1 = criterium1,
            criterium2 = criterium2,
            sb_type       = types[sb_type],

            __FORMAT__ = '--- saltbridge analysis %(residue1)s-%(residue2)s ---\n' +\
                         'model: %(model)d\n' +\
                         'type:  %(sb_type)s\n' +\
                         'r (A): %(r).1f\n' +\
                         'theta: %(theta).1f\n' +\
                         'criteria: %(criterium1)s, %(criterium2)s\n'
        )
        result.append(data)
    #end for over models

    sb_summary.result = result
    r_resultNTList = result.zap('r') # cache for speed
    sb_summary.rAv, sb_summary.rSd, sb_summary.modelCount = r_resultNTList.average()
    if r_resultNTList:
        sb_summary.min   = min( r_resultNTList )
        sb_summary.max   = max( r_resultNTList )
    else:
        sb_summary.min   = NaN
        sb_summary.max   = NaN

    sb_summary.thetaAv, sb_summary.thetaSd, _n = result.zap('theta').average()
    sb_summary.types = zip( types,counts)
    if not sb_summary.rSd:
        sb_summary.rSd = -999.9 # wait until we have a standard approach for dealing with Nans. TODO:
    if not sb_summary.thetaSd:
        sb_summary.thetaSd = -999.9 # wait until we have a standard approach for dealing with Nans. TODO:
    return sb_summary
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
        nTerror('checkHbond: non-proton donor %s\n', donorH )
        return None
    #end if

    if not acceptor:
        nTerror('checkHbond: undefined acceptor %s\n', donorH )
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
    if len(distances) > 0:
        result.distance, result.distanceSD, _n = distances.average()
    if len(angles) > 0:
        result.angle, result.angleCV, _n = angles.cAverage()
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
                if heavy and heavy.isAssigned(resonanceListIdx=RESONANCE_LIST_IDX_ANY) and not heavy.isStereoAssigned():
                    heavy.stereoAssigned = True
                    nTmessage('==> fixed stereo assignment %s', heavy)
                #end if

            # check stereo methyl carbon
            elif atm.isMethyl() and atm.isCarbon():
                pseudo = atm.attachedProtons(includePseudo=True).last()
                if pseudo and pseudo.isAssigned(resonanceListIdx=RESONANCE_LIST_IDX_ANY) and not pseudo.isStereoAssigned():
                    pseudo.stereoAssigned = True
                    nTmessage('==> fixed stereo assignment %s', pseudo)
                #end if
            #end if
            partner = atm.proChiralPartner()
            if partner and partner.isAssigned(resonanceListIdx=RESONANCE_LIST_IDX_ANY) and not partner.isStereoAssigned():
                partner.stereoAssigned = True
                nTmessage('==> fixed stereo assignment %s', partner)
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
FRACTION_REQUIRED = 0.85 # was 0.75 but let's only report real exceptions.

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
#    nTdebug("Starting moleculeValidateAssignments")
    func_name = getCallerName()
    result   = NTlist()
#    if molecule.resonanceCount == 0:
#        nTdebug("Molecule.validateAssignments: No resonance assignments read so no real validation on it can be done. Let's try anyway.")
#        pass
#        return result

    # Keep track of what assignments are done and don't complain about specific ones missing
    # if there are none at all assigned of that type.
    # Just initialize the ones that are checked below; not 1H or P etc.; GV added 1H anyway
    assignmentCountMap = molecule.getAssignmentCountMap()
    notAssignmentCountMap = molecule.getAssignmentCountMap(isAssigned=False)
    hasAssignment = {}
    msg = ''
    if not assignmentCountMap:
        nTerror("Failed in %s to get even an empty assignmentCountMap; skipping" % func_name)
        return None

    keyList = assignmentCountMap.keys()
    at = 0
#    nt = 0
    tt = 0
    for key in keyList:
        a = assignmentCountMap[key]
        n = notAssignmentCountMap[key]
        t = a + n
        at += a
        tt += t
        if not t:
            continue
        f = (1. * a) / t
        hasAssignment[key] = f > FRACTION_REQUIRED
#        nTdebug("key, a, n, t, f, hasAssignment: %s" % str([key, a, n, t, f, hasAssignment]))
        msg += '   %s %s/%s/%.2f' % ( key, a, t, f)
    # end for
    ft = 0.
    if tt:
        ft = (1. * at) / tt
    msg += '   %s %s/%s/%.2f' % ( 'combined', at, tt, ft)
    nTmessage("==> Found assigned/overall/fraction for spins: " + msg)
#    nTdebug("==> Only spins with fraction >= %.2f will be flagged when missing: %s" % ( FRACTION_REQUIRED, str(hasAssignment)))

    for atm in molecule.allAtoms():
        atm.rogScore.reset()
        atm.validateAssignment = NTlist()

    for res in molecule.allResidues():
#        Routine below needs to be called after  atm.validateAssignment is initialized.
        if res.hasProperties('PRO') or res.hasProperties('cPRO'):
            if res.validateChemicalShiftProPeptide(result):
                nTerror("Failed to _validateChemicalShiftProPeptide for %s" % res)
        if res.hasProperties('LEU'):
            if res.validateChemicalShiftLeu(result):
                nTerror("Failed to validateChemicalShiftLeu for %s" % res)

        for atm in res.allAtoms():
            if atm.isAssigned(resonanceListIdx=RESONANCE_LIST_IDX_ANY):
#                nTdebug('Assigned atom: %s' % atm)
                shift = atm.shift(resonanceListIdx=RESONANCE_LIST_IDX_ANY)
                pseudo = atm.pseudoAtom()

                # Check the shift against the database
                if atm.db.shift:
                    av = atm.db.shift.average
                    sd = atm.db.shift.sd
                elif pseudo and pseudo.db.shift:
                    av = pseudo.db.shift.average
                    sd = pseudo.db.shift.sd
                else:
#                    nTdebug("%s: '%s' not in in DB SHIFTS", func_name, atm)
                    av = None
                    sd = None
                #end if

                if av != None and sd:
                    delta = math.fabs((shift - av) / sd)
                    if sd < 0.0:
                        nTerror("Found negative sd. Skipping critiqueing.")
                        continue
                    msg = sprintf('%.1f*sd from (%.2f,%.2f)', delta, av, sd )
#                    debug_msg = sprintf('    shift %.2f, ' % shift)
#                    nTdebug(debug_msg)
                    if delta > 3.0:
                        result.append( atm )
                        atm.validateAssignment.append(msg)
#                        nTdebug("Found situation 2: " + msg)
                    else:
                        pass
#                        nTdebug("Found situation 3: " + msg)
                    #end if
                #end if

                # Check if not both realAtom and pseudoAtom are assigned
                if atm.hasPseudoAtom() and atm.pseudoAtom().isAssigned(resonanceListIdx=RESONANCE_LIST_IDX_ANY):
                    msg = sprintf('%s: and %s', MULTIPLE_ASSIGNMENT, atm.pseudoAtom() )
    #                nTmessage('%-20s %s', atm, msg)
                    result.append( atm )
                    atm.validateAssignment.append(msg)
                #end if

                # Check if not pseudoAtom and realAtom are assigned
                if atm.isPseudoAtom():
                    for a in atm.realAtoms():
                        if a.isAssigned(resonanceListIdx=RESONANCE_LIST_IDX_ANY):
                            msg = sprintf('%s: and %s', MULTIPLE_ASSIGNMENT, a )
    #                        nTmessage('%-20s %s', atm, msg)
                            result.append( atm )
                            atm.validateAssignment.append(msg)
                        #end if
                    #end for
                #end if

                # Check if all realAtoms are assigned in case there is a pseudo atom
                if atm.hasPseudoAtom():
                    for a in atm.pseudoAtom().realAtoms():
                        if a.isMethylProtonButNotPseudo():
                            continue
                        if not a.isAssigned(resonanceListIdx=RESONANCE_LIST_IDX_ANY):
                            msg = sprintf('%s: expected %s', MISSING_ASSIGNMENT, a )
    #                        nTmessage('%-20s %s', atm, msg )
                            result.append( atm )
                            atm.validateAssignment.append(msg)
                        #end if
                    #end for
                #end if

                # Check for protons with unassigned heavy atoms
                if atm.isProton() and not atm.isPseudoAtom():
                    heavyAtm = atm.heavyAtom()
                    if heavyAtm == None: # Happens for all non-standard residues protons.
                        nTwarning("Failed to get heavy for atm: %s" % atm)
                    # end if
                    elif not heavyAtm.isAssigned(resonanceListIdx=RESONANCE_LIST_IDX_ANY):
                        spinType = getDeepByKeys(heavyAtm, 'db', 'spinType')
                        if spinType:
                            # Only complain if type has at least one assignment.
                            if getDeepByKeys( hasAssignment, spinType):
                                msg = sprintf('%s: %s', EXPECTED_ASSIGNMENT, heavyAtm )
            #                    nTmessage('%-20s %s', atm, msg )
                                result.append( atm )
                                atm.validateAssignment.append(msg)
                    #end if
                #end if atm.isProton()

                # stereo assignments checks
                if atm.isStereoAssigned():
                    if not atm.isProChiral():
                        msg = sprintf('%s: %s', INVALID_STEREO_ASSIGNMENT, atm )
                        result.append( atm )
                        atm.validateAssignment.append(msg)
                    else:
                        # Check prochiral partner assignments
                        partner = atm.proChiralPartner()
                        if partner:
                            if not partner.isAssigned(resonanceListIdx=RESONANCE_LIST_IDX_ANY):
                                msg = sprintf('%s: %s unassigned', INVALID_STEREO_ASSIGNMENT, partner )
                                result.append( atm )
                                atm.validateAssignment.append(msg)
                            else:
                                if not partner.isStereoAssigned():
                                    msg = sprintf('%s: %s not stereo assigned', INVALID_STEREO_ASSIGNMENT, partner )
                                    result.append( atm )
                                    atm.validateAssignment.append(msg)
                                #end if
                            #end if
                        #end if
                    #end if
                #end if

                # check stereo methyl protons
                if atm.isMethylProton():
                    heavy = atm.heavyAtom()
                    if atm.name.endswith('1'): # JFD: don't do both.
                        if heavy and heavy.isAssigned():
                            if atm.isStereoAssigned() and not heavy.isStereoAssigned():
                                msg = sprintf('%s: %s not stereo assigned', INVALID_STEREO_ASSIGNMENT, heavy )
                                result.append( atm )
                                atm.validateAssignment.append(msg)
                            #end if
                            if not atm.isStereoAssigned() and heavy.isStereoAssigned():
                                msg = sprintf('%s: %s is stereo assigned', INVALID_STEREO_ASSIGNMENT, heavy )
                                result.append( atm )
                                atm.validateAssignment.append(msg)
                            #end if
                        #end if
                    #end if
                #end if

                if False: # JFD removed this message to avoid cluttering reports
                    # check stereo methyl carbon
                    if atm.isMethyl() and atm.isCarbon():
                        pseudo = atm.attachedProtons(includePseudo=True).last()
                        if pseudo and pseudo.isAssigned(resonanceListIdx=RESONANCE_LIST_IDX_ANY):
                            if atm.isStereoAssigned() and not pseudo.isStereoAssigned():
                                msg = sprintf('%s: %s not stereo assigned', INVALID_STEREO_ASSIGNMENT, pseudo )
                                result.append( atm )
                                atm.validateAssignment.append(msg)
                            #end if
                            if not atm.isStereoAssigned() and pseudo.isStereoAssigned():
                                msg = sprintf('%s: %s is stereo assigned', INVALID_STEREO_ASSIGNMENT, pseudo )
                                result.append( atm )
                                atm.validateAssignment.append(msg)
                            #end if
                        #end if
                    #end if
                #end if

            else:
#                nTdebug('Unassigned atom: %s' % atm)
                # Atm is not assigned but stereo assignment is set
                if atm.isStereoAssigned():
                    msg = sprintf('%s: not assigned but stereo-assignment %s set', INVALID_STEREO_ASSIGNMENT, atm )
                    result.append( atm )
                    atm.validateAssignment.append(msg)
                #end if

                if atm.isProChiral():
                    partner = atm.proChiralPartner()
                    if partner and partner.isAssigned(resonanceListIdx=RESONANCE_LIST_IDX_ANY) and partner.isStereoAssigned():
                        msg = sprintf('%s: prochiral partner %s is stereo assigned', INVALID_STEREO_ASSIGNMENT, partner )
                        result.append( atm )
                        atm.validateAssignment.append(msg)
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

#    nTdebug("Starting validateAssignments")
    if not project.molecule:
#        nTdebug('validateAssignments: no molecule defined')
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
                dihRestraint.angle = 'Discarded'
                atom = dihRestraint.atoms[2]
                if not atom:
                    nTerror("In restoreDihRestraintInfo failed to find atom for restraint: %s" % dihRestraint)
                    dihRestraint.residue = None
                    continue
                dihRestraint.residue = atom.residue #'Invalid'

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

            cav, _cv, _n = d.cAverage(minValue=plotpars.min, maxValue=plotpars.max)
            nTlimit( d, cav-180.0, cav+180.0 )

            goodAndOutliers = peirceTest( d )
            if not goodAndOutliers:
                nTcodeerror("in validateDihedrals: error from peirceTest")
                return True
            d.good, d.outliers = goodAndOutliers

            d.limit(          plotpars.min, plotpars.max )
            d.cAverage(       plotpars.min, plotpars.max )
            d.good.limit(     plotpars.min, plotpars.max, byItem=1 )
            d.good.cAverage(  plotpars.min, plotpars.max, byItem=1 )
            d.outliers.limit( plotpars.min, plotpars.max, byItem=1 )
            if False:
                nTmessage( '--- Residue %s, %s ---', res, dihed )
                nTmessage( 'good:     %2d %6.1f %4.3f',
                           d.good.n, d.good.cav, d.good.cv )
                nTmessage( 'outliers: %2d models: %s',
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
#            msgHol.appendDebug("Failed to getDsspSecStructConsensus from validateDihedralCombinations for residue; skipping: %s" % (
#                residue))
            continue
        # The assumption is that the derived residues can be represented by the regular.
        resName = getDeepByKeysOrDefault(residue, residue.resName, 'nameDict', PDB)
        if len( resName ) > 3: # The above line doesn't work. Manual correction works 95% of the time.
            resName = resName[:3]  # .pdb files have a max of 3 chars in their residue name.
        for checkIdx in range(len(plotDihedral2dLoL)):
#        for checkIdx in [2]:
            checkId = plotDihedral2dLoL[checkIdx][0]
#            nTdebug('Looking at %s %s' % (residue, checkId) )
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
#                    nTdebug( 'Skipping residue without triplet %s' % residue)
                    continue
                # Note that this was a major bug before June 3, 2010.
#                resTypeList = [getDeepByKeys(triplet[i].db.nameDict, IUPAC) for i in tripletIdxList]
                resTypeList = [getDeepByKeys(triplet[i].db.nameDict, IUPAC) for i in range(3)]
            else:
                nTcodeerror("validateDihedralCombinations called for non Rama/Janin/d1d2")
                return None

            if doingNewD1D2plot:
                # depending on doOnlyOverall it will actually return an array of myHist.
                myHistList = residue.getTripletHistogramList( doOnlyOverall = False, ssTypeRequested = ssType, doNormalize=doNormalize  )
                if myHistList == None:
#                    nTdebug("Failed to get the D1D2 hist for %s; skipping. Perhaps a non-protein residue was a neighbor?" % residue)
                    continue
                if len(myHistList) != 3:
                    nTdebug("Expected exactly one but found %s histogram for %s with ssType %s; skipping" % (
                        len(myHistList),residue, ssType))
                    continue
#                myHist = myHistList[0]
            else:
                myHist = getDeepByKeysOrAttributes(histBySsAndResType,ssType,resName)
                if myHist == None:
#                    nTdebug("No hist for ssType %s and resName %s of residue %s" % (ssType,resName,residue))
                    continue
                myHistList = [ myHist ]

            d1 = getDeepByKeysOrAttributes(residue, dihedralName1)
            d2 = getDeepByKeysOrAttributes(residue, dihedralName2)

            if not (d1 and d2):
#                nTdebug( 'in validateDihedralCombinations dihedrals not found for residue: %s and checkId %s; skipping' % (
                    #residue, checkId ))
                continue

            if not (len(d1) and len(d2)):
#                nTdebug( 'in validateDihedralCombinations dihedrals had no defining atoms for 1: %s or', dihedralName1 )
#                nTdebug( 'in validateDihedralCombinations dihedrals had no defining atoms for 2: %s; skipping'   , dihedralName2 )
                continue

            pointList = zip( d1, d2 ) # x,y tuple list NOT REALLY NEEDED JUST CHECKING COUNTS
            modelCountNew = len(pointList)
            if modelCountNew != modelCount:
                nTwarning("Will use %d models instead of %d expected" %(modelCountNew, modelCount))
            if not resTypeList:
                resTypeList = [ resName ]

            zkList = []
            for i, myHist in enumerate(myHistList):
                if doingNewD1D2plot:
                    ssType = ssIdxToType(i)
                keyList = [ ssType ]
                keyList += resTypeList
#                nTdebug("Checking with keyList [%s]" % str(keyList))
                if normalizeBeforeCombining: # can't use predefined ones. Of course the debug checking below makes no sense with this.
                    cTuple = getEnsembleAverageAndSigmaHis( myHist )
    #                cTuple = getArithmeticAverageAndSigmaFromHistogram( myHist ) # TODO: discuss with GWV.
                    (c_av, c_sd, hisMin, hisMax) = cTuple #@UnusedVariable
                else:
                    cTuple = getDeepByKeysOrAttributes( histCtupleBySsAndResType, *keyList)
        #            nTdebug("keyList: %s" % str(keyList))
                    if not cTuple:
                        nTwarning("Failed to get cTuple for residue %s with keyList %s; skipping" % (residue, keyList))
                        continue
                    (c_av, c_sd, hisMin, hisMax, keyListStr) = cTuple
                    keyListQueryStr = str(keyList)
                    if keyListStr != keyListQueryStr:
                        nTerror("Got keyListStr != keyListQueryStr: %s and %s" % (keyListStr, keyListQueryStr))
                        continue

                if myHist == None:
                    nTerror("Got None for hist for %s" % residue)
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
                    ck = getValueFromHistogram( myHistP, a2, a1, bins)
                    zk = ( ck - c_av ) / c_sd
                    zkList.append(zk)
#                    if modelIdx == 0: # costly checks to be disabled later.
                    if False:
    #                if checkIdx == 2: # costly checks to be disabled later.
    #                if cing.verbosity >= cing.verbosityDebug: # costly checks to be disabled later.
                        msg = ("chk %d ssType %4s res %20s mdl %2d a2 %8.2f a1 %8.2f " +
                               "c_av %12.3f c_sd %12.3f ck %12.3f zk %8.2f h- %12.3f h+ %12.3f z- %8.2f z+ %8.2f") % (
                                    checkIdx,
                                    ssType,residue,modelIdx,a2, a1,
                                    c_av, c_sd,ck,zk,
                                    minHist, maxHist, zMin, zMax)
                        if maxHist < c_av:
                            nTerror(msg + " maxHist < c_av")
                        elif maxHist < ck:
                            nTerror(msg + " maxHist < ck")
                        elif minHist > 1000.: # was found in GLY ASN LEU
                            nTwarning(msg + " minHist > 1000") # ' ' GLY GLY GLY
                        elif hisMin != minHist:
                            nTerror(msg + " hisMin != minHist: %8.0f %8.0f" % (hisMin, minHist))
                        elif hisMax != maxHist:
                            nTerror(msg + " hisMax != maxHist: %8.0f %8.0f" % (hisMax, maxHist))
                        else:
                            if doingNewD1D2plot:
                                nTdebug(msg)
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
#                    if modelIdx == 0:
                    if False:
                        nTdebug("For modelIdx %s found: %s and selected max: %s" % (modelIdx, str(ensembleValueLoL[modelIdx]),
                                                                                    ensembleValueList[modelIdx] ))
        # end for checkIdx
    # end for residue
    msgHol.showMessage(max_messages=10, max_debugs = 10)
#end def



def validateModels( self)   :
    """Validate the models on the basis of the dihedral outliers
    """

    if not self.molecule:
        nTerror("validateModels: no molecule defined")
        return True
    if not self.molecule.modelCount:
        nTwarning("validateModels: no model for molecule %s defined", self.molecule)
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
#        nTdebug('Model %2d: %2d backbone dihedral outliers', m, count )
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

def zscaleHist( hist2d, cAv, cSd ):
    'Histogram will be subtracted by cAv and divided by cSd'
    hist2d -= cAv
    hist2d /= cSd
    return hist2d

def getValueFromHistogram( hist, v0, v1, bins=None):
    """Returns the value from the bin pointed to by v0,v1.
        think
    v0 row    y-axis
    v1 col    x-axis
    """
    tx = ogrid[ v0:v0:1j, v1:v1:1j ]
    interpolatedValueArray = interpn_linear( hist, tx, bins )
    interpolatedValue = interpolatedValueArray[ 0, 0 ]
#    nTdebug( 'tx: %-40s bins[1]: \n%s \nhist: \n%s\n%s' % ( tx, bins[1], hist, interpolatedValue ))
    return interpolatedValue



def getRescaling(valuesByEntrySsAndResType):
    '''Use a jack knife technique to get an estimate of the average and sd over all entry) scores.
    http://en.wikipedia.org/wiki/Resampling_%28statistics%29#Jackknife

    Returns the average, standard deviation, and the number of elements in the distribution.

    TODO: ADJUST FOR CIRCULAR NATURE.
    '''
    cList = NTlist()
    for entryId in valuesByEntrySsAndResType.keys():
        histRamaBySsAndResTypeNoEntry = getSumHistExcludingEntry( valuesByEntrySsAndResType, entryId)
#        nTdebug("histRamaBySsAndResTypeNoEntry: %s" % histRamaBySsAndResTypeNoEntry )
        z = NTlist()
        for ssType in valuesByEntrySsAndResType[ entryId ].keys():
            for resType in valuesByEntrySsAndResType[ entryId ][ssType].keys():
                angleDict =valuesByEntrySsAndResType[  entryId ][ssType][resType]
                angleList0 = angleDict[ 'phi' ]
                angleList1 = angleDict[ 'psi' ]
                his = getDeepByKeys(histRamaBySsAndResTypeNoEntry,ssType,resType)
                if his == None:
                    nTdebug('when testing not all residues are present in smaller sets.')
                    continue
                (c_av, c_sd, hisMin, hisMax) = getEnsembleAverageAndSigmaHis( his )
#                nTdebug("For entry %s ssType %s residue type %s found (c_av, c_sd) %8.3f %s" %(entryId,ssType,resType,c_av,repr(c_sd)))
                if c_sd == None:
                    nTdebug('Failed to get c_sd when testing not all residues are present in smaller sets.')
                    continue
                if c_sd == 0.:
                    nTdebug('%s Got zero c_sd, ignoring histogram. This should only occur in smaller sets.' % entryId)
                    continue
                if True: # disable when done debugging.
                    keyList = [ ssType, resType ]
                    cTuple = getDeepByKeysOrAttributes( hPlot.histRamaCtupleBySsAndResType, *keyList)
                    if not cTuple:
                        nTwarning("Failed to get cTuple for keyList %s; skipping" % (keyList))
                        continue
                    (_c_av_stored, _c_sd_stored, minHist, maxHist, _keyListStr) = cTuple
                    if hisMin != minHist:
                        nTerror(" hisMin != minHist: %8.0f %8.0f" % (hisMin, minHist))
                    elif hisMax != maxHist:
                        nTerror(" hisMax != maxHist: %8.0f %8.0f" % (hisMax, maxHist))
                    # TODO: extend checks to stored; then when debugged rewrite the code to use only the stored.
                for k in range(len(angleList0)):
                    ck = getValueFromHistogram(
                        histRamaBySsAndResTypeNoEntry[ssType][resType],
                        angleList0[k], angleList1[k])
                    zk = ( ck - c_av ) / c_sd
#                    nTdebug("For entry %s ssType %s residue type %s resid %3d found ck %8.3f zk %8.3f" %(entryId,ssType,resType,k,ck,zk))
                    z.append( zk )
        (av, sd, n) = z.average()
        nTdebug("%4s,%8.3f,%8.3f,%d" %( entryId, av, sd, n))
        cList.append( av )
#    (Cav, Csd, Cn) = cList.average()
#    return (Cav, Csd, Cn)
    return cList.average()
# end def


def getSumHistExcludingEntry( valuesByEntrySsAndResType,  entryIdToExclude):
    """Todo generalize to do other angles."""
    xRange = (plotparams360.min, plotparams360.max)
    yRange = (plotparams360.min, plotparams360.max)
    hrange = (xRange, yRange)
    histRamaBySsAndResTypeNoEntry = {}
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
#            nTdebug( 'entry: %s ssType %s resType %s angleList0 %s' % (
#                entryId, ssType, resType, angleList0 ))
            hist2d, _xedges, _yedges = histogram2d(
                angleList1, # think rows (y)
                angleList0, # think columns (x)
                bins = binCount,
                range= hrange)
            setDeepByKeys( histRamaBySsAndResTypeNoEntry, hist2d, ssType, resType )

    return histRamaBySsAndResTypeNoEntry



def inRange(a, isRange360=True):
    'Return True if the value is within range [0,360] by default or [-180,180] if not isRange360'
    if isRange360:
        if a < plotparams360.min or a > plotparams360.max:
            return False
        return True
    if a < plotparams180.min or a > plotparams180.max:
        return False
    return True

def getStatsRestraintNTlist(rL):
    """
    Routine will add stats to rL NTlist object.
    Routine should be adjusted for any type of restraint other than distance / dihedral.
    rL stands for restraint list.
    """

#    nTdebug("Looking at rL: %s" % rL)
    rL.rmsd       = None
    rL.violAv     = None
    rL.violAvAll  = None
    rL.violMaxAll = None
    rL.violSum    = None
    rL.violCount1 = 0
    rL.violCount3 = 0
    rL.violCount5 = 0

    if not rL: # Test for at least one member.
        return
    modelCount = rL.getModelCount()
    if not modelCount:
        return


    # Sort on violation count
    NTsort(rL, 'violCount3', inplace=True )
    rL.reverse()

    # Calculate sum, rmsd and sum_of_average_deviation of restraints per list
    # s is sum
    s = 0.0
    sumsq = 0.0
    n = 0 # This counts the total number of violations for each restraint and violated model.

    restraintCount = len(rL)
    for d in rL:
        if d.violations == None: # Happens for ParvulustatParis
            continue
        s = d.violations.sum( s )
        sumsq = d.violations.sumsq( sumsq )
        n += lenNonZero(d.violations)
    #end for
    rL.violSum    = s
    rL.violMaxAll = rL.zap('violMax').max() # note it is not any average. Hence the 'All' postfixed.
    rL.violCount1 = rL.zap('violCount1').sum()
    rL.violCount3 = rL.zap('violCount3').sum()
    rL.violCount5 = rL.zap('violCount5').sum()

#        if residue:
#            nTmessage('Only restraints without values so no rmsd for residue: %s' % residue)
    m = modelCount * restraintCount
    rL.violAvAll = rL.violSum / m
    rL.rmsd = math.sqrt(sumsq/m)

    rL.violAv = 0.0
    if n:
        rL.violAv = rL.violSum / n

#    nTdebug("Found restraintCount,n: %s %s" % (restraintCount,n))
# end def

