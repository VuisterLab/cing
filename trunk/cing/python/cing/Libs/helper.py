from subprocess import PIPE
from subprocess import Popen
import urllib2
import os

"""Very simple functions only here that can be instantiated without the general CING setup.
Called from cing's main __init__.py and setup.py.
"""

#Block to keep in sync with the one in helper.py
#===============================================================================
def _NTgetoutput( cmd ):
    """Return output from command as (stdout,sterr) tuple"""
#    inp,out,err = os.popen3( cmd ) # not forward compatible to python 2.6.
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    (inp,out,err) = (p.stdin, p.stdout, p.stderr)

    output = ''
    for line in out.readlines():
        output += line
    errors = ''
    for line in err.readlines():
        errors += line
    inp.close()
    out.close()
    err.close()
    return (output,errors)
def _NTerror(msg):
    print "ERROR:",msg
def _NTwarning(msg):
    print "WARNING:",msg
def _NTmessage(msg):
    print msg
#===============================================================================

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
    except:
        pass
#        _NTwarning("Failed to getSvnRevision()" )
    return None
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
         ncpus = int(os.environ["NUMBER_OF_PROCESSORS"]);
         if ncpus > 0:
             return ncpus
 return 1 # Default
