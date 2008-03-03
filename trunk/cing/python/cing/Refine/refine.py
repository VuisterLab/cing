#!/usr/bin/env python
"""
#------------------------------------------------------------------------------

 refine.py
 
 GWV 23 February/March 2005: water refinement
 GWV March 2007: Adapted for usage with cing
 - Model indices [0,Nmodels>
 - General directory structure using --setup
 - Inclusion of parsing of refine result using --parse

#------------------------------------------------------------------------------
"""
from cing.Libs.AwkLike import AwkLike
from cing.Libs.NTutils import NTaverage
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import OptionParser
from cing.Libs.NTutils import asci2list
from cing.Libs.NTutils import fprintf
from cing.Libs.NTutils import removedir
from cing.Libs.disk import copy
from cing.Refine import config
from cing.Refine.NTxplor import Analyze
from cing.Refine.NTxplor import GeneratePSF
from cing.Refine.NTxplor import WaterRefine
from cing.Refine.NTxplor import Xplor
from cing.Refine.config import refConfig
from cing.Refine.parameters import params
from cing.core.classes import Project
from cing.core.constants import XPLOR
from string import find
import os
import sys


#------------------------------------------------------------------------------
def doSetup( config, basename ):
    """Generate the directory setup from basename
    """           
    if os.path.exists( basename ): 
        removedir( basename )
    
    #end if
    for dir in config.directories.values():
        os.makedirs( os.path.join( basename, dir ) )
    #end for
    parfile = os.path.join( basename, 'parameters.py' )
    copy( os.path.join( config.refinePath, 'parameters.py'), parfile )
    NTmessage('==> Generated setup under "%s"\nEdit "%s" before continuing',
              basename, parfile
             )
#end def

#------------------------------------------------------------------------------
def generatePSF( config, params, doPrint = 0 ):

    # PSF generation
    psfJob = GeneratePSF(
                         config,
                         params,
#                         inPath     = config.directories.converted,
                         pdbFile    = params.baseName % params.models[0],
                         jobName    = 'generatePSF',

                        )

    psfJob.createScript()
    if doPrint:
        psfJob.printScript()
    #end if
    psfJob.runScript()
#end def

