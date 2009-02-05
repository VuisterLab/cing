/*
 * Utils.java
 *
 * Created on December 6, 2001, 11:37 AM
 *
 * Utilities for dealing with memory, sleep, and reporting.
 *This software is copyright (c) 2002 Board of Regents, University of Wisconsin.
 *All Rights Reserved. No warranty implied or expressed.
 */

package cing.client;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;

import com.google.gwt.i18n.client.DateTimeFormat;

/**
 * Static settings and methods for output stream handling, memory reporting, etc. The show... methods should always end
 * with a non-empty line and one that indicates the error, debug, warning or regular status.
 * 
 * Visibility is to remain in package only.
 * 
 * @author Jurgen F. Doreleijers
 * @version 0.1
 */
class GenClient {

	/**
	 * Next variable controls e.g. how much debug statements will be done.
	 * 
	 * <PRE>
	 * 0 nothing
	 * 1 only errors
	 * 2 and warnings
	 * 3 and output (DEFAULT)
	 * 9 and debug info
	 * </PRE>
	 */
	public static final int verbosityNothing = 0; // Even errors will be suppressed
	public static final int verbosityError = 1; // show only errors
	public static final int verbosityWarning = 2; // show errors and warnings
	public static final int verbosityOutput = 3; // and regular output DEFAULT
	public static final int verbosityDetail = 4; // show more details
	public static final int verbosityDebug = 5; // add debugging info (not

	// recommended for casual user)
	private static int verbosity = verbosityOutput;
//	 public static int verbosity = verbosityDebug; DON'T CHANGE HERE; USE iCing.java#onModuleLoad() call to GenClient.setVerbosityToDebug();

	/**
	 * Should be the same value as the ResultSet.getInt methods return for nulls. This is wrongly documented in
	 * O'Reilly's "Java enterprise in a nutshell", 1st Ed., p.25.
	 */
	public static final int NULL_FOR_INTS = 0;

	/**
	 * When the program was successful. This is the only exit status May be short cut (not always mention explicitly)
	 * because it is the standard in unix any way.
	 */
	public static final int EXIT_STATUS_SUCCESS = 0;
	/** When the program needs a better programmer. */
	public static final int EXIT_STATUS_CODE_ERROR = 1;
	/** When the program needs a better input. */
	public static final int EXIT_STATUS_INPUT_ERROR = 2;
	/** When the program needs more memory. */
	public static final int EXIT_STATUS_OUT_OF_MEMORY = 3;
	/** Undetermined error. */
	public static final int EXIT_STATUS_ERROR = 9;

	public static String eol;
	public static char eolChar;

	public static iCingConstants constants = iCing.c;

	static {
		eol = "\n";
		eolChar = '\n';
	}

	/**
	 * Issues an error message saying this class can not be initiated.
	 */
	public GenClient() {
		showError("Don't try to initiate the GenClient class; it's methods are static");
	}

	// public static void sleep( long sleepTimeInMilliseconds ) {
	// try {
	// Thread.sleep( sleepTimeInMilliseconds ); // current thread sleeps
	// } catch ( InterruptedException e ) {
	// showWarning("received an interruption in my sleep");
	// }
	// }

	// /** As documented in Sun's: The Java programming Language; 3rd edit.
	// */
	// public static void doFullestGarbageCollection() {
	// Runtime rt = Runtime.getRuntime();
	// long isFree = rt.freeMemory();
	// long wasFree;
	// do {
	// wasFree = isFree;
	// rt.runFinalization();
	// rt.gc();
	// isFree = rt.freeMemory();
	// //showOutput("Memory free: " + isFree );
	// } while ( isFree > wasFree );
	// }

	// public static long getMemoryUsed() {
	// // doFullestGarbageCollection();
	// Runtime rt = Runtime.getRuntime();
	// long total = rt.totalMemory();
	// long free = rt.freeMemory();
	// return total - free;
	// }
	//
	// public static void showMemoryUsed() {
	// Runtime rt = Runtime.getRuntime();
	//
	// long total = rt.totalMemory();
	// long free = rt.freeMemory();
	// long used = total - free;
	// String pattern = "0,000,000,000";
	// DecimalFormat nf = new DecimalFormat(pattern);
	// String usedStr = nf.format(used);
	// String totalStr = nf.format(total);
	//        
	// showOutput( "Memory used before GC: "+usedStr+" out of: "+ totalStr);
	// doFullestGarbageCollection();
	// total = rt.totalMemory();
	// free = rt.freeMemory();
	// used = total - free;
	// /**
	// p.add( used );
	// p.add( total );
	// showOutput( Format.sprintf("Memory used before GC: %13d out of: %13d", p)
	// );
	// */
	// }
	//    
	// /** Show a little debug info on environment */
	// public static void showEnvironment( ) {
	// Properties prop = System.getProperties();
	// showOutput( Strings.toString( prop ));
	// try {
	// String hostname = InetAddress.getLocalHost().getHostName();
	// showOutput("From showEnvironment: Hostname is: " + hostname);
	// } catch (UnknownHostException e) {
	// //
	// e.printStackTrace();
	// }
	// }

