package cing.Scripts;

import java.io.File;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Random;

import org.apache.commons.httpclient.HttpClient;
import org.apache.commons.httpclient.HttpStatus;
import org.apache.commons.httpclient.methods.PostMethod;
import org.apache.commons.httpclient.methods.multipart.FilePart;
import org.apache.commons.httpclient.methods.multipart.MultipartRequestEntity;
import org.apache.commons.httpclient.methods.multipart.Part;
import org.apache.commons.httpclient.methods.multipart.StringPart;
import org.json.JSONException;
import org.json.JSONObject;

import cing.Constants;
import cing.client.Settings;

public class iCingRobot {
//	public static String default_url = Settings.DEFAULT_URL;
	// currently JFD doesn't know how to get Java working with the https secure protocols.
	public static String default_url = "http://nmr.cmbi.ru.nl"; // disable when debugged.

	public static String rpcUrl = default_url + "/" + Settings.DEFAULT_URL_PATH + "/" + Settings.SERVLET_URL;
	public static final String SEP_DIR = "/";
	private static final int IDX_ACTION = 0;
	private static final int IDX_USER_ID = 1;
	private static final int IDX_ACCESS_KEY = 2;

	static {
		System.out.println("rpcUrl: " + rpcUrl);
	}

	public static String getNewAccessKey() {
		String allowedCharacters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
		String result = "";
		Random random = new Random();
		for (int i = 1; i <= Settings.accessKeyLength; i++) {
			int idxChar = random.nextInt(allowedCharacters.length());
			result += allowedCharacters.charAt(idxChar);
		}
		return result;
	}

	public static String join(String sep, String[] sal) {
		StringBuffer sb = new StringBuffer();
		for (int i = 0; i < sal.length; i++) {
			sb.append(sep);
			sb.append(sal[i]);
		}
		String result = sb.toString();
		if (sal.length == 0) {
			result = result.substring(1);
		}
		return result;
	}

	public static String[] getResultUrls(String[][] fields, String entryId, String url) {
		String userId = fields[IDX_USER_ID][1];
		String accessKey = fields[IDX_ACCESS_KEY][1];
		String resultBaseUrl = join(SEP_DIR, new String[] { url, "tmp/cing", userId, accessKey }).substring(1);
		String resultHtmlUrl = join(SEP_DIR, new String[] { resultBaseUrl, entryId + ".cing", "index.html" })
				.substring(1);
		String resultLogUrl = join(SEP_DIR, new String[] { resultBaseUrl, "cingRun.log" }).substring(1);
		String resultZipUrl = join(SEP_DIR, new String[] { resultBaseUrl, entryId + "_CING_report.zip" }).substring(1);

		return new String[] { resultBaseUrl, resultHtmlUrl, resultLogUrl, resultZipUrl };
	}

