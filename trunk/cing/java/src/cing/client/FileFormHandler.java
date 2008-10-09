package cing.client;

import java.util.Set;

import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONString;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.FileUpload;
import com.google.gwt.user.client.ui.FormHandler;
import com.google.gwt.user.client.ui.FormSubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormSubmitEvent;
import com.gwtsolutions.components.client.ui.Message;

public class FileFormHandler implements FormHandler {

	private FileUpload fileUpload = null;
	private Message statusMessage = null;

	// When the submit starts, make sure the user selected a file to upload
	public void onSubmit(FormSubmitEvent event) {
		if (getFileUpload().getFilename().length() == 0) {
			Window.alert("You must select a file!");
			event.setCancelled(true);
		}
	}

	// After the submit, get the JSON result and parse it.
	public void onSubmitComplete(FormSubmitCompleteEvent event) {
		String jsonResult = removePreTags(event.getResults());
		// JSONObject, JSONValue, and JSONString are all part of the GWT's JSON
		// parsing package
		JSONValue jsv = JSONParser.parse(jsonResult);
		JSONObject jso = jsv.isObject();

		if (jso != null) {
			Set<String> keySet = jso.keySet();
			Object[] keys = keySet.toArray();

			if (keys.length == 1) { // expect only one object
				String status = (String) keys[0];
				JSONValue v = jso.get(status);
				JSONString message = v.isString();

				if (message != null) {
					General.showOutput("message: [" + message.stringValue()+"]");
					getStatusMessage().removeStyleName("successBorder");
					getStatusMessage().removeStyleName("failureBorder");
					getStatusMessage().setText(message.stringValue());
					// Add a border style in accordance with
					// whether the file upload failed or succeeded
					// on the server. That status is included
					// in the JSON response.
					if ("error".equals(status)) {
						statusMessage.addStyleName("failureBorder");
					} else {
						statusMessage.addStyleName("successBorder");
					}
					statusMessage.setVisible(true);

				}
			}
		}
	}

	// This method strips the <pre> tag out of the response.
	// That <pre> tag in the response because of a GWT 1.3.3 bug.
	// GWT 1.5.1 gives: response is: [<pre
	// style="word-wrap: break-word; white-space: pre-wrap;">{message:
	// 'File upload succeeded'}</pre>]
	private String removePreTags(String response) {
		General.showDebug("response is: [" + response + "]");
		if (response.startsWith("<pre")) {
			int idxClosingAngularBracket = response.indexOf('>');
			// return response.substring("<pre>".length(), response
			return response.substring(idxClosingAngularBracket + 1, response.length() - "</pre>".length());
		} else {
			return response;
		}
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
}
