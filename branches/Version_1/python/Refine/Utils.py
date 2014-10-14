'''
Created on May 2, 2011

@author: jd
'''
from Refine.NTxplor import * #@UnusedWildImport
from Refine.constants import *
from cing.Libs.NTutils import * #@UnusedWildImport

def getParameters( basePath, extraModuleName):
    paramfile = os.path.join(basePath, '%s.py' % extraModuleName)
    if not os.path.exists(paramfile):
        nTerror("Failed to find: %s" % paramfile)
        return

    if 0:
        execfile_(paramfile, globals()) # Standard execfile fails anyhow for functions and is obsolete in Python 3
    if 1: # Less preferred to change sys.path and also fails in some situations.
    #    parameters = refineParameters()
    #    del parameters
        if basePath in sys.path:
            nTdebug("Skipping add since path is already present.")
        else:
            sys.path.insert(0, basePath)
        # end if
    #    nTmessage('sys.path:\n%s' % str(sys.path))
    #    nTmessage('==> Reading user parameters %s', paramfile)
    #    g = globals()
    #    nTmessage("g: %s" % g)
    #    l = locals()
    #    nTmessage("l: %s" % l)
    #    parameters  = refineParameters #@UnusedVariable
    #    _temp = __import__(extraModuleName, globals(), locals(), [], -1)
#        _temp = __import__(extraModuleName, globals())
        _temp = __import__(extraModuleName, fromlist=['parameters'])
    #    _temp = __import__(extraModuleName)
        parameters = _temp.parameters
    # end if

    if not 'parameters' in locals():
        nTerror("Failed sanity check: The variable name 'parameters' should exist in the local scope.")
        return

    if not hasattr( parameters, 'ncpus'): #@UndefinedVariable
        nTerror("Failed sanity check: parameters should have a 'ncpus' attribute.")
        return

#    nTdebug('==> parameters\n%s\n', str(parameters))
    return parameters

def getRefineParser():
    parser = OptionParser(usage="usage: refine.py [options]")
    parser.add_option("--doc",
                      action="store_true",
                      dest="doc", default=False,
                      help="print extended documentation to stdout"
                     )
    parser.add_option("--project",
                      dest="project", default=None,
                      help="Cing project name (required); data will be in PROJECT.cing/Refine/NAME",
                      metavar="PROJECT"
                     )
    parser.add_option("-n", "--name",
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
    parser.add_option("-g", "--generateTemplate",
                      action="store_true",
                      dest="generateTemplate", default=False,
                      help="Generate template PDB file (default: no PSF)"
                     )

    parser.add_option("-a", "--analyze",
                      action="store_true",
                      dest="doAnalyze", default=False,
                      help="Initial analysis (default: no analysis)"
                     )
    parser.add_option("-u", "--useAnnealed",
                      action="store_true",
                      dest=USE_ANNEALED_STR, default=False,
                      help="Use the annealed workflow"
                     )
    # NB the 'fullXXXX' and 'useAnnealed' options will be the only parameters maintained.
    # Most other options will be put into 'parameters'. 
    parser.add_option("--fullRefine",
                      action="store_true",
                      dest="fullRefine", default=False,
                      help="Complete refine workflow (optionally after anneal)"
                     )
    parser.add_option("--fullAnneal",
                      action="store_true",
                      dest="fullAnneal", default=False,
                      help="Complete anneal workflow"
                     )
    parser.add_option("--fullAnnealAndRefine",
                      action="store_true",
                      dest="fullAnnealAndRefine", default=False,
                      help="Complete anneal and refine workflow"
                     )
    parser.add_option("-r", "--refine",
                      action="store_true",
                      dest="doRefine", default=False,
                      help="Refine the structures (default: no refine)"
                     )
    parser.add_option("-e", "--anneal",
                      action="store_true",
                      dest="doAnneal", default=False,
                      help="Anneal the structures (default: no anneal)"
                     )
    parser.add_option("-p", "--print",
                      action="store_true",
                      dest="doPrint", default=False,
                      help="Print script before running (default: no print)"
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
    parser.add_option("--modelsAnneal",
                      dest="modelsAnneal", default='',
                      help="Annealed models",
                     )
    parser.add_option("--models",
                      dest="models", default='',
                      help="Model indices (e.g. 0,2-5,7,10-13)",
                      metavar="MODELS"
                     )
    parser.add_option("--bestModels",
                      dest="bestModels", default='',
                      help="Best refined models",
                     )
    parser.add_option("--modelCountAnneal",
                      dest="modelCountAnneal", default=0, type="int",
                      help="Number of annealed models"
                      )
    parser.add_option("--bestAnneal",
                      dest="bestAnneal", default=0, type="int",
                      help="Number of best annealed models",
                     )
    parser.add_option("--best",
                      dest="best", default=0, type="int",
                      help="Number of best refined models",
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
                      default=9,
                      dest="verbosity", action='store',
                      help="verbosity: [0(nothing)-9(debug)] no/less messages to stdout/stderr (default: 3)"
                     )
    parser.add_option("--ipython",
                      action="store_true",
                      dest="ipython",
                      help="Start ipython interpreter"
                     )
    return parser
# end def

def setParametersFromOptions(project, options, parameters):
    # NB we're using the dest fields of the parser. E.g. sortField and not sort
    optionNameList = 'name modelCountAnneal bestAnneal best modelsAnneal models bestModels overwrite sortField superpose'.split()
    optionNameList += [ USE_ANNEALED_STR ]
    for optionName in optionNameList:
        optionValue = getDeepByKeysOrAttributes(options, optionName)
        if not optionValue:
            continue
        parameters[ optionName ] = optionValue
    # end for
# end def
