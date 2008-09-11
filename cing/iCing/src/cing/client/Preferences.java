package cing.client;

import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.VerticalPanel;

public class Preferences extends Composite {

	public Preferences() {

		final VerticalPanel verticalPanel = new VerticalPanel();
		initWidget(verticalPanel);

		final FlexTable flexTable = new FlexTable();
		verticalPanel.add(flexTable);

		final ListBox listBox = new ListBox();
		listBox.addItem("Debug");
		listBox.addItem("Detail");
		listBox.addItem("Output");
		listBox.addItem("Warning");
		listBox.addItem("Error");
		listBox.addItem("Nothing");
		listBox.setVisibleItemCount(1);
		listBox.setSelectedIndex(2);
		
		flexTable.setWidget(0, 1, listBox);

		final Label verbosityLabel = new Label("Verbosity");
		flexTable.setWidget(0, 0, verbosityLabel);

		final CheckBox createImageryCheckBox = new CheckBox();
		flexTable.setWidget(1, 0, createImageryCheckBox);
		createImageryCheckBox.setChecked(true);
		flexTable.getFlexCellFormatter().setColSpan(1, 0, 2);
		createImageryCheckBox.setText("Create imagery");
	}

}
