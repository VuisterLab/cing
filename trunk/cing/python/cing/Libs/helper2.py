"""
Most simplest functionality without reference to CING api
"""

from subprocess import PIPE
from subprocess import Popen

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
