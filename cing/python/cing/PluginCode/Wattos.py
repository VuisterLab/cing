from cing.Libs.NTplot import * #@UnusedWildImport
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.NmrStar import NmrStar
from cing.PluginCode.required.reqMatplib import MATPLIB_STR
from cing.PluginCode.required.reqWattos import * #@UnusedWildImport
from cing.STAR.File import File
from cing.core.parameters import cingPaths
from cing.core.parameters import plugins


if True: # block
    # TODO: use more advanced tests.
    if not cingPaths.classpath:
#        nTdebug("Missing java classpath which is an optional dependency for Wattos")
        raise ImportWarning(WATTOS_STR)
#    if not (('/Users/jd/workspace35/wattos/lib/Wattos.jar' in cingPaths.classpath) or (# development classes.
#             '/Users/jd/workspace35/wattos/build' in cingPaths.classpath) or
#             ('/Users/alan/workspace/Wattos/lib/Wattos.jar' in cingPaths.classpath)):
    classpathCombinedAgain = ':'.join(cingPaths.classpath)
    if not (('/lib/Wattos.jar' in classpathCombinedAgain) or ('/build' in classpathCombinedAgain)):
#        nTdebug("Missing Wattos jar in java classpath [%s] which is an optional dep for Wattos" % classpathCombinedAgain)
        raise ImportWarning(WATTOS_STR)

#    nTmessage('Using Wattos')
#if True: # for easy blocking of data, preventing the code to be resorted with imports above.
#    from cing.PluginCode.required.reqCcpn import CCPN_STR
#    switchOutput(False)
#    try:
#        import ccpnmr #@UnusedImport
#        from ccp.general.Util import createMoleculeTorsionDict #@UnusedImport
#        from memops.api.Implementation import MemopsRoot #@UnusedImport
#        from memops.general.Io import loadProject #@UnusedImport
#    except:
#        switchOutput(True)
#        raise ImportWarning(WATTOS_STR)
#    finally: # finally fails in python below 2.5
#        switchOutput(True)
##    nTmessage('Using Ccpn')


class Wattos(NTdict):
    """
    Class to use Wattos checks.
    Adding completeness and all other checks.
    """

    nameDefs = [
                (COMPLCHK_STR, 'NOE Completeness 4Ang.', 'NOE Completeness 4A'),
                (OBS_COUNT_STR, 'Restraint count', 'Restraints Observed/Expected/Matched'),
                (OBS_ATOM_COUNT_STR, 'Atom count', 'Atom count'),
    ]

    shortNameDict = NTdict()
    for row in nameDefs:
        n1 = row[0]
