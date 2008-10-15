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
import com.google.gwt.user.client.History;
import com.google.gwt.user.client.HistoryListener;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.ChangeListener;
import com.google.gwt.user.client.ui.ClickListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.HasVerticalAlignment;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.MenuBar;
import com.google.gwt.user.client.ui.MenuItem;
import com.google.gwt.user.client.ui.RootPanel;
import com.google.gwt.user.client.ui.ToggleButton;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

public class iCing implements EntryPoint, HistoryListener {

	public static final String VERSION = "0.0.0";
	public static final String RPC_URL = "../cgi-bin/iCing";
	
	public static final String LOGIN_STATE = "login";
	public static final String WELCOME_STATE = "welcome";
	public static final String FILE_STATE = "file";
	public static final String LOG_STATE = "log";
	public static final String CRITERIA_STATE = "criteria";
	public static final String PREFERENCES_STATE = "preferences";

	public static final String FORM_ACCESS_KEY = "AccessKey";
	public static final String FORM_USER_ID = "UserId";
	public static final String FORM_UPLOAD_FILE_BASE = "UploadFile";
	public static final String JSON_ERROR_STATUS = "error";

	
	/** WATCH out, this needs to be in sync with FileView form.
	 * It's the file and the access key and user id.
	 * */
	public static final int FORM_PART_COUNT = 3;
	
	/**
	 * The available style themes that the user can select.
	 */
	String[] STYLE_THEMES = { "standard", "chrome", "dark" }; 

	/**
	 * The current style theme.
	 */
	public static String CUR_THEME = "standard";

	public static final int margin = 11;
	public static final int yLocTopPanel = 11;
	public static final int yLocMenu = 60;
	public static final int yLocMainWindow = 110;
	public static final String widthMenu = "550";
	protected static boolean soundOn = true;
	protected static boolean debugOn = true;

	public static iCingConstants c;
	public static String currentAccessKey = Options.getNewAccessKey();
	public static String currentUserId = "JoeNmr";  // TODO: implement security functionality later.

	/** NB the html text eol have to be lowercase \<br\> or \<pre\> */
	public static final RichTextAreaIcing area = new RichTextAreaIcing();
	public static final RichTextAreaIcing statusArea = new RichTextAreaIcing();
//	public static final int areaTail = new Boolean(false);

	ArrayList<Composite> views;
	Welcome welcome;
	FileView fileView;
	LogView logView;
	Login login;
	Options options; 
	Preferences preferences;
	Criteria criteria;
	Status status;

	private RootPanel rootPanel = RootPanel.get();
	VerticalPanel vPanel = new VerticalPanel();

	public void onModuleLoad() {
		// set uncaught exception handler for a production version this might be off. JFD prefers
		// to see these in the hosted mode browser. When the below statement is enabled the
		// hosted mode doesn't show a popup!
//		GWT.setUncaughtExceptionHandler(new GWT.UncaughtExceptionHandler() {
//			public void onUncaughtException(Throwable e) {
//				Window.alert(c.Uncaught_ex() + "\n" + e);
//			}
//		});
		c = GWT.create(iCingConstants.class);
		General.setVerbosityToDebug();

		showMenu();

		status = new Status();
		login = new Login();
		welcome = new Welcome();
		fileView = new FileView();
		logView = new LogView();
		options = new Options();
		preferences = new Preferences();
		criteria = new Criteria();

		views = new ArrayList();
		views.add(welcome);
		views.add(fileView);
		views.add(logView);
		views.add(login);
		views.add(options);
		views.add(preferences);
		views.add(welcome);
		views.add(criteria);
		views.add(status);

		for (Composite v : views) {
			vPanel.add(v); // All on top of each
		}
		vPanel.setSpacing(5);
		clearAllViews();
		setupHistory();
	}

	private void setupHistory() {
		History.addHistoryListener(this);
		this.onHistoryChanged(FILE_STATE);	
//		this.onHistoryChanged(WELCOME_STATE);	
	}

