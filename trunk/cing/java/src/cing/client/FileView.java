package cing.client;

import java.util.ArrayList;

import com.google.gwt.core.client.GWT;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.ChangeListener;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DecoratorPanel;
import com.google.gwt.user.client.ui.FileUpload;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;
import com.gwtsolutions.components.client.ui.Message;

public class FileView extends Composite {

	
	private static final String FILE_UPLOAD_SERVLET_RELATIVE_URL = iCing.RPC_URL+"/FileUpload.py";
	// Development:
	// http://localhost:8888/cing.iCing/iCing.html
	final Button startButton = new Button();
	final FlexTable flexTable = new FlexTable();
	final Button addButton = new Button();
	// The Message widget is a GWT Solutions widget. See
	// the GWTSolutions Components module for details.
	private final Message statusMessage = new Message("empty msg", Message.SHAKE, 0.5);

	int i = 0;
	final int checkBoxIdx = i++;
	final int fileIdx = i++;
	final int programIdx = i++;
	final int typeIdx = i++;
	final int subTypeIdx = i++;
	final int otherIdx = i++;
	final int removeIdx = i++;
	final int submitIdx = i++;

	iCingConstants c = iCing.c;

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

		verticalPanel.add(label);
		verticalPanel.add(statusMessage);
		// Since there is no status initially, hide the status message
		statusMessage.setVisible(false);

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
		// General.showDebug("currentRowIdx" + currentRowIdx);
		flexTable.insertRow(currentRowIdx); // push the Add button down.

		final CheckBox checkBoxUseFile = new CheckBox();
		flexTable.setWidget(currentRowIdx, checkBoxIdx, checkBoxUseFile);
		checkBoxUseFile.setChecked(true);
		checkBoxUseFile.setText("");
//		checkBoxUseFile.setVisible(false);

		final Label labelFileUploadDone = new Label("This message should not show up.");
		labelFileUploadDone.setVisible(false);
		
		final FileUpload fileUpload = new FileUpload();
		fileUpload.setName(iCing.FORM_UPLOAD_FILE_BASE);
		Button submitButton = new Button(c.Submit());
		
		final FormPanel formPanel = new FormPanel();
		formPanel.setEncoding(FormPanel.ENCODING_MULTIPART);
		formPanel.setMethod(FormPanel.METHOD_POST);
//		formPanel.setMethod(FormPanel.METHOD_GET);
		String moduleBaseUrlWithPort = GWT.getModuleBaseURL();
//		General.showDebug("moduleBaseUrlWithPort: " + moduleBaseUrlWithPort);
//		int endIndex = moduleBaseUrlWithPort.lastIndexOf(':');
//		if ( endIndex < 0 ) {
//			endIndex = moduleBaseUrlWithPort.length();
//		}
//		String moduleBaseUrl = moduleBaseUrlWithPort.substring(0, endIndex);
//		String actionUrl = "http://localhost/cgi/iCing/bla";
		
		// Testing:
		// moduleBaseUrlWithPort: http://localhost:8888/cing.iCing/
		// Production:
		// moduleBaseUrlWithPort: https://nmr.cmbi.ru.nl/iCing/
		String actionUrl = moduleBaseUrlWithPort + "/" + FILE_UPLOAD_SERVLET_RELATIVE_URL;
//		General.showDebug("actionUrl: [" + actionUrl +"]");
		formPanel.setAction(actionUrl);
		/** Since not more than one element can be added to formpanel; the individual items 
		 * need to be wrapped in another element that can contain them.
		 */
		VerticalPanel formLayoutPanel = new VerticalPanel();
		HorizontalPanel fileUploadHorizontalPanel = new HorizontalPanel();
		fileUploadHorizontalPanel.add(fileUpload); // will switch between these two.
		fileUploadHorizontalPanel.add(labelFileUploadDone);
		formPanel.setWidget(formLayoutPanel);
		formLayoutPanel.add(fileUploadHorizontalPanel);
		flexTable.setWidget(currentRowIdx, fileIdx, formPanel);
		// The GWT calls this form handler after the form
		// is submitted.
		FileFormHandler fileFormHandler = new FileFormHandler();
		
		flexTable.setWidget(currentRowIdx, submitIdx, submitButton);
		/** Invisible parameters to pass */
		formLayoutPanel.add(new Hidden(iCing.FORM_ACCESS_KEY, iCing.currentAccessKey) ); 
		formLayoutPanel.add(new Hidden(iCing.FORM_USER_ID, iCing.currentUserId) ); 
		
