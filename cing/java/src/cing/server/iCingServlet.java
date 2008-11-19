package cing.server;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.util.List;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.commons.fileupload.FileItem;
import org.apache.commons.fileupload.FileItemFactory;
import org.apache.commons.fileupload.FileUploadException;
import org.apache.commons.fileupload.ProgressListener;
import org.apache.commons.fileupload.disk.DiskFileItemFactory;
import org.apache.commons.fileupload.servlet.ServletFileUpload;
import org.json.JSONException;
import org.json.JSONObject;

import Wattos.Utils.General;
import Wattos.Utils.InOut;
import Wattos.Utils.OSExec;
import Wattos.Utils.StringArrayList;
import Wattos.Utils.Strings;
import cing.client.Settings;

import com.braju.format.Format;
import com.braju.format.Parameters;

public class iCingServlet extends HttpServlet {
	private static final long serialVersionUID = 6098745782027999297L;

	public void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException,
			java.io.IOException {
		writeJsonError(response, "Denying iCingServlet.doGet. Try a POST.");
	}

	/**
	 * Return a json string to file formPanel handler with only one element: {"error","reason"} or {"message","999 kb"}
	 * */
	public void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException,
			java.io.IOException {
		General.showDebug("processing doPost");
		JSONObject result = new JSONObject();

		File pathUser = null;
		File pathProject = null;
		FileItem actualFileItem = null;
		String currentAccessKey = null;
		String currentUserId = Settings.FORM_PARM_USER_ID_DEFAULT;
		String currentAction = null;

		FileItemFactory factory = new DiskFileItemFactory();
		ServletFileUpload upload = new ServletFileUpload(factory);
		List<FileItem> items = null;

		// Create a progress listener on server side; pretty useless, so far but
		// when pushed to client can be nice.
		ProgressListener progressListener = new ProgressListener() {
			private long batchesRead = -1; // Currently read.
			private long bytesPerBatch = 100 * 1024; // 10 k incremental report

			// increase when done
			// testing.

			public void update(long pBytesRead, long pContentLength, int pItems) {
				long batchCurrentRead = pBytesRead / bytesPerBatch;
				if (batchesRead == batchCurrentRead) {
					return; // no report.
				}
				batchesRead = batchCurrentRead;
				String pBytesReadStr = Ut.bytesToFormattedString(pBytesRead);
				String pContentLengthStr = Ut.bytesToFormattedString(pContentLength);

				if (pContentLength == -1) {
					General.showDebug("So far, " + pBytesReadStr + " have been read from item[" + pItems + "].");
				} else {
					General.showDebug("So far, " + pBytesReadStr + " of " + pContentLengthStr
							+ " have been read from item[" + pItems + "].");
				}
			}
		};

		upload.setProgressListener(progressListener);
		// Check that we have a file upload request
		boolean isMultipart = ServletFileUpload.isMultipartContent(request);
		if (!isMultipart) {
			writeJsonError(response, Settings.ERROR_NOT_MULTI_PART);
			return;
		}

		try {
			items = upload.parseRequest(request);
		} catch (FileUploadException e) {
			e.printStackTrace();
			writeJsonError(response, Settings.ERROR_PARSE_REQUEST);
			return;
		}

		if (items == null) {
			writeJsonError(response, "Got a serious error while: upload.parseRequest(request).");
			return;
		}

		if (items.size() < Settings.FORM_PARM_MINIMUM.length) {
			String msg = "Got " + items.size() + " items which is less than the expected:"
					+ Settings.FORM_PARM_MINIMUM.length + " items.";
			writeJsonError(response, msg);
			return;
		}

		for (int i = 0; i < items.size(); i++) {
			FileItem item = items.get(i);
			String name = item.getFieldName();
			String value = item.getString();
			// General.showDebug("processing formPanel item: [" + name + "] with value: [" + value + "]");
			if (item.isFormField()) {
				if (name.equals(Settings.FORM_PARM_ACCESS_KEY)) {
					currentAccessKey = value;
					General.showDebug("retrieved currentAccessKey: " + currentAccessKey);
					continue;
				}
				if (name.equals(Settings.FORM_PARM_USER_ID)) {
					currentUserId = value;
					General.showDebug("retrieved currentUserId: " + currentUserId);
					continue;
				}
				if (name.equals(Settings.FORM_PARM_ACTION)) {
					currentAction = value;
					jsonResultPut(result, Settings.FORM_PARM_ACTION, currentAction);
					General.showDebug("retrieved action: " + currentAction);
					continue;
				}
				// When the routine falls thru to here the parameter was not recognized.
				if (value == null) {
					value = Settings.NONE;
				}
				int endIndex = Math.min(100, value.length());
				value = value.substring(0, endIndex);
				String msg = "Parameter [" + name + "] with value (first 100 bytes): [" + value + "] was unexpected.";
				writeJsonError(response, result, msg);
				return;
			} else {
				actualFileItem = item;
				General.showDebug("retrieved actualFileItem: " + actualFileItem);
			}
		}

		if (currentAction == null) {
			writeJsonError(response, result, "Failed to retrieve Action.");
			return;
		}
		if (currentAccessKey == null) {
			writeJsonError(response, result, "Failed to retrieve " + Settings.FORM_PARM_ACCESS_KEY);
			return;
		}
		if (currentUserId == null) {
			writeJsonError(response, result, "Failed to retrieve  " + Settings.FORM_PARM_USER_ID);
			return;
		}

		if (!Settings.FORM_ACTION_ALIST.contains(currentAction)) {
			writeJsonError(response, result, "Requested action unknown:  " + currentAction);
			return;
		}

		pathUser = new File(Settings.SERVER_TMP_DIR, currentUserId);
		if (!pathUser.exists()) {
			if (!pathUser.mkdir()) {
				writeJsonError(response, result, "Failed to mkdir for user at: [" + pathUser + "]");
				return;
			}
			InOut.chmod(pathUser, "a+rw");
		}
		pathProject = new File(pathUser, currentAccessKey);
		if (!pathProject.exists()) {
			if (!pathProject.mkdir()) {
				writeJsonError(response, result, "Failed to mkdir for project at: [" + pathProject + "]");
				return;
			}
			InOut.chmod(pathProject, "a+rw");
		}

		if (currentAction.equals(Settings.FORM_ACTION_SAVE)) {
			processFile(response, result, pathProject, actualFileItem);
		} else if (currentAction.equals(Settings.FORM_ACTION_PROJECT_NAME)) {
			processPname(response, result, pathProject);
		} else if (currentAction.equals(Settings.FORM_ACTION_LOG)) {
			processLog(response, result, pathProject);
		} else if (currentAction.equals(Settings.FORM_ACTION_STATUS)) {
			processStatus(response, result, pathProject);
		} else if (currentAction.equals(Settings.FORM_ACTION_RUN)) {
			processRun(response, result, pathProject);
		} else {
			// Would be a code bug as is checked before.
			writeJsonError(response, result, "Requested action unknown:  " + currentAction + " [CODE ERROR]");
			return;
		}
	}

