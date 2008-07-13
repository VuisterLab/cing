package cing.client;

import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DialogBox;
import com.google.gwt.user.client.ui.FileUpload;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;
//import com.gwtsolutions.components.client.ui.Message;

public class fileUploadRow extends Composite {

//	 private final Message statusMessage = new Message(
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
		final DialogBox moreFileTypesDialogBox = new DialogBox();
		dialogPanel.add(moreFileTypesDialogBox);
		final HorizontalPanel horizontalPanel = new HorizontalPanel();
		verticalPanel.add(horizontalPanel);
		horizontalPanel.setSpacing(5);

		final CheckBox filepresentCheckBox = new CheckBox();
		horizontalPanel.add(filepresentCheckBox);
		filepresentCheckBox.setVisible(false);    

	    FileUpload fileUpload = new FileUpload();
		horizontalPanel.add(fileUpload);

		final ListBox listBox_1 = new ListBox();
		horizontalPanel.add(listBox_1);
		listBox_1.addItem("Coordinate");
		listBox_1.setVisibleItemCount(1);

		final ListBox listBox = new ListBox();
		horizontalPanel.add(listBox);
		listBox.addItem("PDB");
		listBox.addItem("CYANA");
		listBox.addItem("IUPAC");
		listBox.setVisibleItemCount(1);

		final Button submitButton = new Button();
		horizontalPanel.add(submitButton);
		submitButton.setEnabled(false);
		submitButton.setText("Submit");

		final Button removeButton = new Button();
		horizontalPanel.add(removeButton);
		removeButton.setText("remove");

		final HTML egHTML = new HTML("<A HREF=\"example/1brv.tgz\">eg</A>");
		horizontalPanel.add(egHTML);
//		dialogPanel.setWidth("100%");
//		dialogPanel.setHorizontalAlignment(VerticalPanel.ALIGN_CENTER);
		// Set the contents of the Widget
//		dialogBox.setWidget(dialogPanel);		
		Button closeButton = new Button("Close");
		dialogPanel.add(closeButton);		
		closeButton.addClickListener(new ClickListener() {
			public void onClick(Widget sender) {
				moreFileTypesDialogBox.hide();
			}
		});
		moreFileTypesDialogBox.setText("More file types to come soon.");
		moreFileTypesDialogBox.center();
		moreFileTypesDialogBox.show();
	}
}
