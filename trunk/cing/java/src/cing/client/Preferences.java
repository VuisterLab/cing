package cing.client;

import com.google.gwt.user.client.ui.ChangeListener;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

public class Preferences extends iCingView {

	int i = 0;
	final int optionVerbosityIdx = i++;
	final int optionSoundIdx = i++;
    
	public Preferences() {
		super();
	}
	
	public void setIcing(iCing icing) {
        super.setIcing(icing);
		final iCing icingShadow = icing;		
		setState(iCing.PREFERENCES_STATE);

		final Label html_1 = new Label( c.Preferences() );
		html_1.setStylePrimaryName("h1");
		verticalPanel.add(html_1);		
		verticalPanel.add(decPanel);		
		final VerticalPanel verticalPanelInner = new VerticalPanel();
		decPanel.add(verticalPanelInner);
		final FlexTable flexTable = new FlexTable();
		verticalPanelInner.add(flexTable);
		flexTable.setCellSpacing(5);
		flexTable.setCellPadding(5);

		final ListBox listBox = new ListBox();
		listBox.addItem(c.Nothing(),"0");
		listBox.addItem(c.Error(),"1");
		listBox.addItem(c.Warning(),"2");
		listBox.addItem(c.Output(),"3");
		listBox.addItem(c.Detail(),"4");		
		listBox.addItem(c.Debug(),"5"); // give up extra space between 4 and 9 for coding convenience here.

		listBox.setVisibleItemCount(1);
//		flexTable.setWidget(0, 1, listBox);
		listBox.addChangeListener(new ChangeListener() {
			public void onChange(final Widget sender) {
				General.setVerbosity(Integer.parseInt( listBox.getValue( listBox.getSelectedIndex() )));
				General.showOutput("verbosity now: " + General.getVerbosity() );				
				icingShadow.setVerbosityToDebug(General.isVerbosityDebug());
				General.showOutput("visibilityStatusArea: " + General.isVerbosityDebug());
			}
		});
		listBox.setSelectedIndex(General.getVerbosity());
		flexTable.setWidget(optionVerbosityIdx, 1, listBox);
		
		
		final Label verbosityLabel = new Label(c.Verbosity());
		flexTable.setWidget(optionVerbosityIdx, 0, verbosityLabel);
	}
}
