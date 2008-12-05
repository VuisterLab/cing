package cing.client;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;

import com.google.gwt.user.client.History;
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
import com.google.gwt.user.client.ui.Widget;

public class Criteria extends iCingView {

    private CheckBox noneCingCheckBox;
    private CheckBox nonePcCheckBox;
    private CheckBox noneWiCheckBox;
    private TextBox ramaTextBoxBad;
    private TextBox ramaTextBoxPoor;

    int j = 0;
    final int rowIdxCingNone = j++;
    final int rowIdxCingOmega = j++;
    final int rowIdxCingMissingCoord = j++;
    final int rowIdxCingDrMax = j++;
    final int rowIdxCingDrRms = j++;
    final int rowIdxCingAcMax = j++;
    final int rowIdxCingAcRms = j++;
    int l = 0;
    final int rowIdxWiNone = l++;
    final int rowIdxWiRama = l++;
    final int rowIdxWiJanin = l++;
    final int rowIdxWiBb = l++;
    int i = 0;
    final int rowIdxPcNone = i++;
    final int rowIdxPcGfactor = i++;
    final int rowIdxPcIntra = i++;
    final int rowIdxPcObserv = i++;
    final int rowIdxPcComple = i++;
    private TextBox textBoxOmegaPoor;
    private TextBox textBoxOmegaBad;
    private TextBox textBoxDrMaxPoor;
    private TextBox textBoxDrMaxBad;
    private CheckBox checkBoxDrMax;
    private TextBox textBoxDrRmsPoor;
    private TextBox textBoxDrRmsBad;
    private CheckBox checkBoxDrRms;
    private TextBox textBoxAcMaxPoor;
    private TextBox textBoxAcMaxBad;
    private CheckBox checkBoxAcMax;
    private TextBox textBoxAcRmsPoor;
    private TextBox textBoxAcRmsBad;
    private CheckBox checkBoxAcRms;
    private CheckBox checkBoxMissingCoordinates;
    private CheckBox checkBoxOmega;
    private TextBox bbTextBoxBad;
    private TextBox bbTextBoxPoor;
    private CheckBox ramachandranPlotCheckBox;
    private CheckBox janinPlotCheckBox;
    private TextBox janinTextBoxBad;
    private CheckBox backboneNormalityCheckBox;
    private TextBox janinTextBoxPoor;
    private TextBox textBoxGfactorPoor;
    private TextBox textBoxGfactorBad;
    private CheckBox includeIntraresidualContactsCheckBox;
    private CheckBox noeCompletenessCheckBox;
    private TextBox textBoxComplBad;
    private TextBox textBoxComplPoor;
    private ListBox listBoxObs;
    private CheckBox gFactorCheckBox;

    public Criteria() {
        super();
    }