#        nameDict[n1] = row[1]
        if len(row) >= 3:
            shortNameDict[n1] = row[2]

    def __init__(self, rootPath = '.', molecule = None, ranges = None, **kwds):
        NTdict.__init__(self, __CLASS__ = 'Wattos', **kwds)
        self.checks = None
        self.molecule = molecule
        self.rootPath = rootPath
        self.surplus_check_file_name_base = "wattos_surplus_chk"
        self.completeness_check_file_name = "wattos_completeness_chk.str"
        self.ranges                = ranges

        self.scriptTemplate = """
InitAll

SetProp
interactiveSession
false

SetProp
verbosity
VERBOSITY

SetProp
writeSessionOnExit
false

ListProp

#Input file
#Read molecular system and coordinates (y suggested)
#Read restraints (y suggested)
#Match restraints to soup by regular STAR tags. (y suggested)
#Match restraints to soup by author atom and residue names etc. (n suggested; only previous or this can and must be set)
#Remove unlinked restraints (y suggested)
#Sync over models; removing inconsistent atoms (true suggested)
ReadEntryNMRSTAR
INPUT_STR_FILE
y
y
y
n
y
y

SelectResiduesByRangesExp
RANGES
y
y

# Redundancy tolerance (5% suggested)
# Should impossible target distance be reset to null (y suggested)
# Should only fixed distances be considered surplus (n suggested)
# Averaging method id. Center,Sum,R6 are 0,1, and 2 respectively and -1 to let it be determined per list but that's not completely implemented yet: (1 suggested)
# Number of monomers but only relevant when Sum averaging is selected: (1 suggested)"));
# Enter file name base (with path) for output of surplus check summary and constraint lists.
# Should non-redundant constraints be written (y suggested)
# Should redundant constraints be written (n suggested)
# Should redundant constraints be removed (y suggested)
CheckSurplus
5.0
y
n
1
1
""" + \
self.surplus_check_file_name_base + \
"""
y
y
y

CalcDistConstraintViolation
0.5
wattos_dist_viol.str

CalcDihConstraintViolation
5.0
wattos_dihed_viol.str

# Using same defaults as for FRED (NMR Restraints Grid) analysis.
CheckCompleteness
4
2
6
8
2
9
14
1.0
1
1
n
ob_standard.str
""" + \
self.completeness_check_file_name + \
"""
n
wattos_completeness_chk

# Tolerance (0.1 Angstrom suggested)
CalcBond
0.1

# Hydrogen bond distance between proton and acceptor cutoff (2.7 Angstroms suggested)
# Hydrogen bond distance between donor and acceptor cutoff (3.35 Angstroms suggested)
# Hydrogen bond angle (D-H-A) cutoff (90 degrees suggested)
# Enter star file name (with path) for output: (e.g. C:\1brv_hb.txt)
CalcHydrogenBond
2.7
3.35
90.0
wattos_hb.txt

# Angle cutoff (40.0 degrees suggested)
# Use only Watson Crick basepairing (false suggested)
# Enter csv file name (with path) for output of CalcCoPlanarBasesSet.
CalcCoPlanarBasesSet
45.0
n
coPlanarBasesSet.csv

Quit
"""
        self.residueLoL = self.molecule._getResidueLoL()
        if not self.residueLoL:
            nTerror("Failed to get residue LoL")

    def locateWattosResidue(self, entityAssemblyId, compIndexId, compId):
        residue = getDeepByKeys(self.residueLoL, int(entityAssemblyId) - 1, int(compIndexId) - 1)
        strTuple = "entityAssemblyId, compIndexId, compId %s %s %s" % (entityAssemblyId, compIndexId, compId)
        if not residue:
            nTerror("Failed to get residue in locateWattosResidue for " + strTuple)
            return None
#        nTdebug("Retrieved %s for Wattos %s" % (residue, strTuple))
        return residue

    def _processComplCheck(self, fullName):
        """
        Put parsed data of all models into CING data model
        Return None for success or True for error.

        Example of processed data structure attached to say a residue:
            "wattos": {
                "COMPCHK": {
                    "valeList": [ 0.009, 0.100 ],
                    "qualList": ["POOR", "GOOD" ]},
                "BLABLACHK": {
                    "valeList": [ 0.009, 0.100 ],
                    }}
                    """
        nTdetail("==> Processing the Wattos results into CING data model")
        # Assemble the atom, residue and molecule specific checks
        # set the formats of each check easy printing
#        self.molecule.setAllChildrenByKey( WHATIF_STR, None)
        self.molecule.wattos = self # is self and that's asking for luggage


        # sorting on mols, residues, and atoms
