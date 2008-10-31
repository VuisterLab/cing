package cing.server;

import java.io.File;
import java.io.IOException;
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

import Wattos.Utils.InOut;
import Wattos.Utils.Strings;
import cing.client.Keys;

public class iCingServlet extends HttpServlet {
	private static final long serialVersionUID = 6098745782027999297L;

	/** 5 Mb ought to do */
	public static final long FILE_UPLOAD_MAX_SIZE = 5 * 1024 * 1024;
	public static final String SERVER_TMP_DIR = "/Library/WebServer/Documents/tmp/cing";

	private static final String ERROR_SIZE_UNACCEPTABLE = "File larger than: " + FILE_UPLOAD_MAX_SIZE + " bytes";
	private static final String ERROR_PARSE_REQUEST = "Failed to parse request";
	private static final String ERROR_WRITE_FAILED = "File write failed.";
	private static final String ERROR_NOT_MULTI_PART = "Not multipart message.";

	public void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException,
			java.io.IOException {
		writeJsonError(response, "Denying iCingServlet.doGet. Try a POST.");
	}

	/**
	 * Return a json string to file form handler with only one element: {"error","reason"} or {"message","999 kb"}
	 * */
	public void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException,
			java.io.IOException {
		General.showDebug("processing doPost");
		JSONObject result = new JSONObject();

		File pathUser = null;
		File pathProject = null;
		FileItem actualFileItem = null;
		String currentAccessKey = null;
		String currentUserId = Keys.FORM_PARM_USER_ID_DEFAULT;
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
			writeJsonError(response, ERROR_NOT_MULTI_PART);
			return;
		}

		try {
			items = upload.parseRequest(request);
		} catch (FileUploadException e) {
			e.printStackTrace();
			writeJsonError(response, ERROR_PARSE_REQUEST);
			return;
		}

		if (items == null) {
			writeJsonError(response, "Got a serious error while: upload.parseRequest(request).");
			return;
		}

		if (items.size() < Keys.FORM_PARM_MINIMUM.length) {
			String msg = "Got " + items.size() + " items which is less than the expected:"
					+ Keys.FORM_PARM_MINIMUM.length + " items.";
			writeJsonError(response, msg);
			return;
		}

		for (int i = 0; i < items.size(); i++) {
			FileItem item = items.get(i);
			String name = item.getFieldName();
			String value = item.getString();
			General.showDebug("processing form item: [" + name + "] with value: [" + value + "]");
			if (item.isFormField()) {
				if (name.equals(Keys.FORM_PARM_ACCESS_KEY)) {
					currentAccessKey = value;
					General.showDebug("retrieved currentAccessKey: " + currentAccessKey);
					continue;
				}
				if (name.equals(Keys.FORM_PARM_USER_ID)) {
					currentUserId = value;
					General.showDebug("retrieved currentUserId: " + currentUserId);
					continue;
				}
				if (name.equals(Keys.FORM_PARM_ACTION)) {
					currentAction = value;
					jsonResultPut(result, Keys.FORM_PARM_ACTION, currentAction);
					General.showDebug("retrieved action: " + currentAction);
					continue;
				}
				// When the routine falls thru to here the parameter was not recognized.
				if (value == null) {
					value = Keys.None;
				}
				int endIndex = Math.min(100, value.length());
				value = value.substring(0, endIndex);
				String msg = "Parameter [" + name + "] with value (first 100 bytes): [" + value + "] was unexpected.";
				writeJsonError(response, result, msg);
				return;
			} else {
				actualFileItem = item;
			}
		}

		if (currentAction == null) {
			writeJsonError(response, result, "Failed to retrieve Action.");
			return;
		}
		if (currentAccessKey == null) {
			writeJsonError(response, result, "Failed to retrieve " + Keys.FORM_PARM_ACCESS_KEY);
			return;
		}
		if (currentUserId == null) {
			writeJsonError(response, result, "Failed to retrieve  " + Keys.FORM_PARM_USER_ID);
			return;
		}

		if (!Keys.FORM_ACTION_ALIST.contains(currentAction)) {
			writeJsonError(response, result, "Requested action unknown:  " + currentAction);
			return;
		}

