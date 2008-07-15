package cing.client;

//import java.util.ArrayList;

import java.util.Set;

import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.core.client.GWT;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONString;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.FileUpload;
import com.google.gwt.user.client.ui.FormHandler;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.FormSubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormSubmitEvent;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.RootPanel;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;
//import com.gwtsolutions.components.client.ui.Message;

public class iCing implements EntryPoint {
	// The Message widget is a GWT Solutions widget. See
	// the GWTSolutions Components module for details.
//	private final Message statusMessage = new Message(null, Message.SHAKE, 0.5);

	public void onModuleLoad() {
		// Create a GWT FileUpload widget and set its name.
		// The GWT will send the name in the request when the
		// surrounding form is submitted
		final FileUpload fileUpload = new FileUpload();
		fileUpload.setName("uploadFormElement");

		// Create a GWT FormPanel, which submits an HTML form.
		// Set the encoding, mehtod, and action associated with
		// file uploads, and set the form panel's widget to the
		// file upload widget created above.
		final FormPanel formPanel = new FormPanel();
		formPanel.setEncoding(FormPanel.ENCODING_MULTIPART);
		formPanel.setMethod(FormPanel.METHOD_POST);
		formPanel.setAction(GWT.getModuleBaseURL() + "/fileupload");
		formPanel.setWidget(fileUpload);

		// Now create the user interface, wrapped in a
		// vertical panel
		VerticalPanel verticalPanel = new VerticalPanel();
		Label label = new Label("Upload");
		Button button = new Button("Submit");

//		verticalPanel.add(statusMessage);
		verticalPanel.add(label);
		verticalPanel.add(formPanel);
		verticalPanel.add(button);

		// Since there is no status initially, hide the
		// status message
//		statusMessage.setVisible(false);

		// Add the vertical panel, which contains all the
		// other widgets, to the root panel
		RootPanel.get().add(verticalPanel);

		// When the user clicks on the button, we submit
		// the surrounding form
		button.addClickListener(new ClickListener() {
			public void onClick(Widget sender) {
				formPanel.submit();
			}
		});

		// The GWT calls this form handler after the form
		// is submitted in the button click listener implemented
		// above.
		formPanel.addFormHandler(new FormHandler() {
			// When the submit starts, make sure the user
			// selected a file to upload
			public void onSubmit(FormSubmitEvent event) {
				if (fileUpload.getFilename().length() == 0) {
					Window.alert("You must select a file!");
					event.setCancelled(true);
				}
			}

			// After the submit, get the JSON result and parse it.
			// NOTE: The removePreTags method is a workaround for
			// a bug in GWT 1.3.3 that wraps the response in
			// a PRE tage, like this: <pre>JSON response</pre>
			public void onSubmitComplete(FormSubmitCompleteEvent event) {
				// For a successful file upload, the JSON response
				// looks like this:
				//
				// <pre>{message: 'File upload succeeded'}</pre>
				//
				// For a failed file upload, the response looks
				// like t
				//
				// <pre>{error: [error message]}</pre>
				//
				// The <pre> tag is a bug in GWT 1.3.3
				String jsonResult = removePreTags(event.getResults());

				// JSONObject, JSONValue, and JSONString are all
				// part of the GWT's JSON parsing package
				JSONObject jso = null;
				JSONValue jsv = null;
				jsv = JSONParser.parse(jsonResult);
				jso = jsv.isObject();

				if (jso != null) {
					Set keySet = jso.keySet();
					Object[] keys = keySet.toArray();

					if (keys.length == 1) { // expect only one object
						String status = (String) keys[0];
						JSONValue v = jso.get(status);
						JSONString message = v.isString();

						if (message != null) {
//							statusMessage.removeStyleName("successBorder");
//							statusMessage.removeStyleName("failureBorder");
//							statusMessage.setText(message.stringValue());
//
//							// Add a border style in accordance with
//							// whether the file upload failed or succeeded
//							// on the server. That status is included
//							// in the JSON response.
//							if ("error".equals(status))
//								statusMessage.addStyleName("failureBorder");
//							else
//								statusMessage.addStyleName("successBorder");
//
//							statusMessage.setVisible(true);
						}
					}
				}
			}

			// This method strips the <pre> tag out of the response.
			// That <pre> tag in the response because of a
			// GWT 1.3.3 bug.
			private String removePreTags(String response) {
				if (response.startsWith("<pre>")) {
					return response.substring("<pre>".length(), response
							.length()
							- "</pre>".length());
				} else {
					return response;
				}
			}
		});
	}
}