from subprocess import PIPE
from subprocess import Popen
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


