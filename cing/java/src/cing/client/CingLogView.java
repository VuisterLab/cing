package cing.client;

import java.util.Date;

import com.google.gwt.i18n.client.DateTimeFormat;
import com.google.gwt.user.client.History;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.HasVerticalAlignment;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.RichTextArea;
import com.google.gwt.user.client.ui.Widget;

public class CingLogView extends iCingView {

    public final RichTextArea cingArea = iCing.cingArea;
    iCingQuery cingQueryLog = null;
    iCingQuery cingQueryStatus = null;
    iCingQuery cingQueryProjectName = null;

    final Label logLabel = new Label(c.Log() + " " + c.CING());

    final Button nextButton = new Button();
    final Button updateButton = new Button();

    public CingLogView() {
        super();
    }

    public void setIcing(iCing icing) {
        super.setIcing(icing);
        final iCing icingShadow = icing;
        setState(iCing.CING_LOG_STATE);
        cingArea.ensureDebugId("cwRichText-cingArea");
        // RichTextToolbar toolbar = new RichTextToolbar(cingArea);
        // toolbar.ensureDebugId("cwRichText-toolbar");

        verticalPanel.add(logLabel);
        verticalPanel.add(cingArea);
        cingArea.setSize(iCing.widthMenuStr, "25em");

        logLabel.setStylePrimaryName("h1");

        final CheckBox tailCheckBox = new CheckBox();
        tailCheckBox.setChecked(false);
        tailCheckBox.setText(c.Tail());
        tailCheckBox.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                String html = cingArea.getHTML();
                html = Utils.reverseHtml(html);
                if (html == null) {
                    General.showError("Failed to get reversed html");
                    return;
                }
                cingArea.setHTML(html);
                iCing.textIsReversedCingArea = tailCheckBox.isChecked();
            }
        });

        final Button clearButton = new Button();
        clearButton.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                cingArea.setHTML(Utils.preStart + Utils.preEnd);
            }
        });
        clearButton.setText(c.Clear());
        String iniMsg = Utils.preStart + c.Expect_to_see() + ";" +c.Once_CING_is_run() + General.eol + Utils.preEnd;
        cingArea.setHTML(iniMsg);
        nextButton.setText(c.Next());
        nextButton.setFocus(true);
        nextButton.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                icingShadow.onHistoryChanged(iCing.REPORT_STATE);
            }
        });

        HorizontalPanel horizontalPanelActions = new HorizontalPanel();
        horizontalPanelActions.setSpacing(iCing.margin);
        updateButton.setText(c.Update());
        updateButton.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                update();
            }
        });

        horizontalPanelActions.add(updateButton);
        horizontalPanelActions.add(tailCheckBox);
        horizontalPanelActions.add(clearButton);

        verticalPanel.add(horizontalPanelActions);
        horizontalPanelActions.setVerticalAlignment(HasVerticalAlignment.ALIGN_MIDDLE);
        horizontalPanelActions.add(clearButton);
        clearButton.setTitle(c.Clears_the_log_w());
        tailCheckBox.setTitle(c.Reverse_the_orde());
        // horizontalPanel.add(nextButton);
        nextButton.setTitle(c.Goto_CING_report());

        final HorizontalPanel horizontalPanelBackNext = new HorizontalPanel();
        horizontalPanelBackNext.setSpacing(iCing.margin);
        verticalPanel.add(horizontalPanelBackNext);
        final Button backButton = new Button();
        horizontalPanelBackNext.add(backButton);
        backButton.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                History.back();
            }
        });
        backButton.setText(c.Back());
        horizontalPanelBackNext.add(backButton);
        horizontalPanelBackNext.add(nextButton);

        /** JFD is uncertain if individual instances are needed but they're cheap */
        FormHandlerSpecific serverFormHandlerLog = new FormHandlerSpecific(icing);
        FormHandlerSpecific serverFormHandlerStatus = new FormHandlerSpecific(icing);
        FormHandlerSpecific serverFormHandlerProjectName = new FormHandlerSpecific(icing);

        cingQueryLog = new iCingQuery(icing);
        cingQueryLog.action.setValue(Settings.FORM_ACTION_LOG);
        cingQueryLog.setFormHandler(serverFormHandlerLog);
        verticalPanel.add(cingQueryLog.formPanel);

        cingQueryStatus = new iCingQuery(icing);
        cingQueryStatus.action.setValue(Settings.FORM_ACTION_STATUS);
        cingQueryStatus.setFormHandler(serverFormHandlerStatus);
        verticalPanel.add(cingQueryStatus.formPanel);

        cingQueryProjectName = new iCingQuery(icing);
        cingQueryProjectName.action.setValue(Settings.FORM_ACTION_PROJECT_NAME);
        cingQueryProjectName.setFormHandler(serverFormHandlerProjectName);
        verticalPanel.add(cingQueryProjectName.formPanel);
    }

    /** Needs to be called by FormHandlerMain. */
    protected void setStatus(String statusStr) {
        if ((statusStr != null) && statusStr.equals(Settings.RESPONSE_STATUS_DONE)) {
            nextButton.setEnabled(true); // or switch my self. or ...
            icing.report.showResults();
            icing.onHistoryChanged(iCing.REPORT_STATE);
        }
        if (statusStr.equals(Settings.RESPONSE_EXIT_CODE_ERROR)) {
            General.showError("Failed to get status from server; assume it crashed; Stopping");
            nextButton.setEnabled(true);
            icing.report.showCrash();
            icing.onHistoryChanged(iCing.REPORT_STATE);
        }
    }

    protected void setProjectName(String projectName) {
        icing.report.setProjectName(projectName);
    }

    protected void setLogTail(String result) {
        General.showDebug("Now in setLogTail");
        if (result == null || result.length() == 0 || result.equals(Settings.RESPONSE_LOG_VALUE_NONE)) {
            General.showDebug("No new log to display");
            return;
        }
        Utils.appendHtml(result, cingArea);
    }

    protected void getLogTail() {
        if (General.isVerbosityDebug()) {
            Date today = new Date();
            String d = DateTimeFormat.getLongTimeFormat().format(today);
            String msg = "In CingLogView: Now in getLogTail " + d + "<BR>";
            General.showDebug(msg);
        }
        cingQueryLog.formPanel.submit();
    }

    protected void getStatus() {
        General.showDebug("Now in getStatus");
        cingQueryStatus.formPanel.submit();
    }

    protected void getProjectName() {
        General.showDebug("Now in getProjectName");
        if (icing.projectName != null) {
            return;
        }
        cingQueryProjectName.formPanel.submit();
    }

    public void update() {
        if (icing.projectName == null) { // Lazy load
            getProjectName();
        }
        getStatus();
        getLogTail();
    }
}