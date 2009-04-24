package cing.client;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Set;

import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.DecoratedTabPanel;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

public class Criteria extends iCingView {

    private CheckBox noneCingCheckBox;
    private CheckBox nonePcCheckBox;
    private CheckBox noneWiCheckBox;
    private TextBox ramaTextBoxBad;
    private TextBox ramaTextBoxPoor;

    int j = 0;
    final int rowIdxCingNone = j++;
    final int rowIdxCingMissingCoord = j++;
    final int rowIdxCingOmega = j++;
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
    /**
     * CRV stands for CRiteria Value CRS stands for CRiteria String
     */
    static String CRV_NONE = "-999.9";
    static String CRV_TRUE = "1";
    static String CRV_FALSE = CRV_NONE;
    // Might seem verbose but allows for excellent checking by Eclipse.
    static String CRS_OMEGA_MAXALL_POOR = "OMEGA_MAXALL_POOR";
    static String CRS_OMEGA_MAXALL_BAD = "OMEGA_MAXALL_BAD";
    static String CRS_DR_MAXALL_POOR = "DR_MAXALL_POOR";
    static String CRS_DR_MAXALL_BAD = "DR_MAXALL_BAD";
    static String CRS_DR_THRESHOLD_OVER_POOR = "DR_THRESHOLD_OVER_POOR";
    static String CRS_DR_THRESHOLD_FRAC_POOR = "DR_THRESHOLD_FRAC_POOR";
    static String CRS_DR_THRESHOLD_OVER_BAD = "DR_THRESHOLD_OVER_BAD";
    static String CRS_DR_THRESHOLD_FRAC_BAD = "DR_THRESHOLD_FRAC_BAD";
    static String CRS_DR_RMSALL_BAD = "DR_RMSALL_BAD";
    static String CRS_DR_RMSALL_POOR = "DR_RMSALL_POOR";
    static String CRS_AC_MAXALL_POOR = "AC_MAXALL_POOR";
    static String CRS_AC_MAXALL_BAD = "AC_MAXALL_BAD";
    static String CRS_AC_THRESHOLD_OVER_POOR = "AC_THRESHOLD_OVER_POOR";
    static String CRS_AC_THRESHOLD_FRAC_POOR = "AC_THRESHOLD_FRAC_POOR";
    static String CRS_AC_THRESHOLD_OVER_BAD = "AC_THRESHOLD_OVER_BAD";
    static String CRS_AC_THRESHOLD_FRAC_BAD = "AC_THRESHOLD_FRAC_BAD";
    static String CRS_AC_RMSALL_BAD = "AC_RMSALL_BAD";
    static String CRS_AC_RMSALL_POOR = "AC_RMSALL_POOR";
    static String CRS_FLAG_MISSING_COOR = "FLAG_MISSING_COOR";
    static String CRS_WI_RAMCHK_POOR = "WI_RAMCHK_POOR";
    static String CRS_WI_RAMCHK_BAD = "WI_RAMCHK_BAD";
    static String CRS_WI_BBCCHK_POOR = "WI_BBCCHK_POOR";
    static String CRS_WI_BBCCHK_BAD = "WI_BBCCHK_BAD";
    static String CRS_WI_C12CHK_POOR = "WI_C12CHK_POOR";
    static String CRS_WI_C12CHK_BAD = "WI_C12CHK_BAD";
    static String CRS_PC_GF_POOR = "PC_GF_POOR";
    static String CRS_PC_GF_BAD = "PC_GF_BAD";
    static String CRS_AQUA_COMPL_INC_INTRA = "AQUA_COMPL_INC_INTRA";
    static String CRS_AQUA_COMPL_OBS = "AQUA_COMPL_OBS";
    static String CRS_AQUA_COMPL_POOR = "AQUA_COMPL_POOR";
    static String CRS_AQUA_COMPL_BAD = "AQUA_COMPL_BAD";

    static ArrayList<String> cingCriteriaKeyList = new ArrayList<String>();
    static ArrayList<String> wiCriteriaKeyList = new ArrayList<String>();
    static ArrayList<String> pcCriteriaKeyList = new ArrayList<String>();
    static ArrayList<String> criteriaKeyListAll = new ArrayList<String>();

