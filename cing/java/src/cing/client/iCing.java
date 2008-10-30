package cing.client;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.Element;
import com.google.gwt.dom.client.HeadElement;
import com.google.gwt.dom.client.Node;
import com.google.gwt.dom.client.NodeList;
import com.google.gwt.i18n.client.LocaleInfo;
import com.google.gwt.user.client.Command;
import com.google.gwt.user.client.DOM;
import com.google.gwt.user.client.History;
import com.google.gwt.user.client.HistoryListener;
import com.google.gwt.user.client.Random;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.ChangeListener;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.HasVerticalAlignment;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.MenuBar;
import com.google.gwt.user.client.ui.MenuItem;
import com.google.gwt.user.client.ui.RichTextArea;
import com.google.gwt.user.client.ui.RootPanel;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

public class iCing implements EntryPoint, HistoryListener {
	/** Just the initial startup state; for client. Server debug is set in servlet. */
	public static final boolean doDebug = true;
	public static final String STRING_NA = "n/a";
	
	/** States of the gui */
	public static final String WELCOME_STATE = "welcome";
	public static final String PREFERENCES_STATE = "preferences";
	public static final String FILE_STATE = "file";
	public static final String LOG_STATE = "log";
	public static final String CING_LOG_STATE = "cingLog";
	public static final String CRITERIA_STATE = "criteria";
	public static final String OPTIONS_STATE = "options";
	public static final String RUN_STATE = "run";
	public static final String REPORT_STATE = "report";
	public static final String LOGIN_STATE = "login";

	public static String CURRENT_THEME = "standard";

	/** GUI settings */
	public static final int margin = 11;
	public static final int yLocTopPanel = margin;
	public static final int yLocMenu = 60;
	public static final int yLocMainWindow = 110;
	public static final int WIDTH_MENU = 900;
	public static final String widthMenuStr = Integer.toString(WIDTH_MENU);
	/**
	 * How often does iCing check and update asynchronously; DEFAULT 4000 for production.
	 */
	public static final int REFRESH_INTERVAL = 2000;
	public static final int REFRESH_INTERVAL_LOG = 4000;

	/** Class settings */
	public static iCingConstants c;
	// public static String currentAccessKey = "234567";
	public static String currentAccessKey = null;
	public static String currentUserId = "jd3"; // TODO: implement security functionality later.

	/** NB the html text eol have to be lowercase \<br\> or \<pre\> */
	public static final RichTextArea area = new RichTextArea();
	public static final RichTextArea cingArea = new RichTextArea();

	public static boolean textIsReversedArea = false;
	public static boolean textIsReversedCingArea = false;

	ArrayList<iCingView> views;
	Welcome welcome;
	FileView fileView;
	LogView logView;
	CingLogView cingLogView;
	Login login;
	Options options;
	Preferences preferences;
	Criteria criteria;
	Report report;
	RunView runView;
	Footer footer;

	private RootPanel rootPanel = RootPanel.get();
	VerticalPanel vPanel = new VerticalPanel();
	public String projectName;

	public HistoryListener historyListener;


	public void onModuleLoad() {
		// set uncaught exception handler for a production version this might be
		// off. JFD prefers
		// to see these in the hosted mode browser. When the below statement is
		// enabled the
		// hosted mode doesn't show a popup!
		// GWT.setUncaughtExceptionHandler(new GWT.UncaughtExceptionHandler() {
		// public void onUncaughtException(Throwable e) {
		// Window.alert(c.Uncaught_ex() +General.eol + e);
		// }
		// });
		c = GWT.create(iCingConstants.class);
		// Watch out because although this setting is needed here; there's
		// another needed at the end of this routine too.
		if (iCing.doDebug) {
			General.setVerbosityToDebug();
		}
		currentAccessKey = getNewAccessKey();
		// Date today = new Date();
		// VERSION = DateTimeFormat.getShortDateTimeFormat().format(today);

		showMenu();

		login = new Login();
		welcome = new Welcome();
		logView = new LogView();
		cingLogView = new CingLogView();
		options = new Options();
		preferences = new Preferences();
		criteria = new Criteria();
		runView = new RunView();
		report = new Report();
		footer = new Footer();
		fileView = new FileView();

		// Order matters. Status is sometimes displayed so needs to be last.
		views = new ArrayList();
		views.add(welcome);
		views.add(fileView);
		views.add(logView);
		views.add(cingLogView);
		views.add(login);
		views.add(options);
		views.add(preferences);
		views.add(welcome);
		views.add(criteria);
		views.add(report);
		views.add(runView);
		views.add(footer);

		for (iCingView v : views) {
			vPanel.add(v); // All on top of each
			v.setIcing(this);

			if (v instanceof Footer) { // always present view.
				continue;
			}
			v.setVisible(false);
		}
		vPanel.setSpacing(5);

		setVerbosityToDebug(iCing.doDebug); // partner with the above call to
		showLoadingMessage(false);

		History.addHistoryListener(this);
		// If the application starts with no history token, redirect to a new
		// state.
		String initToken = History.getToken();
		if (initToken.length() == 0) {
			// History.newItem();
			// initToken = Keys.FILE_STATE;
			initToken = iCing.LOG_STATE;
		}
		onHistoryChanged(initToken);
	}

