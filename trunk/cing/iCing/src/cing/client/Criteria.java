package cing.client;

import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DecoratedTabPanel;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.VerticalPanel;

public class Criteria extends Composite {


	public Criteria() {

		final VerticalPanel verticalPanel = new VerticalPanel();
		initWidget(verticalPanel);
		final HTML html = new HTML(
				"<h1>Criteria for <A class=\"orange\">Poor</A>/<A class=\"red\">Bad</A></h1>");
		verticalPanel.add(html);
	    DecoratedTabPanel tabPanel = new DecoratedTabPanel();
	    tabPanel.setWidth("400px");
	    tabPanel.setAnimationEnabled(true);
		verticalPanel.add(tabPanel);

	    final FlexTable cingTable = new FlexTable();
	    tabPanel.add(cingTable, "<h2>CING</H2>", true);
	    final FlexTable wiTable = new FlexTable();
	    tabPanel.add(wiTable, "<h2>What If</H2>", true);

	    final CheckBox noneCheckBox = new CheckBox();
	    wiTable.setWidget(0, 0, noneCheckBox);
	    wiTable.getCellFormatter().setHorizontalAlignment(0, 0, HasHorizontalAlignment.ALIGN_CENTER);
	    wiTable.getFlexCellFormatter().setColSpan(0, 0, 5);
	    noneCheckBox.setText("none");
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
	    ramachandranPlotCheckBox.setText("Ramachandran plot");

	    final CheckBox janinPlotCheckBox = new CheckBox();
	    wiTable.setWidget(3, 0, janinPlotCheckBox);
	    janinPlotCheckBox.setChecked(true);
	    janinPlotCheckBox.setText("Janin plot");
	    
	    final TextBox bbTextBox_1 = new TextBox();
	    wiTable.setWidget(3, 2, bbTextBox_1);
	    wiTable.getCellFormatter().setHorizontalAlignment(3, 2, HasHorizontalAlignment.ALIGN_CENTER);
	    bbTextBox_1.setText("-1.2");
	    bbTextBox_1.setStyleName("red");
	    bbTextBox_1.setWidth("3em");
	    
	    final Label residueSigmas22Label = new Label("residue sigmas [-2,2]");
	    wiTable.setWidget(1, 4, residueSigmas22Label);

	    final Label occurancesInDbLabel = new Label("occurances in db [0-80]");
	    wiTable.setWidget(4, 4, occurancesInDbLabel);

	    final CheckBox backboneNormalityCheckBox = new CheckBox();
	    wiTable.setWidget(4, 0, backboneNormalityCheckBox);
	    backboneNormalityCheckBox.setChecked(true);
	    backboneNormalityCheckBox.setText("Backbone normality");

	    final TextBox textBox_4 = new TextBox();
	    wiTable.setWidget(3, 3, textBox_4);
	    wiTable.getCellFormatter().setHorizontalAlignment(3, 3, HasHorizontalAlignment.ALIGN_CENTER);
	    textBox_4.setStyleName("orange");
	    textBox_4.setText("-0.9");
	    textBox_4.setWidth("3em");

	    final Label residueSigmas22Label_1 = new Label("residue sigmas [-2,2]");
	    wiTable.setWidget(3, 4, residueSigmas22Label_1);

	    
	    final FlexTable pcTable = new FlexTable();
	    tabPanel.add(pcTable, "<h2>ProcheckNMR/Aqua</H2>", true);
 
	    final CheckBox nonePcCheckBox = new CheckBox();
	    pcTable.setWidget(0, 0, nonePcCheckBox);
	    pcTable.getCellFormatter().setHorizontalAlignment(0, 0, HasHorizontalAlignment.ALIGN_CENTER);
	    pcTable.getFlexCellFormatter().setColSpan(0, 0, 4);

	    final CheckBox includeIntraresidualContactsCheckBox = new CheckBox();
	    pcTable.setWidget(1, 0, includeIntraresidualContactsCheckBox);
	    includeIntraresidualContactsCheckBox.setChecked(true);
	    includeIntraresidualContactsCheckBox.setText("Include intra-residual contacts");

	    final Label noeCompletenessPerLabel = new Label("NOE completeness");
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

	    final Label perResidue0100Label = new Label("per residue [0,100%]");
	    pcTable.setWidget(2, 3, perResidue0100Label);

	    final ListBox listBox = new ListBox();
	    pcTable.setWidget(4, 0, listBox);
	    listBox.addItem("Standard");
	    listBox.addItem("Standard, no individual prochiral groups");
	    listBox.addItem("Standard, all individual prochiral groups");
	    listBox.addItem("Only amides and alpha protons");
	    listBox.addItem("Only amides");
	    listBox.addItem("All theoretically possible with NMR");
	    listBox.addItem("All non-hydrogens");

	    final Label observableAtomSetLabel = new Label("Observable atom set:");
	    pcTable.setWidget(3, 0, observableAtomSetLabel);
	    nonePcCheckBox.setText("none");
	 
	    
	    
	    final CheckBox checkBox = new CheckBox();
	    cingTable.setWidget(1, 0, checkBox);
	    checkBox.setChecked(true);
	    checkBox.setHTML("Omega");

	    final CheckBox checkBox_1 = new CheckBox();
	    cingTable.setWidget(2, 0, checkBox_1);
	    checkBox_1.setChecked(true);
	    checkBox_1.setHTML("Flag missing coordinates");

	    final TextBox textBox = new TextBox();
	    cingTable.setWidget(1, 1, textBox);
	    textBox.setStyleName("orange");
	    textBox.setText("15");
	    textBox.setWidth("3em");

	    final Label andLabel = new Label("and");
	    cingTable.setWidget(1, 2, andLabel);

	    final TextBox textBox_1 = new TextBox();
	    cingTable.setWidget(1, 3, textBox_1);
	    cingTable.getCellFormatter().setHorizontalAlignment(1, 3, HasHorizontalAlignment.ALIGN_CENTER);
	    textBox_1.setStylePrimaryName("red");
	    textBox_1.setText("20");
	    textBox_1.setWidth("3em");

	    final Label label = new Label("\u00B0");
	    cingTable.setWidget(1, 4, label);

	    final CheckBox checkBox_2 = new CheckBox();
	    cingTable.setWidget(0, 0, checkBox_2);
	    cingTable.getCellFormatter().setHorizontalAlignment(0, 0, HasHorizontalAlignment.ALIGN_CENTER);
	    cingTable.getFlexCellFormatter().setColSpan(0, 0, 5);
	    checkBox_2.setHTML("none");

		final Button saveButton = new Button();
		verticalPanel.add(saveButton);
		verticalPanel.setCellHorizontalAlignment(saveButton, HasHorizontalAlignment.ALIGN_CENTER);
		saveButton.setText("Save");
		// Return the content
	    tabPanel.ensureDebugId("criteriaTabPanel");		
	    tabPanel.selectTab(0);
	    }

}
