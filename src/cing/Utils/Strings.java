/*
 *This software is copyright (c) 2002 Board of Regents, University of Wisconsin.
 *All Rights Reserved. No warranty implied or expressed.
 */
package cing.Utils;

/**
 * One of the largest classes in Wattos. Static utilities for dealing with String.
 *E.g. getting input from a BufferedReader,
 * @author Jurgen F. Doreleijers
 * @version 1.0
 */
public class Strings {
    static {
    }

    /** Will even work when objects are null */
    public static String toString(Object[] a, boolean printEOLAfterEach,
        boolean useBrackets, String separator ) {
        if ( a == null ) {
            return null;
        }
        if ( a.length == 0 ) {
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
        for (int i=0;i<a.length;i++) {
            if ( i != 0 ) {
                if ( printEOLAfterEach ) {
                    result.append('\n');
                } else {
                    //result.append(',');
                    result.append(separator);
                }
            }
            result.append( a[i] );
        }
        if ( useBrackets ) {
            result.append(']');
        }
        return result.toString();
    }

    /** Will even work when objects are null */
    public static String toString(Object[] a, boolean printEOLAfterEach,
        boolean useBrackets ) {
        return toString( a, printEOLAfterEach, useBrackets, ";" );
    }

    public static String toString(String[] a ) {
        return toString(a, false, true );
    }

    /** For rectangular */
    public static String toString(String[][] a ) {
        StringBuffer result = new StringBuffer();
        for (int i=0;i<a.length;i++) {
            result.append(toString(a[i]));
            result.append('\n');
        }
        return result.toString();
    }

}