	private void processPname(HttpServletResponse response, JSONObject result, File pathProject) {

		String regexp = ".*.tgz";
//		General.showOutput("Reg exp files: " + regexp);
//		General.showOutput("Dir: " + pathProject);
		InOut.RegExpFilenameFilter ff = new InOut.RegExpFilenameFilter(regexp);
		String[] list = pathProject.list(ff);

		General.showOutput("Found files: " + Strings.toString(list));
		General.showOutput("Found number of files: " + list.length);

		if (list.length < 1) {
			writeJsonError(response, result, "No project files found");
			return;
		}
		String projectName = list[0];
		projectName = InOut.getFilenameBase(projectName);
		jsonResultPut(result, Settings.RESPONSE_RESULT, projectName);
		writeJson(response, result);
	}

	private void jsonResultPut(JSONObject result, String key, String value) {
		try {
			result.put(key, value);
		} catch (JSONException e) {
			General.showError("Failed to JSONObject.put [" + key + "] [" + key + "]");
			e.printStackTrace();
		}
	}

	/**
	 * If the exit code was not set yet then set it to success
	 * 
	 * @param response
	 * @param result
	 */
	private void writeJson(HttpServletResponse response, JSONObject result) {
		if (!result.has(Settings.RESPONSE_EXIT_CODE)) {
			jsonResultPut(result, Settings.RESPONSE_EXIT_CODE, Settings.RESPONSE_EXIT_CODE_SUCCESS);
		}
		String responseStr = result.toString();
		int endIndex = Math.min(responseStr.length(), Settings.MAX_RESPONSE_REPORTED_FOR_DEBUGGING);
		String responseStrTruncate = responseStr.substring(0,endIndex).replace(General.eol, "");
		General.showDebug("responseTruncate is: [" + responseStrTruncate + "]");
		
		response.setContentType("text/plain");
		try {
			response.getWriter().write(result.toString());
		} catch (IOException e) {
			e.printStackTrace();
			return;
		}
	}

