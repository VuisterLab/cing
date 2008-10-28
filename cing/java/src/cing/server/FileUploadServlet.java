package cing.server;

import java.io.File;
import java.io.IOException;
import java.util.List;

import javax.servlet.ServletConfig;
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

public class FileUploadServlet extends HttpServlet {
	private static final long serialVersionUID = 6098745782027999297L;

	/** 5 Mb ought to do */
	private static final long MAX_SIZE = 5 * 1024 * 1024;

	public static final String FILE_UPLOAD_DIR = "/Library/WebServer/Documents/tmp/cing";

	public static final String FORM_ACTION = "Action";
	public static final String FORM_ACCESS_KEY = "AccessKey";
	public static final String FORM_USER_ID = "UserId";
	public static final String FORM_UPLOAD_FILE_BASE = "UploadFile";

	// Can't import iCing settings here; stupid!
	public static final int FORM_PART_COUNT = 4; // action, key, user, file.
	private static final String RESPONSE_STATUS_ERROR = "error";
	private static final String RESPONSE_STATUS_MESSAGE = "message";

	private static final String ERROR_SIZE_UNACCEPTABLE = "{" + RESPONSE_STATUS_ERROR
			+ ": 'File upload failed. File size must be " + MAX_SIZE + " bytes or less'}";
	private static final String ERROR_PARSE_REQUEST = "{" + RESPONSE_STATUS_ERROR + ": 'Failed to parse request'}";
	private static final String ERROR_WRITE_FAILED = "{" + RESPONSE_STATUS_ERROR
			+ ": 'File upload failed. File write failed.'}";
	private static final String ERROR_NOT_MULTI_PART = "{" + RESPONSE_STATUS_ERROR
			+ ": 'File upload failed. Not multipart message.'}";

	/**
	 * Initializes the servlet.
	 * 
	 * @param config
	 * @throws ServletException
	 */
	public void init(ServletConfig config) throws ServletException {
		super.init(config);
		init2();
	}

	public void init2() throws ServletException {
		/** Set the desired verbosity level */
		General.showDebug("Now in initDb");
		// General.showDebug("Wattos version: " + iCing.VERSION);
		// System.setOut( System.err );
		General.showDebug("this message to System.out after redirect");
	}

	public void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException,
			java.io.IOException {
		doPost(request, response);
	}

