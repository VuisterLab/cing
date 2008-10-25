package cing.client;

import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
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
	CingQuery cingQueryLogTail = null; 
	CingQuery cingQueryStatus = null; 
	CingQuery cingQueryProjectName = null; 
	
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

	public CingLogView() {
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
		Grid gridTop = new Grid(1, 3);
		verticalPanel.add(logLabel);
		verticalPanel.add(gridTop);
		verticalPanel.add(area);
		area.setSize(iCing.widthMenu, "25em");
		// grid.getCellFormatter().setVerticalAlignment(1, 0,
		// HasVerticalAlignment.ALIGN_TOP);

		// horizontalPanel.setSpacing(11);

		logLabel.setStylePrimaryName("h1");

		final CheckBox tailCheckBox = new CheckBox();
		gridTop.setWidget(0, 1, tailCheckBox);
		tailCheckBox.setChecked(false);
		tailCheckBox.setText(c.Tail());
		tailCheckBox.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				String html = area.getHTML();
				html = Utils.reverse(html);
				area.setHTML(html);
				iCing.textIsReversedCingArea = tailCheckBox.isChecked();
			}
		});

		final Button clearButton = new Button();
		gridTop.setWidget(0, 2, clearButton);
		clearButton.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				area.setHTML("");
			}
		});
		clearButton.setText("Clear");
		area.setFocus(true);
		String iniMsg = "Expect to see CING log lines here; once CING is running."+"<br>";
		area.setHTML(iniMsg);

		nextButton.setText(c.Next());
		nextButton.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				icing.onHistoryChanged(iCing.REPORT_STATE);
			}
		});
		nextButton.setEnabled(false); // will be enabled automatically.

		verticalPanel.add(nextButton);
		verticalPanel.setCellHorizontalAlignment(nextButton, HasHorizontalAlignment.ALIGN_CENTER);


		// For debugging logger.
		final Button startLogButton = new Button();
		startLogButton.setText("start log");
		startLogButton.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				startLogRetrieval();
			}
		});
		final Button stopLogButton = new Button();
		stopLogButton.setText("stop log");
		stopLogButton.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				stopLogRetrieval();
			}
		});
		verticalPanel.add(startLogButton);
		verticalPanel.add(stopLogButton);

		// For debugging logger.
		final Button startStatusButton = new Button();
		startStatusButton.setText("start status");
		startStatusButton.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				startStatusChecker();
			}
		});
		final Button stopStatusButton = new Button();
		stopStatusButton.setText("stop status");
		stopStatusButton.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				stopStatusChecker();
			}
		});
		verticalPanel.add(startStatusButton);
		verticalPanel.add(stopStatusButton);

		cingQueryLogTail = new CingQuery(); 
		cingQueryLogTail.action.setValue(iCing.RUN_SERVER_ACTION_LOG);
		cingQueryLogTail.serverFormHandler.setCingLogView(this);
		verticalPanel.add(cingQueryLogTail.formPanel);
		
		cingQueryStatus = new CingQuery(); 
		cingQueryStatus.action.setValue(iCing.RUN_SERVER_ACTION_STATUS);						
		cingQueryStatus.serverFormHandler.setCingLogView(this);
		verticalPanel.add(cingQueryStatus.formPanel);

		cingQueryProjectName = new CingQuery(); 
		cingQueryProjectName.action.setValue(iCing.RUN_SERVER_ACTION_PROJECT_NAME);						
		cingQueryProjectName.serverFormHandler.setCingLogView(this);
		verticalPanel.add(cingQueryProjectName.formPanel);
	}

	public void startStatusChecker() {
		// setup timer to refresh list automatically
		if (statusTimerScheduled) {
			return;
		}
		if ( statusTimerBusy ) {
//			General.showCodeBug("statusTimerBusy but not statusTimerScheduled");
			return;
		}
		Timer timer = new Timer() {
			public void run() {
//				General.showDebug("checking run status");
				if (statusTimerBusy) {
					return;
				}
				statusTimerBusy = true;
				getStatus();
			}
		};
		statusTimer = timer;
		statusTimerScheduled = true;
		statusTimer.scheduleRepeating(iCing.REFRESH_INTERVAL);
	}

	/** Needs to be called by ServerFormHandler */
	protected void setStatus(String statusStr) {
		if ((statusStr != null) && statusStr.equals(iCing.RESPONSE_STATUS_DONE)) {
			stopStatusChecker();
			startLogRetrieval();
			stopLogRetrieval();
			nextButton.setEnabled(true); // or switch my self. or ...
			icing.report.showResults();
			icing.onHistoryChanged(iCing.REPORT_STATE);
		}
		statusTimerBusy = false;
	}
	
	/** Needs to be called by ServerFormHandler */
	protected void setProjectName(String projectName) {		
		if ((projectName != null) && projectName.equals(iCing.RESPONSE_STATUS_NONE)) {
			icing.projectName = projectName;
		}		
	}
	
	protected void stopLogRetrieval() {
//		General.showDebug("Now in stopLogRetrieval");
		logTimer.cancel();
		logTimerScheduled = false;
		logTimerBusy = false; // should have done by setLogTail
	}

	public void startLogRetrieval() {
		// setup timer to refresh list automatically
		if (logTimerScheduled ) {
			return;
		}
		if ( logTimerBusy ) {
//			General.showCodeBug("logTimerBusy but not logTimerScheduled");
			return;
		}
		
		Timer timer = new Timer() {
			public void run() {
				if (logTimerBusy) {
					General.showDebug("logTimerBusy");
					return;
				}
				logTimerBusy = true;
//				General.showDebug("getting CING log");
				getLogTail();
			}
		};
		logTimer = timer;
		logTimerScheduled = true;
		logTimer.scheduleRepeating(iCing.REFRESH_INTERVAL);
	}

	protected void setLogTail(String message) {
//		General.showDebug("Now in setLogTail");
//		appendLog("In iCing: Now in setLogTail");
		if (message != null) {
			appendLog("<PRE>"+message+"</PRE>");
		}
		logTimerBusy = false;
	}

	protected void getLogTail() {
//		Date today = new Date();
//		String d = DateTimeFormat.getLongTimeFormat().format(today);
//		String msg = "In iCing: Now in getLogTail "+d+"<BR>";
//		General.showDebug(msg);
//		appendLog(msg);		
		cingQueryLogTail.formPanel.submit();
	}

	protected void appendLog(String message) {
//		General.showDebug("Now in appendLog");
		if (iCing.textIsReversedArea) {
			area.setHTML(message + area.getHTML());
		} else {
			area.setHTML(area.getHTML() + message);
		}

	}

	protected void stopStatusChecker() {
//		General.showDebug("Now in stopStatusChecker");
		statusTimer.cancel();
		statusTimerScheduled = false;
	}

	protected void getStatus() {
//		General.showDebug("Now in getStatus");
		cingQueryStatus.formPanel.submit();
	}

	protected void getProjectName() {
//		General.showDebug("Now in getProjectName");
		cingQueryProjectName.formPanel.submit();
	}

	public void startLogAndStatuscCheckers() {
		startStatusChecker();
		startLogRetrieval();
	}
}