package cing.client;

//import com.allen_sauer.gwt.voices.client.Sound;
//import com.allen_sauer.gwt.voices.client.SoundController;
//import com.allen_sauer.gwt.voices.client.handler.PlaybackCompleteEvent;
//import com.allen_sauer.gwt.voices.client.handler.SoundHandler;
//import com.allen_sauer.gwt.voices.client.handler.SoundLoadStateChangeEvent;
//import cing.server.General;

import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.DecoratorPanel;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.Hyperlink;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.FlexTable.FlexCellFormatter;

public class Welcome extends iCingView {

	DecoratorPanel decPanel = new DecoratorPanel();
	iCingConstants c = iCing.c;
	Button playButton = new Button();

	public Welcome() {
		super();
	}

	public void setIcing(iCing icing) {
		super.setIcing(icing);
		// final iCing icingShadow = icing;
		setState(iCing.WELCOME_STATE);

		final Label html_1 = new Label(c.Welcome_to() + " " + c.iCing());
		html_1.setStylePrimaryName("h1");
		verticalPanel.add(html_1);
		verticalPanel.add(decPanel);
		FlexTable layout = new FlexTable();
		verticalPanel.add(layout);
		layout.setCellSpacing(5);
		layout.setCellPadding(5);

		FlexCellFormatter cellFormatter = layout.getFlexCellFormatter();

		cellFormatter.setColSpan(0, 0, 2);
		cellFormatter.setHorizontalAlignment(0, 0, HasHorizontalAlignment.ALIGN_CENTER);

		final Hyperlink hyperlink = new Hyperlink(c.Start(), iCing.FILE_STATE);
		layout.setWidget(2, 0, hyperlink);
		hyperlink.setTitle("Begin with file upload.");
		final Hyperlink hyperlink_1 = new Hyperlink(c.Logout(), iCing.LOGIN_STATE);
		layout.setWidget(3, 0, hyperlink_1);
		hyperlink_1.setTitle("Start new session.");
	}

}
