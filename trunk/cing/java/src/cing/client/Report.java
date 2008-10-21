package cing.client;

import com.google.gwt.core.client.GWT;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;

public class Report extends Composite {

	final HTML reportHTML = new HTML();
	
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
		
	}
	public void showResults() {
		// TODO: set this dynamically.
		String moduleBaseUrlWithPort = GWT.getModuleBaseURL();
		String urlToReport = moduleBaseUrlWithPort + "/" + iCing.RESULT_URL + "/" + iCing.currentUserId + "/"+ iCing.currentAccessKey + "/";
		General.showDebug("urlToReport: [" + urlToReport +"]");
		String htmlTextEnabled = "<A HREF=\""+ urlToReport+"\">Report</a>";
		reportHTML.setHTML(htmlTextEnabled);
	}	
}
