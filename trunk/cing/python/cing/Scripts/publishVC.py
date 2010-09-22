'''
Created on Sep 21, 2010

How to copy the VC to nmr (production machine):

-1- Mount tera1 from nmr
-2- Shutdown VC and WMware.
-3- Run this code which will do steps 4 & 5.
    python $CINGROOT/python/cing/Scripts/publishVC.py

====================================================================
-4- cd ~jd/Documents/Virt*
-5- Replace the date in the below command and run:
    VCsecret is kept a secret.
    tar -cpBf - VC.vmwarevm | gzip --fast > /Volumes/tera1/Library/WebServer/Documents/$VCsecret/VC_32bit_2010-09-21.tgz
-6- On nmr:
    cd $D/$VCsecret
    rm VC.tgz
    ln VC_32bit_2010-09-21.tgz VC.tgz

=====================================================================
@author: jd
'''
from cing.Libs.NTutils import ExecuteProgram
from cing.Libs.NTutils import NTerror
import os
import sys
import time

localDir = '/Users/jd/Documents/Virtual Machines'
remoteDir = '/Volumes/tera1/Library/WebServer/Documents/$VCsecret'


os.chdir(localDir)
VCsecret = os.getenv('VCsecret')
if not VCsecret:
    NTerror("Failed to find VCsecret env variable.")
    sys.exit(1)

if not os.path.exists(remoteDir):
    NTerror("Failed to find remote directory (was it mounted?): %s" % remoteDir)
    sys.exit(1)

tt = time.localtime()
dateStr = '%04d-%02d-%02d.tgz' % ( tt.tm_year, tt.tm_mon, tt.tm_mday)
fileName = 'VC_32bit_%s.tgz' % dateStr
remoteFile = os.path.join( remoteDir, fileName)

if os.path.exists(remoteFile):
    NTerror("Failed because found remote file: %s" % remoteFile)
    sys.exit(1)

NTerror("TODO: finish on next time's use.")
sys.exit(1)

tar_cmd = 'tar -cpBf - VC.vmwarevm | gzip --fast'
tarring = ExecuteProgram(tar_cmd, redirectOutputToFile = remoteFile)
if tarring( '' ):
    NTerror("Failed to run tar/gzip with command: " + tar_cmd)
    sys.exit(1)

ssh_cmd = 'ssh -XY -l jd nmr.cmbi.umcn.nl'
sshing = ExecuteProgram(ssh_cmd)



