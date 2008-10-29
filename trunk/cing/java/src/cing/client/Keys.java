package cing.client;

public interface Keys {
	public static final String FILE_UPLOAD_URL = "serv/fileupload";
	public static final int accessKeyLength = 6;
	public static final String SERVER_URL = "server-bin"; // proxied to: :8000
	public static final String NOT_AVAILABLE = "not available";
	public static final String RESULT_URL = "tmp/cing";
	/** The next statement should not be changed by a single char */
	public static final String VERSION = "20081029-2009";
	/** Just the initial startup state */
	public static final boolean doDebug = true;
	public static final String RESPONSE_SAVE_MESSAGE = "message";
	/**
	 * Watch out these variables can not be referenced in the iCing server code.
	 * Enforce consistency with the iCing server code and the python server code
	 * MANUALLY!
	 * 
	 * The RESPONSE_GENERAL_ERROR is special in that it can always be returned
	 * by the server to indicate a general server error such as
	 * "project not found".
	 */
	public static final String RESPONSE_GENERAL_ERROR = "error";
	/** Special meaning to do special behavior */
	public static final String RESPONSE_TAIL_VALUE_NONE = "None";
	public static final String RESPONSE_TAIL_PROGRESS = "tailProgress";
	public static final String RESPONSE_STATUS_NONE = "None";
	public static final String RESPONSE_STATUS_PROJECT_NAME = "projectName";
	public static final String RESPONSE_STATUS_NOT_DONE = "notDone";
	public static final String RESPONSE_STATUS_DONE = "done";
	public static final String RESPONSE_STATUS = "status";
	public static final String RESPONSE_ACTION = "action";
	public static final String RUN_SERVER_ACTION_LOG = "Log";
	public static final String RUN_SERVER_ACTION_PROJECT_NAME = "ProjectName";
	public static final String RUN_SERVER_ACTION_STATUS = "Status";
	public static final String RUN_SERVER_ACTION_SAVE = "Save";
	public static final String RUN_SERVER_ACTION_RUN = "Run";
	public static final String FORM_UPLOAD_FILE_BASE = "UploadFile";
	public static final String FORM_USER_ID = "UserId";
	public static final String FORM_ACCESS_KEY = "AccessKey";
	public static final String FORM_ACTION = "Action";
	public static final String REPORT_STATE = "report";
	public static final String RUN_STATE = "run";
	public static final String OPTIONS_STATE = "options";
	public static final String CRITERIA_STATE = "criteria";
	public static final String CING_LOG_STATE = "cingLog";
	public static final String LOG_STATE = "log";
	public static final String FILE_STATE = "file";
	public static final String PREFERENCES_STATE = "preferences";
	public static final String WELCOME_STATE = "welcome";

}
