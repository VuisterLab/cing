package cing.client;

import java.util.ArrayList;

import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;

public class Utils {
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
	 * Will very simply process a text between PRE tags.
	 * 
	 * @param html
	 * @return null on error.
	 */
	public static String reverse(String html) {
		if (html == null) {
			General.showError("In Utils.reverse: got null for html");
			return null;
		}

		int htmlLength = html.length();
		int htmlLengthMinimal = "<PRE></PRE>".length();

		if (htmlLength < htmlLengthMinimal) {
			General.showError("In Utils.reverse: got too short html");
			return null;
		}
		int a = "<PRE>".length();
		int b = "</PRE>".length();

		html = html.substring(a, htmlLength - b);
		String[] lines = html.split("\n");
		int n = lines.length;
//		General.showDebug("found number of lines: " + n);
		String result = "<PRE>\n";
		for (int i = n - 1; i >= 0; i--) {
			result += lines[i] + "\n";
		}
		result += "</PRE>";
//		General.showDebug("Returned html: [" + result + "]");
		return result;
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
					result.append('\n');
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

	/**
	 * Mostly implemented in i18n. Disabled for now because only needed on
	 * server side, for now. //import com.google.gwt.i18n.client.NumberFormat;
	 * public static String bytesToFormattedString(long size) {
	 * 
	 * long k = 1024; long M = 1024*1024; long G = 1024*1024*1024; long T =
	 * 1024*1024*1024*1024; char cs = 's'; char ck = 'k'; char cM = 'M'; char cG
	 * = 'G'; char cT = 'T'; char postFix = cs;
	 * 
	 * long divider = 1; if ( size < 1024 ) { ; } else if ( size < M ) { divider
	 * = k; postFix = ck; } else if ( size < G ) { divider = M; postFix = cM; }
	 * else if ( size < T ) { divider = G; postFix = cG; } else { divider = T;
	 * postFix = cT; } double r = size/(double)divider; String result = null; if
	 * ( postFix == cs ) { result = NumberFormat.getFormat("0").format(r) +
	 * " bytes"; } else { result = NumberFormat.getFormat("0.00").format(r) +
	 * " " + postFix + "b"; } return result; }
	 */

}