	private void writeJsonError(HttpServletResponse response, JSONObject result, String msg) {
		jsonResultPut(result, Settings.RESPONSE_EXIT_CODE, Settings.RESPONSE_EXIT_CODE_ERROR);
		jsonResultPut(result, Settings.RESPONSE_RESULT, msg);
		writeJson(response, result);
	}

	private void writeJsonError(HttpServletResponse response, String msg) {
		JSONObject result = new JSONObject();
		writeJsonError(response, result, msg);
	}

	/**
	 * 
	 * @param response
	 * @param result
	 * @param pathProject
	 * @return null on error.
	 */
	private String getProjectFile(HttpServletResponse response, JSONObject result, File pathProject) {

		String regexp = ".*.tgz";
//		General.showOutput("Reg exp files: " + regexp);
		General.showOutput("Dir: " + pathProject);
		InOut.RegExpFilenameFilter ff = new InOut.RegExpFilenameFilter(regexp);
		String[] list = pathProject.list(ff);

		General.showOutput("Found files: " + Strings.toString(list));
		General.showOutput("Found number of files: " + list.length);

		if (list.length < 1) {
			writeJsonError(response, result, "No project files found");
			return null;
		}
		String projectName = list[0];
		String projectFileName = InOut.getFileName(projectName);
		return projectFileName;
	}

