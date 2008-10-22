"""
Regular server started by something in the system's startup like:

cing --server >& server.log

Don't forget to have apache do some proxying like:
ProxyPass         /iCing/cgi-bin http://localhost:8001/cgi-bin
ProxyPassReverse  /iCing/cgi-bin http://localhost:8001/cgi-bin

ProxyPass         /iCingServer.py http://localhost:8000/iCingServer.py
ProxyPassReverse  /iCingServer.py http://localhost:8000/iCingServer.py
"""
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityDetail
from cing import verbosityOutput
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import quoteForJson
from cing.Libs.disk import tail
from cing.Libs.forkoff import ForkOff
from cing.Libs.forkoff import do_cmd
from cing.Libs.test.test_Forkoff import my_sleep
import cgi
import cing
import os

FORM_ACCESS_KEY = "AccessKey"
FORM_USER_ID = "UserId"
FORM_UPLOAD_FILE_BASE = "UploadFile"
FORM_ACTION = "Action"
FORM_ACTION_RUN = "Run"
FORM_ACTION_SAVE = "Save"
FORM_ACTION_STATUS = "Status"
FORM_DO_WHATIF = "doWhatif"
FORM_DO_PROCHECK = "doProcheck"
FORM_DO_IMAGES = "doImages"

FORM_LIST_REQUIRED = [ FORM_ACCESS_KEY, FORM_USER_ID, FORM_ACTION ]
JSON_ERROR_STATUS = "error"

MAX_FILE_SIZE_BYTES = 1024 * 1024 * 1 # 50 Mb when time out issue is resolved. TODO: update. 
BUFFER_WRITE = 100*1000

# Number of seconds to wait around for forking to happen
MAX_TIME_TO_WAIT_FORKOFF = 2
# Number of seconds after which the killer process can kill/zombie the runner.
MAX_TIME_TO_RUN = 10 * 60

PYTHON_EXECUTABLE = "/sw/bin/python"
#CING_SCRIPT = "$CINGROOT/python/cing/main.py"
CING_SCRIPT = "$CINGROOT/python/cing/iCing/dummyRun.py"
CING_OPTIONS = "--initCcpn"

server_cgi_url_tmp = "localhost/tmp/cing"
cing_server_tmp = "/Library/WebServer/Documents/tmp/cing"

RESPONSE_CODE_200_OK = 200
RESPONSE_CODE_400_BAD_REQUEST = 400
RESPONSE_CODE_404_NOT_FOUND = 404
# server port
PORT_SERVER = 8000
PORT_CGI = 8001

DONE_FILE = "DONE"
CING_RUN_LOG_FILE = "cingRun.log"

# server response codes.
RESPONSE_STATUS = "status" # follows a clien request FORM_ACTION_STATUS 
RESPONSE_STATUS_DONE = "done"
RESPONSE_STATUS_NOT_DONE = "not done"
RESPONSE_STATUS_ERROR = "error"
RESPONSE_STATUS_MESSAGE = "message"
RESPONSE_TAIL_PROGRESS = "tail progress"
 
class iCingServerHandler(BaseHTTPRequestHandler):
    def sendJSON(self, kwds={} ):        
#        self.send_response(responseCode)   
#        self.send_header('Content-type',    'text/plain')                 
#        self.end_headers()
#        self.wfile.write(msg+"\n");
        """
        For list of codes look at: BaseHTTPRequestHandler.responses dictionary
        Make sure that the caller exits.
        """        
        body =  "{\n"
        for key in kwds.keys():
            keyStr = quoteForJson(key)
            valueStr = quoteForJson(kwds[key])
            body += "%s: %s,\n" % ( keyStr, valueStr ) # extra comma is harmless.
        body +=  "}\n"

        try: # gives a broken pipe but works fine otherwise.... TODO: figure out why 
            self.send_response(RESPONSE_CODE_200_OK) # otherwise we can't send a body?
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', len(body))
            self.send_header('Expires', '-1')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Pragma', 'no-cache')
            self.end_headers()
            
            self.wfile.write(body)
            self.wfile.flush()
            self.connection.shutdown(1)
        except:
            pass
        
    def do_POST(self):    
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        if ctype != 'multipart/form-data':
            self.sendJSON({RESPONSE_STATUS_ERROR: 'Received data is not: multipart/form-data'})
            return
        self.form=cgi.parse_multipart(self.rfile, pdict)

        for expectedKey in FORM_LIST_REQUIRED:
            if not self.form.has_key(expectedKey):
                self.sendJSON({RESPONSE_STATUS_ERROR: "Missing form field: [" + expectedKey + ']'})
                return
        NTdebug("Processing do_POST")
        self.formDict={}
        for key in self.form.keys():
            self.formDict[ key ] = self.form[ key ][0]
        
        action = self.formDict[ FORM_ACTION ]
        self.user_id = self.formDict[ FORM_USER_ID ]
        self.access_key = self.formDict[ FORM_ACCESS_KEY ]
        
