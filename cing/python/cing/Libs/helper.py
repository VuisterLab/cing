"""
Very simple functions only here that can be instantiated without the general CING setup.
Called from cing's main __init__.py and setupCing.py.
"""
from subprocess import PIPE
from subprocess import Popen
import os
import platform
import sys
import time
import urllib2

#-----------------------------------------------------------------------------------
# Synchronize block with cing.Libs.helper.py
#-----------------------------------------------------------------------------------
def _NTgetoutput( cmd ):
    """Return output from command as (stdout,sterr) tuple"""
#    inp,out,err = os.popen3( cmd )
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    (inpStream,outStream,errStream) = (p.stdin, p.stdout, p.stderr)

    output = ''
    for line in outStream.readlines():
        output += line
    errors = ''
    for line in errStream.readlines():
        errors += line
    inpStream.close()
    outStream.close()
    errStream.close()
    return (output,errors)
# end def
def _NTerror(msg):
    'Convenience method'
    print "ERROR:",msg
# end def
def _NTwarning(msg):
    'Convenience method'
    print "WARNING:",msg
# end def
def _NTmessage(msg):
    'Convenience method'
    print msg
# end def
#-----------------------------------------------------------------------------------

def getSvnRevision():
    """Return the revision number (int) or None if the revision isn't known. It depends on svn being available on the system."""
#    return None
    try:
        cingSvnInfo, err = _NTgetoutput('svn info %s' % os.getenv("CINGROOT"))
        #_NTmessage("cingSvnInfo: " + cingSvnInfo)
        #_NTmessage("err: " + err)
        if not err:
            cingSvnInfoList = cingSvnInfo.split('\n')
            for cingSvnInfo in cingSvnInfoList:
                if  cingSvnInfo.startswith('Revision:'):
                    cingRevisionStr = cingSvnInfo.split()[ - 1]
                    cingRevision = int(cingRevisionStr)
                    return cingRevision
                # end if
            # end for
        # end if
    except:
        pass
#        _NTwarning("Failed to getSvnRevision()" )
# end def

def isInternetConnected():
    """Retrieves about 6 kbytes from google; takes 0.2 seconds on fast network."""
    url = 'http://www.google.com'
    req = urllib2.Request(url=url)
    result = None
    try:
        f = urllib2.urlopen(req)
        result = f.readlines()
    except:
#        print "DEBUG: Failed to find internet connection to: %s\nDEBUG: Presuming internet is down." % url
        pass

    if result:
#        print "DEBUG: isInternetConnected retrieved from %s:\n%s" % (url,result)
        return True
    return False
# end def

def detectCPUs():
    """
    Detects the number of CPUs on a system. Cribbed from pp.
    """
    # Linux, Unix and MacOS:
    if hasattr(os, "sysconf"):
        if os.sysconf_names.has_key("SC_NPROCESSORS_ONLN"):
            # Linux & Unix:
            ncpus = os.sysconf("SC_NPROCESSORS_ONLN")
            if isinstance(ncpus, int) and ncpus > 0:
                return ncpus
        else: # OSX:
            return int(os.popen2("sysctl -n hw.ncpu")[1].read())
    # Windows:
    if os.environ.has_key("NUMBER_OF_PROCESSORS"):
        ncpus = int(os.environ["NUMBER_OF_PROCESSORS"])
        if ncpus > 0:
            return ncpus
    return 1 # Default
# end def

def getOsType():
    """Return the type of OS, mapped to either darwin, linux, or windows from sys.platform"""

    # Known platforms to JFD.
    _platformMap = {
        'darwin': 'Darwin',
        'win32': 'Microsoft Windows',
        'linux2': 'Linux', # Ubuntu 10.9 on 64 bit and others
        'sunos5': 'Solaris',
        'freebsd6': 'FreeBSD 6.0'
    }
    # make sure they match the defs in constants.py
#OS_TYPE_MAC = 'darwin'
#OS_TYPE_LINUX = 'linux'
#OS_TYPE_WINDOWS = 'windows' # unsupported.
#OS_TYPE_UNKNOWN = 'unknown'

    if sys.platform.startswith('darwin'):
        return 'darwin'
    if sys.platform.startswith('linux'):
        return 'linux'
    if sys.platform.startswith('sunos'): # Probably needs it's own type in future.
        return 'linux'
    if sys.platform.startswith('win'):
        return 'windows'
    return 'unknown'
# end def

def getStartMessage(ncpus=None):
    """
    Copy catted from xplor
    user = "jd"
    on   = "Stella.local (darwin/32bit/2cores/2.6.6)
    at   = "(3676) 29-Oct-08 15:36:22

    ncpus will be detected if not presented. Derive it from cing.ncpus and pass it in here is normal operation.
    """
    user = os.getenv("USER", "Unknown user")
    machine = os.getenv("HOST", "Unknown host") #only works with (t)csh shell
    if not ncpus:
        ncpus = detectCPUs()
#    ostype = os.getenv("OSTYPE", "Unknown os") #only works with (t)csh shell
    osType = getOsType()
    on = "%s (%s/%s/%scores/%s)" % (machine, osType, platform.architecture()[0], ncpus, sys.version.split()[0])
    at = time.asctime()
    pid = os.getpid()
    at = '(%d) ' %  pid + at
#    atForFileName = "%s" % at
#    atForFileName = re.sub('[ :]', '_', atForFileName)
    return "User: %-10s on: %-42s at: %32s" % (user, on, at)
    #(3737) Thu Oct 21 11:19:30 2010
    #Stella.local (darwin/32bit/2cores/2.6.6)
# end def

def getStopMessage(starttime):
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
# end def
