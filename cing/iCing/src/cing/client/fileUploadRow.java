package cing.client;

import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FileUpload;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.VerticalPanel;

public class fileUploadRow extends Composite {

//	 private final Message moreFileTypesDialogBox = new Message(
//			 null, Message.SHAKE, 0.5);
	
	public fileUploadRow() {

		final FormPanel formPanel = new FormPanel();
		formPanel.setEncoding(FormPanel.ENCODING_MULTIPART);
		formPanel.setMethod(FormPanel.METHOD_POST);
		initWidget(formPanel);

		VerticalPanel verticalPanel = new VerticalPanel();
		formPanel.add(verticalPanel); 
		verticalPanel.setSpacing(5);
		HorizontalPanel dialogPanel = new HorizontalPanel();
		verticalPanel.add(dialogPanel);
		dialogPanel.setSpacing(5);
//		final DialogBox moreFileTypesDialogBox = new DialogBox();
//		dialogPanel.add(moreFileTypesDialogBox);
		final HorizontalPanel horizontalPanel = new HorizontalPanel();
		verticalPanel.add(horizontalPanel);
		horizontalPanel.setSpacing(5);

		final CheckBox filepresentCheckBox = new CheckBox();
		horizontalPanel.add(filepresentCheckBox);
		filepresentCheckBox.setVisible(false);    

	    FileUpload fileUpload = new FileUpload();
		horizontalPanel.add(fileUpload);
		fileUpload.setTitle("choose file");
		fileUpload.setName("choose file");

		final ListBox listBox_FileType = new ListBox();
		horizontalPanel.add(listBox_FileType);
		listBox_FileType.addItem("Coordinate");
		listBox_FileType.setVisibleItemCount(1);

		final ListBox listBox_FileFormat = new ListBox();
		horizontalPanel.add(listBox_FileFormat);
		listBox_FileFormat.addItem("PDB");
		listBox_FileFormat.addItem("CYANA");
		listBox_FileFormat.addItem("IUPAC");
		listBox_FileFormat.setVisibleItemCount(1);

		final Button removeButton = new Button();
		horizontalPanel.add(removeButton);
		removeButton.setText("remove");

		final HTML egHTML = new HTML("<A HREF=\"example/1brv.tgz\">eg</A>");
		horizontalPanel.add(egHTML);
//		dialogPanel.setWidth("100%");
//		dialogPanel.setHorizontalAlignment(VerticalPanel.ALIGN_CENTER);
		// Set the contents of the Widget
//		dialogBox.setWidget(dialogPanel);		
	}
}