#------------------------------------------------------------------------------
def analyze( config, params, doPrint = 0 ):
    # first create the jobs, run later    
    analyzeJobs = []
    for i in params.models:
        job = Analyze(
                        config,
                        params,
                        fileNum    = i,                        
                        molecules  = [
                                      NTdict(   psfFile        = params.psfFile,
                                                pdbFile        = params.baseName % i,
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
        job.createScript()
        if doPrint:
            job.printScript()
        #end if
        job.runScript()
    #end for
#end def

        
#------------------------------------------------------------------------------
def refine( config, params, doPrint = 0 ):

    # first create the jobs, run later    
    refineJobs = []
    for i in params.models:
        refineJobs.append(
            WaterRefine(
                   config,
                   params,                  
                   fileNum    = i,
                   molecules  = [
                                 NTdict(
                                    psfFile        = params.psfFile,
                                    pdbFile        = params.baseName % i,
                                    selectionCode  = '(not resn TIP3 and not resn ANI)'
                                 ),
                                ],
#                   inPath     = config.directories.analyzed,
#                   outPath    = config.directories.refined,
                   jobName    = 'refine_%d' % i,       
            )
        )

    for job in refineJobs:
        job.createScript()
        if doPrint:
            job.printScript()
        job.runScript()

#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Parsing code    
#------------------------------------------------------------------------------
 
def parseRefineOutput( params, options ):

    params.setdefault( 'outPath', params.directories.refined )
    results = NTlist()
    
    # parse all output files   
    for i in params.models:
        
        file = params.checkPath( params.directories.jobs, 'refine_%d.log'%i )
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
    resultFile = open( params.joinPath('parsedOutput.txt'), 'w' )
    NTmessage('\n=== Results: sorted on "%s" ===', options.sortField)
    fprintf(resultFile, '=== Results: sorted on "%s" ===\n', options.sortField)
    fmt = '%-10s '
    for k in keys:
        NTmessage( fmt, str(k))
        fprintf( resultFile, fmt, str(k))
    #end for
    NTmessage('')
    fprintf(resultFile,'\n')
    for data in results:
        for k in keys:
            if k in data:
                NTmessage(fmt, str(data[k]))
                fprintf(resultFile, fmt, str(data[k]))
            else:
                NTmessage(fmt, '-')
                fprintf( resultFile, fmt, '-')
        #end for
        NTmessage('')
        fprintf(resultFile,'\n')
    #end for

    # best results
    bestModels = int(options.bestModels)
    if bestModels > 0:
        NTmessage('\n=== Averages best %d models ===', bestModels)
        fprintf( resultFile, '\n=== Averages best %d models ===\n', bestModels)
        for key in keys:
            getKey = Key( key )
            values = map( getKey, results )
            av,sd,_n = NTaverage( values )
            NTmessage('%-12s: %10.3f +/- %-10.3f', key, av, sd )
            fprintf(resultFile,'%-12s: %10.3f +/- %-10.3f\n', key, av, sd )
        #end for
        NTmessage('\n')
        fprintf(resultFile, '\n\n')

        fname = params.joinPath('best%dModels.list' % bestModels)
        f = open( fname, 'w')
        for i in range(0, bestModels):
            fprintf(f, '%s/%s\n', params.outPath, params.baseName % results[i].model )
        #end for
        f.close()
        NTmessage('==> Best %d models listed in %s', bestModels, fname )
    #end if  
    
    resultFile.close()
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

    version = "0.481 alpha"
    usage   = "usage: refine.py [options]"

    parser = OptionParser(usage=usage, version=version)
    parser.add_option("--doc", 
                      action="store_true", 
                      dest ="doc", default=False,
                      help="print extended documentation to stdout"
                     )
    parser.add_option("-n", "--name", 
                      dest="name", default=None,
                      help="NAME of the refinement run (required)", 
                      metavar="NAME"
                     )
    parser.add_option("--project", 
                      dest="project", default=None,
                      help="Cing project name; data will be in PROJECT/Refine/NAME", 
                      metavar="PROJECT"
                     )
    parser.add_option("-s", "--setup",
                      action="store_true", 
                      dest="doSetup", default=False,
                      help="Generate directory structure and parameter file",
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
                     
    (options, args) = parser.parse_args()
    
    
    #------------------------------------------------------------------------------
    # Documentation
    #------------------------------------------------------------------------------
    if options.doc:
        parser.print_help(file=sys.stdout)
        NTmessage("%s", __doc__ )
        sys.exit(0)
    #end if
    
    #------------------------------------------------------------------------------
    #check for the required name option  
    parser.check_required('-n')
        
    
    NTmessage("-------------------------------------------------------------------------------------------------------")
    NTmessage("     Refine version %s", version)
    NTmessage("-------------------------------------------------------------------------------------------------------")
    
    #------------------------------------------------------------------------------
    # Project
    #------------------------------------------------------------------------------
    project = None
    if options.project:
        project = Project.open(options.project, status = 'old', restore=False)   
        if project==None:
            NTerror("Failed to get a project") 
            sys.exit(1)
        # modify the basePath
        options.name = project.path( project.directories.refine, options.name )
    #end if
    
    #------------------------------------------------------------------------------
    # Setup
    #------------------------------------------------------------------------------
    if options.doSetup:
        doSetup( config, options.name )
        NTdebug("done with refine.doSetup now doing a system exit")
        sys.exit(0)
    #end if
    
    #------------------------------------------------------------------------------
    # Some output
    #------------------------------------------------------------------------------
    NTmessage("==> Reading configuration")
    NTmessage('refinePath:    %s', config.refinePath )
    NTmessage('xplor:         %s', XPLOR )
    for pfile in refConfig.parameterFiles:
        NTmessage("parameterFile: %s", pfile)
    for tfile in refConfig.topologyFiles:
        NTmessage("topologyFile:  %s", tfile)
    
    #------------------------------------------------------------------------------
    # read parameters file
    #------------------------------------------------------------------------------
    paramfile = os.path.join( options.name, 'parameters.py' )
    execfile( paramfile )
    NTmessage('==> Read user parameters %s',  paramfile)
    params.basePath = options.name
    
    #------------------------------------------------------------------------------
    # Model selection
    #------------------------------------------------------------------------------
    if options.models:
        params.models = asci2list( options.models )
    #end if
    
    #------------------------------------------------------------------------------
    # Action selection
    #------------------------------------------------------------------------------
    if options.doPSF:
        generatePSF( config, params, options.doPrint )
        
    elif options.doAnalyze:
        analyze( config, params, options.doPrint )
    
    elif options.doRefine:
        refine( config, params, options.doPrint )
    
    elif options.doParse:
        results = parseRefineOutput( Xplor(config, params), options )
    
    else:
        NTerror('Error: refine.py, invalid option\n')
    #end if
    
    
    
