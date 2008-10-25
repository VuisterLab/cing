package cing.client;

import com.google.gwt.core.client.GWT;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;

public class Report extends iCingView {

	final HTML reportHTML = new HTML();

	final String pleaseWriteDown = "<P>Please copy down the url for future reference.</P>";
	// final Timer refreshShowResultsTimer;

	public Report() {

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
		String runUrl = moduleBaseUrlWithPort + "/" + iCing.RESULT_URL + "/" + iCing.currentUserId + "/"
				+ iCing.currentAccessKey + "/";
		General.showDebug("runUrl: [" + runUrl + "]");
		return runUrl;
	}

	/**
	 * E.g. http://localhost/iCing/../tmp/cing/JoeNmr/123456/9xxx.cing
	 * 
	 * @return
	 */
	public String getProjectUrl() {
		String runUrl = getRunUrl();
		if (runUrl == null) {
			General.showError("Failed to getResultDir");
			return null;
		}
		if (icing.projectName == null) {
			General.showError("Failed to icing.projectName");
			return null;
		}

		String projectDir = runUrl + "/" + icing.projectName + ".cing";
		General.showDebug("projectDir: [" + projectDir + "]");
		return projectDir;
	}

	public void showResults() {
		showTemporaryResults();
		String urlRun = getRunUrl();
		String urlToReport = getProjectUrl();
		// if ( urlToReport == null ) {
		// General.showDebug(
		// "Failed to getProjectUrl; sleeping 2 seconds; as problem is timing related..."
		// );
		// refreshShowResultsTimer.schedule(2000);
		// return;
		// // Don't bother stopping process because only done once and then
		// again...?
		// }

		if (urlToReport == null) {
			General.showError("Failed to getProjectUrl; not changing the report url.");
			urlToReport = iCing.NOT_AVAILABLE;
		}
		if (urlRun == null) {
			General.showError("Failed to getRunUrl; not changing the report url.");
			urlRun =  iCing.NOT_AVAILABLE;
		}
		final String linkToZipFile = "<P>Results can be download from this <A HREF=\"" + urlRun + "/" + icing.projectName + ".zip"
				+ "\">zip</a>.</P>\n";		
		String htmlTextEnabled = "CING has finished running. Please find the results <A HREF=\"" + urlToReport
				+ "\">here</a>.\n" + 
				pleaseWriteDown + 
				linkToZipFile;
		reportHTML.setHTML(htmlTextEnabled);
	}

	public void showTemporaryResults() {
		String runUrl = getRunUrl();
		if (runUrl == null) {
			General.showError("Failed to getRunUrl; not changing the report url.");
			return;
		}
		String htmlTextEnabled = "<P>CING has not finished running.</P>\n"
				+ "<P>A <A HREF=\"" + runUrl
				+ "\">directory</a> in which results are being created may be consulted in the meanwhile"
				+ " or switch to View->Log CING.\n"
				+ "<P>After a while it might be nice to check here anyway as iCing might have timed out checking\n"
				+ " but CING might be finished anywho.</P>\n" + pleaseWriteDown;
		reportHTML.setHTML(htmlTextEnabled);
	}
}
