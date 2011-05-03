#!/usr/bin/env python
"""
Execute as (or use alias refine):

python $CINGROOT/python/Refine/refine.py

 GWV 23 February/March 2005: water refinement
 GWV March 2007: Adapted for usage with cing
 - Model indices [0,Nmodels>
 - General directory structure using --setup
 - Inclusion of parsing of refine result using --parse
 GWV April 2008: version 0.70
 - Modified --setup: full export to refine directories; automated generation
   of parameters file
 - Import into cing (version >= 0.70);
 JFD April 2011
   Adding anneal
#------------------------------------------------------------------------------
"""
from Refine.NTxplor import * #@UnusedWildImport
from Refine.Utils import * #@UnusedWildImport
from Refine.configure import config
from cing.Libs.AwkLike import AwkLike
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.disk import copy
from cing.Libs.forkoff import ForkOff
from cing.core.classes import Project
#from cing.core.constants import * #@UnusedWildImport
#from cing.core.molecule import mapMolecules #@UnusedImport

TEMPLATE_FILE_NAME = 'template.pdb'

# class wrapper to allow passing of key-argument
# to compare dict function
class CompareDict:
    def __init__(self, key):
        self.key = key
    #end def

    def __call__(self, a, b):
        return cmp(a[self.key], b[self.key])
    #end def
#end class

# class wrapper to allow passing of a key-argument
# to dict entry
class Key:
    def __init__(self, key):
        self.key = key
    #end def

    def __call__(self, a):
        return a[self.key]
    #end def
#end class

def importFromRefine(config, params, project, options):
    """
    Import data from params.basePath/XXX directory as new molecule.
    The input can be from the Refined or from the Annealed directory.

    Use params.bestModels

    Return Molecule or None on error
    """
    inPath     = config.directories.refined
    if options.useAnnealed:
        inPath     = config.directories.annealed

    xplor = Xplor(config, params)

    models = asci2list(xplor.bestModels)
    if len(models) == 0:
        NTerror('%s: no bestModels defined' % getCallerName())
        return
    #end if

    project.restore()

    # import the coordinates from Xplor PDB files
    path = xplor.joinPath(inPath, xplor.baseName)
    NTmessage('==> Importing coordinates from %s, models %s', path, models)
    project.molecule.initCoordinates()
    for m in models:
        xplorFile = sprintf(path, m)
        if not os.path.exists(xplorFile):
            NTerror('%s: model "%s" not found' % (getCallerName(), xplorFile))
            return
        #end if
        if not project.molecule.importFromPDB(xplorFile, convention=XPLOR, nmodels=1):
            NTerror("Failed to importFromPDB from: " + getCallerName())
            return
    #end for
    project.molecule.updateAll()

    # rename the molecule
    project.molecules.rename(project.molecule.name, xplor.name)
    print project.molecule.format()

#    if 'superpose' in xplor and len(xplor.superpose) > 0:
    if getDeepByKeysOrAttributes(xplor, 'superpose'):
        project.molecule.superpose(ranges=xplor.superpose)

    print project.format()

    project.close()
    return project.molecule
#end def


def doSetup(config, project, basePath, options):
    """Generate the directory setup and parameter.py file from project and basePath
       Export the data from project.
       Return True on error.
    """

    if os.path.exists(basePath):
        removedir(basePath)
    #end if

#    from Refine.NTxplor import Xplor #@Reimport JFD: I don't know why needed....
    xplor = Xplor(config, basePath=basePath) # generates the directories and initialize parameter setup

    # copy xplor parameter and topology files
    for fname in os.listdir(os.path.join(xplor.refinePath, 'toppar')):
        if not fnmatch(fname, '.*'):
#            print '>>',fname
            copy(os.path.join(xplor.refinePath, 'toppar', fname), xplor.joinPath(xplor.directories.toppar, fname))
    #print ">>", xplor

    # restore the data
