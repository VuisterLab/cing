package cing.client;

import com.google.gwt.core.client.GWT;
import com.google.gwt.user.client.History;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

public class Report extends iCingView {

	final HTML reportHTML = new HTML();

	final String pleaseWriteDown = "<P>Please copy down the url for future reference.</P>"
			+ "<P>Also, open the link in another window or tab.\n"
			+ "This, because when you would go back here, your iCing environment is reinitialized and your previous work is lost.";

	// final Timer refreshShowResultsTimer;

	public Report() {
		setState(Keys.REPORT_STATE);

		iCingConstants c = iCing.c;

		VerticalPanel verticalPanel = new VerticalPanel();
		initWidget(verticalPanel);
		verticalPanel.setSpacing(iCing.margin);

		Label label = new Label(c.Report());
		label.setStylePrimaryName("h1");
		verticalPanel.add(label);

		String htmlText = "No results yet.";
		reportHTML.setHTML(htmlText);
		verticalPanel.add(reportHTML);

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
		// horizontalPanelBackNext.add(nextButton);

		showTemporaryResults();
		// refreshShowResultsTimer = new Timer() {
		// public void run() {
		// showResults();
		// }
		// };
	}

	/**
	 * E.g. http://localhost/iCing/../tmp/cing/JoeNmr/123456/
	 * 
	 * @return
	 */
	public String getRunUrl() {
		String moduleBaseUrlWithPort = GWT.getModuleBaseURL();
		// iCing part should be replaced by tmp/cing
		moduleBaseUrlWithPort = moduleBaseUrlWithPort.replace("iCing", Keys.RESULT_URL);
		String runUrl = moduleBaseUrlWithPort + "/" + iCing.currentUserId + "/" + iCing.currentAccessKey + "/";
		General.showDebug("runUrl: [" + runUrl + "] doesn't look well under local gwt hosted mode.");
		return runUrl;
	}

	// /**
	// * E.g. http://localhost/iCing/../tmp/cing/JoeNmr/123456/9xxx.cing
	// *
	// * @return
	// */
	// public String getProjectUrl() {
	// String runUrl = getRunUrl();
	// if (runUrl == null) {
	// General.showError("Failed to getResultDir");
	// return null;
	// }
	// if (icing.projectName == null) {
	// General.showError("Failed to icing.projectName");
	// return null;
	// }
	//
	// String projectDir = runUrl + "/" + icing.projectName + ".cing";
	// General.showDebug("projectDir: [" + projectDir + "]");
	// return projectDir;
	// }

	public void showResults() {
		String runUrl = getRunUrl();
		if (runUrl == null) {
			General.showError("Failed to getRunUrl; not changing the report url.");
			runUrl = Keys.NOT_AVAILABLE;
		}
		@SuppressWarnings("unused")
		final String linkToZipFile = "<P>Results can be download from this <A HREF=\"" + runUrl + "/"
				+ icing.projectName + ".zip" + "\">zip</a>.</P>\n";
		String htmlTextEnabled = "CING has finished running. Please find the results <A HREF=\"" + runUrl + "/"
				+ icing.projectName + ".cing" + "\">here</a>.\n" + pleaseWriteDown;
		reportHTML.setHTML(htmlTextEnabled);
	}

	public void showTemporaryResults() {
		String runUrl = getRunUrl();
		if (runUrl == null) {
			General.showError("Failed to getRunUrl; not changing the report url.");
			return;
		}
		String htmlTextEnabled = "<P>CING has not finished running.</P>\n" + "<P>A <A HREF=\"" + runUrl
				+ "\">directory</a> in which results are being created may be consulted in the meanwhile"
				+ " or switch to View->Log CING.\n"
				+ "<P>After a while it might be nice to check here anyway as iCing might have timed out checking\n"
				+ " but CING might be finished anywho.</P>\n" + pleaseWriteDown;
		reportHTML.setHTML(htmlTextEnabled);
	}

	public void showCrash() {
		String runUrl = getRunUrl();
		if (runUrl == null) {
			General.showError("Failed to getRunUrl; not changing the report url.");
			runUrl = Keys.NOT_AVAILABLE;
		}
		String htmlTextEnabled = "CING might have crashed as the server status could not be retrieved."+
		"It might also still be running. Please check the results sofar <A HREF=\"" + runUrl + "/"
				+ icing.projectName + ".cing" + "\">here</a>.\n" + pleaseWriteDown;
		reportHTML.setHTML(htmlTextEnabled);
	}
}
