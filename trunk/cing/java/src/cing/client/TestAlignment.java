package cing.client;

import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FileUpload;
import com.google.gwt.user.client.ui.HasVerticalAlignment;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.ListBox;

public class TestAlignment extends Composite {

	public TestAlignment() {

		final HorizontalPanel horizontalPanel = new HorizontalPanel();
		initWidget(horizontalPanel);

		final CheckBox checkBox = new CheckBox();
		horizontalPanel.add(checkBox);
		checkBox.setText("New CheckBox");

		final HorizontalPanel horizontalPanel_1 = new HorizontalPanel();
		horizontalPanel.add(horizontalPanel_1);

		final FileUpload fileUpload = new FileUpload();
		horizontalPanel_1.add(fileUpload);
		horizontalPanel_1.setCellVerticalAlignment(fileUpload, HasVerticalAlignment.ALIGN_BOTTOM);

		final ListBox listBox = new ListBox();
		horizontalPanel.add(listBox);

		final ListBox listBox_1 = new ListBox();
		horizontalPanel.add(listBox_1);
		listBox_1.setVisibleItemCount(5);
	}

}
