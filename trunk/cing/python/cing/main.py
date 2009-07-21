"""
--------------------------------------------------------------------------------
main.py: command line interface to the cing utilities:
--------------------------------------------------------------------------------

Usage: cing [options]       use -h or --help for listing

Options:
  -h, --help            show this help message and exit
  --test                Run set of test routines to verify installation.
  --test2               Run extensive tests on large data sets checking code
                        after fundamental changes.
  --doc                 Print more documentation to stdout
  --docdoc              Print full documentation to stdout
  --pydoc               start pydoc server and browse documentation
  -n PROJECTNAME, --name=PROJECTNAME, --project=PROJECTNAME
                        NAME of the project (required)
  --new                 Start new project PROJECTNAME (overwrite if already
                        present)
  --old                 Open a old project PROJECTNAME (error if not present)
  --init=SEQUENCEFILE[,CONVENTION]
                        Initialize new project PROJECTNAME and new molecule
                        from SEQUENCEFILE[,CONVENTION]
  --initPDB=PDBFILE[,CONVENTION]
                        Initialize new project PROJECTNAME from
                        PDBFILE[,CONVENTION]
  --initBMRB=BMRBFILE   Initialize new project PROJECTNAME from edited BMRB
                        file
  --initCcpn=CCPNFOLDER
                        Initialize new project PROJECTNAME from CCPNFOLDER
  --xeasy=SEQFILE,PROTFILE,CONVENTION
                        Import shifts from xeasy SEQFILE,PROTFILE,CONVENTION
  --xeasyPeaks=SEQFILE,PROTFILE,PEAKFILE,CONVENTION
                        Import peaks from xeasy
                        SEQFILE,PROTFILE,PEAKFILE,CONVENTION
  --merge               Merge resonances
  --generatePeaks=EXP_NAME,AXIS_ORDER
                        Generate EXP_NAME peaks with AXIS_ORDER from the
                        resonance data
  --molecule=MOLECULENAME
                        Restore Molecule MOLECULENAME as active molecule
  --script=SCRIPTFILE   Run script from SCRIPTFILE
  --ipython             Start ipython interpreter
  --validate            Run doValidate.py script [in current or cing
                        directory]
  --shiftx              Predict with shiftx
  --ranges=RANGES       Ranges for superpose, procheck, validate etc; e.g.
                        503-547,550-598,800,801
  --superpose           Do superposition; optionally uses RANGES
  --nosave              Don't save on exit (default: save)
  --export              Export before exit (default: noexport)
  -v VERBOSITY, --verbosity=VERBOSITY
                        verbosity: [0(nothing)-9(debug)] no/less messages to
                        stdout/stderr (default: 3)


--------------------------------------------------------------------------------
Some examples; all assume a project named 'test':
--------------------------------------------------------------------------------

- To start a new Project using most verbose messaging:
cing --name test --new --verbosity 9

- To start a new Project from a xeasy seq file:
cing --name test --init AD.seq,CYANA

- To start a new Project from a xeasy seq file and load an xeasy prot file:
cing --name test --init AD.seq,CYANA --xeasy AD.seq,AD.prot,CYANA

- To start a new Project from a Ccpn project (new implementation):
cing --name test --initCcpn ccpn_project.xml

- To open an existing Project:
cing --name test

- To open an existing Project and load an xeasy prot file:
cing --name test --xeasy AD.seq,AD.prot,CYANA

- To open an existing Project and start an interactive python interpreter:
cing --name test --ipython

- To open an existing Project and run a script MYSCRIPT.py:
cing --name test --script MYSCRIPT.py

- To test CING without any messages (not even errors):
cing --test --verbose 0

- To test CING on many data sets including CCPN, PDB, etc.
cing --test2 --verbose 0

--------------------------------------------------------------------------------
Some simple script examples:
--------------------------------------------------------------------------------

== merging several prot files ==
project.initResonances()      # removes all resonances from the project
project.importXeasy( 'N15.seq', 'N15.prot', 'CYANA' )
project.importXeasy( 'C15.seq', 'C15.prot', 'CYANA' )
project.importXeasy( 'aro.seq', 'aro.prot', 'CYANA' )
project.mergeResonances( status='reduce'  )

== Generating a peak file from shifts ==
project.listPredefinedExperiments() # list all predefined experiments
peaks = project.generatePeaks('hncaha','HN:HA:N')
format(peaks)

== Print list of parameters:
    formatall( project.molecule.A.residues[0].procheck ) # Adjust for your mols
    formatall( project.molecule.A.VAL171.C )
"""
#==============================================================================
from cing import OS_TYPE_LINUX
from cing import OS_TYPE_MAC
from cing import __author__ #@UnusedImport
from cing import __copyright__ #@UnusedImport
from cing import __credits__ #@UnusedImport
from cing import __date__ #@UnusedImport
from cing import __version__ #@UnusedImport
from cing import cingPythonCingDir
from cing import cingPythonDir
from cing import cingVersion
from cing import header
from cing import starttime
from cing.Libs.NTutils import ImportWarning
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTpath
from cing.Libs.NTutils import OptionParser
from cing.Libs.NTutils import findFiles
from cing.core.classes import Project
from cing.core.molecule import Molecule
from cing.core.parameters import cingPaths
from cing.core.parameters import osType
from cing.core.parameters import plugins
from string import join
import cing
import os
import sys
import time
import unittest


