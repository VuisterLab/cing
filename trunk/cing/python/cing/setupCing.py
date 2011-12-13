#!/usr/bin/env python
"""
python setupCing.py
E.g.:
python $CINGROOT/python/cing/setupCing.py -tcsh

Generates either cing.csh or cing.sh to source in your .cshrc or .bashrc
(or equivalent) respective file

Adjust if needed.

GV:  16 Sep 2007: added cingBinPath and profitPath
JFD: 27 Nov 2007: removed again.
GV:  13 Jun 2008: Added CYTHON path and refine, cyana2cing and cython aliases
JFD: 26 May 2009: Added pyMol path

Uses 'which xplor/$prodir/procheck_nmr.scr/DO_WHATIF.COM' to determine initial
xplor/procheck/what if executables; make sure they are in your
path when you run setup. If they are not; you may continue without their
respective functionalities.
"""

# Please note the lack of imports here to cing specific code.
# The idea is that this script runs without PYTHONPATH being set yet.
from string import atoi
from string import strip
from subprocess import PIPE
from subprocess import Popen
import os
import sys
#import warnings

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
def _getSvnRevision( envRootDir = 'CINGROOT'):
    """Return the revision number (int) or None if the revision isn't known. It depends on svn being available on the system."""
#    return None
    try:
        cingSvnInfo, err = _NTgetoutput('svn info %s' % os.getenv(envRootDir))
        #_nTmessage("cingSvnInfo: " + cingSvnInfo)
        #_nTmessage("err: " + err)
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
#        _nTwarning("Failed to getSvnRevision()" )
# end def


#-----------------------------------------------------------------------------------

# disabling some output that can safely be ignored
#warnings.simplefilter('ignore', category=UserWarning)
# fixed problem instead now.

PLEASE_ADD_EXECUTABLE_HERE = "PLEASE_ADD_EXECUTABLE_HERE"
CING_SHELL_TEMPLATE = \
'''
#############################################
# adjust these, if needed
#############################################
%(export)s  xplorPath%(equals)s%(xplorPath)s
%(export)s  procheckPath%(equals)s%(procheckPath)s
%(export)s  aqpcPath%(equals)s%(aqpcPath)s
%(export)s  whatifPath%(equals)s%(whatifPath)s
%(export)s  dsspPath%(equals)s%(dsspPath)s
%(export)s  convertPath%(equals)s%(convertPath)s
%(export)s  ghostscriptPath%(equals)s%(ghostscriptPath)s
%(export)s  ps2pdfPath%(equals)s%(ps2pdfPath)s
%(export)s  molmolPath%(equals)s%(molmolPath)s
%(export)s  povrayPath%(equals)s%(povrayPath)s
%(export)s  talosPath%(equals)s%(talosPath)s
#############################################
# No changes needed below this line.
#############################################
%(export)s  CINGROOT%(equals)s%(cingRoot)s
%(export)s  CYTHON%(equals)s%(cingRoot)s/dist/Cython
%(export)s  PYMOL_PATH%(equals)s%(pyMolPath)s

# Adding each component individually to PYTHONPATH
%(export)s  CING_VARS%(equals)s$CINGROOT/python
%(export)s  CING_VARS%(equals)s${CING_VARS}:$CYTHON
%(export)s  CING_VARS%(equals)s${CING_VARS}:$PYMOL_PATH/modules
%(export)s  CING_VARS%(equals)s${CING_VARS}:%(yasaraPath)s/pym:%(yasaraPath)s/plg

if %(conditional)s then
    %(export)s PYTHONPATH%(equals)s${CING_VARS}:${PYTHONPATH}
else
    %(export)s PYTHONPATH%(equals)s${CING_VARS}
%(close_if)s

# Use -u to ensure messaging streams for stdout/stderr don't mingle (too much).
alias cing%(equals)s'python -u $CINGROOT/python/cing/main.py'
alias queen%(equals)s'python -u $CINGROOT/python/queen/main.py'
alias cyana2cing%(equals)s'python -u $CINGROOT/python/cyana2cing/cyana2cing.py'
alias refine%(equals)s'python -u $CINGROOT/python/Refine/refine.py'
alias cython%(equals)s'$CYTHON/bin/cython'

'''
# make the addition conditional to presence like for tcsh.
#if ( $PYMOL_PATH != 'PLEASE_ADD_EXECUTABLE_HERE' ) then
#    setenv  CING_VARS ${CING_VARS}:$PYMOL_PATH/modules
#endif

