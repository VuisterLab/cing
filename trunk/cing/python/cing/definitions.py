import cing.Libs.helper as helper
import cing.Libs.disk as disk
import cing.constants as constants
import cing.Libs.Adict as Adict
import os
import sys
from ConfigParser import ConfigParser


#-----------------------------------------------------------------------------
# Verbosity settings: How much text is printed to stdout/stderr streams
# Follows exact same int codes as Wattos.
# Reference to it as cing.verbosity if you want to see non-default behavior
#-----------------------------------------------------------------------------
verbosityNothing  = 0 # Even errors will be suppressed
verbosityError    = 1 # show only errors
verbosityWarning  = 2 # show errors and warnings
verbosityOutput   = 3 # and regular output DEFAULT
verbosityDetail   = 4 # show more details
verbosityDebug    = 9 # add debugging info (not recommended for casual user)

verbosityDefault  = verbosityOutput
try:
    from cing.localConstants import verbosityDefault
except:
    pass
#end try
verbosity =  verbosityDefault
try:
    from cing.localConstants import verbosity
except:
    pass
#end try

#-----------------------------------------------------------------------------
# System definitions
#-----------------------------------------------------------------------------
systemDefinitions = helper.SystemDefinitions()

#-----------------------------------------------------------------------------
# General CING definitions
#-----------------------------------------------------------------------------
class CingDefinitions(Adict.Adict):
    def __init__(self):
        Adict.Adict.__init__(self)
        self.programName     = constants.CING
        self.longProgramName = 'CING: Common Interface for NMR structure Generation version'
        self.version         = 1.0
        self.date            = '30 Jan 2014'

        self.codePath        = disk.Path(__file__)[:-1] # all relative from this path
        self.rootPath        = self.codePath[:-2]
        self.libPath         = self.codePath / 'Libs'
        self.pluginCodePath  = self.codePath / 'PluginCode'
        self.pluginCode      = 'cing.PluginCode' # used in importPluging

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

        self.revision        = helper.getSvnRevision(self.rootPath)
        self.revisionUrl     = 'http://code.google.com/p/cing/source/detail?r=%s' % self.revision
        self.issueUrl        = 'http://code.google.com/p/cing/issues/detail?id='

        self.authors         = [  ('Geerten W. Vuister',          'gv29@le.ac.uk'),
                                  ('Jurgen F. Doreleijers',       'jurgend@cmbi.ru.nl'),
                                  ('Alan Wilter Sousa da Silva',  'alanwilter@gmail.com'),
                               ]

        self.copyright       = 'Copyright (c) 2004-2014: Department of Biochemistry, University of Leicester, UK'
        self.credits         = 'More info at http://nmr.le.ru.nl'

        self.verbosity       = verbosity
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
# General CING settings
#-----------------------------------------------------------------------------
class ValidationSettings(Adict.Adict):

    #: CRV stands for CRiteria Value CRS stands for CRiteria String
    CRV_NONE = "-999.9"

    def __init__(self, configurationFile = cingDefinitions.codePath / 'valSets.cfg'):
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

def getInfoMessage():
    """Get all the info there is to get
    """
    l = max(map(len, cingDefinitions.keys()+systemDefinitions.keys()))
    fmt = '{key:%s} : {value}\n' % l
    #print '>>', fmt

    result = '-'*80 +'\n'
    result += cingDefinitions.formatItems(fmt)
    result += systemDefinitions.formatItems(fmt)
    result += '-'*80
    return result
#end def

# pydoc settings
__version__            = cingDefinitions.version
__date__               = cingDefinitions.date
__copyright_years__    = '2004-' + cingDefinitions.date.split()[-1] # Never have to update this again...
__author__             = cingDefinitions.getAuthorsString()
__copyright__          = cingDefinitions.copyright
__credits__            = cingDefinitions.credits + '  ' + __copyright__