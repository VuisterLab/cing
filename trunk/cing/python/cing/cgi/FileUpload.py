#!/sw/bin/python -u
# TODO: make python executable configurable. JFD's mac defaults to wrong one if using env trick.
from cgi import FieldStorage
import os
import sys

# TODO: only allow registered users.
# Nice to have some speed so we're not tying this into the general cing setup. Takes too long for startup.

#CINGROOT = os.getenv("CINGROOT", "/Users/jd/workspace34/cing") # default value should not be used...
#sys.path.insert(0, CINGROOT+"/python")



# Match the iCing.java settings.
#sys.stderr = sys.stdout # Errors from python script will need to flow to user.

FORM_ACCESS_KEY = "AccessKey"
FORM_USER_ID = "UserId"
FORM_UPLOAD_FILE_BASE = "UploadFile"

FORM_UPLOAD_FILE_LIST = [ FORM_ACCESS_KEY, FORM_USER_ID, FORM_UPLOAD_FILE_BASE ]

JSON_ERROR_STATUS = "error"

MAX_FILE_SIZE_BYTES = 1024 * 1024 * 1 # 50 Mb when time out issue is resolved. TODO: update. 
BUFFER_WRITE = 100*1000

server_cgi_url_tmp = "localhost/tmp/cing"
cing_server_tmp = "/Library/WebServer/Documents/tmp/cing"

class FileUpload():
    def serve(self):
        #TODO: prevent time out by sending keep alive commands
        print "Content-Type: text/plain"
        print
#        message = "Just testing done now"
#        print "{message: '"+message+"'}"
#        sys.exit(0)
        
        #        print("Content-Type: text/html\n")     # HTML is following # blank line, end of headers
        #        keyList = os.environ.keys()
        #        keyList.sort()
        #        for key in keyList:
        #            NTdebug(  "<p>key: [" + key + '] value: [' + os.environ[key] + ']')
        
        #import cgi
        #". Do not use "from cgi import *" -- the module defines all sorts of names for
        # its own use or for backward compatibility that you don't want in your namespace.
        #        ACCESS_KEY      = "ACCESS_KEY"
        #        PROJECT_FILE    = "PROJECT_FILE"
        #        COOR_FILE       = "COOR_FILE"
        #        DO_WHATIF       = "DO_WHATIF" # absent when unchecked.
        #        DO_PROCHECK     = "DO_PROCHECK"
        #        DO_IMAGES       = "DO_IMAGES"
                
        form = FieldStorage()
        #        NTmessage('<p>Found form: [%s]' % form)
        #        keyFormList = form.keys()
        #        keyFormList.sort()
        #        for key in keyFormList:
        #            value = ''
        #            element = form[key]
        #            if hasattr(element, 'value'):
        #                value = form[key].value[:80]
        #            if hasattr(element, 'checked'):
        #                value = "checked was set to: " + form[key].checked
        #            logToLog("<p>Found key [%s] and value first 80 char(s): [%s]" % (key, value))
        for expectedKey in FORM_UPLOAD_FILE_LIST:
            if not form.has_key(expectedKey):
                self.endError("Missing form field: [" + expectedKey + ']')
#                . All together expecting: ' + `FORM_UPLOAD_FILE_LIST`)
            logToLog("Found expected key [%s] and value first 80 char(s): [%s]" % (expectedKey, form[expectedKey].value[:80]))
        
        #        cgitb.enable(display=1, logdir="CING_SERVER_TMP")
        access_key  = form[ FORM_ACCESS_KEY ].value
        user_id     = form[ FORM_USER_ID ].value
        
        logToLog('Got user_id: ' + user_id)
        
        #        /** TODO read up on safety issues here. */
        pathUser = os.path.join(cing_server_tmp, user_id)
        logToLog('Got pathUser: ' + pathUser)
        
        # Skipping this step
#        if not os.path.exists(pathUser):
#            if not os.mkdir(pathUser):
#                self.endError("Failed to mkdir for user at: [" + pathUser + "]")
#                
        pathProject = os.path.join(pathUser, access_key)        
        logToLog('Got pathProject: ' + pathProject)
        if not os.path.exists(pathProject):
            logToLog('pathProject does not exist')
            try:
                os.makedirs(pathProject) # defaults to False return.
            except Exception, e:
                self.endError("Failed to makedirs for project at: [" + pathProject + "] with Exception: ["+`e`+"]")
            else:
                logToLog('pathProject created')
                
        
        logToLog('Found/created pathProject: ' + pathProject)
        
        if os.chdir(pathProject):
            self.endError("Failed to change to dir: %s" % pathProject)
            
        
        logToLog('Now in pathProject: ' + pathProject)
        
        fileitem = form[FORM_UPLOAD_FILE_BASE]
        if not fileitem.file:
            self.endError("Please provide an actual file for item: [" + FORM_UPLOAD_FILE_BASE +"]")
                        
        # If an error is encountered when obtaining the contents of an uploaded file (for example, when the user interrupts the form
        #submission by clicking on a Back or Cancel button) the done attribute of the object for the field will be set to the value -1.
        if fileitem.done == -1:
            self.endError("The send file [%s] was not done please retry." % fileitem.filename)
            
        fileLength = len(fileitem.value)
        fileLengthStr = bytesToFormattedString(fileLength)         
         
        if fileLength > MAX_FILE_SIZE_BYTES:
            self.endError("The send file [%s] was larger than the allowed number of bytes compare: [%s] and [%s]" %
                          (fileitem.filename, fileLength, MAX_FILE_SIZE_BYTES))
            
        
        fullFileName = os.path.join(pathProject, fileitem.filename)
        fout = file(fullFileName, 'wb')
        while 1:
            chunk = fileitem.file.read(BUFFER_WRITE)
            if not chunk:
                break
            fout.write (chunk)
        fout.close()
        self.endMessage(fileLengthStr)

    def endError(self, message):
        logToLog('message (error): [%s]' % message)
        print "{error: '"+message+"'}\n"
        sys.exit(0)
    
    def endMessage(self, message):
        logToLog('message (message): [%s]' % message)
        print "{message: '"+message+"'}\n"
        sys.exit(0)



def bytesToFormattedString(size):
    """1600 bytes will be rounded to 2K"""        
    k = 1024
    M = 1024*1024
    G = 1024*1024*1024
    T = 1024*1024*1024*1024
    ck = 'K'
    cM = 'M'
    cG = 'G' 
    cT = 'T'
    postFix = ck
    
    divider = k
    if  size < M:
        divider = k
        postFix = ck
    elif size < G:
        divider = M
        postFix = cM
    elif size < T:
        divider = G
        postFix = cG
    else:
        divider = T
        postFix = cT
    
    r = size/float(divider)
    result = ("%.0f" % r) + postFix
    return result

def logToLog(msg):
        sys.stderr.write(msg)
        sys.stderr.write('\n')
#        myhtml.render() # Can't be done without whole project and content anymore.

def testBytesToFormattedString():
    byteList = [ 1, 1000, 1300, 1600, 13000*1024, 130*1000*1024*1024  ]
    expectedResults= [ '0K', '1K', '1K', '2K', '13M', '127G' ]
    for i in range(len(byteList)):
        r = bytesToFormattedString(byteList[i])
#        self.assertEqual( r, expectedResults[i] )
        if r != expectedResults[i]:
            print( "result [%s] is not expected [%s]" % ( r, expectedResults[i]))
                     
if __name__ == '__main__':
    f = FileUpload()
    f.serve()