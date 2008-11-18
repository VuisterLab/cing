package cing.client;

import java.util.Set;

import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONString;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.user.client.ui.FormHandler;
import com.google.gwt.user.client.ui.FormSubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormSubmitEvent;

public class FormHandlerMain implements FormHandler {

	public iCing icing;
	public String action;
	public String exitCode;
	public String result;
	public JSONObject jso;

	public FormHandlerMain(iCing icing) {
		super();
        if (icing == null) {
            General.showCodeBug("In FormHandlerMain constructor. Found null for icing.");
        }
		setiCing(icing);
	}

	// When the submit starts, make sure the user selected a file to upload
	public void onSubmit(FormSubmitEvent event) {
//		General.showDebug("Starting submit which will be dealt with from FormHandlerMain and sub class.");
		if (icing == null) {
			General.showCodeBug("In FormHandlerMain.onSubmit Found null for icing.");
			event.setCancelled(true);
			return;
		}
	}

	// After the submit, get the JSON result and parse it.
	public void onSubmitComplete(FormSubmitCompleteEvent event) {
		General.showDebug("Now in FormHandlerMain.onSubmitComplete");

		String response = event.getResults();
		if (response == null) {
			General.showError("Failed to get any response from server.");
			return;
		}
		int endIndex = Math.min(response.length(), Settings.MAX_RESPONSE_REPORTED_FOR_DEBUGGING);
		String responseTruncate = response.substring(0,endIndex).replace(General.eol, "");
		General.showDebug("responseTruncate is: [" + responseTruncate + "]");
		String jsonResult = removePreTags(response);
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
		jso = jsv.isObject();

		Set<String> keySet = jso.keySet();
		Object[] keys = keySet.toArray();

		action = null; // Needs to become set.
		exitCode = null; // Needs to become set.
		result = null; // not?
		for (int i = 0; i < keys.length; i++) {
			String key = (String) keys[i];
			JSONValue v = jso.get(key);
			JSONString valueObj = v.isString();
			if (valueObj == null) {
				General.showDebug("Skipping key [" + key + "] with non-String value [" + v.toString() + "]");
				continue;
			}
			String value = valueObj.stringValue();
			endIndex = Math.min(value.length(), Settings.MAX_RESPONSE_REPORTED_FOR_DEBUGGING);
			String valueTruncate = value.substring(0,endIndex);
			General.showDebug("Received key, valueTruncate: [" + key + "], [" + valueTruncate + "]");
			if (key.equals(Settings.FORM_PARM_ACTION)) {
				action = value;
			} else if (key.equals(Settings.RESPONSE_EXIT_CODE)) {
				exitCode = value;
			} else if (key.equals(Settings.RESPONSE_RESULT)) {
				result = value;
			}
		}
		if (action == null) {
			action = Settings.RESPONSE_ACTION_DEFAULT;
			General.showDebug("Missing action; set to default: [" + action + "]");
			return;
		}

		if (exitCode == null) {
			exitCode = Settings.RESPONSE_EXIT_CODE_DEFAULT;
			General.showDebug("Missing exitCode; set to default: [" + exitCode + "]");
		}
		/** Just note here and act on it in subclass. */
		if (!Settings.RESPONSE_EXIT_CODE_ALIST.contains(exitCode)) {
			General.showError("Found invalid exit code: [" + exitCode + "] set to default ["
					+ Settings.RESPONSE_EXIT_CODE_DEFAULT + "]");
			exitCode = Settings.RESPONSE_EXIT_CODE_DEFAULT;
		}
		if (result == null) {
			result = Settings.RESPONSE_RESULT_DEFAULT;
			General.showDebug("Missing result; set to default: [" + result + "]");
			return;
		}
		General.showDebug("Exiting FormHandlerMain.onSubmitComplete");
	}

	public void setiCing(iCing icing) {
		if (icing == null) {
			General.showError("in FormHandlerMain.setiCing found icing: null");
		} else {
//			General.showDebug("in FormHandlerMain.setiCing found icing: " + icing.toString());
		}
		this.icing = icing;
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
}
