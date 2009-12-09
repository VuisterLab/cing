package cing.client;

import java.util.ArrayList;

public class Classification {
    /**
     * Of course using hashes would have been faster on the lookup but don't know if GWT supports them on the client
     * side.
     * 
     * The order of the elements in the below is: program, type, subtype, other, and example file in iCing.
     */
    static final String[][] classi = new String[][] {
            { Settings.FILE_PROGRAM_CCPN, Settings.FILE_TYPE_PROJECT, iCing.STRING_NA, iCing.STRING_NA, "1brv.tgz" },
            { Settings.FILE_PROGRAM_CING, Settings.FILE_TYPE_PROJECT, iCing.STRING_NA, iCing.STRING_NA, "1brv.cing.tgz" },
            { Settings.FILE_PROGRAM_CING, Settings.FILE_TYPE_VALIDATION_SETTINGS, iCing.STRING_NA, iCing.STRING_NA,
                    Settings.VAL_SETS_CFG_DEFAULT_FILENAME },
            // { "CING", "project", iCing.STRING_NA, iCing.STRING_NA },
            // { "CCPN", "bogus", "blabla", iCing.STRING_NA },
            // { "DYANA/DIANA", "distance", "hydrogen bond", "upper" },
            // { "DYANA/DIANA", "distance", "hydrogen bond", "lower" },
            // { "DYANA/DIANA", "distance", "NOE", "upper" },
            // { "DYANA/DIANA", "distance", "NOE", "lower" },
            // { "DYANA/DIANA", "dihedral angle", iCing.STRING_NA, iCing.STRING_NA },
            // { "XPLOR/CNS", "distance", "hydrogen bond", iCing.STRING_NA },
            // { "XPLOR/CNS", "distance", "NOE", iCing.STRING_NA },
            { Settings.FILE_PROGRAM_PDB, "coordinate", iCing.STRING_NA, iCing.STRING_NA, "pdb1brv.ent" }, };

    public static ArrayList<String> getProgramList() {
        ArrayList<String> r = new ArrayList<String>();
        for (String[] o : classi) {
            if (!r.contains(o[0])) {
                r.add(o[0]);
            }
        }
        // GenClient.showDebug("getProgramList: " + Utils.toString(r,false,true,","));
        return r;
    }

    /**
     * @return empty if no types are present or the list of allowed types.
     */
    public static ArrayList<String> getTypeList(String program) {
        ArrayList<String> r = new ArrayList<String>();
        if (program != null) {
            for (String[] o : classi) {
                if (o[0].equals(program)) {
                    if (!r.contains(o[1])) {
                        r.add(o[1]);
                    }
                }
            }
        }
        // GenClient.showDebug("getTypeList: " + Utils.toString(r,false,true,","));
        return r;
    }

    /**
     * @return empty if no types are present or the list of allowed types.
     */
    public static ArrayList<String> getSubTypeList(String program, String type) {
        ArrayList<String> r = new ArrayList<String>();
        for (String[] o : classi) {
            if (o[0].equals(program) && o[1].equals(type)) {
                if (!r.contains(o[2])) {
                    r.add(o[2]);
                }
            }
        }
        // GenClient.showDebug("getSubTypeList: " + Utils.toString(r,false,true,","));
        return r;
    }

    /**
     * @return empty if no types are present or the list of allowed types.
     */
    public static ArrayList<String> getOtherList(String program, String type, String subType) {
        ArrayList<String> r = new ArrayList<String>();
        for (String[] o : classi) {
            // GenClient.showDebug("Looking at string[0]: ["+o[0]+"]");
            if (o[0].equals(program) && o[1].equals(type) && o[2].equals(subType)) {
                if (!r.contains(o[3])) {
                    r.add(o[3]);
                }
            }
        }
        // GenClient.showDebug("getOtherList: " + Utils.toString(r, false, true, ","));
        return r;
    }

    /**
     * @return empty if no types are present or the list of allowed types.
     */
    public static String getExample(String program, String type, String subType, String other) {
        String result = null;
        for (String[] o : classi) {
            // GenClient.showDebug("Looking at string[0]: ["+o[0]+"]");
            if (o[0].equals(program) && o[1].equals(type) && o[2].equals(subType) && o[3].equals(other)) {
                result = o[4];
            }
        }
        // GenClient.showDebug("getExample: " + result);
        return result;
    }

};