	public void onHistoryChanged(String historyToken) {
		if (historyToken == null || historyToken.length() == 0) {
			General.showError("Got an unknown history token: [" + historyToken + "]");
		}
		if (iCing.WELCOME_STATE.equals(historyToken)) {
			loadWelcomeView();
			return;
		}
		if (LOGIN_STATE.equals(historyToken)) {
			loadLoginView();
			return;
		}
		if (iCing.FILE_STATE.equals(historyToken)) {
			loadFileView();
			return;
		}
		if (iCing.LOG_STATE.equals(historyToken)) {
			loadLogView();
			return;
		}
		if (iCing.CING_LOG_STATE.equals(historyToken)) {
			loadCingLogView();
			return;
		}
		if (iCing.CRITERIA_STATE.equals(historyToken)) {
			loadCriteriaView();
			return;
		}
		if (iCing.REPORT_STATE.equals(historyToken)) {
			loadReportView();
			return;
		}
		if (iCing.OPTIONS_STATE.equals(historyToken)) {
			loadOptionsView();
			return;
		}
		if (iCing.RUN_STATE.equals(historyToken)) {
			loadRunView();
			return;
		}
		if (iCing.PREFERENCES_STATE.equals(historyToken)) {
			loadPreferencesView();
			return;
		}

		General.showError("Got an unknown history token: " + historyToken);
	}

	/**
	 * Disable the loading message.
	 */
	public void showLoadingMessage(boolean statusLoaded) {
		Element loadingDiv = DOM.getElementById("loading");
		String styleDisplay = "none";
		if (statusLoaded) {
			styleDisplay = "block";
		}
		loadingDiv.getStyle().setProperty("display", styleDisplay);
	}

	public void clearAllViews() {
		// General.showDebug("Now in clearAllViews");
		for (iCingView v : views) {
			if (v instanceof Footer) { // not a real view.
				continue;
			}
			v.setVisible(false);
		}
	}

	private void showMenu() {

		final HorizontalPanel topPanel = new HorizontalPanel();
		// rootPanel.add(topPanel, 11, 11);
		topPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		topPanel.setVerticalAlignment(HasVerticalAlignment.ALIGN_MIDDLE);

		final Image iCingLogo = new Image();
		topPanel.add(iCingLogo);
		iCingLogo.setSize("49", "40");
		iCingLogo.setUrl("images/cing.png");
		topPanel.setCellVerticalAlignment(iCingLogo, HasVerticalAlignment.ALIGN_MIDDLE);
		topPanel.setCellHorizontalAlignment(iCingLogo, HasHorizontalAlignment.ALIGN_LEFT);

		final VerticalPanel verticalPanel = new VerticalPanel();
		topPanel.add(verticalPanel);
		verticalPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_LEFT);
		verticalPanel.setVerticalAlignment(HasVerticalAlignment.ALIGN_MIDDLE);
		topPanel.setCellHorizontalAlignment(verticalPanel, HasHorizontalAlignment.ALIGN_LEFT);

		final Label icingLabel = new Label(c.iCing());
		verticalPanel.add(icingLabel);
		icingLabel.setStylePrimaryName("h1");

		final Label validationOfNmrLabel = new Label(c.iCing_subtitle());
		validationOfNmrLabel.setStylePrimaryName("h2");
		verticalPanel.add(validationOfNmrLabel);