	/** Show a little info on memory limitations then exit. */
	public static void doOutOfMemoryExit() {
		String message = "";
		message += "Ran out of memory." + eol;
		message += "A way to increase the allowed memory consumption is to" + eol;
		message += "specify this when starting the Java virtual machine, like:" + eol;
		message += "   java -Xmx512m Wattos.Utils.General" + eol;
		message += "to set the maximum memory of the heap to 512 Mb." + eol + eol;
		showError(message);
		// if ( verbosity >= verbosityError ) {
		// showThrowable(e);
		// }
		// showMemoryUsed();
		doExit(EXIT_STATUS_OUT_OF_MEMORY);
	}

	/** Can't exit a JS program so just print request */
	private static void doExit(int code) {
		showError("Ignoring a call to exit with a code: [" + code + "]");
	}

	public static void doErrorExit(String message) {
		showError(message);
		doExit(EXIT_STATUS_ERROR);
	}

	public static void doCodeBugExit(String message) {
		doCodeBugExit(message, null, null, null);
	}

	public static void doCodeBugExit(String message, String lastKnownPosition, Throwable t, Class c) {
		showCodeBug(message, lastKnownPosition, t, c);
		doExit(EXIT_STATUS_CODE_ERROR);
	}

	public static void showCodeBug(String message, String lastKnownPosition, Throwable t, Class c) {

		if (verbosity < verbosityError) {
			return;
		}
		if (lastKnownPosition != null) {
			message += eol + constants.ERROR() + ": ran into a code bug at: ";
			if (c != null) {
				message += c.getName() + ' ';
			} else {
				message += "unknown class, ";
			}
			if (lastKnownPosition != null) {
				message += "at last known position: " + lastKnownPosition + eol;
			} else {
				message += "at unknown last position.";
			}
			if (t != null) {
				message += t.getMessage();
			}
		}
		showError(message);
	}

	public static void showCodeBug(String message) {
		showCodeBug(message, null, null, null);
	}

	public static void showError(String message, String lastKnownPosition, Throwable t, Class cl) {

		if (verbosity < verbosityError) {
			return;
		}
		String prefix = "<font color=\"red\">" + constants.ERROR() + "</font>";
		if (lastKnownPosition != null) {
			message += eol + ": ran into an error at: ";
			if (cl != null) {
				message += cl.getName() + ' ';
			} else {
				message += "unknown class, ";
			}
			if (lastKnownPosition != null) {
				message += "at last known position: " + lastKnownPosition + eol;
			} else {
				message += "at unknown last position.";
			}
			if (t != null) {
				message += t.getMessage();
			}
		} else {
			if (message != null) {
				message = prefix + ": ".concat(message);
			} else {
				message = prefix + ": null";
			}
		}
		// Window.alert(message);
		showOutput(message);
	}

	public static void showError(String message) {
		showError(message, null, null, null);
	}

	public static void showThrowable(Throwable t) {
		// StringWriter stw = new StringWriter();
		// PrintWriter pw = new PrintWriter(stw,true);
		// //pw.println( "Localized message    : " + t.getLocalizedMessage() );
		// //pw.println( "Message              : " + t.getMessage() );
		// t.printStackTrace(pw);
		showError(eol + t.toString());
		showError("Found throwable error above");
	}

	public static void showWarning(String message, String lastKnownPosition, Throwable t, Class c) {
		if (verbosity < verbosityWarning) {
			return;
		}
		String prefix = "<font color=\"orange\">" + constants.WARNING() + "</font>";
		if (lastKnownPosition != null) {
			message += eol + constants.WARNING() + ": ran into a uncommon situation at: ";
			if (c != null) {
				message += c.getName() + ' ';
			} else {
				message += "unknown class, ";
			}
			if (lastKnownPosition != null) {
				message += "at last known position: " + lastKnownPosition + eol;
			} else {
				message += "at unknown last position.";
			}
			if (t != null) {
				message += t.getMessage();
			}
		} else {
			message = prefix + ": ".concat(message);
		}
		showOutput(message);
	}

	public static void showWarning(String message) {
		showWarning(message, null, null, null);
	}

