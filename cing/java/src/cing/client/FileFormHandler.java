package cing.client;

import java.util.Set;

import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONString;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.FileUpload;
import com.google.gwt.user.client.ui.FormHandler;
import com.google.gwt.user.client.ui.FormSubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormSubmitEvent;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.gwtsolutions.components.client.ui.Message;

public class FileFormHandler implements FormHandler {

	private Button nextButton = null;
	private FileUpload fileUpload = null;
	private Message statusMessage = null;
	private Button submitButton = null;
	private CheckBox checkBoxUseFile = null;
	private Label labelFileUploadDone = null;
	private ListBox listBox_Program = null;
	private ListBox listBox_Type = null;
	private ListBox listBox_Subtype = null;
	private ListBox listBox_Other = null;
	private Timer timer = null;

	// When the submit starts, make sure the user selected a file to upload
	public void onSubmit(FormSubmitEvent event) {
//		General.showDebug("are we submitting? Version 0.0.2");
		if (getFileUpload().getFilename().length() == 0) {
			Window.alert("You must select a file!");
			event.setCancelled(true);
			return;
		}
		getTimer().cancel();		
		getSubmitButton().setVisible(false);
//		getCheckBoxUseFile().setVisible(true);
		getFileUpload().setVisible(false);

		String fn = getFileUpload().getFilename();
		String fnNoPath = getFileNameWithoutPath(fn);
		
		getLabelFileUploadDone().setText("Uploading " + fnNoPath );
		getLabelFileUploadDone().setVisible(true);
//		getListBox_Program().setEnabled(false);
//		getListBox_Type().setEnabled(false);
//		getListBox_Subtype().setEnabled(false);
//		getListBox_Other().setEnabled(false);
	}

	// After the submit, get the JSON result and parse it.
	public void onSubmitComplete(FormSubmitCompleteEvent event) {
		// there is a serious bug in this setup as response is always null.
		// It might be due to http://en.wikipedia.org/wiki/Same_origin_policy so going to a different port is
		// already a violation. Here's the fix for when the submit was a :
//		http://code.google.com/docreader/#p=google-web-toolkit-doc-1-5&s=google-web-toolkit-doc-1-5&t=GettingStartedJSON
			
		String response = event.getResults();
		General.showDebug("response is: [" + response + "]");
		if (response == null) {
			showUploadError("Failed to get any response from server.");
			return;
		}

		String jsonResult = removePreTags(response);
		// String status = iCing.JSON_ERROR_STATUS; // reset below.
		// JSONObject, JSONValue, and JSONString are all part of the GWT's JSON
		// parsing package
		JSONValue jsv;
		try {
			jsv = JSONParser.parse(jsonResult);
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			showUploadError("Failed to parse json result from server for json: [" + jsonResult + "]");
			return;
		}
		JSONObject jso = jsv.isObject();

		Set<String> keySet = jso.keySet();
		Object[] keys = keySet.toArray();

		if (keys.length != 1) { // 
			showUploadError("Expected only one object from json result from server for json: [" + jsonResult + "]");
			return;
		}
		String status = (String) keys[0];
		JSONValue v = jso.get(status);
		JSONString message = v.isString();
		if (message == null) { // never happens?
			showUploadError("Failed to get JSONString from object status for json: [" + jsonResult + "]");
			return;
		}
		String messageStr = message.stringValue();
		General.showOutput("message: [" + messageStr + "]");
		if ( status.equals(iCing.JSON_ERROR_STATUS)) {
			showUploadError(messageStr);
			return;
		}		
		showUploadMessage(messageStr);		
	}

	private void showUploadResult(String msg) {
		statusMessage.removeStyleName("successBorder");
		statusMessage.removeStyleName("failureBorder");
		statusMessage.setVisible(true);
	}

	private void showUploadError(String msg) {
		showUploadResult(msg);

		statusMessage.addStyleName("failureBorder");

		// Swap between these two widgets.
		getLabelFileUploadDone().setVisible(false);
		getFileUpload().setVisible(true);
		statusMessage.setText(msg);
//		getFileUpload().clear....

		/** Allow a retry at same row. */
//		getTimer().scheduleRepeating(FileView.REFRESH_INTERVAL); Can't do another time.
//		getSubmitButton().setVisible(true);
//		getCheckBoxUseFile().setVisible(true);
//		getListBox_Program().setEnabled(true);
//		getListBox_Type().setEnabled(true);
//		getListBox_Subtype().setEnabled(true);
//		getListBox_Other().setEnabled(true);

	}

