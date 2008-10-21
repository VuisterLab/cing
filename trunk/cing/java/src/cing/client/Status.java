package cing.client;

import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.RichTextArea;

public class Status extends Composite {
    final static RichTextArea statusArea = iCing.statusArea;

	public Status() {
		initWidget(statusArea);

		statusArea.setHTML("Status bar with last line from log; see View->Log iCing");
		statusArea.setHeight("10em");
		statusArea.setWidth(iCing.widthMenu);
	}
}
