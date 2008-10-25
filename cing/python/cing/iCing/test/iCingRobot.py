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
    localTesting = True
    ## queries possible
    doSave  = 0
    doRun   = 0
    doStatus= 0
    doLog   = 1
    doPname = 0
    ## credentials.
    user_id = "jd3"
    access_key = "234567"

#    user_id = "Tim"
#    access_key = "TimsDirtySecret"

    entryId = '1a4d' # smallest for quick testing.
    ccpnFile = os.path.join(cingDirTestsData, "ccpn", entryId + ".tgz")
    
    machineUrl = "nmr.cmbi.ru.nl"
    rpcCGIUrl = "iCing/cgi-bin/iCingByCgi.py"
    rpcUrl = "iCing/server-bin"
#    rpcUrl = ""
    port = ""
    portCGI = ""
            
    if localTesting:
        machineUrl = "localhost"        
#            rpcUrl = "iCing/cgi-bin/iCingByCgi.py"
#        port = ':'+`PORT_SERVER`
#            portCGI = ':'+`PORT_CGI`
                    
##############################################################################################################
    urlSave = machineUrl + portCGI+ '/' + rpcCGIUrl        
    credentialSettings = "-F UserId=%s -F AccessKey=%s" % ( user_id, access_key)
    cmdSave = """curl %s\
        -F Action=%s \
        -F UploadFile=@%s \
        %s """ % (credentialSettings, FORM_ACTION_SAVE, ccpnFile, urlSave)
    if doSave:
        NTmessage("Curling to: " + urlSave)
        do_cmd(cmdSave)
    
    
##############################################################################################################
    urlRun = machineUrl + port+ '/' + rpcUrl        
    cmdRun = """curl %s\
        -F Action=%s \
        %s """ % (credentialSettings, FORM_ACTION_RUN, urlRun)
    if doRun:
        NTmessage("Curling to: " + urlRun)
        do_cmd(cmdRun)
    
##############################################################################################################
    cmdStatus = """curl %s\
        -F Action=%s \
        %s """ % (credentialSettings, FORM_ACTION_STATUS, urlRun)
    if doStatus:
        NTmessage("Curling to: " + urlRun)
        do_cmd(cmdStatus)
    
##############################################################################################################
    cmdLog = """curl %s\
        -F Action=%s \
        %s """ % (credentialSettings, FORM_ACTION_LOG, urlRun)
    if doLog:
        NTmessage("Curling to: " + urlRun)
        do_cmd(cmdLog)
    
##############################################################################################################
    cmdPname = """curl %s\
        -F Action=%s \
        %s """ % (credentialSettings, FORM_ACTION_PROJECT_NAME, urlRun)
    if doPname:
        NTmessage("Curling to: " + urlRun)
        do_cmd(cmdPname)
    
if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    iCingRobot()