#------------------------------------------------------------------------------------

######################################################################################################
# This code is repeated in __init__.py and setupCing.py please keep it sync-ed
cingPythonCingDir = os.path.split(os.path.abspath(__file__))[0]
# The path to add to your PYTHONPATH thru the settings script generated by cing.core.setupCing.py
cingPythonDir = os.path.split(cingPythonCingDir)[0]
# Now a very important variable used through out the code. Even though the
# environment variable CINGROOT is defined the same this is the preferred
# source for the info within the CING python code.
cingRoot = os.path.split(cingPythonDir)[0]
#nTdebug("cingRoot        : " + cingRoot)
######################################################################################################

######################################################################################################
# This code is repeated in cing/setupCing.py and cing/Libs/NTutils.py please keep it sync-ed
######################################################################################################

def check_python():
    'Python needs to be at least 2 but below 3.'
    hasDep = True
    version = float(sys.version[:3])
    if version < 2.5 or version >= 3.0:
        _nTerror('Failed to find Python version 2.5 or higher and not 3 or above.')
        _nTerror('Current version is %s' % sys.version[:5])
        _nTerror("Python 2.4 in the package managers such as yum, fink, port, and apt " + 
                 "come with a 'matplotlib' version that doesn't work with CING.")
        hasDep = False
    if hasDep:
        _nTmessage("........ Found 'python'        %s" % str(version))
        
        
    else:
        _nTwarning('Failed to find good python.')

def check_matplotlib():
    """
    matplotlib needs to be at 0.98.3-1 or higher.
    Version 0.99.3 fails to plot tick labels in a nicely distributed fashion see Issue 318:    Matplotlib is misbehaving
    """
    try:
        from matplotlib.axis import XAxis
    except:
        _nTmessage("Could not find 'matplotlib' (optional)")
        return

    msg = 'Failed to find good matplotlib (optional). Look for version 0.98.3-1 or higher. Developed with 0.98.5-1'
    try:
        from matplotlib.pylab import axes
        xaxis = XAxis(axes([.1, .1, .8, .8 ]))
        if not hasattr(xaxis, 'convert_units'):
            _nTmessage('0 ' + msg)
            return
    except:
        _nTmessage('1 ' + msg)
        return

    try:
        import matplotlib.pylab #@UnusedImport # pylint: disable=W0612
    except:
        _nTmessage('Could not find matplotlib (b) (optional)')
        return
    
    #In [5]: matplotlib.__version__
    #Out[5]: '0.99.3'    
    versionTuple = matplotlib.__version__.split('.')
    versionTupleReq = ( 0, 98, 3 )
    versionTooLow = False
    if versionTuple[0] < versionTupleReq[0]:
        if versionTuple[1] < versionTupleReq[1]:
            if versionTuple[2] < versionTupleReq[2]:
                versionTooLow = True
            # end if
        # end if
    # end if
    if versionTooLow:
        _nTmessage("Could not find matplotlib at version required (%s): found %s" % (str(versionTupleReq), str(versionTuple)))
        return
    # end if
#    _nTmessage("DEBUG: Version found (%s) and version required (%s) comparison is: %s" % (
#        str(versionTuple), str(versionTupleReq), versionTooLow))
    _nTmessage("........ Found 'matplotlib'    %s" % matplotlib.__version__)


def check_ccpn():
    'ccpnmr is an opional python package.'
#    print '\nCCPN distribution:',
    missing = []
    gotRequiredCcpnModules = False
    try:
        import ccpnmr #@UnusedImport @UnresolvedImport # pylint: disable=W0612
        gotRequiredCcpnModules = True
#        print 'ok.'
    except:
        missing.append('ccpnmr')
#        print

    # JFD disabled these since they aren't used in CING (?yet).
