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
		for ( int row = 0; row < t.getRowCount(); row++ ) {
			if ( row == 0 ) {
				continue;
			}
			int colMax = t.getCellCount(row);
			
			for ( int column = 0; column < colMax; column++ ) {
				Widget w = t.getWidget(row, column);
				setEnabled(w, b);
			}		
		}
		String msg = "Enabled";
		if ( ! b ) {
			msg = "Disabled";
		}
		General.showDebug(msg + " all input fields for table: " + t.getTitle());
		return false; // default in python
	}

	/** Note the log can't be used during shuffle
	 *
	 * @param html
	 * @return
	 */
	public static String reverse(String html) {
//		System.err.print( "Found html: ["+html+"]");
		String[] lines = html.split("<br>"); // need algorithm for doing pre's too.
		int n = lines.length;
		String result = "";
		for (int i=n-1; i>=1; i--) {
			result += lines[i]+"<br>";
		}
		if ( n > 0 ) {
			result += lines[0];
		}
//		System.err.print("Returned html: ["+result+"]");
		return result;
	}
	
	public static void setEnabled(Widget w, boolean b) {
		if ( w instanceof CheckBox ) {
			((CheckBox)w).setEnabled(b);
		}
		if ( w instanceof Button ) {
			((Button)w).setEnabled(b);
		}
		if ( w instanceof ListBox ) {
			((ListBox)w).setEnabled(b);
		}
		if ( w instanceof TextBox ) {
			((TextBox)w).setEnabled(b);
		}		
	}	
	

	/** 
	 * @param flexTable
	 * @param sender
	 * @return row,column indices
	 * 
	 * done before realizing there is an iterator...
	 */
	public static int[] getIndicesFromTable(FlexTable flexTable, Widget w) {
		int rowCount = flexTable.getRowCount();
		for (int row=0;row<rowCount;row++) {
			int colCount = flexTable.getCellCount(row);
			for (int column=0;column<colCount;column++) {
				if ( flexTable.getWidget(row, column) == w ) {
					return new int[] { row, column };
				}
			}
		}
		return null;
	}

	public static void removeAllRows(FlexTable flexTable) {
		int rowCount = flexTable.getRowCount();
		for (int row=rowCount-1;row>=0;row--) {
			flexTable.removeRow(row);
		}			
	}
	
    
    /** Will even work when objects are null */
    public static String toString(ArrayList<String> a, boolean printEOLAfterEach, 
        boolean useBrackets, String separator ) {
        if ( a == null ) {
            return null;
        }        
        if ( a.size() == 0 ) {
            if ( useBrackets ) {
                return "[empty]";
            } else {
                return "empty";
            }
        }
        
        StringBuffer result = new StringBuffer();
        if ( useBrackets ) {
            result.append('[');
        }
        for (int i=0;i<a.size();i++) {
            if ( i != 0 ) {
                if ( printEOLAfterEach ) {
                    result.append('\n');
                } else {
                    result.append(separator);
                }
            }
            result.append( a.get(i) );
        }
        if ( useBrackets ) {
            result.append(']');
        }
        return result.toString();
    }    
	
	
}