    public void setIcing(iCing icing) {
        super.setIcing(icing);
        final iCing icingShadow = icing;
        setState(iCing.CRITERIA_STATE);
        iCingConstants c = iCing.c;

        HorizontalPanel fp = new HorizontalPanel();
        fp.setSpacing(5);
        final Label html_1 = new Label(c.Criteria_for());
        final Label html_2 = new Label(c.Poor());
        final Label html_3 = new Label("/");
        final Label html_4 = new Label(c.Bad());
        fp.add(html_1);
        fp.add(html_2);
        // html_2.setStyleName("h1-orange"); fails!
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
        // tabPanel.setWidth(iCing.widthMenu+"px"); // free is more elegant.
        tabPanel.setAnimationEnabled(true);
        verticalPanel.add(tabPanel);

        final FlexTable cingTable = new FlexTable();
        cingTable.setTitle(c.CING());
        tabPanel.add(cingTable, c.CING(), true);
        final FlexTable wiTable = new FlexTable();
        wiTable.setTitle("What If");
        tabPanel.add(wiTable, "What If", true);

        noneWiCheckBox = new CheckBox();
        wiTable.setWidget(rowIdxWiNone, 0, noneWiCheckBox);
        wiTable.getCellFormatter().setHorizontalAlignment(rowIdxWiNone, 0, HasHorizontalAlignment.ALIGN_CENTER);
        wiTable.getFlexCellFormatter().setColSpan(rowIdxWiNone, 0, 5);
        noneWiCheckBox.setText(c.none());
        ramaTextBoxBad = new TextBox();
        wiTable.setWidget(rowIdxWiRama, 2, ramaTextBoxBad);
        wiTable.getCellFormatter().setHorizontalAlignment(rowIdxWiRama, 2, HasHorizontalAlignment.ALIGN_CENTER);
        ramaTextBoxBad.setStyleName("red");
        ramaTextBoxBad.setText("-1.3");
        ramaTextBoxBad.setWidth("3em");
        ramaTextBoxPoor = new TextBox();
        wiTable.setWidget(rowIdxWiRama, 3, ramaTextBoxPoor);
        wiTable.getCellFormatter().setHorizontalAlignment(rowIdxWiRama, 3, HasHorizontalAlignment.ALIGN_CENTER);
        ramaTextBoxPoor.setStyleName("orange");
        ramaTextBoxPoor.setText("-1.0");
        ramaTextBoxPoor.setWidth("3em");

        bbTextBoxBad = new TextBox();
        wiTable.setWidget(rowIdxWiBb, 2, bbTextBoxBad);
        wiTable.getCellFormatter().setHorizontalAlignment(rowIdxWiBb, 2, HasHorizontalAlignment.ALIGN_RIGHT);
        bbTextBoxBad.setText("3.0");
        bbTextBoxBad.setStyleName("red");
        bbTextBoxBad.setWidth("3em");

        bbTextBoxPoor = new TextBox();
        wiTable.setWidget(rowIdxWiBb, 3, bbTextBoxPoor);
        wiTable.getCellFormatter().setHorizontalAlignment(rowIdxWiBb, 3, HasHorizontalAlignment.ALIGN_CENTER);
        bbTextBoxPoor.setText("10.0");
        bbTextBoxPoor.setStyleName("orange");
        bbTextBoxPoor.setWidth("3em");

        ramachandranPlotCheckBox = new CheckBox();
        wiTable.setWidget(rowIdxWiRama, 0, ramachandranPlotCheckBox);
        ramachandranPlotCheckBox.setChecked(true);
        ramachandranPlotCheckBox.setText("Ramachandran " + c.plot());
        ramachandranPlotCheckBox.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                Utils.setEnabledAllInColumnsButFirst(wiTable, rowIdxWiRama, ramachandranPlotCheckBox.isChecked());
            }
        });

        janinPlotCheckBox = new CheckBox();
        wiTable.setWidget(rowIdxWiJanin, 0, janinPlotCheckBox);
        janinPlotCheckBox.setChecked(true);
        janinPlotCheckBox.setText("Janin " + c.plot());
        janinPlotCheckBox.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                Utils.setEnabledAllInColumnsButFirst(wiTable, rowIdxWiJanin, janinPlotCheckBox.isChecked());
            }
        });

        janinTextBoxBad = new TextBox();
        wiTable.setWidget(rowIdxWiJanin, 2, janinTextBoxBad);
        wiTable.getCellFormatter().setHorizontalAlignment(rowIdxWiBb, 2, HasHorizontalAlignment.ALIGN_CENTER);
        janinTextBoxBad.setText("-1.2");
        janinTextBoxBad.setStyleName("red");
        janinTextBoxBad.setWidth("3em");

        final Label residueSigmas22Label = new Label(c.residue_sigma() + " [-2,2]");
        wiTable.setWidget(rowIdxWiRama, 4, residueSigmas22Label);

        final Label occurancesInDbLabel = new Label(c.occurances_in() + " [0-80]");
        wiTable.setWidget(rowIdxWiBb, 4, occurancesInDbLabel);

        backboneNormalityCheckBox = new CheckBox();
        wiTable.setWidget(rowIdxWiBb, 0, backboneNormalityCheckBox);
        backboneNormalityCheckBox.setChecked(true);
        backboneNormalityCheckBox.setText(c.Backbone_norm());
        backboneNormalityCheckBox.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                Utils.setEnabledAllInColumnsButFirst(wiTable, 4, backboneNormalityCheckBox.isChecked());
            }
        });

        janinTextBoxPoor = new TextBox();
        wiTable.setWidget(rowIdxWiJanin, 3, janinTextBoxPoor);
        wiTable.getCellFormatter().setHorizontalAlignment(3, 3, HasHorizontalAlignment.ALIGN_CENTER);
        janinTextBoxPoor.setStyleName("orange");
        janinTextBoxPoor.setText("-0.9");
        janinTextBoxPoor.setWidth("3em");

        final Label residueSigmas22Label_1 = new Label(c.residue_sigma() + " [-2,2]");
        wiTable.setWidget(rowIdxWiJanin, 4, residueSigmas22Label_1);

        final FlexTable pcTable = new FlexTable();
        pcTable.setTitle("ProcheckNMR/Aqua");
        tabPanel.add(pcTable, "ProcheckNMR/Aqua", true);

        nonePcCheckBox = new CheckBox();
        pcTable.setWidget(rowIdxPcNone, 0, nonePcCheckBox);
        pcTable.getCellFormatter().setHorizontalAlignment(rowIdxPcNone, 0, HasHorizontalAlignment.ALIGN_CENTER);
        pcTable.getFlexCellFormatter().setColSpan(rowIdxPcNone, 0, 4);

        // PC G factor row
        textBoxGfactorPoor = new TextBox();
        pcTable.setWidget(rowIdxPcGfactor, 2, textBoxGfactorPoor);
        textBoxGfactorPoor.setStyleName("orange");
        textBoxGfactorPoor.setText("-1.0");
        textBoxGfactorPoor.setWidth("3em");
        textBoxGfactorBad = new TextBox();
        pcTable.setWidget(rowIdxPcGfactor, 1, textBoxGfactorBad);
        pcTable.getCellFormatter().setHorizontalAlignment(rowIdxPcGfactor, 3, HasHorizontalAlignment.ALIGN_LEFT);
        textBoxGfactorBad.setStylePrimaryName("red");
        textBoxGfactorBad.setText("-1.3");
        textBoxGfactorBad.setWidth("3em");
        @SuppressWarnings("unused")
        final Label gFactorLimitsLabel = new Label("[-99,99]");