#------------------------------------------------------------------------------------
# Support routines
#------------------------------------------------------------------------------------

def pformat( object ):
#$%^%^&&*(()
#
# JURGEN: do NOT touch this routine! Only for interactive usage
#
#%%^$&*$($()
#    print '>>', object
    if hasattr(object,'format'):
        print object.format()
    else:
        print object
    #end if
#end def

def format(object):
    """Returns the formatted object representation"""
#    print '>>', object
    if hasattr(object, 'format'):
        return object.format()
    return  "%s" % object
#end def


def getStartMessage():
    """
    Copy catted from xplor
    user = "jd"
    on   = "Stella.loc(darwin/x86    )
    at   = "29-Oct-08 15:36:22
    """
    user = os.getenv("USER", "Unknown user")
    machine = os.getenv("HOST", "Unknown host") #only works with (t)csh shell
#    ostype = os.getenv("OSTYPE", "Unknown os") #only works with (t)csh shell
    on = "%s (%s)" % (machine, osType)
    at = time.asctime()
#    atForFileName = "%s" % at
#    atForFileName = re.sub('[ :]', '_', atForFileName)
    return "User: %-15s on: %-45s at: %s" % (user, on, at)


def getStopMessage():
    """From Wattos
#    Wattos started at: October 29, 2008 4:04:44 PM CET
#    Wattos stopped at: October 29, 2008 4:04:49 PM CET
#    Wattos took (#ms): 4915"""
    at = time.asctime(time.localtime(starttime))
    now = time.asctime()

#    memory TODO print "in use and allocated"
    msg = "CING started at : %s\n" % at
    msg += "CING stopped at : %s\n" % now
    msg += "CING took       : %-.3f s\n\n" % (time.time() - starttime)
    return msg

def verbosity(value):
    """Set CING verbosity
    """
    try:
        cing.verbosity = int(value)
    except:
        NTerror('verbosity: value should be integer in the interval [0-9] (%s)', value)
#end def


def formatall(object):
    """Returns the formatted object representation"""
    result = ""
    if isinstance(object, list):
        i = 0
        for obj in object:
            #printf(">>> [%d] >>> ", i)
            result += format(obj)
            i += 1
        return result
    if isinstance(object, dict):
        for key, value in object.items():
            result += "%-15s : " % key
            result += format(value)
        return result
    return format(object)
#end def

args = []
kwds = {}

def scriptPath(scriptFile):
    # get path to scriptFile

    if not os.path.exists(scriptFile):
        NTdebug('Missed in current working directory the script file: %s' % scriptFile)
        scriptsDir = os.path.join(cingPythonCingDir, cingPaths.scripts)
        scriptFileAbs = os.path.join(scriptsDir, scriptFile)
        if not os.path.exists(scriptFileAbs):
            NTerror('Missed in current working directory and Scripts directory\n' +
                    '[%s] the script file [%s]' % (scriptsDir, scriptFile))
            return None
        return scriptFileAbs
    #end if
    return scriptFile
#end def

def script(scriptFile, *a, **k):
    # Hack to get arguments to routine as global variables to use in script
    global args
    global kwds
    args = a
    kwds = k

    path = scriptPath(scriptFile)
    if path:
        NTmessage('==> Executing script "%s"', path)
        execfile(path, globals())
    #end if
