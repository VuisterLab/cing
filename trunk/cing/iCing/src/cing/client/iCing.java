package cing.client;

//import java.util.ArrayList;

import com.allen_sauer.gwt.voices.client.Sound;
import com.allen_sauer.gwt.voices.client.SoundController;
import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.DialogBox;
import com.google.gwt.user.client.ui.RootPanel;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;
import cing.client.fileUploadRow;

/**
 * Entry point classes define <code>onModuleLoad()</code>.
 */
public class iCing implements EntryPoint {
	public void onModuleLoad() {
		RootPanel rootPanel = RootPanel.get();
		final VerticalPanel verticalPanel = new VerticalPanel();
		rootPanel.add(verticalPanel);
		verticalPanel.setSpacing(10);

		SoundController soundController = new SoundController();
	    final Sound sound = soundController.createSound(Sound.MIME_TYPE_AUDIO_MPEG,
	        "ngmater.mp3");
		
		final CheckBox soundBox = new CheckBox();
		verticalPanel.add(soundBox);
		soundBox.setEnabled(true);
		soundBox.setChecked(true);
		soundBox.setText("Sound");
		final CheckBox showDialogBoxesBox = new CheckBox();
		verticalPanel.add(showDialogBoxesBox);
		showDialogBoxesBox.setEnabled(true);
		showDialogBoxesBox.setChecked(false);
		showDialogBoxesBox.setText("Show Dialog Boxes");
		soundBox.addClickListener(new ClickListener() {
			public void onClick(Widget sender) {
			    if ( ! soundBox.isChecked() ) { // already reset at this point.
					sound.stop();			}
			    }
		});
	    if ( soundBox.isChecked() ) {
	    	sound.play();	    	
	    }
	   
		
		final CheckBox showAllCheckBox = new CheckBox();
		verticalPanel.add(showAllCheckBox);
		showAllCheckBox.setEnabled(true);
		showAllCheckBox.setText("Show types to come");

		final fileUploadRow fileUploadRow_ = new fileUploadRow();
		verticalPanel.add(fileUploadRow_);
//	    final ArrayList<NmrFileUpload> fileUploadList = new ArrayList<NmrFileUpload>();
//		int firstFileUploadWidgetIdxInPanel = verticalPanel.getWidgetCount();
//		final Options options = new Options();
//		verticalPanel.add(options);
		
		// Create the dialog box
		final DialogBox dialogBox = new DialogBox();
		// dialogBox.setAnimationEnabled(true);
		Button closeButton = new Button("close");
		VerticalPanel dialogVPanel = new VerticalPanel();
		dialogVPanel.setWidth("100%");
		dialogVPanel.setHorizontalAlignment(VerticalPanel.ALIGN_CENTER);
		dialogVPanel.add(closeButton);

		closeButton.addClickListener(new ClickListener() {
			public void onClick(Widget sender) {
				dialogBox.hide();
			}
		});

		// Set the contents of the Widget
		dialogBox.setWidget(dialogVPanel);

		showAllCheckBox.addClickListener(new ClickListener() {
			public void onClick(Widget sender) {
				boolean isChecked = showAllCheckBox.isChecked();
//				options.setVisible(isChecked);
				if ( showDialogBoxesBox.isChecked() ) {
					String msg = "Closed the panels";
					if ( isChecked ) {
						msg = "Opened the panels";
					}
					dialogBox.setText(msg);
					dialogBox.center();
					dialogBox.show();
				}
			}
		});

//		final Criteria criteria = new Criteria();
//		verticalPanel.add(criteria);				
	}
}
