package cing.client;

import java.util.ArrayList;
import java.util.Set;

import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONString;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.user.client.ui.FormHandler;
import com.google.gwt.user.client.ui.FormSubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormSubmitEvent;

public class ServerFormHandler implements FormHandler {

	static final ArrayList<String> validResponseKeys = new ArrayList();
	static final ArrayList<String> validResponseStatusValues = new ArrayList();
	private CingLogView cingLogView = null;

	static {		
		validResponseKeys.add(iCing.RESPONSE_STATUS);
		validResponseKeys.add(iCing.RESPONSE_TAIL_PROGRESS);
		
		validResponseStatusValues.add( iCing.RESPONSE_STATUS_DONE );
		validResponseStatusValues.add( iCing.RESPONSE_STATUS_NOT_DONE );
	}
		
	// When the submit starts, make sure the user selected a file to upload
	public void onSubmit(FormSubmitEvent event) {
		General.showDebug("Starting submit which will be dealt with exclusively from ServerFormHandler");
	}

	// After the submit, get the JSON result and parse it.
	public void onSubmitComplete(FormSubmitCompleteEvent event) {
		
		String response = event.getResults();
		if (response == null) {
			General.showError("Failed to get any response from server.");
			return;
		}
		General.showDebug("response is: [" + response + "]");
		String jsonResult = FileFormHandler.removePreTags(response);
		// String status = iCing.JSON_ERROR_STATUS; // reset below.
		// JSONObject, JSONValue, and JSONString are all part of the GWT's JSON
		// parsing package
		JSONValue jsv;
		try {
			jsv = JSONParser.parse(jsonResult);
		} catch (Exception e) {
			e.printStackTrace();
			General.showError("Failed to parse json result from server for json: [" + jsonResult + "]");
			return;
		}
		JSONObject jso = jsv.isObject();

		Set<String> keySet = jso.keySet();
		Object[] keys = keySet.toArray();

		if (keys.length != 1) {
			General.showError("Expected only one object from json result from server for json: [" + jsonResult + "]");
			return;
		}
		
		String key = (String) keys[0];
		JSONValue v = jso.get(key);
		JSONString message = v.isString();
		if (message == null) { // never happens?
			General.showError("Failed to get JSONString from object status for json: [" + jsonResult + "]");
			return;
		}		
		String value = message.stringValue();
		
		General.showDebug("Received key, value: [" + key + "], [" + value + "]");
//		General.showError("Not a real error.");
//		General.showCodeBug("Not a real error either.");
		if ( ! validResponseKeys.contains(key) ) {
			General.showError("Found invalid response key: [" + key + "]");
			return;
		}
		if ( key.equals(iCing.RESPONSE_STATUS)) {
			if ( ! validResponseStatusValues.contains(value) ) {
				General.showError("Found invalid response value: [" + value + "]");
				return;
			}
			General.showDebug("will do next; cingLogView.setStatus(value)");
			cingLogView.setStatus(value);
			return;
		}
		if ( key.equals(iCing.RESPONSE_TAIL_PROGRESS)) {
			General.showDebug("will do next; cingLogView.setLogTail(value);");
//			if ( cingLogView == null ) {
//				General.showError("Got null for cingLogView");
//				return;
//			}
			cingLogView.setLogTail(value);
			return;
		}
		if ( key.equals(iCing.RESPONSE_STATUS_PROJECT_NAME)) {
			General.showDebug("will do next; cingLogView.setProjectName(value);");
			if ((value == null) || value.equals(iCing.RESPONSE_STATUS_NONE)) {
				General.showError("Found invalid response value: [" + value + "]");
				return;
			}
			cingLogView.setProjectName(value);
			return;
		}
		// shouldn't happen.
		General.showCodeBug("Found invalid response key: [" + key + "]");
		return;
	}

	public void setCingLogView(CingLogView cingLogView) {
		this.cingLogView = cingLogView;
	}
}