#end def


def testOverall(namepattern):
    # Use silent testing from top level.
#    cing.verbosity = verbosityError
    # Add the ones you don't want to test (perhaps you know they don't work yet)
    excludedModuleList = [ cingPythonDir + "/Cython*",
                           cingPythonDir + "/cyana2cing*",
#                           cingPythonDir + "/cing.PluginCode",
#                           cingPythonDir + "/cing.PluginCode.test.test_Whatif",
#                           cingPythonDir + "/cing.Scripts.test.test_cyana2cing",
#                           cingPythonDir + "/cing.STAR.FileTest",
                          ]
    startdir = cingPythonDir
    nameList = findFiles(namepattern, startdir, exclude=excludedModuleList)
    # enable next line to do a single check only.
#    nameList = ['/Users/jd/workspace34/cing/python/cing/iCing/test/test_Json.py']
#    nameList = ['/Users/jd/workspace34/cing/python/cing/PluginCode/test/test_ccpn.py']
#    nameList = ['/Users/jd/workspace34/cing/python/cing/PluginCode/test/test_Molgrap.py']
#    nameList = ['/Users/jd/workspace34/cing/python/cing/PluginCode/test/test_Procheck.py']
#    nameList = ['/Users/jd/workspace34/cing/python/cing/PluginCode/test/test_validate.py']
#    nameList = ['/Users/jd/workspace34/cing/python/cing/PluginCode/test/test_Wattos.py']
#    nameList = ['/Users/jd/workspace34/cing/python/cing/PluginCode/test/test_NmrStar.py']
#    nameList = ['/Users/jd/workspace34/cing/python/cing/Libs/test/test_Imagery.py']
    NTdebug('will unit check: ' + `nameList`)
#    nameList = nameList[0:5]
#    namepattern = "*Test.py"
#    nameList2 = findFiles(namepattern, startdir)
#    for name in nameList2:
#      nameList.append(name)
    # translate: '/Users/jd/workspace/cing/python/cing/Libs/test/test_NTplot.py'
    # to: cing.Libs.test.test_NTplot
    lenCingPythonDirStr = len(cingPythonDir)
    for name in nameList:
#        print name
        tailPathStr = name[lenCingPythonDirStr + 1: - 3]
        mod_name = join(tailPathStr.split('/'), '.')
        if mod_name in excludedModuleList:
            print "Skipping module:  " + mod_name
            continue
        try:
            exec("import %s" % (mod_name))
            exec("suite = unittest.defaultTestLoader.loadTestsFromModule(%s)" % (mod_name))
            testVerbosity = 2
            unittest.TextTestRunner(verbosity=testVerbosity).run(suite) #@UndefinedVariable
            NTmessage('\n\n\n')
        except ImportWarning, extraInfo:
            NTmessage("Skipping test report of an optional compound: %s" % extraInfo)
        except ImportError, extraInfo:
            NTmessage("Skipping test report of an optional module: %s" % mod_name)


def getParser():
    #------------------------------------------------------------------------------------
    # Options
    #------------------------------------------------------------------------------------
    usage = "usage: cing [options]       use -h or --help for listing"

    parser = OptionParser(usage=usage, version=str(cingVersion))
    parser.add_option("--test",
                      action="store_true",
                      dest="test",
                      help="Run set of test routines to verify installations"
                     )
    parser.add_option("--test2",
                      action="store_true",
                      dest="test2",
                      help="Run extensive set of test routines to check code (Those matching test2_*.py)."
                     )
    parser.add_option("--doc",
                      action="store_true",
                      dest="doc",
                      help="Print more documentation to stdout"
                     )
    parser.add_option("--docdoc",
                      action="store_true",
                      dest="docdoc",
                      help="Print full documentation to stdout"
                     )
    parser.add_option("--pydoc",
                      action="store_true",
                      dest="pydoc",
                      help="start pydoc server and browse documentation"
                     )
    parser.add_option("-n", "--name", "--project",
                      dest="name", default=None,
                      help="NAME of the project (required)",
                      metavar="PROJECTNAME"
                     )