		final ListBox listBox_Program = new ListBox();
		flexTable.setWidget(currentRowIdx, programIdx, listBox_Program);
		listBox_Program.setVisibleItemCount(1);
		ArrayList<String> programList = Classification.getProgramList();
		if (programList == null) { // impossible but modeled for consistency
			// with below boxes.
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
		String program = listBox_Program.getValue(listBox_Program.getSelectedIndex());
		ArrayList<String> typeList = Classification.getTypeList(program);
		if (typeList == null) { // impossible but modeled for consistency with
			// below boxes.
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
		String type = listBox_Type.getValue(listBox_Type.getSelectedIndex());
		ArrayList<String> subTypeList = Classification.getSubTypeList(program, type);
		if (subTypeList == null || subTypeList.size() == 0) {
			listBox_Subtype.addItem(Defs.STRING_NA);
		} else {
			for (String item : subTypeList) {
				if (item == null) {
					item = Defs.STRING_NA;
				}
				listBox_Subtype.addItem(item);
			}
		}
		listBox_Subtype.setItemSelected(0, true);

		final ListBox listBox_Other = new ListBox();
		flexTable.setWidget(currentRowIdx, otherIdx, listBox_Other);
		listBox_Other.setVisibleItemCount(1);
		String subType = listBox_Subtype.getValue(listBox_Subtype.getSelectedIndex());
		ArrayList<String> otherList = Classification.getOtherList(program, type, subType);
		if (otherList == null || otherList.size() == 0) {
			listBox_Other.addItem(Defs.STRING_NA);
		} else {
			for (String item : otherList) {
				if (item == null) {
					item = Defs.STRING_NA;
				}
				listBox_Other.addItem(item);
			}
		}
		listBox_Other.setItemSelected(0, true);

		
		fileFormHandler.setFileUpload(fileUpload);
		fileFormHandler.setLabelFileUploadDone(labelFileUploadDone);
		fileFormHandler.setStatusMessage(statusMessage);
		fileFormHandler.setSubmitButton(submitButton);
		fileFormHandler.setCheckBoxUseFile(checkBoxUseFile);
		fileFormHandler.setListBox_Program(listBox_Program);
		fileFormHandler.setListBox_Type(listBox_Type);
		fileFormHandler.setListBox_Subtype(listBox_Subtype);
		fileFormHandler.setListBox_Other(listBox_Other);
		
		/** Removing file while not (fully) transmitted to server. */
//		final Button removeButton = new Button();
//		flexTable.setWidget(currentRowIdx, removeIdx, removeButton);
//		removeButton.setText("Remove");
		checkBoxUseFile.addClickListener(new ClickListener() {
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
					//General.showDebug("After removing all rows; counted rows: "
					// + flexTable.getRowCount());
					// flexTable.removeRow(0);
					// flexTable.removeCells(row, column, num)
					showStartButton();
				}
			}
		});
		

		// setEnableAllWidgetAtByRow(currentRowIdx, false);
//		removeButton.setEnabled(true);
		listBox_Program.addChangeListener(new ChangeListener() {
			public void onChange(Widget sender) {
				updateListBox();

			}

			private void updateListBox() {
				// General.showDebug("Starting: listBox_Program.updateListBox");
				int idx = listBox_Program.getSelectedIndex();
				if (idx < 0) {
					General.showError("Failed to get program");
					return;
				}
				String program = listBox_Program.getValue(idx);
				ArrayList<String> typeList = Classification.getTypeList(program);
				listBox_Type.clear();
				for (String item : typeList) {
					listBox_Type.addItem(item);
				}
				listBox_Type.setItemSelected(0, true);
				listBox_Type.onBrowserEvent(Event.getCurrentEvent());
			}
		});

		listBox_Type.addChangeListener(new ChangeListener() {
			public void onChange(Widget sender) {
				updateListBox();
			}

			private void updateListBox() {
				// General.showDebug("Starting: listBox_Type.updateListBox");
				int idx = listBox_Program.getSelectedIndex();
				if (idx < 0) {
					General.showError("Failed to get program");
					return;
				}
				String program = listBox_Program.getValue(idx);
				idx = listBox_Type.getSelectedIndex();
				if (idx < 0) {
					General.showError("Failed to get type");
					return;
				}
				String type = listBox_Type.getValue(idx);
				ArrayList<String> subTypeList = Classification.getSubTypeList(program, type);
				listBox_Subtype.clear();
				for (String item : subTypeList) {
					listBox_Subtype.addItem(item);
				}
				listBox_Subtype.setItemSelected(0, true);
				listBox_Subtype.onBrowserEvent(Event.getCurrentEvent());
			}
		});

		listBox_Subtype.addChangeListener(new ChangeListener() {
			public void onChange(Widget sender) {
				updateListBox();
			}

			private void updateListBox() {
				// General.showDebug("Starting: listBox_Subtype.updateListBox");
				int idx = listBox_Program.getSelectedIndex();
				if (idx < 0) {
					General.showError("Failed to get program");
					return;
				}
				String program = listBox_Program.getValue(idx);
				idx = listBox_Type.getSelectedIndex();
				if (idx < 0) {
					General.showError("Failed to get type");
					return;
				}
				String type = listBox_Type.getValue(idx);
				idx = listBox_Subtype.getSelectedIndex();
				if (idx < 0) {
					General.showError("Failed to get subType");
					return;
				}
				String subType = listBox_Subtype.getValue(idx);
				ArrayList<String> otherList = Classification.getOtherList(program, type, subType);
				listBox_Other.clear();
				for (String item : otherList) {
					listBox_Other.addItem(item);
				}
				listBox_Other.setItemSelected(0, true);
				// listBox_Other.onBrowserEvent(Event.getCurrentEvent()); // No
				// need to propagate
			}
		});
		formPanel.addFormHandler(fileFormHandler);
		submitButton.addClickListener(new ClickListener() {
			public void onClick(Widget sender) {
//				General.showWarning("Submit button thinks it's clicked (and does a GET instead of a POST) but does so on load of GWT module");
				formPanel.submit();
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
