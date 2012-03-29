#!/usr/bin/env python

"""
--------------------------------------------------------------------------------
main.py: command line interface to the cing utilities:
--------------------------------------------------------------------------------

Usage: cing [options]       use -h or --help for listing

Options:
  -h, --help            show this help message and exit
  --test                Run set of test routines to verify installation, use -c 1
                          for any of these test routines in order to get nice
                          sequential order of outputs.
  --testQ               Same as --test and just grepping for any errors.
  --test2               Run extensive tests on large data sets checking code
                        after fundamental changes.
  --doc                 Print more documentation to stdout
  --docdoc              Print full documentation to stdout
  --pydoc               start pydoc server and browse documentation
  -n PROJECTNAME, --name=PROJECTNAME, --project=PROJECTNAME
                        NAME of the project (required; unless --noProject presented)
  --new                 Start new project PROJECTNAME (overwrite if already
                        present).
  --old                 Open a old project PROJECTNAME (error if not present)
  --init=SEQUENCEFILE[,CONVENTION]
                        Initialize new project PROJECTNAME and new molecule
                        from SEQUENCEFILE[,CONVENTION]
  --initPDB=PDBFILE[,CONVENTION]
                        Initialize new project PROJECTNAME from
                        PDBFILE[,CONVENTION]
  --initCyana=CYANA_PROJECT_FILE[,CONVENTION]
                        Initialize new project from .cyana.tgz
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
  --pylint=PYLINTFILE   Test the CING code base with pylint. Write messages to PYLINTFILE
  -i --ipython          Start ipython interpreter
  --validate            Validate.
  --validateFastest     Fastest possible checks by CING only and without imagery.
                        Implies --validateCingOnly and --validateImageLess.
  --validateCingOnly    Fast checks by CING only but with imagery unless disabled. Implies --validate.
                        Note that a few fast external programs will be done anyway.
  --validateImageLess   Disable creating the imagery when validating. Implies --validate.
  --shiftx              Predict with shiftx
  --ranges=RANGES       Ranges for superpose, procheck, validate etc; e.g.
                        'A.503-547,A.550-598,B.800,B.802' or 'auto' for using
                        the cv if available.
  --superpose           Do superposition; optionally uses RANGES
  --nosave              Don't save on exit (default: save)
  --noProject           Start full CING environment without a project. Useful eg. with --script.
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

- Do a weekly update of PDBj database
cing --noProject --script $CINGROOT/python/cing/NRG/weeklyUpdatePdbjMine.py

- Validate a PDB entry within a minute and drop into iPython.
cing -n $x --initPDB $PDB/pdb$x.ent.gz --ipython --validateFastest
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
from cing import __author__ #@UnusedImport
from cing import __copyright__ #@UnusedImport
from cing import __credits__ #@UnusedImport
from cing import __date__ #@UnusedImport
from cing import __version__ #@UnusedImport
from cing import cingDirTmp
from cing import cingPythonCingDir
from cing import cingPythonDir
from cing import cingVersion
from cing import header
from cing import starttime
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.disk import rmdir
from cing.Libs.forkoff import ForkOff
from cing.Libs.helper import * #@UnusedWildImport
from cing.core.classes import Project
from cing.core.molecule import Molecule
from cing.core.parameters import cingPaths
from cing.core.parameters import osType
from cing.core.parameters import plugins
from cing.core.sml import SMLversion
from nose.plugins.skip import SkipTest # Dependency on nose can be removed in python 2.7 or later when UnitTest has similar functionality.
import commands
import unittest
import webbrowser

#------------------------------------------------------------------------------------
# Support routines
#------------------------------------------------------------------------------------

def pformat( obj ):
    'Convenience method.'
#$%^%^&&*(()
#
# JURGEN: do NOT touch this routine! Only for interactive usage
#
#%%^$&*$($()
#    print '>>', obj
    if hasattr(obj,'format'):
        print obj.format()
    else:
        print obj
    #end if
#end def

def pformatall( obj, *args, **kwds ):
    'Convenience method.'
#$%^%^&&*(()
#
# JURGEN: do NOT touch this routine! Only for interactive usage
#
#%%^$&*$($()
#    print '>>', obj
    if hasattr(obj,'formatAll'):
        print obj.formatAll(*args, **kwds)
    else:
        print formatall(obj)
    #end if
#end def

def format(obj): # pylint: disable=W0622
    """Returns the formatted object representation"""
#    print '>>', obj
    if hasattr(obj, 'format'):
        return obj.format()
    return  "%s" % obj
#end def

def getInfoMessage():
    'Returns information about CING internals. Depreciated: use start message instead.'
    return sprintf(
"""
Version:           %.3f
Revision:          %s (%s)
Date:              %s
Database:          %s
SML:               %.3f

