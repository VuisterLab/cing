package cing.client;

import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.PushButton;
import com.google.gwt.user.client.ui.TextBox;

public class Options extends Composite {

	private TextBox textBox_2;
	private ListBox listBox;
	private TextBox textBox_1;
	private TextBox textBox;
	public Options() {

		final FlexTable flexTable = new FlexTable();
		initWidget(flexTable);
		flexTable.setCellSpacing(0);
		flexTable.setCellPadding(5);

		final Label residuesLabel = new Label("Residues:");
		flexTable.setWidget(0, 0, residuesLabel);

		textBox = new TextBox();
		flexTable.setWidget(0, 1, textBox);
		textBox.setWidth("100%");

		final Label eg175177189Label = new Label("(E.g. 175,177-189)");
		flexTable.setWidget(0, 2, eg175177189Label);

		final Label ensembleModelsLabel = new Label("Ensemble models:");
		flexTable.setWidget(1, 0, ensembleModelsLabel);

		textBox_1 = new TextBox();
		flexTable.setWidget(1, 1, textBox_1);
		textBox_1.setWidth("100%");

		final Label eg219Label = new Label("(E.g. 2-19)");
		flexTable.setWidget(1, 2, eg219Label);

		final Label verbosityinAscendingLabel = new Label("Verbosity (in ascending order)\t");
		flexTable.setWidget(2, 0, verbosityinAscendingLabel);

		listBox = new ListBox();
		flexTable.setWidget(2, 1, listBox);
		listBox.setSelectedIndex(3);
		listBox.addItem("Nothing");
		listBox.addItem("Error");
		listBox.addItem("Warning");
		listBox.addItem("Output");
		listBox.addItem("Detail");
		listBox.addItem("Debug");
		listBox.setVisibleItemCount(5);

		final CheckBox createImageryCheckBox = new CheckBox();
		flexTable.setWidget(2, 2, createImageryCheckBox);
		createImageryCheckBox.setText("Create imagery");

		final Label accessKeyLabel = new Label("Access key");
		flexTable.setWidget(3, 0, accessKeyLabel);

		final HorizontalPanel horizontalPanel = new HorizontalPanel();
		flexTable.setWidget(3, 1, horizontalPanel);
		horizontalPanel.setSpacing(5);

		textBox_2 = new TextBox();
		horizontalPanel.add(textBox_2);
		textBox_2.setVisibleLength(6);

		final Label az096Label = new Label("[a-Z0-9]{6}");
		horizontalPanel.add(az096Label);

		final PushButton regeneratePushButton = new PushButton("Up text", "Down text");
		regeneratePushButton.getDownFace().setHTML("Randomizing...");
		regeneratePushButton.getUpFace().setHTML("Regenerate");
		flexTable.setWidget(3, 2, regeneratePushButton);
		regeneratePushButton.setHTML("Randomizing...");
		regeneratePushButton.setText("Regenerate");
	}
	public TextBox getTextBox() {
		return textBox;
	}
	public TextBox getTextBox_1() {
		return textBox_1;
	}
	public ListBox getListBox() {
		return listBox;
	}
	public TextBox getTextBox_2() {
		return textBox_2;
	}

}
