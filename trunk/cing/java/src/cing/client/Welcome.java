package cing.client;

//import com.allen_sauer.gwt.voices.client.Sound;
//import com.allen_sauer.gwt.voices.client.SoundController;
//import com.allen_sauer.gwt.voices.client.handler.PlaybackCompleteEvent;
//import com.allen_sauer.gwt.voices.client.handler.SoundHandler;
//import com.allen_sauer.gwt.voices.client.handler.SoundLoadStateChangeEvent;
//import cing.server.General;

import com.google.gwt.user.client.ui.Hyperlink;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;

public class Welcome extends iCingView {

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
        VerticalPanel verticalPanelDec = new VerticalPanel();
        verticalPanelDec.setSpacing(iCing.margin);
        decPanel.add(verticalPanelDec);
        final Hyperlink hyperlink = new Hyperlink(c.Start(), iCing.FILE_STATE);
        verticalPanelDec.add(hyperlink);
        hyperlink.setTitle(c.Begin_with_file());
        final Hyperlink hyperlink_1 = new Hyperlink(c.Logout(), iCing.LOGIN_STATE);
        verticalPanelDec.add(hyperlink_1);
        hyperlink_1.setTitle(c.Start_new_sessi());
    }

}