	private void showUploadMessage(String msg) {
		showUploadResult(msg);

		statusMessage.addStyleName("successBorder");
		// Report to status and label.
		String fn = getFileUpload().getFilename();
		String type = getHTMLformTypeFromFileName(fn);
		String fnNoPath = getFileNameWithoutPath(fn);
		String labelTxt = fnNoPath + " (" + type + ") " + msg;
		statusMessage.setText(labelTxt + " uploaded.");
		getLabelFileUploadDone().setText(labelTxt);
		
		nextButton.setEnabled(true);
	}

	private String getFileNameWithoutPath(String fn) {
		int idxSlash = fn.lastIndexOf('/');
		if (fn.charAt(fn.length() - 1) == '/') {
			return "/"; // error of course but prevents an exception to be
			// thrown.
		}
		return fn.substring(idxSlash + 1);
	}

	/** Implement for real; this is just a guess */
	private String getHTMLformTypeFromFileName(String fn) {
		if (fn.endsWith(".tgz")) {
			return "binary/tgz";
		}
		if (fn.endsWith(".tar")) {
			return "binary/tgz";
		}
		return "text/txt";
	}

	// This method strips the <pre> tag out of the response.
	// That <pre> tag in the response because of a GWT 1.3.3 bug.
	// GWT 1.5.1 gives: response is: [<pre
	// style="word-wrap: break-word; white-space: pre-wrap;">{message:
	// 'File upload succeeded'}</pre>]
	public static String removePreTags(String response) {
		if (response == null) {
			return null;
		}
		if (!response.startsWith("<pre")) {
			return response;
		}
		int idxClosingAngularBracket = response.indexOf('>');
		// return response.substring("<pre>".length(), response
		return response.substring(idxClosingAngularBracket + 1, response.length() - "</pre>".length());
	}

	public void setFileUpload(FileUpload fileUpload) {
		this.fileUpload = fileUpload;
	}

	public FileUpload getFileUpload() {
		return fileUpload;
	}

	public void setStatusMessage(Message statusMessage) {
		this.statusMessage = statusMessage;
	}

	public Message getStatusMessage() {
		return statusMessage;
	}

	public void setSubmitButton(Button submitButton) {
		this.submitButton = submitButton;
	}

	public Button getSubmitButton() {
		return submitButton;
	}

	public void setCheckBoxUseFile(CheckBox checkBoxUseFile) {
		this.checkBoxUseFile = checkBoxUseFile;
	}

	public CheckBox getCheckBoxUseFile() {
		return checkBoxUseFile;
	}

	public void setLabelFileUploadDone(Label labelFileUploadDone) {
		this.labelFileUploadDone = labelFileUploadDone;
	}

	public Label getLabelFileUploadDone() {
		return labelFileUploadDone;
	}

	public void setListBox_Program(ListBox listBox_Program) {
		this.listBox_Program = listBox_Program;
	}

	public ListBox getListBox_Program() {
		return listBox_Program;
	}

	public void setListBox_Subtype(ListBox listBox_Subtype) {
		this.listBox_Subtype = listBox_Subtype;
	}

	public ListBox getListBox_Subtype() {
		return listBox_Subtype;
	}

	public void setListBox_Type(ListBox listBox_Type) {
		this.listBox_Type = listBox_Type;
	}

	public ListBox getListBox_Type() {
		return listBox_Type;
	}

	public void setListBox_Other(ListBox listBox_Other) {
		this.listBox_Other = listBox_Other;
	}

	public ListBox getListBox_Other() {
		return listBox_Other;
	}

	public void setTimer(Timer timer) {
		this.timer = timer;
	}

	public Timer getTimer() {
		return timer;
	}

	public void setNextButton(Button nextButton) {
		this.nextButton = nextButton;
	}

	public Button getNextButton() {
		return nextButton;
	}
}