		final VerticalPanel verticalPanel_1 = new VerticalPanel();
		topPanel.add(verticalPanel_1);
		verticalPanel_1.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		verticalPanel_1.setVerticalAlignment(HasVerticalAlignment.ALIGN_MIDDLE);
		topPanel.setCellHorizontalAlignment(verticalPanel_1, HasHorizontalAlignment.ALIGN_RIGHT);

		final HorizontalPanel horizontalPanel_1 = new HorizontalPanel();
		verticalPanel_1.add(horizontalPanel_1);
		horizontalPanel_1.setVerticalAlignment(HasVerticalAlignment.ALIGN_MIDDLE);
		horizontalPanel_1.setSpacing(5);

		final Image imageI18n = new Image();
		horizontalPanel_1.add(imageI18n);
		imageI18n.setSize("16", "16");
		imageI18n.setUrl("images/locale.png");

		final ListBox listBoxLocale = new ListBox();
		horizontalPanel_1.add(listBoxLocale);
		// listBoxLocale.setTabIndex(1);
		listBoxLocale.setWidth("15em");
		// listBoxLocale.setEnabled(false);
		// // Map to location in list.
		HashMap<String, Integer> localeMap = new HashMap<String, Integer>();
		int i = 0;
		localeMap.put("cn", i++);
		localeMap.put("de", i++);
		localeMap.put("en", i++);
		localeMap.put("es", i++);
		localeMap.put("fr", i++);
		localeMap.put("it", i++);
		localeMap.put("nl", i++);
		localeMap.put("pt", i++);

		listBoxLocale.addItem("??????", "cn");
		listBoxLocale.addItem("Deutsch", "de");
		listBoxLocale.addItem("English", "en");
		listBoxLocale.addItem("Espa??ol", "es");
		listBoxLocale.addItem("Fran??ais", "fr");
		listBoxLocale.addItem("Italiano", "it");
		listBoxLocale.addItem("Nederlands", "nl");
		listBoxLocale.addItem("Portugu??s", "pt");
		String currentLocale = LocaleInfo.getCurrentLocale().getLocaleName();

		int idx = 2;
		// if (currentLocale != null) {
		// if (localeMap != null) { // shouldn't have happened.
		idx = localeMap.get(currentLocale);
		if (idx < 0) {
			idx = 2; // en is default
		}
		// } else {
		// General.showWarning("Failed to find localeMap");
		// }
		// } else {
		// General.showWarning("Failed to find currentLocale");
		// }
		listBoxLocale.setSelectedIndex(idx);

		listBoxLocale.addChangeListener(new ChangeListener() {
			public void onChange(Widget sender) {
				String localeName = listBoxLocale.getValue(listBoxLocale.getSelectedIndex());
				Window.open(UtilsJS.getHostPageLocation() + "?locale=" + localeName, "_self", "");
			}
		});

		// // Add the option to change the style
		// final HorizontalPanel styleWrapper = new HorizontalPanel();
		// verticalPanel_1.add(styleWrapper);
		//
		// for (i = 0; i < STYLE_THEMES.length; i++) {
		// final ThemeButton button = new ThemeButton(STYLE_THEMES[i]);
		// styleWrapper.add(button);
		// button.addClickListener(new ClickListener() {
		// public void onClick(Widget sender) {
		// Window.alert("Style selection currently buggy; disabled for now.");
		// return;
		// // // Update the current theme
		// // CUR_THEME = button.getTheme();
		// // General.showError("Selecting theme: " +
		// // button.getTheme());
		// //Window.alert("Feature currently buggy; best to reload now."
		// // );
		// // // if ( debugOn ) {
		// // // // Reload the current tab, loading the new theme if
		// // // necessary
		// // // TabBar bar = ((TabBar) this.getContentTitle());
		// // // bar.selectTab(bar.getSelectedTab());
		// // // Load the new style sheets
		// // updateStyleSheets();
		// // } else {
		// //Window.alert("Feature currently buggy; best to reload now."
		// // );
		// // }
		// }
		// });
		// }

		final MenuBar menuBar = new MenuBar();
		final MenuBar menuBar_file = new MenuBar(true);
		final MenuBar menuBar_iCing = new MenuBar(true);

