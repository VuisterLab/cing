package cing.client;

import com.google.gwt.user.client.ui.FormSubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormSubmitEvent;

public class FormHandlerSpecific extends FormHandlerMain {

    public FormHandlerSpecific(iCing icing) {
        super(icing);
    }
	
	// When the submit starts, make sure the user selected a file to upload
	public void onSubmit(FormSubmitEvent event) {
		super.onSubmit(event);
	}

	// After the submit, get the JSON result and parse it.
	public void onSubmitComplete(FormSubmitCompleteEvent event) {
//        GenClient.showDebug("Initially in FormHandlerSpecific.onSubmitComplete");
		super.onSubmitComplete(event);
//		GenClient.showDebug("Now in FormHandlerSpecific.onSubmitComplete");

		if (exitCode.equals(Settings.RESPONSE_EXIT_CODE_ERROR)) {
			GenClient.showError("Form with action: ["+action+"] came back with an error. Not processing further.");
			return;
		}

		if (action.equals(Settings.FORM_ACTION_STATUS)) {
			icing.cingLogView.setStatus(result);
		} else if (action.equals(Settings.FORM_ACTION_LOG)) {
			icing.cingLogView.setLogTail(result);
        } else if (action.equals(Settings.FORM_ACTION_PROJECT_NAME)) {
            icing.cingLogView.setProjectName(result);
        } else if (action.equals(Settings.FORM_ACTION_PURGE)) {
            icing.cingLogView.setPurgeProject(result);
        } else if (action.equals(Settings.FORM_ACTION_CRITERIA)) { 
            icing.runView.setCriteriaOnServer();
        } else if (action.equals(Settings.FORM_ACTION_RUN)) {
            icing.runView.setRunOnServer();
		} else {
			// shouldn't happen because checked before.
			GenClient.showCodeBug("Weird, found invalid response key: [" + exitCode + "]");
		}
	}
}