#    parser.add_option("--gui",
#                      action="store_true",
#                      dest="gui",
#                      help="Start graphical user interface"
#                     )
    parser.add_option("--new",
                      action="store_true",
                      dest="new",
                      help="Start new project PROJECTNAME (overwrite if already present)"
                     )
    parser.add_option("--old",
                      action="store_true",
                      dest="old",
                      help="Open a old project PROJECTNAME (error if not present)"
                     )
    parser.add_option("--init",
                      dest="init", default=None,
                      help="Initialize new project PROJECTNAME and new molecule from SEQUENCEFILE[,CONVENTION]",
                      metavar="SEQUENCEFILE[,CONVENTION]"
                     )
    parser.add_option("--initPDB",
                      dest="initPDB", default=None,
                      help="Initialize new project PROJECTNAME from PDBFILE[,CONVENTION]",
                      metavar="PDBFILE[,CONVENTION]"
                     )
    parser.add_option("--initBMRB",
                      dest="initBMRB", default=None,
                      help="Initialize new project PROJECTNAME from edited BMRB file",
                      metavar="BMRBFILE"
                     )
    parser.add_option("--initCcpn",
                      dest="initCcpn", default=None,
                      help="Initialize new project PROJECTNAME from CCPNFOLDER",
                      metavar="CCPNFOLDER"
                     )
#    parser.add_option("--loadCcpn",
#                      dest="loadCcpn", default=None,
#                      help="Open project PROJECTNAME and load data from CCPNFOLDER",
#                      metavar="CCPNFOLDER"
#                     )
    parser.add_option("--xeasy",
                      dest="xeasy", default=None,
                      help="Import shifts from xeasy SEQFILE,PROTFILE,CONVENTION",
                      metavar="SEQFILE,PROTFILE,CONVENTION"
                     )
    parser.add_option("--xeasyPeaks",
                      dest="xeasyPeaks", default=None,
                      help="Import peaks from xeasy SEQFILE,PROTFILE,PEAKFILE,CONVENTION",
                      metavar="SEQFILE,PROTFILE,PEAKFILE,CONVENTION"
                     )
    parser.add_option("--merge",
                      action="store_true",
                      dest="merge",
                      help="Merge resonances"
                     )
    parser.add_option("--generatePeaks",
                      dest="generatePeaks", default=None,
                      help="Generate EXP_NAME peaks with AXIS_ORDER from the resonance data",
                      metavar="EXP_NAME,AXIS_ORDER"
                     )
    parser.add_option("--molecule",
                      dest="moleculeName", default=None,
                      help="Restore Molecule MOLECULENAME as active molecule",
                      metavar="MOLECULENAME"
                     )
    parser.add_option("--script",
                      dest="script", default=None,
                      help="Run script from SCRIPTFILE",
                      metavar="SCRIPTFILE"
                     )
    parser.add_option("--ipython",
                      action="store_true",
                      dest="ipython",
                      help="Start ipython interpreter"
                     )
    parser.add_option("--yasara",
                      action="store_true",
                      dest="yasara",
                      help="Start interactive yasara interpreter"
                     )
    parser.add_option("--validate",
                      action="store_true", dest="validate", default=False,
                      help="Run doValidate.py script [in current or cing directory]"
                     )
    parser.add_option("--shiftx",
                      action="store_true", default=False,
                      dest="shiftx",
                      help="Predict with shiftx"
                     )
    parser.add_option("--ranges",
                      dest="ranges", default=None,
                      help="Ranges for superpose, procheck, validate etc; e.g. 503-547,550-598,800,801",
                      metavar="RANGES"
                     )
    parser.add_option("--ensemble",
                      dest="ensemble", default=None,
                      help="Models of the ensemble to use for superpose, procheck, validate etc; e.g. 0,3-8,10,20. Note that model numbers start at zero.",
                      metavar="ENSEMBLE"
                     )
    parser.add_option("--superpose",
                      action="store_true", default=False,
                      dest="superpose",
                      help="Do superposition; optionally uses RANGES"
                     )
    parser.add_option("--nosave",
                      action="store_true",
                      dest="nosave",
                      help="Don't save on exit (default: save)"
                     )
    parser.add_option("--export", default=False,
                      action="store_true",
                      dest="export",
                      help="Export before exit (default: noexport)"
                     )
    parser.add_option("-v", "--verbosity", type='int',
                      default=cing.verbosityDefault,
                      dest="verbosity", action='store',
                      help="verbosity: [0(nothing)-9(debug)] no/less messages to stdout/stderr (default: 3)"
                     )
    return parser
