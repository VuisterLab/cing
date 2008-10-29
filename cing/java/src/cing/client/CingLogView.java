package cing.client;

import java.util.Date;

import com.google.gwt.i18n.client.DateTimeFormat;
import com.google.gwt.user.client.History;
import com.google.gwt.user.client.Timer;
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

	static boolean statusTimerScheduled = false;
	static boolean statusTimerBusy = false;
	static boolean logTimerScheduled = false;
	static boolean logTimerBusy = false;
	iCingConstants c = iCing.c;
	public final RichTextArea area = iCing.cingArea;
	iCingQuery cingQueryLogTail = null;
	iCingQuery cingQueryStatus = null;
	iCingQuery cingQueryProjectName = null;

	Timer statusTimer = null;
	Timer logTimer = null;

	final Label logLabel = new Label(c.Log() + " " + c.CING());

	// int i = 0;
	// final int gridTopIdx = i++;
	// final int gridToolbarIdx = i++;
	// final int gridAreaIdx = i++;
	// final int gridNextButtonIdx = i++;
	// final int countRows = i;

	final Button nextButton = new Button();
	final Button startLogButton = new Button();
	final Button stopLogButton = new Button();
	final Button startStatusButton = new Button();
	final Button stopStatusButton = new Button();

	public CingLogView() {
		setState(Keys.CING_LOG_STATE);
		// Create the text area and toolbar
		// RichTextArea area = new RichTextArea();
		// area.setText(
		// "Expect to see the iCing messages scroll by here. \\nVerbosity may be controlled from iCing->Preferences."
		// );
		area.ensureDebugId("cwRichText-area");
		// RichTextToolbar toolbar = new RichTextToolbar(area);
		// toolbar.ensureDebugId("cwRichText-toolbar");

		// Add the components to a panel
		final VerticalPanel verticalPanel = new VerticalPanel();
		// Grid grid = new Grid(countRows, 1);
		initWidget(verticalPanel);
		// grid.setSize("100%", "100%");
		// grid.setStyleName("cw-RichText");
		// grid.setWidget(gridToolbarIdx, 0, toolbar);
		verticalPanel.add(logLabel);
		verticalPanel.add(area);
		area.setSize(iCing.widthMenuStr, "25em");
		// grid.getCellFormatter().setVerticalAlignment(1, 0,
		// HasVerticalAlignment.ALIGN_TOP);

		// horizontalPanel.setSpacing(11);

		logLabel.setStylePrimaryName("h1");

		final CheckBox tailCheckBox = new CheckBox();
		tailCheckBox.setChecked(false);
		tailCheckBox.setText(c.Tail());
		tailCheckBox.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				String html = area.getHTML();
				html = Utils.reverse(html);
				if (html == null) {
					General.showError("Failed to get reversed html");
					return;
				}
				area.setHTML(html);
				iCing.textIsReversedCingArea = tailCheckBox.isChecked();
			}
		});

		final Button clearButton = new Button();
		clearButton.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				area.setHTML("<PRE></PRE>");
			}
		});
		clearButton.setText("Clear");
		// area.setFocus(false);
		String iniMsg = "<PRE>" + "Expect to see CING log lines here; once CING is running.\n";
		area.setHTML(iniMsg);
		nextButton.setText(c.Next());
		nextButton.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				icing.onHistoryChanged(Keys.REPORT_STATE);
			}
		});
		// nextButton.setEnabled(false); // will be enabled automatically.

		HorizontalPanel horizontalPanel = new HorizontalPanel();
		horizontalPanel.setSpacing(iCing.margin);

		verticalPanel.add(horizontalPanel);
		horizontalPanel.setVerticalAlignment(HasVerticalAlignment.ALIGN_MIDDLE);
		horizontalPanel.add(clearButton);
		clearButton.setTitle("Clears the log window.");
		horizontalPanel.add(tailCheckBox);
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

		// For debugging logger.
		startLogButton.setText("start log");
		startLogButton.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				startLogRetrieval();
			}
		});
		stopLogButton.setText("stop log");
		stopLogButton.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				stopLogRetrieval();
			}
		});
		verticalPanel.add(startLogButton);
		verticalPanel.add(stopLogButton);

		// For debugging logger.
		startStatusButton.setText("start status");
		startStatusButton.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				startStatusChecker();
			}
		});
		stopStatusButton.setText("stop status");
		stopStatusButton.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				stopStatusChecker();
			}
		});
		verticalPanel.add(startStatusButton);
		verticalPanel.add(stopStatusButton);

		startStatusButton.setVisible(false);
		stopStatusButton.setVisible(false);
		startLogButton.setVisible(false);
		stopLogButton.setVisible(false);

		cingQueryLogTail = new iCingQuery();
		cingQueryLogTail.action.setValue(Keys.RUN_SERVER_ACTION_LOG);
		cingQueryLogTail.serverFormHandler.setCingLogView(this);
		verticalPanel.add(cingQueryLogTail.formPanel);

		cingQueryStatus = new iCingQuery();
		cingQueryStatus.action.setValue(Keys.RUN_SERVER_ACTION_STATUS);
		cingQueryStatus.serverFormHandler.setCingLogView(this);
		verticalPanel.add(cingQueryStatus.formPanel);

		cingQueryProjectName = new iCingQuery();
		cingQueryProjectName.action.setValue(Keys.RUN_SERVER_ACTION_PROJECT_NAME);
		cingQueryProjectName.serverFormHandler.setCingLogView(this);
		verticalPanel.add(cingQueryProjectName.formPanel);
	}

	public void startStatusChecker() {
		// setup timer to refresh list automatically
		if (statusTimerScheduled) {
			return;
		}
		if (statusTimerBusy) {
			//General.showCodeBug("statusTimerBusy but not statusTimerScheduled"
			// );
			return;
		}
		Timer timer = new Timer() {
			public void run() {
				// General.showDebug("checking run status");
				if (statusTimerBusy) {
					return;
				}
				statusTimerBusy = true;
				getStatus();
			}
		};
		statusTimer = timer;
		statusTimerScheduled = true;
		statusTimer.scheduleRepeating(iCing.REFRESH_INTERVAL_LOG);
	}

	/** Needs to be called by ServerFormHandler.
	 * 
	 *  */
	protected void setStatus(String statusStr) {
		if ((statusStr != null) && statusStr.equals(Keys.RESPONSE_STATUS_DONE)) {
			stopStatusChecker();
			startLogRetrieval();
			stopLogRetrieval();
			nextButton.setEnabled(true); // or switch my self. or ...
			icing.report.showResults();
			icing.onHistoryChanged(Keys.REPORT_STATE);
		}
		if (statusStr.equals(Keys.RESPONSE_GENERAL_ERROR)) {
			General.showError("Failed to get status from server; assume it crashed; Stopping");
			stopStatusChecker();
			startLogRetrieval();
			stopLogRetrieval();
			nextButton.setEnabled(true);
			icing.report.showCrash();
			icing.onHistoryChanged(Keys.REPORT_STATE);
		}

		statusTimerBusy = false;
	}

	/** Needs to be called by ServerFormHandler */
	protected void setProjectName(String projectName) {
		General.showDebug("Now in setProjectName");
		if (projectName != null) {
			icing.projectName = projectName;
			icing.report.showResults();
		}
	}

	protected void stopLogRetrieval() {
		// General.showDebug("Now in stopLogRetrieval");
		logTimer.cancel();
		logTimerScheduled = false;
		logTimerBusy = false; // should have done by setLogTail
	}

	public void startLogRetrieval() {
		// setup timer to refresh list automatically
		if (logTimerScheduled) {
			return;
		}
		if (logTimerBusy) {
			// General.showCodeBug("logTimerBusy but not logTimerScheduled");
			return;
		}

		Timer timer = new Timer() {
			public void run() {
				if (logTimerBusy) {
					General.showDebug("logTimerBusy");
					return;
				}
				logTimerBusy = true;
				// General.showDebug("getting CING log");
				getLogTail();
			}
		};
		logTimer = timer;
		logTimerScheduled = true;
		logTimer.scheduleRepeating(iCing.REFRESH_INTERVAL_LOG);
	}

	protected void setLogTail(String message) {
		// General.showDebug("Now in setLogTail");
		// appendLog("In iCing: Now in setLogTail");
		if (message.equals(Keys.RESPONSE_TAIL_VALUE_NONE)) {
			Date today = new Date();
			String dateTime = DateTimeFormat.getShortDateTimeFormat().format(today);
			General.showDebug(dateTime + " no new log to display");
		} else if (message != null && message.length() > 0) {
			appendLog(message);
		}
		logTimerBusy = false;
	}

	protected void getLogTail() {
		// Date today = new Date();
		// String d = DateTimeFormat.getLongTimeFormat().format(today);
		// String msg = "In iCing: Now in getLogTail "+d+"<BR>";
		// General.showDebug(msg);
		// appendLog(msg);
		cingQueryLogTail.formPanel.submit();
	}

	protected void appendLog(String message) {
		// General.showDebug("Now in appendLog");
		String orgHTML = area.getHTML();
		String orgText = "";
		int n = orgHTML.length();
		if (n < 11) {
			General.showCodeBug("In appendLog. Expected at least the string: <PRE></PRE>	");
		} else {
			int x = n - 6; // </PRE>
			orgText = orgHTML.substring(5, x);
		}
		message = message.replace("DEBUG", "<font color=\"green\">DEBUG</font>");
		message = message.replace("ERROR", "<font color=\"red\">ERROR</font>");
		message = message.replace("WARNING", "<font color=\"orange\">WARNING</font>");
		message = message.replace("Warning", "<font color=\"orange\">Warning</font>");
		area.setHTML("<PRE>" + orgText + message + "</PRE>");
	}

	protected void stopStatusChecker() {
		// General.showDebug("Now in stopStatusChecker");
		statusTimer.cancel();
		statusTimerScheduled = false;
	}

	protected void getStatus() {
		// General.showDebug("Now in getStatus");
		cingQueryStatus.formPanel.submit();
	}

	protected void getProjectName() {
		// General.showDebug("Now in getProjectName");
		cingQueryProjectName.formPanel.submit();
	}

	public void startLogAndStatuscCheckers() {
		startStatusChecker();
		startLogRetrieval();
	}
}