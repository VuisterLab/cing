package cing.server;

import java.io.File;
import java.io.IOException;
import java.util.Iterator;
import java.util.List;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.commons.fileupload.FileItem;
import org.apache.commons.fileupload.FileItemFactory;
import org.apache.commons.fileupload.FileUploadException;
import org.apache.commons.fileupload.ProgressListener;
import org.apache.commons.fileupload.disk.DiskFileItemFactory;
import org.apache.commons.fileupload.servlet.ServletFileUpload;

import cing.client.iCing;

public class FileUploadServlet extends HttpServlet {
	private static final long serialVersionUID = 6098745782027999297L;

	private static final String UPLOAD_DIRECTORY = "/Users/jd/tmp/iCing";
	/** 50 Mb ought to do */
	private static final long MAX_SIZE = 50 * 1024 * 1024;
	// private static final String ACCEPTABLE_CONTENT_TYPE =
	// "image/jpeg";
	// private static final String CONTENT_TYPE_UNACCEPTABLE =
	// "{error: 'File upload failed. "
	// + " Only text files can be uploaded'}";

	private static final String ERROR_SIZE_UNACCEPTABLE = "{error: 'File upload failed. File size must be " + MAX_SIZE
			+ " bytes or less'}";
	private static final String ERROR_PARSE_REQUEST = "{error: 'Failed to parse request'}";
//	private static final String ERROR_PROCESS_FILE = "{error: 'Failed to get a json object from processFile()'}";
	private static final String ERROR_WRITE_FAILED = "{error: 'File upload failed. File write failed.'}";

	private static final String OUTPUT_SUCCESS = "{message: 'File upload succeeded'}";

	private static final String ERROR_NOT_MULTI_PART = "{error: 'File upload failed. Not multipart message.'}";

	String currentAccessKey = null;
	String currentUserId = null;

	public void doPost(HttpServletRequest request, HttpServletResponse response) {
		System.out.println("DEBUG: processing doPost");
		currentAccessKey = null;
		currentUserId = null;

		FileItemFactory factory = new DiskFileItemFactory();
		ServletFileUpload upload = new ServletFileUpload(factory);
		List items = null;
		String json = null;

		//Create a progress listener on server side; pretty useless, so far but when pushed to client can be nice.
		ProgressListener progressListener = new ProgressListener(){
		   private long batchesRead = -1; // Currently read.
		   private long bytesPerBatch = 10 * 1024; // 10 k incremental report increase when done testing.
		   public void update(long pBytesRead, long pContentLength, int pItems) {
		       long batchCurrentRead = pBytesRead / bytesPerBatch; 
		       if (batchesRead == batchCurrentRead) {
		           return; // no report.
		       }
		       batchesRead = batchCurrentRead;
		       if (pContentLength == -1) {
		           System.out.println("DEBUG: So far, " + pBytesRead + " bytes have been read from item["+pItems+"].");
		       } else {
		           System.out.println("DEBUG: So far, " + pBytesRead + " of " + pContentLength
		                              + " bytes have been read from item["+pItems+"].");
		       }
		   }
		};	
		upload.setProgressListener(progressListener);
		// Check that we have a file upload request
		boolean isMultipart = ServletFileUpload.isMultipartContent(request);
		if ( ! isMultipart ) {
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

		if ( items == null ) {
			json = "{error: 'Got a serious error while: upload.parseRequest(request).'}";
			writeJson(response, json);
			return;
		}
		
		/** The iCing parameter below was not initialized at the servlet end.
		 * Or does it need to have a final modifier? 
		 * */
		if (items.size() != iCing.fileFormItemList.length) {
			json = "{error: 'Got " + items.size() + " file items instead of expected one.'}";
			writeJson(response, json);
			return;
		}

		Iterator it = items.iterator();
		/** Will be reset in loop. */
		json = "{error: 'File item not processed yet.'}";
		FileItem actualFileItem = null;
		while (it.hasNext()) {
			FileItem item = (FileItem) it.next();
			if (item.isFormField()) {
				String name = item.getFieldName();
				String value = item.getString();
				if (name.equals(iCing.FORM_ACCESS_KEY)) {
					currentAccessKey = value;
					continue;
				}
				if (name.equals(iCing.FORM_USER_ID)) {
					currentUserId = value;
					continue;
				}
				json = "{error: 'File item parameter [" + name + "] with value: [" + value + "] was unexpected.'}";
				writeJson(response, json);
				return;
			}
			actualFileItem = (FileItem) it.next();
		}
		// Process actual file after other parameters are retrieved.
		if (actualFileItem == null) {
			json = "{error: 'No actual file item retrieved'}";
			writeJson(response, json);
			return;
		}

		if (currentAccessKey == null || currentUserId == null) {
			json = "{error: 'Failed to retrieve one or more formFields.'}";
			writeJson(response, json);
			return;
		}
		json = processFile(actualFileItem);
		writeJson(response, json);
	}

	private void writeJson(HttpServletResponse response, String json) {
		response.setContentType("text/plain");
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
	private String processFile(FileItem item) {
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
		/** TODO read up on safety issues here. */
		if ( fileName.indexOf("..") >= 0 || fileName.charAt(0) == '/') {
			return "{error: 'Filename not considered safe: ["+fileName+"].'}";
		}
		File pathUser = new File(UPLOAD_DIRECTORY, currentUserId);
		if ( ! pathUser.exists() ) {
			if ( ! pathUser.mkdir()) {
				return "{error: 'Failed to mkdir for user at: ["+pathUser+"].'}";
			}
		}
		File pathProject = new File(pathUser, currentAccessKey);
		if ( ! pathProject.exists() ) {
			if ( ! pathProject.mkdir()) {
				return "{error: 'Failed to mkdir for project at: ["+pathProject+"].'}";
			}
		}
		File uploadedFile = new File(pathProject, fileName);
		if ( uploadedFile.exists() ) {
			if ( pathProject.delete()) {
				return "{error: 'Failed to remove existing file with the same name: ["+uploadedFile+"].'}";
			}
		}		
		try {
			item.write(uploadedFile);
		} catch (Exception e) {
			e.printStackTrace();
			return ERROR_WRITE_FAILED;
		}
		return OUTPUT_SUCCESS;
	}
}