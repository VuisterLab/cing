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
   Adding anneal.
   
Notes on usage in the READMEs here.

Other notes:
- The fullXXXXX targets will execute the doSetup. Do not specify --setup together with these targets.
- Options mostly get parsed to parameters.
- This code may best be executed from project PluginCode.xplor#fullRedo
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

TEMPLATE_FILE_NAME = 'template.pdb'
PARAMETERS_NAME = 'parameters'
PARAMETERS_FILE_NAME = '%s.py' % PARAMETERS_NAME
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

def importFrom(config, project, parameters):
    """
    Import data from parameters.basePath/XXX directory as new molecule.
    The input can be from the Refined or from the Annealed directory.

    Use parameters.bestModels or xxx 

    Will do a project level save when done successfully.
    Return Molecule or None on error
    """
    nTmessage("\n-- importFrom --")
    inPath     = config.directories.refined
    if getDeepByKeysOrAttributes( parameters, USE_ANNEALED_STR):
        inPath     = config.directories.annealed

    xplor = Xplor(config, parameters, project=project)

    bestModels = parameters.bestModels
    if getDeepByKeysOrAttributes( parameters, USE_ANNEALED_STR):
        bestModels = parameters.models    
    models = asci2list(bestModels)
    nTdebug( 'inPath:         %s' % inPath) 
    nTdebug( 'bestModels:     %s' % bestModels) 
    nTdebug( 'models:         %s' % models) 
    
    
    if len(models) == 0:
        nTerror('%s: no bestModels defined' % getCallerName())
        return
    #end if

    if not project.contentIsRestored:
        project.restore()

    # import the coordinates from Xplor PDB files
    path = xplor.joinPath(inPath, xplor.baseName)
    nTmessage('==> Importing coordinates from %s, models %s (low verbosity on later models)', path, models)
    project.molecule.initCoordinates(resetStatusObjects = True)
    for i, m in enumerate(models):
        xplorFile = sprintf(path, m)
        if not os.path.exists(xplorFile):
            nTerror('%s: model "%s" not found' % (getCallerName(), xplorFile))
            return
        #end if
        verbosity = None
        if i != 0: # Only show regular messages for first model
#            nTmessage("Setting verbosity to errors only")
            verbosity = cing.verbosityError
        if not project.molecule.importFromPDB(xplorFile, convention=XPLOR, nmodels=1, verbosity = verbosity):
            nTerror("Failed to importFromPDB from: " + getCallerName())
            return
    #end for
    project.molecule.updateAll()

    # rename the molecule if needed
    if project.molecule.name != xplor.name: # It's fine if the name already matches. Certainly the coordinates are already zipped.        
        project.molecules.rename(project.molecule.name, xplor.name)
        msg = "Renamed molecule to " + project.molecule.name
        project.addHistory(msg)
        nTmessage( msg )
    # end if        
    project.updateProject()
    nTmessage( "Molecule: %s" % project.molecule.format() )

    project.createMoleculeDirectories(project.molecule)

    if getDeepByKeysOrAttributes(parameters, 'superpose'):
        project.molecule.superpose(ranges=parameters.superpose)

#    nTmessage( "Project to save: %s" % project.format())
#    project.save()

#    project.close() # JFD: how come it gets closed but a molecule is still returned?
    return project.molecule
#end def


def doSetup(config, project, basePath, options):
    """Generate the directory setup and parameter.py file from project and basePath
       Export the data from project.
       Return parameters or None on error.
    """
    nTmessage("\n-- doSetup --")

    if os.path.exists(basePath):
        removedir(basePath)
    #end if

    xplor = Xplor(config, basePath=basePath, project=project) # generates the directories and initialize parameter setup
    
    # Set some defaults
    optionNameList = 'modelsAnneal models bestModels'.split()
    modelCount = project.molecule.modelCount
    modelsStr = '0'
    if modelCount != 1:
        modelsStr += '-%d' % (modelCount-1)
    for optionName in optionNameList:    # DEFAULT: number of molecules in current project
        xplor[ optionName ] = modelsStr
    setParametersFromOptions(project, options, xplor) # Do here for the first time and every time refine is called.
    # copy xplor parameter and topology files
    for fname in os.listdir(os.path.join(xplor.refinePath, 'toppar')):
        if not fnmatch(fname, '.*'):
