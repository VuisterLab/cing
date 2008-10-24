# Script for testing of FileUpload at the CGI server and the other commands at the main iCing server.
# Run: python -u $CINGROOT/python/cing/iCing/test/test_iCingRobot.py
from cing import cingDirTestsData
from cing import verbosityDebug
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTwarning
from cing.Libs.forkoff import do_cmd
from cing.iCing.iCingServer import FORM_ACTION_RUN
from cing.iCing.iCingServer import FORM_ACTION_SAVE
from cing.iCing.iCingServer import FORM_ACTION_STATUS
from cing.iCing.iCingServer import PORT_SERVER
import cing
import os

def iCingRobot():
    NTwarning("Excpect errors whitout a server up and running.")
    NTmessage("Firing up the iCing robot; aka CCPN Analysis example interface to CING")
    localTesting = True
    doSave = True
    doRun = False
    doStatus = False
    user_id = "jd3"
    access_key = "234567"

#    user_id = "Tim"
#    access_key = "TimsDirtySecret"

    entryId = '1a4d' # smallest for quick testing.
    ccpnFile = os.path.join(cingDirTestsData, "ccpn", entryId + ".tgz")
    
    machineUrl = "nmr.cmbi.ru.nl"
    rpcUrl = "iCing/cgi-bin/iCingByCgi.py"
    port = ""
    portCGI = ""
            
    if localTesting:
        machineUrl = "localhost"        
#            rpcUrl = "iCing/cgi-bin/iCingByCgi.py"
        port = ':'+`PORT_SERVER`
#            portCGI = ':'+`PORT_CGI`
                    
##############################################################################################################
    urlSave = machineUrl + portCGI+ '/' + rpcUrl        
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
    
if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    iCingRobot()