#    try:
#        import ccpnmr.format #@UnusedImport @Reimport
#        _nTmessage("Found 'FormatConverter'")
#    except:
#        missing.append('ccpnmr.format')
#
#    try:
#        import ccpnmr.analysis #@UnusedImport @Reimport @UnresolvedImport
#        print 'Anaysis: ok.'
#    except:
#        missing.append('ccpnmr.analysis')

    if gotRequiredCcpnModules:
        envRootDir = 'CCPNMR_TOP_DIR'
        ccpnRevison = _getSvnRevision( envRootDir )
        _nTmessage("........ Found 'ccpn'          %s %s" % (ccpnRevison, os.getenv(envRootDir)))
    else:
        _nTmessage("Could not find 'ccpn' (optional)")

#    if missing:
#        _nTmessage( 'Missing (optional) packages: ' + ', '.join(missing))

# disabled for this needs to be no extra- dependency. A version of numarray should
# be in matplotlib. In fact the code doesn't refer to numarray anywhere. Or JFD
# can't find it. Did Alan meant to check for things like: from matplotlib.numerix import nan # is in python 2.6 ?
#def check_numarray():
#
#    print 'Numarray module   ',
#    result = 0
#    try:
#        import numarray #@UnusedImport
#        print 'ok.'
#        result = 1
#    except:
#        print 'could not import Numarray module.'
#
#    return result

# See above.
#def check_numpy():
#
#    print 'Numpy module   ',
#    result = 0
#    try:
#        import numpy #@UnusedImport
#        print 'ok.'
#        result = 1
#    except:
#        print 'could not import Numpy module.'
#
#    return result

def check_cython():
    'Mandatory cython python package'
#    print 'Cython module   ',
    result = 0
    try:
        import Cython.Distutils #@UnusedImport @UnresolvedImport # pylint: disable=W0612
#        print 'ok.'
        result = 1
#        print "Great you have Cython! Please try to compile CING's Cython libs running:"
#        print 'cd %s/python/cing/Libs/cython; python compile.py build_ext --inplace; cd -' % cingRoot

        # JFD disabled this until we get it to work on our Macs.
#        os.chdir(os.path.join(cingRoot,'python/cing/Libs/cython'))
#        out = call(['python', 'compile.py','build_ext', '--inplace'])
#        if out:
#            print '==> Failed to compile CING Cython libs.'
#            print '    Good chance it will run by hand, try running:\n%s' % cmd
#            print '    If your using Mac, see "https://bugs.launchpad.net/cython/+bug/179097"'
    except:
#        print 'failed to import Cython module.'
        pass

    if not result:
        _nTmessage('Failed to find cython (might be optional at this stage)')
    else:
        _nTmessage("........ Found 'cython'")

    return result

# JFD This one is even disabled in the test since some time now.
#def check_profiler():
#
#    print 'Profiler module   ',
#    result = 0
#    try:
#        import profile #@UnusedImport
#        print 'ok.'
#        result = 1
#    except:
#        print 'could not import Profiler module.'
#        print "it's not essencial but used with 'cing --test'."
#    return result


def _writeCingShellFile(isTcsh): # pylint: disable=W0621
    '''Generate the Cing Shell file for csh or bash'''
    if isTcsh:
        parametersDict['export'] = 'setenv'
        parametersDict['equals'] = ' '
        parametersDict['conditional'] = '($?PYTHONPATH)'
        parametersDict['close_if'] = 'endif'
        parametersDict['equals'] = ' '
        sourceCommand = 'source'
        cname = 'cing.csh'
    else:
        parametersDict['export'] = 'export'
        parametersDict['equals'] = '='
        parametersDict['conditional'] = '[ ! -z "${PYTHONPATH}" ];'
        parametersDict['close_if'] = 'fi'
        sourceCommand = '.'
        cname = 'cing.sh'
#    nTdebug("pars:" + repr(parametersDict))
    text = CING_SHELL_TEMPLATE % parametersDict
    if isTcsh:
        text += "\nrehash\n"
    cname = os.path.join( cingRoot, cname )
    fp = open(cname,'w')
    fp.write(text)
    fp.close()
    os.chmod(cname, 0755)

    print ''
    print '==> Please check/modify %s <===' % (cname)
    print '    Then activate it by sourcing it in your shell settings file (.cshrc or .bashrc):'
    print ''
    print '    %s %s' % ( sourceCommand, cname)
    print ''
    print ''
    print '==> Note by JFD'
    print ' There is another dependency; cython. Please install it and run:'
    print ' cd $CINGROOT/python/cing/Libs/cython; python compile.py build_ext --inplace'
    print ' After installing cython; rerun setupCing.py or manually update the settings file.'
    print ' We have included the Cython distribution needed so add to your PYTHONPATH for now:'
    print ' $CINGROOT/dist/Cython (later it will be added by the cing.[c]sh created.'

