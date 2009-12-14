package cing.client;

import com.google.gwt.core.client.GWT;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;

public class Report extends iCingView {

	final HTML reportHTML = new HTML();
	final String pleaseWriteDown = "<P>" + c.Please_copy_down() + "</P>";

	// final Timer refreshShowResultsTimer;

	public Report() {
		super();
	}

	public void setIcing(iCing icing) {
		super.setIcing(icing);
		final iCing icingShadow = icing;

		setState(iCing.REPORT_STATE);

		Label label = new Label(c.Report());
		label.setStylePrimaryName("h1");
		verticalPanel.add(label);

		String htmlText = c.No_results_yet();
		reportHTML.setHTML(htmlText);
		verticalPanel.add(reportHTML);

		final HorizontalPanel horizontalPanelBackNext = new HorizontalPanel();
		horizontalPanelBackNext.setSpacing(iCing.margin);
		verticalPanel.add(horizontalPanelBackNext);
		final Button backButton = new Button();
		horizontalPanelBackNext.add(backButton);
		backButton.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				icingShadow.onHistoryChanged(iCing.CING_LOG_STATE);
				// History.back();
			}
		});
		backButton.setText(c.Back());
		horizontalPanelBackNext.add(backButton);
		// horizontalPanelBackNext.add(nextButton);

		final HorizontalPanel horizontalPanelBackPurge = new HorizontalPanel();
		horizontalPanelBackPurge.setSpacing(iCing.margin);
		verticalPanel.add(horizontalPanelBackPurge);
		final Button purgeButton = new Button();
		horizontalPanelBackPurge.add(purgeButton);
		purgeButton.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				icingShadow.cingLogView.getPurgeProject();
			}
		});
		purgeButton.setText(c.PurgeProject());
		purgeButton.setTitle(c.PurgeProjectTitl());
		horizontalPanelBackPurge.add(purgeButton);

		showTemporaryResults();
		// refreshShowResultsTimer = new Timer() {
		// public void run() {
		// showResults();
		// }
		// };
	}

	/** Input:
	 * http://localhost:8080/icing/iCing.html or
	 * http://localhost:8888/iCing.html?gwt.codesvr=192.168.2.3:9997
	 * https://nmr.cmbi.ru.nl/icing/iCing.html
	 *
	 * @return https://nmr.cmbi.ru.nl/tmp/cing/jd3/123456
	 *         https://localhost/tmp/cing/jd3/123456
	 *         there is no trailing slash.
	 */
	public String getRunUrl() {
//		UrlBuilder builder = Location.createUrlBuilder();
//		builder.setPort(UrlBuilder.PORT_UNSPECIFIED);
//		String urlString = builder.buildString();
//		GenClient.showDebug("urlString 0: " + urlString);
		// Guaranteed to end with a slash e.g.
		String moduleBaseUrl = GWT.getModuleBaseURL();
		// iCing part should be replaced by tmp/cing
//		GenClient.showDebug("moduleBaseUrl 0: " + moduleBaseUrl);
		moduleBaseUrl = moduleBaseUrl.replaceAll(":\\d+", "");
//		GenClient.showDebug("moduleBaseUrl 1: " + moduleBaseUrl);
		moduleBaseUrl = moduleBaseUrl.replace("/icing", ""); // optional.
//		GenClient.showDebug("moduleBaseUrl 2: " + moduleBaseUrl);
		int endIndex = moduleBaseUrl.length() - 1;
		moduleBaseUrl = moduleBaseUrl.substring(0, endIndex);
//		GenClient.showDebug("moduleBaseUrl 3: " + moduleBaseUrl);

		String runUrl = moduleBaseUrl + Settings.RESULT_URL + "/"
				+ iCing.currentUserId + "/" + iCing.currentAccessKey;
		GenClient.showDebug("runUrl: [" + runUrl + "].");
		return runUrl;
	}

	public void showResults() {
		GenClient.showDebug("Now in report#showResults");
		String runUrl = getRunUrl();
		if (runUrl == null) {
			GenClient
					.showError("In showResults. Failed to getRunUrl; not changing the report url.");
			runUrl = Settings.NOT_AVAILABLE;
		}
		if (icing.projectName == null) {
			GenClient
					.showError("Failed to get project name when the results have already been generated");
		}

		String htmlTextEnabled = c.CING_has_finishe() + " <A HREF=\"" + runUrl
				+ "/" + icing.projectName + ".cing" + "\" target=\"_blank\">"
				+ c.here() + "</a>." + GenClient.eol + c.A_zip_file_with()
				+ " <A HREF=\"" + runUrl + "/" + icing.projectName
				+ Settings.ZIP_REPORT_FILENAME_POST_FIX + ".zip"
				+ "\" target=\"_blank\">" + c.here() + "</a>." + GenClient.eol
				+ pleaseWriteDown;
		reportHTML.setHTML(htmlTextEnabled);
	}

	public void showTemporaryResults() {
		String runUrl = getRunUrl();
		if (runUrl == null) {
			GenClient
					.showError("In showTemporaryResults. Failed to getRunUrl; not changing the report url.");
			return;
		}
		String htmlTextEnabled = "<P>" + c.CING_has_not_fin() + "</P>"
				+ GenClient.eol + "<P>" + c.A() + " <A HREF=\"" + runUrl
				+ "\"  target=\"_blank\">" + c.directory() + "</a> "
				+ c.in_which_results() + " " + c.View() + "->" + c.Log()
				+ " CING." + GenClient.eol + "<P>" + c.After_a_while_it()
				+ GenClient.eol + " </P>" + GenClient.eol + pleaseWriteDown;
		reportHTML.setHTML(htmlTextEnabled);
	}

	public void showCrash() {
		String runUrl = getRunUrl();
		if (runUrl == null) {
			GenClient
					.showError("In showTemporaryResults. Failed to getRunUrl; changing the report url to null.");
			runUrl = Settings.NOT_AVAILABLE;
		}
		String htmlTextEnabled = c.CING_might_have() + "<A HREF=\"" + runUrl
				+ "/" + icing.projectName + ".cing" + "\" target=\"_blank\">"
				+ c.here() + "</a>." + GenClient.eol + pleaseWriteDown;
		reportHTML.setHTML(htmlTextEnabled);
	}

	public void setProjectName(String projectName) {
		// GenClient.showDebug("Now in Report.setProjectName");
		if (projectName == null) {
			GenClient
					.showError("Error in Report.setProjectName; got a null for project name.");
			return;
		}
		icing.projectName = projectName;
		GenClient
				.showDebug("Set  project name to: [" + icing.projectName + "]");
		showTemporaryResults();
	}

	public void setPurgeProject(String result) {
		GenClient.showDebug("Now in Report.purgeProject");
		String msg = c.PurgedProject();
		GenClient.showOutput(result);
		Window.alert(msg);
		// icing.fileView.init();
	}

}
