package cing.client;

import com.google.gwt.user.client.ui.Composite;

public class Status extends Composite {
    final static RichTextAreaIcing statusArea = iCing.statusArea;

	public Status() {
		initWidget(statusArea);

		statusArea.setHTML("Status bar with last line from log; see View->Log iCing");
		statusArea.setHeight("10em");
		statusArea.setWidth(iCing.widthMenu);
	}
}