		Command commandCriteria = new Command() {
			public void execute() {
				loadCriteriaView();
			}
		};
		Command commandFile = new Command() {
			public void execute() {
				loadFileView();
			}
		};
		Command commandLog = new Command() {
			public void execute() {
				loadLogView();
			}
		};
		Command commandCingLog = new Command() {
			public void execute() {
				loadCingLogView();
			}
		};
		Command commandExit = new Command() {
			public void execute() {
				loadLoginView();
			}
		};
		Command commandPref = new Command() {
			public void execute() {
				loadPrefView();
			}
		};
		Command commandWelcome = new Command() {
			public void execute() {
				loadWelcomeView();
			}
		};
		Command commandOptions = new Command() {
			public void execute() {
				loadOptionsView();
			}
		};

		Command commandRun = new Command() {
			public void execute() {
				loadRunView();
			}
		};
		Command commandReport = new Command() {
			public void execute() {
				loadReportView();
			}
		};
		Command commandAbout = new Command() {
			public void execute() {
				(new About()).show();
			}
		};

		Command commandHelp = new Command() {
			public void execute() {
				About h = new About();
				h.setHTML(c.About()); // TODO: seems without effect.
				h.details.setHTML(h.details.getHTML() + "<BR>" + c.for_help());
				h.show();
			}
		};

		menuBar_iCing.addItem(c.About(), commandAbout);
		menuBar_iCing.addItem(c.Preferences(), commandPref);
		menuBar.addItem(c.iCing(), menuBar_iCing);
		menuBar.addItem(c.File(), menuBar_file);
		menuBar_file.addItem(c.New(), commandFile);
		menuBar_file.addItem(c.Exit(), commandExit);
		final MenuBar menuBar_edit = new MenuBar(true);
		menuBar_edit.setVisible(false);// doesn't 'help'
		// menuBar.addItem(c.Edit(), menuBar_edit);
		menuBar_edit.addItem(c.Criteria(), commandCriteria);
		menuBar_edit.addItem(c.Options(), commandOptions);
		menuBar.addItem(c.Run(), commandRun);
		final MenuBar menuBar_view = new MenuBar(true);
		menuBar.addItem(c.View(), menuBar_view);

		menuBar_view.addItem(c.Report(), commandReport);
		// menuItemReport.addStyleDependentName("disabled");
		menuBar_view.addItem(c.Log() + " CING", commandCingLog);
		// menuItemLogCing.addStyleDependentName("disabled");
		menuBar_view.addItem(c.Log() + " iCing", commandLog);
		MenuItem menuItem3D = menuBar.addItem(c.threeD(), (Command) null);
		menuItem3D.addStyleDependentName("disabled"); // try to improve styling.
		menuBar.setWidth(widthMenuStr);
		final MenuBar menuBar_help = new MenuBar(true);
		menuBar.addItem(c.Help(), menuBar_help);
		menuBar_help.addItem(c.Welcome(), commandWelcome);
		menuBar_help.addItem(c.Help(), commandHelp);