	/**
	 * Return a json string to file form handler with only one element:
	 * {"error","reason"} or {"message","999 kb"}
	 * */
	public void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException,
			java.io.IOException {
		System.out.println("DEBUG: processing doPost");
		FileItem actualFileItem = null;
		String currentAccessKey = null;
		String currentUserId = null;

		FileItemFactory factory = new DiskFileItemFactory();
		ServletFileUpload upload = new ServletFileUpload(factory);
		List<FileItem> items = null;
		String json = null;

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
				String pBytesReadStr = Utils.bytesToFormattedString(pBytesRead);
				String pContentLengthStr = Utils.bytesToFormattedString(pContentLength);

				if (pContentLength == -1) {
					System.out
							.println("DEBUG: So far, " + pBytesReadStr + " have been read from item[" + pItems + "].");
				} else {
					System.out.println("DEBUG: So far, " + pBytesReadStr + " of " + pContentLengthStr
							+ " have been read from item[" + pItems + "].");
				}
			}
		};

		upload.setProgressListener(progressListener);
		// Check that we have a file upload request
		boolean isMultipart = ServletFileUpload.isMultipartContent(request);
		if (!isMultipart) {
			json = ERROR_NOT_MULTI_PART;
			writeJson(response, json);
			return;
		}

		try {
			items = upload.parseRequest(request);
		} catch (FileUploadException e) {
			e.printStackTrace();
			System.err.println("ERROR: Failed to upload.parseRequest(request)");
			json = ERROR_PARSE_REQUEST;
			writeJson(response, json);
			return;
		}

		if (items == null) {
			json = "{" + RESPONSE_STATUS_ERROR + ": 'Got a serious error while: upload.parseRequest(request).'}";
			writeJson(response, json);
			return;
		}

		if (items.size() != FORM_PART_COUNT) {
			json = "{" + RESPONSE_STATUS_ERROR + ": 'Got " + items.size() + " file items instead of expected one.'}";
			writeJson(response, json);
			return;
		}

		for (int i = 0; i < items.size(); i++) {
			FileItem item = items.get(i);
			String name = item.getFieldName();
			String value = item.getString();
			// System.out.println("DEBUG: processing form item: [" + name +
			// "] with value: ["+value+"]");
			if (item.isFormField()) {
				if (name.equals(FORM_ACCESS_KEY)) {
					currentAccessKey = value;
					System.out.println("DEBUG: retrieved currentAccessKey: " + currentAccessKey);
					continue;
				}
				if (name.equals(FORM_USER_ID)) {
					currentUserId = value;
					System.out.println("DEBUG: retrieved currentUserId: " + currentUserId);
					continue;
				}
				if (name.equals(FORM_ACTION)) {
					System.out.println("DEBUG: retrieved action: " + name);
					continue;
				}
				if (value == null) {
					value = "empty";
				}
				int endIndex = Math.min(100, value.length());
				value = value.substring(0, endIndex);
				json = "{" + RESPONSE_STATUS_ERROR + ": 'File item parameter [" + name
						+ "] with value (first 100 bytes): [" + value + "] was unexpected.'}";
				writeJson(response, json);
				return;
			} else {
				actualFileItem = item;
			}
		}
		// Process actual file after other parameters are retrieved.
		if (actualFileItem == null) {
			json = "{" + RESPONSE_STATUS_ERROR + ": 'No actual file item retrieved'}";
			writeJson(response, json);
			return;
		}

		if (currentAccessKey == null) {
			json = "{" + RESPONSE_STATUS_ERROR + ": 'Failed to retrieve AccessKey.'}";
			writeJson(response, json);
			return;
		}
		if (currentUserId == null) {
			json = "{" + RESPONSE_STATUS_ERROR + ": 'Failed to retrieve UserId.'}";
			writeJson(response, json);
			return;
		}
		json = processFile(actualFileItem, currentUserId, currentAccessKey);
		writeJson(response, json);
	}

	private void writeJson(HttpServletResponse response, String json) {
		response.setContentType("text/plain"); // disable for debugging?
		System.out.println("DEBUG: json is [" + json + "]");
		try {
			response.getWriter().write(json);
		} catch (IOException e) {
			e.printStackTrace();
			return;
		}
	}

	/**
	 * Actually saves the file
	 * 
	 * @param item
	 * @return a JSON string.
	 */
	private String processFile(FileItem item, String currentUserId, String currentAccessKey) {
		// if (!isContentTypeAcceptable(item))
		// return CONTENT_TYPE_UNACCEPTABLE;
		System.out.println("DEBUG: checking size...");

		/**
		 * Set by fileUpload.setName("uploadFormElement"+Integer.toString(
		 * currentRowIdx));
		 */
		@SuppressWarnings("unused")
		String fieldName = item.getFieldName();
		@SuppressWarnings("unused")
		String contentType = item.getContentType();
		@SuppressWarnings("unused")
		boolean isInMemory = item.isInMemory();

		if (item.getSize() > MAX_SIZE) {
			System.err.println("Size not acceptable.");
			return ERROR_SIZE_UNACCEPTABLE;
		}

		String fileName = item.getName();
		/**
		 * TODO read up on safety issues here.
		 * 
		 * No .. or forward slash allowed.
		 */
		if (fileName.indexOf("..") >= 0 || fileName.charAt(0) == '/') {
			return "{" + RESPONSE_STATUS_ERROR + ": 'Filename not considered safe: [" + fileName + "].'}";
		}
		File pathUser = new File(FILE_UPLOAD_DIR, currentUserId);
		if (!pathUser.exists()) {
			if (!pathUser.mkdir()) {
				return "{" + RESPONSE_STATUS_ERROR + ": 'Failed to mkdir for user at: [" + pathUser + "].'}";
			}
			General.chmod( pathUser, "a+rw");
		}
		File pathProject = new File(pathUser, currentAccessKey);
		if (!pathProject.exists()) {
			if (!pathProject.mkdir()) {
				return "{" + RESPONSE_STATUS_ERROR + ": 'Failed to mkdir for project at: [" + pathProject + "].'}";
			}
			General.chmod( pathProject, "a+rw");
		}
		File uploadedFile = new File(pathProject, fileName);
		if (uploadedFile.exists()) {
			if (pathProject.delete()) {
				return "{" + RESPONSE_STATUS_ERROR + ": 'Failed to remove existing file with the same name: ["
						+ uploadedFile + "].'}";
			}
		}
		try {
			item.write(uploadedFile);
		} catch (Exception e) {
			e.printStackTrace();
			return ERROR_WRITE_FAILED;
		}
		General.chmod( uploadedFile, "a+rw");

		String sizeStr = Utils.bytesToFormattedString(item.getSize());
		return "{" + RESPONSE_STATUS_MESSAGE + ": '" + sizeStr + "'}";
	}

	/**
	 * Next 3 not really needed normally. Show an the actual error message to
	 * client and error log.
	 * 
	 * @param resp
	 * @param message
	 * @throws ServletException
	 * @throws IOException
	 *             public void showActualError(HttpServletResponse resp, String
	 *             message) throws ServletException, java.io.IOException {
	 *             resp.setContentType("text/html"); java.io.PrintWriter out =
	 *             resp.getWriter(); out.println("
	 *             <P>
	 *             ERROR: " + message); General.showError(message);
	 *             General.showError(" at: "); }
	 * 
	 *             /** Show a complete error message including header and
	 *             footer.
	 * 
	 * @param resp
	 * @param message
	 * @throws ServletException
	 * @throws IOException
	 *             public void showCompleteError(HttpServletResponse resp,
	 *             String message) throws ServletException, java.io.IOException
	 *             { resp.setContentType("text/html"); java.io.PrintWriter out =
	 *             resp.getWriter(); showHeader(resp);
	 *             out.println("<font color='red'>ERROR:</font> " + message);
	 *             out.println("<BR>
	 *             "); showFooter(resp); }
	 */

	/**
	 * Stick some html code at the top.
	 * 
	 * @param resp
	 * @throws ServletException
	 * @throws IOException
	 */
	public void showHeader(HttpServletResponse resp) throws ServletException, java.io.IOException {

		java.io.PrintWriter out = resp.getWriter();
		String html_header_text = "just debugging now<BR>";
		out.println(html_header_text);
	}

	/**
	 * Stick some html code at the end.
	 * 
	 * @param resp
	 * @throws ServletException
	 * @throws IOException
	 */
	public void showFooter(HttpServletResponse resp) throws ServletException, java.io.IOException {
		java.io.PrintWriter out = resp.getWriter();
		String html_footer_text = "and finished debugging.<BR>";
		out.println(html_footer_text);
	}

}