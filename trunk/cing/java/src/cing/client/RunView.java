package cing.client;

import com.google.gwt.user.client.History;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
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
    static final Button saveOptionsButton = new Button();

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
                // submitButton.setText("Running...");
                run();
            }
        });
        submitButton.setEnabled(true);

        verticalPanelDec.add(html_2);
        verticalPanelDec.add(submitButton);

        /** Options block */
        saveOptionsButton.setTitle(c.Run_the_validati());
        verticalPanelDec.setCellHorizontalAlignment(saveOptionsButton, HasHorizontalAlignment.ALIGN_LEFT);

        saveOptionsButton.setText("saveOptionsButton");
        saveOptionsButton.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                getOptions();
            }
        });

        verticalPanel.add(saveOptionsButton);
        FormHandlerSpecific serverFormHandlerOptions = new FormHandlerSpecific(icing);
        cingQueryOptions = new iCingQuery(icing);
        cingQueryOptions.action.setValue(Settings.FORM_ACTION_OPTIONS);
        cingQueryOptions.setFormHandler(serverFormHandlerOptions);
        verticalPanel.add(cingQueryOptions.formPanel);
        for (int i = 0; i < 2; i++) { // testing if protocol can handle many params.
            String randomKey = iCing.getNewAccessKey();
            cingQueryOptions.formVerticalPanel.add(new Hidden(randomKey, randomKey));
        }

        nextButton.setText(c.Next());
        nextButton.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                icingShadow.onHistoryChanged(iCing.CING_LOG_STATE);
            }
        });
        // nextButton.setEnabled(false); //disable for testing it will be triggered by a run; or not...

        final HorizontalPanel horizontalPanelBackNext = new HorizontalPanel();
        horizontalPanelBackNext.setSpacing(iCing.margin);
        verticalPanel.add(horizontalPanelBackNext);
        final Button backButton = new Button();
        horizontalPanelBackNext.add(backButton);
        backButton.addClickListener(new ClickListener() {
            public void onClick(final Widget sender) {
                History.back();
            }
        });
        backButton.setText(c.Back());
        horizontalPanelBackNext.add(backButton);
        horizontalPanelBackNext.add(nextButton);

        nextButton.setTitle(c.Goto_CING_log());
        // verticalPanel.setCellHorizontalAlignment(nextButton, HasHorizontalAlignment.ALIGN_CENTER);
        // nextButton.setVisible(false);
        cingQueryRun = new iCingQuery(icing);
        cingQueryRun.action.setValue(Settings.FORM_ACTION_RUN);
        verticalPanel.add(cingQueryRun.formPanel);

    }

    /** Save the options; like a get to the server */
    protected void getOptions() {
        saveOptionsButton.setText("Saving options...");
        cingQueryOptions.formPanel.submit();
    }

    /** Call back method */
    protected void setOptions(String result) {
        saveOptionsButton.setText("Options saved: " + result);
    }

    protected void run() {
        submitButton.setEnabled(false);
        nextButton.setEnabled(true);
        icing.cingLogView.getProjectName();
        
        cingQueryRun.formVerticalPanel.add(new Hidden(Settings.FORM_PARM_VERBOSITY, icing.options.getVerbosity()));
        cingQueryRun.formVerticalPanel.add(new Hidden(Settings.FORM_PARM_IMAGERY, icing.options.getImagery()));
        cingQueryRun.formVerticalPanel.add(new Hidden(Settings.FORM_PARM_RESIDUES, icing.options.getResidue()));
        cingQueryRun.formVerticalPanel.add(new Hidden(Settings.FORM_PARM_ENSEMBLE, icing.options.getEnsemble()));
        cingQueryRun.formPanel.submit();
        icing.onHistoryChanged(iCing.CING_LOG_STATE);
    }
}
