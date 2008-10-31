package cing.client;

import java.util.ArrayList;

import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.RichTextArea;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;

public class Utils {
	public static final String preStart = "<pre>";
	public static final String preEnd = "</pre>";
	public static final int preStartLength = preStart.length();
	public static final int preEndLength = preEnd.length();
	public static final int preHtmlLengthMinimal = preStartLength + preEndLength;
	
	public static boolean setEnabledAllInRowsButFirst(FlexTable t, boolean b) {
		for (int row = 0; row < t.getRowCount(); row++) {
			if (row == 0) {
				continue;
			}
			int colMax = t.getCellCount(row);

			for (int column = 0; column < colMax; column++) {
				Widget w = t.getWidget(row, column);
				setEnabled(w, b);
			}
		}
		String msg = "Enabled";
		if (!b) {
			msg = "Disabled";
		}
		General.showDebug(msg + " all input fields for table: " + t.getTitle());
		return false; // default in python
	}

	/**
	 * Assumes that the input is wrapped in pre tags. 
	 * Allows only font tags etc. to be inside but that's enough.
	 *
	 * No regular showDebugs etc can be used because this is used in the reporting in itself.
	 * @param html
	 * @return null on error.
	 */
	public static String reverseHtml(String html) {
		html = unwrapPres( html );
		html = reverseLines(html);
		String result = preStart + html + preEnd;
//		System.out.println("DEBUG: reverseHtml Result html: [" + result + "]");
		return result;
	}

	/** Regardless of content
	 * 
	 * @param html
	 * @return
	 */
	public static String reverseLines(String html) {
		String[] lines = html.split(General.eol);
		int n = lines.length;
//		System.out.println("DEBUG: reverseLines found number of lines: " + n);
		StringBuffer result = new StringBuffer();
		for (int i = n - 1; i >= 0; i--) {
			result.append(lines[i] + General.eol);
		}
//		System.out.println("DEBUG result reverseLines: [" + result + "]");
		return result.toString();
	}

	public static void setEnabled(Widget w, boolean b) {
		if (w instanceof CheckBox) {
			((CheckBox) w).setEnabled(b);
		}
		if (w instanceof Button) {
			((Button) w).setEnabled(b);
		}
		if (w instanceof ListBox) {
			((ListBox) w).setEnabled(b);
		}
		if (w instanceof TextBox) {
			((TextBox) w).setEnabled(b);
		}
	}

	/**
	 * @param flexTable
	 * @param sender
	 * @return row,column indices
	 * 
	 *         done before realizing there is an iterator...
	 */
	public static int[] getIndicesFromTable(FlexTable flexTable, Widget w) {
		int rowCount = flexTable.getRowCount();
		for (int row = 0; row < rowCount; row++) {
			int colCount = flexTable.getCellCount(row);
			for (int column = 0; column < colCount; column++) {
				if (flexTable.getWidget(row, column) == w) {
					return new int[] { row, column };
				}
			}
		}
		return null;
	}

	public static void removeAllRows(FlexTable flexTable) {
		int rowCount = flexTable.getRowCount();
		for (int row = rowCount - 1; row >= 0; row--) {
			flexTable.removeRow(row);
		}
	}

	/** Will even work when objects are null */
	public static String toString(ArrayList<String> a, boolean printEOLAfterEach, boolean useBrackets, String separator) {
		if (a == null) {
			return null;
		}
		if (a.size() == 0) {
			if (useBrackets) {
				return "[empty]";
			} else {
				return "empty";
			}
		}

		StringBuffer result = new StringBuffer();
		if (useBrackets) {
			result.append('[');
		}
		for (int i = 0; i < a.size(); i++) {
			if (i != 0) {
				if (printEOLAfterEach) {
					result.append(General.eolChar);
				} else {
					result.append(separator);
				}
			}
			result.append(a.get(i));
		}
		if (useBrackets) {
			result.append(']');
		}
		return result.toString();
	}

	/** Returns text without the enclosing PRE tags.
	 * Don't use General.showXXX because it would cycle.
	 * @return null on error.
	 */
	public static String unwrapPres(String html) {
//		System.out.println("In Utils.reverseHtml: got ["+html+"]");
		if (html == null) {
			System.err.println("ERROR: In Utils.unwrapPres: got null for html");
			return null;
		}

		int htmlLength = html.length();
		if (htmlLength < preHtmlLengthMinimal) {
			System.err.println("ERROR: In Utils.unwrapPres: got too short html");
			return null;
		}
		if (!html.startsWith(preStart)) {
			System.err.println("ERROR: In Utils.unwrapPres: html should start with: [" + preStart + "]");
			return null;
		}
		if (!html.endsWith(preEnd)) {
			System.err.println("ERROR: In Utils.unwrapPres: html should end with: [" + preEnd + "]");
			return null;
		}

		return  html.substring(preStartLength, htmlLength - preEndLength);
	}

	public static String wrapPres(String html) {
		 return preStart + html + preEnd; 
	}

	public static String colorCodeHtml(String message) {
		message = message.replace("DEBUG", "<font color=\"green\">DEBUG</font>");
		message = message.replace("ERROR", "<font color=\"red\">ERROR</font>");
		message = message.replace("WARNING", "<font color=\"orange\">WARNING</font>");
		message = message.replace("Warning", "<font color=\"orange\">Warning</font>");
		return message;
	}
	
	/**
	 * @param message
	 * @return false on error.
	 */
	public static boolean appendHtml(String message, RichTextArea area ) {
//		System.err.println("DEBUG: [" + message + "]");
		String htmlOrg = area.getHTML();
		htmlOrg = Utils.unwrapPres(htmlOrg);
		if (htmlOrg == null) {
			System.err.println("ERROR: failed to appendHtml because could not unwrapPres");
			return false;
		}

		if (iCing.textIsReversedArea) {
			message = Utils.reverseLines(message);
			if (message == null ) {
				return false;
			}
		}
		message = colorCodeHtml(message);
		
		String htmlNew = null;
		if (iCing.textIsReversedArea) {
			htmlNew = message + htmlOrg;
		} else {
			htmlNew = htmlOrg + message;
		}
		
		htmlNew = Utils.wrapPres( htmlNew ); 
		area.setHTML(htmlNew);
		return true;
	}

	public static String getFileNameWithoutPath(String fn) {
		int idxSlash = fn.lastIndexOf('/');
		int n = fn.length();
		if (idxSlash < 0) {
			idxSlash = fn.lastIndexOf('\\');
		}
		char lastChar = fn.charAt(n - 1);
		if (lastChar == '/' || lastChar == '\\') {
			General.showError("Failed to getFileNameWithoutPath");
			return fn;
		}
		return fn.substring(idxSlash + 1);
	}

	/** Implement for real; this is just a guess */
	public static String getHTMLformTypeFromFileName(String fn) {
		if (fn.endsWith(".tgz")) {
			return "binary/tgz";
		}
		if (fn.endsWith(".tar")) {
			return "binary/tgz";
		}
		return "text/txt";
	}
	

}
