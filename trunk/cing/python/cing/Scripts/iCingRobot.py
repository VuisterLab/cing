# Script for testing of FileUpload at the CGI server and the other commands at the main iCing server.
# Run: python -u $CINGROOT/python/cing/Scripts/iCingRobot.py
# There is a unit test at: cing.Scripts.test.testiCingRobot

from cing import cingDirTestsData
from cing.Libs.NTutils import * #@UnusedWildImport
import mimetools
import urllib2

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

RESPONSE_EXIT_CODE = 'ExitCode'
RESPONSE_SUCCESS = 'Success'
RESPONSE_RESULT = 'Result'
RESPONSE_DONE = 'done'

#DEFAULT_URL = 'http://nmr.cmbi.ru.nl' # production without https security turned on
DEFAULT_URL = 'https://nmr.cmbi.ru.nl' # production with https security turned on
#DEFAULT_URL = 'http://localhost' # local tomcat instance
#DEFAULT_URL = 'http://localhost' # local gwt embedded tomcat instance
DEFAULT_RPC_PORT = ''
#DEFAULT_RPC_PORT = ':8080'

DEFAULT_URL_PATH = 'icing' # ?? lower case?
#DEFAULT_URL_PATH = 'cing.iCing' # use for gwt embedded tomcat

rpcUrl=DEFAULT_URL+"/icing/serv/iCingServlet"
#    rpcUrl=DEFAULT_URL+DEFAULT_RPC_PORT+'/'+DEFAULT_URL_PATH+"/serv/iCingServlet" # TODO make this line working and not the below line!
#    rpcUrl=DEFAULT_URL+DEFAULT_RPC_PORT+'/'+DEFAULT_URL_PATH+"/iCingServlet"

nTmessage("rpcUrl: " + rpcUrl)

def getResultUrls(credentials, entryId, url=None):

    userId = credentials[0][1]
    accessKey = credentials[1][1]

    resultBaseUrl = os.path.join(url, 'tmp/cing', userId, accessKey)
    resultHtmlUrl = os.path.join(resultBaseUrl, entryId + ".cing", "index.html")
    resultLogUrl = os.path.join(resultBaseUrl, "cingRun.log")
    resultZipUrl = os.path.join(resultBaseUrl, entryId + "_CING_report.zip")

    return resultBaseUrl, resultHtmlUrl, resultLogUrl, resultZipUrl

def sendRequest(url, fields, files):
    """Function to send form fields and files to a given URL.
    """

    contentType, bodyData = encodeForm(fields, files)

    headerDict = {'User-Agent': 'anonymous',
                  'Content-Type': contentType,
                  'Content-Length': str(len(bodyData))
                  }

    request = urllib2.Request(url, bodyData, headerDict)
    response = urlOpen(request)

    if not response:
      return

    jsonTxt = response.read()

    result = _processResponse(jsonTxt)
    if result.get(RESPONSE_EXIT_CODE) != RESPONSE_SUCCESS:
        msg  = 'Request not successful. Action was: %s' % fields
        msg += ' Response was: %s' % jsonTxt
        nTwarning('Failure %s' % msg)
        return

    return result

def urlOpen(request):

    try:
        response = urllib2.urlopen(request)

    except urllib2.URLError, e:
        if hasattr(e, 'reason'):
            if isinstance(request, urllib2.Request):
              url = request.get_full_url()
            else:
              url = request

            msg = 'Connection to server URL %s failed with reason:\n%s' % (url, e.reason)

        elif hasattr(e, 'code'):
            msg =    'Server request failed and returned code:\n%s' % e.code

        else:
            msg = 'Server totally barfed with no reason or fail code'

        nTwarning('Failure %s'% msg)
        return

    return response

def _processResponse(text):
    """Convert the strings the iCingServer sends back into Python
       When Python 2.6 is the CCPn standards this should use the JSON
       libraries.
    """

    text = text[2:-2]

    dataDict = {}

    for pair in text.split('","'):
      data = pair.split('":"')

      if len(data) == 2:
        key , value = data
        dataDict[key] = value
      else:
        print "Trouble",  pair


    return dataDict

#########################################################################################
# Initial code from http://www.voidspace.org.uk/python/cgi.shtml#upload                                                #
#########################################################################################

BOUNDARY = mimetools.choose_boundary()