#        NTdebug('Got user_id: ' + self.user_id)
        self.pathUser = os.path.join(cing_server_tmp, self.user_id)
#        NTdebug('Got pathUser: ' + self.pathUser)
        
        self.pathProject = os.path.join(self.pathUser, self.access_key)        
        NTdebug('Got pathProject: ' + self.pathProject)
        if not os.path.exists(self.pathProject):
#            NTdebug('pathProject does not exist')
            try:
                os.makedirs(self.pathProject) # defaults to False return.
            except Exception, e:
                msg = "Failed to makedirs for project at: [" + self.pathProject + "] with Exception: ["+`e`+"]"
                self.sendJSON({RESPONSE_STATUS_ERROR: msg})
                return
        
        if os.chdir(self.pathProject):
            msg = "Failed to change to dir: %s" % self.pathProject
            self.sendJSON({RESPONSE_STATUS_ERROR: msg})
            return
            
        if action == FORM_ACTION_RUN:
            self.run()
        if action == FORM_ACTION_STATUS:
            self.getStatus()
        else:
            msg = "Unknown action: %s" % action
            self.sendJSON({RESPONSE_STATUS_ERROR: msg})
        # no code here but a return!
                        
    def run(self):
        """Start a validation run.
        """        
        if os.path.exists(DONE_FILE):
            os.remove(DONE_FILE) # Can't be done when not started.
        if os.path.exists(CING_RUN_LOG_FILE):
            os.remove(CING_RUN_LOG_FILE) # Can't be done when not started.
            
        f = ForkOff(
                processes_max       = 9999,
                max_time_to_wait    = MAX_TIME_TO_WAIT_FORKOFF,
                max_time_to_wait_kill = 1, # not sure if this should be changed from the default 5
                verbosity           = cing.verbosity,
                
                )
    
    
        # is the done file guaranteed to be in the cwd?
        cmdRunStarting = "(date;echo 'Starting cing run') >> %s 2>&1" % CING_RUN_LOG_FILE
        cmdRunKiller = "(date;echo 'Pretending to start cing killer run') >> %s 2>&1 &" % CING_RUN_LOG_FILE
        cmdRunDone = "touch %s" % DONE_FILE
        cmdRun = "(%s -u %s %s; %s ) >> %s 2>&1 &" % (
            PYTHON_EXECUTABLE,
            CING_SCRIPT,
            CING_OPTIONS,
            cmdRunDone,
            CING_RUN_LOG_FILE
            )
        
        NTmessage("cmdRunStarting: [%s]" % cmdRunStarting)
        NTmessage("cmdRunKiller: [%s]" % cmdRunKiller)
        NTmessage("cmdRun: [%s]" % cmdRun)
        ## For debugging. Sleep too long.
        job_0       = ( do_cmd, (cmdRunStarting,) )
        ## Send the killer on the way first which will kill the actual runner
        job_1       = ( do_cmd, (cmdRunKiller,) )
        ## Runner
        job_2       = ( do_cmd, (cmdRun,) )
        ## For debugging. Sleep too long.
        job_3       = ( my_sleep, (9999,) ) # will be killed by forker
        job_list    = [ job_0, job_1, job_2, job_3 ]    
        NTmessage("Submitting jobs to the shell")
        done_list   = f.forkoff_start( job_list, delay_between_submitting_jobs=0 )    
        NTmessage("Finished ids: %s", done_list)
                
        self.sendJSON({RESPONSE_STATUS_MESSAGE: "Started a run"})
        
    def getStatus(self):
        """Fails because form can't be loaded with large data thru non-cgi
        """        
        NTdebug('Retrieving server status.')
        kwd={}
        responseStatus= RESPONSE_STATUS_NOT_DONE
        if os.path.exists(DONE_FILE):
            responseStatus = RESPONSE_STATUS_DONE
        kwd[ RESPONSE_STATUS ] = responseStatus 

        kwd[ RESPONSE_TAIL_PROGRESS ] = "No log file so far"
        if os.path.exists(CING_RUN_LOG_FILE):
            try:
                f = open(CING_RUN_LOG_FILE,'r')
                lastLineList = tail(f,1)
                if lastLineList:
                    kwd[ RESPONSE_TAIL_PROGRESS ] = lastLineList[0]
            finally:
                f.close()
            
        self.sendJSON(kwd)
        
        
    def do_GET(self):
        self.sendJSONResponse("Access denied through do_GET()")


def main():
    os.chdir(cingDirTmp)
    
    try:
        server = HTTPServer(('', 8000), iCingServerHandler)
        print 'started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received'
    finally:
        print 'shutting down server'
        try:
            server.socket.close()
        except:
            pass

if __name__ == '__main__':
    cing.verbosity = verbosityDetail
    cing.verbosity = verbosityOutput
    cing.verbosity = verbosityDebug    
    main()
