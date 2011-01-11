#!/usr/bin/env python
"""
#------------------------------------------------------------------------------

 refine.py

 GWV 23 February/March 2005: water refinement
 GWV March 2007: Adapted for usage with cing
 - Model indices [0,Nmodels>
 - General directory structure using --setup
 - Inclusion of parsing of refine result using --parse
 GWV April 2008: version 0.70
 - Modified --setup: full export to refine directories; automated generation
   of parameters file
 - Import into cing (version >= 0.70);

#------------------------------------------------------------------------------
"""
from Refine.NTxplor    import Analyze
from Refine.NTxplor    import GeneratePSF
from Refine.NTxplor    import WaterRefine
from Refine.NTxplor    import Xplor
from Refine.NTxplor    import refineDihedralParameters
from Refine.NTxplor    import refineNoeParameters
from Refine.NTxplor    import refineParameters #@UnusedImport
from Refine.configure  import config
from cing import cingRevision
from cing.Libs.AwkLike import AwkLike
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.disk    import copy
from cing.core.classes import Project
from cing.core.constants import * #@UnusedWildImport
#from cing.core.molecule import mapMolecules #@UnusedImport

def importFromRefine( config, params, project ):
    """
    Import data from params.basePath/Refined directory as new molecule
    Use params.bestModels

    Return Molecule or None on error
    """

    xplor = Xplor( config, params )

    models=asci2list( xplor.bestModels )
    if len(models) == 0:
        NTerror('moleculeFromRefine: no bestModels defined\n')
        return None
    #end if

    project.restore()

    # import the coordinates from Xplor PDB files
    path = xplor.joinPath( xplor.directories.refined, xplor.baseName )
    NTmessage('==> Importing coordinates from %s, models %s', path, models)
    project.molecule.initCoordinates()
    for m in models:
        xplorFile = sprintf(path, m)
        if not os.path.exists( xplorFile ):
            NTerror('importFromRefine: model "%s" not found\n', xplorFile)
            continue
        #end if
        project.molecule.importFromPDB( xplorFile, convention=XPLOR, nmodels=1)
    #end for
    project.molecule.updateAll()

    # rename the molecule
    project.molecules.rename(project.molecule.name, xplor.name)
    print project.molecule.format()

    if 'superpose' in xplor and len(xplor.superpose) > 0:
        project.molecule.superpose( ranges = xplor.superpose )

    print project.format()

    project.close()
#end def


def doSetup( config, project, basePath, options ):
    """Generate the directory setup and parameter.py file from project and basePath
       Export the data from project
    """

    if os.path.exists( basePath ):
        removedir( basePath )
    #end if

    xplor = Xplor( config, basePath = basePath ) # generates the directories and initialize parameter setup

    # copy xplor parameter and topology files
    for fname in os.listdir(os.path.join(xplor.refinePath,'toppar')):
        if not fnmatch(fname,'.*'):
#            print '>>',fname
            copy( os.path.join(xplor.refinePath,'toppar', fname), xplor.joinPath( xplor.directories.toppar, fname ) )
    #print ">>", xplor

    # restore the data
    project.restore()
    NTmessage(project.format())
    if project.molecule == None:
        NTerror('doSetup: No molecule defined for project %s\n', project )
        sys.exit(1)
    #end if

    project.validateRestraints( toFile=True )

    if options.superpose and len(options.superpose) > 0:
        xplor.superpose = options.superpose
        project.molecule.superpose( ranges = xplor.superpose )

    # export the data
    NTmessage('\n' + dots*10 )
    NTmessage(   '==> Exporting %s to %s for refinement\n', project, basePath )

    for drl in project.distances:
        drl.renameToXplorCompatible()
        xplor.noeRestraints.append( refineNoeParameters( drl.name ) )
        fname = xplor.joinPath( xplor.directories.tables, drl.name +'.tbl' )
        drl.export2xplor( fname )
    #end for

    for drl in project.dihedrals:
        drl.renameToXplorCompatible()
        xplor.dihedralRestraints.append( refineDihedralParameters( drl.name ) )
        fname = xplor.joinPath( xplor.directories.tables, drl.name +'.tbl' )
        drl.export2xplor( fname )
    #end for

    # export structures in Xplor-PDB format
    xplor.baseName = project.molecule.name + '_%03d.pdb'
    path = xplor.joinPath( xplor.directories.converted, xplor.baseName )
    NTmessage('==> Exporting %s to XPLOR PDB-files (%s)', project.molecule, path)
    project.molecule.export2xplor( path)
    xplor.models     = sprintf('%d-%d', 0, project.molecule.modelCount-1)
    xplor.bestModels = sprintf('%d-%d', 0, project.molecule.modelCount-1)
    #TODO
    #xplor.superpose  = sprintf('%d-%d', 0, project.molecule.modelCount-1)

    # PSF file
    xplor.psfFile = project.molecule.name +'.psf'
    # Set the patches for the psf file
    for res in project.molecule.residuesWithProperties('HIS'):
        xplor.patchHISD.append( res.resNum )
    for res in project.molecule.residuesWithProperties('HISE'):
        xplor.patchHISE.append( res.resNum )
    for res in project.molecule.residuesWithProperties('cPRO'):
        xplor.patchCISP.append( res.resNum )
    disulfide_bridges = []
    for res in project.molecule.residuesWithProperties('CYSS'):
        if res in disulfide_bridges:
            continue