def encodeForm(fields, files=None, lineSep='\r\n',
               boundary='-----'+BOUNDARY+'-----'):
    """Function to encode form fields and files so that they can be sent to a URL"""

    if not files:
        files = []

    lines = []
    if isinstance(fields, dict):
        fields = fields.items()


    for (key, fileName, value) in files:
        #fileType = mimetypes.guess_type(fileName)[0] or 'application/octet-stream'
        fileType = 'application/octet-stream'

        lines.append('--' + boundary)
        lines.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, fileName))
        if not fileType.startswith('text'):
            lines.append('Content-Transfer-Encoding: binary')
        lines.append('Content-Type: %s' % fileType)
        #lines.append('Content-Length: %s\r\n' % str(len(value)))
        lines.append('')
        lines.append(value)

    for (key, value) in fields:
        lines.append('--' + boundary)
        lines.append('Content-Disposition: form-data; name="%s"' % key)
        lines.append('')
        lines.append(value)


    lines.append('--' + boundary + '--')
    lines.append('')

    bodyData = lineSep.join(lines)
    contentType = 'multipart/form-data; boundary=%s' % boundary

    return contentType, bodyData


def iCingRobot():
#    nTwarning("Expect errors without a server up and running.")
    nTmessage("Firing up the iCing robot; aka example interface to CING")

    ## queries possible; do one at a time going down the list.
    ## After the run is started the status will let you know if the run is finished
    ## The log will show what the server is doing at any one time.
    doSave  = 1 # Upload to iCing and show derived urls
    doRun   = 0 # Start the run in Nijmegen
    doStatus= 0 # Find out if the run finished
    doLog   = 0 # Get the next piece of log file (may be empty)
    doPname = 0 # Get the project name back. This is the entryId below.
    doPurge = 0 # Remove data from server again.

    # User id should be a short id (<without any special chars.)
#    user_id = os.getenv("USER", "UnknownUser")
    user_id = "iCingRobot"
#    access_key = "123456"
    access_key = getRandomKey() # Use a different one in a production setup.

    entryId = '1brv' # 68K, smallest for quick testing.
#    entryId = 'gb1' # only included in xplor variant as single model.

    # Select one of the types by uncommenting it
    inputFileType = 'CCPN'
#    inputFileType = 'PDB'
#    inputFileType = 'XPLOR'

    ccpnFile = os.path.join(cingDirTestsData, "ccpn", entryId + ".tgz")
    pdbFile = os.path.join(cingDirTestsData, "pdb", entryId, 'pdb' + entryId + ".ent")
    xplorFile = os.path.join(cingDirTestsData, "xplor", entryId, entryId + ".pdb")

    inputFile = ccpnFile
    if inputFileType == 'PDB':
        inputFile = pdbFile
    elif inputFileType == 'XPLOR':
        inputFile = xplorFile


    credentials = [(FORM_USER_ID, user_id), (FORM_ACCESS_KEY, access_key)]

##############################################################################################################

    if doSave:
        data = credentials + [(FORM_ACTION,FORM_ACTION_SAVE),]
        fileObj = open(inputFile, 'rb')
        files = [( FORM_UPLOAD_FILE_BASE, inputFile, fileObj.read() ),]

        result = sendRequest(rpcUrl, data, files)
        if not result:
            nTerror("Failed to save file to server")
        else:
            print "result of save request: %s" % result
            urls = getResultUrls(credentials, entryId, DEFAULT_URL)
            print "Base URL", urls[0]
            print "Results URL:", urls[1]
            print "Log URL:", urls[2]
            print "Zip URL:", urls[3]


##############################################################################################################
    files = None

    if doRun:
        data = credentials + [(FORM_ACTION,FORM_ACTION_RUN),]
        print  sendRequest(rpcUrl, data, files)

    if doStatus:
        data = credentials + [(FORM_ACTION,FORM_ACTION_STATUS),]
        print  sendRequest(rpcUrl, data, files)

    if doLog:
        data = credentials + [(FORM_ACTION,FORM_ACTION_LOG),]
        print  sendRequest(rpcUrl, data, files)

    if doPname:
        data = credentials + [(FORM_ACTION,FORM_ACTION_PROJECT_NAME),]
        print  sendRequest(rpcUrl, data, files)

    if doPurge:
        data = credentials + [(FORM_ACTION,FORM_ACTION_PURGE),]
        print  sendRequest(rpcUrl, data, files)

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    iCingRobot()