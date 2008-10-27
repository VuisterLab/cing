package cing.client;

import com.google.gwt.user.client.History;
import com.google.gwt.user.client.ui.Composite;

public class iCingView extends Composite {

	iCing icing = null;
	private String state;

	public iCingView() {
	}

	/**
	 * Make the view visible and remember it in browser history
	 * 
	 */
	public void enterView() {
		// Before clearing it; have the browser remember it.
		if (isVisible()) {
			General.showDebug("For view: " + getClass().toString() + " was already visible; no change was made.");
			return;
		}
		String state = getState();
		if (state == null) {
			General.showError("Failed to get state for view" + getClass().toString() + "; making no change");
			return;
		}
		General.showDebug("Added history item for state: " + state);
		setVisible(true);
		boolean issueEvent = false;
		History.newItem(state, issueEvent);
	}

	public void setIcing(iCing icing) {
		this.icing = icing;
	}

	public void setState(String state) {
		this.state = state;
	}

	public String getState() {
		return state;
	}
}
