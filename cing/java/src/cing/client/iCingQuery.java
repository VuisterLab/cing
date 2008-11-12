package cing.client;

import com.google.gwt.core.client.GWT;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.VerticalPanel;

public class iCingQuery {

	final FormPanel formPanel = new FormPanel();
	/**
	 * Since not more than one element can be added to formpanel; the individual items need to be wrapped in another
	 * element that can contain them.
	 */
	final VerticalPanel formVerticalPanel = new VerticalPanel();
	final Hidden action = new Hidden(Keys.FORM_PARM_ACTION);
	public FormHandleriCing serverFormHandler = null;

	public iCingQuery(iCing icing) {
		if (icing == null) {
			General.showError("in iCingQuery() found icing: null");
		} else {
//			General.showDebug("in iCingQuery() found icing: " + icing.toString());
		}
		
		serverFormHandler = new FormHandleriCing(icing);
		formPanel.setEncoding(FormPanel.ENCODING_MULTIPART);
		formPanel.setMethod(FormPanel.METHOD_POST);
		String moduleBaseUrlWithPort = GWT.getModuleBaseURL();
		String actionServerUrl = moduleBaseUrlWithPort + Keys.SERVLET_URL;
		formPanel.setAction(actionServerUrl);		
		General.showDebug("actionServerUrl: [" + actionServerUrl + "]");		

		formVerticalPanel.add(action);
		formVerticalPanel.add(new Hidden(Keys.FORM_PARM_ACCESS_KEY, iCing.currentAccessKey));
		formVerticalPanel.add(new Hidden(Keys.FORM_PARM_USER_ID, iCing.currentUserId));
		
		formPanel.setWidget(formVerticalPanel);
		formPanel.addFormHandler(serverFormHandler);
	}

	/**
	 * Assume just one exists. The formHandler should already have the icing setting set.
	 * 
	 * @param serverFormHandler
	 */
	public void setFormHandler(FormHandleriCing formHandler) {
		General.showDebug("Now in setFormHandler.");
		formPanel.removeFormHandler(this.serverFormHandler);
		formPanel.addFormHandler(formHandler);
		this.serverFormHandler = formHandler;
		if (formHandler.icing == null) {
			General.showError("Got a null for formHandler.icing in iCingQuery.setFormHandler");
		}
	}
}
