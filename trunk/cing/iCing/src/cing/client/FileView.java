package cing.client;

import java.util.Set;

import com.google.gwt.core.client.GWT;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONString;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FileUpload;
import com.google.gwt.user.client.ui.FormHandler;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.FormSubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormSubmitEvent;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

public class FileView extends Composite {

	private FileUpload fileUpload = new FileUpload();
	private FormPanel formPanel = new FormPanel();

	public FileView() {
		
		// Now create the user interface, wrapped in a
		// vertical panel
		VerticalPanel verticalPanel = new VerticalPanel();
		initWidget(verticalPanel);
		fileUpload.setName("uploadFormElement");
		// fileUpload.addChangeListener(this);
		formPanel.setEncoding(FormPanel.ENCODING_MULTIPART);
		formPanel.setMethod(FormPanel.METHOD_POST);
		formPanel.setAction(GWT.getModuleBaseURL() + "/fileupload");
		formPanel.setWidget(fileUpload);

		Label label = new Label("Upload");
		Button button = new Button("Submit");

		// verticalPanel.add(statusMessage);
		verticalPanel.add(label);
		verticalPanel.add(formPanel);
		verticalPanel.add(button);

		// Since there is no status initially, hide the
		// status message
		// statusMessage.setVisible(false);

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
				String jsonResult = removePreTags(event.getResults()); // using
				System.err.println("DEBUG: response is: [" + jsonResult + "]");

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
							// statusMessage.removeStyleName("successBorder");
							// statusMessage.removeStyleName("failureBorder");
							// statusMessage.setText(message.stringValue());
							//
							// // Add a border style in accordance with
							// // whether the file upload failed or succeeded
							// // on the server. That status is included
							// // in the JSON response.
							// if ("error".equals(status))
							// statusMessage.addStyleName("failureBorder");
							// else
							// statusMessage.addStyleName("successBorder");
							//
							// statusMessage.setVisible(true);
						}
					}
				}
			}

			// // This method strips the <pre> tag out of the response.
			// // That <pre> tag in the response because of a
			// // GWT 1.3.3 bug.
			// GWT 1.5.1 gives: response is: [<pre
			// style="word-wrap: break-word; white-space: pre-wrap;">{message:
			// 'File upload succeeded'}</pre>]
			private String removePreTags(String response) {
				System.err.println("DEBUG: response is: [" + response + "]");
				if (response.startsWith("<pre")) {
					int idxClosingAngularBracket = response.indexOf('>');
					// return response.substring("<pre>".length(), response
					return response.substring(idxClosingAngularBracket + 1,
							response.length() - "</pre>".length());
				} else {
					return response;
				}
			}
		});

	}

}
