package cing.client;

import com.google.gwt.user.client.History;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.PasswordTextBox;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;

public class Login extends Composite {
	iCingConstants c = iCing.c;	

	public Login() {

		final Grid grid = new Grid(4, 2);
		initWidget(grid);
		grid.setTitle(c.Login());
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

		grid.setWidget(2, 0, passwordPrompt);
		grid.setWidget(2, 1, passwordTextbox);

		grid.setWidget(3, 1, button);
	}

}
