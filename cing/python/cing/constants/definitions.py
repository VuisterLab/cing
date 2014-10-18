import os
import sys
import platform
import time
from ConfigParser import ConfigParser
#
import cing
from cing.Libs import Adict
from cing.Libs import disk
from cing.Libs import helper
from cing.Libs import io

#-----------------------------------------------------------------------------
# pydoc settings
#-----------------------------------------------------------------------------
__version__         = cing.__version__
__revision__        = cing.__revision__
__date__            = cing.__date__
__author__          = cing.__author__
__copyright__       = cing.__copyright__
__copyright_years__ = cing.__copyright_years__
__credits__         = cing.__credits__

#-----------------------------------------------------------------------------
# System definitions
#-----------------------------------------------------------------------------
class SystemDefinitions(Adict.Adict):
    """A class to store system definitions and system related data
    """
    def __init__(self):
        Adict.Adict.__init__(self)
        self.osType = helper.getOsType()
        self.osRelease = helper.getOsRelease()
        self.osArchitecture = platform.architecture()[0]
        self.nCPU = helper.detectCPUs()
        self.internetConnected = helper.isInternetConnected()
        self.startTime = io.now()
        self.pid = os.getpid()
        self.user = os.getenv("USER", "Unknown user")
        self.host = os.getenv("HOST", "Unknown host") #only works with (t)csh shell
    #end def

    def elapsedTime(self):
        return time.time() - self.startTime

    def getStartMessage(self):
        on = "%s (%s%s/%s/%scores/py%s)" % (self.host, self.osType, self.osRelease, self.osArchitecture, self.nCPU, sys.version.split()[0])
        at = '(pid:%d) %s' %  (self.pid, self.startTime)
        return "User: %-10s on: %-42s at: %32s" % (self.user, on, at)

    def getStopMessage(self):
        now = io.now()
        return 'Started at: %s\nStopped at: %s\nTook      : %.1f seconds' % (self.startTime, now, now-self.startTime)

    def __str__(self):
        return '<SystemDefinitions: osType=%s, osRelease=%s, osArchitecture=%s, nCPU=%s, internetConnected=%s, host=%s, startTime=%s, pid=%s, user=%s>' % \
                (self.osType, self.osRelease, self.osArchitecture, self.nCPU, self.internetConnected, self.host, self.ascTime(), self.pid, self.user)
#end class
systemDefinitions = SystemDefinitions()

#-----------------------------------------------------------------------------
# General CING definitions
#-----------------------------------------------------------------------------
class CingDefinitions(Adict.Adict):
    def __init__(self):
        Adict.Adict.__init__(self)
        self.programName     = 'CING'
        self.longProgramName = 'CING: Common Interface for NMR structure Generation version'
        self.version         = cing.__version__
        self.date            = '15 Oct 2014'

        self.codePath        = disk.Path(__file__)[:-2] # all relative from this path, also assures a Path object
        self.rootPath        = self.codePath[:-2]
        self.libPath         = self.codePath / 'Libs'
        self.pluginPath      = self.codePath / 'PluginCode'
        self.pluginCode      = 'cing.PluginCode' # used in importPlugin

        self.binPath         = self.rootPath / 'bin'
        self.htmlPath        = self.rootPath / 'HTML'

        self.tmpdir          = disk.Path('/tmp') / "cing.tmpdir." + str(systemDefinitions.pid)
        # The TMPDIR environment variable will override the default above but not the one that
        # might be defined in localConstants.py.
        try:
            from cing.localConstants import tmpdir #@UnresolvedImport # pylint: disable=E0611
            self.tmpdir      = disk.Path(tmpdir) / "cing.tmpdir." + str(systemDefinitions.pid)
        except:
            if os.environ.has_key("TMPDIR"):
                self.tmpdir  = disk.Path(os.environ["TMPDIR"]) / "cing.tmpdir." + str(systemDefinitions.pid)
            #end if
        #end try

        self.revision        = cing.__revision__
        self.revisionUrl     = 'http://code.google.com/p/cing/source/detail?r=%s' % self.revision
        self.issueUrl        = 'http://code.google.com/p/cing/issues/detail?id='

        self.authors         = [  ('Geerten W. Vuister',          'gv29@le.ac.uk'),
                                  ('Jurgen F. Doreleijers',       'jurgenfd@gmail.com'),
                                  ('Alan Wilter Sousa da Silva',  'alanwilter@gmail.com'),
                               ]

        # self.copyright       = 'Copyright (c) 2004-2014: Department of Biochemistry, University of Leicester, UK'
        # self.credits         = 'More info at http://nmr.le.ac.uk'
        self.copyright       = cing.__copyright__
        self.credits         = cing.__credits__
    #end def

    def getVersionString(self):
        return '%s (revision %s)' % (self.version, self.revision)

    def getAuthorsString(self):
        result = ''
        for a,e in self.authors[:2]:
            result += '%s (%s) ' % (a, e)
        #end for
        return result.strip()
    #end def

    def getHeaderString(self):
        text = [' %s %s' % (self.longProgramName, self.getVersionString()),
                '',
                ' %s' % (self.getAuthorsString(),),
                '',
                ' %s' % (self.copyright,),
                ' %s' % (self.credits,)
               ]
        l = max(map(len,text))+1
        header = '%s\n' % ('='*l,)
        for line in text:
            header += '%s\n' % line
        header += '%s' % ('='*l,)
        return header
    #end def
