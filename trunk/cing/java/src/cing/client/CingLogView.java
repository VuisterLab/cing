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
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

public class CingLogView extends iCingView {

	iCingConstants c = iCing.c;
	public final RichTextArea cingArea = iCing.cingArea;
	iCingQuery cingQueryLog = null;
	iCingQuery cingQueryStatus = null;
	iCingQuery cingQueryProjectName = null;

	final Label logLabel = new Label(c.Log() + " " + c.CING());

	final Button nextButton = new Button();
	final Button updateButton = new Button();

	public CingLogView() {
		setState(iCing.CING_LOG_STATE);
		cingArea.ensureDebugId("cwRichText-cingArea");
		// RichTextToolbar toolbar = new RichTextToolbar(cingArea);
		// toolbar.ensureDebugId("cwRichText-toolbar");

		// Add the components to a panel
		final VerticalPanel verticalPanel = new VerticalPanel();
		initWidget(verticalPanel);
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
		clearButton.setText("Clear");
		String iniMsg = Utils.preStart
				+ "Expect to see CING log lines here; once CING is running and you update with the below button."+General.eol
				+ Utils.preEnd;
		cingArea.setHTML(iniMsg);
		nextButton.setText(c.Next());
		nextButton.setFocus(true);
		nextButton.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				icing.onHistoryChanged(iCing.REPORT_STATE);
			}
		});

		HorizontalPanel horizontalPanelActions = new HorizontalPanel();
		horizontalPanelActions.setSpacing(iCing.margin);
		updateButton.setText("Update");
		updateButton.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				updateLogAndStatus();
			}
		});

		horizontalPanelActions.add(updateButton);
		horizontalPanelActions.add(clearButton);
		horizontalPanelActions.add(tailCheckBox);

		verticalPanel.add(horizontalPanelActions);
		horizontalPanelActions.setVerticalAlignment(HasVerticalAlignment.ALIGN_MIDDLE);
		horizontalPanelActions.add(clearButton);
		clearButton.setTitle("Clears the log window.");
		tailCheckBox.setTitle("Reverse the order of lines in the log.");
		// horizontalPanel.add(nextButton);
		nextButton.setTitle("Goto CING report.");

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

		cingQueryLog = new iCingQuery();
		cingQueryLog.action.setValue(Keys.FORM_ACTION_LOG);
		cingQueryLog.serverFormHandler.setCingLogView(this);
		verticalPanel.add(cingQueryLog.formPanel);

		cingQueryStatus = new iCingQuery();
		cingQueryStatus.action.setValue(Keys.FORM_ACTION_READINESS);
		cingQueryStatus.serverFormHandler.setCingLogView(this);
		verticalPanel.add(cingQueryStatus.formPanel);

		cingQueryProjectName = new iCingQuery();
		cingQueryProjectName.action.setValue(Keys.FORM_ACTION_PROJECT_NAME);
		cingQueryProjectName.serverFormHandler.setCingLogView(this);
		verticalPanel.add(cingQueryProjectName.formPanel);
	}

	/** Needs to be called by ServerFormHandler. */
	protected void setStatus(String statusStr) {
		if ((statusStr != null) && statusStr.equals(Keys.RESPONSE_STATUS_DONE)) {
			nextButton.setEnabled(true); // or switch my self. or ...
			icing.report.showResults();
			icing.onHistoryChanged(iCing.REPORT_STATE);
		}
		if (statusStr.equals(Keys.RESPONSE_EXIT_CODE_ERROR)) {
			General.showError("Failed to get status from server; assume it crashed; Stopping");
			nextButton.setEnabled(true);
			icing.report.showCrash();
			icing.onHistoryChanged(iCing.REPORT_STATE);
		}
	}

	protected void setProjectName(String projectName) {
		icing.report.setProjectName(projectName);
	}

	protected void setLogTail(String message) {
		// General.showDebug("Now in setLogTail");
		// appendLog("In iCing: Now in setLogTail");
		if (message.equals(Keys.RESPONSE_RESULT)) {
			Date today = new Date();
			String dateTime = DateTimeFormat.getShortDateTimeFormat().format(today);
			General.showDebug(dateTime + " no new log to display");
		} else if (message != null && message.length() > 0) {
			Utils.appendHtml(message, cingArea);
		}
	}

	protected void getLogTail() {
		if (General.isVerbosityDebug()) {
			Date today = new Date();
			String d = DateTimeFormat.getLongTimeFormat().format(today);
			String msg = "In CingLogView: Now in getLogTail " + d + "<BR>";
			General.showDebug(msg);
			Utils.appendHtml(msg, cingArea);
		}
		cingQueryLog.formPanel.submit();
	}

	protected void getStatus() {
		General.showDebug("Now in getStatus");
		cingQueryStatus.formPanel.submit();
	}

	protected void getProjectName() {
		General.showDebug("Now in getProjectName");
		cingQueryProjectName.formPanel.submit();
	}

	public void updateLogAndStatus() {
		if (icing.projectName == null) { // Lazy load
			getProjectName();
		}
		getStatus();
		getLogTail();
	}
}