    // Interface defaults; sync with those in $CINGROOT/python/cing/valSets.cfg.    
    String CRV_AC_MAXALL_BAD = "10";
    String CRV_AC_MAXALL_POOR = "3";
    String CRV_AC_RMSALL_BAD = "5";
    String CRV_AC_RMSALL_POOR = "3";
    String CRV_AC_THRESHOLD_FRAC_BAD = CRV_NONE;
    String CRV_AC_THRESHOLD_FRAC_POOR = CRV_NONE;
    String CRV_AC_THRESHOLD_OVER_BAD = CRV_NONE;
    String CRV_AC_THRESHOLD_OVER_POOR = CRV_NONE;
    String CRV_AQUA_COMPL_BAD = "10";
    String CRV_AQUA_COMPL_INC_INTRA = "1";
    String CRV_AQUA_COMPL_OBS = "Standard";
    String CRV_AQUA_COMPL_POOR = "20";
    String CRV_DR_MAXALL_BAD = "0.5";
    String CRV_DR_MAXALL_POOR = "0.3";
    String CRV_DR_RMSALL_BAD = "0.3";
    String CRV_DR_RMSALL_POOR = "0.15";
    String CRV_DR_THRESHOLD_FRAC_BAD = CRV_NONE;
    String CRV_DR_THRESHOLD_FRAC_POOR = CRV_NONE;
    String CRV_DR_THRESHOLD_OVER_BAD = CRV_NONE;
    String CRV_DR_THRESHOLD_OVER_POOR = CRV_NONE;
    String CRV_FLAG_MISSING_COOR = "true";    
//    String CRV_OMEGA_MAXALL_BAD = "20";
//    String CRV_OMEGA_MAXALL_POOR = "15";
    String CRV_OMEGA_MAXALL_BAD = "14.1";
    String CRV_OMEGA_MAXALL_POOR = "9.4";
    String CRV_PC_BAD_GF = "-1.3";
    String CRV_PC_POOR_GF = "-1.0";
    String CRV_WI_BAD_BBCCHK = "3.0";
    String CRV_WI_BAD_C12CHK = "-1.2";
    String CRV_WI_BAD_RAMCHK = "-1.3";
    String CRV_WI_POOR_BBCCHK = "10.0";
    String CRV_WI_POOR_C12CHK = "-0.9";
    String CRV_WI_POOR_RAMCHK = "-1.0";

    static {
        // Get all added to sub lists.
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

        wiCriteriaKeyList.add(CRS_WI_RAMCHK_POOR);
        wiCriteriaKeyList.add(CRS_WI_RAMCHK_BAD);
        wiCriteriaKeyList.add(CRS_WI_BBCCHK_POOR);
        wiCriteriaKeyList.add(CRS_WI_BBCCHK_BAD);
        wiCriteriaKeyList.add(CRS_WI_C12CHK_POOR);
        wiCriteriaKeyList.add(CRS_WI_C12CHK_BAD);
        wiCriteriaKeyList.add(CRS_PC_GF_POOR);
        wiCriteriaKeyList.add(CRS_PC_GF_BAD);

        pcCriteriaKeyList.add(CRS_AQUA_COMPL_INC_INTRA);
        pcCriteriaKeyList.add(CRS_AQUA_COMPL_OBS);
        pcCriteriaKeyList.add(CRS_AQUA_COMPL_POOR);
        pcCriteriaKeyList.add(CRS_AQUA_COMPL_BAD);

        // Get all added to overall list.
        criteriaKeyListAll.addAll(cingCriteriaKeyList);
        criteriaKeyListAll.addAll(wiCriteriaKeyList);
        criteriaKeyListAll.addAll(pcCriteriaKeyList);
    }

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
        ramaTextBoxBad.setText(CRV_WI_BAD_RAMCHK);
        ramaTextBoxBad.setWidth("3em");
        ramaTextBoxPoor = new TextBox();
        wiTable.setWidget(rowIdxWiRama, 3, ramaTextBoxPoor);
        wiTable.getCellFormatter().setHorizontalAlignment(rowIdxWiRama, 3, HasHorizontalAlignment.ALIGN_CENTER);
        ramaTextBoxPoor.setStyleName("orange");
        ramaTextBoxPoor.setText(CRV_WI_POOR_RAMCHK);
        ramaTextBoxPoor.setWidth("3em");

        bbTextBoxBad = new TextBox();
        wiTable.setWidget(rowIdxWiBb, 2, bbTextBoxBad);
        wiTable.getCellFormatter().setHorizontalAlignment(rowIdxWiBb, 2, HasHorizontalAlignment.ALIGN_RIGHT);
        bbTextBoxBad.setText(CRV_WI_BAD_BBCCHK);
        bbTextBoxBad.setStyleName("red");
        bbTextBoxBad.setWidth("3em");

