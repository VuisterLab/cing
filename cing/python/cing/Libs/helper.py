"""
Very simple functions only here that can be instantiated without the general CING setup.
Called from cing's main __init__.py and setupCing.py.
"""
from subprocess import PIPE
from subprocess import Popen
import IPython
import os
import platform
import sys
import time
import urllib2

#import cing.Libs.Adict as Adict

#-----------------------------------------------------------------------------------
# Synchronize block with cing.Libs.helper.py
#-----------------------------------------------------------------------------------
def _nTgetoutput( cmd ):
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
def _nTerror(msg):
    'Convenience method'
    print "ERROR:",msg
# end def
def _nTwarning(msg):
    'Convenience method'
    print "WARNING:",msg
# end def
def _nTmessage(msg):
    'Convenience method'
    print msg
# end def
#-----------------------------------------------------------------------------------

#OBSOLETE
# def getSvnRevision( path ):
#     """Return the revision number (int) or -1 if the revision isn't known.
#     It depends on (proper) svn being available on the system."""
#     try:
#         cingSvnInfo, err = _nTgetoutput('svn info %s' % path)
#         #_nTmessage("cingSvnInfo: " + cingSvnInfo)
#         #_nTmessage("err: " + err)
#         if not err:
#             cingSvnInfoList = cingSvnInfo.split('\n')
#             for cingSvnInfo in cingSvnInfoList:
#                 if  cingSvnInfo.startswith('Revision:'):
#                     cingRevisionStr = cingSvnInfo.split()[ - 1]
#                     cingRevision = int(cingRevisionStr)
#                     return cingRevision
#                 # end if
#             # end for
#         # end if
#     except:
#         pass
# #        _nTwarning("Failed to getSvnRevision()" )
#     return -1
# # end def

def getIpythonVersionTuple(reportAsIs = False):
    """
    Return a tuple of iPython version ids such as
    (0, 10, 1) older or
    (0, 12) current.
    Returns None on error.
    """
    iPythonVersion = None
    try:
        if reportAsIs:
            return IPython.__version__
        # end if
        iPythonVersionStr = IPython.__version__.split('.')
        iPythonVersion = [ int(x) for x in iPythonVersionStr]
    except:
        _nTwarning("Failed to getIpythonVersion()" )
    # end try
    return iPythonVersion
# end def


def getIpythonVersionType():
    """
    Return IPYTHON_VERSION_XXXX

    Make sure they match the defs in constants.py
    IPYTHON_VERSION_A = 'iPythonVersion_A'
    IPYTHON_VERSION_B = 'iPythonVersion_B'

    Returns None on error.
    """
    iPythonVersionTuple = getIpythonVersionTuple()
    if iPythonVersionTuple == None:
        _nTerror("Failed to getIpythonVersionTuple")
        return None
    # end if

    c = compareVersionTuple(iPythonVersionTuple, (0,11))
    if c == None:
        _nTerror("Failed to compareVersionTuple")
        return None
    # end if
    if c >= 0:
        return 'iPythonVersion_B'
    # end if
    return 'iPythonVersion_A'
# end def


def compareVersionTuple( t1, t2):
    '''
    Return 1,0,-1 for the normal comparison operator as in Java.

    t1    t2    result
    2   > 1     1
    1   < 2     0
    1   < 2    -1
    1,2 > 1     1
    Return None on error.
    Example application: iPython version tuples such as '0.12'
    See test_helper.py unit tests.
    '''
    if t1 == None:
        _nTerror("Input 1 of compareIpythonVersionTuple is None" )
        return None
    # end if
    if t2 == None:
        _nTerror("Input 2 of compareIpythonVersionTuple is None" )
        return None
    # end if
    lt1 = len(t1)
    lt2 = len(t2)
    for i in range(max(lt1,lt2)):
        if lt1 <= i:
            if lt2 <= i:
                return 0
            else:
                return -1
            # end if
        # end if
        if lt2 <= i:
            return 1
        # end if
        v1 = t1[i]
        v2 = t2[i]
        if v1 == v2:
            continue
        # end if
        if v1 > v2:
            return 1
        # end if
        return -1
    # end for
    return 0
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

def getOsRelease():
    """Return the release string; unix style (not 10.8 but 12.0.0 at time of writing)."""
    # system,node,release,version,machine,processor
    unameList = platform.uname()
    return unameList[2]
# end def

