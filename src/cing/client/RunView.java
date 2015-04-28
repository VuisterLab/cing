package cing.client;

import java.util.HashMap;

import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

public class RunView extends iCingView {

    final HTML reportHTML = new HTML();
    static final Button submitButton = new Button();
    static final Button nextButton = new Button();
    iCingQuery cingQueryRun;
    iCingQuery cingQueryOptions = null;
//    static final Button saveCriteriaButton = new Button();

    public RunView() {
        super();
    }

    public void setIcing(iCing icing) {
        super.setIcing(icing);
        final iCing icingShadow = icing;
        setState(iCing.RUN_STATE);

        final Label html_1 = new Label(c.Run());
        html_1.setStylePrimaryName("h1");
        verticalPanel.add(html_1);

        verticalPanel.add(decPanel);
        VerticalPanel verticalPanelDec = new VerticalPanel();
        verticalPanelDec.setSpacing(iCing.margin);
        decPanel.add(verticalPanelDec);

        final Label html_2 = new Label(c.Please_press_the());

        submitButton.setText(c.Submit());
        submitButton.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                getCriteriaOnServer();
            }
        });
        submitButton.setEnabled(true);

        verticalPanelDec.add(html_2);
        verticalPanelDec.add(submitButton);

        /** Options block */
//        saveCriteriaButton.setTitle(c.Run_the_validati());
//        verticalPanelDec.setCellHorizontalAlignment(saveCriteriaButton, HasHorizontalAlignment.ALIGN_LEFT);
//
//        saveCriteriaButton.setText("saveCriteriaButton");
//        saveCriteriaButton.addClickListener(new ClickListener() {
//            public void onClick(final Widget sender) {
//                run();
//            }
//        });

//        verticalPanel.add(saveCriteriaButton);
        FormHandlerSpecific serverFormHandlerOptions = new FormHandlerSpecific(icing);
        cingQueryOptions = new iCingQuery(icing);
        cingQueryOptions.action.setValue(Settings.FORM_ACTION_CRITERIA);
        cingQueryOptions.setFormHandler(serverFormHandlerOptions);
        verticalPanel.add(cingQueryOptions.formPanel);
//        for (int i = 0; i < 2; i++) { // testing if protocol can handle many params.
//            String randomKey = iCing.getNewAccessKey();
//            cingQueryOptions.formVerticalPanel.add(new Hidden(randomKey, randomKey));
//        }

        nextButton.setText(c.Next());
        nextButton.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                icingShadow.onHistoryChanged(iCing.CING_LOG_STATE);
            }
        });

        final HorizontalPanel horizontalPanelBackNext = new HorizontalPanel();
        horizontalPanelBackNext.setSpacing(iCing.margin);
        verticalPanel.add(horizontalPanelBackNext);
        final Button backButton = new Button();
        horizontalPanelBackNext.add(backButton);
        backButton.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                icingShadow.onHistoryChanged(iCing.OPTIONS_STATE);
//                History.back();
            }
        });
        backButton.setText(c.Back());
        horizontalPanelBackNext.add(backButton);
        horizontalPanelBackNext.add(nextButton);

        nextButton.setTitle(c.Goto_CING_log());

        cingQueryRun = new iCingQuery(icing);
        cingQueryRun.action.setValue(Settings.FORM_ACTION_RUN);
        verticalPanel.add(cingQueryRun.formPanel);

    }

    /** Save the options; like a get to the server.
     */
    protected void getCriteriaOnServer() {
        GenClient.showDebug("Now in saveCriteriaOnServer");
        submitButton.setEnabled(false); // only allow once. TODO: set to disabled after done debugging.
        HashMap<String, String> parameterMap = icing.criteria.getCriteria(cingQueryOptions.formVerticalPanel);
        if ( parameterMap == null ) {
            GenClient.showCodeBug("Failed to icing.criteria.getCriteria");
            return;
        }
        cingQueryOptions.formPanel.submit();
    }

    /** Call back method */
    protected void setCriteriaOnServer() {
        GenClient.showDebug("setCriteriaOnServer");
        icing.onHistoryChanged(iCing.CING_LOG_STATE);
        getRunOnServer();
    }
    
    /** Save the options; like a get to the server.
     */
    protected void getRunOnServer() {
        GenClient.showDebug("Now in getRunOnServer");

        
        String verbosity = icing.options.getVerbosity();
//        String imagery = icing.options.getImagery();
        String residue = icing.options.getResidue();
        String ensemble = icing.options.getEnsemble();
        GenClient.showDebug("verbosity: " + verbosity);
//        GenClient.showDebug("imagery: " + imagery);
        GenClient.showDebug("residue: " + residue);
        GenClient.showDebug("ensemble: " + ensemble);
        cingQueryRun.formVerticalPanel.add(new Hidden(Settings.FORM_PARM_VERBOSITY, icing.options.getVerbosity()));
//        cingQueryRun.formVerticalPanel.add(new Hidden(Settings.FORM_PARM_IMAGERY, icing.options.getImagery()));
        cingQueryRun.formVerticalPanel.add(new Hidden(Settings.FORM_PARM_RESIDUES, icing.options.getResidue()));
        cingQueryRun.formVerticalPanel.add(new Hidden(Settings.FORM_PARM_ENSEMBLE, icing.options.getEnsemble()));
        cingQueryRun.formPanel.submit();
    }
    
    /** Save the options; like a get to the server.
     */
    protected void setRunOnServer() {
        GenClient.showDebug("Now in setRunOnServer");
        icing.report.showResults();
    }
}
