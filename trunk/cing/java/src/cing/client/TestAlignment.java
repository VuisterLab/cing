package cing.client;

import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.RichTextArea;
import com.google.gwt.user.client.ui.ScrollPanel;

public class TestAlignment extends Composite {

	public TestAlignment() {

		final ScrollPanel scrollPanel = new ScrollPanel();
		initWidget(scrollPanel);

		final RichTextArea richTextArea = new RichTextArea();
		scrollPanel.setWidget(richTextArea);
		richTextArea.setSize("100%", "100%");
	}

}
