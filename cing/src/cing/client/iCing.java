package cing.client;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import cing.client.i18n.iCingConstants;

import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.Element;
import com.google.gwt.dom.client.HeadElement;
import com.google.gwt.dom.client.Node;
import com.google.gwt.dom.client.NodeList;
import com.google.gwt.http.client.UrlBuilder;
import com.google.gwt.i18n.client.LocaleInfo;
import com.google.gwt.user.client.Command;
import com.google.gwt.user.client.DOM;
import com.google.gwt.user.client.History;
import com.google.gwt.user.client.HistoryListener;
import com.google.gwt.user.client.Random;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.Window.Location;
import com.google.gwt.user.client.ui.ChangeListener;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.HasVerticalAlignment;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.MenuBar;
import com.google.gwt.user.client.ui.RichTextArea;
import com.google.gwt.user.client.ui.RootPanel;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

public class iCing implements EntryPoint, HistoryListener {
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
	public static final String MAINTENANCE_STATE = "maintenance";
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
	 * How often does iCing check and update asynchronously; DEFAULT 4000 for
	 * production. Not in use for now.
	 */
	public static final int REFRESH_INTERVAL = 2000;
	public static final int REFRESH_INTERVAL_LOG = 4000;

	/** Class settings */
	public static iCingConstants c;
	// public static String currentAccessKey = "234567";
	public static String currentAccessKey = null;
	public static String currentUserId = "ano"; // TODO: implement security
	// functionality later.

	/**
	 * NB the html text eol have to be lowercase \<br\>
	 * or \
	 *
	 * <pre\>
	 */
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
	Maintenance maintenance;

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
		// Window.alert(c.Uncaught_ex() +GenClient.eol + e);
		// }
		// });

		c = GWT.create(iCingConstants.class);
		// Watch out because although this setting is needed here; there's
		// another needed at the end of this routine too.
		if (Settings.DO_DEBUG) {
			GenClient.setVerbosityToDebug();
		}
		currentAccessKey = getNewAccessKey();

		login = new Login();
		welcome = new Welcome();
		logView = new LogView();
		cingLogView = new CingLogView();
		options = new Options();
		preferences = new Preferences();
		criteria = new Criteria();
		runView = new RunView();
		report = new Report();
		fileView = new FileView();
		maintenance = new Maintenance();

		showMenu(); // Needs to happen after views have been initialized.

		// Order matters. Status is sometimes displayed so needs to be last.
		views = new ArrayList();
		views.add(logView); // Important to keep this one first so that others
		// can log into it.
		views.add(welcome);
		views.add(fileView);
		views.add(cingLogView);
		views.add(login);
		views.add(options);
		views.add(preferences);
		views.add(criteria);
		views.add(report);
		views.add(runView);
		views.add(maintenance);

		for (iCingView v : views) {
			vPanel.add(v);
			v.setIcing(this);
			v.setVisible(false);
		}
		vPanel.setSpacing(5);

		setVerbosityToDebug(Settings.DO_DEBUG); // partner with the above call
		// to
		showLoadingMessage(false);
		showFooter();

		History.addHistoryListener(this);
		// If the application starts with no history token, redirect to a new
		// state.
		String initToken = History.getToken();
		if (initToken.length() == 0) {
			// History.newItem();
			// initToken = iCing.MAINTENANCE_STATE;
			initToken = iCing.FILE_STATE;
			// initToken = iCing.LOG_STATE;
		}
		onHistoryChanged(initToken);

