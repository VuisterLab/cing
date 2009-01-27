package cing.client;

import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.HasVerticalAlignment;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.RichTextArea;
import com.google.gwt.user.client.ui.Widget;

public class LogView extends iCingView {

    public final RichTextArea area = iCing.area;

    final Label logLabel = new Label(c.Log() + " " + c.iCing());
    final Button startPnameButton = new Button();

    public LogView() {
        super();
    }

    public void setIcing(iCing icing) {
        super.setIcing(icing);
        // final iCing icingShadow = icing;
        setState(iCing.LOG_STATE);
        logLabel.setStylePrimaryName("h1");

        verticalPanel.add(logLabel);
        verticalPanel.add(area);
        area.setSize(iCing.widthMenuStr, "25em");

        HorizontalPanel horizontalPanel = new HorizontalPanel();
        verticalPanel.add(horizontalPanel);
        horizontalPanel.setVerticalAlignment(HasVerticalAlignment.ALIGN_MIDDLE);
        horizontalPanel.setSpacing(iCing.margin);

        final CheckBox tailCheckBox = new CheckBox();

        tailCheckBox.setChecked(false);
        tailCheckBox.setText(c.Tail());
        tailCheckBox.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                String html = area.getHTML();
                html = Utils.reverseHtml(html);
                area.setHTML(html);
                iCing.textIsReversedArea = tailCheckBox.isChecked();
            }
        });

        final Button clearButton = new Button();
        // gridTop.setWidget(0, 2, clearButton);
        clearButton.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                area.setHTML(Utils.wrapPres(""));
            }
        });
        clearButton.setText(c.Clear());
        horizontalPanel.add(clearButton);
        clearButton.setTitle(c.Clears_the_log_w());
        horizontalPanel.add(tailCheckBox);
        tailCheckBox.setTitle(c.Reverse_the_orde());
        // area.setFocus(true);

//        String userAgent = "Browser (user agent): [" + UtilsJS.getUserAgent().toLowerCase() + "]";
        String iniMsg = Utils.preStart;
        iniMsg += c.Expect_to_see() + GenClient.eol;
        iniMsg += c.Verbosity_may() + GenClient.eol;
//        iniMsg += userAgent + GenClient.eol;
        iniMsg += Utils.preEnd;
        area.setHTML(iniMsg);
    }
}
