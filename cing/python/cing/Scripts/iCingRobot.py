# Script for testing of FileUpload at the CGI server and the other commands at the main iCing server.
# Run: python -u $CINGROOT/python/cing/iCing/test/iCingRobot.py
from cing import cingDirTestsData 
from cing import verbosityDebug
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.Libs.network import getRandomKey
from cing.Libs.network import sendRequest
import cing
import os
#from cing.iCing.iCingServer import PORT_SERVER

"""Use the secure protocol at https://nmr.cmbi.ru.nl/icing where is needed.
For non-secure access use the default http protocol below.
"""

#The form strings need to match the code in: 
#http://code.google.com/p/cing/source/browse/trunk/cing/java/src/cing/client/Settings.java
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

def iCingRobot(entryId,
                userId='iCingRobotUser',
                iCingServerBaseUrl='http://nmr.cmbi.ru.nl',
                rpcUrlServlet="icing/serv/iCingServlet",
                projectTgz=None,
                doSave=True, doRun=False, doStatus=False,
                doLog=False, doPname=False, doPurge=False):
    """Function to send a CCPN file for testing CING setup."""
    # Remote procedure call.
    rpcUrl = os.path.join( iCingServerBaseUrl, rpcUrlServlet);

    # Access credentials.
    accessKey = getRandomKey()
    credentials = [(FORM_USER_ID, userId), (FORM_ACCESS_KEY, accessKey)]
        
    jsonResult = None
    # Send the project
    if doSave:
        action = FORM_ACTION_SAVE
        NTmessage("Requesting iCing service: " + action)            
        data = credentials + [(FORM_ACTION, action), ]
        fileObj = open(projectTgz, 'rb')
        files = [(FORM_UPLOAD_FILE_BASE, projectTgz, fileObj.read()), ]
        jsonResult = sendRequest(rpcUrl, data, files)
        fileObj.close()
    
        if not jsonResult:
            return
    
    actions = [(doRun, FORM_ACTION_RUN),
               (doStatus, FORM_ACTION_STATUS),
               (doLog, FORM_ACTION_LOG),
               (doPname, FORM_ACTION_PROJECT_NAME),
               (doPurge, FORM_ACTION_PURGE)]
    
    # Send any other actions
    for boolean, action in actions:
        if boolean:
            NTmessage("Requesting iCing service: " + action)            
            data = credentials + [(FORM_ACTION, action), ]
            jsonResult = sendRequest(rpcUrl, data)    
            if not jsonResult:
                break
    
    # Fetch output e.g.
#    http://nmr.cmbi.ru.nl/tmp/cing/ano/jwNVw1
    resultBaseUrl = os.path.join(iCingServerBaseUrl, 'tmp/cing', userId, accessKey)
    
    # The entryId is derived from the filename of the deposited ccpn project .tgz file.
    # http://nmr.cmbi.ru.nl/tmp/cing/ano/jwNVw1/1brv.cing/index.html also redirects to:
    # http://nmr.cmbi.ru.nl/tmp/cing/ano/jwNVw1/1brv.cing/1brv/HTML/index.html but the 2nd url
    # might change in the future... use the first and accept the redirect if possible..
    resultHtmlUrl = os.path.join(resultBaseUrl, entryId + ".cing", "index.html")
    # CING validation log file.
    # http://nmr.cmbi.ru.nl/tmp/cing/ano/jwNVw1/cingRun.log
    resultLogUrl = os.path.join(resultBaseUrl, "cingRun.log")
    # Zip with cing project directory structure (including html report) and log.
    # http://nmr.cmbi.ru.nl/tmp/cing/ano/jwNVw1/1brv_CING_report.zip
    resultZipUrl = os.path.join(resultBaseUrl, entryId + "_CING_report.zip")
     
    NTdebug("resultHtmlUrl   : " + resultHtmlUrl)
    NTdebug("resultLogUrl    : " + resultLogUrl)
    NTdebug("resultZipUrl    : " + resultZipUrl)
    
    #f1 = urllib2.urlopen(outUrl).read()
    #fopen = open(predOutFile,'wb')
    #fopen.write(f1)
    #fopen.close()


if __name__ == "__main__":
    cing.verbosity = verbosityDebug

    entryId = '1brv' # 68K, smallest for quick testing.
    projectTgz = os.path.join(cingDirTestsData, "ccpn", entryId + ".tgz")

    # Enable the do's one by one or all at once. 
    # No need to worry about purging; it will be done after a while automatically.
    jsonResult = iCingRobot(entryId, projectTgz=projectTgz, doSave=True, doRun=False, doStatus=False,
                doLog=False, doPname=False, doPurge=False)
    
    if not jsonResult:
        NTerror("Failed to use iCingRobot without getting any message back. Big bug.")
    else:
        NTmessage("Result in Javascript object notation (json): " + jsonResult)
    
    
    