#            print '>>',fname
            copy(os.path.join(xplor.refinePath, 'toppar', fname), xplor.joinPath(xplor.directories.toppar, fname))
    #print ">>", xplor

    # restore the data
#    project.restore() # JFD: why ? I get doubling of restraint lists by this.
    nTmessage(project.format())
    if project.molecule == None:
        nTerror('doSetup: No molecule defined for project %s\n', project)
        return
    #end if

    project.validateRestraints(toFile=True)

    if xplor.superpose and len(xplor.superpose) > 0:
        project.molecule.superpose(ranges=xplor.superpose)

    # export the data
#    nTmessage('\n' + dots * 10)
    nTmessage('==> Exporting %s to %s for refinement', project, basePath)

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
    # Only used for psf generation:
    xplor.baseNameByChain = project.molecule.name + '_%s_%03d.pdb'
    pathByChain = xplor.joinPath(xplor.directories.converted, xplor.baseNameByChain)
    nTmessage('==> -A- Exporting first model of %s to XPLOR PDB-files (%s)', project.molecule, pathByChain)
    project.molecule.export2xplor(pathByChain, chainName = ALL_CHAINS_STR, model = 0)
    path = xplor.joinPath(xplor.directories.converted, xplor.baseName)
    nTmessage('==> -B- Exporting all models  of %s to XPLOR PDB-files (%s)', project.molecule, path)
    project.molecule.export2xplor(path)

    
    # PSF file
    xplor.psfFile = project.molecule.name + '.psf'
    # Set the patches for the psf file
    for res in project.molecule.residuesWithProperties('HIS'):
        xplor.patchHISD.append((res.chain.name, res.resNum))
    for res in project.molecule.residuesWithProperties('HISE'):
        xplor.patchHISE.append((res.chain.name, res.resNum))
    for res in project.molecule.residuesWithProperties('cPRO'):
        xplor.patchCISP.append((res.chain.name, res.resNum))
    disulfide_bridges = project.molecule.idDisulfides(toFile=False, applyBonds=False)

    if disulfide_bridges == True:
        nTerror("Failed to analyze disulfide bridges.")
    elif disulfide_bridges:
        nTmessage("==> Located disulfide bridges %s" % str(disulfide_bridges))
    for (res1, res2) in disulfide_bridges:
        xplor.patchDISU.append( ((res1.chain.name, res1.resNum), 
                                 (res2.chain.name, res2.resNum)))

    parfile = xplor.joinPath(PARAMETERS_FILE_NAME)
    xplor.toFile(parfile)
    nTmessage("==> Saved the parameter file %s" % parfile)
#    nTmessage('\n==> Generated setup under "%s"\nEdit "%s" before continuing\n', basePath, parfile ) # Not in all setups relevant.
    return xplor
#end def


def generatePSF(config, project, parameters, doPrint=0):
    '''PSF generation'''
    nTmessage("\n-- generatePSF --")
#    models = asci2list(parameters.models)
#    pdbFile= parameters.baseName % models[0]
    psfJob = GeneratePSF(
         config,
         parameters,
#         pdbFile=pdbFile,
         project=project,
#                         outPath    = config.directories.psf,
         jobName='generatePSF'
    )
    psfJob.createScript()
    if doPrint:
        psfJob.printScript()
    #end if
    return psfJob.runScript()
#end def