	public void onHistoryChanged(String historyToken) {
		if (WELCOME_STATE.equals(historyToken)) {
			loadWelcomeView();
		}
		if (LOGIN_STATE.equals(historyToken)) {
			loadLoginView();
		}
		if (FILE_STATE.equals(historyToken)) {
			loadFileView();
		}
		if (LOG_STATE.equals(historyToken)) {
			loadLogView();
		}
		if (CRITERIA_STATE.equals(historyToken)) {
			loadCriteriaView();
		}
		if (PREFERENCES_STATE.equals(historyToken)) {
			loadPreferencesView();
		}
	}

	public void clearAllViews() {
		for (Composite v : views) {
			// RootPanel.get().add(v, margin, yLocMainWindow);
			if ( v instanceof Status ) { // not a real view.
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
		imageI18n.setUrl("images/showcase/locale.png");

		final ListBox listBoxLocale = new ListBox();
		horizontalPanel_1.add(listBoxLocale);
		listBoxLocale.setTabIndex(1);
		listBoxLocale.setWidth("15em");

		// Map to location in list.
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

		listBoxLocale.addItem(c.cn(), "cn");
		listBoxLocale.addItem(c.de(), "de");
		listBoxLocale.addItem(c.en(), "en");
		listBoxLocale.addItem(c.es(), "es"); 
		listBoxLocale.addItem(c.fr(), "fr");
		listBoxLocale.addItem(c.it(), "it");
		listBoxLocale.addItem(c.nl(), "nl");
		listBoxLocale.addItem(c.pt(), "pt");
	    String currentLocale = LocaleInfo.getCurrentLocale().getLocaleName();

	    int idx = localeMap.get(currentLocale);
	    if ( idx < 0 ) {
	    	idx = 2; // en is default
	    } 
    	listBoxLocale.setSelectedIndex(idx);

		listBoxLocale.addChangeListener(new ChangeListener() {
			public void onChange(Widget sender) {
				String localeName = listBoxLocale.getValue(listBoxLocale.getSelectedIndex());
				Window.open(UtilsJS.getHostPageLocation() + "?locale=" + localeName, "_self", "");
			}
		});

		// Add the option to change the style
		final HorizontalPanel styleWrapper = new HorizontalPanel();
		verticalPanel_1.add(styleWrapper);

		for ( i = 0; i < STYLE_THEMES.length; i++) {
			final ThemeButton button = new ThemeButton(STYLE_THEMES[i]);
			styleWrapper.add(button);
			button.addClickListener(new ClickListener() {
				public void onClick(Widget sender) {
					// Update the current theme
					CUR_THEME = button.getTheme();
					General.showError("Selecting theme: " + button.getTheme());
					Window.alert("Feature currently buggy; best to reload now.");
					// if ( debugOn ) {
					// // Reload the current tab, loading the new theme if
					// necessary
					// TabBar bar = ((TabBar) this.getContentTitle());
					// bar.selectTab(bar.getSelectedTab());
					// Load the new style sheets
					updateStyleSheets();
					// } else {
					//Window.alert("Feature currently buggy; best to reload now."
					// );
					// }
				}
			});
		}

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
				Window.alert(c.unfortunatel());
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
		menuBar.addItem(c.Edit(), menuBar_edit);
		menuBar_edit.addItem(c.Criteria(), commandCriteria);
		menuBar_edit.addItem(c.Options(), commandOptions);
		menuBar.addItem(c.Run(), commandRun);
		final MenuBar menuBar_view = new MenuBar(true);
		menuBar.addItem(c.View(), menuBar_view);
		
		MenuItem menuItemReport = menuBar_view.addItem(c.Report(), (Command) null);
		menuItemReport.addStyleDependentName("disabled");
		MenuItem menuItemLogCing = menuBar_view.addItem(c.Log() + " CING", (Command) null);
		menuItemLogCing.addStyleDependentName("disabled");
		menuBar_view.addItem(c.Log() + " iCing", commandLog);
		MenuItem menuItem3D = menuBar.addItem(c.threeD(), (Command) null);
		menuItem3D.addStyleDependentName("disabled");	// try to improve styling.	
		menuBar.setWidth(widthMenu);
		final MenuBar menuBar_help = new MenuBar(true);
		menuBar.addItem(c.Help(), menuBar_help);
		menuBar_help.addItem(c.Welcome(), commandWelcome);
		menuBar_help.addItem(c.Help(), commandHelp);

		rootPanel.add(vPanel);
		vPanel.setWidth("100%");
		vPanel.add(topPanel);
		topPanel.setWidth("100%");
		topPanel.setSpacing(11);
		vPanel.add(menuBar);

	}

	public void loadLoginView() {
		clearAllViews();
		login.setVisible(true);
	}

	public void loadWelcomeView() {
		clearAllViews();
		welcome.setVisible(true);
	}

	public void loadOptionsView() {
		clearAllViews();
		options.setVisible(true);
	}

	public void loadPrefView() {
		clearAllViews();
		preferences.setVisible(true);
	}

	public void loadCriteriaView() {
		clearAllViews();
		criteria.setVisible(true);
	}

	public void loadPreferencesView() {
		clearAllViews();
		preferences.setVisible(true);
	}

	public void loadFileView() {
		clearAllViews();
		fileView.setVisible(true);
	}
	public void loadLogView() {
		clearAllViews();
		logView.setVisible(true);
	}


	/**
	 * Update the style sheets to reflect the current theme and direction.
	 */
	private void updateStyleSheets() {
		// Generate the names of the style sheets to include
		String gwtStyleSheet = "css/gwt/" + CUR_THEME + "/" + CUR_THEME + ".css";
		String showcaseStyleSheet = "css/sc/" + CUR_THEME + "/Showcase.css";
		if (LocaleInfo.getCurrentLocale().isRTL()) {
			gwtStyleSheet = gwtStyleSheet.replace(".css", "_rtl.css");
			showcaseStyleSheet = showcaseStyleSheet.replace(".css", "_rtl.css");
		}

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
					if (!href.contains(gwtStyleSheet) && !href.contains(showcaseStyleSheet)) {
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
				RootPanel.getBodyElement().getStyle().setProperty("display", "none");
				RootPanel.getBodyElement().getStyle().setProperty("display", "");
				RootPanel.get().add(vPanel);
			}
		};
		StyleSheetLoader.loadStyleSheet(modulePath + gwtStyleSheet, getCurrentReferenceStyleName("gwt"), callback);

		// Load the showcase specific style sheet after the GWT theme style
		// sheet so
		// that custom styles supercede the theme styles.
		StyleSheetLoader.loadStyleSheet(modulePath + showcaseStyleSheet, getCurrentReferenceStyleName("Application"), // should
																														// this
																														// really
																														// be
																														// Application
				// instead of iCing? YES
				callback);
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
		String gwtRef = prefix + "-Reference-" + CUR_THEME;
		if (LocaleInfo.getCurrentLocale().isRTL()) {
			gwtRef += "-rtl";
		}
		return gwtRef;
	}

	/**
	 * A special version of the ToggleButton that cannot be clicked if down. If
	 * one theme button is pressed, all of the others are depressed.
	 */
	private static class ThemeButton extends ToggleButton {
		private static List<ThemeButton> allButtons = null;

		private String theme;

		public ThemeButton(String theme) {
			super();
			this.theme = theme;
			addStyleName("sc-ThemeButton-" + theme);

			// Add this button to the static list
			if (allButtons == null) {
				allButtons = new ArrayList<ThemeButton>();
				setDown(true);
			}
			allButtons.add(this);
		}

		public String getTheme() {
			return theme;
		}

		@Override
		protected void onClick() {
			if (!isDown()) {
				// Raise all of the other buttons
				for (ThemeButton button : allButtons) {
					if (button != this) {
						button.setDown(false);
					}
				}

				// Fire the click listeners
				super.onClick();
			}
		}
	}
}