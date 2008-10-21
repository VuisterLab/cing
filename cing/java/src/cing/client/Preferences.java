package cing.client;

import com.google.gwt.user.client.ui.ChangeListener;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DecoratorPanel;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.RichTextArea;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

public class Preferences extends Composite {

	DecoratorPanel decPanel = new DecoratorPanel();
	iCingConstants c = iCing.c;	
    final static RichTextArea statusArea = iCing.statusArea;

	public Preferences() {

		initWidget(decPanel);
		final VerticalPanel verticalPanel = new VerticalPanel();
		decPanel.setWidget(verticalPanel);

		final FlexTable flexTable = new FlexTable();
		verticalPanel.add(flexTable);

		final ListBox listBox = new ListBox();
		listBox.addItem(c.Nothing(),"0");
		listBox.addItem(c.Error(),"1");
		listBox.addItem(c.Warning(),"2");
		listBox.addItem(c.Output(),"3");
		listBox.addItem(c.Detail(),"4");		
		listBox.addItem(c.Debug(),"9"); // refuse to give up extra space between 4 and 9 for coding convenience here.

		listBox.setVisibleItemCount(1);

		flexTable.setWidget(0, 1, listBox);
		listBox.addChangeListener(new ChangeListener() {
			public void onChange(final Widget sender) {
				General.verbosity = Integer.parseInt( listBox.getValue( listBox.getSelectedIndex() ));
				statusArea.setVisible( General.verbosity >= General.verbosityDetail );
			}
		});

		listBox.setSelectedIndex(5);
		
		
		final Label verbosityLabel = new Label(c.Verbosity());
		flexTable.setWidget(0, 0, verbosityLabel);

		final CheckBox createImageryCheckBox = new CheckBox();
		flexTable.setWidget(1, 0, createImageryCheckBox);
		createImageryCheckBox.setChecked(true);
		flexTable.getFlexCellFormatter().setColSpan(1, 0, 2);
		createImageryCheckBox.setText(c.Imagery_repor());

		final CheckBox soundCheckBox = new CheckBox();
		flexTable.setWidget(2, 0, soundCheckBox);
		soundCheckBox.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				iCing.soundOn = soundCheckBox.isChecked();
			}
		});
		soundCheckBox.setChecked(true);
		soundCheckBox.setText(c.Sound());

		final CheckBox debugModeCheckBox = new CheckBox();
		flexTable.setWidget(3, 0, debugModeCheckBox);
		debugModeCheckBox.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				iCing.debugOn = debugModeCheckBox.isChecked();
			}
		});
		debugModeCheckBox.setChecked(true);
		debugModeCheckBox.setText(c.Debug_mode());
		debugModeCheckBox.setVisible(false); // disabled; work thru the verbosity setting.				
	}
}
