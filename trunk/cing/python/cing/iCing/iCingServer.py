"""
Inspired by: 
http://fragments.turtlemeat.com/pythonwebserver.php
and http://code.google.com/support/bin/answer.py?answer=65632&topic=11368
"""
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from cing.iCing import FORM_ACCESS_KEY
from cing.iCing import FORM_ACTION
from cing.iCing import FORM_ACTION_RUN
from cing.iCing import FORM_LIST_REQUIRED
from cing.iCing import FORM_USER_ID
from cing.iCing import RESPONSE_CODE_200_OK
from cing.iCing import RESPONSE_CODE_400_BAD_REQUEST
from cing.iCing import RESPONSE_CODE_404_NOT_FOUND
from cing.iCing import cing_server_tmp
import cgi
import os
import sys
 
class iCingServerHandler(BaseHTTPRequestHandler):
    def sendJSONResponse(self, msg, responseCode = RESPONSE_CODE_200_OK):
        """
        For list of codes look at: BaseHTTPRequestHandler.responses dictionary
        """
#        self.send_response(responseCode)   
#        self.send_header('Content-type',    'text/plain')                 
#        self.end_headers()
#        self.wfile.write(msg+"\n");
        statusReturned = "error"
        if responseCode == RESPONSE_CODE_200_OK:
            statusReturned = "message"
        body =  "{%s: '%s'}\n" % (statusReturned, msg)
        self.send_response(responseCode) # otherwise we can't send a body?
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Content-Length', len(body))
        self.send_header('Expires', '-1')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Pragma', 'no-cache')
        self.end_headers()
        
        self.wfile.write(body)
        self.wfile.flush()
        self.connection.shutdown(1)
        
        
    def do_POST(self):    
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        if ctype != 'multipart/form-data':
            self.sendJSONResponse('Received data is not: multipart/form-data', RESPONSE_CODE_404_NOT_FOUND)
            return
        self.form=cgi.parse_multipart(self.rfile, pdict)

        for expectedKey in FORM_LIST_REQUIRED:
            if not self.form.has_key(expectedKey):
                self.sendJSONResponse("Missing form field: [" + expectedKey + ']', RESPONSE_CODE_400_BAD_REQUEST)
                return
        
        self.formDict={}
        for key in self.form.keys():
            self.formDict[ key ] = self.form[ key ][0]
        
        action = self.formDict[ FORM_ACTION ]
        self.user_id = self.formDict[ FORM_USER_ID ]
        self.access_key = self.formDict[ FORM_ACCESS_KEY ]
        
#        self.logToLog('Got user_id: ' + self.user_id)
        self.pathUser = os.path.join(cing_server_tmp, self.user_id)
#        self.logToLog('Got pathUser: ' + self.pathUser)
        
        self.pathProject = os.path.join(self.pathUser, self.access_key)        
#        self.logToLog('Got pathProject: ' + self.pathProject)
        if not os.path.exists(self.pathProject):
#            self.logToLog('pathProject does not exist')
            try:
                os.makedirs(self.pathProject) # defaults to False return.
            except Exception, e:
                msg = "Failed to makedirs for project at: [" + self.pathProject + "] with Exception: ["+`e`+"]"
                self.sendJSONResponse(msg, RESPONSE_CODE_400_BAD_REQUEST)
                return
        
        if os.chdir(self.pathProject):
            self.sendJSONResponse("Failed to change to dir: %s" % self.pathProject, RESPONSE_CODE_400_BAD_REQUEST)
            return
            
        if action == FORM_ACTION_RUN:
            self.run()
        else:
            msg = "Unknown action: %s" % action
            self.sendJSONResponse(msg, RESPONSE_CODE_400_BAD_REQUEST)
            return
            
    def logToLog(self, msg):
        sys.stderr.write(msg+'\n')
#        sys.stderr.write(msg+'\n')
            
    def run(self):
        """Fails because form can't be loaded with large data thru non-cgi
        """        
        self.logToLog('Starting run')
        
    def do_GET(self):
        self.sendJSONResponse("Access denied through do_GET()")

def main():
    try:
        server = HTTPServer(('', 8000), iCingServerHandler)
        print 'started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()