#        nTmessage("  for self.checks: " + repr(self.checks))
#        nTdebug("  for self.checks count: %s" % len(self.checks))

        starFile = File()
        starFile.filename = fullName
        if starFile.read():
            nTerror("Failed to read star file: %s" % fullName)
            return True
        # end if

        sfList = starFile.getSaveFrames(category = "NOE_completeness_statistics")
        if not sfList or len(sfList) != 1:
            nTerror("Failed to get single saveframe but got list of: [%s]" % sfList)
            return True

        saveFrameCompl = sfList[0]
        tagTableComplHeader = saveFrameCompl.tagtables[0]
        completenessMol = tagTableComplHeader.getFloat("_NOE_completeness_stats.Completeness_cumulative_pct", 0)
        noe_compl_obs   = tagTableComplHeader.getInt("_NOE_completeness_stats.Constraint_observed_count", 0)
        noe_compl_exp   = tagTableComplHeader.getInt("_NOE_completeness_stats.Constraint_expected_count", 0)
        noe_compl_mat   = tagTableComplHeader.getInt("_NOE_completeness_stats.Constraint_matched_count", 0)

        self.molecule.setDeepByKeys(completenessMol, WATTOS_STR, COMPLCHK_STR,  VALUE_LIST_STR)
        self.molecule.setDeepByKeys(noe_compl_obs  , WATTOS_STR, OBS_COUNT_STR, VALUE_LIST_STR)
        self.molecule.setDeepByKeys(noe_compl_exp  , WATTOS_STR, EXP_COUNT_STR, VALUE_LIST_STR)
        self.molecule.setDeepByKeys(noe_compl_mat  , WATTOS_STR, MAT_COUNT_STR, VALUE_LIST_STR)

        tagTableComplBody = saveFrameCompl.tagtables[3]

        entityAssemblyIdList = tagTableComplBody.getIntListByColumnName("_NOE_completeness_comp.Entity_assembly_ID")
        compIndexIdList = tagTableComplBody.getIntListByColumnName("_NOE_completeness_comp.Comp_index_ID")
        compIdList = tagTableComplBody.getStringListByColumnName("_NOE_completeness_comp.Comp_ID")

        obsAtomCountList = tagTableComplBody.getIntListByColumnName("_NOE_completeness_comp.Obs_atom_count")
        obsCountList = tagTableComplBody.getIntListByColumnName("_NOE_completeness_comp.Constraint_observed_count")
        expCountList = tagTableComplBody.getIntListByColumnName("_NOE_completeness_comp.Constraint_expected_count")
        matCountList = tagTableComplBody.getIntListByColumnName("_NOE_completeness_comp.Constraint_matched_count")

        completenessResidueList = tagTableComplBody.getFloatListByColumnName("_NOE_completeness_comp.Completeness_cumulative_pct")
        detailsList = tagTableComplBody.getStringListByColumnName("_NOE_completeness_comp.Details")

        for i, completenessResidue in enumerate(completenessResidueList):
            entityAssemblyId = entityAssemblyIdList[i]
            compIndexId = compIndexIdList[i]
            compId = compIdList[i]

            obsAtomCount = obsAtomCountList[i]
            obsCount = obsCountList   [i]
            expCount = expCountList   [i]
            matCount = matCountList   [i]

            details = detailsList[i]
            wattosTuple = (entityAssemblyId, compIndexId, compId)
            residue = self.locateWattosResidue(*wattosTuple)
            if not residue:
                nTerror("Failed to find Wattos residue in CING: %s %s %s" % (wattosTuple))
                return True

            residueWattosDic = residue.setdefault(WATTOS_STR, NTdict())
            complDic = residueWattosDic.setdefault(COMPLCHK_STR, NTdict())
#                    "valeList": [ 0.009]
#                    "qualList": [">sigma" ]
            complDic[VALUE_LIST_STR] = completenessResidue
            complDic[QUAL_LIST_STR] = details

            residueWattosDic.setDeepByKeys(obsAtomCount, OBS_ATOM_COUNT_STR, VALUE_LIST_STR)
            residueWattosDic.setDeepByKeys(obsCount, OBS_COUNT_STR, VALUE_LIST_STR)
            residueWattosDic.setDeepByKeys(expCount, EXP_COUNT_STR, VALUE_LIST_STR)
            residueWattosDic.setDeepByKeys(matCount, MAT_COUNT_STR, VALUE_LIST_STR)
        # end for
#        nTdebug('done with _processComplCheck')
    #end def

def runWattos(project, ranges=None, tmp = None, parseOnly=False):
    try:
        return _runWattos(project, ranges=ranges, tmp = tmp, parseOnly=parseOnly)
    except:
        nTerror("Failed runWattos by throwable below.")
        nTtracebackError()
        return True