		pathUser = new File(SERVER_TMP_DIR, currentUserId);
		if (!pathUser.exists()) {
			if (!pathUser.mkdir()) {
				writeJsonError(response, result, "Failed to mkdir for user at: [" + pathUser + "]");
				return;
			}
			Ut.chmod(pathUser, "a+rw");
		}
		pathProject = new File(pathUser, currentAccessKey);
		if (!pathProject.exists()) {
			if (!pathProject.mkdir()) {
				writeJsonError(response, result, "Failed to mkdir for project at: [" + pathProject + "]");
				return;
			}
			Ut.chmod(pathProject, "a+rw");
		}

		if (currentAction.equals(Keys.FORM_ACTION_SAVE)) {
			processFile(response, result, pathProject, actualFileItem, currentUserId, currentAccessKey);
		} else if (currentAction.equals(Keys.FORM_ACTION_PROJECT_NAME)) {
			processPname(response, result, pathProject, actualFileItem, currentUserId, currentAccessKey);
		} else if (currentAction.equals(Keys.FORM_ACTION_LOG)) {
			;
		} else if (currentAction.equals(Keys.FORM_ACTION_STATUS)) {
			;
		} else if (currentAction.equals(Keys.FORM_ACTION_RUN)) {
			;
		} else {
			// Would be a code bug as is checked before.
			writeJsonError(response, result, "Requested action unknown:  " + currentAction + " [CODE ERROR]");
			return;
		}
	}

	private void processPname(HttpServletResponse response, JSONObject result, File pathProject,
			FileItem actualFileItem, String currentUserId, String currentAccessKey) {

		String regexp = ".*.tgz";
		General.showOutput("Reg exp files: " + regexp);
		General.showOutput("Dir: " + pathProject);
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
		jsonResultPut(result, Keys.RESPONSE_EXIT_CODE, Keys.RESPONSE_EXIT_CODE_SUCCESS);
		jsonResultPut(result, Keys.RESPONSE_RESULT, projectName);
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

	private void writeJson(HttpServletResponse response, JSONObject result) {
		General.showDebug("Result is [" + result.toString() + "]");
		response.setContentType("text/plain");
		try {
			response.getWriter().write(result.toString());
		} catch (IOException e) {
			e.printStackTrace();
			return;
		}
	}

	private void writeJsonError(HttpServletResponse response, JSONObject result, String msg) {
		jsonResultPut(result, Keys.RESPONSE_EXIT_CODE, Keys.RESPONSE_EXIT_CODE_ERROR);
		jsonResultPut(result, Keys.RESPONSE_RESULT, msg);
		writeJson(response, result);
	}

	private void writeJsonError(HttpServletResponse response, String msg) {
		JSONObject result = new JSONObject();
		writeJsonError(response, result, msg);
	}

	/**
	 * Actually saves the file
	 * 
	 * @param item
	 * @return a JSON string.
	 */
	private void processFile(HttpServletResponse response, JSONObject result, File pathProject, FileItem item,
			String currentUserId, String currentAccessKey) {

		if (item == null) {
			writeJsonError(response, "No actual file item retrieved");
			return;
		}

		// String fieldName = item.getFieldName();
		// String contentType = item.getContentType();
		// boolean isInMemory = item.isInMemory();

		General.showDebug("Checking size...");
		if (item.getSize() > FILE_UPLOAD_MAX_SIZE) {
			General.showError("Size not acceptable.");
			writeJsonError(response, result, "Failed to retrieve " + ERROR_SIZE_UNACCEPTABLE);
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
			writeJsonError(response, result, ERROR_WRITE_FAILED);
			return;
		}
		Ut.chmod(uploadedFile, "a+rw");

		long length = uploadedFile.length();
		long lengthFormElement = item.getSize();
		// Difference?
		General.showDebug("Fileform     length: " + lengthFormElement);
		General.showDebug("File written length: " + length);
		String sizeStr = Ut.bytesToFormattedString(length);
		jsonResultPut(result, Keys.RESPONSE_EXIT_CODE, Keys.RESPONSE_EXIT_CODE_SUCCESS);
		jsonResultPut(result, Keys.RESPONSE_RESULT, sizeStr);
		writeJson(response, result);
	}
}