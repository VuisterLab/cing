'''
Created on May 2, 2011

@author: jd
'''
from Refine.NTxplor import * #@UnusedWildImport
from cing.Libs.NTutils import * #@UnusedWildImport

def getParameters( basePath, extraModuleName):
    paramfile = os.path.join(basePath, '%s.py' % extraModuleName)
    if not os.path.exists(paramfile):
        NTerror("Failed to find: %s" % paramfile)
        return

    if 0:
        execfile_(paramfile, globals()) # Standard execfile fails anyhow for functions and is obsolete in Python 3
    if 1: # Less preferred to change sys.path and also fails in some situations.
    #    parameters = refineParameters()
    #    del parameters
        if basePath in sys.path:
            NTdebug("Skipping add since path is already present.")
        else:
            sys.path.insert(0, basePath)
        # end if
    #    NTmessage('sys.path:\n%s' % str(sys.path))
    #    NTmessage('==> Reading user parameters %s', paramfile)
    #    g = globals()
    #    NTmessage("g: %s" % g)
    #    l = locals()
    #    NTmessage("l: %s" % l)
    #    parameters  = refineParameters #@UnusedVariable
    #    _temp = __import__(extraModuleName, globals(), locals(), [], -1)
#        _temp = __import__(extraModuleName, globals())
        _temp = __import__(extraModuleName, fromlist=['parameters'])
    #    _temp = __import__(extraModuleName)
        parameters = _temp.parameters
    # end if

    if not 'parameters' in locals():
        NTerror("Failed sanity check: The variable name 'parameters' should exist in the local scope.")
        return

    if not hasattr( parameters, 'ncpus'): #@UndefinedVariable
        NTerror("Failed sanity check: parameters should have a 'ncpus' attribute.")
        return

#    NTdebug('==> parameters\n%s\n', str(parameters))
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
                      dest="useAnnealed", default=False,
                      help="Use the annealed workflow"
                     )
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