        bbTextBoxPoor = new TextBox();
        wiTable.setWidget(rowIdxWiBb, 3, bbTextBoxPoor);
        wiTable.getCellFormatter().setHorizontalAlignment(rowIdxWiBb, 3, HasHorizontalAlignment.ALIGN_CENTER);
        bbTextBoxPoor.setText(CRV_WI_POOR_BBCCHK);
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
        janinTextBoxBad.setText(CRV_WI_BAD_C12CHK);
        janinTextBoxBad.setStyleName("red");
        janinTextBoxBad.setWidth("3em");

        final Label residueSigmas22Label = new Label(c.residue_sigma() + " [-2,2]");
        wiTable.setWidget(rowIdxWiRama, 4, residueSigmas22Label);

        final Label occurancesInDbLabel = new Label(c.occurrences_in() + " [0-80]");
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
        janinTextBoxPoor.setText(CRV_WI_POOR_C12CHK);
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
        textBoxGfactorPoor.setText(CRV_PC_POOR_GF);
        textBoxGfactorPoor.setWidth("3em");
        textBoxGfactorBad = new TextBox();
        pcTable.setWidget(rowIdxPcGfactor, 1, textBoxGfactorBad);
        pcTable.getCellFormatter().setHorizontalAlignment(rowIdxPcGfactor, 3, HasHorizontalAlignment.ALIGN_LEFT);
        textBoxGfactorBad.setStylePrimaryName("red");
        textBoxGfactorBad.setText(CRV_PC_BAD_GF);
        textBoxGfactorBad.setWidth("3em");
        @SuppressWarnings("unused")
        final Label gFactorLimitsLabel = new Label("[-99,99]");
        // pcTable.setWidget(rowIdxPcGfactor, 3, gFactorLimitsLabel);
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
        textBoxComplBad.setText(CRV_AQUA_COMPL_BAD);
        textBoxComplBad.setWidth("3em");

        textBoxComplPoor = new TextBox();
        pcTable.setWidget(rowIdxPcComple, 2, textBoxComplPoor);
        textBoxComplPoor.setVisibleLength(3);
        textBoxComplPoor.setStyleName("orange");
        textBoxComplPoor.setText(CRV_AQUA_COMPL_POOR);
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
        pcTable.removeRow(rowIdxPcComple); // deleting bottom up.
        pcTable.removeRow(rowIdxPcObserv); // TODO: enable when Wattos is run.
        pcTable.removeRow(rowIdxPcIntra);

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
        textBoxOmegaPoor.setText(CRV_OMEGA_MAXALL_POOR);
        textBoxOmegaPoor.setWidth("3em");
        final Label andLabelOmega = new Label(c.and());
        cingTable.setWidget(rowIdxCingOmega, 2, andLabelOmega);
        textBoxOmegaBad = new TextBox();
        cingTable.setWidget(rowIdxCingOmega, 3, textBoxOmegaBad);
        cingTable.getCellFormatter().setHorizontalAlignment(rowIdxCingOmega, 3, HasHorizontalAlignment.ALIGN_CENTER);
        textBoxOmegaBad.setStylePrimaryName("red");
        textBoxOmegaBad.setText(CRV_OMEGA_MAXALL_BAD);
        textBoxOmegaBad.setWidth("3em");
        final Label labelDegreeOmega = new Label("\u00B0");
        cingTable.setWidget(rowIdxCingOmega, 4, labelDegreeOmega);

