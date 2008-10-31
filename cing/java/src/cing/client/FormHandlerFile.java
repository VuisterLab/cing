package cing.client;

import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.FileUpload;
import com.google.gwt.user.client.ui.FormSubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormSubmitEvent;
import com.google.gwt.user.client.ui.Label;
import com.gwtsolutions.components.client.ui.Message;

public class FormHandlerFile extends FormHandleriCing {

	private Button nextButton = null;
	private FileUpload fileUpload = null;
	private Message statusMessage = null;
	private Button submitButton = null;
	private Label labelFileUploadDone = null;

	public FormHandlerFile(iCing icing) {
		super(icing);
	}

	// When the submit starts, make sure the user selected a file to upload
	public void onSubmit(FormSubmitEvent event) {
		super.onSubmit(event);

		/** Extra checks here for this class */
		if (fileUpload.getFilename().length() == 0) {
			Window.alert("You must select a file!");
			event.setCancelled(true);
			return;
		}
		submitButton.setVisible(false);
		fileUpload.setVisible(false);

		String fn = fileUpload.getFilename();
		String fnNoPath = Utils.getFileNameWithoutPath(fn);

		labelFileUploadDone.setText("Uploading " + fnNoPath);
		labelFileUploadDone.setVisible(true);
	}

	public void onSubmitComplete(FormSubmitCompleteEvent event) {
		super.onSubmitComplete(event);

		statusMessage.removeStyleName("successBorder");
		statusMessage.removeStyleName("failureBorder");
		statusMessage.setVisible(true);
		if (exitCode.equals(Keys.RESPONSE_EXIT_CODE_SUCCESS)) {
			showUploadMessage(result);
		} else {
			showUploadError(result);
		}
	}

	private void showUploadError(String result) {
		statusMessage.addStyleName("failureBorder");
		// Swap between these two widgets.
		labelFileUploadDone.setVisible(false);
		fileUpload.setVisible(true);
		statusMessage.setText(result);
	}

	private void showUploadMessage(String result) {
		statusMessage.addStyleName("successBorder");
		String fn = fileUpload.getFilename();
		String type = Utils.getHTMLformTypeFromFileName(fn);
		String fnNoPath = Utils.getFileNameWithoutPath(fn);
		String labelTxt = fnNoPath + " (" + type + ") " + result;
		statusMessage.setText(labelTxt + " uploaded.");
		labelFileUploadDone.setText(labelTxt);
		nextButton.setEnabled(true);
		RunView.runButton.setEnabled(true);
	}

	public void setFileUpload(FileUpload fileUpload) {
		this.fileUpload = fileUpload;
	}

	public void setStatusMessage(Message statusMessage) {
		this.statusMessage = statusMessage;
	}

	public void setSubmitButton(Button submitButton) {
		this.submitButton = submitButton;
	}

	public void setLabelFileUploadDone(Label labelFileUploadDone) {
		this.labelFileUploadDone = labelFileUploadDone;
	}

	public void setNextButton(Button nextButton) {
		this.nextButton = nextButton;
	}
}