def _runWattos(project, ranges=None, tmp = None, parseOnly=False):
    """
        Run and import the wattos results per model.
        All models in the ensemble of the molecule will be checked.
        Set wattos references for Molecule, Chain, Residue and Atom instances
        or None if no wattos results exist
        returns 1 on success or None on any failure.
    """

    if not project.molecule:
        nTerror("runWattos: no molecule defined")
        return True

    mol = project.molecule
    if not mol:
        nTerror("No project molecule in runWattos")
        return None
    if mol.modelCount == 0:
        nTwarning('runWattos: no models for "%s"', mol)
        return



    path = project.path(mol.name, project.moleculeDirectories.wattos)
    if not os.path.exists(path):
        mol.wattos = None
        for chain in mol.allChains():
            chain.wattos = None
        for res in mol.allResidues():
            res.wattos = None
        for atm in mol.allAtoms():
            atm.wattos = None
        return None

    if ranges == None:
        ranges = mol.ranges
    wattos = Wattos(rootPath = path, molecule = mol, ranges = ranges)
    del ranges # only use wattos.ranges now.
    useRanges = mol.useRanges(wattos.ranges)
    if mol == None:
        nTerror('runWattos: no mol defined')
        return None

    if mol.modelCount == 0:
        nTwarning('runWattos: no models for "%s"', mol)
        return None

    wattosDir = project.mkdir(mol.name, project.moleculeDirectories.wattos)

    wattosStatus = project.wattosStatus

    if not parseOnly:
        wattosStatus.completed           = False
        wattosStatus.parsed              = False
        wattosStatus.time                = None
        wattosStatus.exitCode            = None

        fileName = 'project.str'
        fullname = os.path.join(os.path.curdir, wattosDir, fileName)
        fullname = os.path.abspath(fullname)

        if os.path.exists(fullname):
            if not os.unlink(fullname):
                nTmessage("Removing existing file: %s" % fullname)
            else:
                nTerror("Failed to remove existing file: %s" % fullname)
                return None

        nmrStar = NmrStar(project)
        if not nmrStar:
            nTerror("Failed to create NmrStar(project)")
            return None

        if not nmrStar.toNmrStarFile(fullname):
            nTmessage("Failed to nmrStar.toNmrStarFile (fine if there wasn't a CCPN project to start with)")
            return None

        if not os.path.exists(fullname):
            nTerror("Failed to create file [%s] in nmrStar.toNmrStarFile" % fullname)
            return None
        
        scriptComplete = wattos.scriptTemplate
        scriptComplete = scriptComplete.replace("INPUT_STR_FILE", fileName)
        scriptComplete = scriptComplete.replace("VERBOSITY", repr(cing.verbosity))
        rangesTxt = wattos.ranges
        if not useRanges: # Wattos can't handle a None this way.
            rangesTxt = ALL_RANGES_STR
        rangesTxtWattos = project.molecule.rangesToMmCifRanges(rangesTxt)
        if rangesTxtWattos == None:
            rangesTxtWattos = ALL_RANGES_STR
        if rangesTxt != rangesTxtWattos:
            nTmessage("==> Translating ranges %s to mmCIF numbering scheme: %s" % (rangesTxt, rangesTxtWattos ))
        scriptComplete = scriptComplete.replace("RANGES", rangesTxtWattos)
        # Let's ask the user to be nice and not kill us
        # estimate to do **0.5 residues per minutes as with entry 1bus on dual core intel Mac.
        timeRunEstimatedInSeconds = 0.025 * mol.modelCount * len(mol.allResidues())
        timeRunEstimatedInSeconds *= 60
        timeRunEstimatedList = timedelta2Hms(timeRunEstimatedInSeconds)
        msg = '==> Running Wattos for an estimated (5,000 atoms/s): %s hours, %s minutes and %s seconds; please wait' % timeRunEstimatedList
        nTmessage(msg)
        scriptFileName = "wattos.script"
        scriptFullFileName = os.path.join(wattosDir, scriptFileName)
        open(scriptFullFileName, "w").write(scriptComplete)
    #    wattosPath = "echo $CLASSPATH; java -Xmx512m -Djava.awt.headless=true Wattos.CloneWars.UserInterface -at"