#end class
cingDefinitions = CingDefinitions()

#-----------------------------------------------------------------------------
# Directory definitions
#-----------------------------------------------------------------------------

# These directories get created. They are defined relative to project root path,
# can be joined relative to project root by Project.path( *args ) method or
# via myProject.path() / directories.xyz syntax of the Path class.
directories = Adict.Adict(
    data       = 'Data',
    molecules  = 'Data/Molecules',      # molecule data
    peaklists  = 'Data/Peaklists',      # peak lists data
    restraints = 'Data/Restraints',     # restraint data
    ccpn       = 'Data/Ccpn',           # ccpn data
    sources    = 'Data/Sources',        # source data
    version1   = 'Data/Version1',       # legacy version 1 files
#    database   = 'Data/Database',
#    plugins    = 'Data/Plugins',        # plugin data (only in V3)
    validation = 'Data/Validation',     # validation data
    logs       = 'Logs',
    export     = 'Export',
    xeasy      = 'Export/Xeasy',
    xeasy2     = 'Export/Xeasy2',
    nih        = 'Export/NIH',
    sparky     = 'Export/Sparky',
    PDB        = 'Export/PDB',
    xplor      = 'Export/Xplor',
    aqua       = 'Export/Aqua',
    queen      = 'Queen',
    refine     = 'Refine',
    tmp        = 'Temp'
)

#DEPRECIATED:
# in V3 these data will be under Data/Plugins and are to be created by the
# plugin code itself
# V1 These directories get created upon opening/appending a molecule to project
validationDirectories = Adict.Adict(
    # Directories generated
    procheck   = 'Procheck',
    dssp       = 'Dssp',
    whatif     = 'Whatif',
    wattos     = 'Wattos',
    x3dna      = 'X3DNA',
    analysis   = 'Cing',
    shiftx     = 'Shiftx',
    ccpn       = 'Ccpn',
    html       = 'HTML',
    macros     = 'Macros',
    jmol       = 'Macros/Jmol',
    pymol      = 'Macros/pyMol',
    yasara     = 'Macros/Yasara',
    molmol     = 'Macros/Molmol'
)

# These directories get generated below the HTML root of a molecule
htmlDirectories = Adict.Adict(
    molecule    = 'Molecule',
#    atoms       = 'Atoms',
    models      = 'Molecule/Models',
    restraints  = 'Restraints',
    dihedrals   = 'Dihedrals',
    peaks       = 'Peaks'
)

# These files and directories are just definitions
cingPaths = Adict.Adict(
    project      = 'project.json',
    validation   = 'validation.json',
    scripts      = 'Scripts',
    html         = 'HTML',
    css          = 'cing.css',
    xplor        = os.getenv('xplorPath'),
    procheck_nmr = os.getenv('procheckPath'),
    aqpc         = os.getenv('aqpcPath'),
    whatif       = os.getenv('whatifPath'),
    dssp         = os.getenv('dsspPath'),
    convert      = os.getenv('convertPath'),
    ghostscript  = os.getenv('ghostscriptPath'),
    ps2pdf       = os.getenv('ps2pdfPath'),
    molmol       = os.getenv('molmolPath'),
    povray       = os.getenv('povrayPath'),
    talos        = os.getenv('talosPath'),
    classpath    = os.getenv('CLASSPATH')   # Watto's related
)


#-----------------------------------------------------------------------------
# Validation settings
#-----------------------------------------------------------------------------
class ValidationSettings(Adict.Adict):

    #: CRV stands for CRiteria Value CRS stands for CRiteria String
    CRV_NONE = "-999.9"

    def __init__(self, configurationFile = cingDefinitions.codePath / 'constants' / 'valSets.cfg'):
        Adict.Adict.__init__(self )
        self.configurationFile = disk.Path(configurationFile)
    #end def

    def readFromFile(self):
        """Reads the validation settings, return self or None on error
        """
        fn = self.configurationFile
        if not fn.exists():
            helper._nTerror("ValidationSettings.ReadFromFile: Input file does not exist at: " + fn)
            return None

#        nTdebug("ValidationSettings.ReadFromFile: Reading validation file: " + fn)
        config = ConfigParser()
        config.readfp(open(fn))
        for item in config.items('DEFAULT'):
            key = item[0].upper()  # upper only.
            try:
                if item[1] == ValidationSettings.CRV_NONE:
                    value = None
                else:
                    value = float(item[1])
            except ValueError:
                try:
                    value = bool(item[1])
                except:
                    value = item[1]
            #end try

            #GWV: no idea what is the reason here: JFD magic
            valueStr = repr(value)
            if self.has_key(key):
                valueFromStr = repr(self[key])
                if valueStr == valueFromStr:
                    continue  # no print
#                nTdebug("Replacing value for key " + key + " from " + valueFromStr + " with " + valueStr)
            else:
#                nTdebug("Adding              key " + key + " with value: " + valueStr)
                pass
            #end if
            self[key] = value # name value pairs.
        #end for
        return self
    #end def
#end class
validationSettings = ValidationSettings().readFromFile()
#-----------------------------------------------------------------------------

