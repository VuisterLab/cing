package cing.client;

import com.google.gwt.user.client.ui.FormSubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormSubmitEvent;

public class FormHandlerServer extends FormHandleriCing {

    public FormHandlerServer(iCing icing) {
        super(icing);
    }
	
	// When the submit starts, make sure the user selected a file to upload
	public void onSubmit(FormSubmitEvent event) {
		super.onSubmit(event);
	}

	// After the submit, get the JSON result and parse it.
	public void onSubmitComplete(FormSubmitCompleteEvent event) {
		super.onSubmitComplete(event);

		if (exitCode.equals(Keys.RESPONSE_EXIT_CODE_ERROR)) {
			General.showError("Form with action: ["+action+"] came back with an error. Not processing further.");
			return;
		}

		if (action.equals(Keys.FORM_ACTION_STATUS)) {
			icing.cingLogView.setStatus(result);
		} else if (action.equals(Keys.FORM_ACTION_LOG)) {
			icing.cingLogView.setLogTail(result);
		} else if (action.equals(Keys.FORM_ACTION_PROJECT_NAME)) {
			icing.cingLogView.setProjectName(result);
		} else {
			// shouldn't happen because checked before.
			General.showCodeBug("Weird, found invalid response key: [" + exitCode + "]");
		}
	}
}
