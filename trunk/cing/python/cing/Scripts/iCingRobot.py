# Script for testing of FileUpload at the CGI server and the other commands at the main iCing server.
# Run: python -u $CINGROOT/python/cing/iCing/test/iCingRobot.py
from cing import cingDirTestsData 
from cing import verbosityDebug
from cing.Libs.NTutils import NTmessage
from cing.Libs.forkoff import do_cmd
#from cing.iCing.iCingServer import PORT_SERVER
import cing
import os

FORM_ACCESS_KEY = "AccessKey"
FORM_USER_ID = "UserId"
FORM_UPLOAD_FILE_BASE = "UploadFile"
FORM_ACTION = "Action"
FORM_ACTION_RUN = "Run"
FORM_ACTION_SAVE = "Save"
FORM_ACTION_STATUS = "Status"
FORM_ACTION_PROJECT_NAME = "ProjectName"
FORM_ACTION_PURGE = "Purge"
FORM_ACTION_LOG = "Log"

def iCingRobot():
#    NTwarning("Expect errors without a server up and running.")
    NTmessage("Firing up the iCing robot; aka CCPN Analysis example interface to CING")
    ## queries possible
    doSave  = 1
    doRun   = 0
    doStatus= 0
    doLog   = 0
    doPname = 0
    doPurge = 1
    ## credentials.
    user_id = "jd3"
    access_key = "123456"

#    user_id = "Tim"
#    access_key = "TimsDirtySecret"

#    entryId = '1brv' # 68K, smallest for quick testing.
    entryId = '1a4d' # 388K
    ccpnFile = os.path.join(cingDirTestsData, "ccpn", entryId + ".tgz")
#    rpcUrl = "localhost/iCing/serv/iCingServlet" # this is for the development when running in gwt hosted mode with embedded tomcat server at 8888.
    rpcUrl = "localhost:8888/cing.iCing/serv/iCingServlet" # this is for the development when running in gwt hosted mode with embedded tomcat server at 8888.
#/    rpcUrl = "dodos.dyndns.org/icing/serv/iCingServlet" # testing production-like 
#    rpcUrl = "https://nmr.cmbi.ru.nl/iCing/serv/iCingServlet" # testing production
                                
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
    
##############################################################################################################
    cmdPname = """curl %s\
        -F Action=%s \
        %s """ % (credentialSettings, FORM_ACTION_PURGE, rpcUrl)
    if doPurge:
        NTmessage("Curling to: " + rpcUrl)
        do_cmd(cmdPname)
    
if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    iCingRobot()