		rootPanel.add(vPanel);
		// rootPanel.setWidth("950px");
		vPanel.setWidth("100%");
		vPanel.add(topPanel);
		topPanel.setWidth("100%");
		topPanel.setSpacing(11);
		vPanel.add(menuBar);

	}

	public void loadLoginView() {
		clearAllViews();
		login.enterView();
	}

	public void loadWelcomeView() {
		clearAllViews();
		welcome.enterView();
	}

	public void loadReportView() {
		clearAllViews();
		report.enterView();
	}

	public void loadOptionsView() {
		clearAllViews();
		options.enterView();
	}

	public void loadRunView() {
		clearAllViews();
		runView.enterView();
	}

	public void loadPrefView() {
		clearAllViews();
		preferences.enterView();
	}

	public void loadCriteriaView() {
		clearAllViews();
		criteria.enterView();
	}

	public void loadPreferencesView() {
		clearAllViews();
		preferences.enterView();
	}

	public void loadFileView() {
		clearAllViews();
		fileView.enterView();
	}

	public void loadLogView() {
		clearAllViews();
		logView.enterView();
	}

	public void loadCingLogView() {
		clearAllViews();
		cingLogView.enterView();
	}

	/**
	 * Update the style sheets to reflect the current theme and direction.
	 */
	@SuppressWarnings("unused")
	private void updateStyleSheets() {
		// Generate the names of the style sheets to include
		String gwtStyleSheet = "css/gwt/" + CURRENT_THEME + "/" + CURRENT_THEME + ".css";
		// String showcaseStyleSheet = "css/sc/" + CUR_THEME + "/Showcase.css";
		// if (LocaleInfo.getCurrentLocale().isRTL()) {
		// gwtStyleSheet = gwtStyleSheet.replace(".css", "_rtl.css");
		// // showcaseStyleSheet = showcaseStyleSheet.replace(".css",
		// "_rtl.css");
		// }

		// Find existing style sheets that need to be removed
		boolean styleSheetsFound = false;
		final HeadElement headElem = StyleSheetLoader.getHeadElement();
		final List<Element> toRemove = new ArrayList<Element>();
		NodeList<Node> children = headElem.getChildNodes();
		for (int i = 0; i < children.getLength(); i++) {
			Node node = children.getItem(i);
			if (node.getNodeType() == Node.ELEMENT_NODE) {
				Element elem = Element.as(node);
				if (elem.getTagName().equalsIgnoreCase("link")
						&& elem.getPropertyString("rel").equalsIgnoreCase("stylesheet")) {
					styleSheetsFound = true;
					String href = elem.getPropertyString("href");
					// If the correct style sheets are already loaded, then we
					// should have
					// nothing to remove.
					// if (!href.contains(gwtStyleSheet) &&
					// !href.contains(showcaseStyleSheet)) {
					if (!href.contains(gwtStyleSheet)) {
						toRemove.add(elem);
					}
				}
			}
		}

		if (styleSheetsFound && toRemove.size() == 0) {
			General.showError("Return since we already have the correct style sheets");
			return;
		}

		// Detach the app while we manipulate the styles to avoid rendering
		// issues
		RootPanel.get().remove(vPanel);

		// Remove the old style sheets
		for (Element elem : toRemove) {
			headElem.removeChild(elem);
		}

		// Load the GWT theme style sheet
		String modulePath = GWT.getModuleBaseURL();
		Command callback = new Command() {
			/**
			 * The number of style sheets that have been loaded and executed this command.
			 */
			private int numStyleSheetsLoaded = 0;

			public void execute() {
				// Wait until all style sheets have loaded before re-attaching
				// the app
				numStyleSheetsLoaded++;
				if (numStyleSheetsLoaded < 2) {
					return;
				}

				// Different themes use different background colors for the body
				// element, but IE only changes the background of the visible
				// content on the page instead of changing the background color
				// of the
				// entire page. By changing the display style on the body
				// element, we
				// force IE to redraw the background correctly.
				RootPanel.getBodyElement().getStyle().setProperty("display", "none");
				RootPanel.getBodyElement().getStyle().setProperty("display", "");
				RootPanel.get().add(vPanel);
			}
		};
		StyleSheetLoader.loadStyleSheet(modulePath + gwtStyleSheet, getCurrentReferenceStyleName("gwt"), callback);

		// Load the showcase specific style sheet after the GWT theme style
		// sheet so
		// that custom styles supercede the theme styles.
		// StyleSheetLoader.loadStyleSheet(modulePath + showcaseStyleSheet,
		// getCurrentReferenceStyleName("Application"), // should
		// // this
		// // really
		// // be
		// // Application
		// // instead of iCing? YES
		// callback);
	}

	/**
	 * Get the style name of the reference element defined in the current GWT theme style sheet.
	 * 
	 * @param prefix
	 *            the prefix of the reference style name
	 * @return the style name
	 */
	private String getCurrentReferenceStyleName(String prefix) {
		String gwtRef = prefix + "-Reference-" + CURRENT_THEME;
		if (LocaleInfo.getCurrentLocale().isRTL()) {
			gwtRef += "-rtl";
		}
		return gwtRef;
	}

	/**
	 * So this method is not in General because all methods there are static Make sure that where ever the verbosity can
	 * be set to debug it is also callign this routine.
	 * 
	 * @param doDebugNow
	 */
	public void setVerbosityToDebug(boolean doDebugNow) {
		if (doDebugNow) {
			General.setVerbosityToDebug();
		}
		logView.startPnameButton.setVisible(doDebugNow);
	}

	public static String getNewAccessKey() {
		String allowedCharacters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
		String result = "";
		for (int i = 1; i <= Keys.accessKeyLength; i++) {
			int idxChar = Random.nextInt(allowedCharacters.length()); // equal chance for A as for others.
			result += allowedCharacters.charAt(idxChar);
			// TODO: generate on server with cross check on availability...
		}
		return result;
	}
}