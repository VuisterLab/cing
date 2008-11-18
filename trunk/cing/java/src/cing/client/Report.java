package cing.client;

import com.google.gwt.core.client.GWT;
import com.google.gwt.user.client.History;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;

public class Report extends iCingView {

	final HTML reportHTML = new HTML();
	iCingConstants c = iCing.c;

	final String pleaseWriteDown = "<P>Please copy down the url for future reference.</P>";

	// final Timer refreshShowResultsTimer;

	public Report() {
		super();
	}

	public void setIcing(iCing icing) {
		super.setIcing(icing);
		setState(iCing.REPORT_STATE);

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
	 * @return https://nmr.cmbi.ru.nl/tmp/cing/jd3/123456 for production. https://localhost/tmp/cing/jd3/123456 for
	 *         testing. Note that there is no trailing slash.
	 */
	public String getRunUrl() {
		/**
		 * Guaranteed to end with a slash e.g. http://localhost:8888/cing.iCing when testing.
		 * https://nmr.cmbi.ru.nl/iCing at pseudo production.
		 */
		String moduleBaseUrl = GWT.getModuleBaseURL();
		// iCing part should be replaced by tmp/cing
//		General.showDebug("moduleBaseUrl 0: " + moduleBaseUrl);
		moduleBaseUrl = moduleBaseUrl.replaceAll(":\\d+", "");
//		General.showDebug("moduleBaseUrl 1: " + moduleBaseUrl);
		/**
		 * When testing this will do something. The reason that these can't be the same as the production is that the
		 * client code has to reside in cing.client
		 */
		moduleBaseUrl = moduleBaseUrl.replace("/cing.iCing", Settings.RESULT_URL);
//		General.showDebug("moduleBaseUrl 2: " + moduleBaseUrl);
		// When production this will do something.
		moduleBaseUrl = moduleBaseUrl.replace("/iCing", Settings.RESULT_URL);
//		General.showDebug("moduleBaseUrl 3: " + moduleBaseUrl);

		String runUrl = moduleBaseUrl + iCing.currentUserId + "/" + iCing.currentAccessKey;
		General.showDebug("runUrl: [" + runUrl + "].");
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
			General.showError("In showResults. Failed to getRunUrl; not changing the report url.");
			runUrl = Settings.NOT_AVAILABLE;
		}
		if ( icing.projectName == null ) {
		    General.showError("Failed to get project name when the results have already been generated");
		}
		String htmlTextEnabled = "CING has finished running. Please find the results <A HREF=\"" + runUrl + "/"
				+ icing.projectName + ".cing" + "\" target=\"_blank\">here</a>." + General.eol + pleaseWriteDown;
		reportHTML.setHTML(htmlTextEnabled);
	}

	public void showTemporaryResults() {
		String runUrl = getRunUrl();
		if (runUrl == null) {
			General.showError("In showTemporaryResults. Failed to getRunUrl; not changing the report url.");
			return;
		}
		String htmlTextEnabled = "<P>CING has not finished running.</P>"
				+ General.eol
				+ "<P>A <A HREF=\""
				+ runUrl
				+ "\"  target=\"_blank\">directory</a> in which results are being created may be consulted in the meanwhile"
				+ " or switch to View->Log CING." + General.eol
				+ "<P>After a while it might be nice to check here anyway as iCing might have timed out checking"
				+ General.eol + " but CING might be finished anywho.</P>" + General.eol + pleaseWriteDown;
		reportHTML.setHTML(htmlTextEnabled);
	}

	public void showCrash() {
		String runUrl = getRunUrl();
		if (runUrl == null) {
			General.showError("In showTemporaryResults. Failed to getRunUrl; changing the report url to null.");
			runUrl = Settings.NOT_AVAILABLE;
		}
		String htmlTextEnabled = "CING might have crashed as the server status could not be retrieved."
				+ "It might also still be running. Please check the results sofar <A HREF=\"" + runUrl + "/"
				+ icing.projectName + ".cing" + "\" target=\"_blank\">here</a>." + General.eol + pleaseWriteDown;
		reportHTML.setHTML(htmlTextEnabled);
	}

	public void setProjectName(String projectName) {
		General.showDebug("Now in Report.setProjectName");
		if (projectName == null) {
			General.showError("Error in Report.setProjectName; got a null for project name.");
			return;
		}
		icing.projectName = projectName;
        General.showDebug("Set  project name to: [" + icing.projectName +"]");
		showTemporaryResults();
	}
}
