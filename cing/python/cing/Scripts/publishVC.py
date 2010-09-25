'''
Created on Sep 21, 2010

How to copy the VC to nmr (production machine):

-1- Mount tera1 from nmr
-2- Shutdown VC -and- WMware. Well, suspending it is enough.
-3- Run this code which will do steps 4 through 6.
    python $CINGROOT/python/cing/Scripts/publishVC.py

====================================================================
-4- cd ~jd/Documents/Virt*
-5- Replace the date in the below command and run:
    VCsecret is kept a secret.
    tar -cpBf - VC.vmwarevm | gzip --fast > /Volumes/tera1/Library/WebServer/Documents/$VCsecret/VC_32bit_2010-09-21.tgz
-6- On nmr:
    cd $D/$VCsecret
    ln -f VC_32bit_2010-09-21.tgz VC.tgz

=====================================================================
@author: jd
'''
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG.settings import dDir
cing.verbosity = cing.verbosityDebug

localDir = '/Users/jd/Documents/Virtual Machines.localized'
remoteDirBase = os.path.join('/Volumes/tera1', dDir[1:])

vmName = 'Ubuntu_10_4_32_bit'
#vmName = 'VC_32bit'
#vmName = 'test'

doSend = True
doSsh = True

os.chdir(localDir)
VCsecret = os.getenv('VCsecret')
if not VCsecret:
    NTerror("Failed to find VCsecret env variable.")
    sys.exit(1)

remoteDir = os.path.join(remoteDirBase,VCsecret)
if not os.path.exists(remoteDir):
    NTerror("Failed to find remote directory (was it mounted?): %s" % remoteDir)
    sys.exit(1)

dstFile = '%s.tgz' % (vmName)
tt = time.localtime()
dateStr = '%04d-%02d-%02d' % ( tt.tm_year, tt.tm_mon, tt.tm_mday)
fileName = '%s_%s.tgz' % (vmName,dateStr)
remoteFile = os.path.join( remoteDir, fileName)

if doSend:
    if os.path.exists(remoteFile):
        if True:
            os.unlink(remoteFile)
            NTmessage("Removing existing file.")
        else:
            NTerror("Failed because found remote file: %s" % remoteFile)
            sys.exit(1)

    tarring = ExecuteProgram('tar', rootPath=localDir, redirectOutputToFile = remoteFile)
    tar_cmd = '-cpBf - %s.vmwarevm | gzip --fast' % vmName
    NTmessage("Running tar with options: %s" % tar_cmd)
    if tarring( tar_cmd ):
        NTerror("Failed to run tar with options: " + tar_cmd)
        sys.exit(1)

#NTerror("TODO: finish on next time's use.")
#sys.exit(1)

if doSsh:
    sshing = ExecuteProgram('ssh', redirectOutput = False)
    ssh_todo = "'cd %s/%s; ln -f %s %s'" % ( dDir, VCsecret, fileName, dstFile )
    ssh_cmd = ' jd@nmr.cmbi.umcn.nl %s' % ssh_todo
    NTmessage("Running ssh with options: %s" % ssh_cmd)
    if sshing( ssh_cmd ):
        NTerror("Failed to run ssh with options: " + ssh_cmd)
        sys.exit(1)




