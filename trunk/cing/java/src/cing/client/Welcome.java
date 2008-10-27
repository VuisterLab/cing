package cing.client;

//import com.allen_sauer.gwt.voices.client.Sound;
//import com.allen_sauer.gwt.voices.client.SoundController;
//import com.allen_sauer.gwt.voices.client.handler.PlaybackCompleteEvent;
//import com.allen_sauer.gwt.voices.client.handler.SoundHandler;
//import com.allen_sauer.gwt.voices.client.handler.SoundLoadStateChangeEvent;
import com.google.gwt.user.client.Command;
import com.google.gwt.user.client.DeferredCommand;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.DecoratorPanel;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.Hyperlink;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.user.client.ui.FlexTable.FlexCellFormatter;

public class Welcome extends iCingView {

	DecoratorPanel decPanel = new DecoratorPanel();
	iCingConstants c = iCing.c;
	Button playButton = new Button();

	public Welcome() {
		setState(iCing.WELCOME_STATE);
		final VerticalPanel verticalPanelTop = new VerticalPanel();
		initWidget(verticalPanelTop);

		final Label html_1 = new Label( c.Welcome_to() + " " + c.iCing());
		html_1.setStylePrimaryName("h1");
		verticalPanelTop.add(html_1);		
		verticalPanelTop.add(decPanel);		
		final VerticalPanel verticalPanel = new VerticalPanel();
		decPanel.add(verticalPanel);
		FlexTable layout = new FlexTable();
		verticalPanel.add(layout);
		layout.setCellSpacing(5);
		layout.setCellPadding(5);

		FlexCellFormatter cellFormatter = layout.getFlexCellFormatter();

		cellFormatter.setColSpan(0, 0, 2);
		cellFormatter.setHorizontalAlignment(0, 0, HasHorizontalAlignment.ALIGN_CENTER);
		playButton.setText( c.Silly_sound());
		layout.setWidget(4, 0, playButton);
		playButton.setTitle("Make some noise.");
		playButton.setVisible(false);
		// add the load state status
		// RootPanel.get().add(loadStateHTML);
//		layout.setWidget(5, 0, loadStateHTML);
//		loadStateHTML.setVisible(false);
		
		final Hyperlink hyperlink = new Hyperlink(c.Start(), iCing.FILE_STATE);
		layout.setWidget(2, 0, hyperlink);
		hyperlink.setTitle("Begin with file upload.");
		final Hyperlink hyperlink_1 = new Hyperlink(c.Logout(), iCing.LOGIN_STATE);
		layout.setWidget(3, 0, hyperlink_1);
		hyperlink_1.setTitle("Start new session.");

		// use deferred command to catch initialization exceptions
		DeferredCommand.addCommand(new Command() {
			public void execute() {
				onModuleLoad2();
			}
		});
	}

	public void onModuleLoad2() {
//		SoundController soundController = new SoundController();
//		final Sound sound = soundController.createSound(Sound.MIME_TYPE_AUDIO_MPEG, "sound/ngmater.mp3");

		// add a sound handler so we know when the sound has loaded
		// create a place holder for the load state
//		final HTML loadStateHTML = new HTML();
		// loadStateHTML.setHTML( iCing.soundLoadState );
//		sound.addEventHandler(new SoundHandler() {
//			public void onPlaybackComplete(PlaybackCompleteEvent event) {
//			}
//
//			public void onSoundLoadStateChange(SoundLoadStateChangeEvent event) {
////				loadStateHTML.setHTML(c.Load_state() + ": " + event.getLoadStateAsString());
//			}
//		});

		// create a (disabled) play button
		// playButton = new Button("Silly sound");
		// when we click, play the sound
		playButton.addClickListener(new ClickListener() {
			public void onClick(Widget sender) {
				if (iCing.soundOn) {
//					sound.play();
				} else {
					Window.alert(c.Sound_is_turn());
				}
			}
		});
	}
}
