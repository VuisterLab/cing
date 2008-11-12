package cing.server;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.text.NumberFormat;

/**
 * Add specific iCing stuff here.
 * All other code can remain in Wattos.
 * @author jd
 *
 */
public class Ut {
    public static NumberFormat nf = NumberFormat.getInstance();

    public static String formatReal(double d, int precision) {
        nf.setMaximumFractionDigits(precision);
        nf.setMinimumFractionDigits(precision);
        return nf.format(d);
    }
    
    /** Next might be implemented in i18n but is pretty fast here.*/
	public static String bytesToFormattedString(long size) {
		
		long k = 1024;
		long M = 1024*1024;
		long G = 1024*1024*1024;
		long T = 1024*1024*1024*1024;
		char cs = 's';
		char ck = 'k';
		char cM = 'M';
		char cG = 'G';
		char cT = 'T';
		char postFix = cs;
		
		long divider = 1;
		if ( size < 1024 ) {
			;
		} else if ( size < M ) {
			divider = k;
			postFix = ck;
		} else if ( size < G ) {
			divider = M;
			postFix = cM;
		} else if ( size < T ) {
			divider = G;
			postFix = cG;
		} else  {
			divider = T;
			postFix = cT;
		}
		double r = size/(double)divider;
		String result = null;
		if ( postFix == cs ) {
		    result = Integer.toString((int)r) + " bytes";
		} else {
			result = formatReal(r,2) + " " + postFix + "b";
		}
		return result;
	}

	/**
	 *  
	 * @return true for error
	 */
	public static boolean chmod(File f, String mod) {
		String cmd = "chmod " + mod + " " + f.toString();
		General.showDebug("Executing command: [" + cmd + "]");
		try {
			Process p = Runtime.getRuntime().exec(cmd);
			BufferedReader in = new BufferedReader(new InputStreamReader(p.getInputStream()));
			String line = null;
			while ((line = in.readLine()) != null) {
				General.showDebug(line);
			}
		} catch (IOException e) {
			e.printStackTrace();
		}
		return true;
	}    
	
	
}