CING root:         %s
CING tmp:          %s

Default verbosity: %d
""",
     cing.cingVersion, cing.cingRevision, cing.cingRevisionUrl+str(cing.cingRevision),
     cing.__date__, cing.INTERNAL,  SMLversion,
     cing.cingRoot, cing.cingDirTmp,
     cing.verbosityDefault
    )

def verbosity(value):
    """Set CING verbosity
    """
    try:
        cing.verbosity = int(value)
    except:
        nTerror('verbosity: value should be integer in the interval [0-9] (%s)', value)
#end def


def formatall(obj):
    """Returns the formatted obj representation"""
    result = ""
    if isinstance(obj, list):
#        i = 0
        for obj in obj:
            #printf(">>> [%d] >>> ", i)
            result += format(obj)
            result += "\n"
#            i += 1
        return result
    if isinstance(obj, dict):
        for key, value in obj.items():
            result += "%-15s : " % key
            result += format(value)
            result += "\n"
        return result
    return format(obj)
#end def

args = []
kwds = {}

def scriptPath(scriptFile):
    'get path to scriptFile'
    if not os.path.exists(scriptFile):
#        nTwarning('Missed in current working directory the script file: %s' % scriptFile)
        scriptsDir = os.path.join(cingPythonCingDir, cingPaths.scripts)
        scriptFileAbs = os.path.join(scriptsDir, scriptFile)
        if not os.path.exists(scriptFileAbs):
            nTerror('Missed in current working directory and Scripts directory\n' +
                    '[%s] the script file [%s]' % (scriptsDir, scriptFile))
            return None
        return scriptFileAbs
    #end if
    return scriptFile
#end def

def script(scriptFile, *a, **k):
    'Execute given script and arguments/keywords.'
    # Hack to get arguments to routine as global variables to use in script
    # pylint: disable=W0603
    global args # pylint: disable=W0621
    # pylint: disable=W0603
    global kwds # pylint: disable=W0621
    args = a
    kwds = k

    path = scriptPath(scriptFile)
    if path:
        nTmessage('==> Executing script "%s"', path)
        execfile(path, globals())
    #end if
#end def


def testQuiet():
    'Return True on error'
    cing.verbosity = cing.verbosityOutput
    fn = 'cingTest.log'
    nTmessage("\nStarting quiet test in %s logged to %s\n" % (cingDirTmp, fn))
    os.chdir(cingDirTmp)
    resultStatus = False 
    cmdCingTest = 'python -u $CINGROOT/python/cing/main.py --test -c %d -v 0 > %s 2>&1' % ( cing.ncpus, fn )
#    nTmessage("In cing.main doing [%s]" % cmdCingTest)
    status, content = commands.getstatusoutput(cmdCingTest)
    if status:
        nTerror("Failed to finish CING test")
        resultStatus = True
    else:
        nTmessage("Finished CING test\n")
    # end if
    if content:        
        nTerror("Unexpected output: [%s]" % content)
        resultStatus = True
    # end if
    resultList = []
    status = grep(fn, 'error', resultList=resultList, caseSensitive=False)
    if status == 0:
        nTerror("Found %d errors, please check the errors below and full log %s" % ( len(resultList), os.path.join(cingDirTmp,fn)))
        nTerror("Errors:\n%s" % '\n'.join(resultList))
        resultStatus = True
    else:
        nTmessage("No problems were found")
    # end if
    resultTestFileList = []
    status = grep(fn, 'tests in', resultList=resultTestFileList)
    nTmessage("Ran %d test files" % len(resultTestFileList))
    resultList = []
    status = grep(fn, '... ok', resultList=resultList)
    if status == 0:
        nTmessage("Ran %d tests ok\n" % len(resultList))
    else:
        nTerror("Failed to do a single test ok")
        resultStatus = True
    # end if
    if resultStatus:
        nTerror("Overall failure of testQuiet.")
    return resultStatus
#end def

def doPylintOverallSummary(pylintFileName='pylint.txt'):
    'Summarizing which pylint message types occur'
    nTdebug("Now in " + getCallerName())
    nTdebug("Will work on " + pylintFileName)
#    pylintDir = os.path.join( cingDirTmp, 'pylint' ) # Sync with below routine.
    pylintMsgCountMap = CountMap()
    lineList = readLinesFromFile(pylintFileName)
    for line in lineList:
        if line.count("GtkWarning") or line.count("_gtk.Warning"):
            nTdebug("Ignoring warnings from Gtk that have to do with running headless:\n%s" % line)
            continue
        # Match the message id with a starting bracket 
        # an alpha
        # a 4 digit number 
        match_msg_id = re.search(r'\[([EWICRF][0-9]{4})', line, 0)
        if not match_msg_id:
            nTwarning( "Failed to find message id from line: %s" % line )
            continue
        msg_id = match_msg_id.group(1)
        pylintMsgCountMap.increaseCount(msg_id, 1)
    # end for        
    nTmessage("pylint message types counts:\n%s" % (pylintMsgCountMap.toString()))
#    nTmessage('pylint message types overall count: %s' % len(pylintMsgHash.keys()))
#end def
    
def doPylintOverall(pylintFileName='pylint.txt'):
    "Add the ones you don't want to pylint (perhaps you know they don't work yet)"
    namepattern = "*.py"
    pylintDir = os.path.join( cingDirTmp, 'pylint' )
#    pylintFileName = os.path.join( pylintDir, 'pylint.log')
    if os.path.exists( pylintDir ):
        rmdir( pylintDir )
    mkdirs( pylintDir )
    if os.path.exists( pylintFileName ):
        os.unlink(pylintFileName)
    excludedModuleList = [ 
                            # enable exclusions for quick testing.
#                           cingPythonDir + "/cing/core*",
#                           cingPythonDir + "/cing/Database*",
#                           cingPythonDir + "/cing/Libs*",
#                           cingPythonDir + "/cing/NRG*",
#                           cingPythonDir + "/cing/PluginCode*",
#                           cingPythonDir + "/cing/Scripts*",
#                           cingPythonDir + "/cing/STAR*",
#                           cingPythonDir + "/cing/Talos*",
                           # Normal set:
                           cingPythonDir + "/cing/Database/CCPN*",
                           cingPythonDir + "/cyana2cing*",
                           cingPythonDir + "/pdbe2*",
                           cingPythonDir + "/queen*",
                           cingPythonDir + "/Refine*",
                           cingPythonDir + "/UtilsAnalysis*",
                           cingPythonDir + "/xplorcing*"
                          ]
    startdir = cingPythonDir
    nameList = findFiles(namepattern, startdir, exclude=excludedModuleList)
    # enable next line(s) to do a couple of checks only.
#    nameList = ['/Users/jd/workspace35/cing/python/cing/PluginCode/test/test_NmrStar.py',
#                '/Users/jd/workspace35/cing/python/cing/PluginCode/test/test_ccpn.py',
#                '/Users/jd/workspace35/cing/python/cing/PluginCode/test/test_ccpn_2.py']
    nTdebug('Will unit check: ' + repr(nameList))
    f = ForkOff(
            processes_max=cing.ncpus,
            max_time_to_wait=600, # on a very slow setup
            verbosity=2            
            )
    job_list = []
    for name in nameList:
        job_list.append( (doPylintByName, (name, excludedModuleList)) )
    done_list = f.forkoff_start(job_list, 0)
    nTmessage("Finished ids: %s", done_list)

    for name in nameList:
        mod_name = pathToModuleName( name )
        if mod_name in excludedModuleList:
            print "Skipping module:  " + mod_name
            return
        pylintOutputFileName = os.path.join( pylintDir, mod_name + '.log')        
        if not os.path.exists( pylintDir ):
            nTerror("Failed to find pylint output: " + pylintOutputFileName)
            continue
        if appendTextFileToFile( pylintOutputFileName, pylintFileName):
            nTerror("Failed to appendTextFileToFile")
#        nTdebug("Done appending from: %s" % pylintOutputFileName)
    # end for
    doPylintOverallSummary(pylintFileName=pylintFileName)
    nTmessage("Done with pylint")
# end def

def testOverall(namepattern):
    'Use silent testing from top level.'
#    cing.verbosity = verbosityError
    # Add the ones you don't want to test (perhaps you know they don't work yet)
    excludedModuleList = [ 
#                           cingPythonDir + "/Cython*",
                           cingPythonDir + "/cyana2cing*",
#                           cingPythonDir + "/cing.PluginCode",
#                           cingPythonDir + "/cing.PluginCode.test.test_Whatif",
#                           cingPythonDir + "/cing.Scripts.test.test_cyana2cing",
#                           cingPythonDir + "/cing.STAR.FileTest",
                          ]
    startdir = cingPythonDir
    nameList = findFiles(namepattern, startdir, exclude=excludedModuleList)
    # enable next line(s) to do a single check only.
#    nameList = ['/Users/jd/workspace35/cing/python/cing/Libs/test/test_Imagery.py']
#    nameList = [
#                '/Users/jd/workspace35/cing/python/cing/PluginCode/test/test_NmrStar.py',
#                '/Users/jd/workspace35/cing/python/cing/PluginCode/test/test_ccpn.py'
#                ]
    nTdebug('Will unit check: ' + repr(nameList))
#    nameList = nameList[0:5]
#    namepattern = "*Test.py"
#    nameList2 = findFiles(namepattern, startdir)
#    for name in nameList2:
#      nameList.append(name)
    # translate: '/Users/jd/workspace/cing/python/cing/Libs/test/test_NTplot.py'
    # to: cing.Libs.test.test_NTplot

    f = ForkOff(
#            processes_max=1,     # use 1 if you really want to read it line by line.
            processes_max=cing.ncpus,
            max_time_to_wait=600, # on a very slow setup
            verbosity=cing.verbosity
            )
    job_list = []
    for name in nameList:
        job_list.append( (testByName, (name, excludedModuleList)) )
    done_list = f.forkoff_start(job_list, 0)
    nTmessage("Finished ids: %s", done_list)

    # Exit with timer info anywho. After this CING should exit so the tweak shouldn't break anything.
    if cing.verbosity <= cing.verbosityError:
        cing.verbosity = cing.verbosityOutput
# end def

def testByName(name, excludedModuleList):
    'Test an individual module. Return True on error.'
    lenCingPythonDirStr = len(cingPythonDir)
    tailPathStr = name[lenCingPythonDirStr + 1: - 3]
    mod_name = '.'.join(tailPathStr.split('/'))
    if mod_name in excludedModuleList:
        print "Skipping module:  " + mod_name
        return

    try:
        exec("import %s" % (mod_name))
        exec("suite = unittest.defaultTestLoader.loadTestsFromModule(%s)" % (mod_name))
        testVerbosity = 2
        unittest.TextTestRunner(verbosity=testVerbosity).run(suite) #@UndefinedVariable
        nTmessage('\n\n\n')
    except ImportWarning, extraInfo:
        nTmessage("Skipping test report of an optional compound (please recode to use SkipTest): %s" % extraInfo)
    except SkipTest, extraInfo:
        nTmessage("Skipping test report of an optional compound: %s" % extraInfo)    
    except ImportError, extraInfo:
        nTmessage("Skipping test report of an optional module: %s" % mod_name)

    # Exit with timer info anywho. After this CING should exit so the tweak shouldn't break anything.
    if cing.verbosity <= cing.verbosityError:
        cing.verbosity = cing.verbosityOutput
# end def

def pathToModuleName( name ):
    "Convert full filename to module name assuming it's in this project"
    lenCingPythonDirStr = len(cingPythonDir)
    tailPathStr = name[lenCingPythonDirStr + 1: - 3]
    mod_name = '.'.join(tailPathStr.split('/'))
    return mod_name
# end def

def doPylintByName(name, excludedModuleList):
    'Code check an individual module, return True on error or None for success.'
    mod_name = pathToModuleName( name )
    if mod_name in excludedModuleList:
        print "Skipping module:  " + mod_name
        return
    cmd = ' --rcfile ../.pylintrc --report=no ' + mod_name
    pylintDir = os.path.join( cingDirTmp, 'pylint' )
    pylintOutputFileName = os.path.join( pylintDir, mod_name + '.log')
#    nTdebug("Writing to " + pylintOutputFileName)
    if os.path.exists(pylintOutputFileName):
        os.unlink( pylintOutputFileName )
    pylint = ExecuteProgram('pylint', rootPath=cingPythonDir, redirectOutputToFile=pylintOutputFileName)
    status = pylint( cmd )
    if status:
        nTmessage("Pylint found some flaws or crashed for " + mod_name)
    else:
#        nTdebug("pylint was flawless for " + mod_name)
        pass 
    if not os.path.exists(pylintOutputFileName):
        # Will be created even if pylint found messages or crashed.
        nTerror("Failed to find pylint result file: " + pylintOutputFileName)
        return True        
# end def


def getParser():
    'Return instance of OptionParser'
    usage = "usage: cing [options]       use -h or --help for listing"

    parser = OptionParser(usage=usage, version=str(cingVersion))
    parser.add_option("--test",
                      action="store_true",
                      dest="test",
                      help="Run set of test routines to verify installations"
                     )
    parser.add_option("--testQ",
                      action="store_true",
                      dest="testQ",
                      help="Same as --test and simply grepping for any errors."
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
    parser.add_option("--info",
                      action="store_true",
                      dest="info",
                      help="Print some program info to stdout"
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
    parser.add_option("--initCyana",
                      dest="initCyana", default=None,
                      help="Initialize new project from *.cyana.tgz"
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
    parser.add_option("--doPylint",
                      dest="doPylint", default=None,                      
                      help="Do code analysis using pylint on those matching *.py excluding some.",
                      metavar="PYLINTFILE"
                     )
    parser.add_option("--doPylintsum",
                      dest="doPylintsum", default=None,                      
                      help="Do summary code analysis on previous pylint run.",
                      metavar="PYLINTSUMFILE"
                     )
    parser.add_option('-i', "--ipython",
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
    parser.add_option("--validateFastest",
                      action="store_true", dest="validateFastest", default=False,
                      help="Validate without external programs or imagery."
                     )
    parser.add_option("--validateCingOnly",
                      action="store_true", dest="validateCingOnly", default=False,
                      help="Validate without slower external programs."
                     )
    parser.add_option("--validateImageLess",
                      action="store_true", dest="validateImageLess", default=False,
                      help="Validate without imagery."
                     )
    parser.add_option("--shiftx",
                      action="store_true", default=False,
                      dest="shiftx",
                      help="Predict with shiftx"
                     )
    parser.add_option("--ranges",
                      dest="ranges", default=None,
                      help="Ranges for superpose, procheck, validate etc; e.g. A.503-547,A.550-598,B.800,B.802",
                      metavar="RANGES"
                     )
    parser.add_option("--ensemble",
                      dest="ensemble", default=None,
                      help="Models of the ensemble to use for superpose, procheck, validate etc; "+
                      "e.g. 0,3-8,10,20. Note that model numbers start at zero.",
                      metavar="ENSEMBLE"
                     )
    parser.add_option("--superpose",
                      action="store_true", default=False,
                      dest="superpose",
                      help="Do superposition; optionally uses RANGES"
                     )
    _doc = """Next option enables us to reuse CING wrapper code like in CingWrapper.csh for using scripts
    like: cing/NRG/weeklyUpdatePdbjMine.py"""
    parser.add_option("--nosave",
                      action="store_true",
                      dest="nosave",
                      help="Don't save on exit (default: save)"
                     )
    parser.add_option("--noProject",
                      action="store_true",
                      dest="noProject",
                      help="Start without opening a project (default: with project)"
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
    parser.add_option("-c", "--cores", "--ncpus", type='int',
                      action="store",
                      dest="ncpus",
                      help="Number of separate threads to start. Can be below or above number the number of physical/logical cpu cores."
                     )
    return parser
#end def

project = None # after running main it will be filled (unless options.noProject was set)

# pylint: disable=W0612
def yasara( project ):
    'Fire up a yasara shell from within CING'
    from cing.PluginCode.yasaraPlugin import yasaraShell # pylint: disable=W0404
    yasaraShell( project )
#end def

def startIpythonShell(
        in_template =  'CING \#>  ',
        in2_template = 'CING \#>> ',
        out_template = 'CING \#:  ',
        banner = '--------Dropping to IPython--------',
        exit_msg='--------Leaving IPython--------'
    ):
    iPythonVersionType = getIpythonVersionType()
    if iPythonVersionType == None:
        nTerror("Failed to getIpythonVersionType")
    elif iPythonVersionType == IPYTHON_VERSION_A:
        # The next import is missing in one OSX installation but is on all others.
        # The new way of doing this would be the below but that still fails on all OSX installs but the one above.
        # from IPython.frontend.terminal.embed import InteractiveShellEmbed 
        # The next method started to fail in 2012 see issue 329
        # pylint: disable=W0404
        # pylint: disable=E0611
        from IPython.Shell import IPShellEmbed #@UnresolvedImport
        ipshell = IPShellEmbed(
                               ['-prompt_in1',in_template], # Fails to be set correctly on ipython version 0.11.
                                banner=banner, exit_msg=exit_msg
                              )        
        ipshell()
    elif iPythonVersionType == IPYTHON_VERSION_B:
        # pylint: disable=W0404
        # pylint: disable=E0611
        from IPython.config.loader import Config  #@UnresolvedImport
        cfg = Config()
        cfg.PromptManager.in_template =  in_template 
        cfg.PromptManager.in2_template = in2_template
        cfg.PromptManager.out_template = out_template                
        IPython.embed(config=cfg, banner1 =banner, exit_msg=exit_msg) #@UnresolvedImport # pylint: disable=E1101
    else:
        nTerror("Got unexpected value %s from getIpythonVersionType" % str(iPythonVersionType))
    # end if 
#end def

  
def main():
    'Main entry point for all CING functionality. Use --help for a list of all options.'
    if not ( osType == OS_TYPE_MAC or
             osType == OS_TYPE_LINUX ):
        nTerror("CING only runs on mac or linux.")
        sys.exit(1)

    global project # pylint: disable=W0603
    # pylint: disable=W0601
    global options # pylint: disable=W0603

#    _root, file, _ext = nTpath(__file__)

    parser = getParser()
    (options, _args) = parser.parse_args()

    if options.verbosity >= 0 and options.verbosity <= 9:
        cing.verbosity = options.verbosity
    else:
        nTerror("set verbosity is outside range [0-9] at: " + options.verbosity)
        nTerror("Ignoring setting")
    # From this point on code may be executed that will go through the appropriate verbosity filtering

    if options.ncpus > 0:
        cing.ncpus = options.ncpus
        nTdebug("Set the number of threads for cing to: %d" % cing.ncpus)

    nTmessage(header)
    nTmessage(getStartMessage(ncpus=cing.ncpus))

    nTdebug(getInfoMessage())

    nTdebug('options: %s', options)
    nTdebug('args: %s', _args)

    # The weird location of this import is because we want it to be verbose.
#    from cing.core.importPlugin import importPlugin # This imports all plugins    @UnusedImport
    # JFD: already present in __init__.py.

    if options.test:
        if testOverall(namepattern="test_*.py"):
#        testOverall(namepattern="test_NTutils*.py")
            sys.exit(1)
        # end if
        sys.exit(0)
    # end if
    if options.test2:
        if testOverall(namepattern="test2_*.py"):
            sys.exit(1)
        # end if
        sys.exit(0)
    # end if
    if options.testQ:
        if testQuiet():
            sys.exit(1)
        # end if
        sys.exit(0)
    # end if
    
    # Bug in pylint requires mention of: Unable to consider inline option %r pylint: disable=I0010
    if options.doPylint:
        if doPylintOverall(options.doPylint):
            sys.exit(1)
        sys.exit(0)
    # end if
        
    if options.doPylintsum:
        if doPylintOverallSummary(options.doPylintsum):
            sys.exit(1)
        sys.exit(0)
    # end if
        
    #------------------------------------------------------------------------------------
    # Extended documentation
    #------------------------------------------------------------------------------------
    if options.doc:
        parser.print_help(file=sys.stdout)
        print __doc__
        sys.exit(0)
    #end if

    if options.pydoc:
        nTmessage('==> Serving documentation at http://localhost:9999')
        nTmessage('    Type <control-c> to quit')
        webbrowser.open('http://localhost:9999/cing.html')
        pydoc.serve(port=9999)
        sys.exit(0)
    #end if

    if options.info:
        nTmessage(getInfoMessage())
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
            nTmessage('-------------------------------------------------------------------------------' +
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
    if not options.noProject:
        parser.check_required('-n')

#    args = []
    _kwds = {}


    #------------------------------------------------------------------------------------
    # open project
    #------------------------------------------------------------------------------------
    if not options.noProject:
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
        elif options.initCyana:
            project = Project.open(options.name, status='new')
            project.initCyana(cyanaFolder=options.initCyana)
        elif options.initCcpn:
            project = Project.open(options.name, status='new')
#            if options.ensemble:
#                modelCount = len(asci2list( options.ensemble ))
            project.initCcpn(ccpnFolder=options.initCcpn)
    #    elif options.loadCcpn:
    #        project = Project.open(options.name, status='create', restore=False)
    #        project.initCcpn(ccpnFolder=options.loadCcpn)
        else:
            project = Project.open(options.name, status='create')

        if not project:
            nTdebug("No project, doing a hard system exit")
            sys.exit(2)
        #end if
        if not options.noProject and not project.molecule:
            nTdebug("No project.molecule, doing a hard system exit")
            project.close()
            sys.exit(2)

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

        if options.ranges:
            project.molecule.setRanges(options.ranges)

        nTmessage(project.format())

        # shortcuts
        p = project
        mol = project.molecule #@UnusedVariable # pylint: disable=W0612        
        m = project.molecule #@UnusedVariable # pylint: disable=W0612

#        nTdebug("p.molecule.ranges: %s" % p.molecule.ranges)
    #   pr = print
        f = pformat #@UnusedVariable # pylint: disable=W0612
        fa = pformatall #@UnusedVariable # pylint: disable=W0612

        if options.ensemble:
    #        nTdebug( "Truncating the ensemble because ensemble option was set to: [" +options.ensemble+"]" )
            mol.keepSelectedModels( options.ensemble )
    #    else:
    #        nTdebug( "ensemble option was not found." )

        #------------------------------------------------------------------------------------
        # Import xeasy protFile
        #------------------------------------------------------------------------------------
        if options.xeasy:
            xeasy = options.xeasy.split(',')
            if (len(xeasy) != 3):
                nTerror("--xeasy=SEQFILE,PROTFILE,CONVENTION arguments required")
            else:
                project.importXeasy(seqFile=xeasy[0], protFile=xeasy[1], convention=xeasy[2])

        #------------------------------------------------------------------------------------
        # Import xeasy peakFile
        #------------------------------------------------------------------------------------
        if options.xeasyPeaks:
            xeasy = options.xeasyPeaks.split(',')
            if len(xeasy) != 4:
                nTerror("--xeasyPeaks=SEQFILE,PROTFILE,PEAKFILE,CONVENTION arguments required")
            else:
                project.importXeasyPeaks(seqFile=xeasy[0], protFile=xeasy[1], peakFile=xeasy[2], convention=xeasy[3])

        #------------------------------------------------------------------------------------
        # Merge resonances
        #------------------------------------------------------------------------------------
        if options.merge:
            project.mergeResonances()
        #end if

        #------------------------------------------------------------------------------------
        # Generate peaks
        #------------------------------------------------------------------------------------
        if options.generatePeaks:
            gp = options.generatePeaks.split(',')
            if len(gp) != 2:
                nTerror("--generatePeaks: EXP_NAME,AXIS_ORDER arguments required")
            else:
                peaks = project.generatePeaks(experimentName=gp[0], axisOrder=gp[1]) #@UnusedVariable # pylint: disable=W0612
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
            project.superpose() # will use the ranges set to molecule

        #------------------------------------------------------------------------------------
        # Validate
        #------------------------------------------------------------------------------------
        if options.validate or options.validateFastest or options.validateCingOnly or options.validateImageLess:
            project.validate(validateFastest = options.validateFastest, validateCingOnly = options.validateCingOnly, 
                             validateImageLess = options.validateImageLess)
        #end if
    # end if noProject

    #------------------------------------------------------------------------------------
    # Script
    #------------------------------------------------------------------------------------
    if options.script:
        scriptFile = scriptPath(options.script)
        if scriptFile:
            nTmessage('==> Executing script "%s"', scriptFile)
            execfile(scriptFile, globals() )
        #end if
    #end if
    if options.ipython:
        startIpythonShell()
    #end if
    if project:
        if options.yasara:
            yasara(project)
    #end if

    if project and  options.export:
        project.export()
    #end if
    if project:
        project.close(save=not options.nosave)
    #end if
# end def

if __name__ == '__main__':
    try:
        main()
    finally:
        nTmessage(getStopMessage(starttime))
