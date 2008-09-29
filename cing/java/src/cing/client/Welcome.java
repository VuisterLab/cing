package cing.client;

import com.allen_sauer.gwt.voices.client.Sound;
import com.allen_sauer.gwt.voices.client.SoundController;
import com.allen_sauer.gwt.voices.client.handler.PlaybackCompleteEvent;
import com.allen_sauer.gwt.voices.client.handler.SoundHandler;
import com.allen_sauer.gwt.voices.client.handler.SoundLoadStateChangeEvent;
import com.google.gwt.user.client.Command;
import com.google.gwt.user.client.DeferredCommand;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DecoratorPanel;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.Hyperlink;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.user.client.ui.FlexTable.FlexCellFormatter;

public class Welcome extends Composite {

	DecoratorPanel decPanel = new DecoratorPanel();
	FlexTable layout = new FlexTable();
	iCingConstants c = iCing.c;

	public Welcome() {
		// Wrap the content in a DecoratorPanel
		initWidget(decPanel);

		// Create a table to layout the form options
		decPanel.setWidget(layout);
		layout.setCellSpacing(6);
		FlexCellFormatter cellFormatter = layout.getFlexCellFormatter();

		// Add a title to the form
		// layout.setHTML(0, 0, "Welcome");
		cellFormatter.setColSpan(0, 0, 2);
		cellFormatter.setHorizontalAlignment(0, 0, HasHorizontalAlignment.ALIGN_CENTER);
		// Add some standard form options
		final Label welcomeMsg = new Label(c.Welcome_to() + " " + c.iCing());
		welcomeMsg.setStyleName("h1");
//		welcomeMsg.addStyleName("BigText");
		welcomeMsg.addStyleName("LoudText");
		
		layout.setWidget(1, 0, welcomeMsg);
		cellFormatter.setColSpan(1, 0, 2);
		layout.setWidget(2, 0, new Hyperlink(c.Start(), iCing.FILE_STATE));
		layout.setWidget(3, 0, new Hyperlink(c.Logout(), iCing.LOGIN_STATE));

		// use deferred command to catch initialization exceptions
		DeferredCommand.addCommand(new Command() {
			public void execute() {
				onModuleLoad2();
			}
		});
	}

	public void onModuleLoad2() {
		SoundController soundController = new SoundController();
		final Sound sound = soundController.createSound(Sound.MIME_TYPE_AUDIO_MPEG, "sound/ngmater.mp3");

		// add a sound handler so we know when the sound has loaded
		// create a place holder for the load state
		final HTML loadStateHTML = new HTML();
		// loadStateHTML.setHTML( iCing.soundLoadState );
		sound.addEventHandler(new SoundHandler() {
			public void onPlaybackComplete(PlaybackCompleteEvent event) {
			}

			public void onSoundLoadStateChange(SoundLoadStateChangeEvent event) {
				loadStateHTML.setHTML(c.Load_state() + ": " + event.getLoadStateAsString());
			}
		});
		Button playButton = new Button(c.Silly_sound());

		// create a (disabled) play button
		// playButton = new Button("Silly sound");
		// when we click, play the sound
		playButton.addClickListener(new ClickListener() {
			public void onClick(Widget sender) {
				if (iCing.soundOn) {
					sound.play();
				} else {
					Window.alert(c.Sound_is_turn());
				}
			}
		});

		// add the button
		// RootPanel.get().add(playButton);
		layout.setWidget(4, 0, playButton);

		// add the load state status
		// RootPanel.get().add(loadStateHTML);
		layout.setWidget(5, 0, loadStateHTML);
		loadStateHTML.setVisible(false);

	}
}
