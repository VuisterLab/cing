package cing.client;

import cing.client.i18n.iCingConstants;

import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;

public class RestraintCriteria extends Composite {

    public RestraintCriteria() {

        final FlexTable cingTable = new FlexTable();
        initWidget(cingTable);
        iCingConstants c = iCing.c;

        final CheckBox checkBoxDR = new CheckBox();
        cingTable.setWidget(1, 0, checkBoxDR);
        cingTable.getCellFormatter().setHorizontalAlignment(1, 0, HasHorizontalAlignment.ALIGN_CENTER);
        cingTable.getFlexCellFormatter().setColSpan(1, 0, 5);
        checkBoxDR.setText("Distance Restraints");
        checkBoxDR.setEnabled(true);
        checkBoxDR.setChecked(true);
        checkBoxDR.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                Utils.setEnabledAllInColumnsButFirst(cingTable, 1, checkBoxDR.isChecked());
            }
        });

        final CheckBox checkBoxMissingCoordinates = new CheckBox();
        cingTable.setWidget(3, 0, checkBoxMissingCoordinates);
        checkBoxMissingCoordinates.setChecked(true);
        checkBoxMissingCoordinates.setHTML(c.Flag_missing());

        // row omega
        final TextBox textBoxOmegaPoor = new TextBox();
        cingTable.setWidget(2, 1, textBoxOmegaPoor);
        textBoxOmegaPoor.setStyleName("orange");
        textBoxOmegaPoor.setText("15");
        textBoxOmegaPoor.setWidth("3em");

        final Label andLabel = new Label(c.and());
        cingTable.setWidget(2, 2, andLabel);

        final TextBox textBoxOmegaBad = new TextBox();
        cingTable.setWidget(2, 3, textBoxOmegaBad);
        cingTable.getCellFormatter().setHorizontalAlignment(2, 3, HasHorizontalAlignment.ALIGN_CENTER);
        textBoxOmegaBad.setStylePrimaryName("red");
        textBoxOmegaBad.setText("20");
        textBoxOmegaBad.setWidth("3em");

        final Label label = new Label("\u00B0");
        cingTable.setWidget(2, 4, label);

        final CheckBox noneCingCheckBox = new CheckBox();
        cingTable.setWidget(0, 0, noneCingCheckBox);
        noneCingCheckBox.setText("none");
        cingTable.getCellFormatter().setHorizontalAlignment(0, 0, HasHorizontalAlignment.ALIGN_CENTER);
        cingTable.getFlexCellFormatter().setColSpan(0, 0, 5);
        noneCingCheckBox.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                Utils.setEnabledAllInRowsButFirst(cingTable, !noneCingCheckBox.isChecked());
            }
        });

        final CheckBox omegaCheckBox = new CheckBox();
        cingTable.setWidget(2, 0, omegaCheckBox);
        omegaCheckBox.setText("Omega");
        
    }

}