#        wattosPath = "java -Xmx512m -Djava.awt.headless=true Wattos.CloneWars.UserInterface -at"
        # 2 Gb fails on ubuntu 11.4 but 1800 Mb works.
        wattosPath = "java -d32 -Xmx1800m -Djava.awt.headless=true Wattos.CloneWars.UserInterface -at"
        logFileName = "wattos_compl.log"
        wattosProgram = ExecuteProgram(wattosPath, rootPath = wattosDir,
                                 redirectOutputToFile = logFileName,
                                 redirectInputFromFile = scriptFileName)
        # The last argument becomes a necessary redirection into fouling Wattos into
        # thinking it's running interactively.
        now = time.time()
        wattosExitCode = wattosProgram()

#        nTdebug("Took number of seconds: " + sprintf("%8.1f", time.time() - now))

        wattosStatus.exitCode  = wattosExitCode
        wattosStatus.time      = sprintf("%.1f", time.time() - now)
        wattosStatus.keysformat()

        if wattosExitCode:
            nTerror("Failed wattos checks with exit code: " + repr(wattosExitCode))
            return None
        wattosStatus.completed = True
    # end if not parseOnly

    if not project.hasDistanceRestraints():
        return wattos

    fullname = os.path.join(wattosDir, wattos.completeness_check_file_name)
    if not os.path.exists(fullname):
        nTwarning("Failed to find wattos completeness check result file: %s" % fullname)
        return None
#    nTmessage('==> Parsing checks')

    if wattos._processComplCheck(fullname):
        nTerror("\nrunWattos Failed to parse check %s", fullname)
        return None


    pathOutSurplus = os.path.join(path, wattos.surplus_check_file_name_base + '_summary.txt')
    if not os.path.exists(pathOutSurplus): # Happened for 1ao2 on production machine; not on development...
        nTerror("Path does not exist: %s" % (pathOutSurplus))
        return True
#    nTdebug('> parsing ' + pathOutSurplus)
    fullTextSurplus = open(pathOutSurplus, 'r').read()
    if not fullTextSurplus:
        nTerror('Failed to parse Wattos surplus summary file')
        return True


    startString = 'SUMMARY:'
    surplusSummary = getTextBetween(fullTextSurplus, startString, endString = None, startIncl = False, endIncl = False)
    if not surplusSummary:
        nTerror("Failed to find surplusSummary in surplusSummary[:80]: [%s]" % surplusSummary[:80])
        return True
    surplusSummary = "Wattos Surplus Analysis Summary\n\n" + surplusSummary.strip()

#    nTdebug('got surplusSummary: \n' + surplusSummary)

#    pathOutCompleteness = os.path.join(path, 'wattos_completeness_chk.str')
#    if not os.path.exists(pathOutCompleteness): # Happened for 1ao2 on production machine; not on development...
#        nTerror("Path does not exist: %s" % (pathOutCompleteness))
#        return True
#    nTdebug('> parsing ' + pathOutCompleteness)
#    fullTextCompleteness = open(pathOutCompleteness, 'r').read()
#    if not fullTextCompleteness:
#        nTerror('Failed to parse Wattos completeness summary file')
#        return True
#
#    startString = '_NOE_completeness_shell.Type'
#    endString = 'stop_'
#    completenessSummary = getTextBetween(fullTextCompleteness, startString, endString, endIncl = False)
#    if not completenessSummary:
#        nTerror("Failed to find completenessSummary in fullText[:80]: [%s]" % fullTextCompleteness[:80])
#        return True
#    completenessSummary = '\n'.join([HTML_TAG_PRE,
#                                completenessSummary.strip(),
#                                '---------------------------------------------',
#                                HTML_TAG_PRE2])
#
#    nTdebug('got completenessSummary: \n' + completenessSummary)