#        TODO
    for (res1,res2) in disulfide_bridges:
        xplor.patchDISN.append( (res1.resNum,res2.resNum) )


    # save the parameterfile
    parfile = xplor.joinPath( 'parameters.py' )
    xplor.toFile( parfile )

    NTmessage('\n==> Generated setup under "%s"\nEdit "%s" before continuing\n',
              basePath, parfile
             )
#end def


def generatePSF( config, params, doPrint = 0 ):
    '''PSF generation'''
    NTmessage("Generating .psf file for xplor")
    models = asci2list(params.models)
    psfJob = GeneratePSF(
         config,
         params,
#                         inPath     = config.directories.converted,
         pdbFile    = params.baseName%models[0],
         jobName    = 'generatePSF'
    )
    psfJob.createScript()
    if doPrint:
        psfJob.printScript()
    #end if
    psfJob.runScript()
#end def


def analyze( config, params, doPrint = 0 ):
    '''Analyze a run
    Returns True on failure.
    '''
    NTmessage("Analyzing a run")

    # first create the jobs, run later
    analyzeJobs = []
    for i in asci2list( params.models ):
        job = Analyze(
                        config,
                        params,
                        fileNum    = i,
                        molecules  = [
                                      NTdict(
                                                psfFile        = params.psfFile,
                                                pdbFile        = params.baseName%i,
                                                selectionCode  = '(not resn TIP3 and not resn ANI)'
                                  ),
                         ],
#                         inPath     = config.directories.converted,
#                         outPath    = config.directories.analyzed,
                        jobName    = 'analyze_%d'%i,
                     )

        analyzeJobs.append( job )
    #end for


    for job in analyzeJobs:
        if job.createScript():
            NTerror("In refine#analyze failed to create at least one job's script.")
            return True
        if doPrint:
            job.printScript()
        #end if
        job.runScript()
    #end for
#end def


def refine( config, params, doPrint = 0 ):

    # first create the jobs, run later
    refineJobs = []
    for i in asci2list( params.models ):
        refineJobs.append(
            WaterRefine(
                   config,
                   params,
                   fileNum    = i,
                   molecules  = [
                                 NTdict(
                                    psfFile        = params.psfFile,
                                    pdbFile        = params.baseName%i,
                                    selectionCode  = '(not resn TIP3 and not resn ANI)'
                                 ),
                                ],
#                   inPath     = config.directories.analyzed,
#                   outPath    = config.directories.refined,
                   jobName    = 'refine_%d'%i,
            )
        )

    for job in refineJobs:
        job.createScript()
        if doPrint:
            job.printScript()
        job.runScript()
    #end for
#end def


