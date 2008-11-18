package cing.client;

import java.util.ArrayList;
import java.util.Arrays;

/** Settings for both the client and server code */
public interface Settings {
    /** Local install location of CING */
    public static final String CINGROOT = "/Users/jd/workspace34/cing";
    /** Wrapper to take care of environment settings and some os specific things. */
    public static final String CING_WRAPPER_SCRIPT = CINGROOT + "/scripts/cing/CingWrapper.csh";
    /** Relative url of results from a CING run */
    public static final String RESULT_URL = "/tmp/cing";
    /** Directory with the web server root documents. */
    public static final String SERVER_ROOT_DIR = "/Library/WebServer/Documents";
    /** Directory with the CING run results. */
    public static final String SERVER_TMP_DIR = SERVER_ROOT_DIR + "/" + RESULT_URL;
    /** 10 Mb ought to do it for now. 100 in the future? */
    public static final long FILE_UPLOAD_MAX_SIZE = 10 * 1024 * 1024;
    /** Name of file that indicates the CING run is done */
    public static final String DONE_FILE = "DONE";
    /** Name of file that holds a single long number with the last send log byte position */
    public static final String LAST_LOG_SEND_FILE = "LAST_LOG_SEND";
    /** Name of log file of CING run */
    public static final String CING_RUN_LOG_FILE = "cingRun.log";
    /** TODO remove dep. Needs to be defined from interface. */
    public static final int CING_VERBOSITY = 9;
    /** Number of characters of the unique secret key. */
    public static final int accessKeyLength = 6;
    /** When debugging the max number of chars to show on a response that might be way too long */
    public static final int MAX_RESPONSE_REPORTED_FOR_DEBUGGING = 80;

    // No changes below this line.
    public static final String ERROR_SIZE_UNACCEPTABLE = "File larger than: " + FILE_UPLOAD_MAX_SIZE + " bytes";
    public static final String ERROR_PARSE_REQUEST = "Failed to parse request";
    public static final String ERROR_WRITE_FAILED = "File write failed.";
    public static final String ERROR_NOT_MULTI_PART = "Not multipart message.";

    /** Url of servlet. Is hard coded in several places in GWT setup. Match! */
    public static final String SERVLET_URL = "serv/iCingServlet";
    public static final String NOT_AVAILABLE = "not available";
    /** The next statement should not be changed by a single char. It gets updated by ant make file. */
    public static final String VERSION = "20081118-1437";

    public static final String NONE = "NONE";

    public static final String FORM_PARM_ACTION = "Action";
    public static final String FORM_PARM_USER_ID = "UserId";
    public static final String FORM_PARM_ACCESS_KEY = "AccessKey";
    public static final String FORM_PARM_UPLOAD_FILE_BASE = "UploadFile";

    public static final String FORM_PARM_USER_ID_ANONYMOUS = "anonymous";
    public static final String FORM_PARM_USER_ID_DEFAULT = FORM_PARM_USER_ID_ANONYMOUS;

    public static final String FORM_ACTION_LOG = "Log";
    public static final String FORM_ACTION_PROJECT_NAME = "ProjectName";
    public static final String FORM_ACTION_STATUS = "Status";
    public static final String FORM_ACTION_SAVE = "Save";
    public static final String FORM_ACTION_RUN = "Run";

    /** No default response action really. */
    public static final String RESPONSE_ACTION_DEFAULT = NONE;
    /**
     * The RESPONSE_EXIT_CODE is special in that it is always returned by the server to indicate the general server
     * result status.
     */
    public static final String RESPONSE_EXIT_CODE = "ExitCode";
    public static final String RESPONSE_EXIT_CODE_ERROR = "Error";
    public static final String RESPONSE_EXIT_CODE_SUCCESS = "Success";
    public static final String RESPONSE_EXIT_CODE_DEFAULT = RESPONSE_EXIT_CODE_ERROR;

    public static final String RESPONSE_RESULT = "Result";
    public static final String RESPONSE_STATUS_NOT_DONE = "notDone";
    public static final String RESPONSE_STATUS_DONE = "done";
    public static final String RESPONSE_RESULT_DEFAULT = NONE;
    public static final String RESPONSE_STARTED = "started";

    static final ArrayList<String> validResponseKeys = new ArrayList();
    static final ArrayList<String> validResponseStatusValues = new ArrayList();

    public static final String[] FORM_ACTION_LIST = new String[] { FORM_ACTION_LOG, FORM_ACTION_PROJECT_NAME,
            FORM_ACTION_STATUS, FORM_ACTION_SAVE, FORM_ACTION_RUN, FORM_ACTION_LOG };
    public static final String[] FORM_PARM_MINIMUM = new String[] { FORM_PARM_USER_ID, FORM_PARM_ACCESS_KEY,
            FORM_PARM_ACTION };
    public static final String[] RESPONSE_EXIT_CODE_LIST = new String[] { RESPONSE_EXIT_CODE_ERROR,
            RESPONSE_EXIT_CODE_SUCCESS };

    public static final ArrayList<String> FORM_ACTION_ALIST = new ArrayList(Arrays.asList(FORM_ACTION_LIST));
    public static final ArrayList<String> RESPONSE_EXIT_CODE_ALIST = new ArrayList(Arrays
            .asList(RESPONSE_EXIT_CODE_LIST));
    public static final String RESPONSE_LOG_VALUE_NONE = RESPONSE_RESULT_DEFAULT;

}
