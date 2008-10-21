package cing.client;

import cing.client.content.text.RichTextToolbar;

import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.HasVerticalAlignment;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.RichTextArea;
import com.google.gwt.user.client.ui.Widget;

public class LogView extends Composite {
	
    final static RichTextArea area = iCing.area;
	iCingConstants c = iCing.c;
	public LogView() {
	    // Create the text area and toolbar
//	    RichTextArea area = new RichTextArea();
//	    area.setText("Expect to see the iCing messages scroll by here. \\nVerbosity may be controlled from iCing->Preferences.");
	    area.ensureDebugId("cwRichText-area");
	    RichTextToolbar toolbar = new RichTextToolbar(area);
	    toolbar.ensureDebugId("cwRichText-toolbar");
	    
	 // Add the components to a panel
	    Grid grid = new Grid(3, 1);
		initWidget(grid);
		grid.setSize("100%", "100%");
	    grid.setStyleName("cw-RichText");
	    grid.setWidget(1, 0, toolbar);
	    grid.setWidget(2, 0, area);
	    area.setSize("100%", "25em");
	    grid.getCellFormatter().setVerticalAlignment(1, 0, HasVerticalAlignment.ALIGN_TOP);

	    Grid gridTop = new Grid(1, 3);
	    grid.setWidget(0, 0, gridTop);
//	    horizontalPanel.setSpacing(11);

	    final Label logIcingLabel = new Label(c.Log()+" "+c.iCing());
	    logIcingLabel.setStylePrimaryName("h1");
	    gridTop.setWidget(0, 0, logIcingLabel);
		
	    final CheckBox tailCheckBox = new CheckBox();
	    gridTop.setWidget(0, 1, tailCheckBox);
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
	    gridTop.setWidget(0, 2, clearButton);
	    clearButton.addClickListener(new ClickListener() {
	    	public void onClick(final Widget sender) {
	    		area.setHTML("");
	    	}
	    });
	    clearButton.setText("Clear");
	    area.setFocus(true);
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
	    
	}	
}
