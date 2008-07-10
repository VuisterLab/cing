package cing.client;

import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.RootPanel;
import com.google.gwt.user.client.ui.Widget;

/**
 * Entry point classes define <code>onModuleLoad()</code>.
 */
public class iCing implements EntryPoint {
	private Button clickMeButton;
	public void onModuleLoad() {
		RootPanel rootPanel = RootPanel.get();

		clickMeButton = new Button();
		rootPanel.add(clickMeButton);
		clickMeButton.setText("Click me!");
		clickMeButton.addClickListener(new ClickListener() {
			public void onClick(Widget sender) {
				Window.alert("Hello, GWT World!");
			}
		});
	}
}
