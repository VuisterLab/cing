package cing.client;


import com.google.gwt.user.client.History;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.DecoratorPanel;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.PasswordTextBox;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

public class Login extends iCingView {
	iCingConstants c = iCing.c;	
	DecoratorPanel decPanel = new DecoratorPanel();

	public Login() {
		setState(iCing.LOGIN_STATE);
		final VerticalPanel verticalPanelTop = new VerticalPanel();
		initWidget(verticalPanelTop);
		final Label html_1 = new Label( c.Login() );
		html_1.setStylePrimaryName("h1");
		verticalPanelTop.add(html_1);
		verticalPanelTop.add(decPanel);
				
		final Grid grid = new Grid(4, 2);
		decPanel.setWidget(grid);
		grid.setTitle(c.Login()); // pretty useless.
		grid.setCellPadding(10);
		setTitle(c.Login());

		final Label loginPrompt = new Label(c.Please_log_in());
//				"Please log in; leaving fields empty.");
		final Label namePrompt = new Label(c.Name());
		final TextBox nameTextbox = new TextBox();
		final Label passwordPrompt = new Label(c.Password());
		final PasswordTextBox passwordTextbox = new PasswordTextBox();
		final Button button = new Button(c.Login());

		nameTextbox.setEnabled(false);
		passwordTextbox.setEnabled(false);

		button.addClickListener(new ClickListener() {
			public void onClick(Widget sender) {
				History.newItem(iCing.WELCOME_STATE);
			}
		});

		
		loginPrompt.addStyleName("loginPrompt");
		/**
		nameTextbox.addStyleName("nameField");
		passwordTextbox.addStyleName("passwordField");
*/
		grid.setWidget(0, 1, loginPrompt);
		grid.setWidget(1, 0, namePrompt);
		grid.setWidget(1, 1, nameTextbox);
		nameTextbox.setTitle("Short name like JoeNmr (no special characters)");

		grid.setWidget(2, 0, passwordPrompt);
		grid.setWidget(2, 1, passwordTextbox);
		passwordTextbox.setTitle("Short secret word like 234567.");

		grid.setWidget(3, 1, button);
		button.setTitle("Advance to file upload.");
	}

}
