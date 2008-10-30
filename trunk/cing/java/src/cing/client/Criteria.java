package cing.client;

import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.DecoratedTabPanel;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

public class Criteria extends iCingView {

	public Criteria() {
		setState(iCing.CRITERIA_STATE);
		iCingConstants c = iCing.c;

		final VerticalPanel verticalPanel = new VerticalPanel();
		initWidget(verticalPanel);
		HorizontalPanel fp = new HorizontalPanel();
		fp.setSpacing(5);
		final Label html_1 = new Label( c.Criteria_for() );
		final Label html_2 = new Label( c.Poor() );
		final Label html_3 = new Label( "/" );
		final Label html_4 = new Label( c.Bad());
		fp.add(html_1);
		fp.add(html_2);
//		html_2.setStyleName("h1-orange"); fails!
		fp.add(html_3);
		fp.add(html_4);
		html_1.setStylePrimaryName("h1");
		html_2.setStylePrimaryName("h1");
		html_3.setStylePrimaryName("h1");
		html_4.setStylePrimaryName("h1");
		html_2.addStyleDependentName("orange");
		html_4.addStyleDependentName("red");
		
		verticalPanel.add(fp);
		DecoratedTabPanel tabPanel = new DecoratedTabPanel();
//		tabPanel.setWidth(iCing.widthMenu+"px"); // free is more elegant.
		tabPanel.setAnimationEnabled(true);
		verticalPanel.add(tabPanel);

		final FlexTable cingTable = new FlexTable();
		cingTable.setTitle(c.CING());
		tabPanel.add(cingTable, c.CING(), true);
		final FlexTable wiTable = new FlexTable();
		wiTable.setTitle("What If");
		tabPanel.add(wiTable, "What If", true);

		final CheckBox noneWiCheckBox = new CheckBox();
		wiTable.setWidget(0, 0, noneWiCheckBox);
		wiTable.getCellFormatter().setHorizontalAlignment(0, 0, HasHorizontalAlignment.ALIGN_CENTER);
		wiTable.getFlexCellFormatter().setColSpan(0, 0, 5);
		noneWiCheckBox.setText(c.none());
		final TextBox ramaTextBox_1 = new TextBox();
		wiTable.setWidget(1, 2, ramaTextBox_1);
		wiTable.getCellFormatter().setHorizontalAlignment(1, 2, HasHorizontalAlignment.ALIGN_CENTER);
		ramaTextBox_1.setStyleName("red");
		ramaTextBox_1.setText("-1.3");
		ramaTextBox_1.setWidth("3em");
		final TextBox ramaTextBox_2 = new TextBox();
		wiTable.setWidget(1, 3, ramaTextBox_2);
		wiTable.getCellFormatter().setHorizontalAlignment(1, 3, HasHorizontalAlignment.ALIGN_CENTER);
		ramaTextBox_2.setStyleName("orange");
		ramaTextBox_2.setText("-1.0");
		ramaTextBox_2.setWidth("3em");

		final TextBox janinTextBox_1 = new TextBox();
		wiTable.setWidget(4, 2, janinTextBox_1);
		wiTable.getCellFormatter().setHorizontalAlignment(4, 2, HasHorizontalAlignment.ALIGN_CENTER);
		janinTextBox_1.setText("3.0");
		janinTextBox_1.setStyleName("red");
		janinTextBox_1.setWidth("3em");
		final TextBox janinTextBox_2 = new TextBox();
		wiTable.setWidget(4, 3, janinTextBox_2);
		wiTable.getCellFormatter().setHorizontalAlignment(4, 3, HasHorizontalAlignment.ALIGN_CENTER);
		janinTextBox_2.setStyleName("orange");
		janinTextBox_2.setText("-0.9");
		janinTextBox_2.setWidth("3em");

		final CheckBox ramachandranPlotCheckBox = new CheckBox();
		wiTable.setWidget(1, 0, ramachandranPlotCheckBox);
		ramachandranPlotCheckBox.setChecked(true);
		ramachandranPlotCheckBox.setText("Ramachandran " + c.plot());

		final CheckBox janinPlotCheckBox = new CheckBox();
		wiTable.setWidget(3, 0, janinPlotCheckBox);
		janinPlotCheckBox.setChecked(true);
		janinPlotCheckBox.setText("Janin " + c.plot());

		final TextBox bbTextBox_1 = new TextBox();
		wiTable.setWidget(3, 2, bbTextBox_1);
		wiTable.getCellFormatter().setHorizontalAlignment(3, 2, HasHorizontalAlignment.ALIGN_CENTER);
		bbTextBox_1.setText("-1.2");
		bbTextBox_1.setStyleName("red");
		bbTextBox_1.setWidth("3em");

		final Label residueSigmas22Label = new Label(c.residue_sigma() + " [-2,2]");
		wiTable.setWidget(1, 4, residueSigmas22Label);

		final Label occurancesInDbLabel = new Label(c.occurances_in() + " [0-80]");
		wiTable.setWidget(4, 4, occurancesInDbLabel);

		final CheckBox backboneNormalityCheckBox = new CheckBox();
		wiTable.setWidget(4, 0, backboneNormalityCheckBox);
		backboneNormalityCheckBox.setChecked(true);
		backboneNormalityCheckBox.setText(c.Backbone_norm());

		final TextBox textBox_4 = new TextBox();
		wiTable.setWidget(3, 3, textBox_4);
		wiTable.getCellFormatter().setHorizontalAlignment(3, 3, HasHorizontalAlignment.ALIGN_CENTER);
		textBox_4.setStyleName("orange");
		textBox_4.setText("-0.9");
		textBox_4.setWidth("3em");

		final Label residueSigmas22Label_1 = new Label(c.residue_sigma() + " [-2,2]");
		wiTable.setWidget(3, 4, residueSigmas22Label_1);

		final FlexTable pcTable = new FlexTable();
		pcTable.setTitle("ProcheckNMR/Aqua");
		tabPanel.add(pcTable, "ProcheckNMR/Aqua", true);

		final CheckBox nonePcCheckBox = new CheckBox();
		pcTable.setWidget(0, 0, nonePcCheckBox);
		pcTable.getCellFormatter().setHorizontalAlignment(0, 0, HasHorizontalAlignment.ALIGN_CENTER);
		pcTable.getFlexCellFormatter().setColSpan(0, 0, 4);

		final CheckBox includeIntraresidualContactsCheckBox = new CheckBox();
		pcTable.setWidget(1, 0, includeIntraresidualContactsCheckBox);
		includeIntraresidualContactsCheckBox.setChecked(true);
		includeIntraresidualContactsCheckBox.setText(c.Include_intra());

		final Label noeCompletenessPerLabel = new Label(c.NOE_completen());
		pcTable.setWidget(2, 0, noeCompletenessPerLabel);

		final TextBox textBox_2 = new TextBox();
		pcTable.setWidget(2, 1, textBox_2);
		textBox_2.setVisibleLength(3);
		textBox_2.setMaxLength(3);
		textBox_2.setStyleName("red");
		textBox_2.setText("10");
		textBox_2.setWidth("3em");

		final TextBox textBox_3 = new TextBox();
		pcTable.setWidget(2, 2, textBox_3);
		textBox_3.setVisibleLength(3);
		textBox_3.setStyleName("orange");
		textBox_3.setText("20");
		textBox_3.setWidth("3em");

		final Label perResidue0100Label = new Label(c.per_residue() + "[0,100%]");
		pcTable.setWidget(2, 3, perResidue0100Label);

		final ListBox listBox = new ListBox();
		pcTable.setWidget(4, 0, listBox);

		listBox.addItem(c.Standard());
		listBox.addItem(c.Standard_no());
		listBox.addItem(c.Standard_all());
		listBox.addItem(c.Only_amides_a());
		listBox.addItem(c.Only_amides());
		listBox.addItem(c.All_theoretic());
		listBox.addItem(c.All_non_hydro());

		final Label observableAtomSetLabel = new Label(c.Observable_at());
		pcTable.setWidget(3, 0, observableAtomSetLabel);
		nonePcCheckBox.setText(c.none());

		final CheckBox checkBox = new CheckBox();
		cingTable.setWidget(1, 0, checkBox);
		checkBox.setEnabled(true);
		checkBox.setChecked(true);
		checkBox.setHTML("Omega");

		final CheckBox checkBox_1 = new CheckBox();
		cingTable.setWidget(2, 0, checkBox_1);
		checkBox_1.setChecked(true);
		checkBox_1.setHTML(c.Flag_missing());

		final TextBox textBox = new TextBox();
		cingTable.setWidget(1, 1, textBox);
		textBox.setStyleName("orange");
		textBox.setText("15");
		textBox.setWidth("3em");

		final Label andLabel = new Label(c.and());
		cingTable.setWidget(1, 2, andLabel);

		final TextBox textBox_1 = new TextBox();
		cingTable.setWidget(1, 3, textBox_1);
		cingTable.getCellFormatter().setHorizontalAlignment(1, 3, HasHorizontalAlignment.ALIGN_CENTER);
		textBox_1.setStylePrimaryName("red");
		textBox_1.setText("20");
		textBox_1.setWidth("3em");

		final Label label = new Label("\u00B0");
		cingTable.setWidget(1, 4, label);

		final CheckBox noneCingCheckBox = new CheckBox();
		cingTable.setWidget(0, 0, noneCingCheckBox);
		noneCingCheckBox.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				Utils.setEnabledAllInRowsButFirst(cingTable, ! noneCingCheckBox.isChecked());
			}
		});
		nonePcCheckBox.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				Utils.setEnabledAllInRowsButFirst(pcTable, ! nonePcCheckBox.isChecked());
			}
		});
		noneWiCheckBox.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				Utils.setEnabledAllInRowsButFirst(wiTable, ! noneWiCheckBox.isChecked());
			}
		});
		cingTable.getCellFormatter().setHorizontalAlignment(0, 0, HasHorizontalAlignment.ALIGN_CENTER);
		cingTable.getFlexCellFormatter().setColSpan(0, 0, 5);
		noneCingCheckBox.setHTML(c.none());

		final Button nextButton = new Button();
		nextButton.setText(c.Next());
		nextButton.addClickListener(new ClickListener() {
			public void onClick(final Widget sender) {
				icing.onHistoryChanged(iCing.OPTIONS_STATE);					
			}
		});	
		verticalPanel.add(nextButton);
		nextButton.setTitle("Goto CING run options.");
		verticalPanel.setCellHorizontalAlignment(nextButton, HasHorizontalAlignment.ALIGN_CENTER);
		
		
		// Return the content
		tabPanel.ensureDebugId("criteriaTabPanel");
		tabPanel.selectTab(0);
	}	
}