#end def
#------------------------------------------------------------------------------------


if __name__ == '__main__':
#    cing.verbosity = verbosityOutput # Default is no output of anything.

    isTcsh = None
    if len(sys.argv) > 1:
        if sys.argv[1] == '-tcsh':
            isTcsh = True
        elif sys.argv[1] == '-sh':
            isTcsh = False
        else:
            print 'Failed to process argument(s) in sys.argv: [' + str(sys.argv) + ']'
        # end if
    # end if
    envRootDir = 'CINGROOT'
    cingRevison = _getSvnRevision()
    _nTmessage("........ Found 'cing'          %s %s" % (cingRevison, os.getenv(envRootDir)) )       
    
    check_python()
    check_matplotlib()
    check_ccpn()
    check_cython()

    if not cingRoot:
        print "Failed to derive the CINGROOT from this setupCing.py script; are there other setupCing.py or code confusing me here?"
        sys.exit(1)

    if not os.path.exists(cingRoot):
        print "The derived CINGROOT does not exist: ["  + cingRoot + "]"
        sys.exit(1)

    if not cingPythonDir:
        print "Failed to derive the CING python directory from this setupCing.py script. No clue why?"
        sys.exit(1)

    parametersDict = {}
    parametersDict['cingPythonDir'] = cingPythonDir
    parametersDict['cingRoot']      = cingRoot

    xplorPath,err  = _NTgetoutput('which xplor')
    if not xplorPath:
        _nTmessage("Could not find 'xplor'  (optional)")
        parametersDict['xplorPath']  = PLEASE_ADD_EXECUTABLE_HERE
    else:
        xplorPath = strip(xplorPath)
        _nTmessage("........ Found 'xplor'         %s" % xplorPath)        
        parametersDict['xplorPath']  = xplorPath
    # end if
    # is now an alias like: env -i PATH=$PATH HOME=$HOME USER=$USER /Users/jd/workspace/xplor-nih-2.27/bin/xplor
#    parametersDict['xplorPath']  = 'xplor' 

#    procheckPath,err  = _NTgetoutput('which $prodir/procheck_nmr.scr')
    if os.environ.has_key("prodir"):
        procheckPath = os.path.join( os.environ["prodir"], "procheck_nmr.scr")
        if not os.path.exists(procheckPath):
            _nTwarning("Found the system variable prodir but the script below was not found")
            _nTwarning( procheckPath )
            _nTwarning("Could not find 'procheck_nmr'  (optional)")
            parametersDict['procheckPath']  = PLEASE_ADD_EXECUTABLE_HERE
        else:
            _nTmessage("........ Found 'procheck_nmr'  %s" % procheckPath)        
            parametersDict['procheckPath'] = procheckPath
        # end if
    else:
        _nTmessage("Could not find 'procheck_nmr'  (optional)")
        parametersDict['procheckPath']  = PLEASE_ADD_EXECUTABLE_HERE
    # end if