//        pcTable.setWidget(rowIdxPcGfactor, 3, gFactorLimitsLabel);
        includeIntraresidualContactsCheckBox = new CheckBox();
        pcTable.setWidget(rowIdxPcIntra, 0, includeIntraresidualContactsCheckBox);
        includeIntraresidualContactsCheckBox.setChecked(true);
        includeIntraresidualContactsCheckBox.setText(c.Include_intra());

        noeCompletenessCheckBox = new CheckBox();
        pcTable.setWidget(rowIdxPcComple, 0, noeCompletenessCheckBox);
        noeCompletenessCheckBox.setChecked(true);
        noeCompletenessCheckBox.setText(c.NOE_completen() + " " + c.per_residue());
        noeCompletenessCheckBox.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                Utils.setEnabledAllInColumnsButFirst(pcTable, rowIdxPcComple, noeCompletenessCheckBox.isChecked());
            }
        });
        gFactorCheckBox = new CheckBox();
        pcTable.setWidget(rowIdxPcGfactor, 0, gFactorCheckBox);
        gFactorCheckBox.setChecked(true);
        gFactorCheckBox.setText(c.gFactor());
        gFactorCheckBox.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                Utils.setEnabledAllInColumnsButFirst(pcTable, rowIdxPcGfactor, gFactorCheckBox.isChecked());
            }
        });

        textBoxComplBad = new TextBox();
        pcTable.setWidget(rowIdxPcComple, 1, textBoxComplBad);
        textBoxComplBad.setVisibleLength(3);
        textBoxComplBad.setMaxLength(3);
        textBoxComplBad.setStyleName("red");
        textBoxComplBad.setText("10");
        textBoxComplBad.setWidth("3em");

        textBoxComplPoor = new TextBox();
        pcTable.setWidget(rowIdxPcComple, 2, textBoxComplPoor);
        textBoxComplPoor.setVisibleLength(3);
        textBoxComplPoor.setStyleName("orange");
        textBoxComplPoor.setText("20");
        textBoxComplPoor.setWidth("3em");
        final Label per0100Label = new Label("[0,100%]");
        pcTable.setWidget(rowIdxPcComple, 3, per0100Label);

        listBoxObs = new ListBox();
        pcTable.setWidget(rowIdxPcObserv, 1, listBoxObs);
        pcTable.getFlexCellFormatter().setColSpan(rowIdxPcObserv, 1, 2);

        listBoxObs.addItem(c.Standard());
        listBoxObs.addItem(c.Standard_no());
        listBoxObs.addItem(c.Standard_all());
        listBoxObs.addItem(c.Only_amides_a());
        listBoxObs.addItem(c.Only_amides());
        listBoxObs.addItem(c.All_theoretic());
        listBoxObs.addItem(c.All_non_hydro());
        listBoxObs.setWidth("6em");
        final Label observableAtomSetLabel = new Label(c.Observable_at());
        pcTable.setWidget(rowIdxPcObserv, 0, observableAtomSetLabel);
        nonePcCheckBox.setText(c.none());

        checkBoxOmega = new CheckBox();
        cingTable.setWidget(rowIdxCingOmega, 0, checkBoxOmega);
        checkBoxOmega.setEnabled(true);
        checkBoxOmega.setChecked(true);
        checkBoxOmega.setHTML("Omega");
        checkBoxOmega.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                Utils.setEnabledAllInColumnsButFirst(cingTable, 1, checkBoxOmega.isChecked());
            }
        });
        textBoxOmegaPoor = new TextBox();
        cingTable.setWidget(rowIdxCingOmega, 1, textBoxOmegaPoor);
        textBoxOmegaPoor.setStyleName("orange");
        textBoxOmegaPoor.setText("15");
        textBoxOmegaPoor.setWidth("3em");
        final Label andLabelOmega = new Label(c.and());
        cingTable.setWidget(rowIdxCingOmega, 2, andLabelOmega);
        textBoxOmegaBad = new TextBox();
        cingTable.setWidget(rowIdxCingOmega, 3, textBoxOmegaBad);
        cingTable.getCellFormatter().setHorizontalAlignment(rowIdxCingOmega, 3, HasHorizontalAlignment.ALIGN_CENTER);
        textBoxOmegaBad.setStylePrimaryName("red");
        textBoxOmegaBad.setText("20");
        textBoxOmegaBad.setWidth("3em");
        final Label labelDegreeOmega = new Label("\u00B0");
        cingTable.setWidget(rowIdxCingOmega, 4, labelDegreeOmega);

        textBoxDrMaxPoor = new TextBox();
        cingTable.setWidget(rowIdxCingDrMax, 1, textBoxDrMaxPoor);
        textBoxDrMaxPoor.setStyleName("orange");
        textBoxDrMaxPoor.setText("0.1");
        textBoxDrMaxPoor.setWidth("3em");
        textBoxDrMaxBad = new TextBox();
        final Label andLabelDr = new Label(c.and());
        cingTable.setWidget(rowIdxCingDrMax, 2, andLabelDr);
        cingTable.setWidget(rowIdxCingDrMax, 3, textBoxDrMaxBad);
        cingTable.getCellFormatter().setHorizontalAlignment(rowIdxCingDrMax, 3, HasHorizontalAlignment.ALIGN_CENTER);
        textBoxDrMaxBad.setStylePrimaryName("red");
        textBoxDrMaxBad.setText("0.3");
        textBoxDrMaxBad.setWidth("3em");
        final Label labelAng = new Label("\u00C5");
        cingTable.setWidget(rowIdxCingDrMax, 4, labelAng);
        checkBoxDrMax = new CheckBox();
        cingTable.setWidget(rowIdxCingDrMax, 0, checkBoxDrMax);
        checkBoxDrMax.setChecked(true);
        checkBoxDrMax.setHTML(c.Maximum_violatio());
        textBoxDrRmsPoor = new TextBox();
        cingTable.setWidget(rowIdxCingDrRms, 1, textBoxDrRmsPoor);
        textBoxDrRmsPoor.setStyleName("orange");
        textBoxDrRmsPoor.setText("0.1");
        textBoxDrRmsPoor.setWidth("3em");
        textBoxDrRmsBad = new TextBox();
        final Label andLabelDrRms = new Label(c.and());
        cingTable.setWidget(rowIdxCingDrRms, 2, andLabelDrRms);
        cingTable.setWidget(rowIdxCingDrRms, 3, textBoxDrRmsBad);
        cingTable.getCellFormatter().setHorizontalAlignment(rowIdxCingDrRms, 3, HasHorizontalAlignment.ALIGN_CENTER);
        textBoxDrRmsBad.setStylePrimaryName("red");
        textBoxDrRmsBad.setText("0.3");
        textBoxDrRmsBad.setWidth("3em");
        final Label labelAngDrRms = new Label("\u00C5");
        cingTable.setWidget(rowIdxCingDrRms, 4, labelAngDrRms);
        checkBoxDrRms = new CheckBox();
        cingTable.setWidget(rowIdxCingDrRms, 0, checkBoxDrRms);
        checkBoxDrRms.setChecked(true);
        checkBoxDrRms.setHTML(c.Rms_violatio());
        textBoxAcMaxPoor = new TextBox();
        cingTable.setWidget(rowIdxCingAcMax, 1, textBoxAcMaxPoor);
        textBoxAcMaxPoor.setStyleName("orange");
        textBoxAcMaxPoor.setText("3");
        textBoxAcMaxPoor.setWidth("3em");
        textBoxAcMaxBad = new TextBox();
        final Label andLabelAc = new Label(c.and());
        cingTable.setWidget(rowIdxCingAcMax, 2, andLabelAc);
        cingTable.setWidget(rowIdxCingAcMax, 3, textBoxAcMaxBad);
        cingTable.getCellFormatter().setHorizontalAlignment(rowIdxCingAcMax, 3, HasHorizontalAlignment.ALIGN_CENTER);
        textBoxAcMaxBad.setStylePrimaryName("red");
        textBoxAcMaxBad.setText("5");
        textBoxAcMaxBad.setWidth("3em");
        final Label labelDegreeAc = new Label("\u00B0");
        cingTable.setWidget(rowIdxCingAcMax, 4, labelDegreeAc);
        checkBoxAcMax = new CheckBox();
        cingTable.setWidget(rowIdxCingAcMax, 0, checkBoxAcMax);
        checkBoxAcMax.setChecked(true);
        checkBoxAcMax.setHTML(c.Maximum_violatio());
        textBoxAcRmsPoor = new TextBox();
        cingTable.setWidget(rowIdxCingAcRms, 1, textBoxAcRmsPoor);
        textBoxAcRmsPoor.setStyleName("orange");
        textBoxAcRmsPoor.setText("3");
        textBoxAcRmsPoor.setWidth("3em");
        textBoxAcRmsBad = new TextBox();
        cingTable.setWidget(rowIdxCingAcRms, 2, new Label(c.and()));
        cingTable.setWidget(rowIdxCingAcRms, 3, textBoxAcRmsBad);
        cingTable.getCellFormatter().setHorizontalAlignment(rowIdxCingAcRms, 3, HasHorizontalAlignment.ALIGN_CENTER);
        textBoxAcRmsBad.setStylePrimaryName("red");
        textBoxAcRmsBad.setText("5");
        textBoxAcRmsBad.setWidth("3em");
        final Label labelDegreeAcRms = new Label("\u00B0");
        cingTable.setWidget(rowIdxCingAcRms, 4, labelDegreeAcRms);
        checkBoxAcRms = new CheckBox();
        cingTable.setWidget(rowIdxCingAcRms, 0, checkBoxAcRms);
        checkBoxAcRms.setChecked(true);
        checkBoxAcRms.setHTML(c.Rms_violatio());
        // /

        checkBoxMissingCoordinates = new CheckBox();
        cingTable.setWidget(rowIdxCingMissingCoord, 0, checkBoxMissingCoordinates);
        checkBoxMissingCoordinates.setChecked(true);
        checkBoxMissingCoordinates.setHTML(c.Flag_missing());

        noneCingCheckBox = new CheckBox();
        cingTable.setWidget(rowIdxCingNone, 0, noneCingCheckBox);
        noneCingCheckBox.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                Utils.setEnabledAllInRowsButFirst(cingTable, !noneCingCheckBox.isChecked());
            }
        });
        nonePcCheckBox.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                Utils.setEnabledAllInRowsButFirst(pcTable, !nonePcCheckBox.isChecked());
            }
        });
        noneWiCheckBox.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                Utils.setEnabledAllInRowsButFirst(wiTable, !noneWiCheckBox.isChecked());
            }
        });
        cingTable.getCellFormatter().setHorizontalAlignment(0, 0, HasHorizontalAlignment.ALIGN_CENTER);
        cingTable.getFlexCellFormatter().setColSpan(rowIdxCingNone, 0, 5);
        noneCingCheckBox.setHTML(c.none());

        // Return the content
        tabPanel.ensureDebugId("criteriaTabPanel");
        tabPanel.selectTab(0);

        final HorizontalPanel horizontalPanelBackNext = new HorizontalPanel();
        horizontalPanelBackNext.setSpacing(iCing.margin);
        verticalPanel.add(horizontalPanelBackNext);
        final Button backButton = new Button();
        final Button nextButton = new Button();
        horizontalPanelBackNext.add(backButton);
        backButton.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                History.back();
            }
        });
        backButton.setText(c.Back());
        horizontalPanelBackNext.add(backButton);
        horizontalPanelBackNext.add(nextButton);

        nextButton.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                icingShadow.onHistoryChanged(iCing.OPTIONS_STATE);
            }
        });
        nextButton.setText(c.Next());
        nextButton.setTitle(c.Set_the_options());

    }

    /**
     * Per table the criteria will be read out into a settings map
     * 
     * The values do need to be presented. An absent value might become supplemented within CING.
     * 
     * CRV stands for CRiteria Value CRS stands for CRiteria String
     * 
     * @return null on error.
     */
    public HashMap<String, String> getCriteria() {
        HashMap<String, String> result = new HashMap<String, String>();

        String CR_NONE = "-999.9";
        String CR_TRUE = "1";
        String CR_FALSE = CR_NONE;

        String CRS_OMEGA_MAXALL_POOR = "OMEGA_MAXALL_POOR";
        String CRS_OMEGA_MAXALL_BAD = "OMEGA_MAXALL_BAD";
        String CRS_DR_MAXALL_POOR = "DR_MAXALL_POOR";
        String CRS_DR_MAXALL_BAD = "DR_MAXALL_BAD";
        String CRS_DR_THRESHOLD_OVER_POOR = "DR_THRESHOLD_OVER_POOR";
        String CRS_DR_THRESHOLD_FRAC_POOR = "DR_THRESHOLD_FRAC_POOR";
        String CRS_DR_THRESHOLD_OVER_BAD = "DR_THRESHOLD_OVER_BAD";
        String CRS_DR_THRESHOLD_FRAC_BAD = "DR_THRESHOLD_FRAC_BAD";
        String CRS_DR_RMSALL_BAD = "DR_RMSALL_BAD";
        String CRS_AC_MAXALL_POOR = "AC_MAXALL_POOR";
        String CRS_AC_MAXALL_BAD = "AC_MAXALL_BAD";
        String CRS_AC_THRESHOLD_OVER_POOR = "AC_THRESHOLD_OVER_POOR";
        String CRS_AC_THRESHOLD_FRAC_POOR = "AC_THRESHOLD_FRAC_POOR";
        String CRS_AC_THRESHOLD_OVER_BAD = "AC_THRESHOLD_OVER_BAD";
        String CRS_AC_THRESHOLD_FRAC_BAD = "AC_THRESHOLD_FRAC_BAD";
        String CRS_AC_RMSALL_BAD = "AC_RMSALL_BAD";
        String CRS_FLAG_MISSING_COOR = "FLAG_MISSING_COOR";
        String CRS_WI_POOR_RAMCHK = "WI_POOR_RAMCHK";
        String CRS_WI_BAD_RAMCHK = "WI_BAD_RAMCHK";
        String CRS_WI_POOR_BBCCHK = "WI_POOR_BBCCHK";
        String CRS_WI_BAD_BBCCHK = "WI_BAD_BBCCHK";
        String CRS_WI_POOR_C12CHK = "WI_POOR_C12CHK";
        String CRS_WI_BAD_C12CHK = "WI_BAD_C12CHK";
        String CRS_PC_POOR_GF = "PC_POOR_GF";
        String CRS_PC_BAD_GF = "PC_BAD_GF";
        String CRS_AQUA_COMPL_INC_INTRA = "AQUA_COMPL_INC_INTRA";
        String CRS_AQUA_COMPL_OBS = "AQUA_COMPL_OBS";
        String CRS_AQUA_COMPL_POOR = "AQUA_COMPL_POOR";
        String CRS_AQUA_COMPL_BAD = "AQUA_COMPL_BAD";
        // CING
        if (!checkBoxOmega.isChecked()) {
            textBoxOmegaBad.setText(CR_NONE);
            textBoxOmegaPoor.setText(CR_NONE);
        }
        if (!checkBoxDrMax.isChecked()) {
            textBoxDrMaxBad.setText(CR_NONE);
            textBoxDrMaxPoor.setText(CR_NONE);
        }
        if (!checkBoxDrRms.isChecked()) {
            textBoxDrRmsBad.setText(CR_NONE);
            textBoxDrRmsPoor.setText(CR_NONE);
        }
        if (!checkBoxAcMax.isChecked()) {
            textBoxAcMaxBad.setText(CR_NONE);
            textBoxAcMaxPoor.setText(CR_NONE);
        }
        if (!checkBoxAcRms.isChecked()) {
            textBoxAcRmsPoor.setText(CR_NONE);
            textBoxAcRmsBad.setText(CR_NONE);
        }
        String CRV_OMEGA_MAXALL_POOR = textBoxOmegaPoor.getText();
        String CRV_OMEGA_MAXALL_BAD = textBoxOmegaBad.getText();
        String CRV_FLAG_MISSING_COOR = (checkBoxMissingCoordinates.isChecked() ? CR_TRUE : CR_FALSE);
        String CRV_DR_MAXALL_POOR = textBoxDrMaxPoor.getText();
        String CRV_DR_MAXALL_BAD = textBoxDrMaxBad.getText();
        String CRV_DR_THRESHOLD_OVER_POOR = "0.5"; // not implemented all threshold parameters. TODO: if too much time.
        String CRV_DR_THRESHOLD_FRAC_POOR = "0.5";
        String CRV_DR_THRESHOLD_OVER_BAD = "1.0";
        String CRV_DR_THRESHOLD_FRAC_BAD = "0.5";
        String CRV_DR_RMSALL_BAD = textBoxDrRmsBad.getText();
        String CRV_AC_MAXALL_POOR = textBoxAcMaxPoor.getText();
        String CRV_AC_MAXALL_BAD = textBoxAcMaxBad.getText();
        String CRV_AC_THRESHOLD_OVER_POOR = "3";
        String CRV_AC_THRESHOLD_FRAC_POOR = "0.5";
        String CRV_AC_THRESHOLD_OVER_BAD = "5";
        String CRV_AC_THRESHOLD_FRAC_BAD = "0.5";
        String CRV_AC_RMSALL_BAD = textBoxAcRmsBad.getText();
        // WI
        if (!ramachandranPlotCheckBox.isChecked()) {
            ramaTextBoxBad.setText(CR_NONE);
            ramaTextBoxPoor.setText(CR_NONE);
        }
        if (!janinPlotCheckBox.isChecked()) {
            janinTextBoxBad.setText(CR_NONE);
            janinTextBoxPoor.setText(CR_NONE);
        }
        if (!backboneNormalityCheckBox.isChecked()) {
            bbTextBoxBad.setText(CR_NONE);
            bbTextBoxPoor.setText(CR_NONE);
        }
        
//        just finished typing here to continue maandag TODO:
        
        String CRV_WI_POOR_RAMCHK = ramaTextBoxPoor.getText();
        String CRV_WI_BAD_RAMCHK = ramaTextBoxBad.getText();
        String CRV_WI_POOR_BBCCHK = bbTextBoxPoor.getText();
        String CRV_WI_BAD_BBCCHK = bbTextBoxBad.getText();
        String CRV_WI_POOR_C12CHK = janinTextBoxPoor.getText();
        String CRV_WI_BAD_C12CHK = janinTextBoxBad.getText();
        // PC
        if (!gFactorCheckBox.isChecked()) {
            textBoxGfactorBad.setText(CR_NONE);
            textBoxGfactorBad.setText(CR_NONE);
        }
        if (!noeCompletenessCheckBox.isChecked()) {
            textBoxComplBad.setText(CR_NONE);
            textBoxComplPoor.setText(CR_NONE);
        }        
        String CRV_PC_POOR_GF = textBoxGfactorPoor.getText();
        String CRV_PC_BAD_GF = textBoxGfactorBad.getText();
        String CRV_AQUA_COMPL_INC_INTRA = (includeIntraresidualContactsCheckBox.isChecked() ? CR_TRUE : CR_FALSE);
        String CRV_AQUA_COMPL_OBS = Utils.getListBoxItemText(listBoxObs);
        String CRV_AQUA_COMPL_POOR =textBoxComplPoor.getText();
        String CRV_AQUA_COMPL_BAD = textBoxComplBad.getText();

        ArrayList<String> cingCriteriaKeyList = new ArrayList<String>();
        cingCriteriaKeyList.add(CRS_OMEGA_MAXALL_POOR);
        cingCriteriaKeyList.add(CRS_OMEGA_MAXALL_BAD);
        cingCriteriaKeyList.add(CRS_FLAG_MISSING_COOR);
        cingCriteriaKeyList.add(CRS_DR_MAXALL_POOR);
        cingCriteriaKeyList.add(CRS_DR_MAXALL_BAD);
        cingCriteriaKeyList.add(CRS_DR_THRESHOLD_OVER_POOR);
        cingCriteriaKeyList.add(CRS_DR_THRESHOLD_FRAC_POOR);
        cingCriteriaKeyList.add(CRS_DR_THRESHOLD_OVER_BAD);
        cingCriteriaKeyList.add(CRS_DR_THRESHOLD_FRAC_BAD);
        cingCriteriaKeyList.add(CRS_DR_RMSALL_BAD);
        cingCriteriaKeyList.add(CRS_AC_MAXALL_POOR);
        cingCriteriaKeyList.add(CRS_AC_MAXALL_BAD);
        cingCriteriaKeyList.add(CRS_AC_THRESHOLD_OVER_POOR);
        cingCriteriaKeyList.add(CRS_AC_THRESHOLD_FRAC_POOR);
        cingCriteriaKeyList.add(CRS_AC_THRESHOLD_OVER_BAD);
        cingCriteriaKeyList.add(CRS_AC_THRESHOLD_FRAC_BAD);
        cingCriteriaKeyList.add(CRS_AC_RMSALL_BAD);

        ArrayList<String> wiCriteriaKeyList = new ArrayList<String>();
        cingCriteriaKeyList.add(CRS_WI_POOR_RAMCHK);
        cingCriteriaKeyList.add(CRS_WI_BAD_RAMCHK);
        cingCriteriaKeyList.add(CRS_WI_POOR_BBCCHK);
        cingCriteriaKeyList.add(CRS_WI_BAD_BBCCHK);
        cingCriteriaKeyList.add(CRS_WI_POOR_C12CHK);
        cingCriteriaKeyList.add(CRS_WI_BAD_C12CHK);

        ArrayList<String> pcCriteriaKeyList = new ArrayList<String>();
        cingCriteriaKeyList.add(CRS_PC_POOR_GF);
        cingCriteriaKeyList.add(CRS_PC_BAD_GF);
        cingCriteriaKeyList.add(CRS_AQUA_COMPL_INC_INTRA);
        cingCriteriaKeyList.add(CRS_AQUA_COMPL_OBS);
        cingCriteriaKeyList.add(CRS_AQUA_COMPL_POOR);
        cingCriteriaKeyList.add(CRS_AQUA_COMPL_BAD);

        ArrayList<String> criteriaKeyListAll = new ArrayList<String>();
        criteriaKeyListAll.addAll(cingCriteriaKeyList);

        result.put(CRS_OMEGA_MAXALL_POOR, CRV_OMEGA_MAXALL_POOR);
        result.put(CRS_OMEGA_MAXALL_BAD, CRV_OMEGA_MAXALL_BAD);
        result.put(CRS_FLAG_MISSING_COOR, CRV_FLAG_MISSING_COOR);
        result.put(CRS_DR_MAXALL_POOR, CRV_DR_MAXALL_POOR);
        result.put(CRS_DR_MAXALL_BAD, CRV_DR_MAXALL_BAD);
        result.put(CRS_DR_THRESHOLD_OVER_POOR, CRV_DR_THRESHOLD_OVER_POOR);
        result.put(CRS_DR_THRESHOLD_FRAC_POOR, CRV_DR_THRESHOLD_FRAC_POOR);
        result.put(CRS_DR_THRESHOLD_OVER_BAD, CRV_DR_THRESHOLD_OVER_BAD);
        result.put(CRS_DR_THRESHOLD_FRAC_BAD, CRV_DR_THRESHOLD_FRAC_BAD);
        result.put(CRS_DR_RMSALL_BAD, CRV_DR_RMSALL_BAD);
        result.put(CRS_AC_MAXALL_POOR, CRV_AC_MAXALL_POOR);
        result.put(CRS_AC_MAXALL_BAD, CRV_AC_MAXALL_BAD);
        result.put(CRS_AC_THRESHOLD_OVER_POOR, CRV_AC_THRESHOLD_OVER_POOR);
        result.put(CRS_AC_THRESHOLD_FRAC_POOR, CRV_AC_THRESHOLD_FRAC_POOR);
        result.put(CRS_AC_THRESHOLD_OVER_BAD, CRV_AC_THRESHOLD_OVER_BAD);
        result.put(CRS_AC_THRESHOLD_FRAC_BAD, CRV_AC_THRESHOLD_FRAC_BAD);
        result.put(CRS_AC_RMSALL_BAD, CRV_AC_RMSALL_BAD);
        //
        result.put(CRS_WI_POOR_RAMCHK, CRV_WI_POOR_RAMCHK);
        result.put(CRS_WI_BAD_RAMCHK, CRV_WI_BAD_RAMCHK);
        result.put(CRS_WI_POOR_BBCCHK, CRV_WI_POOR_BBCCHK);
        result.put(CRS_WI_BAD_BBCCHK, CRV_WI_BAD_BBCCHK);
        result.put(CRS_WI_POOR_C12CHK, CRV_WI_POOR_C12CHK);
        result.put(CRS_WI_BAD_C12CHK, CRV_WI_BAD_C12CHK);
        //
        result.put(CRS_PC_POOR_GF, CRV_PC_POOR_GF);
        result.put(CRS_PC_BAD_GF, CRV_PC_BAD_GF);
        result.put(CRS_AQUA_COMPL_INC_INTRA, CRV_AQUA_COMPL_INC_INTRA);
        result.put(CRS_AQUA_COMPL_OBS, CRV_AQUA_COMPL_OBS);
        result.put(CRS_AQUA_COMPL_POOR, CRV_AQUA_COMPL_POOR);
        result.put(CRS_AQUA_COMPL_BAD, CRV_AQUA_COMPL_BAD);

        ArrayList<String> keyListToNull = new ArrayList<String>();
        if (noneCingCheckBox.isChecked()) {
            keyListToNull.addAll(cingCriteriaKeyList);
        }
        if (noneWiCheckBox.isChecked()) {
            keyListToNull.addAll(wiCriteriaKeyList);
        }
        if (nonePcCheckBox.isChecked()) {
            keyListToNull.addAll(pcCriteriaKeyList);
        }

        for (Iterator i = keyListToNull.iterator(); i.hasNext();) {
            String key = (String) i.next();
            result.put(key, CR_NONE);
        }

        return result;
    }
}
