package cing.client;

import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.PushButton;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;

public class Options extends iCingView {

//	static final private Random r = new Random();
	private Label accessKeyLabelValue;
	private TextBox textBoxEnsemble;
	private TextBox textBoxResidue;
	
	int i = 0;
	final int optionVerbosityIdx = i++;
	final int optionImagerIdx = i++;
	final int optionResidueIdx = i++;
	final int optionModelIdx = i++;
//	final int optionAccessIdx = i++;
    final ListBox listBoxVerbosity = new ListBox();
    final CheckBox createImageryCheckBox = new CheckBox();

	
	public Options() {
		super();
	}
	
	
	public void setIcing(iCing icing) {
        super.setIcing(icing);
		final iCing icingShadow = icing;		
		setState(iCing.OPTIONS_STATE);
		
		final Label html_1 = new Label( c.Options() );
		html_1.setStylePrimaryName("h1");
		verticalPanel.add(html_1);
		verticalPanel.add(decPanel);
		
		final FlexTable flexTable = new FlexTable();
		flexTable.setCellSpacing(5);
		flexTable.setCellPadding(5);
		decPanel.add(flexTable);

		
		final Label verbosityLabel = new Label(c.Verbosity());
		flexTable.setWidget(optionVerbosityIdx, 0, verbosityLabel);
		
		listBoxVerbosity.addItem(c.Nothing(),"0");
		listBoxVerbosity.addItem(c.Error(),"1");
		listBoxVerbosity.addItem(c.Warning(),"2");
		listBoxVerbosity.addItem(c.Output(),"3");
		listBoxVerbosity.addItem(c.Detail(),"4");		
		listBoxVerbosity.addItem(c.Debug(),"9"); // refuse to give up extra space between 4 and 9 for coding convenience here.
		listBoxVerbosity.setVisibleItemCount(1);
		flexTable.setWidget(optionVerbosityIdx, 1, listBoxVerbosity);
		listBoxVerbosity.setSelectedIndex(3);
		if ( Settings.DO_DEBUG ) {
		    listBoxVerbosity.setSelectedIndex(5);
		}
		
		flexTable.setWidget(optionImagerIdx, 0, createImageryCheckBox);
		flexTable.getFlexCellFormatter().setColSpan(1, 0, 2);
		createImageryCheckBox.setText(c.Imagery_repor());
		createImageryCheckBox.setChecked(true);
		
		final Label residuesLabel = new Label(c.Residues());
		flexTable.setWidget(optionResidueIdx, 0, residuesLabel);

		textBoxResidue = new TextBox();
		flexTable.setWidget(optionResidueIdx, 1, textBoxResidue);
		textBoxResidue.setWidth("100%");
//		textBoxResidue.setEnabled(false);
		textBoxResidue.setText(""); // space will be stripped by servlet.
		
		final Label egResidue175177189Label = new Label(c.E_g_() + " 175,177-189");
		flexTable.setWidget(optionResidueIdx, 2, egResidue175177189Label);

		final Label ensembleModelsLabel = new Label(c.Ensemble_mode() + ":");
		flexTable.setWidget(optionModelIdx, 0, ensembleModelsLabel);

		textBoxEnsemble = new TextBox();
//		textBoxEnsemble.setEnabled(false);
		flexTable.setWidget(optionModelIdx, 1, textBoxEnsemble);
		textBoxEnsemble.setWidth("100%");
//		textBoxEnsemble.setEnabled(false);
		textBoxEnsemble.setText("");

		final Label egModel219Label = new Label(c.E_g_() + " 0,3-8");
		flexTable.setWidget(optionModelIdx, 2, egModel219Label);

//		final Label accessKeyLabel = new Label(c.Access_key());
//		flexTable.setWidget(optionAccessIdx, 0, accessKeyLabel);

		// Added panel for getting better spacing?
		final HorizontalPanel horizontalPanel = new HorizontalPanel();
//		flexTable.setWidget(optionAccessIdx, 1, horizontalPanel);
		horizontalPanel.setSpacing(5);

		accessKeyLabelValue = new Label();
		horizontalPanel.add(accessKeyLabelValue);
//		accessKeyLabelValue.setVisibleLength(accessKeyLength+1); // depending on font the last char sometimes doesn't show.

//		final Label az096Label = new Label("[a-Z0-9]{6}");
//		horizontalPanel.add(az096Label);

		final PushButton regeneratePushButton = new PushButton("Up text", "Down text");
		regeneratePushButton.getDownFace().setHTML(c.Randomizing());
		regeneratePushButton.getUpFace().setHTML(c.Regenerate());
//		flexTable.setWidget(optionAccessIdx, 2, regeneratePushButton);
		regeneratePushButton.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				generateAccessKey();
			}
		});
		regeneratePushButton.setHTML(c.Randomizing());
		regeneratePushButton.setText(c.Regenerate());
		regeneratePushButton.setEnabled(false);
//		generateAccessKey(); 
				
        final HorizontalPanel horizontalPanelBackNext = new HorizontalPanel();
        horizontalPanelBackNext.setSpacing(iCing.margin);
        verticalPanel.add(horizontalPanelBackNext);
        final Button backButton = new Button();
        final Button nextButton = new Button();
        horizontalPanelBackNext.add(backButton);
        backButton.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                icingShadow.onHistoryChanged(iCing.CRITERIA_STATE);
//                History.back();
            }
        });
        backButton.setText(c.Back());
        horizontalPanelBackNext.add(backButton);
        horizontalPanelBackNext.add(nextButton);

        nextButton.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                icingShadow.onHistoryChanged(iCing.RUN_STATE);
            }
        });
        nextButton.setText(c.Next());
        nextButton.setTitle(c.Submit_to_CING_s());
	}
	
	
	protected void generateAccessKey() { 
		/** Not used at the moment... */		
		String new_access = iCing.getNewAccessKey();
		accessKeyLabelValue.setText(new_access);
		iCing.currentAccessKey = new_access;
		GenClient.showDebug("Set access key to: " + iCing.currentAccessKey);
	}

    public String getVerbosity() {
        return Utils.getListBoxItemValue(listBoxVerbosity);
    }

    public String getImagery() {
        return Boolean.toString( createImageryCheckBox.isChecked() );
    }

    public String getResidue() {
        return textBoxResidue.getText();
    }

	public String getEnsemble() {
		return textBoxEnsemble.getText();
	}	
}