		String userAgent = UtilsJS.getUserAgent().toLowerCase();
		/**
		 * Considering http://msdn.microsoft.com/en-us/library/ms537503.aspx
		 * E.g. Windows-RSS-Platform/1.0 (MSIE 7.0; Windows NT 5.1)
		 */
		String msg = "userAgent: [" + userAgent + "]";
		GenClient.showDebug(msg);
		if (userAgent.contains("msie")) {
			showBrowserWarning();
		}

	}

	private void showFooter() {
		// String x = null;
		String cingRevisionUrl = Settings.CING_REVISION_URL + Settings.REVISION;
		String cingRevisionhtml = "iCing " + "(<a href=\"" + cingRevisionUrl
				+ "\">r" + Settings.REVISION + "</a>)" + GenClient.eol;

		String imgHtml = "<img class=\"gwt-Image\" style=\"width:16px;height:12px;border:0px\" src=\"images/icon_email.gif\">";

		final HTML html = new HTML("<div id=\"footer\">" + GenClient.eol
				+ "<p align=\"center\">" + GenClient.eol + cingRevisionhtml
				+ "\t" + GenClient.eol + "Geerten W. Vuister"
				+ " <a href=\"mailto:g.vuister@science.ru.nl\">" + imgHtml
				+ "</a>, \t" + GenClient.eol + "Jurgen F. Doreleijers \t"
				+ "<a href=\"mailto:jurgend@cmbi.ru.nl\">" + imgHtml
				+ "</a> \t" + GenClient.eol + " " + c.and() + " \t"
				+ GenClient.eol + "Alan Wilter Sousa da Silva \t"
				+ "<a href=\"mailto:alanwilter@gmail.com\">" + imgHtml
				+ "</a> \t" + "</p>" + GenClient.eol + "</div>" + GenClient.eol);
		vPanel.add(html);
		html.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
	}

	public void onHistoryChanged(String historyToken) {
		if (historyToken == null || historyToken.length() == 0) {
			GenClient.showError("Got an unknown history token: ["
					+ historyToken + "]");
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
		if (iCing.MAINTENANCE_STATE.equals(historyToken)) {
			loadMaintenance();
			return;
		}

		GenClient.showError("Got an unknown history token: " + historyToken);
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

	public void showBrowserWarning() {
		About h = new About();
		String userAgent = UtilsJS.getUserAgent().toLowerCase();
		String msg = c.warningBrowser() + "[" + userAgent + "]" + "<BR>"
				+ c.PleaseUse();
		GenClient.showError(msg);
		h.setHTML(msg);
		h.details.setHTML(h.details.getHTML() + "<BR>" + c.for_help());
		h.show();
	}

	public void clearAllViews() {
		// GenClient.showDebug("Now in clearAllViews");
		for (iCingView v : views) {
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
		topPanel.setCellVerticalAlignment(iCingLogo,
				HasVerticalAlignment.ALIGN_MIDDLE);
		topPanel.setCellHorizontalAlignment(iCingLogo,
				HasHorizontalAlignment.ALIGN_LEFT);

		final VerticalPanel verticalPanel = new VerticalPanel();
		topPanel.add(verticalPanel);
		verticalPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_LEFT);
		verticalPanel.setVerticalAlignment(HasVerticalAlignment.ALIGN_MIDDLE);
		topPanel.setCellHorizontalAlignment(verticalPanel,
				HasHorizontalAlignment.ALIGN_LEFT);

		final Label icingLabel = new Label(c.iCing());
		verticalPanel.add(icingLabel);
		icingLabel.setStylePrimaryName("h1");

		final Label validationOfNmrLabel = new Label(c.iCing_subtitle());
		validationOfNmrLabel.setStylePrimaryName("h2");
		verticalPanel.add(validationOfNmrLabel);

		final VerticalPanel verticalPanel_1 = new VerticalPanel();
		topPanel.add(verticalPanel_1);
		verticalPanel_1
				.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		verticalPanel_1.setVerticalAlignment(HasVerticalAlignment.ALIGN_MIDDLE);
		topPanel.setCellHorizontalAlignment(verticalPanel_1,
				HasHorizontalAlignment.ALIGN_RIGHT);

		final HorizontalPanel horizontalPanel_1 = new HorizontalPanel();
		verticalPanel_1.add(horizontalPanel_1);
		horizontalPanel_1
				.setVerticalAlignment(HasVerticalAlignment.ALIGN_MIDDLE);
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
		/**
		 * Two letter codes are taken by ISO 639-1 specs at:
		 * http://www.sil.org/iso639-3/codes.asp?order=639_1
		 */
		localeMap.put("de", i++);
		localeMap.put("en", i++);
		localeMap.put("es", i++);
		localeMap.put("fr", i++);
		localeMap.put("it", i++);
		localeMap.put("ja", i++);
		localeMap.put("nl", i++);
		localeMap.put("pt", i++);
		localeMap.put("ru", i++);
		localeMap.put("zh", i++);

		listBoxLocale.addItem("Deutsch", "de");
		listBoxLocale.addItem("English", "en");
		listBoxLocale.addItem("Español", "es");
		listBoxLocale.addItem("Français", "fr");
		listBoxLocale.addItem("Italiano", "it");
		listBoxLocale.addItem("日本語", "ja");
		listBoxLocale.addItem("Nederlands", "nl");
		listBoxLocale.addItem("Português", "pt");
		listBoxLocale.addItem("Русский", "ru");
		listBoxLocale.addItem("中文", "zh");

		String currentLocale = LocaleInfo.getCurrentLocale().getLocaleName();
		if (currentLocale.equals("default")) {
			currentLocale = "en";
		}
		// GenClient.showDebug("localeMap: " + localeMap);
		// GenClient.showDebug("currentLocale: " + currentLocale);
		int idx = localeMap.get(currentLocale);
		if (idx < 0) {
			idx = 1; // en is default
		}
		listBoxLocale.setSelectedIndex(idx);

		listBoxLocale.addChangeListener(new ChangeListener() {
			public void onChange(Widget sender) {
				// Window.open(UtilsJS.getHostPageLocation() + "?locale="
				// + localeName, "_self", "");
				String localeName = listBoxLocale.getValue(listBoxLocale
						.getSelectedIndex());
				UrlBuilder builder = Location.createUrlBuilder().setParameter(
						"locale", localeName);
				Window.Location.replace(builder.buildString());
			}
		});

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
		// Command commandExit = new Command() {
		// public void execute() {
		// loadLoginView();
		// }
		// };
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

		Command commandPurgeProject = new Command() {
			public void execute() {
				// loadLogView();
				cingLogView.getPurgeProject();
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

		menuBar_iCing.addItem(c.About() + " iCing", commandAbout);
		menuBar_iCing.addItem(c.Preferences(), commandPref);
		menuBar.addItem(c.iCing(), menuBar_iCing);
		menuBar.addItem(c.File(), menuBar_file);
		menuBar_file.addItem(c.Upload(), commandFile);
		menuBar_file.addItem(c.PurgeProject(), commandPurgeProject);
		// menuBar_file.addItem(c.Exit(), commandExit);
		final MenuBar menuBar_edit = new MenuBar(true);
		// menuBar_edit.setVisible(false);// doesn't 'help'
		menuBar.addItem(c.Edit(), menuBar_edit);
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
		// MenuItem menuItem3D = menuBar.addItem(c.threeD(), (Command) null);
		// menuItem3D.addStyleDependentName("disabled"); // try to improve
		// styling.
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

	public void loadMaintenance() {
		clearAllViews();
		maintenance.enterView();
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
		String gwtStyleSheet = "css/gwt/" + CURRENT_THEME + "/" + CURRENT_THEME
				+ ".css";
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
						&& elem.getPropertyString("rel").equalsIgnoreCase(
								"stylesheet")) {
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
			GenClient
					.showError("Return since we already have the correct style sheets");
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
			 * The number of style sheets that have been loaded and executed
			 * this command.
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
				RootPanel.getBodyElement().getStyle().setProperty("display",
						"none");
				RootPanel.getBodyElement().getStyle()
						.setProperty("display", "");
				RootPanel.get().add(vPanel);
			}
		};
		StyleSheetLoader.loadStyleSheet(modulePath + gwtStyleSheet,
				getCurrentReferenceStyleName("gwt"), callback);

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
	 * Get the style name of the reference element defined in the current GWT
	 * theme style sheet.
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
	 * So this method is not in GenClient because all methods there are static
	 * Make sure that where ever the verbosity can be set to debug it is also
	 * calling this routine.
	 *
	 * @param doDebugNow
	 */
	public void setVerbosityToDebug(boolean doDebugNow) {
		if (doDebugNow) {
			GenClient.setVerbosityToDebug();
		}
		logView.startPnameButton.setVisible(doDebugNow);
	}

	public static String getNewAccessKey() {
		String allowedCharacters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
		String result = "";
		for (int i = 1; i <= Settings.accessKeyLength; i++) {
			int idxChar = Random.nextInt(allowedCharacters.length()); // equal
			// chance
			// for A
			// as
			// for
			// others.
			result += allowedCharacters.charAt(idxChar);
		}
		// result = "123456"; // TODO: disable for production.

		return result;
	}
}