        textBoxDrMaxPoor = new TextBox();
        cingTable.setWidget(rowIdxCingDrMax, 1, textBoxDrMaxPoor);
        textBoxDrMaxPoor.setStyleName("orange");
        textBoxDrMaxPoor.setText(CRV_DR_MAXALL_POOR);
        textBoxDrMaxPoor.setWidth("3em");
        textBoxDrMaxBad = new TextBox();
        final Label andLabelDr = new Label(c.and());
        cingTable.setWidget(rowIdxCingDrMax, 2, andLabelDr);
        cingTable.setWidget(rowIdxCingDrMax, 3, textBoxDrMaxBad);
        cingTable.getCellFormatter().setHorizontalAlignment(rowIdxCingDrMax, 3, HasHorizontalAlignment.ALIGN_CENTER);
        textBoxDrMaxBad.setStylePrimaryName("red");
        textBoxDrMaxBad.setText(CRV_DR_MAXALL_BAD);
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
        textBoxDrRmsPoor.setText(CRV_DR_RMSALL_POOR);
        textBoxDrRmsPoor.setWidth("3em");
        textBoxDrRmsBad = new TextBox();
        final Label andLabelDrRms = new Label(c.and());
        cingTable.setWidget(rowIdxCingDrRms, 2, andLabelDrRms);
        cingTable.setWidget(rowIdxCingDrRms, 3, textBoxDrRmsBad);
        cingTable.getCellFormatter().setHorizontalAlignment(rowIdxCingDrRms, 3, HasHorizontalAlignment.ALIGN_CENTER);
        textBoxDrRmsBad.setStylePrimaryName("red");
        textBoxDrRmsBad.setText(CRV_DR_RMSALL_BAD);
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
        textBoxAcMaxPoor.setText(CRV_AC_MAXALL_POOR);
        textBoxAcMaxPoor.setWidth("3em");
        textBoxAcMaxBad = new TextBox();
        final Label andLabelAc = new Label(c.and());
        cingTable.setWidget(rowIdxCingAcMax, 2, andLabelAc);
        cingTable.setWidget(rowIdxCingAcMax, 3, textBoxAcMaxBad);
        cingTable.getCellFormatter().setHorizontalAlignment(rowIdxCingAcMax, 3, HasHorizontalAlignment.ALIGN_CENTER);
        textBoxAcMaxBad.setStylePrimaryName("red");
        textBoxAcMaxBad.setText(CRV_AC_MAXALL_BAD);
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
        textBoxAcRmsPoor.setText(CRV_AC_RMSALL_POOR);
        textBoxAcRmsPoor.setWidth("3em");
        textBoxAcRmsBad = new TextBox();
        cingTable.setWidget(rowIdxCingAcRms, 2, new Label(c.and()));
        cingTable.setWidget(rowIdxCingAcRms, 3, textBoxAcRmsBad);
        cingTable.getCellFormatter().setHorizontalAlignment(rowIdxCingAcRms, 3, HasHorizontalAlignment.ALIGN_CENTER);
        textBoxAcRmsBad.setStylePrimaryName("red");
        textBoxAcRmsBad.setText(CRV_AC_RMSALL_BAD);
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
                icingShadow.onHistoryChanged(iCing.FILE_STATE);
                // History.back();
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
     * Per table the criteria will be read out into a settings map that is returned if all's well. The criteria will
     * also be added to the panel argument as hidden parameters.
     * 
     * The values do need to be presented. An absent value might become supplemented within CING.
     * 
     * CRV stands for CRiteria Value CRS stands for CRiteria String
     * 
     * @param verticalPanel
     * 
     * @return null on error.
     */
    public HashMap<String, String> getCriteria(VerticalPanel verticalPanel) {
        HashMap<String, String> result = new HashMap<String, String>();

        // CING
        if (!checkBoxOmega.isChecked()) {
            textBoxOmegaBad.setText(CRV_NONE);
            textBoxOmegaPoor.setText(CRV_NONE);
        }
        if (!checkBoxDrMax.isChecked()) {
            textBoxDrMaxBad.setText(CRV_NONE);
            textBoxDrMaxPoor.setText(CRV_NONE);
        }
        if (!checkBoxDrRms.isChecked()) {
            textBoxDrRmsBad.setText(CRV_NONE);
            textBoxDrRmsPoor.setText(CRV_NONE);
        }
        if (!checkBoxAcMax.isChecked()) {
            textBoxAcMaxBad.setText(CRV_NONE);
            textBoxAcMaxPoor.setText(CRV_NONE);
        }
        if (!checkBoxAcRms.isChecked()) {
            textBoxAcRmsPoor.setText(CRV_NONE);
            textBoxAcRmsBad.setText(CRV_NONE);
        }
        CRV_OMEGA_MAXALL_POOR = textBoxOmegaPoor.getText();
        CRV_OMEGA_MAXALL_BAD = textBoxOmegaBad.getText();
        CRV_FLAG_MISSING_COOR = (checkBoxMissingCoordinates.isChecked() ? CRV_TRUE : CRV_FALSE);
        CRV_DR_MAXALL_POOR = textBoxDrMaxPoor.getText();
        CRV_DR_MAXALL_BAD = textBoxDrMaxBad.getText();
        CRV_DR_RMSALL_BAD = textBoxDrRmsBad.getText();
        CRV_AC_MAXALL_POOR = textBoxAcMaxPoor.getText();
        CRV_AC_MAXALL_BAD = textBoxAcMaxBad.getText();
        CRV_AC_RMSALL_BAD = textBoxAcRmsBad.getText();
        // WI
        if (!ramachandranPlotCheckBox.isChecked()) {
            ramaTextBoxBad.setText(CRV_NONE);
            ramaTextBoxPoor.setText(CRV_NONE);
        }
        if (!janinPlotCheckBox.isChecked()) {
            janinTextBoxBad.setText(CRV_NONE);
            janinTextBoxPoor.setText(CRV_NONE);
        }
        if (!backboneNormalityCheckBox.isChecked()) {
            bbTextBoxBad.setText(CRV_NONE);
            bbTextBoxPoor.setText(CRV_NONE);
        }

        CRV_WI_POOR_RAMCHK = ramaTextBoxPoor.getText();
        CRV_WI_BAD_RAMCHK = ramaTextBoxBad.getText();
        CRV_WI_POOR_BBCCHK = bbTextBoxPoor.getText();
        CRV_WI_BAD_BBCCHK = bbTextBoxBad.getText();
        CRV_WI_POOR_C12CHK = janinTextBoxPoor.getText();
        CRV_WI_BAD_C12CHK = janinTextBoxBad.getText();
        // PC
        if (!gFactorCheckBox.isChecked()) {
            textBoxGfactorBad.setText(CRV_NONE);
            textBoxGfactorBad.setText(CRV_NONE);
        }
        if (!noeCompletenessCheckBox.isChecked()) {
            textBoxComplBad.setText(CRV_NONE);
            textBoxComplPoor.setText(CRV_NONE);
        }
        CRV_PC_POOR_GF = textBoxGfactorPoor.getText();
        CRV_PC_BAD_GF = textBoxGfactorBad.getText();
        CRV_AQUA_COMPL_INC_INTRA = (includeIntraresidualContactsCheckBox.isChecked() ? CRV_TRUE : CRV_FALSE);
        CRV_AQUA_COMPL_OBS = Utils.getListBoxItemText(listBoxObs);
        CRV_AQUA_COMPL_POOR = textBoxComplPoor.getText();
        CRV_AQUA_COMPL_BAD = textBoxComplBad.getText();

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
        result.put(CRS_DR_RMSALL_POOR, CRV_DR_RMSALL_POOR);
        result.put(CRS_AC_MAXALL_POOR, CRV_AC_MAXALL_POOR);
        result.put(CRS_AC_MAXALL_BAD, CRV_AC_MAXALL_BAD);
        result.put(CRS_AC_THRESHOLD_OVER_POOR, CRV_AC_THRESHOLD_OVER_POOR);
        result.put(CRS_AC_THRESHOLD_FRAC_POOR, CRV_AC_THRESHOLD_FRAC_POOR);
        result.put(CRS_AC_THRESHOLD_OVER_BAD, CRV_AC_THRESHOLD_OVER_BAD);
        result.put(CRS_AC_THRESHOLD_FRAC_BAD, CRV_AC_THRESHOLD_FRAC_BAD);
        result.put(CRS_AC_RMSALL_BAD, CRV_AC_RMSALL_BAD);
        result.put(CRS_AC_RMSALL_POOR, CRV_AC_RMSALL_POOR);
        //
        result.put(CRS_WI_RAMCHK_POOR, CRV_WI_POOR_RAMCHK);
        result.put(CRS_WI_RAMCHK_BAD, CRV_WI_BAD_RAMCHK);
        result.put(CRS_WI_BBCCHK_POOR, CRV_WI_POOR_BBCCHK);
        result.put(CRS_WI_BBCCHK_BAD, CRV_WI_BAD_BBCCHK);
        result.put(CRS_WI_C12CHK_POOR, CRV_WI_POOR_C12CHK);
        result.put(CRS_WI_C12CHK_BAD, CRV_WI_BAD_C12CHK);
        //
        result.put(CRS_PC_GF_POOR, CRV_PC_POOR_GF);
        result.put(CRS_PC_GF_BAD, CRV_PC_BAD_GF);
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
        Collections.sort(keyListToNull);
        for (Iterator i = keyListToNull.iterator(); i.hasNext();) {
            String key = (String) i.next();
            if (!result.containsKey(key)) {
                GenClient.showError("Nulling value to key that does not exist yet: [" + key);
                return null;
            }
            GenClient.showDebug("Nulling value to key: [" + key);
            result.put(key, CRV_NONE);
        }

        Set<String> keySet = result.keySet();
        ArrayList keyList = new ArrayList(keySet);
        Collections.sort(keyList);
        for (Iterator i = keyList.iterator(); i.hasNext();) {
            String key = (String) i.next();
            String value = result.get(key);
            // GenClient.showDebug("Adding to form: key, value: [" + key + "] ["+value+"]");
            verticalPanel.add(new Hidden(key, value));
        }
        return result;
    }
}
