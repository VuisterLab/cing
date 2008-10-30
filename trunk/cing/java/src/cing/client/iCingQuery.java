package cing.client;

import com.google.gwt.core.client.GWT;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.VerticalPanel;

public class iCingQuery {

	final FormPanel formPanel = new FormPanel();
	final VerticalPanel formLayoutPanel = new VerticalPanel();
	final Hidden action = new Hidden(Keys.FORM_PARM_ACTION);
	ServerFormHandler serverFormHandler = new ServerFormHandler();
	
	public iCingQuery() {
		formPanel.setEncoding(FormPanel.ENCODING_MULTIPART);
		formPanel.setMethod(FormPanel.METHOD_POST);
		String moduleBaseUrlWithPort = GWT.getModuleBaseURL();
		String actionServerUrl = moduleBaseUrlWithPort + "/" + Keys.SERVLET_URL;
		General.showDebug("actionServerUrl: [" + actionServerUrl + "]");
		formPanel.setAction(actionServerUrl);
		VerticalPanel formLayoutPanel = new VerticalPanel();
		formPanel.setWidget(formLayoutPanel);

		formLayoutPanel.add(new Hidden(Keys.FORM_PARM_ACCESS_KEY, iCing.currentAccessKey));
		formLayoutPanel.add(new Hidden(Keys.FORM_PARM_USER_ID, iCing.currentUserId));
		formLayoutPanel.add(action);
		
		formPanel.addFormHandler(serverFormHandler);
	}	
}