def parseRefineOutput( config, params, options ):
    """
    Parse the output in the Jobs directory
    params is a NTxplor instance

    """

    xplor = Xplor( config, params, outPath = config.directories.refined )

    results = NTlist()
    # parse all output files
    for i in asci2list( params.models ):

        file = xplor.checkPath( xplor.directories.jobs, 'refine_%d.log'%i )
        NTmessage('==> Parsing %s', file )

        data = NTdict( fileName = file,
                         model = i
                       )
        foundEnergy = 0
        foundNOE1 = 0
        foundNOE2 = 0
        foundDIHED = 0
        awkf = AwkLike( file )
        for line in awkf:
            if (not foundEnergy) and find(line.dollar[0],'--------------- cycle=     1 ----------------') >= 0:
                awkf.next()
                data['Etotal'] =  float( line.dollar[0][11:22] )

                awkf.next()
                awkf.next()
                data['Enoe'] = float( line.dollar[0][68:75] )
                foundEnergy = 1

            elif (not foundNOE1) and find(line.dollar[0], 'NOEPRI: RMS diff. =') >= 0:
                data['NOErmsd'] = float( line.dollar[5][:-1] )
                data['NOEbound1'] = float( line.dollar[7][:-2] )
                data['NOEviol1'] = int( line.dollar[8] )
                foundNOE1 = 1

            elif (not foundNOE2) and find(line.dollar[0], 'NOEPRI: RMS diff. =') >= 0:
                data['NOEbound2'] = float( line.dollar[7][:-2] )
                data['NOEviol2'] = int( line.dollar[8] )
                data['NOEnumber'] = float( line.dollar[10] )
                foundNOE2 = 1

            elif (not foundDIHED) and find(line.dollar[0],'Number of dihedral angle restraints=') >= 0:
                data['DIHEDnumber'] = int( line.dollar[6] )
                awkf.next()
                data['DIHEDbound'] = float( line.dollar[6][:-1] )
                data['DIHEDviol'] = int( line.dollar[7] )
                awkf.next()
                data['DIHEDrmsd'] = float( line.dollar[3] )
                foundDIHED = 1
            #endif

        #end for

        results.append( data )
    #end for

    keys = ['model', 'Etotal','Enoe','NOErmsd','NOEnumber', 'NOEbound1',
            'NOEviol1', 'NOEbound2', 'NOEviol2',
            'DIHEDrmsd','DIHEDnumber', 'DIHEDbound', 'DIHEDviol'
           ]

    # sort the results
    if options.sortField in keys:
        myComp = CompareDict( options.sortField )
        results.sort( myComp )
    else:
        options.sortField = None
    #endif

    # print results to file and screen
    resultFile = open( xplor.joinPath('parsedOutput.txt'), 'w' )
    printf('\n=== Results: sorted on "%s" ===\n', options.sortField)
    fprintf(resultFile, '=== Results: sorted on "%s" ===\n', options.sortField)
    fmt = '%-10s '
    for k in keys:
        printf( fmt, str(k))
        fprintf( resultFile, fmt, str(k))
    #end for
    printf('\n')
    fprintf(resultFile,'\n')
    for data in results:
        for k in keys:
            if k in data:
                printf(fmt, str(data[k]))
                fprintf(resultFile, fmt, str(data[k]))
            else:
                printf(fmt, '-')
                fprintf( resultFile, fmt, '-')
        #end for
        printf('\n')
        fprintf(resultFile,'\n')
    #end for

    # best results
    bestModels = int(options.bestModels)
    if bestModels > 0:
        printf('\n=== Averages best %d models ===\n', bestModels)
        fprintf( resultFile, '\n=== Averages best %d models ===\n', bestModels)
        for key in keys:
            getKey = Key( key )
            values = map( getKey, results )
            av,sd,dummy_n = NTaverage( values )
            printf('%-12s: %10.3f +/- %-10.3f\n', key, av, sd )
            fprintf(resultFile,'%-12s: %10.3f +/- %-10.3f\n', key, av, sd )
        #end for
        printf('\n\n')
        fprintf(resultFile, '\n\n')

        fname = xplor.joinPath( 'best%dModels.txt' % bestModels )
        f = open( fname, 'w')
        params.bestModels = ''
        for i in range(0, bestModels):
            fprintf(f, '%s/%s\n', xplor.outPath, xplor.baseName % results[i].model )
            params.bestModels = sprintf('%s%s,', params.bestModels, results[i].model )
        #end for
        f.close()
        params.bestModels = params.bestModels[:-1]
        NTmessage('==> Best %d models listed in %s\n', bestModels, fname )
    else:
        params.bestModels = params.models
    #end if

    resultFile.close()
    params.toFile( xplor.joinPath( 'parameters.py' ) )

    #print '>>>'
    #print xplor.format( params.__FORMAT__ )

    return results
#end def
#------------------------------------------------------------------------------

# class wrapper to allow passing of key-argument
# to compare dict function
class CompareDict:
    def __init__( self, key ):
        self.key = key
    #end def

    def __call__( self, a, b ):
        return cmp( a[self.key], b[self.key] )
    #end def
#end class

# class wrapper to allow passing of a key-argument
# to dict entry
class Key:
    def __init__( self, key ):
        self.key = key
    #end def

    def __call__( self, a ):
        return a[self.key]
    #end def
#end class


