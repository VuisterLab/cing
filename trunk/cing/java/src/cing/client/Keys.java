package cing.client;

import java.util.ArrayList;
import java.util.Arrays;

/** Settings for both the client and server code */
public interface Keys {
	public static final String SERVLET_URL = "serv/iCingServlet";
	public static final int accessKeyLength = 6;
	public static final String NOT_AVAILABLE = "not available";
	public static final String RESULT_URL = "tmp/cing";
	/** The next statement should not be changed by a single char */
	public static final String VERSION ="20081110-1327";

	public static final String None = "None";

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
	public static final String RESPONSE_ACTION_DEFAULT = None;
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
	public static final String RESPONSE_RESULT_DEFAULT = None;
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
