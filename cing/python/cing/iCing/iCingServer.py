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
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTpath
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import quoteForJson
from cing.Libs.forkoff import ForkOff
from cing.Libs.forkoff import do_cmd
from glob import glob
import cgi
import cing
import os
#from cing.Libs.disk import tail

FORM_ACCESS_KEY = "AccessKey"
FORM_USER_ID = "UserId"
FORM_UPLOAD_FILE_BASE = "UploadFile"
FORM_ACTION = "Action"
FORM_ACTION_RUN = "Run"
FORM_ACTION_SAVE = "Save"
FORM_ACTION_STATUS = "Status"
FORM_ACTION_PROJECT_NAME = "ProjectName"
FORM_ACTION_LOG = "Log"
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
CING_SCRIPT = "$CINGROOT/python/cing/main.py"
#CING_SCRIPT = "$CINGROOT/python/cing/iCing/test/dummyRun.py"

server_cgi_url_tmp = "localhost/tmp/cing"
cing_server_tmp = "/Library/WebServer/Documents/tmp/cing"

RESPONSE_CODE_200_OK = 200
RESPONSE_CODE_400_BAD_REQUEST = 400
RESPONSE_CODE_404_NOT_FOUND = 404
# server port
PORT_SERVER = 8000
PORT_CGI = 8001

DONE_FILE = "DONE"
"Contains the string representation of the byte length already read from the log file before"
LAST_LOG_SEND_FILE = ".LAST_LOG_SEND" 
CING_RUN_LOG_FILE = "cingRun.log"

# server response codes.
RESPONSE_STATUS = "status" # follows a clien request FORM_ACTION_STATUS 
RESPONSE_STATUS_DONE = "done"
RESPONSE_STATUS_NOT_DONE = "notDone"
RESPONSE_STATUS_ERROR = "error"
RESPONSE_STATUS_MESSAGE = "message"
RESPONSE_TAIL_PROGRESS = "tailProgress"
RESPONSE_PROJECT_NAME = "projectName"
RESPONSE_NONE = "None"


 
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
        body =  "{"
        keyList = kwds.keys()
        for key in keyList:
            keyStr = quoteForJson(key)
            valueStr = quoteForJson(kwds[key], isValue=True)
            body += "%s: %s," % ( keyStr, valueStr ) # extra comma is harmless.
        if len(keyList):
            body = body[:-1] # get rid of the extra comma anywho.
        body +=  "}"

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
                if os.path.exists(self.pathUser):
                    mod = 0555 # dir is not readable but is executable
#                    mod = 'u-r'
                    NTdebug("Setting mod")
                    os.chmod(self.pathUser, mod) 
                    # This prevents people from seeing a user x but not the project's secret access_id's
                    # If the secret access_id is know that dir can be retrieved. Same as Aqua server
                    # which worked fine for a million years.
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
        if action == FORM_ACTION_LOG:
            self.getLog()
        if action == FORM_ACTION_PROJECT_NAME:
            self.getProjectName()
            
        else:
            msg = "Unknown action: %s" % action
            self.sendJSON({RESPONSE_STATUS_ERROR: msg})
        # no code here but a return!
                        
    def run(self):
        """Start a validation run.
        """        
        