#    procheckPath,err  = _NTgetoutput('which $prodir/procheck_nmr.scr')
    if os.environ.has_key("aquaroot"):
        aqpcPath = os.path.join( os.environ["aquaroot"], "scripts", "aqpc")
        if not os.path.exists(aqpcPath):
            _nTwarning("Found the system variable aquaroot but the script below wasn't found")
            _nTwarning( aqpcPath )
            _nTwarning("Could not find 'aqua'  (optional)")
            parametersDict['aqpcPath']  = PLEASE_ADD_EXECUTABLE_HERE
        else:
            _nTmessage("........ Found 'aqua'          %s" % aqpcPath)
            parametersDict['aqpcPath'] = aqpcPath
        # end if
    else:
        _nTmessage("Could not find 'aqua'  (optional)")
        parametersDict['aqpcPath']  = PLEASE_ADD_EXECUTABLE_HERE
    # end if

    whatifPath,err  = _NTgetoutput('which DO_WHATIF.COM')
    parametersDict['whatifPath']  = PLEASE_ADD_EXECUTABLE_HERE
    parametersDict['dsspPath']    = PLEASE_ADD_EXECUTABLE_HERE
    if not whatifPath:
        defaultWhatifPath = '/home/vriend/whatif/DO_WHATIF.COM'
        if os.path.exists(defaultWhatifPath):
            whatifPath = defaultWhatifPath
    # end if
    if not whatifPath:
        _nTmessage("Could not find 'what if'  (optional)")
    else:
        whatifPath = strip(whatifPath)
        _nTmessage("........ Found 'what if'       %s" % whatifPath)
        
        parametersDict['whatifPath'] = whatifPath
        head, _tail = os.path.split( whatifPath )
        dsspPath = os.path.join( head, 'dssp', 'DSSP.EXE' )
        if not os.path.exists(dsspPath):
            _nTmessage("Could not find 'dssp'")
        else:
            _nTmessage("........ Found 'dssp'          %s" % dsspPath)
            parametersDict['dsspPath'] = dsspPath
        # end if
    # end if

    wattosRevision = -1
    try:
        envRootDir = 'WATTOSROOT'
        wattosRevision = _getSvnRevision( envRootDir )        
    except:
        pass
    # end try
        
#    nTdebug("time: " + repr(time))
    if wattosRevision < 0: # time at: Mon Dec 10 15:56:33 CET 2007
        _nTmessage("Could not find 'wattos'  (optional)")
#        _nTmessage("Failed to get epoch time. This was a test of Wattos installation.'")
    else:        
        _nTmessage("........ Found 'wattos'        %s %s" % (str(wattosRevision), os.getenv(envRootDir)) )
    # end if

    convertPath,err  = _NTgetoutput('which convert')
    if not convertPath:
        _nTwarning("Could not find 'convert' (from ImageMagick)")
        parametersDict['convertPath']  = PLEASE_ADD_EXECUTABLE_HERE
    else:
        _nTmessage("........ Found 'convert'")
        parametersDict['convertPath'] = strip(convertPath)
    # end if

    ghostscriptPath,err  = _NTgetoutput('which gs')
    if not ghostscriptPath:
        _nTwarning("Could not find 'ghostscript' (from ImageMagick)")
        parametersDict['ghostscriptPath']  = PLEASE_ADD_EXECUTABLE_HERE
    else:
        _nTmessage("........ Found 'ghostscript'")
        parametersDict['ghostscriptPath'] = strip(ghostscriptPath)
    # end if

    ps2pdfPath,err  = _NTgetoutput('which ps2pdf14')
    if not ps2pdfPath:
        _nTwarning("Could not find 'ps2pdf' (from Ghostscript)")
        parametersDict['ps2pdfPath']  = PLEASE_ADD_EXECUTABLE_HERE
    else:
        ps2pdfPath = strip(ps2pdfPath)
        parametersDict['ps2pdfPath'] = strip(ps2pdfPath)
        _nTmessage("........ Found 'ps2pdf'        %s" % ps2pdfPath)        
    # end if

    molmolPath,err  = _NTgetoutput('which molmol')
    if not molmolPath:
        _nTmessage("Could not find 'molmol'  (optional)")
        parametersDict['molmolPath']  = PLEASE_ADD_EXECUTABLE_HERE
    else:
        molmolPath = strip(molmolPath)
        _nTmessage("........ Found 'molmol'        %s" % molmolPath)        
        parametersDict['molmolPath'] = molmolPath
    # end if

    povrayPath,err  = _NTgetoutput('which povray')
    if not povrayPath:
        _nTmessage("Could not find 'povray'  (optional)")
        parametersDict['povrayPath']  = PLEASE_ADD_EXECUTABLE_HERE
    else:
        povrayPath = strip(povrayPath)
        _nTmessage("........ Found 'povray'        %s" % povrayPath)        
        parametersDict['povrayPath'] = povrayPath
    # end if

    talosPath,err  = _NTgetoutput('which talos+')
    if not talosPath:
        _nTmessage("Could not find 'talos+'  (optional)")
        parametersDict['talosPath']  = PLEASE_ADD_EXECUTABLE_HERE
    else:
        talosPath = strip(talosPath)
        _nTmessage("........ Found 'talos+'        %s" % talosPath)        
        parametersDict['talosPath'] = talosPath
    # end if

    # TODO: enable real location finder. This just works for some cases but we shouldn't bother
    # others. The integration code is actually not finished.
    pyMolPathList  = ('/sw/lib/pymol-py26', # mac's fink
                      '/opt/local/lib/pymol/modules/pymol', # mac port
                      '/usr/lib/pymodules/python2.6/pymol', # Ubuntu 9.10
                      )
    pyMolPath = None
    for pyMolPathToTest in pyMolPathList:
        if  os.path.exists(pyMolPathToTest):
            pyMolPath = pyMolPathToTest
            break
        # end if
    # end for
    if not pyMolPath:
        if False: # DEFAULT: False TODO: enable when done.
            _nTmessage("Could not find 'pymol' code (optional)")
        parametersDict['pyMolPath']  = PLEASE_ADD_EXECUTABLE_HERE
    else:
        pyMolPath = strip(pyMolPath)
        _nTmessage("........ Found 'pymol' code    %s" % pyMolPath)
        parametersDict['pyMolPath'] = strip(pyMolPath)
    # end if
    
    # Just to get a message to user; not important.
    pyMolBinPath,err  = _NTgetoutput('which pymol')
    if not pyMolBinPath:
        pyMolBinPath = '//sw/bin/pymol'
        if not os.path.exists(pyMolBinPath):
            pyMolBinPath = None
    if not pyMolBinPath:
        _nTmessage("Could not find 'pymol' (optional)")
