package cing.client;

import com.google.gwt.user.client.Random;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.PushButton;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;

public class Options extends Composite {

//	static final private Random r = new Random();
	private Label accessKeyLabelValue;
	private TextBox textBox_1;
	private TextBox textBox;

	public int accessKeyLength = 6;
	
	iCingConstants c = iCing.c;

	public Options() {

		final FlexTable flexTable = new FlexTable();
		initWidget(flexTable);
		flexTable.setCellSpacing(0);
		flexTable.setCellPadding(5);

		final Label residuesLabel = new Label(c.Residues());
		flexTable.setWidget(0, 0, residuesLabel);

		textBox = new TextBox();
		flexTable.setWidget(0, 1, textBox);
		textBox.setWidth("100%");

		final Label eg175177189Label = new Label(c.E_g_() + " 175,177-189");
		flexTable.setWidget(0, 2, eg175177189Label);

		final Label ensembleModelsLabel = new Label(c.Ensemble_mode() + ":");
		flexTable.setWidget(1, 0, ensembleModelsLabel);

		textBox_1 = new TextBox();
		flexTable.setWidget(1, 1, textBox_1);
		textBox_1.setWidth("100%");

		final Label eg219Label = new Label(c.E_g_() + " 2-19");
		flexTable.setWidget(1, 2, eg219Label);

		final Label accessKeyLabel = new Label(c.Access_key());
		flexTable.setWidget(2, 0, accessKeyLabel);

		final HorizontalPanel horizontalPanel = new HorizontalPanel();
		flexTable.setWidget(2, 1, horizontalPanel);
		horizontalPanel.setSpacing(5);

		accessKeyLabelValue = new Label();
		horizontalPanel.add(accessKeyLabelValue);
//		accessKeyLabelValue.setVisibleLength(accessKeyLength+1); // depending on font the last char sometimes doesn't show.

//		final Label az096Label = new Label("[a-Z0-9]{6}");
//		horizontalPanel.add(az096Label);

		final PushButton regeneratePushButton = new PushButton("Up text", "Down text");
		regeneratePushButton.getDownFace().setHTML(c.Randomizing());
		regeneratePushButton.getUpFace().setHTML(c.Regenerate());
		flexTable.setWidget(2, 2, regeneratePushButton);
		regeneratePushButton.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				generateAccessKey();
			}
		});
		regeneratePushButton.setHTML(c.Randomizing());
		regeneratePushButton.setText(c.Regenerate());
		regeneratePushButton.setEnabled(false);
		generateAccessKey();
	}

	protected void generateAccessKey() {
		String allowedCharacters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
		String new_access = "";
		for (int i = 1; i <= accessKeyLength; i++) {
			int idxChar = Random.nextInt( allowedCharacters.length() ); // equal chance for A as for others.
			new_access = new_access + allowedCharacters.charAt(idxChar);
			// TODO: generate on server with cross check on availability...
		}
		accessKeyLabelValue.setText(new_access);
		iCing.currentAccessKey = new_access;
	}

	public TextBox getTextBox() {
		return textBox;
	}

	public TextBox getTextBox_1() {
		return textBox_1;
	}
}
