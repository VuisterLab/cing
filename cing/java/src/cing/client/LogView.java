package cing.client;

import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.HasVerticalAlignment;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.RichTextArea;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

public class LogView extends iCingView {
	
	iCingConstants c = iCing.c;
    public final RichTextArea area = iCing.area;
    
    final Label logLabel = new Label(c.Log()+" "+c.iCing());
	final Button startPnameButton = new Button();

    public LogView() {
		setState(iCing.LOG_STATE);
		// Add the components to a panel
		final VerticalPanel verticalPanel = new VerticalPanel();
		// Grid grid = new Grid(countRows, 1);
		initWidget(verticalPanel);
	    // Create the text area and toolbar
//	    RichTextArea area = new RichTextArea();
//	    area.setText("Expect to see the iCing messages scroll by here. \\nVerbosity may be controlled from iCing->Preferences.");
	    area.ensureDebugId("cwRichText-area");
//	    RichTextToolbar toolbar = new RichTextToolbar(area);
//	    toolbar.ensureDebugId("cwRichText-toolbar");
	    
	 // Add the components to a panel
//	    Grid grid = new Grid(3, 1);
//		initWidget(grid);
//		grid.setSize("100%", "100%");
//	    grid.setStyleName("cw-RichText");
//	    grid.setWidget(1, 0, toolbar);
//	    grid.setWidget(2, 0, area);
	    logLabel.setStylePrimaryName("h1");
//	    gridTop.setWidget(0, 0, logLabel);

	    verticalPanel.add( logLabel );
	    verticalPanel.add( area );
		area.setSize(iCing.widthMenu, "25em");
	    
//	    grid.getCellFormatter().setVerticalAlignment(1, 0, HasVerticalAlignment.ALIGN_TOP);

//	    Grid gridTop = new Grid(1, 3);
//	    grid.setWidget(0, 0, gridTop);
//	    horizontalPanel.setSpacing(11);


	    HorizontalPanel horizontalPanel = new HorizontalPanel();
	    verticalPanel.add( horizontalPanel );
	    horizontalPanel.setVerticalAlignment(HasVerticalAlignment.ALIGN_MIDDLE);
	    horizontalPanel.setSpacing(iCing.margin);
	    
	    final CheckBox tailCheckBox = new CheckBox();
//	    gridTop.setWidget(0, 1, tailCheckBox);
	    tailCheckBox.setChecked(false);
	    tailCheckBox.setText(c.Tail());	    
	    tailCheckBox.addClickListener(new ClickListener() {
	    	public void onClick(final Widget sender) {
	    		String html = area.getHTML();
	    		html = Utils.reverse( html);
	    		area.setHTML(html);
	    		iCing.textIsReversedArea = tailCheckBox.isChecked();
	    	}
		});

	    final Button clearButton = new Button();
//	    gridTop.setWidget(0, 2, clearButton);
	    clearButton.addClickListener(new ClickListener() {
	    	public void onClick(final Widget sender) {
	    		area.setHTML("");
	    	}
	    });
	    clearButton.setText("Clear");
	    horizontalPanel.add(clearButton);
	    clearButton.setTitle("Clears the log window.");
	    horizontalPanel.add(tailCheckBox);
	    tailCheckBox.setTitle("Reverse the order of lines in the log.");
//	    area.setFocus(true);
	    String iniMsg = c.Expect_to_see()+"<br>";
	    iniMsg += c.Verbosity_may()+"<br>"; //Verbosity may be controlled from iCing->Preferences.\n";
//	    iniMsg += "<PRE>[debug] 1</PRE>\n";
//	    iniMsg += "<PRE>[debug] 2</PRE>\n";
//	    iniMsg += "<PRE>[debug] Stop staring at this very very very verbose \\ndebugging...</PRE>\n";
//	    iniMsg += "12:01:10 PM [debug] EditBus: RegisterChanged[register=$,source=null]</PRE>";
//	    iniMsg += "</PRE>";
	    

	    area.setHTML( iniMsg );
//	    General.showDebug("1 Found text area html: ["+area.getHTML()+"]");   
//	    General.showDebug(  "Test debug msg");   
//		General.showOutput( "Test output msg");
//		General.showWarning("Test warning msg");
//		General.showError(  "Test error msg");

		/** Section for testing within GWT hosted mode without having to do Junit testing 
		 * 
		 * 
		 * PLACEHOLDER
		 * 
		 * 
		int[] inputList = new int[] { 0, 1, 1050, 1000000, 2000000 };
		String[] expectedResultList = new String[] { "0 bytes", "1 bytes", "1.03 kb", "976.56 kb", "1.91 Mb" };
		for (int i = 0; i < inputList.length; i++) {
			String result = Utils.bytesToFormattedString(inputList[i]);
			General.showDebug("Converted input: ["+inputList[i]+"] to ["+result+"] and expected: [" + expectedResultList[i] +"]");
//			assertEquals(result, expectedResultList[i]);
		}
		 * */
		// For debugging logger.
		startPnameButton.setText("get Project name");
		startPnameButton.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				icing.cingLogView.getProjectName();		
			}
		});
		verticalPanel.add(startPnameButton);
	}	
}
