package cing.client;

import java.util.ArrayList;

import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.ChangeListener;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DecoratorPanel;
import com.google.gwt.user.client.ui.FileUpload;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

public class FileView extends Composite {

	final Button startButton = new Button();
	final FlexTable flexTable = new FlexTable();
	final Button addButton = new Button();
	int i = 0;
	final int checkBoxIdx = i++;
	final int fileIdx = i++;
	final int programIdx = i++;
	final int typeIdx = i++;
	final int subTypeIdx = i++;
	final int otherIdx = i++;
	final int removeIdx = i++;

	public FileView() {
		iCingConstants c = iCing.c;

		// Now create the user interface, wrapped in a
		// vertical panel
		VerticalPanel verticalPanel = new VerticalPanel();
		initWidget(verticalPanel);
		verticalPanel.setSpacing(iCing.margin);
		// fileUpload.addChangeListener(this);

		Label label = new Label(c.Upload());
		label.setStylePrimaryName("h1");

		// verticalPanel.add(statusMessage);
		verticalPanel.add(label);

		DecoratorPanel decPanel = new DecoratorPanel();
		final HorizontalPanel horizontalPanel = new HorizontalPanel();
		verticalPanel.add(decPanel);
		decPanel.add(horizontalPanel);
		horizontalPanel.setSpacing(11);

		final Image image = new Image();
		horizontalPanel.add(image);
		image.setUrl("images/paperclip.png");
		image.setSize("24", "24");

		horizontalPanel.add(flexTable);
		showStartButton();
		startButton.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				showUpload();
				addUploadRow();
			}
		});
		addButton.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				addUploadRow();
			}
		});
		showUpload();
		addUploadRow();
		

	}

	public boolean showStartButton() {
		flexTable.setWidget(0, 0, startButton);
		startButton.setText("Upload file");
		startButton.setVisible(true);
		flexTable.getCellFormatter().setHorizontalAlignment(1, 1, HasHorizontalAlignment.ALIGN_CENTER);

		return false;
	}

	public boolean showUpload() {
		startButton.setVisible(false);
		final Label programLabel = new Label("Program");
		flexTable.setWidget(0, programIdx, programLabel);

		final Label typeLabel = new Label("Type");
		flexTable.setWidget(0, typeIdx, typeLabel);

		final Label subtypeLabel = new Label("Subtype");
		flexTable.setWidget(0, subTypeIdx, subtypeLabel);

		final Label otherLabel = new Label("Other");
		flexTable.setWidget(0, otherIdx, otherLabel);

		flexTable.setWidget(1, 1, addButton);
		addButton.setText("Upload another file");
		flexTable.getCellFormatter().setHorizontalAlignment(1, 1, HasHorizontalAlignment.ALIGN_CENTER);
		return false;
	}

	public boolean addUploadRow() {
		int currentRowIdx = flexTable.getRowCount() - 1;
		General.showDebug("currentRowIdx" + currentRowIdx);
		flexTable.insertRow(currentRowIdx); // push the Add button down.

		final CheckBox checkBox = new CheckBox();
		flexTable.setWidget(currentRowIdx, checkBoxIdx, checkBox);
		checkBox.setChecked(true);
		checkBox.setText("");
		checkBox.setVisible(false);

		final FileUpload fileUpload = new FileUpload();
		flexTable.setWidget(currentRowIdx, fileIdx, fileUpload);

		final ListBox listBox_Program = new ListBox();
		flexTable.setWidget(currentRowIdx, programIdx, listBox_Program);
		listBox_Program.setVisibleItemCount(1);
		ArrayList<String> programList = Classification.getProgramList();
		if (programList == null) { // impossible but modeled for consistency with below boxes.
			listBox_Program.addItem(Defs.STRING_NA);
		} else {
			for (String item : programList) {
				listBox_Program.addItem(item);
			}
		}
		listBox_Program.setItemSelected(0, true);

		final ListBox listBox_Type = new ListBox();
		flexTable.setWidget(currentRowIdx, typeIdx, listBox_Type);
		listBox_Type.setVisibleItemCount(1);
		String program = listBox_Program.getValue( listBox_Program.getSelectedIndex()); 
		ArrayList<String> typeList = Classification.getTypeList(program);
		if (typeList == null) { // impossible but modeled for consistency with below boxes.
			listBox_Type.addItem(Defs.STRING_NA);
		} else {
			for (String item : typeList) {
				listBox_Type.addItem(item);
			}
		}
		listBox_Type.setItemSelected(0, true);

		final ListBox listBox_Subtype = new ListBox();
		flexTable.setWidget(currentRowIdx, subTypeIdx, listBox_Subtype);
		listBox_Subtype.setVisibleItemCount(1);
		String type = listBox_Type.getValue( listBox_Type.getSelectedIndex()); 
		ArrayList<String> subTypeList = Classification.getSubTypeList(program, type);
		if (subTypeList == null || subTypeList.size() == 0) {
			listBox_Subtype.addItem(Defs.STRING_NA);
		} else {
			for (String item : subTypeList) {
				if ( item == null ) {
					item = Defs.STRING_NA;
				}
				listBox_Subtype.addItem(item);
			}
		}
		listBox_Subtype.setItemSelected(0, true);

		final ListBox listBox_Other = new ListBox();
		flexTable.setWidget(currentRowIdx, otherIdx, listBox_Other);
		listBox_Other.setVisibleItemCount(1);
		String subType = listBox_Subtype.getValue( listBox_Subtype.getSelectedIndex()); 
		ArrayList<String> otherList = Classification.getOtherList(program, type, subType );
		if (otherList == null || otherList.size() == 0 ) {
			listBox_Other.addItem(Defs.STRING_NA);
		} else {
			for (String item : otherList) {
				if ( item == null ) {
					item = Defs.STRING_NA;
				}
				listBox_Other.addItem(item);
			}
		}
		listBox_Other.setItemSelected(0, true);

		/** Removing file while not (fully) transmitted to server. */
		final Button removeButton = new Button();
		flexTable.setWidget(currentRowIdx, removeIdx, removeButton);
		removeButton.setText("Remove");
		removeButton.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				int[] indices = Utils.getIndicesFromTable(flexTable, sender);
				if (indices == null) {
					General.showCodeBug("Failed to get getIndicesFromTable");
					return;
				}
				flexTable.removeRow(indices[0]);
				if (flexTable.getRowCount() < 3) { // Start over.
				// flexTable.clear();
					Utils.removeAllRows(flexTable);
					General.showDebug("After removing all rows; counted rows: " + flexTable.getRowCount());
					// flexTable.removeRow(0);
					// flexTable.removeCells(row, column, num)
					showStartButton();
				}
			}
		});