	/**
	 * Function to send form fields and files to a given URL. Returns null on
	 * error.
	 * */
	public static HashMap sendRequest(String url, String[][] fields, File[] files) {
		String jsonTxt = null;
		try {
			PostMethod post = new PostMethod(url);
			post.setRequestHeader("User-Agent", "anonymous");
			ArrayList al = new ArrayList();
			for (int k = 0; k < fields.length; k++) {
				al.add(new StringPart(fields[k][0], fields[k][1]));
			}
			if (files != null) {
				for (int i = 0; i < files.length; i++) {
					File f = files[i];
					al.add(new FilePart(f.getName(), f));
				}
			}
			Part[] parts = new Part[al.size()];
			for (int j = 0; j < parts.length; j++) {
				parts[j] = (Part) al.get(j);
				// System.out.println("DEBUG: Part is " + parts[j].toString());
			}
			System.out.println("\n\nDoing action:   [" + fields[IDX_ACTION][1] + "]");
			post.setRequestEntity(new MultipartRequestEntity(parts, post.getParams()));
			HttpClient client = new HttpClient();
			int status = client.executeMethod(post);
			jsonTxt = post.getResponseBodyAsString();
			// System.out.println("DEBUG: status:   [" + status + "]");
			if (status != HttpStatus.SC_OK) {
				System.err.println("Upload failed: " + post.getStatusLine());
				return null;
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
		HashMap result = processResponse(jsonTxt);

		String msgFailed = null;
		if (!result.containsKey(Settings.RESPONSE_EXIT_CODE)) {
			msgFailed = "Request not successful. Exit code was even not retrieved";
		}
		String responseExitcode = (String) result.get(Settings.RESPONSE_EXIT_CODE);
		if (!responseExitcode.equals(Settings.RESPONSE_EXIT_CODE_SUCCESS)) {
			msgFailed = "Request not successful. Exit code was: " + responseExitcode;
		}
		if (msgFailed != null) {
			msgFailed += " Response was: " + jsonTxt;
			msgFailed += "\nResult was:\n" + result.toString();
			System.err.println("ERROR: " + msgFailed);
			return null;
		}
		return result;
	}

	/**
	 * Convert the strings the iCingServer sends back into more general Java data structure.
	 */
	private static HashMap processResponse(String text) {
		HashMap dataDict = new HashMap();
		try {
			JSONObject jsonObject = new JSONObject(text);
	        for (Iterator i = jsonObject.keys(); i.hasNext();) {
	            String key = (String) i.next();
	            String value = jsonObject.getString(key);
	            dataDict.put(key, value);
	        }
		} catch (JSONException e) {
			e.printStackTrace();
		}
		return dataDict;
	}

	/**
	 * Return true on success.
	 *
	 * Expect errors without a server up and running.
	 */
	public boolean run() {
		System.out.println("Firing up the Java iCing robot; aka example interface to CING for workflows");

		// Queries possible; do one at a time going down the list.
		// After the run is started the status will let you know if the run is
		// finished
		// The log will show what the server is doing at any one time.
		boolean doSave = true; // Upload to iCing and show derived urls
		boolean doRun = false; // Start the run in Nijmegen. Use the other items first please.
		boolean doStatus = true; // Find out if the run finished
		boolean doLog = true; // Get the next piece of log file (may be empty)
		boolean doPname = true; // Get the project name back. This is the entryId below.
		boolean doPurge = true; // Remove data from server again.

		// User id should be a short id (<without any special chars.)
		// user_id = os.getenv("USER", "UnknownUser")
		String user_id = "iCingRobotJ";
//		 String access_key = getNewAccessKey(); // Use a different one in a production environment.
		String access_key = "123456";

		String entryId = "1brv"; // 68K, smallest for quick testing.
		String inputFile = join(SEP_DIR, new String[] { Constants.cingDirTestsData, "ccpn", entryId + ".tgz" })
				.substring(1);
		// System.out.println("DEBUG: inputFile: " + inputFile);
		String[][] fields = new String[][] { { Settings.FORM_PARM_ACTION, null },
				{ Settings.FORM_PARM_USER_ID, user_id }, { Settings.FORM_PARM_ACCESS_KEY, access_key }, };
		if (doSave) {
			fields[IDX_ACTION][1] = Settings.FORM_ACTION_SAVE;
			File file = new File(inputFile);
			File[] files = new File[] { file };
			// System.out.println("DEBUG: fields: " + Strings.toString(fields));
			HashMap result = sendRequest(rpcUrl, fields, files);
			if (result == null) {
				System.err.println("Failed to save file to server");
				return false;
			} else {
				System.out.println("result of save request: " + result.toString());
				String[] urls = getResultUrls(fields, entryId, default_url);
				System.out.println("Base URL	: " + urls[0]);
				System.out.println("Results URL	: " + urls[1]);
				System.out.println("Log URL		: " + urls[2]);
				System.out.println("Zip URL		: " + urls[3]);
			}
		}
		if (doRun) {
			fields[0][1] = Settings.FORM_ACTION_RUN;
			System.out.println(sendRequest(rpcUrl, fields, null));
		}
		if (doStatus) {
			fields[0][1] = Settings.FORM_ACTION_STATUS;
			System.out.println(sendRequest(rpcUrl, fields, null));
		}
		if (doLog) {
			fields[0][1] = Settings.FORM_ACTION_LOG;
			System.out.println(sendRequest(rpcUrl, fields, null));
		}
		if (doPname) {
			fields[0][1] = Settings.FORM_ACTION_PROJECT_NAME;
			System.out.println(sendRequest(rpcUrl, fields, null));
		}
		if (doPurge) {
			fields[0][1] = Settings.FORM_ACTION_PURGE; // First pair!
			System.out.println(sendRequest(rpcUrl, fields, null));
		}
		return true;
	}

	/**
	 * Expect the result: (doing just a save) rpcUrl:
	 * https://nmr.cmbi.ru.nl/icing/serv/iCingServlet Firing up the iCing robot;
	 * aka example interface to CING result of save request: {'Action': 'Save',
	 * 'Result': '67.44 kb', 'ExitCode': 'Success'} Base URL
	 * https://nmr.cmbi.ru.nl/tmp/cing/iCingRobot/sV3nfD Results URL:
	 * https://nmr.cmbi.ru.nl/tmp/cing/iCingRobot/sV3nfD/1brv.cing/index.html
	 * Log URL: https://nmr.cmbi.ru.nl/tmp/cing/iCingRobot/sV3nfD/cingRun.log
	 * Zip URL:
	 * https://nmr.cmbi.ru.nl/tmp/cing/iCingRobot/sV3nfD/1brv_CING_report.zip
	 *
	 * @param args
	 */
	public static void main(String[] args) {
		iCingRobot iRobot = new iCingRobot();
		iRobot.run();
	}
}