#------------------------------------------------------------------------------
## main section
#------------------------------------------------------------------------------
if __name__ == '__main__':

    version = cing.cingVersion
    usage   = "usage: refine.py [options]"

    parser = OptionParser(usage=usage, version=version)
    parser.add_option("--doc",
                      action="store_true",
                      dest ="doc", default=False,
                      help="print extended documentation to stdout"
                     )
    parser.add_option("--project",
                      dest="project", default=None,
                      help="Cing project name (required); data will be in PROJECT.cing/Refine/NAME",
                      metavar="PROJECT"
                     )
    parser.add_option("--name",
                      dest="name", default=None,
                      help="NAME of the refinement run (required)",
                      metavar="NAME"
                     )
    parser.add_option("-s", "--setup",
                      action="store_true",
                      dest="doSetup", default=False,
                      help="Generate directory structure, parameter file, export project data",
                     )
    parser.add_option("-f", "--psf",
                      action="store_true",
                      dest="doPSF", default=False,
                      help="Generate PSF file (default: no PSF)"
                     )
    parser.add_option("-a", "--analyze",
                      action="store_true",
                      dest="doAnalyze", default=False,
                      help="Initial analysis (default: no analysis)"
                     )
    parser.add_option("-r", "--refine",
                      action="store_true",
                      dest="doRefine", default=False,
                      help="Refine the structures (default: no refine)"
                     )
    parser.add_option("-p", "--print",
                      action="store_true",
                      dest="doPrint", default=False,
                      help="Print script before running (default: no print)"
                     )
    parser.add_option("--models",
                      dest="models", default=None,
                      help="Model indices (e.g. 0,2-5,7,10-13)",
                      metavar="MODELS"
                     )
    parser.add_option("--overwrite",
                      action="store_true",
                      dest="overwrite", default=False,
                      help="Overwrite existing files (default: from parameters.py)"
                     )
    parser.add_option("--parse",
                      action="store_true",
                      dest="doParse", default=False,
                      help="Parse the output of the refine run (default: no parse)"
                     )
    parser.add_option("--sort",
                      dest="sortField", default=None,
                      help="sort field for parse option",
                      metavar="SORTFIELD"
                     )
    parser.add_option("--best",
                      dest="bestModels", default=0,
                      help="Number of best models for parse option",
                      metavar="BESTMODELS"
                     )
    parser.add_option("--import",
                      action="store_true",
                      dest="doImport", default=False,
                      help="Import the best models from PROJECT.cing/Refine/NAME/Refined (default: no import)"
                     )
    parser.add_option("--superpose",
                      dest="superpose", default=None,
                      help="superpose ranges; e.g. 503-547,550-598,800,801",
                      metavar="SUPERPOSE"
                     )
    parser.add_option("-v", "--verbosity", type='int',
                      default=cing.verbosityDefault,
                      dest="verbosity", action='store',
                      help="verbosity: [0(nothing)-9(debug)] no/less messages to stdout/stderr (default: 3)"
                     )
    parser.add_option("--ipython",
                      action="store_true",
                      dest="ipython",
                      help="Start ipython interpreter"
                     )

    (options, args) = parser.parse_args()

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
        NTmessage("%s\n", __doc__ )
        sys.exit(0)
    #end if

    #------------------------------------------------------------------------------
    #check for the required project, name option
    parser.check_required('--name')
    parser.check_required('--project')

    NTmessage(dots*10+"\n")
    versionStr = "     Refine version %s" % version
    if cingRevision:
        versionStr += " (r%d)" % cingRevision
    NTmessage(versionStr)
    NTmessage("\n"+dots*10+"\n")

    #------------------------------------------------------------------------------
    # Project
    #------------------------------------------------------------------------------
    project = Project.open(options.project, status = 'old', restore=False )
    if project==None:
        NTerror("Failed to get a project")
        sys.exit(1)
    #end if
    basePath = project.path( project.directories.refine, options.name )

    #------------------------------------------------------------------------------
    # Setup
    #------------------------------------------------------------------------------
    if options.doSetup:
        doSetup( config, project, basePath, options )
        sys.exit(0)
    #end if

    #------------------------------------------------------------------------------
    # Some output
    #------------------------------------------------------------------------------
    NTmessage("==> Reading configuration")
    NTmessage('refinePath:     %s', config.refinePath )
    NTmessage('xplor:          %s', config.XPLOR )
    NTmessage("parameterFiles: %s", config.parameterFiles )
    NTmessage("topologyFiles:  %s", config.topologyFiles )

    #------------------------------------------------------------------------------
    # read parameters file
    #------------------------------------------------------------------------------
    parameters = None #@UndefinedVariable dummy for pydev extensions code analysis
    paramfile = project.path( project.directories.refine, options.name, 'parameters.py' )
    execfile( paramfile )
    NTmessage('==> Read user parameters %s\n',  paramfile)
    parameters.basePath = basePath
    parameters.name     = options.name

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
        generatePSF( config, parameters, options.doPrint )

    elif options.doAnalyze:
        analyze( config, parameters, options.doPrint )

    elif options.doRefine:
        refine( config, parameters, options.doPrint )

    elif options.doParse:
        results = parseRefineOutput(  config, parameters, options )

    elif options.doImport:
        mol = importFromRefine( config, parameters, project )
    else:
        NTerror('refine.py, invalid option\n')

    #end if
    #------------------------------------------------------------------------------------
    # ipython
    #------------------------------------------------------------------------------------
    if options.ipython:
        from IPython.Shell import IPShellEmbed
        ipshell = IPShellEmbed(['-prompt_in1','CING \#> '],
                                banner='--------Dropping to IPython--------',
                                exit_msg='--------Leaving IPython--------'
                              )
        ipshell()
    #end if