#end def

project = None # after running main it will be filled.

def yasara( project ):
    from cing.PluginCode.yasaraPlugin import yasaraShell
    yasaraShell( project )
#end def


def main():

    if not ( osType == OS_TYPE_MAC or
             osType == OS_TYPE_LINUX ):
        NTerror("CING only runs on unix")
        sys.exit(1)

    global project
    global options

    _root, file, _ext = NTpath(__file__)

    parser = getParser()
    (options, _args) = parser.parse_args()

    if options.verbosity >= 0 and options.verbosity <= 9:
        cing.verbosity = options.verbosity
    else:
        NTerror("set verbosity is outside range [0-9] at: " + options.verbosity)
        NTerror("Ignoring setting")
    # From this point on code may be executed that will go through the appropriate verbosity filtering

    NTmessage(header)
    NTmessage(getStartMessage())

    NTdebug('options: %s', options)
    NTdebug('args: %s', _args)

    # The weird location of this import is because we want it to be verbose.
#    from cing.core.importPlugin import importPlugin # This imports all plugins    @UnusedImport
    # JFD: already present in __init__.py.

    if options.test:
        testOverall(namepattern="test_*.py")
        sys.exit(0)
    if options.test2:
        testOverall(namepattern="test2_*.py")
        sys.exit(0)

    #------------------------------------------------------------------------------------
    # Extended documentation
    #------------------------------------------------------------------------------------
    if options.doc:
        parser.print_help(file=sys.stdout)
        print __doc__
        sys.exit(0)
    #end if

    if options.pydoc:
        import pydoc
        import webbrowser
        NTmessage('==> Serving documentation at http://localhost:9999')
        NTmessage('    Type <control-c> to quit')
        webbrowser.open('http://localhost:9999/cing.html')
        pydoc.serve(port=9999)
        sys.exit(0)
    #end if

    #------------------------------------------------------------------------------------
    # Full documentation
    #------------------------------------------------------------------------------------
    if options.docdoc:
        print '=============================================================================='
        parser.print_help(file=sys.stdout)
        print __doc__

        print Project.__doc__
        for p in plugins.values():
            NTmessage('-------------------------------------------------------------------------------' +
                       'Plugin %s\n' +
                       '-------------------------------------------------------------------------------\n%s\n',
                        p.module.__file__, p.module.__doc__
                     )
        #end for

        print Molecule.__doc__
        sys.exit(0)
    #end if

    #------------------------------------------------------------------------------------
    # START
    #------------------------------------------------------------------------------------

    # GUI
#    if options.gui:
#        import Tkinter
#        from cing.core.gui import CingGui
#
#        root = Tkinter.Tk()
#
#        popup = CingGui(root, options=options)
#        popup.open()
#
#        root.withdraw()
#        root.mainloop()
#        exit()
#    #end if

    #check for the required name option
    parser.check_required('-n')

#    args = []
    _kwds = {}


    #------------------------------------------------------------------------------------
    # open project
    #------------------------------------------------------------------------------------
    if options.new:
        project = Project.open(options.name, status='new')
    elif options.old:
        project = Project.open(options.name, status='old')
    elif options.init:
        init = options.init.split(',')
        if (len(init) == 2):
            project = Project.open(options.name, status='new')
            project.newMolecule(options.name, sequenceFile=init[0], convention=init[1])
        else:
            project = Project.open(options.name, status='new')
            project.newMolecule(options.name, sequenceFile=init[0])
        #end if
    elif options.initPDB:
        init = options.initPDB.split(',')
        if (len(init) == 2):
            project = Project.open(options.name, status='new')
            project.initPDB(pdbFile=init[0], convention=init[1])
        else:
            project = Project.open(options.name, status='new')
            project.initPDB(pdbFile=init[0])
    elif options.initBMRB:
        project = Project.open(options.name, status='new')
        project.initBMRB(bmrbFile=options.initBMRB, moleculeName=project.name)
    elif options.initCcpn:
        project = Project.open(options.name, status='new')
        project.initCcpn(ccpnFolder=options.initCcpn)
