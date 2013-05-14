package cing.client;

import java.util.ArrayList;
import java.util.Arrays;

/** Settings for both the client and server code */
public interface Settings {
    /** Just the initial startup state; for client and server. Server debug is set in servlet from this value.
     * Can NOT be left to true as it will be used by CING.*/
    public static final boolean DO_DEBUG = false;
    /** Instead of messages to the iCing log window; show them on the stdout stream
     * The iCing log is not showing by default anymore so this parameter is needed.
     * */
    public static final boolean DEBUG2STDOUT = true;
    /** The next statement is automatically updated. Don't even change spacing. Note there this is the current number and not the new one.*/
    public static final String REVISION = "1185";
    /** URL for svn site specific for certain revision. */
    public static final String CING_REVISION_URL = "http://code.google.com/p/cing/source/detail?r=";
    /** URL base only used in iCingRobot.java it's derived in iCing on the client side. */
    public static final String DEFAULT_URL = "https://nmr.cmbi.ru.nl";
    /** URL base for secure iCing */
    public static final String DEFAULT_URL_PATH = "icing";
//	#DEFAULT_URL_PATH = 'cing.iCing' # use for gwt embedded tomcat
    /** URL for NRG-CING. */
    public static final String NRG_CING_URL = "http://nmr.cmbi.ru.nl/NRG-CING";
    /** Local install location of CING */
//    public static final String CINGROOT = "/Users/jd/workspace35/cing";
    /** Wrapper to take care of environment settings and some os specific things. */
//    public static final String CING_WRAPPER_SCRIPT = CINGROOT + "/scripts/cing/CingWrapper.csh";
    public static final String CING_WRAPPER_SCRIPT = "scripts/cing/CingWrapper.csh";
    /** Relative url of results from a CING run */
    public static final String RESULT_URL = "/tmp/cing";
    /** Directory with the web server root documents. */
//    public static final String SERVER_ROOT_DIR = "/Library/WebServer/Documents";
    /** Directory with the CING run results. */
//    public static final String SERVER_TMP_DIR = SERVER_ROOT_DIR + "/" + RESULT_URL;
    /** 50 Mb ought to do it for now. The PDB file for 2k0e is 28 Mb. Which crashed the Servlet on Java out of memory. */
    public static final long FILE_UPLOAD_MAX_SIZE = 50 * 1024 * 1024;
    /** Name of file that indicates the CING run is done */
    public static final String DONE_FILE = "DONE";
    /** Name of file that holds a single long number with the last send log byte position */
    public static final String LAST_LOG_SEND_FILE = "LAST_LOG_SEND";
    /** Name of log file of CING run */
    public static final String CING_RUN_LOG_FILE = "cingRun.log";
    /** TODO remove dep. Needs to be defined from interface. */
    public static final int CING_VERBOSITY = 3;
    /** Number of characters of the unique secret key. */
    public static final int accessKeyLength = 6;
    /** When debugging the max number of chars to show on a response that might be way too long */
    public static final int MAX_RESPONSE_REPORTED_FOR_DEBUGGING = 80;

    // No changes below this line.
    public static final String ERROR_SIZE_UNACCEPTABLE = "File larger than: " + FILE_UPLOAD_MAX_SIZE + " bytes";
    public static final String ERROR_PARSE_REQUEST = "Failed to parse request";
    public static final String ERROR_WRITE_FAILED = "File write failed.";
    public static final String ERROR_NOT_MULTI_PART = "Not multipart message.";

    /** Url of servlet. */
    public static final String SERVLET_URL = "serv/iCingServlet";
    public static final String NOT_AVAILABLE = "not available";

    public static final String NONE = "NONE";

    public static final String FORM_PARM_ACTION = "Action";
    public static final String FORM_PARM_USER_ID = "UserId";
    public static final String FORM_PARM_ACCESS_KEY = "AccessKey";
    public static final String FORM_PARM_UPLOAD_FILE_BASE = "UploadFile";
    public static final String FORM_PARM_VERBOSITY = "Verbosity";
//    public static final String FORM_PARM_IMAGERY = "Imagery";
    public static final String FORM_PARM_RESIDUES = "Residues";
    public static final String FORM_PARM_ENSEMBLE = "Ensemble";

    public static final String FORM_PARM_USER_ID_ANONYMOUS = "anonymous";
    public static final String FORM_PARM_USER_ID_DEFAULT = FORM_PARM_USER_ID_ANONYMOUS;

    public static final String FORM_ACTION_LOG = "Log";
    public static final String FORM_ACTION_PROJECT_NAME = "ProjectName";
    public static final String FORM_ACTION_STATUS = "Status";
    public static final String FORM_ACTION_SAVE = "Save";
    public static final String FORM_ACTION_RUN = "Run";
    public static final String FORM_ACTION_PURGE = "Purge";
    public static final String FORM_ACTION_CRITERIA = "Criteria";

    public static final String ZIP_REPORT_FILENAME_POST_FIX = "_CING_report";
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
            FORM_ACTION_PURGE, FORM_ACTION_STATUS, FORM_ACTION_SAVE, FORM_ACTION_RUN, FORM_ACTION_LOG,
            FORM_ACTION_CRITERIA };
    public static final String[] FORM_PARM_MINIMUM = new String[] { FORM_PARM_USER_ID, FORM_PARM_ACCESS_KEY,
            FORM_PARM_ACTION };
    public static final String[] RESPONSE_EXIT_CODE_LIST = new String[] { RESPONSE_EXIT_CODE_ERROR,
            RESPONSE_EXIT_CODE_SUCCESS };

    public static final ArrayList<String> FORM_ACTION_ALIST = new ArrayList(Arrays.asList(FORM_ACTION_LIST));
    public static final ArrayList<String> RESPONSE_EXIT_CODE_ALIST = new ArrayList(Arrays
            .asList(RESPONSE_EXIT_CODE_LIST));
    public static final String RESPONSE_LOG_VALUE_NONE = RESPONSE_RESULT_DEFAULT;
    public static final String VAL_SETS_CFG_DEFAULT_FILENAME = "valSets.cfg";
    public static final String FILE_PROGRAM_CING = "CING";
    public static final String FILE_PROGRAM_CYANA = "CYANA";
    public static final String FILE_PROGRAM_CCPN = "CCPN";
    public static final String FILE_PROGRAM_PDB = "PDB";
    public static final String FILE_TYPE_PROJECT = "project";
    public static final String FILE_TYPE_VALIDATION_SETTINGS = "validation settings";
}
