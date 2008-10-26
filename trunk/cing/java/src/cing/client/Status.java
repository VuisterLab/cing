package cing.client;

import com.google.gwt.user.client.ui.RichTextArea;

public class Status extends iCingView {

	RichTextArea statusArea = null;

	public Status() {
		statusArea = iCing.statusArea;
		initWidget(statusArea);

		statusArea.setHTML("Status bar with last line from log; see View->Log iCing");
		statusArea.setHeight("10em");
		statusArea.setWidth(iCing.widthMenu);
		statusArea.setWidth(iCing.widthMenu);
		statusArea.setVisible(General.getVerbosity() == General.verbosityDebug);
	}
}