#    elif options.loadCcpn:
#        project = Project.open(options.name, status='create', restore=False)
#        project.initCcpn(ccpnFolder=options.loadCcpn)
    else:
        project = Project.open(options.name, status='create')

    if not project:
        NTdebug("Doing a hard system exit")
        sys.exit(2)
    #end if

    #------------------------------------------------------------------------------------
    # check for alternative molecule
    #------------------------------------------------------------------------------------
    if options.moleculeName:
        if options.moleculeName in project:
            project.molecule = project[options.moleculeName]
        else:
            project.restoreMolecule(options.moleculeName)
        #end if
    #end if

    NTmessage(project.format())

    # shortcuts
    p = project
    mol = project.molecule #@UnusedVariable
    m = project.molecule #@UnusedVariable

 #   pr = print
    f = pformat #@UnusedVariable
    fa = formatall #@UnusedVariable

    if options.ensemble:
#        NTdebug( "Truncating the ensemble because ensemble option was set to: [" +options.ensemble+"]" )
        mol.keepSelectedModels( options.ensemble )
#    else:
#        NTdebug( "ensemble option was not found." )

    #------------------------------------------------------------------------------------
    # Import xeasy protFile
    #------------------------------------------------------------------------------------
    if options.xeasy:
        xeasy = options.xeasy.split(',')
        if (len(xeasy) != 3):
            NTerror("--xeasy=SEQFILE,PROTFILE,CONVENTION arguments required")
        else:
            project.importXeasy(seqFile=xeasy[0], protFile=xeasy[1], convention=xeasy[2])

    #------------------------------------------------------------------------------------
    # Import xeasy peakFile
    #------------------------------------------------------------------------------------
    if options.xeasyPeaks:
        xeasy = options.xeasyPeaks.split(',')
        if len(xeasy) != 4:
            NTerror("--xeasyPeaks=SEQFILE,PROTFILE,PEAKFILE,CONVENTION arguments required")
        else:
            project.importXeasyPeaks(seqFile=xeasy[0], protFile=xeasy[1], peakFile=xeasy[2], convention=xeasy[3])

    #------------------------------------------------------------------------------------
    # Merge resonances
    #------------------------------------------------------------------------------------
    if (options.merge):
        project.mergeResonances()
    #end if

    #------------------------------------------------------------------------------------
    # Generate peaks
    #------------------------------------------------------------------------------------
    if (options.generatePeaks):
        gp = options.generatePeaks.split(',')
        if len(gp) != 2:
            NTerror("--generatePeaks: EXP_NAME,AXIS_ORDER arguments required")
        else:
            peaks = project.generatePeaks(experimentName=gp[0], axisOrder=gp[1]) #@UnusedVariable
        #end if
    #end if

    #------------------------------------------------------------------------------------
    # Shiftx
    #------------------------------------------------------------------------------------
    if options.shiftx:
        project.runShiftx()

    #------------------------------------------------------------------------------------
    # Superpose
    #------------------------------------------------------------------------------------
    if options.superpose:
        project.superpose(ranges=options.ranges)

    #------------------------------------------------------------------------------------
    # Validate; just run doValidate script
    #------------------------------------------------------------------------------------
    if options.validate:
        path = scriptPath('doValidate.py')
        if path:
            NTmessage('==> Executing script "%s"', path)
            execfile(path)
    #end if

    #------------------------------------------------------------------------------------
    # Script
    #------------------------------------------------------------------------------------
    if options.script:
        scriptFile = scriptPath(options.script)
        if scriptFile:
            NTmessage('==> Executing script "%s"', scriptFile)
            execfile(scriptFile, globals() )
        #end if
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

    #------------------------------------------------------------------------------------
    # yasara ipython
    #------------------------------------------------------------------------------------
    if options.yasara:
        yasara(project)
    #end if

    #------------------------------------------------------------------------------------
    # Optionally export project
    #------------------------------------------------------------------------------------
    if project and  options.export:
        project.export()

    #------------------------------------------------------------------------------------
    # CLose and optionally not save project
    #------------------------------------------------------------------------------------
    if project:
        project.close(save=not options.nosave)
    #------------------------------------------------------------------------------------

if __name__ == '__main__':
    try:
        main()
    finally:
        NTmessage(getStopMessage())
