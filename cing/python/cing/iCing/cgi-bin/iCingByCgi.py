#!/sw/bin/python -u
"""

TODO: why doesn't pydev extensions analyze this code?

The reason that this code isn't integrated with the regular iCing server is that the large file uploads require
cgi parameters to be parsed with FieldStorage() and can thus not be done with subclassing BaseHTTPRequestHandler.

Inspired by: 
http://www.python.org/doc/2.5/lib/module-cgi.html
http://fragments.turtlemeat.com/pythonwebserver.php
http://code.google.com/support/bin/answer.py?answer=65632&topic=11368
"""
from cgi import FieldStorage
from cing.Libs.NTutils import bytesToFormattedString
from cing.iCing.iCingServer import BUFFER_WRITE
from cing.iCing.iCingServer import FORM_ACCESS_KEY
from cing.iCing.iCingServer import FORM_ACTION
from cing.iCing.iCingServer import FORM_ACTION_SAVE
from cing.iCing.iCingServer import FORM_LIST_REQUIRED
from cing.iCing.iCingServer import FORM_UPLOAD_FILE_BASE
from cing.iCing.iCingServer import FORM_USER_ID
from cing.iCing.iCingServer import MAX_FILE_SIZE_BYTES
from cing.iCing.iCingServer import cing_server_tmp
import cgitb
import os
import sys 
import time

class iCingByCgi():
    def serve(self):
        print "Content-Type: text/plain"
        print        
#        cgitb.enable(display=0, logdir="/tmp") 
        self.form = FieldStorage()            
#        msg = "form: %r" % self.form
#        self.logToLog(msg)
        for expectedKey in FORM_LIST_REQUIRED: 
            if not self.form.has_key(expectedKey):
                msg = "Missing form field: [" + expectedKey + ']'
                self.endError(msg)
                
#                . All together expecting: ' + `FORM_UPLOAD_FILE_LIST`)
#            self.logToLog("Found expected key [%s] and value first 80 char(s): [%s]" % (expectedKey,
#                self.form[expectedKey].value[:80]))
        
        #        cgitb.enable(display=1, logdir="CING_SERVER_TMP")
        
        action = self.form[ FORM_ACTION ].value
        self.user_id = self.form[ FORM_USER_ID ].value
        self.access_key = self.form[ FORM_ACCESS_KEY ].value
        
#        self.logToLog('Got user_id: ' + self.user_id)
        #        /** TODO read up on safety issues here. */
        self.pathUser = os.path.join(cing_server_tmp, self.user_id)
#        self.logToLog('Got pathUser: ' + self.pathUser)
        
        self.pathProject = os.path.join(self.pathUser, self.access_key)        
#        self.logToLog('Got pathProject: ' + self.pathProject)
        if not os.path.exists(self.pathProject):
            self.logToLog('Creating pathProject: %s' % self.pathProject)
            try:
                os.makedirs(self.pathProject) # defaults to False return.
            except Exception, e:
                msg = "Failed to makedirs for project at: [" + self.pathProject + "] with Exception: ["+`e`+"]"
                self.endError(msg)
                
                                            
#        self.logToLog('Found/created pathProject: ' + self.pathProject)
        
        if os.chdir(self.pathProject):
            msg = "Failed to change to dir: %s" % self.pathProject
            self.endError(msg)
                        
        
        if action == FORM_ACTION_SAVE:
            self.save()
        else:
            msg = "Unknown action: %s" % action
            self.endError(msg)
                        
            
    def save(self):        
        fileitem = self.form[FORM_UPLOAD_FILE_BASE]
#        self.logToLog("%r"% fileitem)
        if not fileitem.file:
            self.endError("Please provide an actual file for item: [" + FORM_UPLOAD_FILE_BASE +"]")            
                        
        # If an error is encountered when obtaining the contents of an uploaded file (for example, when the user interrupts the form
        #submission by clicking on a Back or Cancel button) the done attribute of the object for the field will be set to the value -1.
        if fileitem.done == -1:
            self.endError("The send file [%s] was not done please retry." % fileitem.filename)
        fileLength = len(fileitem.value)         
        if fileLength > MAX_FILE_SIZE_BYTES:
            self.endError("The send file [%s] was larger than the allowed number of bytes compare: [%s] and [%s]" %
                          (fileitem.filename, fileLength, MAX_FILE_SIZE_BYTES))
        
        fullFileName = os.path.join(self.pathProject, fileitem.filename)
        fout = file(fullFileName, 'wb')
        while 1:
            chunk = fileitem.file.read(BUFFER_WRITE)
            if not chunk:
                break
            fout.write (chunk)
        fout.close()
        self.endMessage(bytesToFormattedString(fileLength))



    def endError(self, message):
        self.endNow(message, isError=True)
    
    def endMessage(self, message):
        self.endNow(message)

    def endNow(self, message, isError=False):
        self.logToLog('message (message): [%s]' % message)
        # Can't have single quotes in json.
        message = message.replace("'", '"')
        status = "message"
        if isError:
            status = "error"
        result = "{%s: '%s'}\n" % (status, message)
        print result
        sys.exit(0)

    def logToLog(self, msg):
        sys.stderr.write(msg+'\n')
#        sys.stderr.write(msg+'\n')

if __name__ == '__main__':
    f = iCingByCgi()
    f.serve()