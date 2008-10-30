package cing.client;

/** Settings for both the client and server code */
public interface Keys {
	public static final String SERVLET_URL = "serv/iCingServlet";
	public static final int accessKeyLength = 6;
	public static final String NOT_AVAILABLE = "not available";
	public static final String RESULT_URL = "tmp/cing";
	/** The next statement should not be changed by a single char */
	public static final String VERSION ="20081030-1320";

	public static final String FORM_PARM_ACTION = "Action";
	public static final String FORM_PARM_USER_ID = "UserId";
	public static final String FORM_PARM_ACCESS_KEY = "AccessKey";
	public static final String FORM_PARM_UPLOAD_FILE_BASE = "UploadFile";
	public static final String[] FORM_PARM_MINIMUM = new String[] { FORM_PARM_USER_ID, FORM_PARM_ACCESS_KEY, FORM_PARM_ACTION} ;
	public static final String FORM_ACTION_LOG = "Log";
	public static final String FORM_ACTION_PROJECT_NAME = "ProjectName";
	public static final String FORM_ACTION_READINESS = "Readiness";
	public static final String FORM_ACTION_SAVE = "Save";
	public static final String FORM_ACTION_RUN = "Run";
	/**
	 * The RESPONSE_EXIT_CODE is special in that it is always returned by the server to indicate the general
	 * server result status.
	 */
	public static final String RESPONSE_EXIT_CODE = "ExitCode";
	public static final String RESPONSE_EXIT_CODE_ERROR = "Error";
	public static final String RESPONSE_EXIT_CODE_SUCCESS = "Success";
	public static final String RESPONSE_RESULT = "Result";
	public static final String RESPONSE_STATUS_NOT_DONE = "notDone";
	public static final String RESPONSE_STATUS_DONE = "done";
	public static final Object RESPONSE_STATUS_NONE = null;	
}
