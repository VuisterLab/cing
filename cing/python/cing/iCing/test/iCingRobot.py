# Script for testing of FileUpload at the CGI server and the other commands at the main iCing server.
# Run: python -u $CINGROOT/python/cing/iCing/test/iCingRobot.py
from cing import cingDirTestsData 
from cing import verbosityDebug
from cing.Libs.NTutils import NTmessage
from cing.Libs.forkoff import do_cmd
from cing.iCing.iCingServer import FORM_ACTION_RUN
from cing.iCing.iCingServer import FORM_ACTION_SAVE
from cing.iCing.iCingServer import FORM_ACTION_STATUS
#from cing.iCing.iCingServer import PORT_SERVER
from cing.iCing.iCingServer import FORM_ACTION_LOG
from cing.iCing.iCingServer import FORM_ACTION_PROJECT_NAME
import cing
import os

def iCingRobot():
#    NTwarning("Expect errors without a server up and running.")
    NTmessage("Firing up the iCing robot; aka CCPN Analysis example interface to CING")
    ## queries possible
    doSave  = 1
    doRun   = 0
    doStatus= 0
    doLog   = 0
    doPname = 1
    ## credentials.
    user_id = "jd3"
    access_key = "234567"

#    user_id = "Tim"
#    access_key = "TimsDirtySecret"

#    entryId = '1brv' # 68K, smallest for quick testing.
    entryId = '1a4d' # 388K
    ccpnFile = os.path.join(cingDirTestsData, "ccpn", entryId + ".tgz")
    
    rpcUrl = "localhost:8888/cing.iCing/serv/iCingServlet"
                                
##############################################################################################################
    credentialSettings = "-F UserId=%s -F AccessKey=%s" % ( user_id, access_key)
    cmdSave = "curl %s -F Action=%s -F UploadFile=@%s %s" % (
        credentialSettings, 
        FORM_ACTION_SAVE, 
        ccpnFile, 
        rpcUrl)
    if doSave:
        NTmessage("Curling to: " + rpcUrl)
        do_cmd(cmdSave)
    
    
##############################################################################################################
    cmdRun = """curl %s\
        -F Action=%s \
        %s """ % (credentialSettings, FORM_ACTION_RUN, rpcUrl)
    if doRun:
        NTmessage("Curling to: " + rpcUrl)
        do_cmd(cmdRun)
    
##############################################################################################################
    cmdStatus = """curl %s\
        -F Action=%s \
        %s """ % (credentialSettings, FORM_ACTION_STATUS, rpcUrl)
    if doStatus:
        NTmessage("Curling to: " + rpcUrl)
        do_cmd(cmdStatus) 
    
##############################################################################################################
    cmdLog = """curl %s\
        -F Action=%s \
        %s """ % (credentialSettings, FORM_ACTION_LOG, rpcUrl)
    if doLog:
        NTmessage("Curling to: " + rpcUrl)
        do_cmd(cmdLog)
    
##############################################################################################################
    cmdPname = """curl %s\
        -F Action=%s \
        %s """ % (credentialSettings, FORM_ACTION_PROJECT_NAME, rpcUrl)
    if doPname:
        NTmessage("Curling to: " + rpcUrl)
        do_cmd(cmdPname)
    
if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    iCingRobot()