#    project.restore() # JFD: why ? I get doubling of restraint lists by this.
    NTmessage(project.format())
    if project.molecule == None:
        NTerror('doSetup: No molecule defined for project %s\n', project)
        return True
    #end if

    project.validateRestraints(toFile=True)

    if options.superpose and len(options.superpose) > 0:
        xplor.superpose = options.superpose
        project.molecule.superpose(ranges=xplor.superpose)

    # export the data
    NTmessage('\n' + dots * 10)
    NTmessage('==> Exporting %s to %s for refinement\n', project, basePath)

    for drl in project.distances:
        drl.renameToXplorCompatible()
        xplor.noeRestraints.append(refineNoeParameters(drl.name))
        fname = xplor.joinPath(xplor.directories.tables, drl.name + '.tbl')
        drl.export2xplor(fname)
    #end for

    for drl in project.dihedrals:
        drl.renameToXplorCompatible()
        xplor.dihedralRestraints.append(refineDihedralParameters(drl.name))
        fname = xplor.joinPath(xplor.directories.tables, drl.name + '.tbl')
        drl.export2xplor(fname)
    #end for

    # export structures in Xplor-PDB format
    xplor.baseName = project.molecule.name + '_%03d.pdb'
    path = xplor.joinPath(xplor.directories.converted, xplor.baseName)
    NTmessage('==> Exporting %s to XPLOR PDB-files (%s)', project.molecule, path)
    project.molecule.export2xplor(path)
    xplor.models = sprintf('%d-%d', 0, project.molecule.modelCount - 1)
    xplor.bestModels = sprintf('%d-%d', 0, project.molecule.modelCount - 1)
    #TODO
    #xplor.superpose  = sprintf('%d-%d', 0, project.molecule.modelCount-1)

    # PSF file
    xplor.psfFile = project.molecule.name + '.psf'
    # Set the patches for the psf file
    for res in project.molecule.residuesWithProperties('HIS'):
        xplor.patchHISD.append(res.resNum)
    for res in project.molecule.residuesWithProperties('HISE'):
        xplor.patchHISE.append(res.resNum)
    for res in project.molecule.residuesWithProperties('cPRO'):
        xplor.patchCISP.append(res.resNum)
    disulfide_bridges = project.molecule.idDisulfides(toFile=False, applyBonds=False)

    if disulfide_bridges == True:
        NTerror("Failed to analyze disulfide bridges.")
    elif disulfide_bridges:
        NTmessage("==> Located disulfide bridges %s" % str(disulfide_bridges))
    for (res1, res2) in disulfide_bridges:
        xplor.patchDISU.append((res1.resNum, res2.resNum))

    # save the parameter file
    parfile = xplor.joinPath('parameters.py')
    xplor.toFile(parfile)

    NTmessage('\n==> Generated setup under "%s"\nEdit "%s" before continuing\n',
              basePath, parfile
             )
#end def


def generatePSF(config, params, doPrint=0):
    '''PSF generation'''
    NTmessage("Generating .psf file for xplor")
    models = asci2list(params.models)
    pdbFile= params.baseName % models[0]
    psfJob = GeneratePSF(
         config,
         params,
         pdbFile=pdbFile,
#                         outPath    = config.directories.psf,
         jobName='generatePSF'
    )
    psfJob.createScript()
    if doPrint:
        psfJob.printScript()
    #end if
    psfJob.runScript()
#end def


def generateTemplate(config, params, doPrint=0):
    '''Extended structure generation'''
    NTmessage("Generating .pdb file for xplor")
    templateJob = GenerateTemplate(
         config,
         params,
         molecules=[
                         NTdict(
                            pdbFile=TEMPLATE_FILE_NAME,
                            selectionCode='(all)'
                         ),
                        ],
         outPath    = config.directories.template,
         jobName='generateTemplate'
    )
    templateJob.createScript()
    if doPrint:
        templateJob.printScript()
    #end if

    templateJob.runScript()
#end def


def analyze(config, params, doPrint=0, useAnnealed = False):
    '''Analyze a run
    Returns True on failure.
    '''
    NTmessage("Analyzing a run")

    inPath     = config.directories.converted
    if useAnnealed:
        inPath     = config.directories.annealed

    # first create the jobs, run later
    analyzeJobs = []
    for i in asci2list(params.models):
        job = Analyze(
                        config,
                        params,
                        fileNum=i,
                        molecules=[
                                      NTdict(
                                                psfFile=params.psfFile,
                                                pdbFile=params.baseName % i,
                                                selectionCode='(not resn TIP3 and not resn ANI)'
                                  ),
                         ],
                         inPath     = inPath,
                         outPath    = config.directories.analyzed,
                        jobName='analyze_%d' % i,
                     )

        analyzeJobs.append(job)
    #end for


    job_list = []
    for job in analyzeJobs:
        if job.createScript():
            NTerror("In refine#analyze failed to create at least one job's script.")
            return True
        if doPrint:
            job.printScript()
        #end if