	/**
	 * Actually saves the file
	 * 
	 * @param item
	 * @return a JSON string.
	 */
	private void processRun(HttpServletResponse response, JSONObject result, File pathProject) {

		File doneFile = new File(pathProject, Settings.DONE_FILE);
		File cingRunLogFile = new File(pathProject, Settings.CING_RUN_LOG_FILE);
		File lastLogSendFile = new File(pathProject, Settings.LAST_LOG_SEND_FILE);
		
		File[] fileListToDelete = new File[] { doneFile, cingRunLogFile, lastLogSendFile };
		for (int i=0;i< fileListToDelete.length;i++) {
			File f = fileListToDelete[i];
			if (f.exists()) {
				f.delete();
			}
		}
		// Note that Java has no current working directory so no Unix cd equivalent
		// Commands will be executed in csh by Wattos by default.
		String cmdCdProjectDir = "cd " + pathProject;
		// String cmdRunStarting = "(" + cmdCd + ";date;echo 'Starting cing run') >> " + cingRunLogFile + " 2>&1"; //
		// leave as an example of complex redirection under bash instead of tcsh.
		String cmdRunStarting = "(" + cmdCdProjectDir + ";date;echo 'Starting cing run') >>& " + cingRunLogFile;
		String cmdRunKiller = "(" + cmdCdProjectDir + ";date;echo 'As if starting killer') >>& " + cingRunLogFile
				+ " &";
		String cmdRunDone = "touch " + doneFile; // Using absolute path so no cd needed.

		String projectFileName = getProjectFile(response, result, pathProject);
		if (projectFileName == null) {
			// Will already have generated a Json error back.
			return;
		}

		String projectName = InOut.getFilenameBase(projectFileName);
		if (projectFileName == null) {
			writeJsonError(response, result, "Failed to find project name");
			return;
		}

		/**
		 * For the long command string it's real nice to have the overview layed out in a printf way
		 */
		Parameters p = new Parameters(); // Printf parameters autoclearing after use.
		p.add(projectName);
		p.add(projectFileName);
		p.add(Settings.CING_VERBOSITY);
		String cing_options = Format.sprintf("--name %s --initCcpn %s -v %s --script doValidateiCing.py", p);

		p.add(cmdCdProjectDir);
		p.add(Settings.CING_WRAPPER_SCRIPT);
		p.add(cing_options);
		p.add(cmdRunDone);
		p.add(cingRunLogFile);
		String cmdRun = Format.sprintf("(%s; %s %s; %s) >>& %s &", p);

		General.showOutput("cmdRunStarting: [" + cmdRunStarting + "]");
		General.showOutput("cmdRunKiller:   [" + cmdRunKiller + "]");
		General.showOutput("cmdRun:         [" + cmdRun + "]");

		String[] cmdList = new String[] { cmdRunStarting, cmdRunKiller, cmdRun };
		int delayBetweenSubmittingJobs = 500; // ms
		int status = OSExec.exec(cmdList, delayBetweenSubmittingJobs);
		if (status != 0) {
			writeJsonError(response, result, "Failed to submit all jobs.");
			return;
		}
		jsonResultPut(result, Settings.RESPONSE_RESULT, Settings.RESPONSE_STARTED);
		writeJson(response, result);
	}

	/**
	 * Actually saves the file
	 * 
	 * @param item
	 * @return a JSON string.
	 */
	private void processFile(HttpServletResponse response, JSONObject result, File pathProject, FileItem item) {

		if (item == null) {
			writeJsonError(response, "No actual file item retrieved");
			return;
		}

		// String fieldName = item.getFieldName();
		// String contentType = item.getContentType();
		// boolean isInMemory = item.isInMemory();

		General.showDebug("Checking size...");
		if (item.getSize() > Settings.FILE_UPLOAD_MAX_SIZE) {
			General.showError("Size not acceptable.");
			writeJsonError(response, result, "Failed to retrieve " + Settings.ERROR_SIZE_UNACCEPTABLE);
			return;
		}

		/** Name without path part */
		String fileName = item.getName();
		/**
		 * TODO: read up on safety issues here. No .. or forward slash allowed.
		 */
		if (fileName.indexOf(":") >= 0 || fileName.indexOf("..") >= 0 || fileName.charAt(0) == '/') {
			writeJsonError(response, result, "Filename not considered safe: [" + fileName + "]");
			return;
		}

		File uploadedFile = new File(pathProject, fileName);
		if (uploadedFile.exists()) {
			if (pathProject.delete()) {
				writeJsonError(response, result, "Failed to remove file with the same name: [" + uploadedFile + "]");
				return;
			}
		}
		try {
			item.write(uploadedFile);
		} catch (Exception e) {
			e.printStackTrace();
			writeJsonError(response, result, Settings.ERROR_WRITE_FAILED);
			return;
		}
		InOut.chmod(uploadedFile, "a+rw");

		long length = uploadedFile.length();
		long lengthFormElement = item.getSize();
		// Difference?
		General.showDebug("Fileform     length: " + lengthFormElement);
		General.showDebug("File written length: " + length);
		String sizeStr = Ut.bytesToFormattedString(length);
		jsonResultPut(result, Settings.RESPONSE_RESULT, sizeStr);
		writeJson(response, result);
	}

