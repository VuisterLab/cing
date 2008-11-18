package cing.client;

//import com.allen_sauer.gwt.voices.client.Sound;
//import com.allen_sauer.gwt.voices.client.SoundController;
//import com.allen_sauer.gwt.voices.client.handler.PlaybackCompleteEvent;
//import com.allen_sauer.gwt.voices.client.handler.SoundHandler;
//import com.allen_sauer.gwt.voices.client.handler.SoundLoadStateChangeEvent;
//import cing.server.General;

import com.google.gwt.user.client.ui.Label;

public class Maintenance extends iCingView {

	iCingConstants c = iCing.c;

	public Maintenance() {
		super();
	}

	public void setIcing(iCing icing) {
        super.setIcing(icing);
		// final iCing icingShadow = icing;
		setState(iCing.MAINTENANCE_STATE);

		final Label html_1 = new Label("CING is temporarily down for maintenance; please stay tuned.");
		html_1.setStylePrimaryName("h1");
		verticalPanel.add(html_1);
	}

}