#        job.runScript()
        job_list.append((job.runScript,) )
    #end for
    f = ForkOff(
            processes_max=cing.ncpus,
            max_time_to_wait=600,
            verbosity=cing.verbosity
        )
    done_list = f.forkoff_start(job_list, 0) # delay 0 second between jobs.
    NTmessage("Finished ids: %s", done_list)
#end def


def refine(config, params, doPrint=0):

    # first create the jobs, run later
    refineJobs = []
    for i in asci2list(params.models):
        refineJobs.append(
            WaterRefine(
                   config,
                   params,
                   fileNum=i,
                   molecules=[
                                 NTdict(
                                    psfFile=params.psfFile,
                                    pdbFile=params.baseName % i,
                                    selectionCode='(not resn TIP3 and not resn ANI)'
                                 ),
                                ],
                   inPath     = config.directories.analyzed,
                   outPath    = config.directories.refined,
                   jobName='refine_%d' % i,
            )
        )

    job_list = []
    for job in refineJobs:
        job.createScript()
        if doPrint:
            job.printScript()
#        job.runScript()
        job_list.append((job.runScript,) )
    #end for
    f = ForkOff(
            processes_max=cing.ncpus,
            max_time_to_wait=6000,
            verbosity=cing.verbosity
        )
    done_list = f.forkoff_start(job_list, 0) # delay 0 second between jobs.
    NTmessage("Finished ids: %s", done_list)
#end def


def anneal(config, params, doPrint=0):
    NTdebug("Now in %s" % getCallerName())
    # first create the jobs, run later
    annealJobs = []
    for i in asci2list(params.models):
        annealJobs.append(
            Anneal(
                   config,
                   params,
                   fileNum=i,
                   molecules=[
                                 NTdict(
                                    psfFile=params.psfFile,
                                    pdbFile=params.baseName % i,
                                    selectionCode='(all)'
                                 ),
                                ],
                   inPath     = config.directories.template,
                   outPath    = config.directories.annealed,
                   templateFile = TEMPLATE_FILE_NAME,
                   jobName='anneal_%d' % i,
            )
        )

    job_list = []
    for job in annealJobs:
        job.createScript()
        if doPrint:
            job.printScript()
        job_list.append((job.runScript,) )
#        job.runScript()
    #end for
    f = ForkOff(
            processes_max=cing.ncpus,
            max_time_to_wait=600,
            verbosity=cing.verbosity
        )
    done_list = f.forkoff_start(job_list, 0) # delay 0 second between jobs.
    NTmessage("Finished ids: %s", done_list)
#end def


def parseRefineOutput(config, params, options ):
    """
    Parse the output in the Jobs directory
    params is a NTxplor instance

    Return None on error.
    """

    xplor = Xplor(config, params, outPath=config.directories.refined)

    logFileNameFmt = 'refine_%d.log'
    resultFileName = 'parsedOutput.txt'
    bestModelsFileNameFmt = 'best%dModels.txt'
    if options.useAnnealed:
        logFileNameFmt = 'anneal_%d.log'
        resultFileName = 'parsedAnnealOutput.txt'
        bestModelsFileNameFmt = 'best%dModelsAnneal.txt'

    results = NTlist()
    # parse all output files
    for i in asci2list(params.models):

        file = xplor.checkPath(xplor.directories.jobs, logFileNameFmt % i)
        NTmessage('==> Parsing %s', file)

        data = NTdict(fileName=file,
                         model=i
                       )
        foundEnergy = 0
        foundNOE1 = 0
        foundNOE2 = 0
        foundDIHED = 0
        awkf = AwkLike(file)
        for line in awkf:
#            NTdebug("line: %s" % line.dollar[0])
            if (not foundEnergy) and find(line.dollar[0], '--------------- cycle=     1 ----------------') >= 0:
                awkf.next()
#                NTdebug("Getting total energy from line: %s" % line.dollar[0])
                data['Etotal'] = float(line.dollar[0][11:22])

                awkf.next()
#                NTdebug("Getting NOE energy from line: %s" % line.dollar[0])
                if line.dollar[0].count("E(NOE"): # Dirty hack; use regexp next time.
#                    NTdebug("Bingo")
                    data['Enoe'] = float(line.dollar[0][68:75])
                else:
                    awkf.next()
