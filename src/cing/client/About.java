package cing.client;

import cing.client.i18n.iCingConstants;

import com.google.gwt.i18n.client.LocaleInfo;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.DialogBox;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

public class About extends DialogBox {

    iCingConstants c = iCing.c;
    // Add some text to the top of the dialog
    public HTML details = new HTML();

    public About() {
        setHTML(c.About() + " iCing");
        details.setHTML(c.iCing() + " " + c.is_part() + " <A href=\"http://nmr.cmbi.ru.nl/cing/\">" + c.CING()
                + "</a> " + c.software() + ".");
        // Create a table to layout the content
        VerticalPanel dialogContents = new VerticalPanel();
        dialogContents.setSpacing(4);
        this.setWidget(dialogContents);

        dialogContents.add(details);
        dialogContents.setCellHorizontalAlignment(details, HasHorizontalAlignment.ALIGN_CENTER);

        // Add an image to the dialog
        Image image = new Image("images/cing.png");
        image.setSize("393", "295");
        dialogContents.add(image);
        dialogContents.setCellHorizontalAlignment(image, HasHorizontalAlignment.ALIGN_CENTER);
        final DialogBox dialogBox = this;
        // Add a close button at the bottom of the dialog.
        Button closeButton = new Button(c.Close(), new ClickListener() {
            public void onClick(Widget sender) {
                dialogBox.hide();
            }
        });
        dialogContents.add(closeButton);
        if (LocaleInfo.getCurrentLocale().isRTL()) {
            dialogContents.setCellHorizontalAlignment(closeButton, HasHorizontalAlignment.ALIGN_LEFT);

        } else {
            dialogContents.setCellHorizontalAlignment(closeButton, HasHorizontalAlignment.ALIGN_RIGHT);
        }
        this.center();
        this.setAnimationEnabled(true);
    }

}