	public static void showDebug(String message, String lastKnownPosition, Throwable t, Class c) {
		if (verbosity < verbosityDebug) {
			return;
		}

		if (lastKnownPosition != null) {
			message += constants.DEBUG() + ": ran into a uncommon situation at: ";
			if (c != null) {
				message += c.getName() + ' ';
			} else {
				message += "unknown class, ";
			}
			if (lastKnownPosition != null) {
				message += "at last known position: " + lastKnownPosition + eol;
			} else {
				message += "at unknown last position.";
			}
			if (t != null) {
				message += t.getMessage();
			}
		} else {
			message = constants.DEBUG() + ": ".concat(message);
		}
		showOutput(message);
	}

	public static void showDebug(String message) {
		showDebug(message, null, null, null);
	}

	public static void showDetail(String message) {
		if (verbosity < verbosityDetail) {
			return;
		}
		showOutput(message);
	}

	public static void showOutput(String message) {
		if (verbosity < verbosityOutput) {
			return;
		}
		if (verbosity > verbosityOutput) {
			Date today = new Date();
			String date_str = DateTimeFormat.getLongTimeFormat().format(today);
			message = date_str + " " + message;
		}
		Utils.appendHtml(message + eol, iCing.area);
		// System.out.println(message); // Echo
	}

	/**
	 * Sort the ArrayList with the selected element first wrapping around at the end. If the given first element doesn't
	 * occur, a warning will be issued and the collection will be returned in a simple sorted order. Multiple
	 * occurrences of the same item in the list will be treated correctly.
	 * 
	 * @param al
	 *            The ArrayList to be rotated.
	 * @param first_element
	 *            Element that should become the first element after this operation.
	 */
	public static void rotateCollectionToFirst(ArrayList al, Object first_element) {
		// Sort
		Collections.sort(al);
		// int last_element_index = al.size()-1;
		int first_position = al.indexOf(first_element);
		if (first_position < 0) {
			showWarning("element given does not exist, rotateCollectionToFirst");
			return;
		}
		// Rotate
		for (int i = 0; i < first_position; i++) {
			Object ob_temp = al.get(0);
			al.remove(0);
			al.add(ob_temp);
		}
		/*
		 * The following simpler/faster code didn't worksubList didn't cast well and actually only generates a view...
		 * al.subList(first_position,al.size()); al.removeRange(first_position,al.size()); al.addAll(0, al_temp);
		 */
	}

	/**
	 * Combine the contents in two attributes, putting the result into the first by overwriting the original.
	 * 
	 * @param add
	 *            The new stuff in here.
	 */
	// public static void appendAttributes(Attributes old, Attributes add) {
	// if (add.size() > 0) {
	// Iterator keys = (add.keySet()).iterator();
	// while (keys.hasNext()) {
	// String key = ((Attributes.Name)(keys.next())).toString();
	// String value = add.getValue(key);
	// old.putValue(key, value);
	// }
	// }
	// }
	public static void flushOutputStream() {
		showError("Ignoring a call to flush out");
		// out.flush();
	}

	public static void setVerbosityToDebug() {
		setVerbosity(verbosityDebug);
	}

	// /** Shows an error message with the string prepended to the current date
	// */
	// public static void showErrorDate(String string) {
	// String date = java.text.DateFormat.getDateTimeInstance(
	// java.text.DateFormat.FULL, java.text.DateFormat.FULL).format(new
	// java.util.Date());
	// showError(string + date);
	// }
	//    
	/**
	 * public static final int verbosityNothing = 0; // Even errors will be suppressed public static final int
	 * verbosityError = 1; // show only errors public static final int verbosityWarning = 2; // show errors and warnings
	 * public static final int verbosityOutput = 3; // and regular output DEFAULT public static final int
	 * verbosityDetail = 4; // show more details public static final int verbosityDebug = 5; // add debugging info (not
	 * 
	 * verbosityNothing = 0 # Even errors will be suppressed verbosityError = 1 # show only errors verbosityWarning = 2
	 * # show errors and warnings verbosityOutput = 3 # and regular output DEFAULT verbosityDetail = 4 # show more
	 * details verbosityDebug = 9 # add debugging info (not recommended for casual user)
	 * 
	 * @param verbosity
	 * @return
	 */
	public static int map2CingVerbosity(int verbosity) {
		if (verbosity == 5) {
			return 9;
		}
		return verbosity;
	}

	public static void setVerbosity(int verbosity) {
		GenClient.verbosity = verbosity;
	}

	public static boolean isVerbosityDebug() {
		return verbosity == verbosityDebug;
	}

	public static int getVerbosity() {
		return verbosity;
	}

}