#                    NTdebug("Getting NOE energy (try 2) from line: %s" % line.dollar[0])
                    data['Enoe'] = float(line.dollar[0][68:75])
                # end if
                foundEnergy = 1
            elif (not foundNOE1) and find(line.dollar[0], 'NOEPRI: RMS diff. =') >= 0:
                data['NOErmsd'] = float(line.dollar[5][:-1])
                data['NOEbound1'] = float(line.dollar[7][:-2])
                data['NOEviol1'] = int(line.dollar[8])
                foundNOE1 = 1
            elif (not foundNOE2) and find(line.dollar[0], 'NOEPRI: RMS diff. =') >= 0:
                data['NOEbound2'] = float(line.dollar[7][:-2])
                data['NOEviol2'] = int(line.dollar[8])
                data['NOEnumber'] = float(line.dollar[10])
                foundNOE2 = 1
            elif (not foundDIHED) and find(line.dollar[0], 'Number of dihedral angle restraints=') >= 0:
                data['DIHEDnumber'] = int(line.dollar[6])
                awkf.next()
                data['DIHEDbound'] = float(line.dollar[6][:-1])
                data['DIHEDviol'] = int(line.dollar[7])
                awkf.next()
                data['DIHEDrmsd'] = float(line.dollar[3])
                foundDIHED = 1
            #endif
        #end for
        results.append(data)
    #end for

    keys = ['model', 'Etotal', 'Enoe', 'NOErmsd', 'NOEnumber', 'NOEbound1',
            'NOEviol1', 'NOEbound2', 'NOEviol2',
            'DIHEDrmsd', 'DIHEDnumber', 'DIHEDbound', 'DIHEDviol'
           ]

    # sort the results
    if options.sortField in keys:
        myComp = CompareDict(options.sortField)
        results.sort(myComp)
    else:
        options.sortField = None
    #endif

    # print results to file and screen
    resultFile = open(xplor.joinPath(resultFileName), 'w')
    printf('\n=== Results: sorted on "%s" ===\n', options.sortField)
    fprintf(resultFile, '=== Results: sorted on "%s" ===\n', options.sortField)
    fmt = '%-10s '
    for k in keys:
        printf(fmt, str(k))
        fprintf(resultFile, fmt, str(k))
    #end for
    printf('\n')
    fprintf(resultFile, '\n')
    for data in results:
        for k in keys:
            if k in data:
                printf(fmt, str(data[k]))
                fprintf(resultFile, fmt, str(data[k]))
            else:
                printf(fmt, '-')
                fprintf(resultFile, fmt, '-')
        #end for
        printf('\n')
        fprintf(resultFile, '\n')
    #end for

    # best results
    bestModels = int(options.bestModels)
    if bestModels > 0:
        printf('\n=== Averages best %d models ===\n', bestModels)
        fprintf(resultFile, '\n=== Averages best %d models ===\n', bestModels)
        for key in keys:
            getKey = Key(key)
            values = map(getKey, results)
            av, sd, dummy_n = NTaverage(values)
            printf('%-12s: %10.3f +/- %-10.3f\n', key, av, sd)
            fprintf(resultFile, '%-12s: %10.3f +/- %-10.3f\n', key, av, sd)
        #end for
        printf('\n\n')
        fprintf(resultFile, '\n\n')

        fname = xplor.joinPath(bestModelsFileNameFmt % bestModels)
        f = open(fname, 'w')
        params.bestModels = ''
        for i in range(0, bestModels):
            fprintf(f, '%s/%s\n', xplor.outPath, xplor.baseName % results[i].model)
            params.bestModels = sprintf('%s%s,', params.bestModels, results[i].model)
        #end for
        f.close()
        params.bestModels = params.bestModels[:-1]
        NTmessage('==> Best %d models listed in %s\n', bestModels, fname)
    else:
        params.bestModels = params.models
    #end if

    resultFile.close()
    params.toFile(xplor.joinPath('parameters.py'))

    #print '>>>'
    #print xplor.format( params.__FORMAT__ )
    return results
#end def

def fullAnneal( config, parameters, project, options ):
    """
    Recalculate the coordinates.
    Return True on error.
    """
    options.name = 'annealed'

    refinePath = project.path(project.directories.refine )
    NTmessage('==> refinePath: %s', refinePath)
    basePath = os.path.join( refinePath, options.name)
    NTmessage('==> basePath: %s', basePath)

    NTmessage("-- analyze --")
    if doSetup(config, project, basePath, options):
        NTerror("Failed setup")
        return True
    # end if

    NTmessage("-- generatePSF --")
    if generatePSF(config, parameters):
        NTerror("Failed generatePSF")
        return True
    # end if

    NTmessage("-- generateTemplate --")
    if generateTemplate(config, parameters):
        NTerror("Failed generateTemplate")
        return True
    # end if

    NTmessage("-- anneal --")
    if anneal(config, parameters):
        NTerror("Failed anneal")
        return True
    # end if

    NTmessage("-- analyze --")
    if analyze(config, parameters, useAnnealed = True):
        NTerror("Failed analyze")
        return True
    # end if

    NTmessage("-- parseRefineOutput --")
    if not parseRefineOutput(config, parameters, options):
        NTerror("Failed parseRefineOutput")
        return True
    # end if

    NTmessage("-- importFromRefine --")
    if not importFromRefine(config, parameters, project, options):
        NTerror("Failed importFromRefine")
        return True
    # end if