#        parametersDict['pyMolBinPath']  = PLEASE_ADD_EXECUTABLE_HERE
    else:
        pyMolBinPath = strip( pyMolBinPath )
        _nTmessage("........ Found 'pymol' binary  %s" % pyMolBinPath)
#        parametersDict['pyMolBinPath'] = strip(pyMolPath)
    # end if

    
    # Linux:
    yasaraPath = None
    yasaraFullPath,err  = _NTgetoutput('which yasara')
    # For Linux the sub dirs are parallel to executable.
    if yasaraFullPath:
        yasaraFullPath = strip(yasaraFullPath)
        n = len(yasaraFullPath)
        m = len('/yasara')
        # Truncate the /yasara from the path
        yasaraPath = yasaraFullPath[0:n-m] 
    else:
        # Mac name in e.g. /Applications/YASARA.app/Contents/MacOS/yasara.app
        # For Mac the sub dirs are subbed by to executable like in:
        # /Applications/YASARA.app/yasara/plg
        yasaraFullPath,err  = _NTgetoutput('which yasara.app')
        if yasaraFullPath:
            yasaraFullPath = strip(yasaraFullPath)
            n = len(yasaraFullPath)
            m = len('/Contents/MacOS/yasara.app')
            yasaraPath = yasaraFullPath[0:n-m] + '/yasara'
            if not os.path.exists(yasaraPath):
                _nTerror("Failed to find OSX yasara install.")
                yasaraPath = None
        # end if
    # end if
    if not yasaraPath:
        _nTmessage("Could not find 'yasara' code (optional)")
        parametersDict['yasaraPath']  = PLEASE_ADD_EXECUTABLE_HERE
    else:
        _nTmessage("........ Found 'yasara'        %s" % yasaraPath)
        parametersDict['yasaraPath'] = yasaraPath
    # end if

#    userShell = os.environ.get('SHELL')
#    Better not use the above as this gives on JFD's mac: /bin/bash and actually
#    use tcsh. Better ask a question once.
    if isTcsh == None:
        answer = None
        print ''
        while answer not in ["y","n"]:
            answer = raw_input("Do you use tcsh/csh [y] or bash/sh/ksh/zsh/ash etc. [n]; please enter y or n:")
        isTcsh = answer == "y"
    # end if
    
    _writeCingShellFile(isTcsh)
#    _nTmessage("TODO: configure MolProbity by running it's setup.sh") # TODO:
