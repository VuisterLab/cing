/*
 * Definitions.java
 *
 * Created on July 7, 2003, 5:22 PM
 */

package cing.client;

import java.util.*;

/**
 *Definitions and methods for dealing with database null and bit values.
 * Contains only static methods so it doesn't need to be serialized.
 * @author Jurgen F. Doreleijers
 */
public class Defs {
    
    /** The primitive data types below are overloaded to deal with null values such
     *as encountered in relational databases and star. Every time arithmetic is
     *performed make sure to check that the values aren't 'nilled'.
     *For BitSet no NULLs are possible because of limited range.
     */
    public static final short   NULL_BYTE       = Byte.MAX_VALUE - 1; 
    public static final short   NULL_SHORT      = Short.MAX_VALUE - 1; 
    public static final int     NULL_INT        = Integer.MAX_VALUE - 1;
//    public static final float   NULL_FLOAT      = Float.intBitsToFloat(0x7f7ffffe);             // Like: MAX_VALUE - 1 bit;
//    public static final double  NULL_DOUBLE     = Double.longBitsToDouble(0x7feffffffffffffeL); // Like: MAX_VALUE - 1 bit;
    public static final char    NULL_CHAR       = Character.MAX_VALUE - 1;                      
    public static final String  NULL_STRING_NULL = null; // Just to be explicit; this holds for all objects.
    public static final Object  NULL_OBJECT_NULL = null; // Just to be explicit; this holds for all objects.
    // Taken the same as Wattos.Star.General.STAR_NULL_STRING;  but reference is removed to keep packages distinct.
    public static final String  NULL_STRING_DOT  = ".";            
    public static final String  NULL_STRING_QUESTION_MARK  = "?";            
    /** Used as default distinguished from null which is usually reserved for error status.
     */
    public static final String  EMPTY_STRING  = "";
/** Not applicable abbreviation */
    public static final String STRING_NA  = "n/a";
    public static final String STRING_TRUE  = "true";
    public static final String STRING_FALSE = "false";
    public static final ArrayList possibleWaysToSayYesLowerCase = new ArrayList();
    public static final String[] possibleWaysToSayYesLowerCaseArray = {"y", "yes", "t", STRING_TRUE, "0"};
    
    
    /** Returns true only if same and both are not null */
    public static boolean equals( int a, int b ) {
        if ( a!=b  || isNull(a) || isNull(b)) {
            return false;
        }
        return true;
    }

//    /** Returns true only if all within are same and both are not null */
//    public static boolean equals( IntArrayList a, IntArrayList b ) {
//        if ( a==null || b==null  || a.size()!=b.size()) {
//            return false;
//        }
//        int size = a.size();
//        for (int i=0; i<size; i++) {
//            if ( ! equals( a.getQuick(i), b.getQuick(i) )) { // takes one rotten apple
//                return false;
//            }
//        }
//        return true;
//    }

    // Inline them when speed is needed.
    public static boolean isNull( Object v ) {
        if ( v == null ) {
            return true;
        }
        return false;
    }

    // Inline them when speed is needed.
    public static boolean isNull( char v ) {
        if ( v == NULL_CHAR ) {
            return true;
        }
        return false;
    }

    public static boolean isNull( int v ) {
        if ( v == NULL_INT ) {
            return true;
        }
        return false;
    }
    
    public static boolean isNull( short v ) {
        if ( v == NULL_SHORT ) {
            return true;
        }
        return false;
    }
    
//    public static boolean isNull( float v ) {
//        if ( v == NULL_FLOAT ) {
//            return true;
//        }
//        return false;
//    }
//    
//    public static boolean isNull( double v ) {
//        if ( v == NULL_DOUBLE ) {
//            return true;
//        }
//        return false;
//    }
    
    /** Using this method for any object in general is a bit dangerous
     *because the compiler can't check my object types anymore. The method
     *is therefor specially named with the argument type.
     *
     *The method is handy but not fast for dealing with nulls in a consistent way.
     */
    public static boolean isNullString( String v ) {
        if ( v == NULL_STRING_NULL || 
            (v.length() == 0) || 
            v.equals(NULL_STRING_DOT) ||
            v.equals(NULL_STRING_QUESTION_MARK)
            ) {
            return true;
        }
        return false;
    }
    
    public static String toString( char v) {
        if ( isNull(v)) {
            return NULL_STRING_DOT;
        }
        return Character.toString(v);
    }        
    public static String toString( int v) {
        if ( isNull(v)) {
            return NULL_STRING_DOT;
        }
        return Integer.toString(v);
    }        
    public static String toString( float v) {
        if ( isNull(v)) {
            return NULL_STRING_DOT;
        }
        return Float.toString(v);
    }        
    public static String toString( double v) {
        if ( isNull(v)) {
            return NULL_STRING_DOT;
        }
        return Double.toString(v);
    }        
    public static String toString( short v) {
        if ( isNull(v)) {
            return NULL_STRING_DOT;
        }
        return Short.toString(v);
    }        

    public static int getInt( String str ) {
        int result = Defs.NULL_INT;
        try {
            result = new Integer( str ).intValue();
        } catch ( Exception e ) {
            return Defs.NULL_INT;
        }
        return result;
    }        
//    public static float getFloat( String str ) {
//        float result = Defs.NULL_FLOAT;
//        try {
//            result = new Float( str ).floatValue();
//        } catch ( Exception e ) {
//            return Defs.NULL_FLOAT;
//        }
//        return result;
//    }        
    /** returns false if string failed to be matched to the possibilities
     *The whitespace will be removed and the string converted to lower case.
     */
    public static boolean getBoolean( String str ) {
        if ( str == null ) {
            return false;
        }
        String tmp = str.replaceAll("\\s+","").toLowerCase();
        if ( possibleWaysToSayYesLowerCase.contains( tmp ) ) {
            return true;
        }
        return false;
    }     
   /** Self test; tests the function <CODE>showmap</CODE>.
     * @param args Ignored.
     */
    public static void main (String[] args) 
    {
        General.showOutput("Is: " + getBoolean("t rue"));
//        General.showOutput("Null float is: " + NULL_FLOAT);
    }            
}