//		setEnableAllWidgetAtByRow(currentRowIdx, false);
		removeButton.setEnabled(true);

		listBox_Program.addChangeListener( new ChangeListener() {
			public void onChange(Widget sender) {
				ListBox listBox_Program = (ListBox) sender;
				String program = listBox_Program.getValue( listBox_Program.getSelectedIndex()); 				
				updateListBox_Type(listBox_Type, program);
			}

			private void updateListBox_Type(ListBox listBox_Type, String program) {
				listBox_Type.clear();
				ArrayList<String> typeList = Classification.getTypeList(program);
				if (typeList == null) { // impossible but modeled for consistency with below boxes.
					listBox_Type.addItem(Defs.STRING_NA);
				} else {
					for (String item : typeList) {
						listBox_Type.addItem(item); 
					}
				}
				listBox_Type.setItemSelected(0, true);				
			}			
		});
		
		listBox_Type.addChangeListener( new ChangeListener() {
			public void onChange(Widget sender) {
				ListBox listBox_Type = (ListBox) sender;
				String program = listBox_Program.getValue( listBox_Program.getSelectedIndex()); 				
				String type = listBox_Type.getValue( listBox_Type.getSelectedIndex()); 				
				updateListBox_Subtype(listBox_Subtype, program, type);
			}

			private void updateListBox_Subtype(ListBox listBox_Subtype, String program, String type) {
				listBox_Subtype.clear();
				ArrayList<String> subTypeList = Classification.getSubTypeList(program, type);
				if (subTypeList == null) { // impossible but modeled for consistency with below boxes.
					listBox_Subtype.addItem(Defs.STRING_NA);
				} else {
					for (String item : subTypeList) {
						listBox_Subtype.addItem(item); 
					}
				}
				listBox_Subtype.setItemSelected(0, true);				
			}			
		});
		
		return false;
	}

	
	public void setEnableAllWidgetAtByRow(int row, boolean b) {
		int colCount = flexTable.getCellCount(row);
		for (int i = 0; i < colCount; i++) {
			Widget w = flexTable.getWidget(row, i);
			Utils.setEnabled(w, b);
		}
	}
}
