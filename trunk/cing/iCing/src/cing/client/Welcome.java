package cing.client;

import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DecoratorPanel;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.Hyperlink;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.FlexTable.FlexCellFormatter;

public class Welcome extends Composite {

	public Welcome() {
		// Wrap the content in a DecoratorPanel
		DecoratorPanel decPanel = new DecoratorPanel();
		initWidget(decPanel);
		// Create a table to layout the form options
		FlexTable layout = new FlexTable();
		decPanel.setWidget(layout);
		layout.setCellSpacing(6);
		FlexCellFormatter cellFormatter = layout.getFlexCellFormatter();

		// Add a title to the form
//		layout.setHTML(0, 0, "Welcome");
		cellFormatter.setColSpan(0, 0, 2);
		cellFormatter.setHorizontalAlignment(0, 0,
				HasHorizontalAlignment.ALIGN_CENTER);
		// Add some standard form options
		final Label welcomeMsg = new Label("Welcome to iCing");
		welcomeMsg.addStyleName("welcomeMsg");
		layout.setWidget(1, 0, welcomeMsg);
		cellFormatter.setColSpan(1, 0, 2);
		layout.setWidget(2, 0, new Hyperlink("Start now.", iCing.FILE_STATE));
		layout.setWidget(3, 0,
				new Hyperlink("Logout again.", iCing.LOGIN_STATE));
	}
}
