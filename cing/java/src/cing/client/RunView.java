package cing.client;

import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.DecoratorPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

public class RunView extends iCingView {

	final HTML reportHTML = new HTML();
	DecoratorPanel decPanel = new DecoratorPanel();
	static final Button runButton = new Button();
	static final Button nextButton = new Button();
	CingQuery cingQueryRun; 
	
	public RunView() {
		initWidget(decPanel);
		iCingConstants c = iCing.c;
		final VerticalPanel verticalPanel = new VerticalPanel();
		verticalPanel.setSpacing(iCing.margin);
		decPanel.setWidget(verticalPanel);

		final Label html_1 = new Label( c.Run() );
		html_1.setStylePrimaryName("h1");
		verticalPanel.add(html_1);

		final Label html_2 = new Label( "Please press the button when you are ready." );
		verticalPanel.add(html_2);
		
		runButton.setText(c.Run());
		runButton.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				runButton.setText("Running...");
				run();
			}
		});
		runButton.setEnabled(true);
		
		verticalPanel.add(runButton);
		verticalPanel.setCellHorizontalAlignment(runButton, HasHorizontalAlignment.ALIGN_LEFT);
				
		nextButton.setText(c.Next());
		nextButton.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				icing.onHistoryChanged(iCing.CING_LOG_STATE);					
			}
		});	
//		nextButton.setEnabled(false); //disable for testing it will be triggered by a run; or not...
		verticalPanel.add(nextButton);
		verticalPanel.setCellHorizontalAlignment(nextButton, HasHorizontalAlignment.ALIGN_CENTER);
		
		cingQueryRun = new CingQuery(); 
		cingQueryRun.action.setValue(iCing.RUN_SERVER_ACTION_RUN);
		verticalPanel.add(cingQueryRun.formPanel);
		
	}	
	
	protected void run() {		

		// Fire this one off first.
		icing.cingLogView.getProjectName();		

		runButton.setEnabled(false);
		
		icing.report.showTemporaryResults();
		nextButton.setEnabled(true); // or switch my self. or enable after run submitted.
		/** Needs to be called by ServerFormHandler */
		icing.cingLogView.getProjectName();		
		icing.cingLogView.startLogAndStatuscCheckers();
		// Call it right away.
		cingQueryRun.formPanel.submit();		
		icing.onHistoryChanged(iCing.CING_LOG_STATE);							
	}			
}
