package cing.server;

import java.io.InputStream;
import java.text.NumberFormat;
import java.util.HashMap;
import java.util.Set;

import Wattos.Utils.General;
import Wattos.Utils.InOut;
import Wattos.Utils.StringArrayList;

import com.braju.format.Format;
import com.braju.format.Parameters;

/**
 * Add specific iCing stuff here. All other code can remain in Wattos.
 * 
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

    /** Next might be implemented in i18n but is pretty fast here. */
    public static String bytesToFormattedString(long size) {

        long k = 1024;
        long M = 1024 * 1024;
        long G = 1024 * 1024 * 1024;
        long T = 1024 * 1024 * 1024 * 1024;
        char cs = 's';
        char ck = 'k';
        char cM = 'M';
        char cG = 'G';
        char cT = 'T';
        char postFix = cs;

        long divider = 1;
        if (size < 1024) {
            ;
        } else if (size < M) {
            divider = k;
            postFix = ck;
        } else if (size < G) {
            divider = M;
            postFix = cM;
        } else if (size < T) {
            divider = G;
            postFix = cG;
        } else {
            divider = T;
            postFix = cT;
        }
        double r = size / (double) divider;
        String result = null;
        if (postFix == cs) {
            result = Integer.toString((int) r) + " bytes";
        } else {
            result = formatReal(r, 2) + " " + postFix + "b";
        }
        return result;
    }

    /**
     * 
     * @param parameterMap
     * @return Conforms to: Python RFC822 Configuration Settings
     */
    public static String mapToPythonRFC822ConfigurationSettings(HashMap<String, String> parameterMap) {
        String FILE_LOCATION = "Data/valSetsHeader.cfg";
        InputStream file_is = Ut.class.getResourceAsStream(FILE_LOCATION); // was getClass()
        String header = InOut.readTextFromInputStream(file_is);

        if (header == null) {
            General.showError("Failed to read header from: " + FILE_LOCATION);
            return null;
        }
        StringBuffer result = new StringBuffer();
        result.append(header);
        /**
         * For the long command string it's real nice to have the overview layed out in a printf way
         */
        Parameters p = new Parameters(); // Printf parameters autoclearing after use.
        Set<String> keySet = parameterMap.keySet();
        StringArrayList sal = new StringArrayList(keySet);
        sal.sort();
        int n = sal.size();
        for (int i = 0; i < n; i++) {
            String key = sal.getString(i);
            p.add(key);
            p.add(parameterMap.get(key));
            String item = Format.sprintf("%-30s = %-30s\n", p);
            result.append(item);
        }
        return result.toString();
    }

}