def generateTemplate(config, project, parameters, doPrint=0):
    '''Extended structure generation'''
    nTmessage("\n-- generateTemplate --")
    templateJob = GenerateTemplate(
         config,
         parameters,
         project = project,
         # JFD: noting that these molecules aren't meant to be the same as the chains in a CING project. At least I'm not certain.
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

    return templateJob.runScript()
#end def


def analyze(config, project, parameters, doPrint=0 ):
    '''Analyze a run
    Returns True on failure.
    '''
    nTmessage("\n-- analyze --")         

    inPath     = config.directories.converted
    modelList  = asci2list(parameters.models)
    if getDeepByKeysOrAttributes( parameters, USE_ANNEALED_STR):
        inPath     = config.directories.annealed
        modelList  = asci2list(parameters.modelsAnneal)
        
    nTdebug( 'inPath:         %s' % inPath) 
    nTdebug( 'modelList:      %s' % modelList) 
        
    # first create the jobs, run later
    analyzeJobs = []
    for i in modelList:
        job = Analyze(
                        config,
                        parameters,
                        project = project,
                        fileNum=i,
                        molecules=[
                                      NTdict(
                                                psfFile=parameters.psfFile,
                                                pdbFile=parameters.baseName % i,
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
            nTerror("In refine#analyze failed to create at least one job's script.")
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
    nTmessage("Finished ids: %s", done_list)
    if not done_list:
        nTerror("Failed to analyze %s", i)
        return True    
#end def


def refine(config, project, parameters, doPrint=0):
    nTmessage("\n-- refine --")
    # first create the jobs, run later
    refineJobs = []
    for i in asci2list(parameters.models):
        refineJobs.append(
            WaterRefine(
                   config,
                   parameters,
                   project = project,
                   fileNum=i,
                   molecules=[
                                 NTdict(
                                    psfFile=parameters.psfFile,
                                    pdbFile=parameters.baseName % i,
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
    nTmessage("Finished ids: %s", done_list)
    if not done_list:
        nTerror("Failed to refine %s", i)
        return True
    
#end def


def anneal(config, project, parameters, doPrint=0):
    nTmessage("\n-- anneal --")
    # first create the jobs, run later
    annealJobs = []
    for i in range(parameters.modelCountAnneal):
        annealJobs.append(
            Anneal(
                   config,
                   parameters,
                   project = project,
                   fileNum=i,
                   molecules=[
                                 NTdict(
                                    psfFile=parameters.psfFile,
                                    pdbFile=parameters.baseName % i,
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
    nTmessage("Finished ids: %s", done_list)
    if not done_list:
        nTerror("Failed to anneal %s", i)
        return True
#end def


def parseOutput(config, project, parameters ):
    """
    Parse the output in the Jobs directory
    parameters is a NTxplor instance

    Return None on error or results on success.
    """
    nTmessage("\n-- parseOutput --")    

    xplor = Xplor(config, parameters, project=project, outPath=config.directories.refined)

    logFileNameFmt = 'refine_%d.log'
    resultFileName = 'parsedOutput.txt'
    bestModelsFileNameFmt = 'best%dModels.txt'
    bestModelsParameterName = 'bestModels'
    bestModels = parameters.best                    # Integer
    allPreviousModels = parameters.models           # String
    allPreviousModelCount = parameters.bestAnneal   # Integer
    
    if getDeepByKeysOrAttributes( parameters, USE_ANNEALED_STR):
        logFileNameFmt = 'anneal_%d.log'
        resultFileName = 'parsedAnnealOutput.txt'
        bestModelsFileNameFmt = 'best%dModelsAnneal.txt'
        bestModelsParameterName = 'models'
        bestModels = parameters.bestAnneal
        allPreviousModels = parameters.modelsAnneal 
        allPreviousModelCount = parameters.modelCountAnneal

    nTdebug( 'logFileNameFmt:         %s' % logFileNameFmt) 
    nTdebug( 'resultFileName:         %s' % resultFileName) 
    nTdebug( 'bestModelsFileNameFmt:  %s' % bestModelsFileNameFmt) 
    nTdebug( 'bestModelsParameterName:%s' % bestModelsParameterName) 
    nTdebug( 'bestModels:             %s (int)'     % bestModels) 
    nTdebug( 'allPreviousModels:      %s (string)"' % allPreviousModels)
    nTdebug( 'allPreviousModelCount:  %s (int)'     % allPreviousModelCount)
     
    results = NTlist()
    keys = ['model', 'Etotal', 
            'Enoe', 'NOErmsd', 'NOEnumber', 
            'NOEbound1', 'NOEviol1', 
            'NOEbound2', 'NOEviol2',
            'DIHEDrmsd', 'DIHEDnumber', 'DIHEDbound', 'DIHEDviol'
           ]
    
    # parse all output files
    for i in asci2list(allPreviousModels):

        file = xplor.checkPath(xplor.directories.jobs, logFileNameFmt % i)
        nTmessage('==> Parsing %s', file)

        data = NTdict()
        for key in keys:
            data[key] = None
        data.model = i
        
        foundEnergy = 0
        foundNOE1 = 0
        foundNOE2 = 0
        foundDIHED = 0
        awkf = AwkLike(file)
        for line in awkf:
#            nTdebug("line: %s" % line.dollar[0])
            if (not foundEnergy) and find(line.dollar[0], '--------------- cycle=     1 ----------------') >= 0:
                awkf.next()
#                nTdebug("Getting total energy from line: %s" % line.dollar[0])
                data['Etotal'] = float(line.dollar[0][11:22])

                awkf.next()
#                nTdebug("Getting NOE energy from line: %s" % line.dollar[0])
                if line.dollar[0].count("E(NOE"): # Dirty hack; use regexp next time.
#                    nTdebug("Bingo")
                    data['Enoe'] = float(line.dollar[0][68:75])
                else:
                    awkf.next()
#                    nTdebug("Getting NOE energy (try 2) from line: %s" % line.dollar[0])
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
        Etotal = getDeepByKeysOrAttributes( data, 'Etotal' )
        if Etotal == None:
            nTwarning("Failed to read energy for model: %s (probably crashed/stopped)." % i)
            continue
        results.append(data)
    #end for i

    # Since above compile might have ommissions check here how many may continue.
    resultCount = len(results)
    if allPreviousModelCount > resultCount:
        nTwarning("Will only consider %s results." %resultCount)
    elif allPreviousModelCount != resultCount:
        nTwarning("Got more results (%s) than expected input (%s). Will use all results." % (bestModels,resultCount))
    # end if
    
    # sort the results
    if parameters.sortField in keys:
#        nTdebug("Now sorting on field: %s" % parameters.sortField)
#        if 0: # The below failed at some point but is also not much in use. Removing.
#            myComp = CompareDict(parameters.sortField)
#            results.sort(myComp)
#        else:
            NTsort( results, parameters.sortField, inplace=True )            
    else:
        parameters.sortField = None
    #endif

    # print results to file and screen
    resultFile = open(xplor.joinPath(resultFileName), 'w')
    msg = '\n=== Results: sorted on "%s" ===' % parameters.sortField
    nTmessage( msg )
    fprintf(resultFile, msg + '\n')    
    fmt = '%-11s '
    for k in keys:
        nTmessageNoEOL(fmt % str(k))
        fprintf(resultFile, fmt, str(k))
    #end for
    nTmessage('')
    fprintf(resultFile, '\n')
    for data in results:
        for k in keys:
            value = val2Str(getDeepByKeysOrAttributes(data, k), fmt, count=11)
            nTmessageNoEOL(value)
            fprintf(resultFile, fmt, value)
        #end for
        nTmessage('')
        fprintf(resultFile, '\n')
    #end for
                
    # best results to put in parameter file.
    resultCountBest = min( resultCount, bestModels )      
    if resultCountBest > 0:
        msgLine = '\n=== Averages best %d models ===' % resultCountBest
        nTmessage(msgLine)
        fprintf(resultFile, msgLine + '\n' )
        for key in keys:
            getKey = Key(key)
            values = map(getKey, results[:resultCountBest])
            av, sd, dummy_n = nTaverage(values)
            msgLine = '%-12s: %10.3f +/- %-10.3f' % ( key, av, sd)
            nTmessage(msgLine)
            fprintf(resultFile, msgLine + '\n')
        #end for
        nTmessage('\n')
        fprintf(resultFile, '\n\n')

        fname = xplor.joinPath(bestModelsFileNameFmt % resultCountBest)
        f = open(fname, 'w')
        parameters[bestModelsParameterName] = ''
        for i in range(resultCountBest):
            fprintf(f, '%s/%s\n', xplor.outPath, xplor.baseName % results[i].model)
            parameters[bestModelsParameterName] = '%s%s,' % (parameters[bestModelsParameterName], results[i].model)
        #end for
        f.close()
        parameters[bestModelsParameterName] = parameters[bestModelsParameterName][:-1] # Remove trailing comma.
        nTmessage('==> Best %d models (%s) listed in %s\n', resultCountBest, parameters[bestModelsParameterName], fname)
    else:
        parameters[bestModelsParameterName] = allPreviousModels
    #end if
    resultFile.close()
    parameters.toFile(xplor.joinPath(PARAMETERS_FILE_NAME))
    return results
#end def

def fullAnnealAndRefine( config, project, options ):
    """
    Calling fullAnneal and then fullRefine
    Return None on error or parameters on success.        
    """
    nTmessage("\n-- %s --" % getCallerName())   
 
    options.fullAnnealAndRefine = True # Might have been set before but e.g. not from PluginCode.        

    parameters = fullAnneal(config, project, options)
    if not parameters:
        nTerror("Failed fullAnneal")
        return
    # end if

#    nTdebug("-- Calling fullRefine --")
    parameters = fullRefine(config, project, parameters, options)
    if not parameters:
        nTerror("Failed fullRefine")
        return
    # end if
    return parameters
#end def

def fullRefine( config, project, parameters, options ):
    """
    Refine the coordinates and process them back into CING.
    Return None on error or parameters on success.
    
       
    """
    nTmessage("\n-- %s --" % getCallerName())
    refinePath = project.path(project.directories.refine )
    nTmessage('==> refinePath: %s', refinePath)
    basePath = os.path.join( refinePath, options.name)
    nTmessage('==> basePath: %s', basePath)
    nTdebug('==> options: %s' % str(options))
    
    
    if parameters:
        nTdebug("Using previously provided parameters.")
    else:
        parameters = doSetup(config, project, basePath, options)
        if not parameters:
            nTerror("Failed setup")
            return
        # end if        
    # end if
    
    # Since the original options might have been to use Annealed this might need to be disabled.
    parameters[ USE_ANNEALED_STR ] = False

    targetListStr = "generatePSF, analyze, and parseOutput"
    if not options.fullRefine:
        nTmessage("Skipping %s, and jump straight into refine now." % targetListStr)
    else:
        nTmessage("Doing %s, before starting refine." % targetListStr)
        if generatePSF(config, project, parameters):
            nTerror("Failed generatePSF")
            return
        # end if
        if analyze(config, project, parameters):
            nTerror("Failed analyze")
            return
        # end if
        if not parseOutput(config, project, parameters):
            nTerror("Failed parseOutput")
            return
        # end if        
    # end if
    
    if refine(config, project, parameters ):
        nTerror("Failed refine")
        return
    # end if

    if not parseOutput(config, project, parameters):
        nTerror("Failed parseOutput")
        return
    # end if

    if not importFrom(config, project, parameters):
        nTerror("Failed importFrom")
        return
    # end if
    return parameters
# end def


def fullAnneal( config, project, options  ):
    """
    Recalculate the coordinates.
    Return None on error or parameters on success.    
    """

    nTmessage("\n-- %s --" % getCallerName())
    refinePath = project.path(project.directories.refine )
    nTmessage('==> refinePath: %s', refinePath)
    basePath = os.path.join( refinePath, options.name)
    nTmessage('==> basePath: %s', basePath)
    nTdebug('==> options: %s' % str(options))

    parameters = doSetup(config, project, basePath, options)
    if not parameters:
        nTerror("Failed setup")
        return
    # end if
    
    if generatePSF(config, project, parameters):
        nTerror("Failed generatePSF")
        return
    # end if
    if generateTemplate(config, project, parameters):
        nTerror("Failed generateTemplate")
        return
    # end if
    if anneal(config, project, parameters):
        nTerror("Failed anneal")
        return
    # end if
    parameters[ USE_ANNEALED_STR ] = True
    if analyze(config, project, parameters):
        nTerror("Failed analyze")
        return
    # end if
    if not parseOutput(config, project, parameters):
        nTerror("Failed parseOutput")
        return
    # end if
    if options.fullAnnealAndRefine:
        nTmessage("Skipping parseOutput and importFrom because we'll jump straight into refine now.")
        return parameters
    # end if    
    if not importFrom(config, project, parameters):
        nTerror("Failed importFrom")
        return
    # end if
    return parameters
#end def


def run():
    parser = getRefineParser()
    (options, _args) = parser.parse_args()

    if options.verbosity >= 0 and options.verbosity <= 9:
        cing.verbosity = options.verbosity
    else:
        nTerror("set verbosity is outside range [0-9] at: " + options.verbosity)
        nTerror("Ignoring setting")
    # end if
    # From this point on code may be executed that will go through the appropriate verbosity filtering
    nTdebug("options: %s" % str(options))


    #------------------------------------------------------------------------------
    # Documentation
    #------------------------------------------------------------------------------
    if options.doc:
        parser.print_help(file=sys.stdout)
        nTmessage("%s\n", __doc__)
        return
    #end if

    #------------------------------------------------------------------------------
    #check for the required project, name option
    parser.check_required('--name')
    parser.check_required('--project')

    project = Project.open(options.project, status='old',
                           restore=1) #DEFAULT 0
    if project == None:
        nTerror("Failed to get a project")
        return True
    #end if
    basePath = project.path(project.directories.refine, options.name)
#    nTdebug("basePath: " + basePath)
    #------------------------------------------------------------------------------
    # Setup
    #------------------------------------------------------------------------------
    parameters = None
    if options.doSetup:
        parameters = doSetup(config, project, basePath, options)
#        return # We had like to continue in new setup. So don't exit here.
    #end if

    #------------------------------------------------------------------------------
    # Some output
    #------------------------------------------------------------------------------
    nTmessage("==> Reading configuration")
    nTmessage('refinePath:     %s', config.refinePath)
    nTmessage('xplor:          %s', config.XPLOR)
    nTmessage("parameterFiles: %s", config.parameterFiles)
    nTmessage("topologyFiles:  %s", config.topologyFiles)

    if ( options.fullRefine or options.fullAnneal or options.fullAnnealAndRefine):
        if options.doSetup:
            nTerror("Setup was done but fullXXX would do it again. Just run fullXXXX again without setup please.")
            sys.exit(1)
        pass
    else:
        #------------------------------------------------------------------------------
        # read parameters file
        #------------------------------------------------------------------------------
        if not parameters:
#            nTdebug('==> will read parameters')
            parameters = getParameters( basePath, 'parameters')    
        #    nTdebug('==> parameters\n%s\n', str(parameters))
            nTmessage('==> Read parameters')
        # end if    
        setParametersFromOptions(project, options, parameters) # Do here for the first time and every time refine is called.
        nTmessage('==> Done transferring some options from commandline to parameters (again)')
        
        parameters.basePath = basePath
        if parameters.name != options.name:
            nTwarning("parameters.name (%s) != options.name (%s)" % ( parameters.name, options.name) )
        # end if
    # end if
    
    #------------------------------------------------------------------------------
    # Action selection
    #------------------------------------------------------------------------------
    if options.doPSF:
        generatePSF(config, project, parameters, options.doPrint)
    elif options.generateTemplate:
        generateTemplate(config, project, parameters, options.doPrint)
    elif options.doAnneal:
        anneal(config, project, parameters, options.doPrint)
    elif options.doAnalyze:
        analyze(config, project, parameters, options.doPrint )
    elif options.doRefine:
        refine(config, project, parameters, options.doPrint)
    elif options.doParse:
        _results = parseOutput(config, project, parameters)
    elif options.doImport:
        importFrom(config, project, parameters)
    elif options.fullAnneal:
        if not fullAnneal(config, project, options):
            nTerror("Failed fullAnneal")
    elif options.fullRefine:
        if not fullRefine(config, project, parameters, options):
            nTerror("Failed fullRefine")
    elif options.fullAnnealAndRefine:
        if not fullAnnealAndRefine( config, project, options):
            nTerror("Failed fullAnnealAndRefine")
    else:
        if not options.doSetup:
            nTerror('refine.py, invalid options combinations:\n%s' % str(options))
            return True
        else:
            nTmessage("Done after setup.")
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
        nTerror("Failed refine.py")