#end def


def run():
    parser = getRefineParser()
    (options, _args) = parser.parse_args()

    if options.verbosity >= 0 and options.verbosity <= 9:
        cing.verbosity = options.verbosity
    else:
        NTerror("set verbosity is outside range [0-9] at: " + options.verbosity)
        NTerror("Ignoring setting")
    # From this point on code may be executed that will go through the appropriate verbosity filtering


    #------------------------------------------------------------------------------
    # Documentation
    #------------------------------------------------------------------------------
    if options.doc:
        parser.print_help(file=sys.stdout)
        NTmessage("%s\n", __doc__)
        return
    #end if

    #------------------------------------------------------------------------------
    #check for the required project, name option
    parser.check_required('--name')
    parser.check_required('--project')

    NTmessage(dots * 10 + "\n")
#    versionStr = "     Refine reversion %s" % cing.revision
#    if cingRevision:
#        versionStr += " (r%d)" % cingRevision
#    NTmessage(versionStr)
#    NTmessage("\n" + dots * 10 + "\n")

    #------------------------------------------------------------------------------
    # Project
    #------------------------------------------------------------------------------
    project = Project.open(options.project, status='old',
                           restore=1) #DEFAULT 0
    if project == None:
        NTerror("Failed to get a project")
        return True
    #end if
    basePath = project.path(project.directories.refine, options.name)

    #------------------------------------------------------------------------------
    # Setup
    #------------------------------------------------------------------------------
    if options.doSetup:
        doSetup(config, project, basePath, options)
#        return # We had like to continue in new setup.
    #end if

    #------------------------------------------------------------------------------
    # Some output
    #------------------------------------------------------------------------------
    NTmessage("==> Reading configuration")
    NTmessage('refinePath:     %s', config.refinePath)
    NTmessage('xplor:          %s', config.XPLOR)
    NTmessage("parameterFiles: %s", config.parameterFiles)
    NTmessage("topologyFiles:  %s", config.topologyFiles)

    #------------------------------------------------------------------------------
    # read parameters file
    #------------------------------------------------------------------------------
    parameters = getParameters( basePath, 'parameters')
#    NTdebug('==> parameters\n%s\n', str(parameters))

    parameters.basePath = basePath
    parameters.name = options.name

    #------------------------------------------------------------------------------
    # Model selection
    #------------------------------------------------------------------------------
    if options.models:
        parameters.models = options.models
    #end if

    #------------------------------------------------------------------------------
    # Overwrite selection
    #------------------------------------------------------------------------------
    if options.overwrite:
        parameters.overwrite = options.overwrite
    #end if

    #------------------------------------------------------------------------------
    # Action selection
    #------------------------------------------------------------------------------
    if options.doPSF:
        generatePSF(config, parameters, options.doPrint)
    elif options.generateTemplate:
        generateTemplate(config, parameters, options.doPrint)
    elif options.doAnneal:
        anneal(config, parameters, options.doPrint)
    elif options.doAnalyze:
        analyze(config, parameters, options.doPrint, useAnnealed = options.useAnnealed )
    elif options.doRefine:
        refine(config, parameters, options.doPrint)
    elif options.doParse:
        _results = parseRefineOutput(config, parameters, options)
    elif options.doImport:
        _mol = importFromRefine(config, parameters, project, options)
    elif options.fullAnneal:
        fullAnneal(config, parameters, project, options)
    else:
        if not options.doSetup:
            NTerror('refine.py, invalid option\n')
            return True
        else:
            NTmessage("Done after setup.")
    #end if

    if options.ipython:
        from IPython.Shell import IPShellEmbed
        ipshell = IPShellEmbed(['-prompt_in1', 'CING \#> '],
                                banner='--------Dropping to IPython--------',
                                exit_msg='--------Leaving IPython--------' )
        ipshell()
    #end if
#end def


if __name__ == '__main__':
    if run():
        NTerror("Failed refine.py")