#    intro = '----------- Wattos summary -----------'
    completenessMolStr = NaNstring
    completenessMol = mol.getDeepByKeys( WATTOS_STR, COMPLCHK_STR, VALUE_LIST_STR)
    if completenessMol:
        completenessMolStr = val2Str(completenessMol, "%.2f")
    complStatement = 'Overall NOE completeness is %s percent\n' % completenessMolStr

    summary = '\n\n'.join([surplusSummary, complStatement])
    if setDeepByKeys(mol, summary, WATTOS_SUMMARY_STR):
        nTerror('Failed to set Wattos summary')
        return True

    wattosStatus.parsed = True
#    nTdebug("In runWattos: project.wattosStatus.completed: %s" % project.wattosStatus.completed)

    return wattos # Success
#end def

def createHtmlWattos(project, ranges = None):
    """ Read out wiPlotList to see what get's created. """

    if not getDeepByKeysOrAttributes(plugins, MATPLIB_STR, IS_INSTALLED_STR):
#        nTdebug('Skipping createHtmlWattos because no matplib installed.')
        return
    from cing.PluginCode.matplib import MoleculePlotSet #@UnresolvedImport

#    wiPlotList.append( ('_01_backbone_chi','QUA/RAM/BBC/C12') )
    # The following object will be responsible for creating a (png/pdf) file with
    # possibly multiple pages
    # Level 1: row
    # Level 2: against main or alternative y-axis
    # Level 3: plot parameters dictionary (extendable).
    keyLoLoL = []
    plotAttributesRowMain = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ WATTOS_STR, COMPLCHK_STR, VALUE_LIST_STR ]
    plotAttributesRowMain[ YLABEL_STR] = Wattos.shortNameDict[  COMPLCHK_STR ]
    plotAttributesRowMain[ USE_ZERO_FOR_MIN_VALUE_STR] = True
    plotAttributesRowMain[ USE_MAX_VALUE_STR] = 100.0
    keyLoLoL.append([ [plotAttributesRowMain] ])

    plotAttributesRowMain = NTdict()
    plotAttributesRowAlte = NTdict()
    plotAttributesRowMain[ KEY_LIST_STR] = [ WATTOS_STR, OBS_COUNT_STR, VALUE_LIST_STR ]
    plotAttributesRowMain[ KEY_LIST2_STR] = [ WATTOS_STR, EXP_COUNT_STR, VALUE_LIST_STR ]
    plotAttributesRowMain[ KEY_LIST3_STR] = [ WATTOS_STR, MAT_COUNT_STR, VALUE_LIST_STR ]
    plotAttributesRowAlte[ KEY_LIST_STR] = [ WATTOS_STR, OBS_ATOM_COUNT_STR, VALUE_LIST_STR ]
    plotAttributesRowMain[ YLABEL_STR] = Wattos.shortNameDict[  OBS_COUNT_STR ]
    plotAttributesRowAlte[ YLABEL_STR] = Wattos.shortNameDict[  OBS_ATOM_COUNT_STR ]
    plotAttributesRowMain[ USE_ZERO_FOR_MIN_VALUE_STR] = True
    keyLoLoL.append([ [plotAttributesRowMain], [plotAttributesRowAlte] ])

    printLink = project.moleculePath('wattos', project.molecule.name + wattosPlotList[0][0] + ".pdf")
    moleculePlotSet = MoleculePlotSet(project = project, ranges = ranges, keyLoLoL = keyLoLoL)
    moleculePlotSet.renderMoleculePlotSet(printLink, createPngCopyToo = True)
#end def

def restoreWattos( project, tmp=None ):
    """
    Optionally restore Wattos results
    """
    if project.wattosStatus.completed:
        nTmessage('==> Restoring Wattos results')
        project.runWattos(parseOnly=True)
#    else:
#        nTdebug("In restoreWattos: project.wattosStatus.completed: %s" % project.wattosStatus.completed)
#end def

# register the functions
methods = [(runWattos, None),
           (createHtmlWattos, None)
           ]
restores = [(restoreWattos, None)]