#    def run(self):        
#
#        logToLog('Now in pathProject: ' + pathProject)        
#        doWhatif   =      form.has_key(FORM_DO_WHATIF)  and form[FORM_DO_WHATIF].value   == 'on'
#        doProcheck =      form.has_key(FORM_DO_PROCHECK) and form[FORM_DO_PROCHECK].value == 'on'
#        htmlOnly   = not (form.has_key(FORM_DO_IMAGES)   and form[FORM_DO_IMAGES].value   == 'on')
#        msg = "<p>doWhatif     %3s" % doWhatif
#        msg +="\n<p>doProcheck   %3s" % doProcheck
#        msg +="\n<p>htmlOnly     %3s" % htmlOnly
#        
#        fastestTest = True
#        if fastestTest:
#            htmlOnly = True 
#            doWhatif = False
#            doProcheck = False
#
#        
#        projectList = glob("*.tgz")
#        if len(projectList) == 0:
#            endError("Failed to get any ccpn project on disk with .tgz")
#        projectFile = projectList[0]
#        if len(projectList) > 1:
#            logToLog("Got more than one project file; taking first one: " + projectFile)            
#        (_directory, entryId, _extension)  = NTpath(projectFile)
#        project = Project.open(entryId, status='new')
#        
#        ccpnFile = projectFile
#        try:
#            rmtree(entryId) # remove if present before.
#        except:
#            pass
#        tar = tarfile.open(ccpnFile, "r:gz")
#        for itar in tar:
#            tar.extract(itar.name, '.')
#
#        org = 'linkNmrStarData' # TODO: mod the NRG examples to follow this convention too.
#        if not entryId[0].isdigit():  # pdb file?
#            org = entryId
#        move(org, entryId)
#        project.initCcpn(ccpnFolder=entryId)
#        project.save()
#        project.validate(
#          htmlOnly=htmlOnly,
#          doProcheck = doProcheck,
#          doWhatif=doWhatif)
#        msg = "Finished validation"        
#        endMessage(msg)        
        if os.path.exists(DONE_FILE):
            os.remove(DONE_FILE) # Can't be done when not started.
        if os.path.exists(CING_RUN_LOG_FILE):
            os.remove(CING_RUN_LOG_FILE) # Can't be done when not started.
            
        f = ForkOff(
                processes_max       = 9999,
                max_time_to_wait    = MAX_TIME_TO_WAIT_FORKOFF,
                max_time_to_wait_kill = 1, # not sure if this should be changed from the default 5
                verbosity           = cing.verbosity                
                )
    
    
        # is the done file guaranteed to be in the cwd?
        cmdRunStarting = "(date;echo 'Starting cing run') >> %s 2>&1" % CING_RUN_LOG_FILE
        cmdRunKiller = "(date;echo 'Pretending to start cing killer run') >> %s 2>&1 &" % CING_RUN_LOG_FILE
        cmdRunDone = "touch %s" % DONE_FILE
        
        projectFile = self._getProjectFile()
        if not projectFile:
            self.sendJSON({RESPONSE_STATUS_ERROR: "Failed to find project file"})
            return
            
        projectName = self._getProjectName(projectFile)
        if not projectName:
            self.sendJSON({RESPONSE_STATUS_ERROR: "Failed to find project name"})
            return
        
        cing_options = "--name %s --initCcpn %s --nosave -v %s --script doValidateiCing.py" % (
            projectName, projectFile, cing.verbosity )

        cmdRun = "(%s -u %s %s; %s ) >> %s 2>&1 &" % (
            PYTHON_EXECUTABLE,
            CING_SCRIPT,
            cing_options,
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
        job_list    = [ job_0, job_1, job_2 ]    
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
        self.sendJSON(kwd)
        

    def getLog(self):
        NTdebug('Retrieving cing log tail.')
        kwd={}
        lastLog = "No log file so far"
        if os.path.exists(CING_RUN_LOG_FILE):
            try:
                cingrunLogFileSize = os.path.getsize(CING_RUN_LOG_FILE)
                cingrunLogFileSizeLast = 0
                if os.path.exists(LAST_LOG_SEND_FILE):
                    fl = open(LAST_LOG_SEND_FILE,'r')
                    cingrunLogFileSizeLast = fl.getline()
                    fl.close()
                    if cingrunLogFileSizeLast:
                        cingrunLogFileSizeLast = int(cingrunLogFileSizeLast)
                    os.remove(fl)
                # doesn't exist because it was just removed.
                fl = open(LAST_LOG_SEND_FILE,'w')
                fl.write( `cingrunLogFileSize` )
                fl.close()
                        
                if cingrunLogFileSize > cingrunLogFileSizeLast:
                    f = open(CING_RUN_LOG_FILE,'r')
                    f.seek(cingrunLogFileSizeLast)
                    lastLog = f.read( cingrunLogFileSize - cingrunLogFileSize )
                
#                lastLineList = tail(f,1)
#                if lastLineList:
#                    kwd[ RESPONSE_TAIL_PROGRESS ] = lastLineList[0]
            except:
                pass
            finally:
                f.close()            
        kwd[ RESPONSE_TAIL_PROGRESS ] = lastLog
        self.sendJSON(kwd)

    def getProjectName(self):
        NTdebug('Retrieving project name.')
        projectFile = self._getProjectFile()
        if not projectFile:
            NTerror( "Failed to find project file" )
            self.sendJSON({RESPONSE_PROJECT_NAME: RESPONSE_NONE})
            return
            
        projectName = self._getProjectName(projectFile)
        if not projectName:
            NTerror( "Failed to find project name" )
            self.sendJSON({RESPONSE_PROJECT_NAME: RESPONSE_NONE})
            return
        self.sendJSON({RESPONSE_PROJECT_NAME: projectName})
        
        
    def do_GET(self):
        self.sendJSON({RESPONSE_STATUS_ERROR: "Access denied through do_GET()"})

    def _getProjectFile(self):
        if not self.user_id:
            NTerror("Failed to get user id")
            return
        if not self.access_key:
            NTerror("Failed to get access key")
            return
        projectFileList = glob( "*.tgz" ) + glob( "*.tar.gz" )
        if len( projectFileList ) == 0:
            NTerror("Failed to get any project file")
            return
        if len( projectFileList ) > 1:
            NTwarning("Get multiple project files %s; picking first one." % projectFileList)
        return projectFileList[0]

    def _getProjectName(self, projectFile):
        if not projectFile:
            NTerror("In _getProjectName: Failed to get any project file")
            return
        (_directory, basename, _extension) = NTpath( projectFile )            
        projectName = basename
        return projectName

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
