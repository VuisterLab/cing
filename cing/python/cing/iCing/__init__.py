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

server_cgi_url_tmp = "localhost/tmp/cing"
cing_server_tmp = "/Library/WebServer/Documents/tmp/cing"

RESPONSE_CODE_200_OK = 200
RESPONSE_CODE_400_BAD_REQUEST = 400
RESPONSE_CODE_404_NOT_FOUND = 404
# server port
PORT_SERVER = 8000
PORT_CGI = 8001
