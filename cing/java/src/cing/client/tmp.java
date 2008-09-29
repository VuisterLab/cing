package cing.client;

import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DecoratorPanel;
import com.google.gwt.user.client.ui.FileUpload;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Hyperlink;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.VerticalPanel;

public class tmp extends Composite {

	public tmp() {
		iCingConstants c = iCing.c;	
		
		// Now create the user interface, wrapped in a
		// vertical panel
		VerticalPanel verticalPanel = new VerticalPanel();
		initWidget(verticalPanel);
		// fileUpload.addChangeListener(this);

		Label label = new Label(c.Upload());
		label.setStylePrimaryName("h1");

		// verticalPanel.add(statusMessage);
		verticalPanel.add(label);

		// Since there is no status initially, hide the
		// status message
		// statusMessage.setVisible(false);

		// When the user clicks on the button, we submit
		// the surrounding form

		 
		// The GWT calls this form handler after the form
		// is submitted in the button click listener implemented
		// above.

		DecoratorPanel decPanel = new DecoratorPanel();
		final HorizontalPanel horizontalPanel = new HorizontalPanel();
		verticalPanel.add(decPanel);
		decPanel.add(horizontalPanel);
		horizontalPanel.setSpacing(11);

		final Image image = new Image();
		horizontalPanel.add(image);
		image.setUrl("images/paperclip.png");
		image.setSize("24", "24");

		final FlexTable flexTable = new FlexTable();
		horizontalPanel.add(flexTable);

		final Button saveButton = new Button();
		flexTable.setWidget(6, 1, saveButton);
		flexTable.getCellFormatter().setHorizontalAlignment(6, 1, HasHorizontalAlignment.ALIGN_CENTER);
		flexTable.getFlexCellFormatter().setColSpan(6, 1, 7);
		saveButton.setText("Add");

		final Label coordinateLabel = new Label("project");
		flexTable.setWidget(2, 3, coordinateLabel);

		final Label rdcLabel = new Label("hydrogen bond");
		flexTable.setWidget(4, 5, rdcLabel);

		final Label ccpnLabel = new Label("CING");
		flexTable.setWidget(2, 2, ccpnLabel);
		flexTable.getCellFormatter().setHorizontalAlignment(2, 4, HasHorizontalAlignment.ALIGN_CENTER);

		final Label xplorLabel = new Label("XPLOR/CNS");
		flexTable.setWidget(4, 2, xplorLabel);

		final FileUpload fileUpload_3 = new FileUpload();
		flexTable.setWidget(5, 1, fileUpload_3);

		final ListBox listBox = new ListBox();
		flexTable.setWidget(5, 2, listBox);
		listBox.setSelectedIndex(5);
		listBox.addItem("CCPN");
		listBox.addItem("CING");
		listBox.addItem("DYANA/DIANA");
		listBox.addItem("NMR-STAR");
		listBox.addItem("PDB");
		listBox.addItem("XPLOR/CNS");
		listBox.setTitle("Program");
		listBox.setVisibleItemCount(1);

		final Label programLabel = new Label("Program");
		flexTable.setWidget(0, 2, programLabel);

		final Label typeLabel = new Label("Type");
		flexTable.setWidget(0, 3, typeLabel);

		final Label subtypeLabel = new Label("Subtype");
		flexTable.setWidget(0, 5, subtypeLabel);

		final CheckBox checkBox = new CheckBox();
		flexTable.setWidget(2, 0, checkBox);
		checkBox.setChecked(true);
		checkBox.setText("");

		final CheckBox checkBox_1 = new CheckBox();
		flexTable.setWidget(4, 0, checkBox_1);
		checkBox_1.setChecked(true);
		checkBox_1.setText("");

		final CheckBox checkBox_2 = new CheckBox();
		flexTable.setWidget(5, 0, checkBox_2);
		checkBox_2.setEnabled(false);
		checkBox_2.setText("");

		final Label label_1 = new Label("-");
		flexTable.setWidget(2, 5, label_1);

		final ListBox listBox_1 = new ListBox();
		flexTable.setWidget(5, 3, listBox_1);
		listBox_1.setEnabled(false);
		listBox_1.setVisibleItemCount(1);

		final Button removeButton_2 = new Button();
		flexTable.setWidget(5, 7, removeButton_2);
		removeButton_2.setEnabled(false);
		removeButton_2.setText("Remove");

		final Label distanceLabel = new Label("distance");
		flexTable.setWidget(4, 3, distanceLabel);

		final Hyperlink hyperlink = new Hyperlink("1brv.cing.tgz (binary/tgz) 100K", "some history token");
		flexTable.setWidget(2, 1, hyperlink);

		final Hyperlink hyperlink_1 = new Hyperlink("1brv_noe.tbl (text/txt) 3K", "some history token");
		flexTable.setWidget(4, 1, hyperlink_1);

		final Label other_propLabel = new Label("Other_prop");
		flexTable.setWidget(0, 6, other_propLabel);

		final Label lowerLabel = new Label("lower");
		flexTable.setWidget(4, 6, lowerLabel);

		final ListBox listBox_2 = new ListBox();
		flexTable.setWidget(5, 5, listBox_2);
		listBox_2.setEnabled(false);
		listBox_2.setVisibleItemCount(1);

		final ListBox listBox_3 = new ListBox();
		flexTable.setWidget(5, 6, listBox_3);
		listBox_3.setEnabled(false);
		listBox_3.setVisibleItemCount(1);


	}

}