	private void processStatus(HttpServletResponse response, JSONObject result, File pathProject ) {

		File doneFile = new File(pathProject, Settings.DONE_FILE);
		String status = Settings.RESPONSE_STATUS_NOT_DONE;
		if (doneFile.exists()) {
			status = Settings.RESPONSE_STATUS_DONE;
		}
		jsonResultPut(result, Settings.RESPONSE_RESULT, status);
		writeJson(response, result);
		return;
	}

	/**
	 * 
	 * @param response
	 * @param result
	 *            Message will be byte by byte and end up in a PRE block
	 * @param pathProject
	 * @param item
	 * @param currentUserId
	 * @param currentAccessKey
	 */
	private void processLog(HttpServletResponse response, JSONObject result, File pathProject) {

		General.showDebug("Retrieving cing log tail.");
		File lastLogSendFile = new File(pathProject, Settings.LAST_LOG_SEND_FILE);

		String lastLog = Settings.RESPONSE_LOG_VALUE_NONE;

		File cingRunLogFile = new File(pathProject, Settings.CING_RUN_LOG_FILE);
		if (!cingRunLogFile.exists()) {
			jsonResultPut(result, Settings.RESPONSE_RESULT, lastLog);
			writeJson(response, result);
		}
		long cingrunLogFileSize = cingRunLogFile.length();
		General.showDebug("cingrunLogFileSize: " + cingrunLogFileSize);
		long cingrunLogFileSizeLast = 0;
		if (lastLogSendFile.exists()) {
			General.showDebug("Checking lastLogSendFile: " + lastLogSendFile);
			StringArrayList sal = new StringArrayList();
			boolean statusRead = sal.read(lastLogSendFile.toString());
			lastLogSendFile.delete();
			if (!statusRead) {
				writeJsonError(response, result, "Failed to read the lastLogSendFile: " + lastLogSendFile);
				return;
			}
			if (sal.size() < 1) {
				writeJsonError(response, result, "Failed to read at least one line from the present lastLogSendFile: "
						+ lastLogSendFile);
				return;
			}
			String cingrunLogFileSizeLastStr = sal.getString(0);
			General.showDebug("cingrunLogFileSizeLast (string): " + cingrunLogFileSizeLastStr);
			cingrunLogFileSizeLast = Long.parseLong(cingrunLogFileSizeLastStr);

			General.showDebug("cingrunLogFileSizeLast (long): " + cingrunLogFileSizeLast);
		} else {
			General.showDebug("no LAST_LOG_SEND_FILE: " + Settings.LAST_LOG_SEND_FILE);
		}

		// # doesn't exist because it was just removed if it even existed to start with.
		StringArrayList sal = new StringArrayList();
		sal.add(Long.toString(cingrunLogFileSize));
		General.showDebug("writing to LAST_LOG_SEND_FILE: " + Settings.LAST_LOG_SEND_FILE);
		if (!sal.write(lastLogSendFile.toString())) {
			writeJsonError(response, result, "Failed to write to new lastLogSendFile: " + lastLogSendFile);
			return;
		}

		if (cingrunLogFileSize > cingrunLogFileSizeLast) {
			long newLogSize = cingrunLogFileSize - cingrunLogFileSizeLast;
			General.showDebug("New log size: " + newLogSize);
			try {
				RandomAccessFile raf = new RandomAccessFile(cingRunLogFile, "r");
				raf.seek(cingrunLogFileSizeLast);
				byte[] b = new byte[(int) newLogSize];
				raf.readFully(b);
				raf.close();
				lastLog = new String(b);
			} catch (FileNotFoundException e) {
				e.printStackTrace();
				writeJsonError(response, result, "Failed to find cingRunLogFile: " + cingRunLogFile);
				return;
			} catch (IOException e) {
				e.printStackTrace();
				writeJsonError(response, result, "Detected IOException see tomcat log");
				return;
			}
		} else {
			General.showDebug("No new log");
		}
		jsonResultPut(result, Settings.RESPONSE_EXIT_CODE, Settings.RESPONSE_EXIT_CODE_SUCCESS);
		jsonResultPut(result, Settings.RESPONSE_RESULT, lastLog);
		writeJson(response, result);

	}
}