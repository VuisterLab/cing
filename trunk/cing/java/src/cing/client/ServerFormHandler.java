package cing.client;

import java.util.Set;

import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONString;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.user.client.ui.FormHandler;
import com.google.gwt.user.client.ui.FormSubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormSubmitEvent;
import com.gwtsolutions.components.client.ui.Message;

public class ServerFormHandler implements FormHandler {

	private Message statusMessage = null;

	// When the submit starts, make sure the user selected a file to upload
	public void onSubmit(FormSubmitEvent event) {
		General.showDebug("Starting submit");
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
		String jsonResult = FileFormHandler.removePreTags(response);
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

		if (keys.length != 1) {
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
		statusMessage.setText(msg);
		statusMessage.setVisible(true);
	}

	private void showUploadError(String msg) {
		showUploadResult(msg);
		statusMessage.addStyleName("failureBorder");
	}

	private void showUploadMessage(String msg) {
		showUploadResult(msg);
		statusMessage.addStyleName("successBorder");
	}
}
