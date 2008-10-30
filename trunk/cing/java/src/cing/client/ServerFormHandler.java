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
		validResponseKeys.add(Keys.FORM_ACTION_READINESS);
		validResponseKeys.add(Keys.FORM_ACTION_LOG);
		validResponseKeys.add(Keys.FORM_ACTION_PROJECT_NAME);
		
		validResponseStatusValues.add( Keys.RESPONSE_STATUS_DONE );
		validResponseStatusValues.add( Keys.RESPONSE_STATUS_NOT_DONE );
		validResponseStatusValues.add( Keys.RESPONSE_EXIT_CODE_ERROR );
	}
		
	// When the submit starts, make sure the user selected a file to upload
	public void onSubmit(FormSubmitEvent event) {
		General.showDebug("Starting submit which will be dealt with exclusively from ServerFormHandler");
	}

	// After the submit, get the JSON result and parse it.
	public void onSubmitComplete(FormSubmitCompleteEvent event) {
		
		if ( cingLogView == null ) {
			General.showCodeBug("Found null for cingLogView.");
			return;
		}
		
		String response = event.getResults();
		if (response == null) {
			General.showError("Failed to get any response from server.");
			return;
		}
		General.showDebug("response is: [" + response + "]");
		String jsonResult = FileFormHandler.removePreTags(response);
		// JSONObject, JSONValue, and JSONString are all part of the GWT's JSON
		// parsing package
		JSONValue jsv;
		try {
			jsv = JSONParser.parse(jsonResult);
		} catch (Exception e) {
			e.printStackTrace();
			String msg = "Failed to parse json result from server for json: [" + jsonResult + "]";
			General.showError(msg);
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
		if ( key.equals(Keys.RESPONSE_EXIT_CODE_ERROR)) {
			General.showDebug("will do next; cingLogView.setStatus(value)");			
			cingLogView.setStatus(value);
			return;
		}

		if ( key.equals(Keys.FORM_ACTION_READINESS)) {
			if ( ! validResponseStatusValues.contains(value) ) {
				General.showError("Found invalid response value: [" + value + "]");
				return;
			}
			General.showDebug("will do next; cingLogView.setStatus(value)");			
			cingLogView.setStatus(value);
			return;
		}
		if ( key.equals(Keys.FORM_ACTION_LOG)) {
			General.showDebug("will do next; cingLogView.setLogTail(value);");
			cingLogView.setLogTail(value);
			return;
		}
		if ( key.equals(Keys.FORM_ACTION_PROJECT_NAME)) {
			General.showDebug("will do next; cingLogView.setProjectName(value);");
			if ((value == null) || value.equals(Keys.RESPONSE_STATUS_NONE)) {
				General.showError("Found invalid response value: [" + value + "]");
				return;
			}
			cingLogView.setProjectName(value);
			return;
		}
		// shouldn't happen.
		General.showCodeBug("Weird, found invalid response key: [" + key + "]");
		return;
	}

	public void setCingLogView(CingLogView cingLogView) {
		this.cingLogView = cingLogView;
	}
}
